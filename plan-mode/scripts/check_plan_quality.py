#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import re
import sys


REQUIRED_SECTIONS = [
    "## 0. 预检清单",
    "## 1. 核心变更摘要",
    "## 2. 涉及文件清单",
    "## 3. 核心数据结构与接口",
    "## 4. 详细实施步骤",
    "## 5. 验证策略",
    "## 5. 风险评估与回滚",
]

BANNED_PHRASES = [
    "实现逻辑",
    "处理边界情况",
    "TBD",
    "TODO",
]

CMD_HINTS = re.compile(
    r"(npm|pnpm|yarn|go test|pytest|mvn|gradle|cargo|dotnet test)",
    re.IGNORECASE,
)


def _section_slice(text: str, heading: str) -> str:
    idx = text.find(heading)
    if idx == -1:
        return ""
    rest = text[idx:]
    next_idx = rest.find("\n## ", len(heading))
    if next_idx == -1:
        return rest
    return rest[:next_idx]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check plan file against quality gates.")
    parser.add_argument("plan_file", help="Path to plan file")
    args = parser.parse_args()

    try:
        with open(args.plan_file, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"FAIL: file not found: {args.plan_file}")
        return 1

    errors = []

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"Missing section: {section}")

    for phrase in BANNED_PHRASES:
        if phrase in text:
            errors.append(f"Contains banned phrase: {phrase}")

    impl = _section_slice(text, "## 4. 详细实施步骤")
    if "```" not in impl:
        errors.append("Implementation Details: no code block found")

    data_struct = _section_slice(text, "## 3. 核心数据结构与接口")
    if "```" not in data_struct:
        errors.append("Data Structures: no code block found")

    verify = _section_slice(text, "## 5. 验证策略")
    if ("`" not in verify) and (not CMD_HINTS.search(verify)):
        errors.append("验证策略: no executable command detected")

    risk = _section_slice(text, "## 5. 风险评估与回滚")
    if ("Rollback" not in risk) and ("回滚" not in risk):
        errors.append("风险评估与回滚: missing rollback hint")

    if errors:
        print("FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
