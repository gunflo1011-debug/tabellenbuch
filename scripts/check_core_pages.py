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
    Path("pages/mathematik/algebra/algebra.html"),
    Path("pages/mathematik/algebra/gleichungen/index.html"),
    Path("pages/mathematik/algebra/gleichungen/grundlagen.html"),
    Path("pages/mathematik/algebra/gleichungen/lineare-gleichungen.html"),
    Path("pages/mathematik/algebra/gleichungen/quadratische-gleichungen.html"),
    Path("pages/mathematik/algebra/gleichungssysteme/gleichungssysteme.html"),
    Path("pages/mathematik/algebra/gleichungssysteme/lineare-systeme.html"),
    Path("pages/mathematik/algebra/gleichungssysteme/nichtlineare-systeme.html"),
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
        target = (ROOT / page.parent / raw).resolve()
    if str(target).endswith("/"):
        target = target / "index.html"
    return target


def check(page: Path, *, require_english: bool) -> list[str]:
    full = ROOT / page
    errors: list[str] = []
    if not full.exists():
        return [f"missing page: {page}"]
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
    if require_english and parser.html_lang != "en":
        errors.append(f"{page}: html lang should be 'en', found {parser.html_lang!r}")
    elif not require_english and not re.fullmatch(
        r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*", parser.html_lang or ""
    ):
        errors.append(f"{page}: missing or invalid html lang: {parser.html_lang!r}")
    duplicates = sorted({x for x in parser.ids if parser.ids.count(x) > 1})
    if duplicates:
        errors.append(f"{page}: duplicate ids: {', '.join(duplicates)}")
    for href in parser.hrefs:
        target = local_target(page, href)
        if target is not None and not target.exists():
            try:
                shown = target.relative_to(ROOT)
            except ValueError:
                shown = target
            errors.append(f"{page}: broken local link {href!r} -> {shown}")
    for placeholder in ("Formeln & Inhalte folgen", "Content follows", "TODO"):
        if placeholder in text:
            errors.append(f"{page}: placeholder text remains: {placeholder!r}")
    return errors


def changed_html_pages(base: str) -> set[Path]:
    if not base or set(base) == {"0"}:
        base = "HEAD^"
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
            f"{base}...HEAD",
            "--",
            "*.html",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {
        Path(name)
        for name in result.stdout.splitlines()
        if name and Path(name).parts[0] != "components" and (ROOT / name).is_file()
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--changed-since",
        help="also validate every HTML document changed since this Git commit",
    )
    args = parser.parse_args()
    core_pages = set(CORE_PAGES)
    changed_pages = changed_html_pages(args.changed_since) if args.changed_since else set()
    pages = sorted(core_pages | changed_pages)
    errors = [
        error
        for page in pages
        for error in check(page, require_english=page in core_pages)
    ]
    if errors:
        print("HTML page quality checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"HTML page quality checks passed for {len(pages)} pages "
        f"({len(core_pages)} core, {len(changed_pages)} changed)."
    )
    return 0

if __name__ == "__main__":
    sys.exit(main())
