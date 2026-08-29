#!/usr/bin/env python3
"""Build or verify the canonical sitemap from indexable repository HTML files."""

from __future__ import annotations

import argparse
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"
BASE_URL = "https://tabellenbuch.org"
EXCLUDED_FILES = {Path("404.html")}
EXCLUDED_DIRECTORIES = {"components"}


class CanonicalParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonicals: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        data = dict(attrs)
        rel = data.get("rel", "").lower().split()
        if tag == "link" and "canonical" in rel and data.get("href"):
            self.canonicals.append(data["href"])


def points_to_different_canonical(path: Path) -> bool:
    parser = CanonicalParser()
    parser.feed((ROOT / path).read_text(encoding="utf-8"))
    if not parser.canonicals:
        return False
    page_url = f"{BASE_URL}{route_for(path)}"
    targets = {urljoin(page_url, canonical) for canonical in parser.canonicals}
    return targets != {page_url}


def content_pages() -> list[Path]:
    pages = []
    for path in ROOT.rglob("*.html"):
        relative = path.relative_to(ROOT)
        if relative in EXCLUDED_FILES or relative.parts[0] in EXCLUDED_DIRECTORIES:
            continue
        if points_to_different_canonical(relative):
            continue
        pages.append(relative)
    return sorted(pages, key=route_for)


def route_for(path: Path) -> str:
    route = "/" + path.as_posix()
    if path.name == "index.html":
        route = route.removesuffix("index.html")
    return route


def last_modified(path: Path) -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", path.as_posix()],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() or date.today().isoformat()


def render() -> str:
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    urlset = ET.Element("{http://www.sitemaps.org/schemas/sitemap/0.9}urlset")
    routes: set[str] = set()
    for page in content_pages():
        route = route_for(page)
        if route in routes:
            raise ValueError(f"duplicate canonical route: {route}")
        routes.add(route)
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = f"{BASE_URL}{route}"
        ET.SubElement(url, "lastmod").text = last_modified(page)
    ET.indent(urlset, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
        urlset, encoding="unicode", short_empty_elements=False
    ) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="fail if sitemap.xml is not up to date"
    )
    args = parser.parse_args()
    generated = render()
    if args.check:
        current = SITEMAP.read_text(encoding="utf-8")
        if current != generated:
            print("sitemap.xml is stale; run: python scripts/build_sitemap.py")
            return 1
        print(f"Sitemap check passed for {len(content_pages())} content routes.")
        return 0
    SITEMAP.write_text(generated, encoding="utf-8")
    print(f"Wrote {len(content_pages())} content routes to sitemap.xml.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
