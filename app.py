"""
The Draft Desk - Streamlit UI for the Chief of Staff workflow.

Phases (driven by session_state.current_phase):
   1. Inbox & Triage
   2. Draft Generation
   3. Approval Gate
   4. Export Proof
"""

from __future__ import annotations

import json
import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlparse

import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow as GoogleFlow

# -----------------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="The Draft Desk",
    page_icon="✍️",
    layout="wide",
)

# -----------------------------------------------------------------------------
# Paths & constants
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
SAMPLE_THREADS_PATH = BASE_DIR / "sample_threads.json"

PHASES = [
    "Inbox & Triage",
    "Draft Generation",
    "Approval Gate",
    "Export Proof",
]

PRIORITY_CONFIG = {
    "urgent":      {"emoji": "🔴", "label": "Urgent"},
    "needs-reply": {"emoji": "⚪", "label": "Needs Reply"},
    "fyi":         {"emoji": "🟢", "label": "FYI"},
    "ignore":      {"emoji": "⚫", "label": "Ignore"},
}

# -----------------------------------------------------------------------------
# Local imports
# -----------------------------------------------------------------------------
import sys
# For development, we can still have these paths as fallbacks
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "Gmail-MCP-Server"))

# Import from root directory (deployment-friendly)
from triage import triage_inbox
from draft_machine import draft_reply, draft_reply_with_metadata
from engine import send_reply
from task_logger import log_action, get_action_log


# -----------------------------------------------------------------------------
# Lazy imports for calendar engine
# -----------------------------------------------------------------------------
@st.cache_resource
def get_calendar_engine():
    """Lazy import calendar_engine functions to avoid loading them eagerly.

    Returns
    -------
    tuple of (parse_meeting_request, find_free_slot, create_event)
    """
    import importlib
    mod = importlib.import_module("calendar_engine")
    return (mod.parse_meeting_request, mod.find_free_slot, mod.create_event)


