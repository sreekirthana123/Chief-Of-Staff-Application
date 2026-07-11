import os
import json
from dotenv import load_dotenv
# Upgraded to the current Google GenAI SDK package
from google import genai
from google.genai import types

load_dotenv()

# Initialize the new SDK client syntax
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def triage_inbox(threads: list) -> list:
    """
    Processes all emails in a single batch API call to optimize
    and protect your daily request quota.
    """
    if not threads:
        return []

    # Format the entire inbox collection into a single string text block
    emails_input = ""
    for idx, thread in enumerate(threads):
        emails_input += f"--- EMAIL INDEX: {idx} ---\n"
        emails_input += f"Sender: {thread.get('sender', '')}\n"
        emails_input += f"Subject: {thread.get('subject', '')}\n"
        emails_input += f"Preview: {thread.get('snippet', '')}\n\n"

    prompt = f"""
    You are an intelligent email assistant helping triage an inbox.
    Analyze the following list of email metadata segments and classify each one.

    {emails_input}

    Use these priority definitions strictly:
    - "urgent": Only for genuine emergencies — security breaches, account compromised, payment failures, data loss, legal notices. Do NOT classify an email as urgent just because its subject line says "urgent" or "needs immediate reply" — that is the sender's opinion, not yours.
    - "needs-reply": Any email that requires a human response, including meeting requests, scheduling, work questions, cost or billing discussions, follow-ups, or collaboration requests.
    - "fyi": Informational emails that do not need a reply — newsletters, notifications, receipts, announcements.
    - "ignore": Spam, promotions, marketing, unsubscribe-worthy content.

    Return a JSON array containing objects matching this schema context format:
    [
    {{
        "index": <int matching the email index above>,
        "priority": "<urgent | needs-reply | fyi | ignore>",
        "category": "<meeting_request | follow-up | newsletter | billing | job-app | social | admin>",
        "reason": "<one sentence explaining why>" }}
    ]
    """

    try:
        # Request a strict structured JSON array back from Gemini 2.5 Flash
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        # Safely extract and map the JSON results back to the original threads
        classifications = json.loads(response.text)

        # Build an indexed dictionary map of the classifications
        class_map = {item["index"]: item for item in classifications if "index" in item}

        # Keywords that strongly indicate a meeting/scheduling request
        MEETING_KEYWORDS = [
            "free for a", "would you be free", "30-minute call", "30 minute call",
            "slots open", "calendar invite", "call", "meet", "meeting", "schedule",
            "slot", "slots", "available", "free for", "30-minute", "15-minute",
            "zoom", "invite", "book a", "would you be", "are you free", "time slot",
            "catch up", "sync", "walkthrough", "walk you through", "hop on", "quick chat",
        ]

        triaged = []
        for idx, thread in enumerate(threads):
            label = class_map.get(idx, {"priority": "unknown", "category": "unknown", "reason": "unknown"})
            priority = label.get("priority", "unknown").lower()
            category = label.get("category", "unknown").lower()

            # Override: if the content looks like a meeting/scheduling request,
            # force to needs-reply regardless of what AI returned
            combined = (thread.get("subject", "") + " " + thread.get("snippet", "")).lower()
            if any(kw in combined for kw in MEETING_KEYWORDS):
                priority = "needs-reply"
                category = "meeting_request"
                label["reason"] = "Email contains a meeting or scheduling request."

            # Combine email data with AI classification labels
            triaged.append({
                **thread,
                "priority": priority,
                "category": category,
                "reason": label.get("reason", "unknown")
            })

        # Sort based on the instructor's exact sorting rules
        priority_order = {"urgent": 0, "needs-reply": 1, "fyi": 2, "ignore": 3, "unknown": 4}
        triaged.sort(key=lambda x: priority_order.get(x['priority'], 4))
        return triaged

    except Exception as e:
        print(f"Batch triage failed: {e}. Applying robust keyword fallback rules.")
        triaged = []
        for thread in threads:
            subject = thread.get('subject', '').lower()
            sender = thread.get('sender', '').lower()
            snippet = thread.get('snippet', '').lower()
            combined = subject + " " + snippet

            priority = "fyi"
            category = "admin"
            reason = "Automated email processing fallback."

            meeting_keywords = [
                "needs immediate reply",
                "needs reply",
                "immediate reply",
                "free for a",
                "would you be free",
                "30-minute call",
                "30 minute call",
                "slots open",
                "calendar invite",
                "call", "meet", "meeting", "schedule", "calendar",
                "slot", "slots", "available", "free for", "30-minute",
                "15-minute", "zoom", "invite", "book a", "would you be",
                "are you free", "time slot", "catch up",
                "sync", "walkthrough", "walk you through", "30 minute",
                "15 minute", "hop on", "quick chat", "review"
            ]
            if any(kw in combined for kw in meeting_keywords):
                priority = "needs-reply"
                category = "meeting_request"
                reason = "Email contains a meeting or scheduling request."
            elif any(kw in combined for kw in [
                "action required", "urgent", "reminder", "asap",
                "immediately", "critical", "deadline", "due today"
            ]):
                priority = "urgent"
                category = "job-app"
                reason = "Time-sensitive action required."
            elif any(kw in combined for kw in [
                "newsletter", "unsubscribe", "promotion", "offer",
                "sale", "discount", "marketing"
            ]) or "linkedin" in sender or "noreply" in sender:
                priority = "fyi"
                category = "newsletter"
                reason = "Promotional or newsletter email."

            triaged.append({
                **thread,
                "priority": priority,
                "category": category,
                "reason": reason
            })

        priority_order = {"urgent": 0, "needs-reply": 1,
                         "fyi": 2, "ignore": 3, "unknown": 4}
        triaged.sort(key=lambda x: priority_order.get(x['priority'], 4))
        return triaged


