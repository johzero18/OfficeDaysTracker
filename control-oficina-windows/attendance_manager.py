from datetime import datetime, date, timedelta
import uuid
import json
from PySide6.QtCore import QObject, Signal

from utils.network import get_default_gateway
from utils.storage import get, set_val, load_data, save_data
from utils.holidays import get_holidays_for_month
from utils.autostart import is_autostart_enabled, set_autostart
import i18n


MONTHLY_GOAL = 8
RECORDS_KEY = "attendance_records"
GATEWAY_KEY = "office_gateway"
INTERVAL_KEY = "check_interval"
LAUNCH_KEY = "launch_at_login"
GOAL_KEY = "monthly_goal"
LANG_KEY = "language"
DEFAULT_GATEWAY = "10.15.16.1"
DEFAULT_INTERVAL = 3600


class AttendanceManager(QObject):
    state_changed = Signal()

    def __init__(self):
        super().__init__()
        self._is_connected = False
        self._days_this_month = 0
        self._today_registered = False
        self._workdays_remaining = 0
        self._office_gateway = DEFAULT_GATEWAY
        self._check_interval = DEFAULT_INTERVAL
        self._monthly_goal = MONTHLY_GOAL
        self._language = "es"
        self._current_gateway: str | None = None
        self._holidays: list[str] = []
        self._records_cache: list[dict] | None = None
        self._holidays_cache_key: tuple[int, int] | None = None

        self._load_settings()
        self._load_month_data()
        self._load_holidays()
        self._check_gateway_now()

    def _load_settings(self):
        data = load_data()
        self._office_gateway = data.get(GATEWAY_KEY, DEFAULT_GATEWAY)
        self._check_interval = data.get(INTERVAL_KEY, DEFAULT_INTERVAL)
        self._monthly_goal = data.get(GOAL_KEY, MONTHLY_GOAL)
        self._language = data.get(LANG_KEY, "es")
        i18n.set_language(self._language)

    def _load_holidays(self):
        now = datetime.now()
        key = (now.year, now.month)
        if self._holidays_cache_key == key:
            return
        self._holidays = get_holidays_for_month(now.year, now.month)
        self._holidays_cache_key = key
        self._calculate_workdays()

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def days_this_month(self) -> int:
        return self._days_this_month

    @property
    def today_registered(self) -> bool:
        return self._today_registered

    @property
    def workdays_remaining(self) -> int:
        return self._workdays_remaining

    @property
    def office_gateway(self) -> str:
        return self._office_gateway

    @office_gateway.setter
    def office_gateway(self, value: str):
        self._office_gateway = value
        set_val(GATEWAY_KEY, value)

    @property
    def check_interval(self) -> int:
        return self._check_interval

    @check_interval.setter
    def check_interval(self, value: int):
        self._check_interval = max(60, value)
        set_val(INTERVAL_KEY, self._check_interval)

    @property
    def current_gateway(self) -> str | None:
        return self._current_gateway

    @property
    def progress_percentage(self) -> float:
        return min(self._days_this_month / self._monthly_goal, 1.0)

    @property
    def goal_reached(self) -> bool:
        return self._days_this_month >= self._monthly_goal

    @property
    def days_remaining(self) -> int:
        return max(self._monthly_goal - self._days_this_month, 0)

    @property
    def monthly_goal(self) -> int:
        return self._monthly_goal

    @monthly_goal.setter
    def monthly_goal(self, value: int):
        self._monthly_goal = max(1, min(31, int(value)))
        set_val(GOAL_KEY, self._monthly_goal)

    @property
    def language(self) -> str:
        return self._language

    @language.setter
    def language(self, value: str):
        self._language = value if value in ("es", "en") else "es"
        set_val(LANG_KEY, self._language)
        i18n.set_language(self._language)
        self.state_changed.emit()

    @property
    def launch_at_login(self) -> bool:
        return is_autostart_enabled()

    @launch_at_login.setter
    def launch_at_login(self, value: bool):
        set_autostart(value)
        set_val(LAUNCH_KEY, value)

    def check_gateway(self):
        self._check_gateway_now()
        self._load_month_data()
        self._load_holidays()
        self.state_changed.emit()

    def _check_gateway_now(self):
        was_connected = self._is_connected
        self._current_gateway = get_default_gateway()
        self._is_connected = self._current_gateway == self._office_gateway

        if self._is_connected and not self._today_registered:
            self._register_today()

        if self._is_connected != was_connected:
            self._load_month_data()

    def _register_today(self):
        today_str = date.today().isoformat()
        records = self._load_all_records()

        already = any(r["date"] == today_str for r in records)
        if not already:
            records.append({"id": str(uuid.uuid4()), "date": today_str})
            self._save_records(records)

        self._today_registered = True
        self._load_month_data()

    def _load_all_records(self) -> list[dict]:
        raw = get(RECORDS_KEY)
        if raw:
            try:
                return json.loads(raw) if isinstance(raw, str) else raw
            except (json.JSONDecodeError, TypeError):
                pass
        return []

    def _save_records(self, records: list[dict]):
        cutoff = date.today() - __import__("datetime").timedelta(days=365)
        filtered = [
            r for r in records
            if datetime.fromisoformat(r["date"]).date() > cutoff
        ]
        set_val(RECORDS_KEY, json.dumps(filtered))
        self._records_cache = None

    def _load_month_data(self):
        records = self._load_all_records()
        today = date.today()
        self._days_this_month = sum(
            1 for r in records
            if datetime.fromisoformat(r["date"]).year == today.year
            and datetime.fromisoformat(r["date"]).month == today.month
        )
        self._today_registered = any(r["date"] == today.isoformat() for r in records)
        self._calculate_workdays()

    def get_records_for_current_month(self) -> list[dict]:
        records = self._load_all_records()
        today = date.today()
        return sorted(
            [
                r for r in records
                if datetime.fromisoformat(r["date"]).year == today.year
                and datetime.fromisoformat(r["date"]).month == today.month
            ],
            key=lambda r: r["date"],
        )

    def add_record(self, day: date) -> bool:
        records = [dict(r) for r in self._load_all_records()]
        day_str = day.isoformat()
        if any(r["date"] == day_str for r in records):
            return False
        records.append({"id": str(uuid.uuid4()), "date": day_str})
        records.sort(key=lambda r: r["date"])
        self._save_records(records)
        self._load_month_data()
        self.state_changed.emit()
        return True

    def remove_record(self, record_id: str) -> bool:
        records = [dict(r) for r in self._load_all_records()]
        filtered = [r for r in records if r["id"] != record_id]
        if len(filtered) == len(records):
            return False
        self._save_records(filtered)
        self._load_month_data()
        self.state_changed.emit()
        return True

    def edit_record(self, record_id: str, new_day: date) -> bool:
        records = [dict(r) for r in self._load_all_records()]
        day_str = new_day.isoformat()
        found = False
        for r in records:
            if r["id"] == record_id:
                if any(x["date"] == day_str and x["id"] != record_id for x in records):
                    return False
                r["date"] = day_str
                found = True
                break
        if not found:
            return False
        records.sort(key=lambda r: r["date"])
        self._save_records(records)
        self._load_month_data()
        self.state_changed.emit()
        return True

    def _is_holiday(self, d: date) -> bool:
        return d.isoformat() in self._holidays

    def _calculate_workdays(self):
        today = date.today()
        last_day = today.replace(day=28) + timedelta(days=4)
        last_day = last_day.replace(day=1) - timedelta(days=1)

        workdays = 0
        current = today + timedelta(days=1)
        while current <= last_day:
            if current.weekday() < 5 and not self._is_holiday(current):
                workdays += 1
            current += timedelta(days=1)

        self._workdays_remaining = workdays

    def refresh(self):
        self._check_gateway_now()
        self._load_month_data()
        self._load_holidays()
        self.state_changed.emit()
