#!/usr/bin/env python3
"""Conservative structural preflight for Telegram Bot API rich-message JSON.

This validator intentionally checks a high-value subset of Bot API 10.3. It is
not a replacement for Telegram's server-side validation or framework models.
It is designed to catch common generated-code regressions before an API call.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

MAX_CHARS = 32768
MAX_BLOCKS = 500
MAX_DEPTH = 16
MAX_MEDIA = 50
MAX_TABLE_COLUMNS = 20
MEDIA_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
BUTTON_ACTIONS = {
    "url",
    "callback_data",
    "web_app",
    "login_url",
    "switch_inline_query",
    "switch_inline_query_current_chat",
    "switch_inline_query_chosen_chat",
    "copy_text",
    "disabled",
}


def utf8_bytes(value: str) -> int:
    return len(value.encode("utf-8"))


def validate_message(msg: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sources = [key for key in ("html", "markdown", "blocks") if key in msg and msg[key] is not None]
    if len(sources) != 1:
        errors.append("InputRichMessage must contain exactly one of html, markdown, or blocks")

    # Telegram limits rich-message text to 32,768 UTF-8 characters. For HTML
    # and Markdown we conservatively check source code points. Markup is part
    # of the source but not necessarily part of rendered text, so this can be
    # stricter than Telegram and is intentionally a preflight guard only.
    for key in ("html", "markdown"):
        value = msg.get(key)
        if value is not None:
            if not isinstance(value, str):
                errors.append(f"{key} must be a string")
            elif len(value) > MAX_CHARS:
                errors.append(f"{key} source exceeds conservative {MAX_CHARS}-character preflight budget")

    media = msg.get("media")
    if media is not None:
        if not isinstance(media, list):
            errors.append("media must be a list")
        else:
            if len(media) > MAX_MEDIA:
                errors.append(f"media contains more than {MAX_MEDIA} items")
            seen: set[str] = set()
            for i, item in enumerate(media):
                if not isinstance(item, dict):
                    errors.append(f"media[{i}] must be an object")
                    continue
                ident = item.get("id")
                if not isinstance(ident, str) or not MEDIA_ID.fullmatch(ident):
                    errors.append(f"media[{i}].id must match [A-Za-z0-9_-]{{1,64}}")
                elif ident in seen:
                    errors.append(f"duplicate media id: {ident}")
                else:
                    seen.add(ident)
                if "media" not in item:
                    errors.append(f"media[{i}].media is required")

    blocks = msg.get("blocks")
    if blocks is not None:
        if not isinstance(blocks, list):
            errors.append("blocks must be a list")
        else:
            counter = [0]
            for i, block in enumerate(blocks):
                _validate_block(block, f"blocks[{i}]", 1, counter, errors)
            if counter[0] > MAX_BLOCKS:
                errors.append(
                    f"rich-message structural block count {counter[0]} exceeds {MAX_BLOCKS}; "
                    "Telegram counts nested blocks, list items, and table rows"
                )
            text_chars = sum(_block_text_chars(block) for block in blocks)
            if text_chars > MAX_CHARS:
                errors.append(f"structured rich text count {text_chars} exceeds {MAX_CHARS} characters")
    return errors


def _validate_block(block: Any, path: str, depth: int, counter: list[int], errors: list[str]) -> None:
    if depth > MAX_DEPTH:
        errors.append(f"{path} exceeds nesting depth {MAX_DEPTH}")
        return
    if not isinstance(block, dict):
        errors.append(f"{path} must be an object")
        return

    counter[0] += 1
    kind = block.get("type")
    if not isinstance(kind, str) or not kind:
        errors.append(f"{path}.type is required")
        return

    if kind == "table":
        if "rows" in block:
            errors.append(f"{path}: InputRichBlockTable uses cells, not rows")
        cells = block.get("cells")
        if not isinstance(cells, list) or not cells:
            errors.append(f"{path}.cells must be a non-empty two-dimensional list")
        else:
            # Telegram's 500-block limit explicitly counts table rows.
            counter[0] += len(cells)
            _validate_table_grid(cells, path, errors)

    if kind == "buttons":
        buttons = block.get("buttons")
        if not isinstance(buttons, list) or not (1 <= len(buttons) <= 8):
            errors.append(f"{path}.buttons must contain 1-8 buttons")
        else:
            for i, button in enumerate(buttons):
                _validate_button(button, f"{path}.buttons[{i}]", errors)
        align = block.get("align")
        if align is not None and align not in {"left", "center", "right"}:
            errors.append(f"{path}.align must be left, center, or right")

    nested = block.get("blocks")
    if isinstance(nested, list):
        for i, child in enumerate(nested):
            _validate_block(child, f"{path}.blocks[{i}]", depth + 1, counter, errors)

    items = block.get("items")
    if isinstance(items, list):
        # Telegram's 500-block limit explicitly counts list items.
        counter[0] += len(items)
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"{path}.items[{i}] must be an object")
                continue
            item_blocks = item.get("blocks")
            if not isinstance(item_blocks, list):
                errors.append(f"{path}.items[{i}].blocks must be a list")
                continue
            for j, child in enumerate(item_blocks):
                _validate_block(child, f"{path}.items[{i}].blocks[{j}]", depth + 1, counter, errors)


def _validate_table_grid(cells: list[Any], path: str, errors: list[str]) -> None:
    """Validate high-value table constraints without inventing a rectangular-row rule.

    Telegram's own Rich HTML examples contain rows with different numbers of
    cells, so this preflight does not require equal row widths. It tracks
    rowspans only to estimate effective occupied columns and enforce the
    documented 20-column maximum.
    """
    active: dict[int, int] = {}  # column -> remaining future rows occupied

    for r, row in enumerate(cells):
        if not isinstance(row, list) or not row:
            errors.append(f"{path}.cells[{r}] must be a non-empty list")
            active = {c: n - 1 for c, n in active.items() if n - 1 > 0}
            continue

        occupied = set(active)
        new_spans: dict[int, int] = {}
        cursor = 0

        for c, cell in enumerate(row):
            cell_path = f"{path}.cells[{r}][{c}]"
            if not isinstance(cell, dict):
                errors.append(f"{cell_path} must be an object")
                continue

            colspan = cell.get("colspan", 1)
            rowspan = cell.get("rowspan", 1)
            if not isinstance(colspan, int) or isinstance(colspan, bool) or colspan < 1:
                errors.append(f"{cell_path}.colspan must be a positive integer")
                colspan = 1
            if not isinstance(rowspan, int) or isinstance(rowspan, bool) or rowspan < 1:
                errors.append(f"{cell_path}.rowspan must be a positive integer")
                rowspan = 1

            align = cell.get("align")
            if align is not None and align not in {"left", "center", "right"}:
                errors.append(f"{cell_path}.align must be left, center, or right")
            valign = cell.get("valign")
            if valign is not None and valign not in {"top", "middle", "bottom"}:
                errors.append(f"{cell_path}.valign must be top, middle, or bottom")

            while any(col in occupied for col in range(cursor, cursor + colspan)):
                cursor += 1

            if cursor + colspan > MAX_TABLE_COLUMNS:
                errors.append(f"{cell_path} makes the effective table wider than {MAX_TABLE_COLUMNS} columns")

            for col in range(cursor, cursor + colspan):
                occupied.add(col)
                if rowspan > 1:
                    new_spans[col] = max(new_spans.get(col, 0), rowspan - 1)
            cursor += colspan

        if occupied and max(occupied) + 1 > MAX_TABLE_COLUMNS:
            errors.append(f"{path}.cells[{r}] exceeds {MAX_TABLE_COLUMNS} effective table columns")

        aged = {col: remaining - 1 for col, remaining in active.items() if remaining - 1 > 0}
        for col, remaining in new_spans.items():
            aged[col] = max(aged.get(col, 0), remaining)
        active = aged


def _validate_button(button: Any, path: str, errors: list[str]) -> None:
    if not isinstance(button, dict):
        errors.append(f"{path} must be an object")
        return
    actions = [key for key in BUTTON_ACTIONS if key in button and button[key] not in (None, False)]
    if len(actions) != 1:
        errors.append(f"{path} must contain exactly one action field")
        return

    action = actions[0]
    if action == "callback_data":
        data = button.get("callback_data")
        if not isinstance(data, str) or not (1 <= utf8_bytes(data) <= 64):
            errors.append(f"{path}.callback_data must be 1-64 UTF-8 bytes")
    if action == "login_url":
        value = button.get("login_url")
        url = value.get("url") if isinstance(value, dict) else value
        if not isinstance(url, str) or not url.startswith("https://"):
            errors.append(f"{path}.login_url must use HTTPS")

    style = button.get("style")
    if style is not None and style not in {"primary", "success", "danger", "link"}:
        errors.append(f"{path}.style is invalid")
    if style == "link" and action != "callback_data":
        errors.append(f"{path}: style=link is only valid for callback_data")


def _rich_text_chars(value: Any) -> int:
    if isinstance(value, str):
        return len(value)
    if isinstance(value, list):
        return sum(_rich_text_chars(v) for v in value)
    if not isinstance(value, dict):
        return 0
    kind = value.get("type")
    if kind == "custom_emoji":
        alt = value.get("alternative_text")
        return len(alt) if isinstance(alt, str) else 0
    if kind == "mathematical_expression":
        expression = value.get("expression")
        return len(expression) if isinstance(expression, str) else 0
    if kind == "button":
        button = value.get("button")
        return _rich_text_chars(button.get("text")) if isinstance(button, dict) else 0
    return _rich_text_chars(value.get("text"))


def _block_text_chars(block: Any) -> int:
    if not isinstance(block, dict):
        return 0
    total = 0
    for key in ("text", "summary", "credit", "caption"):
        if key in block:
            total += _rich_text_chars(block[key])
    if block.get("type") == "mathematical_expression":
        expression = block.get("expression")
        if isinstance(expression, str):
            total += len(expression)
    if block.get("type") == "buttons":
        for button in block.get("buttons", []):
            if isinstance(button, dict):
                total += _rich_text_chars(button.get("text"))
    if block.get("type") == "table":
        for row in block.get("cells", []):
            if isinstance(row, list):
                for cell in row:
                    if isinstance(cell, dict):
                        total += _rich_text_chars(cell.get("text"))
    nested = block.get("blocks")
    if isinstance(nested, list):
        total += sum(_block_text_chars(child) for child in nested)
    items = block.get("items")
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict) and isinstance(item.get("blocks"), list):
                total += sum(_block_text_chars(child) for child in item["blocks"])
    return total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("ERROR: root must be a JSON object", file=sys.stderr)
        return 2
    errors = validate_message(data)
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print("OK: structural rich-message preflight passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
