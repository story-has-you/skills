#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser


class _DDGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._in_link = False
        self._link_href = ""
        self._link_text = []
        self.results = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attr_map = dict(attrs)
        css = attr_map.get("class", "")
        if "result__a" in css:
            self._in_link = True
            self._link_href = attr_map.get("href", "")
            self._link_text = []

    def handle_data(self, data):
        if self._in_link:
            self._link_text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._in_link:
            title = "".join(self._link_text).strip()
            href = self._link_href.strip()
            if title and href:
                self.results.append({"title": title, "url": href})
            self._in_link = False
            self._link_href = ""
            self._link_text = []


def _fetch_ddg(query: str, timeout: int) -> str:
    encoded = urllib.parse.urlencode({"q": query})
    url = f"https://duckduckgo.com/html/?{encoded}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (plan-mode web_search.py)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _filter_domains(results, domains):
    if not domains:
        return results
    filtered = []
    for item in results:
        try:
            netloc = urllib.parse.urlparse(item["url"]).netloc.lower()
        except Exception:
            continue
        if any(netloc == d or netloc.endswith("." + d) for d in domains):
            filtered.append(item)
    return filtered


def main() -> int:
    parser = argparse.ArgumentParser(description="Web search helper (DuckDuckGo HTML).")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--num", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument(
        "--domain",
        action="append",
        default=[],
        help="Restrict to domain (repeatable), e.g. --domain openai.com",
    )
    parser.add_argument("--timeout", type=int, default=10, help="HTTP timeout seconds")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    try:
        html = _fetch_ddg(args.query, args.timeout)
    except Exception as exc:
        print(f"FAIL: fetch error: {exc}")
        return 1

    parser_ = _DDGParser()
    parser_.feed(html)
    results = _filter_domains(parser_.results, [d.lower() for d in args.domain])
    results = results[: max(args.num, 0)]

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    if not results:
        print("NO_RESULTS")
        return 0

    for idx, item in enumerate(results, 1):
        print(f"{idx}. {item['title']}\n   {item['url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
