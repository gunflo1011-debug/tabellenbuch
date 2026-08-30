#!/usr/bin/env python3
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CORE_PAGES = [
    Path("index.html"),
    Path("pages/mathematik/mathematik.html"),
    Path("pages/mathematik/algebra/algebra.html"),
    Path("pages/mathematik/algebra/gleichungen/index.html"),
    Path("pages/mathematik/algebra/gleichungen/grundlagen.html"),
    Path("pages/mathematik/algebra/gleichungen/lineare-gleichungen.html"),
    Path("pages/mathematik/algebra/gleichungen/quadratische-gleichungen.html"),
    Path("pages/mathematik/algebra/gleichungssysteme/gleichungssysteme.html"),
    Path("pages/mathematik/algebra/gleichungssysteme/lineare-systeme.html"),
    Path("pages/mathematik/funktionen/funktionen.html"),
    Path("pages/mathematik/funktionen/typen.html"),
    Path("pages/mathematik/funktionen/transformationen.html"),
    Path("pages/mathematik/funktionen/umkehr-komposition.html"),
    Path("pages/mathematik/funktionen/extrema-uebersicht.html"),
    Path("pages/mathematik/analysis-reell/analysis-reell.html"),
    Path("pages/mathematik/analysis-reell/grenzwerte-stetigkeit.html"),
    Path("pages/mathematik/analysis-reell/differential.html"),
    Path("pages/mathematik/analysis-reell/integral.html"),
    Path("pages/mathematik/analysis-reell/folgen-reihen.html"),
    Path("pages/mathematik/analysis-reell/mehrdim.html"),
    Path("pages/mathematik/analysis-reell/vektorsatz.html"),
    Path("pages/mathematik/dgl/dgl.html"),
    Path("pages/mathematik/dgl/ode.html"),
    Path("pages/mathematik/dgl/ode-systeme.html"),
    Path("pages/mathematik/lineare-algebra/lineare-algebra.html"),
]

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.head_count = 0
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.has_title = False
        self.has_description = False
        self.has_canonical = False
        self.has_viewport = False
        self.html_lang = None

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "html":
            self.html_lang = data.get("lang")
        elif tag == "head":
            self.head_count += 1
        elif tag == "title":
            self.has_title = True
        elif tag == "meta":
            name = data.get("name", "").lower()
            if name == "description" and data.get("content", "").strip():
                self.has_description = True
            if name == "viewport":
                self.has_viewport = True
        elif tag == "link" and data.get("rel", "").lower() == "canonical":
            self.has_canonical = bool(data.get("href"))
        if "id" in data:
            self.ids.append(data["id"])
        if tag == "a" and data.get("href"):
            self.hrefs.append(data["href"])


def local_target(page: Path, href: str) -> Path | None:
    if href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc:
        return None
    raw = parsed.path
    if not raw:
        return None
    if raw.startswith("/"):
        target = ROOT / raw.lstrip("/")
    else:
        target = ROOT / page.parent / raw
    if target.is_dir():
        target = target / "index.html"
    return target.resolve()


def changed_html(base_ref: str) -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD", "--", "*.html"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [Path(line) for line in result.stdout.splitlines() if line.strip()]


def validate(page: Path) -> list[str]:
    errors: list[str] = []
    full = ROOT / page
    if not full.exists():
        return [f"{page}: missing"]
    text = full.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(text)
    if parser.head_count != 1:
        errors.append(f"{page}: expected exactly one <head>, found {parser.head_count}")
    if not parser.has_title:
        errors.append(f"{page}: missing <title>")
    if not parser.has_description:
        errors.append(f"{page}: missing meta description")
    if not parser.has_canonical:
        errors.append(f"{page}: missing canonical link")
    if not parser.has_viewport:
        errors.append(f"{page}: missing viewport meta")
    if parser.html_lang != "en":
        errors.append(f"{page}: html lang must be 'en', found {parser.html_lang!r}")
    duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
    if duplicates:
        errors.append(f"{page}: duplicate ids: {', '.join(duplicates)}")
    for href in parser.hrefs:
        target = local_target(page, href)
        if target is not None and not target.exists():
            errors.append(f"{page}: broken local link {href}")
    placeholders = [
        r"formeln\s*&(?:amp;)?\s*inhalte\s+folgen",
        r"content\s+coming\s+soon",
        r"todo\b",
        r"placeholder\b",
    ]
    lower = text.lower()
    for pattern in placeholders:
        if re.search(pattern, lower):
            errors.append(f"{page}: placeholder content matched {pattern!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref", default="")
    args = parser.parse_args()
    pages = list(CORE_PAGES)
    changed: list[Path] = []
    if args.base_ref:
        changed = changed_html(args.base_ref)
        pages.extend(changed)
    seen: set[Path] = set()
    ordered = []
    for page in pages:
        if page not in seen:
            seen.add(page)
            ordered.append(page)
    errors = []
    for page in ordered:
        errors.extend(validate(page))
    if errors:
        print("Core page quality checks failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"HTML page quality checks passed for {len(ordered)} pages ({len(CORE_PAGES)} core, {len(changed)} changed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
