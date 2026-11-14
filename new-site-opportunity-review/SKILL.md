---
name: new-site-opportunity-review
source: gefei-seo-distiller
dimensions: [D1, D2]
unit_count: 84
kinds: [decision_rule, principle, procedure]
author: 哥飞
sample_units:
  - a_06bebe1a6b1cb0#K002
  - a_06bebe1a6b1cb0#K003
  - a_37d7fc779db178#K001
  - a_617c9a227322c0#K002
  - a_57f8f63f1f6bb0#K004
  - a_2cdfa864b2d091#K004
  - a_efddc06e0fee3a#K004
  - a_efddc06e0fee3a#K006
  - a_e37860903b7c01#K008
  - a_e77d90575335c9#K001
time_scope_mix: {time_sensitive: 0.6, evergreen: 0.4}
trigger_keywords:
  - 新站机会
  - 关键词机会
  - 新词
  - 蓝海词
  - 低竞争词
  - KGR
  - 月入万刀
  - 选词
  - 找词
  - 创业方向
description: Use when 评估一个新词/旧词是否值得开新站接 SEO 流量。判断上站/不上站/待验证三档，附竞争度+趋势+变现三段分析。基于哥飞公众号 84 个 D1/D2 knowledge_units 蒸馏。
---

# new-site-opportunity-review

评估**一个新词/旧词**是否值得开新站接 SEO 流量；输出"上站 / 不上站 / 待验证"三档结论，并附竞争度、趋势、变现三段判断。

## 何时触发

- 用户给出一个**候选关键词**或一个**想法**问"值不值得做站"。
- 用户给出一个**已上线站**，问"要不要 / 还能不能换方向"。
- 用户给出一个**模板站名**，问"应该选哪个关键词做"。
- 任何**D1 维度**（机会/方向/关键词）相关的"该不该做"问题。

## 输入 / 输出

**输入**：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `keyword` | string | 是 | 待评估的关键词或中文/英文短语 |
| `country` | string | 否 | 默认 US；ISO 3166-1 alpha-2 |
| `language` | string | 否 | 默认按关键词语种推断 |
| `business_model` | string \| null | 否 | ads / affiliate / saas / ecommerce / leadgen |
| `known_trend` | "up" \| "down" \| "flat" \| "unknown" | 否 | 用户口述的趋势方向 |
| `known_volume` | int \| "unknown" | 否 | 月搜索量；未知时必须传 "unknown" |

**输出**：

```yaml
decision: "上站" | "不上站" | "待验证"
confidence: high | medium | low
reasons:
  - cite: "article_id#unit_id"
    note: "..."   # 一行总结
checks_due:
  - tool: "google_trends" | "gsc_inspect" | "keyword_planner" | "ahrefs_kd" | "kgr_check"
    why: "..."
evidence: [article_id#unit_id, ...]
counterexamples: ["..."]
```

## 步骤（按顺序，缺失数据时跳到 missing_data_branch）

1. **定性：是「新词」还是「老词」？**
   - 跑 `google_trends` 看 12 个月曲线：陡升尖峰 → 新词；长期水平线 → 老词。
   - 哥飞原文：尖峰形状 = 新词（a_e77d90575335c9#K001）；不陡升 = 老词。

2. **量化：竞争程度**
   - 看 SERP 首页 intitle:`<keyword>` 结果数；
   - 看 `ahrefs_kd`（KD 值）；
   - 看 KGR（intitle 含 Allintitle:anchor 域名 数 < 30 视为低竞争，引用 a_06bebe1a6b1cb0#K003）。
   - **新词也要查 KD**——新词 ≠ 蓝海，a_efddc06e0fee3a#K004。

3. **方向：趋势**
   - 候选词趋势下行 → 不要做（a_37d7fc779db178#K001 蓝色曲线案例）；
   - 趋势上行 → 继续；
   - 趋势未明 → 标"待验证"。

4. **变现阻力**
   - 候选词 SERP 是否有广告位 → 看顶部/底部 Sponsored 是否铺满；
   - 落地页是工具站 / 内容站 / 电商 / SaaS 哪种 → 评估落地承接难度。
   - 哥飞原文：阻力小者拿更多 SEO 流量；阻力大者 SEM 转化被强者吃掉（a_02bc6c6e55718a#K002）。

5. **新词玩法分级**（a_e37860903b7c01#K008）
   - L1 跟随：别人上什么你也上；
   - L2 预测：提前注册域名占坑；
   - L3 创造：自己造词，全部流量归你。

6. **出三档结论**
   - 上站：低竞争 + 趋势上/平 + 变现可承接；
   - 不上站：高竞争 + 趋势下 + 落地页烂/缺广告位；
   - 待验证：缺数据 → 列出要核实的子问题。

## missing_data_branch

- **没有 `known_volume`** → 写"搜索量未知"，不要编造数字；要求用户提供 Keyword Planner / GSC 历史 / 第三方工具数字。
- **没有 `google_trends` 凭据** → 改用 `keyword_planner`（需登录 + 已产生广告花费）或第三方 `similarweb_rank`。
- **KD 拿不到**（新词未收录）→ 走 KGR 流程（intitle: 页面数 + Allintitle: 域名 数）。
- **业务模式未知** → 列出四种模式的落地页要求，由用户选。

## 成功条件 / 反例 / 校验

**成功条件**：
- 决策 ∈ {上站, 不上站, 待验证}，且至少引用 1 条 `article_id#unit_id`；
- 高 confidence 时至少引用 3 条证据；
- 列出的 `checks_due` 与实际缺失的工具对应。

**反例**（来自哥飞原文）：
- 看到有广告就立刻做同款（a_b18612963a8f01#K004）；
- 词不新就放弃（a_37d7fc779db178#K001 红色曲线）；
- 自创品牌词无人搜，排第一也没流量（a_e142be96104363#K003）。

**校验**：
- 人工对照：把决策输入 `serp-competitor-audit`，跑一遍对手页面，看决策是否仍成立；
- 用 `replication_similarity` eval 题集验证是否能复刻哥飞原文的判断路径。

## 引用映射

| 决策点 | 文章证据 |
|---|---|
| 看趋势方向 | a_37d7fc779db178#K001 |
| 看竞争度，不是看新旧 | a_efddc06e0fee3a#K004 |
| KGR 量化蓝海词 | a_efddc06e0fee3a#K006 |
| 阻力 = 变现效率 | a_02bc6c6e55718a#K002 |
| 新词玩法三级 | a_e37860903b7c01#K008 |
| 高天花板 vs 低竞争 | a_2cdfa864b2d091#K004 |

## 已知边界

- 不覆盖**付费流量 ROI 评估**（那是 `keyword-research`）；
- 不覆盖**网站能否上线**的技术体检（那是 `technical-seo-triage`）；
- 哥飞原文无"SERP intent 分类法"明确指令，因此本 Skill 用 SERP 页面形态代替；如需更细需外部文档。
