#!/usr/bin/env python3
"""Repository-level validation for the telegram-rich-ui skill."""
from __future__ import annotations

import json
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "agents/openai.yaml",
    "metadata/hermes.yaml",
    "references/SOURCES.md",
    "references/rich-formatting-overview.md",
    "references/tables-and-grids.md",
    "references/rich-buttons-and-colors.md",
    "references/slideshow-and-media.md",
    "references/custom-emojis-and-stickers.md",
    "references/thinking-drafts-and-streaming.md",
    "references/ephemeral-messages.md",
    "references/aiogram-python-recipes.md",
    "references/grammy-cloudflare-recipes.md",
    "references/compatibility-and-fallbacks.md",
    "references/ui-design-patterns.md",
    "scripts/validate_rich_message.py",
    "scripts/legacy_fallback.py",
    "scripts/thinking_draft_demo.py",
    "assets/templates/product-catalog-card.html",
    "assets/emoji-catalog/catalog.json",
    "assets/emoji-catalog/catalog.csv",
    "assets/emoji-catalog/curated-ui.json",
    "assets/emoji-catalog/regional-packs.json",
    "assets/emoji-catalog/sources.json",
    "scripts/search_emoji.py",
    "scripts/validate_emoji_catalog.py",
    "scripts/enrich_custom_emoji.py",
    "scripts/import_emoji_pack.py",
    "assets/templates/invoice-receipt.html",
    "assets/templates/persistent-menu-rich.html",
    "assets/templates/persian-rtl-dashboard.html",
    "assets/aiogram-starter/main.py",
    "assets/grammy-cloudflare-worker/src/index.ts",
]


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def check_frontmatter(errors: list[str]) -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return fail(errors, "SKILL.md must start with YAML frontmatter")
    try:
        _, front, _ = text.split("---", 2)
    except ValueError:
        return fail(errors, "SKILL.md frontmatter is malformed")
    keys = []
    for line in front.splitlines():
        if line and not line.startswith((" ", "\t", "#")) and ":" in line:
            keys.append(line.split(":", 1)[0].strip())
    if keys != ["name", "description"]:
        fail(errors, f"SKILL.md frontmatter keys must be exactly name, description; got {keys}")
    if "name: telegram-rich-ui" not in front:
        fail(errors, "SKILL.md name must be telegram-rich-ui")


def check_local_references(errors: list[str]) -> None:
    pattern = re.compile(r"(?:`|\()((?:references|scripts|templates|assets|agents|metadata)/[^`)\s]+)")
    for md in list(ROOT.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        for match in pattern.finditer(text):
            raw = match.group(1).rstrip(".,;:")
            if "*" in raw or "<" in raw:
                continue
            target = ROOT / raw
            if not target.exists():
                fail(errors, f"broken local reference in {md.relative_to(ROOT)}: {raw}")


def check_tocs(errors: list[str]) -> None:
    for md in (ROOT / "references").glob("*.md"):
        lines = md.read_text(encoding="utf-8").splitlines()
        if len(lines) > 100:
            head = "\n".join(lines[:35]).lower()
            if "## table of contents" not in head:
                fail(errors, f"{md.relative_to(ROOT)} has {len(lines)} lines but no early Table of contents")


def check_regressions(errors: list[str]) -> None:
    text_files = list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.py")) + list(ROOT.rglob("*.ts")) + list(ROOT.rglob("*.html"))
    for path in text_files:
        text = path.read_text(encoding="utf-8")
        # The name may appear only in explicit warnings that say it does not exist.
        for line_no, line in enumerate(text.splitlines(), 1):
            if "editRichMessageText" in line and not any(token in line.lower() for token in ("no ", "not", "nonexistent", "invented")):
                fail(errors, f"possible invented Telegram method at {path.relative_to(ROOT)}:{line_no}")
        if path.name == "tables-and-grids.md" and re.search(r'"rows"\s*:', text):
            fail(errors, "tables-and-grids.md reintroduced a JSON table rows field")
        if "no 429" in text.lower() and "do not" not in text.lower():
            fail(errors, f"unsupported no-429 guarantee in {path.relative_to(ROOT)}")


def check_python(errors: list[str]) -> None:
    paths = list((ROOT / "scripts").glob("*.py"))
    starter = ROOT / "assets/aiogram-starter/main.py"
    if starter.exists():
        paths.append(starter)
    with tempfile.TemporaryDirectory(prefix="telegram-rich-ui-pyc-") as tmp:
        tmpdir = Path(tmp)
        for index, path in enumerate(paths):
            try:
                py_compile.compile(
                    str(path),
                    cfile=str(tmpdir / f"{index}.pyc"),
                    doraise=True,
                )
            except py_compile.PyCompileError as exc:
                fail(errors, f"Python syntax error in {path.relative_to(ROOT)}: {exc.msg}")


def check_json(errors: list[str]) -> None:
    for path in ROOT.rglob("*.json"):
        # wrangler.jsonc and tsconfig are not strict JSON fixtures and use .jsonc/.json respectively.
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(errors, f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def check_fixtures(errors: list[str]) -> None:
    validator = ROOT / "scripts/validate_rich_message.py"
    valid = ROOT / "tests/fixtures/valid-table.json"
    valid_rowspan = ROOT / "tests/fixtures/valid-table-rowspan.json"
    invalid = ROOT / "tests/fixtures/invalid-table-rows.json"
    if valid.exists():
        proc = subprocess.run([sys.executable, str(validator), str(valid)], capture_output=True, text=True)
        if proc.returncode != 0:
            fail(errors, f"valid fixture failed: {proc.stdout}{proc.stderr}")
    if valid_rowspan.exists():
        proc = subprocess.run([sys.executable, str(validator), str(valid_rowspan)], capture_output=True, text=True)
        if proc.returncode != 0:
            fail(errors, f"valid rowspan fixture failed: {proc.stdout}{proc.stderr}")
    if invalid.exists():
        proc = subprocess.run([sys.executable, str(validator), str(invalid)], capture_output=True, text=True)
        if proc.returncode == 0:
            fail(errors, "invalid rows fixture unexpectedly passed")


def check_emoji_catalog(errors: list[str]) -> None:
    validator = ROOT / "scripts/validate_emoji_catalog.py"
    proc = subprocess.run([sys.executable, str(validator)], capture_output=True, text=True)
    if proc.returncode != 0:
        fail(errors, f"emoji catalog validation failed: {proc.stdout}{proc.stderr}")


def check_required(errors: list[str]) -> None:
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            fail(errors, f"missing required file: {rel}")


def main() -> int:
    errors: list[str] = []
    check_required(errors)
    if not errors:
        check_frontmatter(errors)
        check_local_references(errors)
        check_tocs(errors)
        check_regressions(errors)
        check_python(errors)
        check_json(errors)
        check_fixtures(errors)
        check_emoji_catalog(errors)
    if errors:
        print("VALIDATION FAILED")
        for err in errors:
            print(f"- {err}")
        return 1
    print("VALIDATION OK")
    print("- required files present")
    print("- SKILL.md frontmatter portable")
    print("- local references resolved")
    print("- long references have TOCs")
    print("- regression guards passed")
    print("- Python syntax passed")
    print("- JSON fixtures parsed")
    print("- rich-message fixture semantics passed")
    print("- premium emoji registry passed dedupe and curated-set validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
