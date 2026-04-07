# 接入 `npx skills update` 指南

本文目标：实现“主仓库 `master` 分支更新后，本地执行 `npx skills update` 即可同步技能目录”。

## 1. 功能说明

本仓库新增了 `skills` CLI：

- 命令：`npx skills update`
- 默认同步目标目录：`$CODEX_HOME/skills`（未设置时为 `~/.codex/skills`）
- 默认分支：`master`
- 默认仓库地址：读取 `SKILLS_REPO`，未设置时使用 CLI 内置默认值

## 2. 首次使用

```bash
SKILLS_REPO=<你的技能仓库地址> npx skills update
```

行为：

1. 若本地不存在 `~/.codex/skills`，执行浅克隆（`--depth 1`）
2. 若已存在并且是 git 仓库，执行：`fetch -> checkout master -> pull --ff-only`

## 3. 日常更新

当远端 `master` 有新提交后，本地执行：

```bash
npx skills update --repo <你的技能仓库地址>
```

或提前配置环境变量：

```bash
export SKILLS_REPO=<你的技能仓库地址>
npx skills update
```

## 4. 建议发布方式

如果你希望直接通过 `npx skills update`（不带包名作用域）调用：

1. npm 包名需要是 `skills`（且可用）
2. 发布后，用户即可通过 `npx skills update` 获取最新 CLI
3. CLI 再从你指定的 Git 仓库同步 `master` 内容到本地技能目录

> 如果 npm 名称不可用，可改为 `npx @your-scope/skills update`。