def format_digest(results: list) -> None:
    from datetime import datetime

    group_order = ["urgent", "needs-reply", "fyi", "ignore", "unknown"]
    priority_label = {
        "urgent": "URGENT",
        "needs-reply": "NEEDS-REPLY",
        "fyi": "FYI",
        "ignore": "IGNORE",
        "unknown": "UNKNOWN",
    }

    today = datetime.now().strftime("%Y-%m-%d")
    total = len(results)

    # Header
    print("=" * 60)
    print(f"INBOX DIGEST | {today} | {total} thread(s)")
    print("=" * 60)

    if total == 0:
        print("(no threads to display)")
        return

    # Walk groups in display order and emit a separator between them.
    first_group_emitted = False
    for group in group_order:
        group_items = [r for r in results if r.get("priority") == group]
        if not group_items:
            continue

        if first_group_emitted:
            print("-" * 60)

        first_group_emitted = True

        for r in group_items:
            label = priority_label.get(group, group.upper())
            sender = r.get("sender", "")
            subject = r.get("subject", "")
            reason = r.get("reason", "")
            print(f"[{label}] {sender} | {subject} - {reason}")


if __name__ == "__main__":
    sample_threads = [
        {
            "sender": "no-reply@google.com",
            "subject": "Security alert",
            "snippet": "This email is an official security alert from Google regarding account access...",
            "priority": "urgent",
            "category": "admin",
            "reason": "This email is an official security alert from Google regarding account access, which requires immediate attention to verify if the action was authorized or if the account is compromised."
        },
        {
            "sender": "teamzoom@zoom.us",
            "subject": "Explore advanced features for enhanced collaboration.",
            "snippet": "This email from Zoom is a promotional message encouraging the user...",
            "priority": "fyi",
            "category": "newsletter",
            "reason": "This email from Zoom is a promotional message encouraging the user to upgrade to advanced product features."
        }
    ]

    # Run format_digest directly on these mock classified threads to verify the divider line
    format_digest(sample_threads)
