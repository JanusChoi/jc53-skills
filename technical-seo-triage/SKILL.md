---
name: technical-seo-triage
source: gefei-seo-distiller
dimensions: [D4]
unit_count: 56
kinds: [decision_rule, procedure, anti_pattern]
author: 哥飞
sample_units:
  - a_0d301ec26d5342#K001
  - a_0d301ec26d5342#K002
  - a_0d301ec26d5342#K003
  - a_0d301ec26d5342#K004
  - a_0d301ec26d5342#K005
  - a_185dbc785ad7fd#K001
  - a_3676792356c8d7#K002
  - a_0ca83f1e35f464#K006
trigger_keywords:
  - 没有流量
  - 不收录
  - 排名掉了
  - GSC 数据
  - 抓取
  - 索引
  - 索引下降
  - 技术 SEO
  - 页面没排名
  - 改版后掉量
description: Use when 给一个站点做技术 SEO 五层漏斗诊断（爬行收录/抓取预算/索引/规范化/外链）。输出可执行修复列表与严重度。基于哥飞公众号 64 个 D4 knowledge_units 蒸馏。
---

# technical-seo-triage

按"流量消失 → GSC 分层 → 对症处置"顺序，定位**技术 SEO 问题**（发现 / 抓取 / 收录 / 曝光 / 点击）并给出操作清单。

## 何时触发

- 用户说"网站没流量 / 点击下降 / 不收录"；
- 用户说"改版后排名掉了"；
- 用户说"GSC 里看不到页面 / 页面爬取失败"；
- 任何 D4 维度（技术 / 收录 / 抓取）相关问题。

## 输入 / 输出

**输入**：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `site_url` | string | 是 | 站点根 URL |
| `date_range` | string | 是 | ISO 日期区间 "YYYY-MM-DD..YYYY-MM-DD" |
| `symptom` | enum | 是 | no_clicks / no_impressions / dropped_ranking / not_indexed / not_crawled / unknown |
| `gsc_property` | string \| "absent" | 否 | GSC 已验证的 property URL；缺失时走 `missing_data_branch` |

**输出**：

```yaml
diagnosis:
  layer: "discovery" | "crawl" | "index" | "exposure" | "click"
  root_cause: "..."  # 单行假设
  evidence:
    - metric: "..."
      observed: "..."
      expected: "..."
      cite: "article_id#unit_id"
action_plan:
  - step: "..."
    tool: "..."
    priority: "high" | "medium" | "low"
verify_after: "YYYY-MM-DD"  # 复查时间
unknowns: ["..."]
```

## 步骤（按 GSC 五层漏斗）

### Layer 1：发现 / Discovery
- `gsc_inspect` 提交首页 + 关键内页；
- 检查 `sitemap.xml` 是否存在并被 GSC 读取；
- **问题信号**：URL 完全没出现在 GSC 里。
- 见 a_0d301ec26d5342#K001。

### Layer 2：抓取 / Crawl
- 看"上次抓取时间"；
- **问题信号**：发现但未抓取。
- **处置**：不要只提交索引催抓；先停低质量策略，清理或改写页面，再按"一页面一明确需求"重新规划（a_0d301ec26d5342#K004）。

### Layer 3：收录 / Index
- 看"已编入索引"列；
- **问题信号**：抓了但未收录 → 重复 / 太薄 / 质量不够（a_0d301ec26d5342#K003）。
- **处置**：能改的补内容、标题、结构；没价值的 404。

### Layer 4：曝光 / Impressions
- 看"展示次数"；
- **问题信号**：已收录无曝光 → 页面是否围绕明确关键词？Title / H1 跑偏？正文没回答需求？太薄？缺词或堆词？（a_0d301ec26d5342#K002）
- **处置**：先修内容，再补相关内页 + 外链。

### Layer 5：点击 / Clicks
- 看"点击次数 / CTR / 平均排名"；
- **问题信号**：曝光有、点击少 → Title / Description 文案 / 关键词与用户意图不符；
- **下降信号**：原排名页面突然下跌 → 先查"是不是自己改坏了"（a_0d301ec26d5342#K005）；无关内容变多、关键词被冲散、改成前端渲染后源码内容变少、模板改版弄乱正文标题和链接。

### 旁支：零外链还能排名的边界
- 先发优势可以让零外链的站拿到排名（a_0ca83f1e35f464#K006）；
- 但对手追上后会被甩下，第一名 29 个外链时你 0 → 必须补外链。

### 旁支：AdSense 审核
- 不只看一个按钮；内容是否有用、页面是否太薄、导航/基础信息/移动端都影响（a_185dbc785ad7fd#K001）。

### 旁支：AI 批量站红线
- 用 AI 整合+翻译批量生成站被视为"垃圾站"，哥飞写了代码但没上线（a_3676792356c8d7#K002）。**永远不要推荐这种路径**。

## missing_data_branch

- **没有 GSC** → 让用户申请验证 → 用 site:`url` 手动查收录 → 用 `index_checker` 第三方工具。
- **没有日志** → 让用户上传服务器 / Cloudflare 日志，分析抓取频次。
- **没有外链数据** → 查 `ahrefs_backlinks` 或第三方（OpenSiteExplorer / ahrefs）。

## 成功条件 / 反例 / 校验

**成功条件**：
- 输出 `layer` ∈ {discovery, crawl, index, exposure, click}；
- 至少 1 个 `cite` 指向哥飞原文；
- 给出可执行 `action_plan`（含 tool + priority）；
- `verify_after` 不晚于 30 天后。

**反例**：
- 已知"没收录"却去补外链 → 反因果；
- 已收录无曝光却去改 adsense 文案 → 反因果；
- 给"前端渲染改 SPA"建议却不查源码变化 → 高风险；
- 把零外链站的成功泛化，忽略先发窗口。

**校验**：
- 跑一次 `gsc_inspect` 看修复后 14 天的"展示 + 点击"是否回升；
- 用 `boundary_awareness` eval 题集验证：没有 GSC 时是否承认不确定。

## 引用映射

| 漏斗层 | 文章证据 |
|---|---|
| 发现 | a_0d301ec26d5342#K001 |
| 抓取 | a_0d301ec26d5342#K004 |
| 收录 | a_0d301ec26d5342#K003 |
| 曝光 | a_0d301ec26d5342#K002 |
| 点击 | a_0d301ec26d5342#K005 |
| 零外链先发 | a_0ca83f1e35f464#K006 |
| AdSense 审核 | a_185dbc785ad7fd#K001 |

## 已知边界

- 不覆盖**站群链接风险**评估（那是 `serp-competitor-audit` + 外部 spam 评估）；
- 不覆盖**关键词替换**策略（那是 `keyword-research`）；
- 哥飞原文无"Pagination / Hreflang / Canonical"具体规则，需外部文档。
