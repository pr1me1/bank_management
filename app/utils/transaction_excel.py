import logging

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.utils import BankTypesMapping

logger = logging.getLogger(__name__)

try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
    FONT_NAME = 'DejaVuSans'
    FONT_NAME_BOLD = 'DejaVuSans-Bold'
except Exception as e:
    logger.warning(f"Could not load DejaVuSans fonts: {e}, using Helvetica")
    FONT_NAME = 'Helvetica'
    FONT_NAME_BOLD = 'Helvetica-Bold'

import logging
from datetime import datetime, date, timedelta  # noqa
from pathlib import Path
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from PyPDF2 import PdfMerger
from sqlalchemy.orm import Session

from app.core.configs import settings
from app.models import BankAccount, Transaction
from app.repo import TransactionRepository

logger = logging.getLogger(__name__)

try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
    FONT_NAME = 'DejaVuSans'
    FONT_NAME_BOLD = 'DejaVuSans-Bold'
except:
    FONT_NAME = 'Helvetica'
    FONT_NAME_BOLD = 'Helvetica-Bold'
    logger.warning("Could not load DejaVuSans fonts, using Helvetica")


async def handle_daily_report(
        company_name: str,
        bank_accounts: list[BankAccount],
        db: Session
) -> tuple[str, bytes, str] | None:
    timezone = ZoneInfo(settings.TIMEZONE)
    now = datetime.now(timezone)
    date_from = now.replace(hour=9, minute=0, second=0, microsecond=0)
    # date_from = now - timedelta(days=7)
    transaction_repo = TransactionRepository(db)
    pdf_paths = []
    for bank_account in bank_accounts:
        transactions = transaction_repo.get_by_account(
            bank_account.account_number,
            date_from=date_from
        )
        bank_name = BankTypesMapping.get(bank_account.bank_type)
        if transactions:
            pdf_path = await _generate_pdf(
                company_name,
                bank_account,
                transactions,
                current_date=date_from.date(),
                bank_name=bank_name
            )
            if pdf_path:
                pdf_paths.append(pdf_path)

    if pdf_paths:
        filepath, pdf_bytes = await _merge_pdfs(pdf_paths, company_name, date_from.date())
        filename = Path(filepath).name

        for pdf_path in pdf_paths:
            try:
                Path(pdf_path).unlink()
            except Exception as e:
                logger.error(f"Failed to delete temporary PDF {pdf_path}: {e}")

        return filepath, pdf_bytes, filename

    return None


async def _generate_pdf(
        company_name: str,
        bank_account: BankAccount,
        transactions: list[Transaction],
        current_date: date,
        bank_name: str
) -> str:
    if not transactions:
        return None

    output_dir = Path("reports/daily")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    formated_company_name = company_name.replace(" ", "_")
    filename = f"{formated_company_name}_{bank_account.account_number}_{timestamp}_temp.pdf"
    filepath = output_dir / filename

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    story = []
    elements = await _generate_pdf_parts(
        company_name,
        bank_account,
        transactions,
        current_date,
        bank_name
    )

    if elements:
        story.extend(elements)
        doc.build(story)
        return str(filepath)

    return None


