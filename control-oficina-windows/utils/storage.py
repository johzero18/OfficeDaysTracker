import os
import json
from pathlib import Path


APP_DATA_DIR = Path(os.environ.get("APPDATA", Path.home() / ".local")) / "ControlOficina"
DATA_FILE = APP_DATA_DIR / "data.json"


def _ensure_dir():
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> dict:
    _ensure_dir()
    if not DATA_FILE.exists():
        return {}
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_data(data: dict):
    _ensure_dir()
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get(key: str, default=None):
    return load_data().get(key, default)


def set_val(key: str, value):
    data = load_data()
    data[key] = value
    save_data(data)
