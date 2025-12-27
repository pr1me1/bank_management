from __future__ import annotations

from zoneinfo import ZoneInfo
from datetime import datetime, timezone as dt_timezone

from app.core.configs import settings

tz = settings.TIMEZONE


def now(tz: dt_timezone | ZoneInfo | None = None) -> datetime:
    if tz is None:
        tz = ZoneInfo(settings.TIMEZONE)
    return datetime.now(tz)
