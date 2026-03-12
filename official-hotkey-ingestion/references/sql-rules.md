# SQL 约束与核对清单

## 通用规则
- 单事务：`BEGIN` / `COMMIT`
- 幂等优先：`INSERT ... ON CONFLICT`
- 批量映射优先用 CTE + `VALUES` 或 `jsonb_each` / `jsonb_each_text`
- 执行时 SQL 必须完整，不能因为消息太长省略任何条目

## 英文阶段建议覆盖
- `public.app`
- `public.app_category`
- `public.app_hotkey`
- `public.app_faq`

## 国际化阶段建议覆盖
- `public.app_i18n`
- `public.app_hotkey_i18n`
- `public.app_faq_i18n`

## 建议的语义 ID 约定
- `app.id`：`app_<slug>`
- `app_hotkey.id`：`<app-prefix>-<category-or-group>-<action-slug>`

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
  - `SELECT COUNT(*) FROM public.app_hotkey WHERE app_slug = '<slug>';`
  - `SELECT os, COUNT(*) FROM public.app_hotkey WHERE app_slug = '<slug>' GROUP BY os ORDER BY os;`
  - `SELECT COUNT(*) FROM public.app_faq WHERE app_id = 'app_<slug>';`
- 国际化阶段：
  - `SELECT locale FROM public.app_i18n WHERE app_id = 'app_<slug>' ORDER BY locale;`
  - `SELECT locale, COUNT(*) FROM public.app_hotkey_i18n WHERE hotkey_id IN (SELECT id FROM public.app_hotkey WHERE app_slug = '<slug>') GROUP BY locale ORDER BY locale;`
  - `SELECT locale, COUNT(*) FROM public.app_faq_i18n WHERE faq_id IN (SELECT id FROM public.app_faq WHERE app_id = 'app_<slug>') GROUP BY locale ORDER BY locale;`

## 执行前最后确认
- 是否所有快捷键都能追溯到官方页面
- 是否所有 FAQ 都来自官方说明，而不是主观补充
- 是否所有 locale 映射都完整
- 是否已在计划中明确哪些内容是保守假设
