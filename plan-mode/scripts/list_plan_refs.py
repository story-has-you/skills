#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys


def main() -> int:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ref_dir = os.path.join(base_dir, "references")
    index_path = os.path.join(ref_dir, "api_reference.md")

    if not os.path.exists(index_path):
        print(f"FAIL: not found: {index_path}")
        return 1

    with open(index_path, "r", encoding="utf-8") as f:
        text = f.read()

    files = re.findall(r"`([^`]+)`", text)
    if not files:
        print("FAIL: no references found in api_reference.md")
        return 1

    missing = []
    for name in files:
        target = os.path.join(ref_dir, name)
        if not os.path.exists(target):
            missing.append(name)

    if missing:
        print("MISSING")
        for name in missing:
            print(f"- {name}")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
