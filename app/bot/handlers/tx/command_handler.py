from aiogram import Router, filters, types

from app.bot.handlers.tx.balance_formatter import balance_formatter
from app.core.configs import settings, logger
from app.db import get_db_session
from app.repo import CompanyRepository, BankAccountRepository, CompanyGroupRepository, GroupRepository, UserRepository
from app.services.integrate_bank.kapital import Kapitalbank
from app.utils.translations import t, get_user_language

router = Router()


@router.message(filters.Command("balance"))
async def get_balance(message: types.Message, user_repo: UserRepository):
    user = user_repo.get_by_telegram_id(message.from_user.id)
    lang = get_user_language(user)

    if not settings.KAPITALBANK_URL:
        await message.answer(t("error_service_unavailable", lang))
        logger.error("KAPITALBANK_URL is not configured")
        return

    try:
        with get_db_session() as db:
            group_repo = GroupRepository(db)
            company_group_repo = CompanyGroupRepository(db)
            company_repo = CompanyRepository(db)
            bank_account_repo = BankAccountRepository(db)

            group_id = message.chat.id
            group = group_repo.get_by_telegram_id(group_id)

            if not group:
                await message.answer(t("bot_not_added", lang))
                return

            company_groups = company_group_repo.get_by_group_id(group.id)

            if not company_groups:
                await message.answer(t("group_not_linked", lang))
                return

            companies_processed = 0

            for cg in company_groups:
                company_id = cg.company_id
                company = company_repo.get_by_id(company_id)

                if not company:
                    logger.warning(f"Company {company_id} not found in database")
                    continue

                has_bank_account = company_repo.has_bank_accounts(company_id)

                if not has_bank_account:
                    logger.info(f"Company {company.name} ({company_id}) has no bank accounts yet")
                    continue

                try:
                    service = Kapitalbank(company_id, db=db)
                    result = await service.accounts()

                    if not result or result.get("success") is False:
                        logger.warning(
                            f"Failed to fetch accounts from Kapitalbank for company {company.name}: "
                            f"{result.get('message') if result else 'No response'}"
                        )
                        continue

                    accounts = []
                    for account_data in result.get('items', []):
                        account = bank_account_repo.get_or_create(
                            company_id=company_id,
                            account_number=account_data.account_number,
                            defaults={
                                'bank_type': account_data.bank_type,
                                'currency': account_data.currency,
                                'balance': account_data.balance,
                                'mfo_number': account_data.mfo_number,
                            }
                        )
                        accounts.append(account)

                    if not accounts:
                        await message.answer(
                            t("bank_account_not_found", lang, company=company),
                            parse_mode="HTML"
                        )
                        continue

                    accounts.sort(key=lambda acc: acc.bank_type, reverse=True)

                    message_text = await balance_formatter(company.name, accounts, lang)
                    await message.answer(message_text, parse_mode="HTML")

                    companies_processed += 1
                    logger.info(f"✅ Sent balance for company {company.name} to group {group_id}")

                except Exception as e:
                    logger.error(
                        f"Error processing company {company.name} ({company_id}): {e}",
                        exc_info=True
                    )
                    await message.answer(
                        t("bank_data_load_error", lang, company=company),
                        parse_mode="HTML"
                    )
                    continue

            if companies_processed == 0:
                await message.answer(t("no_bank_accounts", lang))


    except Exception as e:
        logger.error(f"Critical error in get_balance command: {e}", exc_info=True)
        await message.answer(t("balance_load_error", lang))
