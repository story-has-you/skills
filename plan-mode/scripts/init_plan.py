#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import datetime as _dt
import os
import re
import sys

TEMPLATE = """# [{date}] {title} 深度实施方案

## 0. 预检清单 (Pre-Flight Checklist)
- [ ] 当前环境是否可通过构建？(Build Status)
- [ ] 关键依赖是否存在？
- [ ] 是否已读取并理解项目的 CONTRIBUTING.md 或代码规范？

## 1. 核心变更摘要
- **目标**: 一句话描述要做什么。
- **待确认项**: (如果在规划中通过对话已解决，请记录在此，例如：*已确认使用 JWT 方案*)

## 2. 涉及文件清单 (Scope)
| 操作 | 文件路径 | 关键改动点 |
| :--- | :--- | :--- |
| Create | `src/services/auth.ts` | 新增 JWT 验证逻辑 |

## 3. 核心数据结构与接口 (Data Structures & Interfaces)
**所有新定义的 Type/Interface 必须在此列出。这是代码实现的基石。**

```typescript
// src/types/user.ts
export interface UserProfile {{
  id: string;
  role: 'admin' | 'user'; // Explicit union types, not just "string"
  preferences: UserPreferences; // Reference other interfaces
}}
```

## 4. 详细实施步骤 (Implementation Details)
**注意：本部分必须包含可直接使用的代码骨架。禁止使用伪代码。**

### 步骤 1: [具体动作]
- **文件**: `src/types/user.d.ts`
- **依赖**: (列出需要 import 的模块)
- **代码骨架**:
```typescript
// 必须包含完整的函数签名和核心逻辑流
export async function updateUserProfile(userId: string, data: Partial<UserProfile>): Promise<void> {{
    if (!userId) throw new Error("Invalid ID");
    // ... 具体调用 ...
}}
```

### 步骤 2: ...

## 5. 验证策略
- [ ] 单元测试...

## 5. 风险评估与回滚 (Risk & Rollback)
- **High Risk**: 修改了 `auth.ts` 核心逻辑，可能导致全站登录失效。
- **Mitigation**: 必须先编写针对 `auth.ts` 的回归测试。
- **Rollback**: `git checkout src/services/auth.ts`
"""


def _sanitize_slug(raw: str) -> str:
    slug = raw.strip().lower().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9._-]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "task"


def _parse_date(value: str | None) -> str:
    if not value:
        return _dt.date.today().strftime("%Y%m%d")
    try:
        return _dt.datetime.strptime(value, "%Y%m%d").strftime("%Y%m%d")
    except ValueError as exc:
        raise SystemExit(f"Invalid --date {value}. Use YYYYMMDD.") from exc


def _ensure_under_dir(target: str, base_dir: str) -> None:
    base = os.path.abspath(base_dir)
    tgt = os.path.abspath(target)
    if os.path.commonpath([base, tgt]) != base:
        raise SystemExit(f"Refusing to write outside {base_dir}: {target}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a plan file with the standard template.")
    parser.add_argument("slug", help="Short task slug (english or pinyin).")
    parser.add_argument("--date", help="YYYYMMDD, default today.")
    parser.add_argument("--dir", default="plans", help="Plan directory (default: plans).")
    parser.add_argument("--force", action="store_true", help="Overwrite if file exists.")
    parser.add_argument("--dry-run", action="store_true", help="Print path only.")
    parser.add_argument("--allow-outside", action="store_true", help="Allow writing outside --dir.")
    args = parser.parse_args()

    date = _parse_date(args.date)
    slug = _sanitize_slug(args.slug)
    filename = f"{date}-{slug}.md"
    target_dir = args.dir
    target_path = os.path.join(target_dir, filename)

    if not args.allow_outside:
        _ensure_under_dir(target_path, target_dir)

    if args.dry_run:
        print(target_path)
        return 0

    os.makedirs(target_dir, exist_ok=True)
    if os.path.exists(target_path) and not args.force:
        raise SystemExit(f"File exists: {target_path} (use --force to overwrite)")

    content = TEMPLATE.format(date=date, title=slug)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(target_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
