#!/usr/bin/env python3
"""Dependency-free sendRichMessageDraft -> sendRichMessage canary."""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from typing import Any


def call(token: str, method: str, payload: dict[str, Any]) -> Any:
    url = f"https://api.telegram.org/bot{token}/{method}"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram HTTP {exc.code}: {detail}") from exc
    if not body.get("ok"):
        raise RuntimeError(f"Telegram API error: {body}")
    return body.get("result")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True)
    ap.add_argument("--chat-id", required=True, type=int, help="Private chat ID")
    ap.add_argument("--draft-id", type=int, default=None)
    ap.add_argument("--rtl", action="store_true")
    ap.add_argument("--pause", type=float, default=1.0)
    args = ap.parse_args()

    draft_id = args.draft_id or (int(time.time() * 1000) % 2_000_000_000) or 1
    draft_html = "<tg-thinking>Analyzing...</tg-thinking>"
    final_html = "<p><b>Canary complete.</b> Rich draft and final message succeeded.</p>"

    print(f"draft_id={draft_id}")
    call(args.token, "sendRichMessageDraft", {
        "chat_id": args.chat_id,
        "draft_id": draft_id,
        "rich_message": {"html": draft_html, "is_rtl": args.rtl},
        "can_stop": True,
        "keep_on_stop": True,
    })
    time.sleep(max(args.pause, 0))
    result = call(args.token, "sendRichMessage", {
        "chat_id": args.chat_id,
        "rich_message": {"html": final_html, "is_rtl": args.rtl},
    })
    print(f"message_id={result.get('message_id') if isinstance(result, dict) else result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
