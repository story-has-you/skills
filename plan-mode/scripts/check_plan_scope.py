#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import re


def _extract_scope_section(text: str) -> str:
    start = text.find("## 2. 涉及文件清单")
    if start == -1:
        return ""
    rest = text[start:]
    end = rest.find("\n## ", len("## 2. 涉及文件清单"))
    if end == -1:
        return rest
    return rest[:end]


def _iter_rows(section: str):
    for line in section.splitlines():
        if "|" not in line:
            continue
        if ":---" in line:
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 2:
            continue
        yield parts[0], parts[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check plan scope file paths exist.")
    parser.add_argument("plan_file", help="Path to plan file")
    args = parser.parse_args()

    try:
        with open(args.plan_file, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"FAIL: file not found: {args.plan_file}")
        return 1

    scope = _extract_scope_section(text)
    if not scope:
        print("FAIL: scope section not found")
        return 1

    missing = []
    for op, path_cell in _iter_rows(scope):
        match = re.search(r"`([^`]+)`", path_cell)
        if not match:
            continue
        path = match.group(1).strip()
        if not path or path.startswith("<") or path.startswith("["):
            continue
        exists = os.path.exists(path)
        op_lower = op.lower()
        if "create" in op_lower:
            continue
        if not exists:
            missing.append(f"{path} (op: {op})")

    if missing:
        print("FAIL")
        for item in missing:
            print(f"- missing: {item}")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
