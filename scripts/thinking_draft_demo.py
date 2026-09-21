#!/usr/bin/env python3
"""
Telegram Rich Message Thinking Draft Demo

Demonstrates the full lifecycle of sendRichMessageDraft with <tg-thinking>
and finalization via sendRichMessage. Uses only Python standard library
(zero third-party dependencies).

Usage:
    python3 thinking_draft_demo.py --token BOT_TOKEN --chat-id CHAT_ID
    python3 thinking_draft_demo.py --token BOT_TOKEN --chat-id CHAT_ID --thinking-text "Analyzing…"
    python3 thinking_draft_demo.py --token BOT_TOKEN --chat-id CHAT_ID --rtl --thinking-text "در حال پردازش…"

Lifecycle:
    1. Sends a thinking draft via sendRichMessageDraft with <tg-thinking>.
    2. Simulates background processing with phase-based draft updates.
    3. Sends the final rich message via sendRichMessage.
    4. Telegram automatically replaces the draft bubble with the final content.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import time
import urllib.error
import urllib.request


BASE_URL = "https://api.telegram.org/bot{token}/{method}"


def telegram_request(token: str, method: str, payload: dict) -> dict:
    """Send a POST request to the Telegram Bot API and return the parsed response."""
    url = BASE_URL.format(token=token, method=method)
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        print(f"[ERROR] {method} failed: HTTP {exc.code}", file=sys.stderr)
        print(f"[ERROR] Response: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"[ERROR] {method} network error: {exc.reason}", file=sys.stderr)
        sys.exit(1)

    if not body.get("ok"):
        desc = body.get("description", "Unknown error")
        print(f"[ERROR] {method} API error: {desc}", file=sys.stderr)
        sys.exit(1)

    return body


def send_thinking_draft(
    token: str,
    chat_id: int,
    draft_id: int,
    thinking_text: str,
    is_rtl: bool = False,
    extra_html: str = "",
) -> dict:
    """Send a thinking draft via sendRichMessageDraft."""
    inner_html = "<tg-thinking>{text}</tg-thinking>{extra}".format(
        text=html.escape(thinking_text),
        extra=extra_html,
    )
    payload = {
        "chat_id": chat_id,
        "draft_id": draft_id,
        "rich_message": {
            "html": inner_html,
            "is_rtl": is_rtl,
        },
        "can_stop": True,
        "keep_on_stop": True,
    }
    return telegram_request(token, "sendRichMessageDraft", payload)


def send_final_message(
    token: str,
    chat_id: int,
    rich_html: str,
    is_rtl: bool = False,
) -> dict:
    """Send the final rich message via sendRichMessage, replacing the draft."""
    payload = {
        "chat_id": chat_id,
        "rich_message": {
            "html": rich_html,
            "is_rtl": is_rtl,
        },
    }
    return telegram_request(token, "sendRichMessage", payload)


def run_demo(
    token: str,
    chat_id: int,
    thinking_text: str,
    is_rtl: bool,
    delay: float,
) -> None:
    """Execute the full thinking → processing → final message lifecycle."""
    draft_id = int(time.time() * 1000)
    print(f"[INFO] Starting thinking draft demo (draft_id={draft_id})")

    # ── Phase 1: Initial thinking state ──────────────────────────
    print(f"[Phase 1] Sending thinking draft: {thinking_text!r}")
    send_thinking_draft(token, chat_id, draft_id, thinking_text, is_rtl=is_rtl)
    print("[Phase 1] ✓ Draft sent — client shows frosted thinking bubble")

    time.sleep(delay)

    # ── Phase 2: Update thinking text (processing phase) ─────────
    phase2_text = "در حال پردازش داده‌ها…" if is_rtl else "Processing data…"
    print(f"[Phase 2] Updating thinking draft: {phase2_text!r}")
    send_thinking_draft(
        token,
        chat_id,
        draft_id,
        phase2_text,
        is_rtl=is_rtl,
        extra_html="<p>{}</p>".format(
            html.escape("۲ مورد از ۳ پردازش شد…" if is_rtl else "2 of 3 items processed…")
        ),
    )
    print("[Phase 2] ✓ Draft updated with progress")

    time.sleep(delay)

    # ── Phase 3: Final thinking update before result ─────────────
    phase3_text = "در حال آماده‌سازی نتایج…" if is_rtl else "Formatting results…"
    print(f"[Phase 3] Updating thinking draft: {phase3_text!r}")
    send_thinking_draft(token, chat_id, draft_id, phase3_text, is_rtl=is_rtl)
    print("[Phase 3] ✓ Draft updated — nearly done")

    time.sleep(delay)

    # ── Phase 4: Send final rich message ─────────────────────────
    if is_rtl:
        final_html = (
            "<h3>نتایج پردازش</h3>"
            "<p>پردازش با موفقیت انجام شد. <b>۳ مورد</b> یافت شد.</p>"
            "<table bordered compact>"
            "<tr><th>ردیف</th><th>نام</th><th>وضعیت</th></tr>"
            "<tr><td>۱</td><td>آلفا</td><td>فعال</td></tr>"
            "<tr><td>۲</td><td>بتا</td><td>در انتظار</td></tr>"
            "<tr><td>۳</td><td>گاما</td><td>فعال</td></tr>"
            "</table>"
        )
    else:
        final_html = (
            "<h3>Processing Results</h3>"
            "<p>Processing complete. <b>3 items</b> found.</p>"
            "<table bordered compact>"
            "<tr><th>ID</th><th>Name</th><th>Status</th></tr>"
            "<tr><td>1</td><td>Alpha</td><td>Active</td></tr>"
            "<tr><td>2</td><td>Beta</td><td>Pending</td></tr>"
            "<tr><td>3</td><td>Gamma</td><td>Active</td></tr>"
            "</table>"
        )

    print("[Phase 4] Sending final rich message…")
    result = send_final_message(token, chat_id, final_html, is_rtl=is_rtl)
    msg_id = result.get("result", {}).get("message_id", "?")
    print(f"[Phase 4] ✓ Final message sent (message_id={msg_id})")
    print("[Done] Telegram has replaced the thinking draft with the final content.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Telegram Rich Message Thinking Draft Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s --token 123:ABC --chat-id 456\n"
            "  %(prog)s --token 123:ABC --chat-id 456 --rtl --thinking-text 'در حال فکر…'\n"
            "  %(prog)s --token 123:ABC --chat-id 456 --delay 3\n"
        ),
    )
    parser.add_argument(
        "--token",
        required=True,
        help="Telegram bot token (e.g. 123456:ABC-DEF).",
    )
    parser.add_argument(
        "--chat-id",
        required=True,
        type=int,
        help="Target chat ID to send the demo messages to.",
    )
    parser.add_argument(
        "--thinking-text",
        default=None,
        help=(
            "Custom text for the thinking bubble. "
            "Defaults to an English or Persian string based on --rtl."
        ),
    )
    parser.add_argument(
        "--rtl",
        action="store_true",
        default=False,
        help="Enable RTL (right-to-left) mode for Persian/Arabic text.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Delay in seconds between phases (default: 3.0).",
    )

    args = parser.parse_args()

    thinking_text = args.thinking_text
    if thinking_text is None:
        thinking_text = (
            "در حال تحلیل و ساخت پیام غنی…" if args.rtl
            else "Analyzing your request and preparing a response…"
        )

    run_demo(
        token=args.token,
        chat_id=args.chat_id,
        thinking_text=thinking_text,
        is_rtl=args.rtl,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
