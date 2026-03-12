# SQL 约束与核对清单

## 通用规则
- 单事务：`BEGIN` / `COMMIT`
- 幂等优先：`INSERT ... ON CONFLICT`
- 批量映射优先用 CTE + `VALUES` 或 `jsonb_each` / `jsonb_each_text`
- `public.app_hotkey.hotkey` 按按键 token 数组写入，不把 `⌘ K`、`Ctrl Shift P` 这类组合键拼成一个字符串
- 执行时 SQL 必须完整，不能因为消息太长省略任何条目
- 所有主键与外键一律使用 UUID，关联必须通过 UUID 字段完成，不使用 `slug` 或语义字符串充当关联键
- 上游记录写入后，必须通过 `RETURNING` 或唯一键回查拿到 UUID，再继续写下游关联表

## `app_hotkey.hotkey` 代表性写法

```sql
WITH target_app AS (
    SELECT id
    FROM public.app
    WHERE slug = 'claude-code'
),
hotkey_rows(os, category, action, hotkey_tokens) AS (
    VALUES
        ('macos', 'General', 'Open Command Palette', ARRAY['⌘', 'K']::text[]),
        ('windows', 'General', 'Open Command Palette', ARRAY['Ctrl', 'K']::text[]),
        ('windows', 'General', 'Open Command Palette', ARRAY['Ctrl', 'Shift', 'P']::text[])
)
INSERT INTO public.app_hotkey (
    id,
    app_id,
    os,
    category,
    action,
    hotkey
)
SELECT
    gen_random_uuid(),
    target_app.id,
    hotkey_rows.os,
    hotkey_rows.category,
    hotkey_rows.action,
    hotkey_rows.hotkey_tokens
FROM target_app
CROSS JOIN hotkey_rows;
```

- 上面示例只展示 `hotkey` 字段形态与 UUID 关联链路。
- 真正执行时，仍需按目标库的真实唯一约束补齐幂等 `ON CONFLICT` 或存在性判断。
- macOS 绑定优先用标准符号 token，如 `⌘`、`⌥`、`⌃`、`⇧`。

## 英文阶段建议覆盖
- `public.app`
- `public.app_category`
- `public.app_hotkey`
- `public.app_faq`

## 国际化阶段建议覆盖
- `public.app_i18n`
- `public.app_hotkey_i18n`
- `public.app_faq_i18n`

## UUID 与关联规则
- `public.app.id`、`public.app_hotkey.id`、`public.app_faq.id` 以及各国际化表、绑定表中的 `*_id` 字段都应为 UUID
- `slug` 仅作为业务唯一键、查询条件或幂等 upsert 的冲突键，不参与表间关联
- 若需要新建记录，可使用数据库现有 UUID 生成函数；若命中已有记录，必须复用已有 UUID，不得重新派生语义 ID

## 国际化默认语言
- `zh`
- `ja`
- `ru`
- `ar`
- `de`
- `fr`
- `pt`
- `in`

## 国际化默认策略
- `app_i18n.name = NULL`
- `description`、`category`、`action`、`FAQ question/answer` 全量补齐
- 说明性文案优先自然、克制、可直接展示

## 手动验收最小清单
- 英文阶段：
  - `SELECT id, name, slug FROM public.app WHERE slug = '<slug>';`
  - `WITH target_app AS (SELECT id FROM public.app WHERE slug = '<slug>') SELECT COUNT(*) FROM public.app_hotkey WHERE app_id = (SELECT id FROM target_app);`
  - `WITH target_app AS (SELECT id FROM public.app WHERE slug = '<slug>') SELECT os, COUNT(*) FROM public.app_hotkey WHERE app_id = (SELECT id FROM target_app) GROUP BY os ORDER BY os;`
  - `WITH target_app AS (SELECT id FROM public.app WHERE slug = '<slug>') SELECT COUNT(*) FROM public.app_faq WHERE app_id = (SELECT id FROM target_app);`
- 国际化阶段：
  - `WITH target_app AS (SELECT id FROM public.app WHERE slug = '<slug>') SELECT locale FROM public.app_i18n WHERE app_id = (SELECT id FROM target_app) ORDER BY locale;`
  - `WITH target_app AS (SELECT id FROM public.app WHERE slug = '<slug>') SELECT locale, COUNT(*) FROM public.app_hotkey_i18n WHERE hotkey_id IN (SELECT id FROM public.app_hotkey WHERE app_id = (SELECT id FROM target_app)) GROUP BY locale ORDER BY locale;`
  - `WITH target_app AS (SELECT id FROM public.app WHERE slug = '<slug>') SELECT locale, COUNT(*) FROM public.app_faq_i18n WHERE faq_id IN (SELECT id FROM public.app_faq WHERE app_id = (SELECT id FROM target_app)) GROUP BY locale ORDER BY locale;`

## 执行前最后确认
- 是否所有快捷键都能追溯到官方页面
- 是否所有 FAQ 都来自官方说明，而不是主观补充
- 是否所有 locale 映射都完整
- 是否已在计划中明确哪些内容是保守假设
