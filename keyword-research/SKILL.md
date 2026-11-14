---
name: keyword-research
source: gefei-seo-distiller
dimensions: [D2, D7]
unit_count: 79
kinds: [decision_rule, procedure, principle, case]
author: 哥飞
sample_units:
  - a_0bf4ab2bd9e0df#K001
  - a_0bf4ab2bd9e0df#K002
  - a_0bf4ab2bd9e0df#K003
  - a_efddc06e0fee3a#K006
  - a_06bebe1a6b1cb0#K002
  - a_06bebe1a6b1cb0#K003
  - a_e77d90575335c9#K001
  - a_e77d90575335c9#K011
  - a_57f8f63f1f6bb0#K003
  - a_57f8f63f1f6bb0#K004
trigger_keywords:
  - 关键词研究
  - 月入万刀
  - 蓝海词
  - KGR
  - 新词判断
  - 趋势词
  - 找词
  - KD 难度
  - 搜索量
description: Use when 给一个方向/产品/竞品做关键词扩展研究（找母词 → 扩长尾 → 分意图 → 排优先级）。输出关键词表 + 落地策略。基于哥飞公众号 92 个 D1/D2/D7 knowledge_units 蒸馏。
---

# keyword-research

按"词能不能赚到钱"做完整关键词研究：先算**月收入目标 ↔ 搜索量**，再判断**竞争度 + 趋势 + 形态**，输出可执行的关键词清单。

## 何时触发

- 用户问"这个词每月能赚多少 / 需多少点击"；
- 用户问"什么是蓝海词 / 怎么找"；
- 用户问"KGR 怎么用"；
- 用户问"怎么判断新词"；
- 任何 D2（关键词 / SERP）+ D7（变现）相关问题。

## 输入 / 输出

**输入**：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `seed_keywords` | list[string] | 是 | 种子词 ≥ 1 |
| `target_monthly_usd` | int | 是 | 月收入目标（USD） |
| `business_model` | enum | 是 | "ads" \| "affiliate" \| "saas" \| "ecommerce" |
| `avg_order_value_usd` | float \| null | 否 | SaaS / 电商必填 |
| `epc_or_rpm_estimate` | float \| "unknown" | 否 | ads 模式 RPM；affiliate EPC；未知时填 "unknown" |

**输出**：

```yaml
target_metrics:
  required_monthly_clicks: int
  required_monthly_search_volume: int
  cpc_threshold_for_paid: float | "unknown"
keyword_cards:
  - keyword: "..."
    trend_shape: "spike" | "flat" | "growth" | "decline"
    intent: "informational" | "transactional" | "navigational" | "commercial"
    competition_proxy: "kgr" | "intitle_count" | "kd"
    is_blue_ocean: true | false | "unknown"
    fits_target: true | false | "needs_verification"
    cite: "article_id#unit_id"
next_actions:
  - "..."
unknowns: ["..."]
```

## 步骤

### Step 1：算"赚到 X 美元需要多少搜索量"
- 公式（a_0bf4ab2bd9e0df#K001）：
  - 目标 330 USD/天 → 17 单/天（客单价 20 USD）；
  - 千分之五付费转化 → 3400 点击/天；
  - 拿到 1/3 点击 → 需 1 万搜索/天 = 月均搜索量 **30 万**；
  - 这是分母，分子的转化率 / 客单价一变，所需搜索量也会变。
- 必须同时校验：ads 模式用 RPM，affiliate 用 EPC，SaaS 用 AOV × 转化率。

### Step 2：判断是不是"蓝海词"
- 哥飞定义：搜索量在增长 + intitle 页面数不多（a_efddc06e0fee3a#K006）；
- 不必是新词；ai image editor 是老词但符合蓝海条件。
- KGR 量化：intitle:`<keyword>` + Allintitle:`<keyword> inurl:` 域名 数 < 30 → 低竞争（a_06bebe1a6b1cb0#K003）。

### Step 3：判断"新词" vs "老词"
- 趋势形状分新旧：陡升尖峰 = 新词；长期水平线 = 老词（a_e77d90575335c9#K001）。
- 竞争判断 ≠ 新旧判断：新词可能已有竞争；老词可能仍蓝海。

### Step 4：趋势对比定方向
- 主词升、竞品词降 → 替代需求；
- 两者一起升 → 赛道扩张（a_e77d90575335c9#K011）。

### Step 5：分类搜索意图
- 工具类：commercial / transactional；
- 信息类：informational → 变现弱；
- 品牌类：navigational → 通常是新词站打不动。

### Step 6：标"需验证"
- 拿不到搜索量时，必须标 "unknown" 而不是编造；
- 哥飞明确写：Ahrefs 等 SEO 平台新词还没收录时查不到 KD，要用 KGR 量化（a_efddc06e0fee3a#K004）。

## missing_data_branch

- **`epc_or_rpm_estimate = unknown`** → 不假设数字；列出 3 种可信来源（Adsense 后台 / 联盟平台平均 EPC / SimilarWeb 单页估算）；
- **没有 Google Trends** → 用百度指数（仅限中文）+ 看谷歌下拉框（a_d51632d976a6e8#K003）；
- **新词无 KD** → KGR 替代；
- **客单价未知** → 列 3 个常见段位（10 / 50 / 200 USD），让用户选。

## 成功条件 / 反例 / 校验

**成功条件**：
- `target_metrics.required_monthly_search_volume` 必须有显式数字（哪怕估算过程附"unknown"标记）；
- 每个 `keyword_card` 至少含 `trend_shape` + `competition_proxy` + `cite`；
- `unknowns` 至少 1 条（除非所有数据齐全）。

**反例**：
- 把月入万刀直接套所有词（哥飞公式依赖客单价、转化率、RPM）（a_0bf4ab2bd9e0df#K001）；
- 找不到词就放弃（哥飞说"限制太多"是常见错误，初学者可多限制练手，但不要永远自我设限）（a_0bf4ab2bd9e0df#K002）；
- 站做错就重做同样方向（哥飞说"带着记忆重生"，经验/外链/落地页/转化路径都要迭代）（a_0bf4ab2bd9e0df#K003）。

**校验**：
- 把 `keyword_cards` 喂给 `new-site-opportunity-review` 看是否决策一致；
- 用 `rule_preservation` eval 题集验证"先算量再判断"路径。

## 引用映射

| 步骤 | 文章证据 |
|---|---|
| 月入万刀公式 | a_0bf4ab2bd9e0df#K001 |
| 别自我设限 | a_0bf4ab2bd9e0df#K002 |
| 带着记忆重生 | a_0bf4ab2bd9e0df#K003 |
| 蓝海词定义 | a_efddc06e0fee3a#K006 |
| 新词≠蓝海 | a_efddc06e0fee3a#K004 |
| KGR 量化 | a_06bebe1a6b1cb0#K003 |
| 趋势形状分新旧 | a_e77d90575335c9#K001 |
| 主词升 vs 竞品词 | a_e77d90575335c9#K011 |
| AI 时代新词机会 | a_57f8f63f1f6bb0#K003, K004 |

## 已知边界

- 不覆盖**长尾关键词自动挖掘**流程；
- 不覆盖**多语种关键词**本地化细节；
- 哥飞原文无"SERP intent 自动分类"具体方法，需接外部 NLP。