async def _generate_pdf_parts(
        company_name: str,
        bank_account: BankAccount,
        transactions: list[Transaction],
        current_date: date,
        bank_name: str
):
    account_number = bank_account.account_number
    current_amount = float(bank_account.balance)

    income_transactions = [
        t for t in transactions
        if t.receiver_account == account_number
    ]
    income_for_period = sum(
        float(t.payment_amount) for t in income_transactions
    )

    outcome_transactions = [
        t for t in transactions
        if t.sender_account == account_number
    ]
    outcome_for_period = sum(
        float(t.payment_amount) for t in outcome_transactions
    )

    opening_balance = current_amount - income_for_period + outcome_for_period

    formatted_date = current_date.strftime("%d.%m.%Y")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=FONT_NAME_BOLD,
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=12
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9,
        alignment=TA_LEFT
    )

    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontName=FONT_NAME_BOLD,
        fontSize=8,
        alignment=TA_CENTER
    )

    cell_style = ParagraphStyle(
        'CustomCell',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=8,
        alignment=TA_CENTER,
        wordWrap='CJK'
    )

    story = []

    title = Paragraph(f"Выписка лицевых счетов за {formatted_date}", title_style)
    story.append(title)
    story.append(Spacer(1, 5 * mm))

    info_data = [
        [Paragraph(f"Дата: {current_date.strftime('%d.%m.%Y')}", normal_style), ""],
        [Paragraph(f"Банк: {bank_name}", normal_style), Paragraph(f"№ счёта: {account_number}", normal_style)],
        [Paragraph(f"Наименование счёта: {company_name}", normal_style), ],
        [
            Paragraph(f"Остаток: Начало {opening_balance:,.2f}", normal_style),
            Paragraph(f"Остаток: Конец дня {current_amount:,.2f}", normal_style)
        ]
    ]

    info_table = Table(info_data, colWidths=[140 * mm, 120 * mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))

    story.append(info_table)
    story.append(Spacer(1, 5 * mm))

    headers = [
        Paragraph("№ пп", header_style),
        Paragraph("Дата документа", header_style),
        Paragraph("№ док.", header_style),
        Paragraph("Наименование счёта", header_style),
        Paragraph("№ счёта", header_style),
        Paragraph("МФО", header_style),
        Paragraph("Обороты по дебету", header_style),
        Paragraph("Обороты по кредиту", header_style),
        Paragraph("Назначение платежа", header_style),
    ]

    table_data = [headers]

    for idx, transaction in enumerate(transactions, start=1):

        is_income = transaction.receiver_account == account_number

        if is_income:
            counterparty_name = transaction.sender_name or ""
            counterparty_account = transaction.sender_account or ""
            counterparty_mfo = transaction.sender_bank_code or ""
            debit = float(transaction.payment_amount)
            credit = 0.0
        else:
            counterparty_name = transaction.receiver_name or ""
            counterparty_account = transaction.receiver_account or ""
            counterparty_mfo = transaction.receiver_bank_code or ""
            debit = 0.0
            credit = float(transaction.payment_amount)

        doc_date = transaction.document_date.strftime("%d.%m.%Y") if transaction.document_date else ""

        row = [
            Paragraph(str(idx), cell_style),
            Paragraph(doc_date, cell_style),
            Paragraph(transaction.payment_number or "", cell_style),
            Paragraph(counterparty_name, cell_style),
            Paragraph(counterparty_account, cell_style),
            Paragraph(counterparty_mfo, cell_style),
            Paragraph(f"{debit:,.2f}" if debit > 0 else "0,00", cell_style),
            Paragraph(f"{credit:,.2f}" if credit > 0 else "0,00", cell_style),
            Paragraph(transaction.payment_description or "", cell_style),
        ]

        table_data.append(row)

    col_widths = [
        15 * mm,
        22 * mm,
        20 * mm,
        45 * mm,
        35 * mm,
        15 * mm,
        25 * mm,
        25 * mm,
        65 * mm,
    ]

    trans_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    table_style = TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), FONT_NAME_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),

        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (6, 1), (7, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),

        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ])

    trans_table.setStyle(table_style)
    story.append(trans_table)

    return story


async def _merge_pdfs(pdf_paths: list[str], company_name: str, report_date: date) -> tuple[str, bytes]:
    output_dir = Path("reports/daily")
    output_dir.mkdir(parents=True, exist_ok=True)

    formatted_date = report_date.strftime("%Y%m%d")
    filename = f"{company_name}_{formatted_date}_kapital_transactions.pdf"
    filepath = output_dir / filename

    merger = PdfMerger()

    for pdf_path in pdf_paths:
        merger.append(pdf_path)

    merger.write(str(filepath))
    merger.close()

    with open(filepath, 'rb') as f:
        pdf_bytes = f.read()

    logger.info(f"Generated merged daily report: {filepath}")
    return str(filepath), pdf_bytes
