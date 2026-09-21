#!/usr/bin/env python3
"""Convert Telegram rich HTML into a conservative plain-text fallback."""
from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
from pathlib import Path

BLOCK_START = {
    "p", "div", "section", "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "aside", "details", "summary", "table", "tr", "ul", "ol",
    "li", "tg-button-row", "tg-collage", "tg-slideshow", "figcaption",
}
CELL = {"th", "td"}
MEDIA_LABELS = {
    "img": "[image]",
    "video": "[video]",
    "audio": "[audio]",
    "tg-document": "[document]",
    "tg-map": "[map]",
}


class Renderer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._last_cell = False

    def _newline(self) -> None:
        if self.parts and not self.parts[-1].endswith("\n"):
            self.parts.append("\n")

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag == "br":
            self._newline()
        elif tag in BLOCK_START:
            self._newline()
        elif tag in CELL:
            if self._last_cell:
                self.parts.append(" | ")
            self._last_cell = True
        elif tag in MEDIA_LABELS:
            self.parts.append(MEDIA_LABELS[tag])
        elif tag == "tg-button":
            self.parts.append("[")

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "tg-button":
            self.parts.append("]")
        if tag == "tr":
            self._last_cell = False
            self._newline()
        elif tag in BLOCK_START:
            self._newline()

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        raw = html.unescape("".join(self.parts))
        lines = [" ".join(line.split()) for line in raw.splitlines()]
        out: list[str] = []
        for line in lines:
            if line:
                out.append(line)
            elif out and out[-1] != "":
                out.append("")
        return "\n".join(out).strip()


def render(source: str) -> str:
    parser = Renderer()
    parser.feed(source)
    parser.close()
    return parser.text()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", type=Path)
    args = ap.parse_args()
    print(render(args.file.read_text(encoding="utf-8")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
