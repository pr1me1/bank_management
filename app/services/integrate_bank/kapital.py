import asyncio
import hashlib
import json
import logging
import uuid
from decimal import Decimal
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.core.configs import settings
from app.core.redis import get_redis_client
from app.models import BankTypes, Transaction
from app.repo import BankAccountRepository
from app.repo.transaction import TransactionRepository

logger = logging.getLogger(__name__)


class Kapitalbank:
    def __init__(self, company_id: uuid.UUID, db: Optional[Session] = None) -> None:
        self.redis_client = get_redis_client()
        self.company_id = company_id
        self.db = db
        self.device_id = self.redis_client.get(f"kapitalbank:{company_id}:device")

        if self.device_id is None:
            self.device_id = self._generate_device_id()
            self.redis_client.setex(name=f"kapitalbank:{company_id}:device", value=self.device_id, time=30 * 24 * 3600)

        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"

    def _generate_device_id(self):
        generated = hashlib.md5(str(uuid.getnode()).encode()).hexdigest()
        return generated

    async def headers(self, auth_required: bool = False, x_api_version: float = 2.0) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU",
            "Content-Language": "ru",
            "Origin": "https://b2b.kapitalbank.uz",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": self.user_agent,
            "x-api-version": f"{x_api_version}",
            "x-device-info": f"{self.user_agent} {self.device_id}",
            "x-user-app": "name=Uzum Business;version=2.2.0",
            "x-user-device": f"id={self.device_id};type=Desktop;name=Chrome",
            "x-user-os": "name=Windows;version=10",
        }
        if auth_required:
            token_key = f"kapitalbank:{self.company_id}:tokens"
            cached_token = self.redis_client.get(token_key)
            logger.info(cached_token)
            if cached_token is None:
                token = await self._refresh_tokens()
                logger.info(token)
                headers["Authorization"] = f"Bearer {token.get('access_token')}"
                return headers

            cached_data = json.loads(cached_token)
            logger.info(cached_data)
            if not cached_data or not cached_data.get('access_token'):
                raise ValueError("Invalid authentication tokens. Please authenticate again.")
            headers["Authorization"] = f"Bearer {cached_data.get('access_token')}"
        return headers

    async def _refresh_tokens(self):

        credentials = self._get_credentials()

        if credentials is None:
            raise ValueError("Credentials not found. Please authenticate first.")

        try:
            if isinstance(credentials, str):
                payload = json.loads(credentials)
            else:
                payload = credentials
        except Exception as e:

            raise

        data = await self.auth(login=payload.get("login"), password=payload.get("password"), confirm_type=0)

        return data

    async def auth(self, login, password, confirm_type: int = 0):
        try:
            headers = await self.headers()
            payload = {"login": str(login).strip(), "password": str(password).strip(), "confirmType": confirm_type}

            current_creds = self._get_credentials()
            if not current_creds:
                self._save_credentials(login, password)

            response_data = await self._make_auth_request(payload, headers)

            return await self._process_auth_response(response_data, login, password, confirm_type)

        except httpx.TimeoutException:

            return {"success": False, "message": "Request timeout"}
        except httpx.RequestError as e:

            return {"success": False, "message": f"Request error: {str(e)}"}
        except Exception as e:

            return {"success": False, "message": f"Unexpected error: {str(e)}"}

    async def _make_auth_request(self, payload: dict, headers: dict) -> dict:
        url = f"{settings.KAPITALBANK_URL}/auth"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url=url,
                json=payload,
                headers=headers
            )

        if response.status_code != 200 and response.json().get("error"):
            error_msg = response.json().get("error")

            raise ValueError(f"Failed to authenticate with Kapitalbank: {error_msg}")

        return response.json()

    async def _process_auth_response(self, response_data: dict, login: str, password: str, confirm_type: int) -> dict:

        result = response_data.get("result", {})
        confirm_token = result.get("confirmToken")
        need_confirm = result.get("needConfirm", False)
        confirm_phone = result.get("confirmPhone")

        if need_confirm and confirm_token:

            if confirm_type == 0:
                return self._create_confirmation_session(result, login, password, confirm_phone)

        return self._save_auth_tokens(result)

    def _create_confirmation_session(self, result: dict, login: str, password: str, confirm_phone: str) -> dict:
        session_id = str(uuid.uuid4())

        self.redis_client.setex(
            session_id,
            65,
            json.dumps({
                "confirm_token": result.get("confirmToken"),
                "user_id": result.get("userId"),
                "login": str(login).strip(),
                "password": str(password).strip(),
            })
        )

        return {
            "success": True,
            "session_id": session_id,
            "confirm_type": 0,
            "next_step": "otp",
            "confirm_phone": confirm_phone,
        }

    def _save_auth_tokens(self, result: dict) -> dict:
        data = {
            "user_id": result.get("userId"),
            "access_token": result.get("accessToken"),
            "refresh_token": result.get("refreshToken"),
        }
        cache_key = f"kapitalbank:{self.company_id}:tokens"
        self.redis_client.setex(cache_key, 12 * 60 * 60, json.dumps(data))

        return data

    def _save_credentials(self, login, password):

        data = {
            "login": str(login).strip(),
            "password": str(password).strip(),
        }
        cache_key = f"kapitalbank:{self.company_id}:payload"
        self.redis_client.set(cache_key, json.dumps(data))

        return data

    def _get_credentials(self):
        cache_key = f"kapitalbank:{self.company_id}:payload"
        cached_data = self.redis_client.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        return None

    async def confirm_by_otp(self, code: str, session_id: str):
        try:
            cached_data = self._get_session_data(session_id)
            result = await self._send_otp_confirmation(code, cached_data)
            self._save_confirmation_tokens(result, cached_data)
            return {"success": True, "message": "Confirmed successfully"}
        except ValueError as e:

            return {"success": False, "message": str(e)}
        except httpx.TimeoutException:

            return {"success": False, "message": "Request timeout"}
        except httpx.RequestError as e:

            return {"success": False, "message": f"Request error: {str(e)}"}
        except Exception as e:

            return {"success": False, "message": f"Unexpected error: {str(e)}"}

    def _get_session_data(self, session_id: str) -> dict:

        cached = self.redis_client.get(session_id)
        if not cached:
            raise ValueError("Session expired")
        return json.loads(cached)

    async def _send_otp_confirmation(self, code: str, cached_data: dict) -> dict:
        url = f"{settings.KAPITALBANK_URL}/auth/confirm"

        payload = {
            "confirmCode": code,
            "confirmToken": cached_data.get("confirm_token"),
            "userId": cached_data.get("user_id")
        }

        async with httpx.AsyncClient(timeout=30) as client:
            headers = await self.headers()
            response = await client.put(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )

        if response.status_code != 200:
            raise ValueError("Failed to confirm")

        response_data = response.json()
        return response_data.get("result") or {}

    def _save_confirmation_tokens(self, result: dict, cached_data: dict):
        self.redis_client.set(
            name=f"kapitalbank:{self.company_id}:tokens",
            value=json.dumps(result)
        )
        data = {
            "user_id": cached_data.get("user_id"),
            "access_token": result.get("accessToken"),
            "refresh_token": result.get("refreshToken"),
        }
        self.redis_client.setex(
            name=f"kapitalbank:{self.company_id}:tokens",
            time=12 * 60 * 60,
            value=json.dumps(data)
        )

    async def get_business_info(self):

        business_info = self.redis_client.get(f"kapitalbank:{self.company_id}:business_info")
        if business_info:
            return self._parse_cached_business_info(business_info)

        try:

            business_data = await self._fetch_business_info()

            self._cache_business_info(business_data)

            return {
                "success": True,
                "businessCode": business_data['businessCode'],
                "branch": business_data['branch'],
            }
        except httpx.TimeoutException:

            return {"success": False, "message": "Request timeout"}
        except httpx.RequestError as e:

            return {"success": False, "message": f"Request error: {str(e)}"}
        except Exception as e:

            return {"success": False, "message": f"Unexpected error: {str(e)}"}

    def _parse_cached_business_info(self, cached_data: str) -> dict:

        business_info = json.loads(cached_data)
        return {
            "success": True,
            "businessCode": business_info['businessCode'],
            "branch": business_info['branch'],
        }

    async def _fetch_business_info(self) -> dict:
        url = f"{settings.KAPITALBANK_URL}/business/list"

        headers = await self.headers(auth_required=True)
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise httpx.RequestError("Failed to fetch business info")

        return response.json().get("result", [])[0]

    def _cache_business_info(self, business_data: dict):

        self.redis_client.setex(
            name=f"kapitalbank:{self.company_id}:business_info",
            time=30 * 24 * 3600,
            value=json.dumps(business_data)
        )

    async def accounts(self):
        business_info = await self.get_business_info()
        if not business_info.get("success"):
            return business_info

        business_code = business_info['businessCode']
        branch_code = business_info['branch']

        try:
            account_items = await self._fetch_all_accounts(business_code, branch_code)
            accounts = self._transform_accounts(account_items)
            bank_accounts = await self._save_or_update_accounts(accounts)
            return {
                "success": True,
                "message": "Accounts fetched successfully",
                "items": bank_accounts
            }
        except httpx.TimeoutException:

            return {"success": False, "message": "Request timeout"}
        except httpx.RequestError as e:

            return {"success": False, "message": f"Request error: {str(e)}"}
        except Exception as e:

            return {"success": False, "message": f"Unexpected error: {str(e)}"}

    async def _fetch_all_accounts(self, business_code: str, branch_code: str) -> list:
        results = []
        page_number = 1
        page_size = 100

        while True:
            url = f"{settings.KAPITALBANK_URL}/business/{business_code}/{branch_code}/filtered-accounts"
            params = {"pageNumber": page_number, "pageSize": page_size}
            headers = await self.headers(auth_required=True)

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, headers=headers, params=params)

            if response.status_code != 200:
                raise httpx.RequestError("Failed to fetch accounts")

            response_data = response.json()
            result = response_data.get("result", {})
            items = result.get("items", [])

            results.extend(items)

            if page_number >= result.get("totalPages", 0):
                break

            page_number += 1
            await asyncio.sleep(3)

        return results

    def _transform_accounts(self, items: list) -> list:

        accounts = []
        for item in items:
            accounts.append({
                "bank_type": BankTypes.KAPITALBANK.value,
                "account_number": item.get("number"),
                "currency": item.get("currency", {}).get("alphaCode"),
                "balance": Decimal(item.get("currentBalance", 0)) / 100,
                "mfo_number": item.get("branch"),
                "company_id": self.company_id,
            })

        return accounts

    async def _save_or_update_accounts(self, accounts: list[dict]):
        bank_account_repo = BankAccountRepository(self.db)
        accounts = bank_account_repo.bulk_create_or_update(accounts)
        return accounts

    async def transactions(self):

        business_info = await self.get_business_info()
        if not business_info.get("success"):
            return business_info

        business_code = business_info['businessCode']
        branch_code = business_info['branch']

        try:

            transaction_repo = TransactionRepository(self.db)

            new_transaction_ids = await self._collect_new_transaction_ids(
                business_code,
                branch_code,
                transaction_repo
            )

            if not new_transaction_ids:
                return {
                    "success": True,
                    "message": "No new transactions found",
                    "new_transactions": []
                }

            new_transactions = await self._fetch_and_create_transactions(
                business_code,
                branch_code,
                new_transaction_ids,
                transaction_repo
            )

            return {
                "success": True,
                "new_transactions": new_transactions,
                "count": new_transactions
            }

        except httpx.TimeoutException:

            self._handle_db_rollback()
            return {"success": False, "message": "Request timeout"}
        except httpx.RequestError as e:

            self._handle_db_rollback()
            return {"success": False, "message": f"Request error: {str(e)}"}
        except Exception as e:

            self._handle_db_rollback()
            return {"success": False, "message": f"Unexpected error: {str(e)}"}

    async def _collect_new_transaction_ids(
            self,
            business_code: str,
            branch_code: str,
            transaction_repo: TransactionRepository
    ) -> list[str]:

        new_ids = []
        page_number = 1
        page_size = 100

        while True:

            url = f"{settings.KAPITALBANK_URL}/business/{business_code}/{branch_code}/paymentOrders/inBank"
            params = {"pageNumber": page_number, "pageSize": page_size}

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    url,
                    headers=await self.headers(auth_required=True),
                    params=params
                )

            if response.status_code != 200:
                raise httpx.RequestError(f"Failed to fetch transactions: {response.status_code}")

            response_data = response.json()
            items = response_data.get("result", {}).get("items", [])

            current_ids = [str(item["id"]) for item in items if
                           "id" in item]  # faqat in out larri olishga if item["direction"] in ["out", "in"]
            non_existing_ids = transaction_repo.get_non_existing_transaction_ids(current_ids)

            new_ids.extend(non_existing_ids)

            if not non_existing_ids or non_existing_ids != current_ids:
                break

            total_pages = response_data.get("result", {}).get("totalPages", 0)
            if page_number >= total_pages:
                break

            page_number += 1
            await asyncio.sleep(3)

        return new_ids

    async def _fetch_and_create_transactions(
            self,
            business_code: str,
            branch_code: str,
            transaction_ids: list[str],
            transaction_repo: TransactionRepository
    ) -> list[Transaction]:

        transactions_data = []
        for i, transaction_id in enumerate(transaction_ids):
            transaction_data = await self._fetch_transaction_details(
                business_code,
                branch_code,
                transaction_id
            )
            transactions_data.append(transaction_data)
            await asyncio.sleep(1)

        new_transactions = transaction_repo.bulk_create(transactions_data)

        return new_transactions

    async def _fetch_transaction_details(
            self,
            business_code: str,
            branch_code: str,
            transaction_id: str
    ) -> dict:

        from app.models import TransactionStatus
        from datetime import datetime

        url = f"{settings.KAPITALBANK_URL}/business/{business_code}/{branch_code}/paymentOrders/{transaction_id}"
        params = {"source": "bank"}
        headers = await self.headers(auth_required=True, x_api_version=4.0)

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise httpx.RequestError(f"Failed to fetch transaction {transaction_id}: {response.status_code}")

        response_data = response.json()
        item = response_data.get("result", {})

        document_date_str = item.get("provedDate")
        document_date = None
        if document_date_str:
            try:
                document_date = datetime.fromisoformat(document_date_str)
            except (ValueError, TypeError) as e:

                document_date = None

        return {
            "transaction_id": str(item.get("id", transaction_id)),
            "document_date": document_date,
            "payment_amount": Decimal(item.get("amount", 0)) / 100,
            "currency": item.get("currency", {}).get("alphaCode", "UZS"),
            "receiver_name": item.get("receiverName"),
            "receiver_inn": item.get("receiverInnOrPinfl"),
            "receiver_account": item.get("receiverAccountNumber"),
            "receiver_bank_code": item.get("receiverBranch"),
            "sender_name": item.get("senderName"),
            "sender_inn": item.get("senderInn"),
            "sender_account": item.get("senderAccountNumber"),
            "sender_bank_code": item.get("senderBranch"),
            "payment_description": item.get("paymentPurpose"),
            "payment_purpose_code": item.get("paymentPurposeCode"),
            "payment_number": item.get("paymentNumber"),
            "status": TransactionStatus.COMPLETED,
            "direction": item.get("direction"),
        }

    def _handle_db_rollback(self):
        if self.db:
            self.db.rollback()


__all__ = ["Kapitalbank"]
