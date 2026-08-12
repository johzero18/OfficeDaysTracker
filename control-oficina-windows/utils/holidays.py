import json
import urllib.request
from datetime import datetime

from .storage import set_val, get


HOLIDAYS_API = "https://api.argentinadatos.com/api/v2/feriados/{year}/{month}"
CACHE_KEY = "cached_holidays"

_cache: dict[str, list[str]] = {}


def _fetch_holidays(year: int, month: int) -> list[str]:
    url = HOLIDAYS_API.format(year=year, month=month)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [feriado["fecha"] for feriado in data]
    except Exception:
        return []


def get_holidays_for_month(year: int | None = None, month: int | None = None) -> list[str]:
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    key = f"{year}-{month}"
    if key in _cache:
        return _cache[key]

    cache = get(CACHE_KEY, {})
    if key in cache:
        _cache[key] = cache[key]
        return cache[key]

    holidays = _fetch_holidays(year, month)
    _cache[key] = holidays
    cache[key] = holidays
    set_val(CACHE_KEY, cache)
    return holidays
