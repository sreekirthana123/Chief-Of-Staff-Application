from __future__ import annotations

import socket

# IPv4 monkey patch (mirrors engine.py)
# Prevents hangs on hosts that advertise IPv6 but can't complete the
# connection - forces all DNS resolution to return IPv4 addresses only.

_original_getaddrinfo = socket.getaddrinfo

def ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _original_getaddrinfo(
        host,
        port,
        socket.AF_INET,
        type,
        proto,
        flags,
    )

socket.getaddrinfo = ipv4_only_getaddrinfo

import os
import json
import datetime
from typing import Any
from dotenv import load_dotenv
load_dotenv()

# ############################################################################
# Config
# ############################################################################

# Scopes must match engine.py exactly so both modules share the same
# token.json without triggering a re-auth flow.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
]

# ############################################################################
# Calendar service builder
# ############################################################################

def build_calendar_service(credentials_json: str | None = None):
    """Return an authenticated Google Calendar v3 service resource.

    Authentication priority (mirrors engine._build_gmail_service):
      1. credentials_json argument (Web OAuth login from the Streamlit UI)
      2. Local token.json file (for development)
      3. Full OAuth flow with local server (for CLI / local development)

    The `credentials.json` and `token.json` files are resolved relative
    to this file's directory - the same location engine.py uses - so both
    modules share a single set of credential files.

    Parameters
    ----------
    credentials_json : str | None
        JSON string of authorized user credentials (from the Streamlit UI
        OAuth callback). Used first when provided.

    Returns
    -------
    googleapiclient.discovery.Resource
        Authenticated Calendar v3 service.

    Raises
    ------
    FileNotFoundError
        If no valid credentials can be obtained.
    """
    from google.auth.transport.requests import Request # type: ignore
    from google.oauth2.credentials import Credentials # type: ignore
    from google_auth_oauthlib.flow import InstalledAppFlow # type: ignore
    from googleapiclient.discovery import build # type: ignore

    here = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(here, "credentials.json")
    token_path = os.path.join(here, "token.json")

    creds: Credentials | None = None

    # ── 1. Credentials from explicit parameter (Web OAuth login) ──────
    if credentials_json:
        try:
            creds = Credentials.from_authorized_user_info(
                json.loads(credentials_json), SCOPES
            )
        except Exception:
            creds = None

    # ── 2. Local token.json file ──────────────────────────────────────
    if not creds and os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except ValueError:
            creds = None

    # ── Validate / refresh / acquire credentials ──────────────────────
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            try:
                with open(token_path, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
            except Exception:
                pass
        else:
            # ── 3. Full OAuth flow (local development / CLI only) ─────
            if not os.path.exists(creds_path):
                raise FileNotFoundError(
                    f"Google OAuth client secrets not found at {creds_path}"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path,
                SCOPES,
            )
            creds = flow.run_local_server(
                host="localhost",
                port=8080,
                open_browser=True,
            )
            try:
                with open(token_path, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
            except Exception:
                pass

    service = build(
        "calendar",
        "v3",
        credentials=creds,
        cache_discovery=False,
    )

    return service


def parse_meeting_request(thread: dict[str, Any]) -> dict[str, Any]:
    """
    Parse a thread dict and extract meeting details using Gemini.

    Parameters
    ----------
    thread : dict
        A dict with "subject" and "messages" keys. Messages is a list of
        dicts with "from", "date", "body" keys.

    Returns
    -------
    dict
        Parsed meeting details with keys: proposed_times, attendees, topic,
        duration_minutes. On failure, returns a dict with "parsing_error"
        and "raw_response".
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "parsing_error": "GEMINI_API_KEY environment variable not set",
            "raw_response": "",
        }

    # Concatenate all messages
    thread_text = ""
    messages = thread.get("messages", [])
    for msg in messages:
        sender = msg.get("from", "")
        date = msg.get("date", "")
        body = msg.get("body", "")
        thread_text += f"From: {sender}\nDate: {date}\n{body}\n\n"

    # Build prompt
    today = datetime.date.today().isoformat()
    prompt = (
        f"Today's date is {today}.\n\n"
        f"Here is the email thread:\n\n{thread_text}\n\n"
        "Return ONLY valid JSON with these keys:\n"
        '  - "proposed_times": list of ISO-8601 datetime strings\n'
        '  - "attendees": list of email addresses\n'
        '  - "topic": one-line summary string\n'
        '  - "duration_minutes": integer, default 30 if not mentioned\n'
    )

    response = None
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a meeting parser. Return ONLY "
                "valid JSON. No markdown, no explanation, no code fences.",
                temperature=0.1,
            ),
        )

        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        result = json.loads(text.strip())
        return result

    except Exception as e:
        return {
            "parsing_error": str(e),
            "raw_response": getattr(response, "text", "") if response else "",
        }


def check_availability(time_min: str, time_max: str, credentials_json: str | None = None) -> bool:
    """
    Check whether the user's primary calendar is free during a time window.

    Parameters
    ----------
    time_min : str
        Start of the time window (ISO-8601).
    time_max : str
        End of the time window (ISO-8601).
    credentials_json : str | None
        JSON string of authorized user credentials (passed to the service builder).

    Returns
    -------
    bool
        True if the calendar is free (no busy intervals), False if busy
        or if an error occurs.
    """
    try:
        # Append "Z" (UTC) to times that lack timezone info
        if not time_min.endswith("Z") and "T" in time_min and "+" not in time_min[-6:] and "-" not in time_min[-6:]:
            time_min += "Z"
        if not time_max.endswith("Z") and "T" in time_max and "+" not in time_max[-6:] and "-" not in time_max[-6:]:
            time_max += "Z"

        service = build_calendar_service(credentials_json=credentials_json)
        body = {
            "timeMin": time_min,
            "timeMax": time_max,
            "items": [{"id": "primary"}],
        }
        freebusy = service.freebusy().query(body=body).execute()
        busy = freebusy.get("calendars", {}).get("primary", {}).get("busy", [])
        return len(busy) == 0
    except Exception:
        return False


def find_free_slot(
    proposed_times: list[str],
    duration_minutes: int,
    credentials_json: str | None = None,
) -> str | None:
    """
    Find the first free time slot among a list of proposed meeting times.

    Parameters
    ----------
    proposed_times : list of str
        ISO-8601 datetime strings representing proposed meeting start times.
    duration_minutes : int
        Duration of the meeting in minutes.
    credentials_json : str | None
        JSON string of authorized user credentials (passed through to availability check).

    Returns
    -------
    str | None
        The first free ISO-8601 time string, or None if all slots are busy
        or all strings are malformed.
    """
    from dateutil import parser

    for time_str in proposed_times:
        try:
            dt = parser.parse(time_str)
            time_min = dt.isoformat()
            end_dt = dt + datetime.timedelta(minutes=duration_minutes)
            time_max = end_dt.isoformat()
        except Exception:
            # Skip malformed time strings gracefully
            continue

        if check_availability(time_min, time_max, credentials_json=credentials_json):
            return time_str

    return None


def create_event(
    summary: str,
    start_time: str,
    duration_minutes: int,
    attendees: list[str],
    description: str = "",
    credentials_json: str | None = None,
) -> dict[str, Any]:
    """
    Create a Google Calendar event and send invitation emails to attendees.

    Parameters
    ----------
    summary : str
        Event title.
    start_time : str
        ISO-8601 datetime string for the event start.
    duration_minutes : int
        Duration of the event in minutes.
    attendees : list of str
        List of attendee email addresses.
    description : str
        Optional event description.
    credentials_json : str | None
        JSON string of authorized user credentials (passed to the service builder).

    Returns
    -------
    dict
        The created Google Calendar event resource.
    """
    from dateutil import parser

    start_dt = parser.parse(start_time)
    end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)

    event_body: dict[str, Any] = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "UTC",
        },
    }

    # Only include attendees that have valid emails (contain "@")
    valid_attendees = [
        {"email": email.strip()}
        for email in attendees
        if "@" in email
    ]
    if valid_attendees:
        event_body["attendees"] = valid_attendees

    service = build_calendar_service(credentials_json=credentials_json)
    event = (
        service.events()
        .insert(
            calendarId="primary",
            body=event_body,
            sendUpdates="all",
        )
        .execute()
    )
    return event
