import logging
from typing import Optional, Tuple
from datetime import datetime, timedelta

import dateparser

logger = logging.getLogger(__name__)


def parse_and_validate_date(
        date_str: str,
        min_days_ago: int = 31,
        max_days_future: int = 366
) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse and validate date using dateparser with auto language detection.

    Supports all languages automatically - no need to specify language!

    Examples:
        "4 dek"      → 04.12.2024 (Russian: dekabr)
        "4 avg"      → 04.08.2024 (Uzbek: avgust)
        "4 dec"      → 04.12.2024 (English: december)
        "bugun"      → today (Uzbek)
        "сегодня"    → today (Russian)
        "today"      → today (English)
        "23.12.2026" → 23.12.2026
    """
    if not date_str or not date_str.strip():
        return None, 'doc_invalid_date_format'


    try:
        parsed_date = dateparser.parse(
            date_str,
            languages=['uz', 'uz', 'en', 'ru'],
            settings={
                'PREFER_DATES_FROM': 'current_period',
                'RETURN_AS_TIMEZONE_AWARE': False,
                'RELATIVE_BASE': datetime.now(),
                'STRICT_PARSING': False,
                'DATE_ORDER': 'DMY'
            }
        )

        if not parsed_date:
            logger.info(f"Trying all languages for: {date_str}")
            parsed_date = dateparser.parse(
                date_str,
                settings={
                    'STRICT_PARSING': False,
                    'DATE_ORDER': 'DMY',
                }
            )

        if not parsed_date:
            logger.warning(f"Failed to parse date: '{date_str}'")
            return None, 'doc_invalid_date_format'

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        min_date = today - timedelta(days=min_days_ago)
        max_date = today + timedelta(days=max_days_future)

        parsed_date_clean = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)

        if parsed_date_clean < min_date:
            return None, 'doc_date_too_old'

        if parsed_date_clean > max_date:
            return None, 'doc_date_too_future'

        return parsed_date.strftime('%d.%m.%Y'), None

    except Exception as e:
        logger.error(f"Error parsing date '{date_str}': {e}")
        return None, 'doc_invalid_date_format'