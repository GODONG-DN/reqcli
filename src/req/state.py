"""Request state — store extracted values for chaining requests."""

from __future__ import annotations

import json
from pathlib import Path

STATE_FILE = Path.cwd() / ".req" / "state.json"


def _load() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def _save(data: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def set_state(key: str, value: str) -> None:
    data = _load()
    data[key] = str(value)
    _save(data)


def get_state(key: str) -> str:
    return _load().get(key, "")


def substitute_state(text: str) -> str:
    """Replace {{$key}} placeholders with previously extracted values."""
    data = _load()
    result = text
    for key, val in data.items():
        result = result.replace(f"{{{{${key}}}}}", val)
    return result


def extract_value(body: str, jsonpath: str) -> str:
    """Extract a value from a JSON response using a simple dotted path.

    Example: extract_value(body, "token") for {"token": "abc"} returns "abc"
    Example: extract_value(body, "user.id") for {"user":{"id":1}} returns "1"
    """
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return ""

    parts = jsonpath.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit():
            idx = int(part)
            if 0 <= idx < len(current):
                current = current[idx]
            else:
                return ""
        else:
            return ""
    return str(current) if not isinstance(current, (dict, list)) else ""
