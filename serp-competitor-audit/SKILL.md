---
name: serp-competitor-audit
source: gefei-seo-distiller
dimensions: [D2]
unit_count: 66
kinds: [decision_rule, procedure, case]
author: 哥飞
sample_units:
  - a_036ce74f8514f1#K001
  - a_036ce74f8514f1#K002
  - a_036ce74f8514f1#K004
  - a_12342cf81d1690#K006
  - a_154a476d3b5e99#K006
  - a_02bc6c6e55718a#K002
  - a_a2a23247ea1297#K002
  - a_a2ceb17c63aee0#K005
trigger_keywords:
  - 竞争对手
  - SERP 分析
  - 流量来源
  - 替代品页
  - 比较页
  - alternate 页面
  - 抢流量
  - 拆解竞品
description: Use when 给一个关键词查 SERP 首页 10 个结果的页面形态/站点权重/意图/反链结构，做 7 步竞品审计。判定"是否有新站切入空间"并给切入路径。基于哥飞公众号 56 个 D2 knowledge_units 蒸馏。
---

# serp-competitor-audit

拆解 **SERP 首页竞争者** + **相似站**（不一定是首页 SERP）的产品形态、流量结构、变现阻力，输出"差距点 + 上手位置"清单。

## 何时触发

- 用户问"对手为什么排前面 / 我能不能抢"；
- 用户问"alternative / 替代品 页面怎么写"；
- 用户问"做这类站的人流量从哪来 / 怎么变现"；
- 任何 D2 维度（竞争 / SERP / 替代品）相关问题。

## 输入 / 输出

**输入**：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `keyword` | string | 是 | 候选词 |
| `competitors` | list[string] | 否 | 用户给定的对手 URL 列表；省略时取 SERP 前 10 |
| `depth` | enum | 否 | "shallow"(只看首页 SERP) / "deep"(看流量来源+变现)，默认 deep |
| `country` | string | 否 | 默认 US |

**输出**：

```yaml
serp_summary:
  intent: "informational" | "transactional" | "navigational" | "mixed"
  page_formats: ["工具站", "内容站", "电商", "SaaS", "导航", "论坛", "PDF"]
  competitor_count: 10
competitor_cards:
  - url: "..."
    age_months: int | "unknown"
    authority_proxy: "DR" | "KD"
    format: "..."
    monetization_hint: "ads" | "affiliate" | "saas" | "leadgen" | "unknown"
    similarity_to_user: "high" | "medium" | "low"
gaps:
  - what: "..."
    why_it_matters: "..."
    action: "..."
follow_plan:
  - tool: "similarweb_rank" | "ahrefs_backlinks" | "aitdk_traffic"
    question: "..."
citations:
  - "article_id#unit_id"
```

## 步骤

1. **取 SERP 首页 10 条**
   - 工具：直接 `google_search`；
   - 看**主导页面形态**（工具站 / 内容站 / 电商 / SaaS / 导航 / 论坛 / PDF）；
   - 看**主导意图**。

2. **画像每个对手**
   - 域名年龄（`whois` / `archive.org`）；
   - DR / KD 趋势（`ahrefs_backlinks`，哥飞原文说 Ahrefs DR/排名"只作趋势"，a_aitdk 类原文证据）；
   - 流量结构（`similarweb_rank`：直接 / 搜索 / 社媒 / 外链）；
   - 变现提示（页面是否带 Adsense 自动广告 / Stripe / 下载按钮）。

3. **看相似站而非只 SERP**（a_a2a23247ea1297#K002）
   - 起点站不必和你要做的产品完全一样，只需用户和想服务的人有交集；
   - 每发现一个站至少记三件事：服务谁、用户完成什么、用户从哪进来。

4. **看对手的内容深度与广度顺序**
   - 已有排名的关键词站：先做深度、后做广度；首页原问题不能改（a_036ce74f8514f1#K001）；
   - 新功能放首页还是内页：看是否改变用户来这个页面要完成的事（a_036ce74f8514f1#K002）。

5. **看替代品页（alternate）写法**
   - 案例：Pallyy / SocialBee 对比页先承认对方优势再比差异（a_12342cf81d1690#K006）；
   - Tally 用专门页接"换工具的人"（a_154a476d3b5e99#K006）。

6. **变现阻力评估**
   - 多个产品竞争 SEO 免费流量时，体验好、阻力小者占优（a_02bc6c6e55718a#K002）；
   - SEM 付费流量：转化率强者吃掉大部分。

7. **识别差距点**
   - SERP 页面形态都烂 → 你做精致的可以抢；
   - 都没替代品页 → 你上一个 `[竞品名] alternative` 页；
   - 都靠 Adsense → 你加 SaaS / Affiliate 拉开客单价。

## missing_data_branch

- **没有 SimilarWeb** → 改用 `aitdk_traffic`（导航站流量估算）或 `trends.google.com` 反推；
- **没有 Ahrefs** → 用 `semrush_as`（Authority Score）替代；哥飞原文多次提到 Semrush 与 Ahrefs 同用；
- **没有 Whois** → 看 `archive.org` 最早快照年；
- **拿不到对手变现细节** → 看是否有 Stripe checkout 域名、SaaS 价格页、Adsense 公开案例。

## 成功条件 / 反例 / 校验

**成功条件**：
- 至少给出 1 张 `competitor_card`（即便 `competitors` 为空，至少 SERP 前 3）；
- `gaps` 列表至少 1 条，且 `action` 可在 7 天内启动；
- `citations` 至少 1 条。

**反例**：
- 把对手流量大直接等同变现强（a_914#K002：MCP.so 150 万访问但作者说一开始没赚到钱）；
- 把对手有 Adsense 当成可抄的广告位（要先查对手 Adsense 是否已满）；
- 只看首页 SERP，忽略"换工具意图"人群；
- 把"年龄比我久"当成无法超越的证据（哥飞原文有 2023 年 4 月注册站到 2025 年仍算新站的案例，a_33d08e80f2134a#K003）。

**校验**：
- 用 `replication_similarity` eval 题集验证对比卡是否按哥飞原文要求覆盖维度；
- 把 `gaps` 输入 `sitemap-page-matrix` 看落地可行性。

## 引用映射

| 步骤 | 文章证据 |
|---|---|
| 起点站 vs 产品 | a_a2a23247ea1297#K002 |
| 深度→广度 | a_036ce74f8514f1#K001 |
| 内页 vs 首页 | a_036ce74f8514f1#K002 |
| alternate 写法 | a_12342cf81d1690#K006 |
| 变现阻力 | a_02bc6c6e55718a#K002 |
| 访问量 ≠ 收入 | a_6aedba708c2c84#K002 |
| 域名年龄非绝对 | a_33d08e80f2134a#K003 |

## 已知边界

- 不评估对手**站群 / spam** 风险（需外部 backlink audit）；
- 不做对手**意图 / 产品**一对一映射（需人工）；
- 哥飞原文无"sandbox 沙盒期"明文，因此本 Skill 不评论沙盒。
