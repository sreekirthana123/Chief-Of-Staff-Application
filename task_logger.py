"""
task_logger.py
--------------
Lightweight append-only action log for the Chief of Staff workflow.

Records every "sent" and "booked" action to `action_log.json` in the
same directory as this file. No third-party dependencies – only the
Python standard library.

Public API
----------
- `log_action(action_type, thread_subject, detail, action_id)` -> dict
- `get_action_log()`                                           -> list[dict]
- `clear_log()`                                                -> None
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any


# Config
# ------

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(HERE, "action_log.json")


# Public API
# ----------

def log_action(
    action_type: str,
    thread_subject: str,
    detail: str,
    action_id: str,
) -> dict[str, Any]:
    """Append one action record to `action_log.json`."""
    
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action_type": action_type,
        "thread_subject": thread_subject,
        "detail": detail,
        "id": action_id
    }
    
    log = get_action_log()
    log.append(record)
    
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
        
    return record


def get_action_log() -> list[dict[str, Any]]:
    """Read `action_log.json` and return the full list."""
    if not os.path.exists(LOG_PATH):
        return []
        
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []


def clear_log() -> None:
    """Write an empty list to `action_log.json`."""
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action_type": action_type,
        "thread_subject": thread_subject,
        "detail": detail,
        "id": action_id,
    }
    
    existing = get_action_log()
    existing.append(record)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
        
    return record


def get_action_log() -> list[dict[str, Any]]:
    """Return all records from `action_log.json`."""
    
    # Returns
    # -------
    # list[dict]
    #     The full log in append order, or `[]` if the file does not
    #     exist, is empty, or contains invalid JSON.
    
    if not os.path.exists(LOG_PATH):
        return []
        
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def clear_log() -> None:
    """Overwrites `action_log.json` with an empty list."""
    
    # Creates the file if it does not exist.
    
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)
