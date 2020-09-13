from datetime import datetime, timedelta
from typing import Optional


def utc_now():
    """Don't keep timezone"""
    return datetime.utcnow()


def utc_delta(
    *,
    days: Optional[int] = None,
    hours: Optional[int] = None,
    minutes: Optional[int] = None,
    seconds: Optional[int] = None,
):
    params = {}
    if days:
        params["days"] = days
    if hours:
        params["hours"] = hours
    if minutes:
        params["minutes"] = minutes
    if seconds:
        params["seconds"] = seconds
    return datetime.utcnow() + timedelta(**params)
