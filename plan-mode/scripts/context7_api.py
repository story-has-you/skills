#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError


DEFAULT_BASE_URL = "https://context7.com/api/v2"


def _get_api_key(env_name: str) -> str:
    key = os.environ.get(env_name, "").strip()
    if not key:
        raise SystemExit(f"Missing API key in env: {env_name}")
    return key


def _build_url(base_url: str, path: str, params: dict) -> str:
    base = base_url.rstrip("/")
    query = urllib.parse.urlencode(params)
    return f"{base}{path}?{query}"


def _request(url: str, api_key: str, timeout: int) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "plan-mode context7_api.py",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _run_search(args) -> int:
    url = _build_url(
        args.base_url,
        "/libs/search",
        {"libraryName": args.library_name, "query": args.query},
    )
    api_key = _get_api_key(args.api_key_env)
    print(_request(url, api_key, args.timeout))
    return 0


def _run_context(args) -> int:
    url = _build_url(
        args.base_url,
        "/context",
        {"libraryId": args.library_id, "query": args.query, "type": args.type},
    )
    api_key = _get_api_key(args.api_key_env)
    print(_request(url, api_key, args.timeout))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Context7 API helper (reads API key from env only)."
    )
    parser.add_argument(
        "--api-key-env",
        default="CONTEXT7_API_KEY",
        help="Env var name for API key (default: CONTEXT7_API_KEY)",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base API URL (default: https://context7.com/api/v2)",
    )
    parser.add_argument("--timeout", type=int, default=10, help="HTTP timeout seconds")

    sub = parser.add_subparsers(dest="cmd", required=True)
    search = sub.add_parser("search", help="Search libraries")
    search.add_argument("--library-name", required=True, help="Library name")
    search.add_argument("--query", required=True, help="Search query")
    search.set_defaults(func=_run_search)

    ctx = sub.add_parser("context", help="Fetch context")
    ctx.add_argument("--library-id", required=True, help="Library ID, e.g. /vercel/next.js")
    ctx.add_argument("--query", required=True, help="Context query")
    ctx.add_argument("--type", default="txt", help="Context type (default: txt)")
    ctx.set_defaults(func=_run_context)

    args = parser.parse_args()

    try:
        return args.func(args)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}: {body}")
        return 1
    except URLError as exc:
        print(f"FAIL: network error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