# -----------------------------------------------------------------------------
# Session state initialization
# -----------------------------------------------------------------------------
def _init_session_state() -> None:
    defaults: dict[str, Any] = {
        "threads": [],
        "triaged": {},       # subject -> full triage result dict
        "drafts": {},        # thread_id -> {draft, metadata, thread}
        "approved": {},
        "rejected": [],
        "sent": [],
        "booked": {},
        "current_phase": "Inbox & Triage",
        "source": "Sample threads",
        "pipeline_running": False,
        "pipeline_log": [],
        "logged_in": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

_init_session_state()


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def load_sample_threads() -> list[dict[str, Any]]:
    if not SAMPLE_THREADS_PATH.exists():
        return []
    try:
        with SAMPLE_THREADS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def fetch_gmail_threads() -> list[dict[str, Any]]:
    """Fetch threads from Gmail via engine.py and normalize to our format.
    
    If Gmail authentication fails or any error occurs, automatically falls back
    to loading sample threads and updates the session state source accordingly.
    """
    from engine import fetch_threads, DEFAULT_MAX_RESULTS
    try:
        raw = fetch_threads(
            max_results=DEFAULT_MAX_RESULTS,
            credentials_json=st.session_state.get("google_credentials"),
        )
        if isinstance(raw, list) and raw:
            normalized = []
            for i, t in enumerate(raw):
                normalized.append({
                    "id": t.get("thread_id", f"gmail_{i}"),
                    "subject": t.get("subject", "(no subject)"),
                    "messages": [
                        {
                            "from": t.get("sender", ""),
                            "date": t.get("date", ""),
                            "body": t.get("body", "") or t.get("snippet", ""),
                        }
                    ],
                })
            return normalized
    except Exception:
        pass
    
    # Auto-fallback to sample threads on any Gmail failure
    st.session_state.source = "Sample threads"
    sample = load_sample_threads()
    if sample:
        st.warning("Gmail unavailable — switched to Sample threads automatically.")
    return sample


def get_triage_result(thread: dict[str, Any]) -> dict[str, Any]:
    """Return full triage result for a thread."""
    return st.session_state.triaged.get(thread.get("subject", ""), {})


def get_actionable_threads() -> list[dict[str, Any]]:
    """Return threads classified as urgent or needs-reply."""
    actionable = []
    for thread in st.session_state.threads:
        result = get_triage_result(thread)
        priority = result.get("priority", "")
        if priority in ("urgent", "needs-reply"):
            actionable.append(thread)
    return actionable


def render_thread_expander(thread: dict[str, Any], triage_result: dict) -> None:
    """Render a thread inside an st.expander with full message history."""
    subject = thread.get("subject", "(no subject)")
    messages = thread.get("messages", []) or []
    priority = triage_result.get("priority", "unknown")
    reason = triage_result.get("reason", "")

    cfg = PRIORITY_CONFIG.get(priority, {"emoji": "❓", "label": priority})
    label = f"{cfg['emoji']} {subject}"

    with st.expander(label, expanded=False):
        if reason:
            st.caption(f"**Reason:** {reason}")
        st.divider()
        for i, msg in enumerate(messages, start=1):
            st.markdown(
                f"**{msg.get('from', 'Unknown')}** · {msg.get('date', '')}"
            )
            st.write(msg.get("body", ""))
            if i < len(messages):
                st.divider()


# -----------------------------------------------------------------------------
# Pipeline wrappers (thin adapters used by run_full_pipeline)
# -----------------------------------------------------------------------------
def fetch_threads_via_engine() -> list[dict[str, Any]]:
    """Alias for fetch_gmail_threads — fetches and normalises Gmail threads."""
    return fetch_gmail_threads()


def triiage_threads(threads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run triage_inbox and store results in session state. Returns triaged list."""
    triaged_results = triage_inbox(threads)
    st.session_state.triaged = {}
    for r in triaged_results:
        subject = r.get("subject", "")
        st.session_state.triaged[subject] = r
    return triaged_results


def get_draft_reply(thread: dict[str, Any]) -> dict[str, Any]:
    """Return draft + metadata dict for a single thread via draft_reply_with_metadata."""
    return draft_reply_with_metadata(thread)


# -----------------------------------------------------------------------------
# Full pipeline
# -----------------------------------------------------------------------------
def run_full_pipeline() -> list[str]:
    """Run the complete inbox → triage → draft pipeline without rendering any UI.

    Steps
    -----
    1. Fetch threads from the source stored in st.session_state.source.
    2. Triage all fetched threads and store results in session state.
    3. Reset all downstream session state (drafts, approved, rejected, sent, booked).
    4. Draft replies for every urgent / needs-reply thread.
    5. Set current_phase to "Approval Gate".

    Returns
    -------
    list[str]
        Human-readable log lines describing what happened at each step.
        Errors are logged but never raise — if one draft fails the loop continues.
    """
    log: list[str] = []

    # ── Step 1: fetch threads ─────────────────────────────────────────────────
    source = st.session_state.get("source", "Sample threads")
    log.append(f"[1/5] Fetching threads (source: {source})...")
    try:
        if source == "Sample threads":
            threads = load_sample_threads()
        else:
            threads = fetch_threads_via_engine()

        if not threads:
            log.append("  ⚠ No threads returned. Aborting pipeline.")
            return log

        st.session_state.threads = threads
        log.append(f"  ✓ Fetched {len(threads)} thread(s).")
    except Exception as exc:
        log.append(f"  ✗ Fetch failed: {exc}")
        return log

    # ── Step 2: triage ────────────────────────────────────────────────────────
    log.append("[2/5] Triaging threads with AI...")
    try:
        triage_input = [
            {
                "sender": (t.get("messages") or [{}])[0].get("from", ""),
                "subject": t.get("subject", ""),
                "snippet": (t.get("messages") or [{}])[0].get("body", "")[:150],
            }
            for t in threads
        ]
        triiage_threads(triage_input)
        needs_reply_count = sum(
            1 for v in st.session_state.triaged.values()
            if isinstance(v, dict) and v.get("priority") in ("urgent", "needs-reply")
        )
        log.append(
            f"  ✓ Triaged {len(threads)} thread(s). "
            f"{needs_reply_count} need a reply."
        )
    except Exception as exc:
        log.append(f"  ✗ Triage failed: {exc}")
        return log

    # ── Step 3: reset downstream state ───────────────────────────────────────
    log.append("[3/5] Resetting downstream session state...")
    st.session_state.drafts = {}
    st.session_state.approved = {}
    st.session_state.rejected = []
    st.session_state.sent = []
    st.session_state.booked = {}
    log.append("  ✓ drafts / approved / rejected / sent / booked cleared.")

    # ── Step 4: draft replies for actionable threads ──────────────────────────
    actionable = [
        t for t in st.session_state.threads
        if get_triage_result(t).get("priority") in ("urgent", "needs-reply")
    ]
    log.append(f"[4/5] Drafting replies for {len(actionable)} actionable thread(s)...")

    for i, thread in enumerate(actionable, start=1):
        thread_id = thread.get("id", thread.get("subject", f"thread_{i}"))
        subject = thread.get("subject", "(no subject)")
        try:
            result = get_draft_reply(thread)
            st.session_state.drafts[thread_id] = {
                "draft": result["draft"],
                "model": result.get("model", ""),
                "reply_to": result.get("reply_to", ""),
                "char_count": result.get("char_count", 0),
                "thread": thread,
            }
            log.append(f"  ✓ [{i}/{len(actionable)}] Drafted: {subject[:60]}")
        except Exception as exc:
            error_msg = str(exc)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                friendly = "API limit reached — draft skipped."
            elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                friendly = "AI service temporarily unavailable — draft skipped."
            else:
                friendly = f"Error — {exc}"
            log.append(f"  ✗ [{i}/{len(actionable)}] {subject[:60]}: {friendly}")
            # Store a placeholder so the thread still appears in Approval Gate
            st.session_state.drafts[thread_id] = {
                "draft": "",
                "model": "",
                "reply_to": "",
                "char_count": 0,
                "thread": thread,
            }

    drafted_ok = sum(
        1 for d in st.session_state.drafts.values() if d.get("draft")
    )
    log.append(f"  ✓ {drafted_ok}/{len(actionable)} draft(s) generated successfully.")

    # ── Step 5: advance phase ─────────────────────────────────────────────────
    log.append("[5/5] Setting phase to Approval Gate...")
    st.session_state.current_phase = "Approval Gate"
    log.append("  ✓ Pipeline complete. Ready for review.")

    return log


# -----------------------------------------------------------------------------
# Pipeline execution UI
# -----------------------------------------------------------------------------
def render_pipeline_execution() -> None:
    """Execute the full pipeline with live progress UI.

    Runs fetch → triage → draft inline (not via run_full_pipeline) so each
    step can update the st.status container in real time. No return value —
    all results are written directly to session state.
    """
    log: list[str] = []

    with st.status("Running full pipeline...", expanded=True) as status:

        # ── Step 1: Fetch ─────────────────────────────────────────────────────
        status.update(label="Step 1/3: Fetching threads...")
        source = st.session_state.get("source", "Sample threads")
        try:
            if source == "Sample threads":
                threads = load_sample_threads()
            else:
                threads = fetch_threads_via_engine()

            if not threads:
                msg = "No threads returned — nothing to process."
                st.write(f"✗ {msg}")
                log.append(msg)
                status.update(label="Pipeline failed: no threads found.", state="error")
                st.session_state.pipeline_running = False
                return

            st.session_state.threads = threads
            msg = f"Fetched {len(threads)} thread(s) from {source}."
            st.write(f"✓ {msg}")
            log.append(msg)

        except Exception as exc:
            msg = f"Fetch failed: {exc}"
            st.write(f"✗ {msg}")
            log.append(msg)
            status.update(label="Pipeline failed during fetch.", state="error")
            st.session_state.pipeline_running = False
            return

        # ── Step 2: Triage ────────────────────────────────────────────────────
        status.update(label="Step 2/3: Triaging threads with AI...")
        try:
            triage_input = [
                {
                    "sender": (t.get("messages") or [{}])[0].get("from", ""),
                    "subject": t.get("subject", ""),
                    "snippet": (t.get("messages") or [{}])[0].get("body", "")[:150],
                }
                for t in threads
            ]
            triiage_threads(triage_input)

            needs_reply_count = sum(
                1 for v in st.session_state.triaged.values()
                if isinstance(v, dict) and v.get("priority") in ("urgent", "needs-reply")
            )
            msg = (
                f"Triaged {len(threads)} thread(s) — "
                f"{needs_reply_count} need a reply."
            )
            st.write(f"✓ {msg}")
            log.append(msg)

        except Exception as exc:
            msg = f"Triage failed: {exc}"
            st.write(f"✗ {msg}")
            log.append(msg)
            status.update(label="Pipeline failed during triage.", state="error")
            st.session_state.pipeline_running = False
            return

        # Reset downstream state after a successful triage
        st.session_state.drafts = {}
        st.session_state.approved = {}
        st.session_state.rejected = []
        st.session_state.sent = []
        st.session_state.booked = {}

        # ── Step 3: Draft loop ────────────────────────────────────────────────
        actionable = [
            t for t in st.session_state.threads
            if get_triage_result(t).get("priority") in ("urgent", "needs-reply")
        ]
        status.update(
            label=f"Step 3/3: Drafting replies for {len(actionable)} thread(s)..."
        )

        drafted_ok = 0
        for i, thread in enumerate(actionable, start=1):
            thread_id = thread.get("id", thread.get("subject", f"thread_{i}"))
            subject = thread.get("subject", "(no subject)")
            short = subject[:55]
            try:
                result = get_draft_reply(thread)
                st.session_state.drafts[thread_id] = {
                    "draft": result["draft"],
                    "model": result.get("model", ""),
                    "reply_to": result.get("reply_to", ""),
                    "char_count": result.get("char_count", 0),
                    "thread": thread,
                }
                drafted_ok += 1
                msg = f"[{i}/{len(actionable)}] Drafted: {short}"
                st.write(f"✓ {msg}")
                log.append(msg)

            except Exception as exc:
                error_msg = str(exc)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    friendly = "API limit reached — draft skipped."
                elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                    friendly = "AI service temporarily unavailable — draft skipped."
                else:
                    friendly = f"Error: {exc}"
                msg = f"[{i}/{len(actionable)}] {short}: {friendly}"
                st.write(f"✗ {msg}")
                log.append(msg)
                # Store empty placeholder so thread still appears in Approval Gate
                st.session_state.drafts[thread_id] = {
                    "draft": "",
                    "model": "",
                    "reply_to": "",
                    "char_count": 0,
                    "thread": thread,
                }

        summary = f"{drafted_ok}/{len(actionable)} draft(s) generated successfully."
        st.write(f"✓ {summary}")
        log.append(summary)

        status.update(
            label=f"Pipeline complete — {summary}",
            state="complete",
        )

    # ── Outside status block ──────────────────────────────────────────────────
    st.session_state.pipeline_log = log
    st.session_state.current_phase = "Approval Gate"
    st.session_state.pipeline_running = False
    st.rerun()


# -----------------------------------------------------------------------------
# Export helpers
# -----------------------------------------------------------------------------
def generate_proof_markdown() -> str:
    """Generate a markdown proof document with all approved drafts."""
    lines = []
    lines.append("# Draft Desk — Proof of Work")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append(f"**Total approved:** {len(st.session_state.approved)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for thread_id, approved_data in st.session_state.approved.items():
        thread = approved_data.get("thread", {})
        subject = thread.get("subject", "(no subject)")
        messages = thread.get("messages", []) or []
        draft_text = approved_data.get("draft", "")

        lines.append(f"## {subject}")
        lines.append("")
        lines.append("### Original Thread")
        for msg in messages:
            sender = msg.get("from", "Unknown")
            date = msg.get("date", "")
            body = msg.get("body", "").strip()
            lines.append(f"> **From:** {sender} · {date}")
            lines.append(">")
            for line in body.split("\n"):
                lines.append(f"> {line}")
            lines.append("")
        lines.append("### Draft Reply")
        lines.append("")
        lines.append("```")
        lines.append(draft_text)
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("")
    lines.append(
        "_Share with **#MyAIChiefOfStaff** to earn your Ghostwriter badge!_"
    )
    return "\n".join(lines)


def generate_proof_html() -> str:
    """Generate a styled HTML proof document with all approved drafts and action log."""
    approved = st.session_state.approved
    items_html = ""

    for thread_id, approved_data in approved.items():
        thread = approved_data.get("thread", {})
        subject = thread.get("subject", "(no subject)")
        messages = thread.get("messages", []) or []
        draft_text = approved_data.get("draft", "")

        # Build original messages HTML
        msgs_html = ""
        for msg in messages:
            sender = msg.get("from", "Unknown")
            date = msg.get("date", "")
            body = msg.get("body", "").strip().replace("\n", "<br>")
            msgs_html += f"""
            <div class="message">
                <div class="msg-header">{sender} · {date}</div>
                <div class="msg-body">{body}</div>
            </div>
            """

        items_html += f"""
        <div class="thread-card">
            <h2>{subject}</h2>
            <div class="grid">
                <div class="original">
                    <div class="label label-orange">📨 Original Thread</div>
                    {msgs_html}
                </div>
                <div class="draft-col">
                    <div class="label label-green">🤖 Draft Reply</div>
                    <pre>{draft_text}</pre>
                </div>
            </div>
        </div>
        """

    # Generate Action Log HTML
    action_log_html = ""
    action_entries = get_action_log()
    
    if action_entries:
        action_log_html = """
        <div class="action-log-section">
            <h2>📋 Action Log</h2>
            <div class="action-log">
        """
        
        for entry in action_entries:
            action_type = entry.get("action_type", "")
            thread_subject = entry.get("thread_subject", "")
            detail = entry.get("detail", "")
            timestamp_str = entry.get("timestamp", "")
            
            # Format timestamp as "Jan 01 02:30 PM"
            try:
                timestamp_obj = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                formatted_time = timestamp_obj.strftime("%b %d %I:%M %p")
            except:
                formatted_time = timestamp_str
            
            icon = "📝" if action_type.lower() == "sent" else "📅"
            action_log_html += f"""
                <div class="action-entry">
                    <div class="action-type">{icon} {action_type.upper()}</div>
                    <div class="action-subject">{thread_subject}</div>
                    <div class="action-detail"><code>{detail}</code></div>
                    <div class="action-time">{formatted_time}</div>
                </div>
            """
        
        action_log_html += """
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Draft Desk — Proof of Work</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: #0e1117;
            color: #fafafa;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            font-size: 2rem;
            margin-bottom: 8px;
        }}
        h2 {{
            font-size: 1.5rem;
            margin-bottom: 16px;
            color: #e0e0e0;
        }}
        .subtitle {{
            color: #888;
            margin-bottom: 32px;
        }}
        .thread-card {{
            background: #1a1b26;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .thread-card h2 {{
            margin-bottom: 16px;
            font-size: 1.25rem;
            color: #e0e0e0;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .original {{
            background: #262730;
            border-radius: 8px;
            padding: 16px;
            border-left: 4px solid #ff9800;
        }}
        .draft-col {{
            background: #262730;
            border-radius: 8px;
            padding: 16px;
            border-left: 4px solid #4caf50;
        }}
        .label {{
            font-weight: 600;
            margin-bottom: 12px;
            font-size: 0.9rem;
        }}
        .label-orange {{ color: #ff9800; }}
        .label-green {{ color: #4caf50; }}
        .message {{
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid #333;
        }}
        .message:last-child {{ border-bottom: none; }}
        .msg-header {{
            color: #4a9eff;
            font-size: 0.85rem;
            margin-bottom: 4px;
        }}
        .msg-body {{
            font-size: 0.9rem;
            line-height: 1.5;
            color: #d0d0d0;
        }}
        pre {{
            white-space: pre-wrap;
            font-size: 0.9rem;
            line-height: 1.5;
            color: #d0d0d0;
            font-family: 'Consolas', 'Courier New', monospace;
        }}
        .action-log-section {{
            background: #1a1b26;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .action-log {{
            display: grid;
            gap: 12px;
        }}
        .action-entry {{
            display: grid;
            grid-template-columns: 120px 2fr 2fr 120px;
            gap: 16px;
            padding: 12px;
            background: #262730;
            border-radius: 8px;
            align-items: center;
        }}
        .action-type {{
            font-weight: 600;
            color: #4a9eff;
        }}
        .action-subject {{
            font-weight: 600;
            color: #e0e0e0;
        }}
        .action-detail code {{
            background: #1a1b26;
            color: #4caf50;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
        }}
        .action-time {{
            color: #888;
            font-size: 0.85rem;
            text-align: right;
        }}
        .badge {{
            margin-top: 32px;
            text-align: center;
            padding: 16px;
            background: linear-gradient(135deg, #1a1b26, #262730);
            border-radius: 8px;
            color: #ffd700;
            font-style: italic;
        }}
        @media (max-width: 768px) {{
            .grid {{ grid-template-columns: 1fr; }}
            .action-entry {{ grid-template-columns: 1fr; text-align: center; }}
            .action-time {{ text-align: center; }}
            body {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
    <h1>✍️ Draft Desk — Proof of Work</h1>
    <div class="subtitle">
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} &nbsp;|&nbsp;
        Approved: {len(approved)} &nbsp;|&nbsp;
        Actions: {len(action_entries) if action_entries else 0}
    </div>
    {items_html}
    {action_log_html}
    <div class="badge">
        Share with <strong>#MyAIChiefOfStaff</strong> to earn your Ghostwriter badge!
    </div>
</body>
</html>"""
    return html


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
def render_sidebar() -> None:
    with st.sidebar:
        st.title("✍️ The Draft Desk")
        triaged_count = len(st.session_state.triaged)
        needs_reply_count = sum(
            1 for v in st.session_state.triaged.values()
            if isinstance(v, dict) and v.get("priority") == "needs-reply"
        )
        st.caption(
            f"Loaded: **{len(st.session_state.threads)}** thread(s)\n"
            f"Triaged: **{triaged_count}**\n"
            f"Needs reply: **{needs_reply_count}**\n"
            f"Drafts: **{len(st.session_state.drafts)}**\n"
            f"Approved: **{len(st.session_state.approved)}**\n"
            f"Rejected: **{len(st.session_state.rejected)}**"
        )
        st.divider()

        if st.button(
            "⚡ Run Full Pipeline",
            type="primary",
            use_container_width=True,
            key="run_pipeline_btn",
        ):
            st.session_state.pipeline_running = True
            st.rerun()
        st.caption("Fetches, triages, and drafts – stops at Approval Gate.")

        st.subheader("Source")
        st.session_state.source = st.radio(
            "source_radio",
            options=["Sample threads", "Gmail via engine.py"],
            index=0 if st.session_state.source == "Sample threads" else 1,
            label_visibility="collapsed",
            key="source_radio",
        )

        st.divider()
        st.subheader("Navigation")

        for phase in PHASES:
            is_current = st.session_state.current_phase == phase
            label = f"▶️ {phase}" if is_current else phase
            if st.button(label, key=f"nav_{phase}", use_container_width=True):
                st.session_state.current_phase = phase
                st.rerun()

        st.divider()


# -----------------------------------------------------------------------------
# Phase 1: Inbox & Triage
# -----------------------------------------------------------------------------
def render_inbox_phase() -> None:
    st.header("📥 Inbox & Triage")
    st.write(
        "Pull threads from the selected source, then triage them by priority. "
        "Once triaged, the highest-priority threads move to *Draft Generation*."
    )

    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        pull_clicked = st.button("Pull & Triage", type="primary", use_container_width=True)
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.threads = []
            st.session_state.triaged = {}
            st.session_state.drafts = {}
            st.session_state.approved = {}
            st.session_state.rejected = []
            st.rerun()

    if pull_clicked:
        source = st.session_state.source
        with st.spinner("Loading threads..."):
            if source == "Sample threads":
                loaded = load_sample_threads()
                if not loaded:
                    st.error(f"No threads found at `{SAMPLE_THREADS_PATH.name}`.")
                    return
            else:
                loaded = fetch_gmail_threads()
                if not loaded:
                    st.warning("No Gmail threads returned. Check credentials.")
                    return

        st.session_state.threads = loaded
        st.session_state.triaged = {}

        triage_input = [
            {
                "sender": (t.get("messages") or [{}])[0].get("from", ""),
                "subject": t.get("subject", ""),
                "snippet": (t.get("messages") or [{}])[0].get("body", ""),
            }
            for t in loaded
        ]

        with st.spinner("Triaging threads with AI..."):
            triaged_results = triage_inbox(triage_input)

        for r in triaged_results:
            subject = r.get("subject", "")
            st.session_state.triaged[subject] = r

        needs_reply = sum(
            1 for r in triaged_results if r.get("priority") == "needs-reply"
        )
        st.success(
            f"Loaded and triaged {len(loaded)} thread(s) — "
            f"{needs_reply} need a reply."
        )
        st.rerun()

    st.divider()

    threads = st.session_state.threads
    if not threads:
        st.info("No threads loaded yet. Click **Pull & Triage** to get started.")
        return

    groups: dict[str, list] = {p: [] for p in PRIORITY_CONFIG}
    for thread in threads:
        result = get_triage_result(thread)
        priority = result.get("priority", "ignore")
        if priority not in groups:
            priority = "ignore"
        groups[priority].append((thread, result))

    for priority, cfg in PRIORITY_CONFIG.items():
        items = groups[priority]
        if not items:
            continue
        st.subheader(f"{cfg['emoji']} {cfg['label']} ({len(items)})")
        for thread, triage_result in items:
            render_thread_expander(thread, triage_result)
        st.divider()

    needs_reply_threads = groups.get("needs-reply", [])
    urgent_threads = groups.get("urgent", [])
    actionable_count = len(needs_reply_threads) + len(urgent_threads)

    if actionable_count > 0:
        st.info(f"{actionable_count} thread(s) need a reply → go to **Draft Generation**")
    
    if st.session_state.threads:
        if st.button("Go to Draft Generation →", type="primary"):
            st.session_state.current_phase = "Draft Generation"
            st.rerun()


# -----------------------------------------------------------------------------
# Phase 2: Draft Generation
# -----------------------------------------------------------------------------
def render_draft_generation_phase() -> None:
    st.header("📝 Draft Generation")

    actionable = get_actionable_threads()

    if not actionable:
        st.warning("No actionable threads found. Go to **Inbox & Triage** first and pull threads.")
        return

    already_drafted = len(st.session_state.drafts)
    st.write(
        f"**{len(actionable)} actionable thread(s)** (urgent + needs-reply) ready for drafting. "
        f"{already_drafted} draft(s) already generated."
    )

    # ── Generate All Drafts button ────────────────────────────────────────────
    if st.button("✨ Generate All Drafts", type="primary"):
        progress_bar = st.progress(0, text="Starting draft generation...")
        total = len(actionable)

        for i, thread in enumerate(actionable):
            thread_id = thread.get("id", thread.get("subject", f"thread_{i}"))
            subject = thread.get("subject", "(no subject)")

            progress_bar.progress(
                (i) / total,
                text=f"Drafting {i + 1}/{total}: {subject[:50]}..."
            )

            try:
                result = draft_reply_with_metadata(thread)
                st.session_state.drafts[thread_id] = {
                    "draft": result["draft"],
                    "model": result.get("model", ""),
                    "reply_to": result.get("reply_to", ""),
                    "char_count": result.get("char_count", 0),
                    "thread": thread,
                }
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    st.warning(f"⏳ Quota reached on thread '{subject}'. Resets at 12:30 PM IST.")
                else:
                    st.error(f"Failed to draft '{subject}': {e}")
                st.session_state.drafts[thread_id] = {
                    "draft": "⏳ Quota reached — draft will generate when quota resets at 12:30 PM IST.",
                    "model": "",
                    "reply_to": "",
                    "char_count": 0,
                    "thread": thread,
                }

        progress_bar.progress(1.0, text="All drafts generated!")
        st.rerun()

    st.divider()

    # ── Display drafts ────────────────────────────────────────────────────────
    if not st.session_state.drafts:
        st.info("Click **Generate All Drafts** to create AI replies for all actionable threads.")
        return

    for thread_id, draft_data in st.session_state.drafts.items():
        thread = draft_data.get("thread", {})
        subject = thread.get("subject", "(no subject)")
        messages = thread.get("messages", []) or []
        latest_msg = messages[-1] if messages else {}

        with st.expander(f"📧 {subject}", expanded=True):
            col_left, col_right = st.columns([1, 1], gap="large")

            # Left: original thread latest message
            with col_left:
                st.markdown("**📨 Original Thread**")
                st.caption(
                    f"From: {latest_msg.get('from', 'Unknown')} · "
                    f"{latest_msg.get('date', '')}"
                )
                st.text_area(
                    "Thread content",
                    value=(latest_msg.get("body") or "").strip(),
                    height=250,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"thread_{thread_id}",
                )

            # Right: AI draft
            with col_right:
                st.markdown("**🤖 AI Draft Reply**")
                meta = draft_data
                st.caption(
                    f"Model: {meta.get('model', 'gemini-2.5-flash')} · "
                    f"To: {meta.get('reply_to', '')} · "
                    f"Chars: {meta.get('char_count', 0)}"
                )
                st.text_area(
                    "Draft content",
                    value=draft_data.get("draft", ""),
                    height=250,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"draft_{thread_id}",
                )

    st.divider()

    # ── Bottom CTA ────────────────────────────────────────────────────────────
    if st.session_state.drafts:
        st.success(f"✅ {len(st.session_state.drafts)} draft(s) ready → go to **Approval Gate**")
        if st.button("Go to Approval Gate →", type="primary"):
            st.session_state.current_phase = "Approval Gate"
            st.rerun()


# -----------------------------------------------------------------------------
# Approval Gate CSS (matching instructor's approval_gate.py)
# -----------------------------------------------------------------------------
def _apply_approval_gate_css() -> None:
    st.markdown(
        """
        <style>
        .thread-box {
            background-color: #262730;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #4a9eff;
        }
        
        .draft-box {
            background-color: #1a1b26;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #4caf50;
            margin-bottom: 15px;
        }
        
        .status-approved {
            background-color: #1b4d34;
            border-radius: 5px;
            padding: 10px;
            color: #4caf50;
            font-weight: bold;
            text-align: center;
        }
        
        .status-rejected {
            background-color: #4d1b1b;
            border-radius: 5px;
            padding: 10px;
            color: #f44336;
            font-weight: bold;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Phase 3: Approval Gate
# -----------------------------------------------------------------------------
def render_thread_html(thread: dict[str, Any]) -> str:
    """Return thread as HTML string with proper line breaks."""
    lines = []
    if "subject" in thread:
        lines.append(f"<p><strong>Subject:</strong> {thread['subject']}</p>")
    for msg in thread.get("messages", []):
        sender = msg.get("from", "unknown sender")
        date = msg.get("date", "unknown date")
        body = msg.get("body", "").strip().replace("\n", "<br>")
        lines.append(f"<p><strong>From:</strong> {sender}</p>")
        lines.append(f"<p><strong>Date:</strong> {date}</p>")
        lines.append(f"<p>{body}</p>")
    return "\n".join(lines)


def render_approval_gate_phase() -> None:
    _apply_approval_gate_css()
    st.header("✅ Approval Gate")
    st.write(
        "Review each AI-generated draft below. You can **Approve**, **Edit**, "
        "or **Reject** each draft. Only explicitly approved drafts move to Export."
    )

    # ── Pipeline execution log ────────────────────────────────────────────────
    pipeline_log = st.session_state.get("pipeline_log", [])
    if pipeline_log:
        with st.expander("🗒 Pipeline Execution Log", expanded=False):
            for entry in pipeline_log:
                entry_upper = entry.upper()
                if "ERROR" in entry_upper or "FAILED" in entry_upper or entry.lstrip().startswith("✗"):
                    st.write(f"✗ {entry}" if not entry.lstrip().startswith("✗") else entry)
                else:
                    st.write(f"✓ {entry}" if not entry.lstrip().startswith("✓") else entry)
            st.divider()
            if st.button("Clear log", key="clear_pipeline_log"):
                st.session_state.pipeline_log = []
                st.rerun()
        st.divider()

    if not st.session_state.drafts:
        st.warning("No drafts to review. Go to **Draft Generation** first and generate drafts.")
        return

    # Running counts
    approved_count = len(st.session_state.approved)
    rejected_count = len(st.session_state.rejected)
    total = len(st.session_state.drafts)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total drafts", total)
    col2.metric("✅ Approved", approved_count)
    col3.metric("❌ Rejected", rejected_count)
    col4.metric("⏳ Pending", total - approved_count - rejected_count)

    st.divider()

    all_reviewed = True
    for thread_id, draft_data in st.session_state.drafts.items():
        thread = draft_data.get("thread", {})
        subject = thread.get("subject", "(no subject)")
        messages = thread.get("messages", []) or []
        latest_msg = messages[-1] if messages else {}

        # Determine status for this draft
        if thread_id in st.session_state.approved:
            status = "approved"
        elif thread_id in st.session_state.rejected:
            status = "rejected"
        else:
            status = "pending"
            all_reviewed = False

        with st.container():
            st.subheader(f"📧 {subject}")

            # Show status indicator
            if status == "approved":
                st.markdown(
                    '<div class="status-approved">✅ Approved - Ready to Send</div>',
                    unsafe_allow_html=True,
                )
            elif status == "rejected":
                st.markdown(
                    '<div class="status-rejected">❌ Rejected - Discarded</div>',
                    unsafe_allow_html=True,
                )

            # Two-column layout (like instructor)
            col_left, col_right = st.columns([1, 1], gap="large")

            with col_left:
                st.subheader("Thread History")
                thread_html = render_thread_html(thread)
                st.markdown(
                    f'<div class="thread-box">{thread_html}</div>',
                    unsafe_allow_html=True,
                )

            with col_right:
                st.subheader("AI Generated Draft")

                # Show metadata line
                meta = draft_data
                st.caption(
                    f"Model: {meta.get('model', 'gemini-2.5-flash')} · "
                    f"To: {meta.get('reply_to', '')} · "
                    f"Chars: {meta.get('char_count', 0)}"
                )

                if status == "approved":
                    # Allow re-editing an approved draft
                    if st.session_state.get(f"editing_{thread_id}"):
                        st.divider()
                        st.subheader("Edit Draft")

                        edit_widget_key = f"edited_draft_area_{thread_id}"

                        # Seed from the currently-approved text (not the original quota placeholder)
                        if edit_widget_key not in st.session_state:
                            current_approved_text = st.session_state.approved[thread_id].get("draft", "")
                            # Clear quota placeholder so the user starts with a blank slate
                            if current_approved_text.startswith("⏳") or "quota" in current_approved_text.lower():
                                current_approved_text = ""
                            st.session_state[edit_widget_key] = current_approved_text

                        st.text_area(
                            "Modify the draft:",
                            height=300,
                            key=edit_widget_key,
                        )

                        save_col, cancel_col = st.columns(2)
                        with save_col:
                            if st.button("✅ Save & Approve", type="primary",
                                    key=f"save_edit_approved_{thread_id}"):
                                st.session_state.approved[thread_id] = {
                                    "draft": st.session_state[edit_widget_key],
                                    "thread": thread,
                                    "metadata": draft_data,
                                }
                                st.session_state[f"editing_{thread_id}"] = False
                                del st.session_state[edit_widget_key]
                                st.rerun()
                        with cancel_col:
                            if st.button("✖ Cancel", key=f"cancel_edit_approved_{thread_id}"):
                                st.session_state[f"editing_{thread_id}"] = False
                                st.session_state.pop(edit_widget_key, None)
                                st.rerun()
                    else:
                        approved_text = st.session_state.approved[thread_id].get("draft", "")
                        st.markdown(
                            f'<div class="draft-box"><pre style="white-space: pre-wrap; margin: 0;">{approved_text}</pre></div>',
                            unsafe_allow_html=True,
                        )
                        edit_row, _ = st.columns([1, 3])
                        with edit_row:
                            if st.button("✏️ Edit", key=f"edit_approved_{thread_id}", use_container_width=True):
                                st.session_state[f"editing_{thread_id}"] = True
                                st.rerun()
                        st.success("✅ Approved & saved")

                    # Extract recipient email from thread's last message
                    messages = thread.get("messages", []) or []
                    latest_msg = messages[-1] if messages else {}
                    raw_from = latest_msg.get("from", "")
                    if "<" in raw_from:
                        recipient = raw_from.split("<")[1].strip(">")
                    else:
                        recipient = raw_from.strip()

                    subject = thread.get("subject", "")
                    approved_draft = st.session_state.approved[thread_id].get("draft", "")

                    # Check if already sent
                    is_sent = thread_id in st.session_state.sent
                    is_booked = thread_id in st.session_state.booked

                    # Check if this is a meeting request thread
                    triage_result = get_triage_result(thread)
                    category = triage_result.get("category", "")
                    _subject_lower = thread.get("subject", "").lower()
                    _body_lower = " ".join(
                        m.get("body", "") for m in thread.get("messages", [])
                    ).lower()
                    _meeting_kws = [
                        "meeting", "call", "sync", "slot", "schedule",
                        "30 min", "30-min", "would you be free", "free for a",
                        "calendar invite", "slots open", "book a", "are you free",
                        "time slot", "catch up", "zoom", "hop on", "quick chat",
                        "15 min", "walkthrough",
                    ]
                    is_meeting = (
                        category in ("meeting_request", "meeting-request")
                        or any(kw in _subject_lower for kw in _meeting_kws)
                        or any(kw in _body_lower for kw in _meeting_kws)
                    )

                    if is_meeting:
                        # Always show two columns: Send (or sent indicator) + Book Meeting
                        btn_col_a, btn_col_b = st.columns(2)

                        with btn_col_a:
                            if is_sent:
                                st.success("📤 Sent successfully")
                            else:
                                if st.button("📤 Send", key=f"send_btn_{thread_id}",
                                            use_container_width=True):
                                    try:
                                        result = send_reply(
                                            thread_id=thread_id,
                                            to=recipient,
                                            subject=subject,
                                            body=approved_draft,
                                            credentials_json=st.session_state.get("google_credentials"),
                                        )
                                        st.session_state.sent.append(thread_id)
                                        log_action("sent", subject, "Email sent successfully", thread_id)

                                        st.rerun()
                                    except Exception as e:
                                        error_msg = str(e)
                                        if "could not locate runnable browser" in error_msg:
                                            st.error("Your API limit has been reached.")
                                        elif "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                                            st.error("Your API limit has been reached.")
                                        elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                                            st.error("The AI service is temporarily unavailable. Please try again in a moment.")
                                        else:
                                            st.error("Your API limit has been reached.")

                        with btn_col_b:
                            if is_booked:
                                booked_data = st.session_state.booked[thread_id]
                                link = booked_data.get("htmlLink", "")
                                if link:
                                    st.markdown(f"[📅 View Calendar Event]({link})")
                                else:
                                    st.success("📅 Booked")
                            else:
                                if st.button("📅 Book Meeting", key=f"book_btn_{thread_id}",
                                            use_container_width=True):
                                    try:
                                        parse_req, find_slot, create_evt = get_calendar_engine()

                                        with st.spinner("Parsing meeting request..."):
                                            parsed = parse_req(thread)

                                        if "parsing_error" in parsed:
                                            parse_err = parsed['parsing_error']
                                            if "429" in str(parse_err) or "RESOURCE_EXHAUSTED" in str(parse_err):
                                                st.error("Your API limit has been reached.")
                                            elif "503" in str(parse_err) or "UNAVAILABLE" in str(parse_err):
                                                st.error("The AI service is temporarily unavailable. Please try again in a moment.")
                                            else:
                                                st.error("Unable to parse meeting details. Please try again.")
                                        else:
                                            st.info(
                                                f"**Topic:** {parsed.get('topic', '')}\n\n"
                                                f"**Proposed times:** {parsed.get('proposed_times', [])}\n\n"
                                                f"**Attendees:** {parsed.get('attendees', [])}\n\n"
                                                f"**Duration:** {parsed.get('duration_minutes', 30)} min"
                                            )

                                            proposed = parsed.get("proposed_times", [])
                                            duration = parsed.get("duration_minutes", 30)

                                            with st.spinner("Checking availability..."):
                                                free_slot = find_slot(
                                                    proposed,
                                                    duration,
                                                    credentials_json=st.session_state.get("google_credentials"),
                                                )

                                            if free_slot:
                                                with st.spinner("Creating calendar event..."):
                                                    event = create_evt(
                                                        summary=parsed.get("topic", subject),
                                                        start_time=free_slot,
                                                        duration_minutes=duration,
                                                        attendees=parsed.get("attendees", []),
                                                        description=approved_draft,
                                                        credentials_json=st.session_state.get("google_credentials"),
                                                    )
                                                st.session_state.booked[thread_id] = event
                                                link = event.get("htmlLink", "")
                                                log_action("booked", subject, f"Meeting booked: {link}", thread_id)
                                                
                                                if link:
                                                    st.success(f"✅ Meeting booked! [📅 View Event]({link})")
                                                else:
                                                    st.success("✅ Meeting booked!")
                                                st.rerun()
                                            else:
                                                st.warning("No free slot found among proposed times.")
                                    except Exception as e:
                                        error_msg = str(e)
                                        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                                            st.error("Your API limit has been reached.")
                                        elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                                            st.error("The AI service is temporarily unavailable. Please try again in a moment.")
                                        else:
                                            st.error("Something went wrong while booking the meeting. Please try again.")
                    else:
                        # Regular thread: just a Send button
                        if is_sent:
                            st.success("📤 Sent successfully")
                        else:
                            if st.button("📤 Send", key=f"send_btn_{thread_id}",
                                         use_container_width=True):
                                try:
                                    result = send_reply(
                                        thread_id=thread_id,
                                        to=recipient,
                                        subject=subject,
                                        body=approved_draft,
                                        credentials_json=st.session_state.get("google_credentials"),
                                    )
                                    st.session_state.sent.append(thread_id)
                                    log_action("sent", subject, "Email sent successfully", thread_id)

                                    st.rerun()
                                except Exception as e:
                                    error_msg = str(e)
                                    if "could not locate runnable browser" in error_msg:
                                        st.error("Your API limit has been reached.")
                                    elif "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                                        st.error("Your API limit has been reached.")
                                    elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                                        st.error("The AI service is temporarily unavailable. Please try again in a moment.")
                                    else:
                                        st.error("Your API limit has been reached.")

                elif status == "rejected":
                    st.markdown(
                        f'<div class="draft-box"><pre style="white-space: pre-wrap; margin: 0;">{draft_data.get("draft", "")}</pre></div>',
                        unsafe_allow_html=True,
                    )
                    # Regenerate button for rejected drafts
                    if st.button("🔄 REGENERATE", key=f"regen_rejected_{thread_id}", use_container_width=True):
                        with st.spinner("Regenerating draft..."):
                            try:
                                result = draft_reply_with_metadata(thread)
                                st.session_state.drafts[thread_id] = {
                                    "draft": result["draft"],
                                    "model": result.get("model", ""),
                                    "reply_to": result.get("reply_to", ""),
                                    "char_count": result.get("char_count", 0),
                                    "thread": thread,
                                }
                            except Exception as e:
                                st.error(f"Regeneration failed: {e}")
                            st.rerun()

                else:
                    # Pending: show draft in a draft-box
                    st.markdown(
                        f'<div class="draft-box"><pre style="white-space: pre-wrap; margin: 0;">{draft_data.get("draft", "")}</pre></div>',
                        unsafe_allow_html=True,
                    )

                    # Three action buttons (like instructor)
                    st.divider()
                    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])

                    with btn_col1:
                        if st.button("✅ APPROVE", key=f"approve_btn_{thread_id}", use_container_width=True):
                            st.session_state.approved[thread_id] = {
                                "draft": draft_data.get("draft", ""),
                                "thread": thread,
                                "metadata": draft_data,
                            }
                            st.rerun()

                    with btn_col2:
                        if st.button("✏️ EDIT", key=f"edit_btn_{thread_id}", use_container_width=True):
                            st.session_state[f"editing_{thread_id}"] = True
                            st.rerun()

                    # Look for this section inside render_approval_gate_phase:

                    with btn_col3:
                        # REPLACE EVERYTHING BELOW THIS LINE inside the 'with' block
                        if st.button("🔄 REGENERATE", key=f"regen_pending_{thread_id}", use_container_width=True):
                            with st.spinner("Regenerating draft..."):
                                try:
                                    result = draft_reply_with_metadata(thread)
                                    st.session_state.drafts[thread_id] = {
                                        "draft": result["draft"],
                                        "model": result.get("model", ""),
                                        "reply_to": result.get("reply_to", ""),
                                        "char_count": result.get("char_count", 0),
                                        "thread": thread,
                                    }
                                    st.rerun() # Added rerun here to update the UI immediately
                                except Exception as e:
                                    # This logic now catches the quota error and shows a clear message
                                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                                        st.error("Quota exceeded! Please wait a minute before trying again.")
                                    else:
                                        st.error(f"Regeneration failed: {e}")

                    # Edit mode (like instructor)
                    if st.session_state.get(f"editing_{thread_id}"):
                        st.divider()
                        st.subheader("Edit Draft")

                        edit_widget_key = f"edited_draft_area_{thread_id}"

                        # Seed the widget state only on first entry into edit mode
                        if edit_widget_key not in st.session_state:
                            initial = draft_data.get("draft", "")
                            # Clear quota placeholder so the user starts fresh
                            if initial.startswith("⏳") or "quota" in initial.lower():
                                initial = ""
                            st.session_state[edit_widget_key] = initial

                        st.text_area(
                            "Modify the draft:",
                            height=300,
                            key=edit_widget_key,
                        )

                        if st.button("✅ Approve Edited Version", type="primary",
                                     key=f"approve_edit_btn_{thread_id}"):
                            st.session_state.approved[thread_id] = {
                                "draft": st.session_state[edit_widget_key],
                                "thread": thread,
                                "metadata": draft_data,
                            }
                            st.session_state[f"editing_{thread_id}"] = False
                            del st.session_state[edit_widget_key]
                            st.rerun()

            st.divider()

    # When all drafts are reviewed
    if all_reviewed and total > 0:
        st.balloons()
        st.success("🎉 All drafts have been reviewed!")
        if st.button("Go to Export Proof →", type="primary"):
            st.session_state.current_phase = "Export Proof"
            st.rerun()


# -----------------------------------------------------------------------------
# Phase 4: Export Proof
# -----------------------------------------------------------------------------
def render_export_proof_phase() -> None:
    st.header("📄 Export Proof")

    if not st.session_state.approved:
        st.warning("No approved drafts to export. Go to **Approval Gate** first and approve some drafts.")
        return

    st.write(
        f"**{len(st.session_state.approved)}** approved draft(s) ready for export. "
        "Download your proof of work as Markdown or HTML."
    )

    st.divider()

    # Preview all approved drafts side-by-side
    st.subheader("Preview of Approved Drafts")
    for thread_id, approved_data in st.session_state.approved.items():
        thread = approved_data.get("thread", {})
        subject = thread.get("subject", "(no subject)")
        messages = thread.get("messages", []) or []
        draft_text = approved_data.get("draft", "")

        with st.expander(f"📧 {subject}", expanded=True):
            col_left, col_right = st.columns([1, 1], gap="large")
            with col_left:
                st.markdown("**📨 Original Thread**")
                for msg in messages:
                    st.caption(f"{msg.get('from', 'Unknown')} · {msg.get('date', '')}")
                    safe_body = msg.get("body", "").replace("\n", "<br>")
                    st.markdown(f"<div style='white-space: pre-wrap;'>{safe_body}</div>", unsafe_allow_html=True)
                    st.divider()
            with col_right:
                st.markdown("**🤖 Approved Draft Reply**")
                st.text_area(
                    "draft_preview",
                    value=draft_text,
                    height=200,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"export_draft_{thread_id}",
                )

    st.divider()

    # Action Log section
    st.subheader("📋 Action Log")
    action_entries = get_action_log()
    
    if not action_entries:
        st.info("No actions logged yet.")
    else:
        for entry in action_entries:
            action_type = entry.get("action_type", "")
            thread_subject = entry.get("thread_subject", "")
            detail = entry.get("detail", "")
            timestamp_str = entry.get("timestamp", "")
            
            # Format timestamp as "Jan 01 02:30 PM"
            try:
                # Parse ISO timestamp and format
                timestamp_obj = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                formatted_time = timestamp_obj.strftime("%b %d %I:%M %p")
            except:
                formatted_time = timestamp_str
            
            # Create four columns for display
            col1, col2, col3, col4 = st.columns([1, 3, 3, 2])
            
            with col1:
                icon = "📝" if action_type.lower() == "sent" else "📅"
                st.write(f"{icon} {action_type.upper()}")
            
            with col2:
                st.markdown(f"**{thread_subject}**")
            
            with col3:
                st.code(detail)
            
            with col4:
                st.caption(formatted_time)

    st.divider()

    # Generate export content
    markdown_content = generate_proof_markdown()
    html_content = generate_proof_html()

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.download_button(
            label="📥 Download Proof (Markdown)",
            data=markdown_content,
            file_name=f"draft_desk_proof_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with btn_col2:
        st.download_button(
            label="📥 Download Proof (HTML)",
            data=html_content,
            file_name=f"draft_desk_proof_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
            use_container_width=True,
        )

    st.divider()
    st.info("📢 Share with **#MyAIChiefOfStaff** to earn your Ghostwriter badge!")


# -----------------------------------------------------------------------------
# Phase dispatch
# -----------------------------------------------------------------------------
def render_phase(phase: str) -> None:
    if phase == "Inbox & Triage":
        render_inbox_phase()
    elif phase == "Draft Generation":
        render_draft_generation_phase()
    elif phase == "Approval Gate":
        render_approval_gate_phase()
    elif phase == "Export Proof":
        render_export_proof_phase()
    else:
        st.warning(f"Unknown phase: {phase}")


# -----------------------------------------------------------------------------
# OAuth 2.0 constants & helpers
# -----------------------------------------------------------------------------

# Gmail + Calendar scopes required by the application
OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
]

# Path to the downloaded credentials.json (installed app type)
_CREDS_PATH = BASE_DIR / "credentials.json"

# PKCE verifiers securely cached on the server to survive redirects
@st.cache_resource
def _get_pkce_store() -> dict[str, str]:
    return {}


def _save_oauth_pkce(state: str, code_verifier: str) -> None:
    _get_pkce_store()[state] = code_verifier


def _pop_oauth_pkce(state: str) -> str | None:
    return _get_pkce_store().pop(state, None)


def _make_flow(redirect_uri: str | None = None, state: str | None = None) -> GoogleFlow:
    import streamlit as st

    secret_creds = st.secrets.get("google_credentials")
    if secret_creds:
        client_config = {"web": dict(secret_creds)}
        flow = GoogleFlow.from_client_config(
            client_config,
            scopes=OAUTH_SCOPES,
            state=state,
        )
    else:
        flow = GoogleFlow.from_client_secrets_file(
            str(_CREDS_PATH),
            scopes=OAUTH_SCOPES,
            state=state,
        )

    if redirect_uri is not None:
        flow.redirect_uri = redirect_uri
    return flow


def _get_app_url() -> str:
    import os
    # Streamlit Cloud always mounts repositories in the /mount/src directory
    if os.path.exists("/mount/src"):
        return "https://sree-kirthana-chief-of-staff.streamlit.app"
    # Otherwise, fallback to local testing
    return "http://localhost:8501"


def _exchange_code_for_creds(authorization_response) -> Credentials:
    """Exchange the OAuth authorization code (returned in the callback URL)
    for a refreshable Credentials object.

    Recreates the PKCE flow using the OAuth ``state`` from the callback URL
    to recover the code_verifier from server-side storage (session state alone
    does not survive the Google redirect).  The redirect URI used here *must*
    exactly match the one registered in the Google Cloud Console.
    """
    params = dict(authorization_response)
    oauth_state = params.get("state")
    if not oauth_state:
        raise ValueError("OAuth callback missing state parameter.")

    oauth_verifier = _pop_oauth_pkce(oauth_state)
    if not oauth_verifier:
        oauth_verifier = st.session_state.get("oauth_verifier")
    if not oauth_verifier:
        raise ValueError("OAuth session expired. Please sign in again.")

    app_url = _get_app_url()
    redirect_uri = f"{app_url}/"
    flow = _make_flow(redirect_uri=redirect_uri, state=oauth_state)
    flow.code_verifier = oauth_verifier
    # fetch_token expects the full callback URL; build it from query params
    callback_url = f"{redirect_uri}?{urlencode(params, doseq=True)}"
    flow.fetch_token(authorization_response=callback_url)
    return flow.credentials


# -----------------------------------------------------------------------------
# OAuth callback handler
# -----------------------------------------------------------------------------
def _handle_oauth_callback() -> bool:
    """Check URL query parameters for an OAuth authorization code and, if
    present, exchange it for credentials and store them in session state.

    Returns True if a callback was successfully processed (the page should be
    re-rendered immediately).
    """
    params = st.query_params

    # Google appends ?code=XXXXX&scope=YYYYY when redirecting back
    code = params.get("code")
    if not code:
        return False

    try:
        creds = _exchange_code_for_creds(params)
        st.session_state.google_credentials = creds.to_json()
        st.session_state.logged_in = True
        st.session_state.pop("oauth_state", None)
        st.session_state.pop("oauth_verifier", None)
        # Clear the query parameters so the code is not visible after refresh
        st.query_params.clear()
        return True
    except Exception as exc:
        st.error(f"Authentication failed: {exc}")
        st.query_params.clear()
        return False


# -----------------------------------------------------------------------------
# Landing page (public-facing, no auth required)
# -----------------------------------------------------------------------------
def render_landing_page() -> None:
    """Render the public landing page with Aurora Glassmorphism UI, app explanation, 
    and a real "Sign in with Google" button that triggers the OAuth 2.0 Web flow."""
    
    # --- OAuth setup (Unchanged) ---
    app_url = _get_app_url()
    redirect_uri = f"{app_url}/"

    flow = _make_flow(redirect_uri=redirect_uri)
    auth_url, state = flow.authorization_url(
        access_type="offline",      
        include_granted_scopes="true",
        prompt="consent",           
    )
    st.session_state["oauth_state"] = state
    st.session_state["oauth_verifier"] = flow.code_verifier
    _save_oauth_pkce(state, flow.code_verifier)

    # --- CSS Injection ---
    st.markdown(
        """
        <style>
        /* The Aurora Background */
        .stApp {
            background: 
                radial-gradient(circle at 15% 50%, rgba(45, 11, 63, 0.6), transparent 30%),
                radial-gradient(circle at 85% 30%, rgba(27, 5, 58, 0.8), transparent 30%),
                radial-gradient(circle at 50% 80%, rgba(13, 33, 79, 0.6), transparent 40%),
                #040b16 !important;
            background-attachment: fixed !important;
            color: #FAFAFA;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Glitter/Stars Effect Overlay */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                radial-gradient(1.5px 1.5px at 20px 30px, #ffffff, rgba(0,0,0,0)),
                radial-gradient(1px 1px at 40px 70px, #ffffff, rgba(0,0,0,0)),
                radial-gradient(2px 2px at 50px 160px, rgba(255,255,255,0.8), rgba(0,0,0,0)),
                radial-gradient(1px 1px at 90px 40px, #ffffff, rgba(0,0,0,0)),
                radial-gradient(1.5px 1.5px at 130px 80px, #ffffff, rgba(0,0,0,0)),
                radial-gradient(1px 1px at 160px 120px, #ffffff, rgba(0,0,0,0));
            background-repeat: repeat;
            background-size: 200px 200px;
            opacity: 0.35;
            z-index: 0;
            pointer-events: none;
        }

        /* Hide default Streamlit elements for a clean canvas */
        #MainMenu, header, footer {visibility: hidden;}

        /* Container and Glass Cards */
        .landing-wrapper {
            position: relative;
            z-index: 1;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, border 0.3s ease;
        }
        .glass-card:hover {
            transform: translateY(-2px);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }

        .card-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #ffffff;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 0.75rem;
        }

        /* Hero Section */
        .hero-section {
            text-align: center;
            margin-bottom: 3.5rem;
            margin-top: 2rem;
        }
        .hero-title {
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 800;
            background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            line-height: 1.2;
        }
        .hero-subtitle {
            font-size: 1.25rem;
            color: #a0aec0;
            margin-bottom: 2rem;
        }

        /* Typography */
        p, li {
            line-height: 1.6;
            color: #d1d5db;
            font-size: 1.05rem;
        }
        ul {
            margin-left: 1.5rem;
            margin-bottom: 1rem;
        }
        li { margin-bottom: 0.75rem; }
        strong { color: #ffffff; font-weight: 600; }

        /* Links */
        .footer-links a {
            color: #a5b4fc;
            text-decoration: none;
            margin-right: 1.5rem;
            font-weight: 600;
            transition: color 0.2s ease;
        }
        .footer-links a:hover {
            color: #ffffff;
            text-decoration: underline;
        }
        .disclaimer {
            font-size: 0.85rem;
            color: #888;
            margin-top: 2rem;
            font-style: italic;
            border-top: 1px solid rgba(255,255,255,0.05);
            padding-top: 1rem;
        }

        /* The Custom Google Auth Button */
        .google-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 14px 32px;
            background: rgba(255, 255, 255, 0.08);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            cursor: pointer;
            pointer-events: auto;
        }
        .google-btn:hover {
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.4);
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- HTML Structure ---
    st.markdown(
        f"""
        <div class="landing-wrapper">
            
            <div class="glass-card">
                <div class="card-title">Who I Am</div>
                <p>I’m <strong>V Sree Kirthana</strong>, an AI specialist, full-stack developer, and automation engineer based in Hyderabad, India. Currently pursuing my B.Tech in Computer Science with a specialization in Artificial Intelligence and Machine Learning (AIML), my core focus is bridging the gap between raw datasets and production-ready machine learning architectures.</p>
                <p>I engineer automated, self-sustaining AI workflows and the full-stack systems required to support them. My practical experience includes processing analytical data and building predictive algorithms as a Data Science Intern at CodSoft, alongside building robust web frameworks during my Full-Stack Development stint at Cognifyz Technologies. I've also advanced my capabilities in prompt engineering and next-gen autonomous systems through the Outskill GenAI Mastermind Program. Whether I am integrating generative AI tools, optimizing data pipelines, or writing core Python logic, I don't just write code—I architect intelligent solutions that solve real-world bottlenecks.</p>
            </div>

            <div class="hero-section">
                <div class="hero-title">Chief of Staff AI</div>
                <div class="hero-subtitle">Intelligent Triage & Autonomous Scheduling for your Inbox.</div>
                <a href="{auth_url}" target="_top" class="google-btn">
                    🔑 Sign in with Google
                </a>
            </div>

            <div class="glass-card">
                <div class="card-title">What This Is</div>
                <p>Meet your new fully functional AI agent. <strong>Chief of Staff AI</strong> acts as a ruthless gatekeeper for your attention. It connects securely to your Google account and automatically classifies your incoming emails into four buckets: <strong>Urgent</strong>, <strong>Needs Reply</strong>, <strong>FYI</strong>, and <strong>Ignore</strong>. You only give your energy to what actually matters, while the AI handles the heavy lifting of reading, sorting, and drafting.</p>
                <p>Want to skip the manual steps? Hit the <strong>Run Full Pipeline</strong> button to instantly fetch your emails, triage them, generate all necessary drafts, and jump straight to the Approval Gate.</p>
            </div>

            <div class="glass-card">
                <div class="card-title">Inside the Engine: The Four Phases</div>
                <p>This application operates on a strict, transparent four-step pipeline:</p>
                <ul>
                    <li><strong>Phase 1: Inbox & Triage</strong><br>The agent pulls your live email threads and uses AI to analyze the context, intent, and urgency of every message, assigning a strict priority level to each one.</li>
                    <li><strong>Phase 2: Draft Generation</strong><br>For any email flagged as <em>Urgent</em> or <em>Needs Reply</em>, the AI instantly generates a highly contextual, professional draft response.</li>
                    <li><strong>Phase 3: Approval Gate (Human-in-the-Loop)</strong><br><strong>Total Control.</strong> The AI generates the responses, but it never sends an email without your explicit permission. You are in the driver's seat with three options for every draft:
                        <ul>
                            <li><strong>Regenerate:</strong> Don't like the AI's first attempt? Click this to generate a brand new response.</li>
                            <li><strong>Edit:</strong> Jump in and manually tweak the text exactly how you want it.</li>
                            <li><strong>Approve:</strong> Once the draft is perfect, approve it.</li>
                        </ul>
                        Only after you hit Approve will the <strong>Send</strong> button appear, allowing you to dispatch the email directly from the app. Mistakes do not make it to your outbox.
                    </li>
                    <li><strong>Phase 4: Export Proof</strong><br>A complete audit trail of the AI's work. Once your triage is complete, you can download a full Proof of Work report as a cleanly formatted <strong>Markdown</strong> or <strong>HTML file</strong>.</li>
                </ul>
            </div>

            <div class="glass-card">
                <div class="card-title">Smart Calendar Scheduling</div>
                <p>More than just an email drafter, this agent understands time. If an incoming email asks for a meeting or proposes a time, the AI parses the request, checks your availability, and finds a free slot. Upon your approval, it automatically schedules the event and bookmarks it directly onto your <strong>Google Calendar</strong>.</p>
            </div>

            <div class="glass-card">
                <div class="card-title">Architecture & Timeline</div>
                <p>This agent is powered by a robust, modern tech stack designed for speed and security:</p>
                <ul>
                    <li><strong>Core Logic:</strong> Python</li>
                    <li><strong>Frontend UI:</strong> Streamlit (Custom Aurora Glassmorphism)</li>
                    <li><strong>AI Engine:</strong> Google Gemini 2.5 Flash</li>
                    <li><strong>Cloud Infrastructure:</strong> Google Cloud Platform (OAuth 2.0 Web Flow)</li>
                    <li><strong>Integrations:</strong> Gmail API, Google Calendar API</li>
                </ul>
                <p>I architected, built, and deployed this entire system from the ground up in <strong>2 Weeks</strong>.</p>
            </div>

            <div class="glass-card">
                <div class="card-title">Connect With Me</div>
                <div class="footer-links">
                    <a href="https://bold.pro/" target="_blank">Bold.pro</a>
                    <a href="https://www.linkedin.com/in/v-sree-kirthana/" target="_blank">LinkedIn</a>
                    <br><br>
                    <a href="https://raw.githubusercontent.com/sreekirthana123/Chief-Of-Staff-Application/master/PRIVACY.md" target="_blank" style="font-size:0.9em; font-weight:normal;">Privacy Policy</a>
                    <a href="https://raw.githubusercontent.com/sreekirthana123/Chief-Of-Staff-Application/master/TERMS.md" target="_blank" style="font-size:0.9em; font-weight:normal;">Terms & Conditions</a>
                </div>
                <p class="disclaimer">Note: This application currently runs on a free-tier API. If you encounter an "API limit reached" error, I apologize for the inconvenience! A future update is coming soon to upgrade the model to a paid version for uninterrupted access.</p>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> None:
    # ── OAuth callback handling (runs on every page load) ──────────────
    if _handle_oauth_callback():
        st.rerun()

    # ── Unauthenticated → show landing page ────────────────────────────
    if not st.session_state.get("logged_in", False):
        render_landing_page()
        return

    # ── Authenticated → full application ───────────────────────────────
    render_sidebar()
    if st.session_state.get("pipeline_running"):
        render_pipeline_execution()
    else:
        render_phase(st.session_state.current_phase)


if __name__ == "__main__":
    main()
