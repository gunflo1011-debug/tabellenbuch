#!/usr/bin/env python3
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CORE_PAGES = [
    Path("pages/mathematik/algebra/algebra.html"),
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


def check(page: Path) -> list[str]:
    full = ROOT / page
    errors: list[str] = []
    if not full.exists():
        return [f"missing core page: {page}"]
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
        errors.append(f"{page}: html lang should be 'en', found {parser.html_lang!r}")
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


def main() -> int:
    errors = [error for page in CORE_PAGES for error in check(page)]
    if errors:
        print("Core page quality checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Core page quality checks passed for {len(CORE_PAGES)} pages.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
