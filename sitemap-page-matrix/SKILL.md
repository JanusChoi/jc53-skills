---
name: sitemap-page-matrix
source: gefei-seo-distiller
dimensions: [D3]
unit_count: 81
kinds: [decision_rule, procedure]
author: 哥飞
sample_units:
  - a_036ce74f8514f1#K001
  - a_036ce74f8514f1#K002
  - a_036ce74f8514f1#K004
  - a_111a7feaaec465#K005
  - a_111a7feaaec465#K006
  - a_111a7feaaec465#K007
  - a_0be44cea16fbd5#K002
  - a_09daf7d346f307#K003
  - a_09daf7d346f307#K006
trigger_keywords:
  - 站内结构
  - 页面规划
  - sitemap
  - 内页
  - 架构
  - 新手村
  - 多站矩阵
  - 多个站
  - 关停水
description: Use when 规划一个站点的页面矩阵（Silo / Topic Cluster / 主页-内页-详情三层）。先深度后广度，输出页面清单 + 内部链接结构。基于哥飞公众号 71 个 D3 knowledge_units 蒸馏。
---

# sitemap-page-matrix

把站点拆成 **首页 + 内页 + 子工具** 的页面矩阵；按"练手站 → 进阶站 → 多站矩阵"三阶给出可执行的页面规划。

## 何时触发

- 用户问"我应该做哪些页面"；
- 用户问"内页怎么搭"；
- 用户问"做多少个站能赚到钱"；
- 用户问"域名 / 服务器 / 站群成本怎么压"；
- 任何 D3 维度（结构 / 架构 / 多站）相关问题。

## 输入 / 输出

**输入**：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `site_type` | enum | 是 | "tool" \| "content" \| "directory" \| "saas" \| "ecommerce" |
| `primary_keyword` | string | 是 | 主词 |
| `secondary_keywords` | list[string] | 否 | 内页候选词 |
| `stage` | enum | 否 | "novice" \| "intermediate" \| "advanced"，默认 novice |
| `budget_per_month_usd` | float | 否 | 域名 + 服务器预算，默认 0 |

**输出**：

```yaml
matrix:
  home_page:
    intent: "..."
    primary_keyword: "..."
    must_have_sections: ["..."]
  inner_pages:
    - url_slug: "..."
      target_keyword: "..."
      type: "deep_dive" | "tool" | "comparison" | "faq" | "list"
      priority: "P0" | "P1" | "P2"
  sub_sites:
    - domain: "..."
      purpose: "练手" | "进阶" | "养站" | "导流"
      monthly_cost_usd: float | "0"
hosting: "Vercel" | "Cloudflare Pages" | "传统VPS" | "..."
domain_strategy: "..."
citations: ["article_id#unit_id"]
```

## 步骤

### Step 1：定阶段（哥飞三阶）
- **练手站**：几乎没人竞争、但有人搜的词；日搜索量几十即可（a_111a7feaaec465#K005）。
- **进阶站**：每天几百搜索量；目标：新手村走出后攻更高竞争词（a_111a7feaaec465#K007）。
- **多站矩阵**：哥飞说"不做十个八个网站就无法积累经验"（a_0be44cea16fbd5#K002）；不能同一方法二十站，也不能一经验重复二十次。

### Step 2：定首页承接
- 已有排名的关键词站：先深度后广度；首页原问题不删（a_036ce74f8514f1#K001）；
- 主词还没站稳：先围绕主词找相关关键词、补紧密相关页面 + 有效外链（a_036ce74f8514f1#K004）；
- 新功能放首页还是内页：是否改变用户来这个页面要完成的事（a_036ce74f8514f1#K002）。

### Step 3：内页规划
- 每个内页对应一个独立搜索意图；
- 形态：deep_dive（深度） / tool（工具页） / comparison（对比页） / faq（问答） / list（清单）。

### Step 4：子站矩阵
- 养站成本低（Vercel / Cloudflare Pages）→ 每年赚回域名费即可长期养（a_09daf7d346f307#K006）；
- 养着的老站可给新站反向链接、帮新站更快收录（a_09daf7d346f307#K006）；
- 推 Vercel 类按访问量计费：流量小免费、流量大付费但已赚钱（a_09daf7d346f307#K003）。

### Step 5：域名 / 托管策略
- `site_type = tool` → 优先 EMD（Exact Match Domain）或 BM（Brand Match）；
- `stage = novice` → 一个主域吃所有内页；
- `stage = advanced` → 多域轮转，每个域一个核心方向。

## missing_data_branch

- **没有 `secondary_keywords`** → 用 `keyword-research` Skill 反推；
- **没有 `budget_per_month_usd`** → 默认按 Vercel / Cloudflare Pages 计，假定 0 ~ 5 USD；
- **没有现成外链策略** → 把外链这步单独喂给 `keyword-research`。

## 成功条件 / 反例 / 校验

**成功条件**：
- `matrix` 至少含 `home_page` + 1 个 `inner_pages`；
- `citations` ≥ 2；
- 给出可执行 `hosting` 推荐；
- 三阶段对应至少有 1 条原文支撑。

**反例**：
- 同一站套同一关键词做 20 个页面；
- 主词还没站稳就做大而全平台（a_036ce74f8514f1#K004）；
- 每月服务器花 50 USD 却月访问 1k（应换 Vercel / Cloudflare 类按访问计费）；
- 把"首页答所有问题"作为省事方案（这是新站最常见错误）。

**校验**：
- 把矩阵输入 `technical-seo-triage` 跑抓取 / 收录检查；
- 用 `replication_similarity` eval 题集验证页面规划步骤是否符合哥飞三阶。

## 引用映射

| 阶段 | 文章证据 |
|---|---|
| 练手站关键词 | a_111a7feaaec465#K005 |
| 进阶站关键词 | a_111a7feaaec465#K007 |
| 不做十个站不行 | a_0be44cea16fbd5#K002 |
| 深度 → 广度 | a_036ce74f8514f1#K001 |
| 首页 vs 内页 | a_036ce74f8514f1#K002 |
| 主词站稳前广度 | a_036ce74f8514f1#K004 |
| Vercel 计费 | a_09daf7d346f307#K003 |
| 养站成本低 | a_09daf7d346f307#K006 |

## 已知边界

- 不覆盖**Schema / Structured Data** 细节；
- 不覆盖**多语言站 hreflang** 细节；
- 哥飞原文无"信息架构 IA 命名规范"指令。
