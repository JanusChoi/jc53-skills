# 从方法论蒸馏产物到可复刻 SEO Agent

**重要区分**：公众号文章能证明“作者表达了某方法”，不能证明原版 Agent 的隐藏实现方式。后者必须结合真实 Agent 对话/工具痕迹验证。

## 四类资产的不同消费方式

| 资产 | 用于解决 | 推荐格式 | 不应做的事情 |
|---|---|---|---|
| RAG Knowledge | 解释概念、引用案例、提供出处 | `knowledge.jsonl` + 搜索索引 | 把过时案例当当下实时数据 |
| Skills | 按条件执行完整 SOP | 单独 `SKILL.md` | 没有执行链就硬包装为 Skill |
| Tools | 获取真实外部数据、执行动作 | 函数接口/schema/错误协议 | 把 Agent 提到的名词当成现成接口 |
| Eval | 验证 Agent 会判断而非胡说 | 测试集 JSONL | 使用训练过的原文作为未见测试样本 |

## 规则 → Skill 的转换标准

满足以下至少三点才适合编译为一个 Skill：

1. 有明确任务触发语义。
2. 有明确输入/输出。
3. 有 2 个以上有顺序或条件依赖的步骤。
4. 能说清楚需要什么 Tool、拿不到数据怎么办。
5. 能说清楚成功条件、反例或校验方法。

例：`new-site-opportunity-review`、`technical-seo-triage`、`serp-competitor-audit`、`sitemap-page-matrix`。

如果只有原则“多用长尾词”，应留在 RAG，不要强行编译成 Skill。

## 可复刻 SEO Agent 的输入/输出契约模板

```yaml
skill: keyword-opportunity-review
intent: 评估某个词是否有新站机会
input:
  keyword: string
  country: string
  language: string
  business_model: string | null
requires:
  - SERP top results
  - evidence-backed search-volume data (optional; absent must say unknown)
  - ranking-domain age (optional)
steps:
  - query SERP
  - identify dominant page intent and new sites
  - inspect ranking-page format
  - compare with user/product intent
  - produce conditional recommendation
missing_data_branch: 不对未知搜索量编造数字；要求核实或只给待验证假设
output: opportunity_analysis_with_citations
```

模板仅用于说明，不代表哥飞原版 Agent 真的实现了同名 Skill。

## Blueprint Bridge 输出模板

```markdown
| 方法或需求 | 文章证据 | 黑盒 Agent 证据 | 分类 | 结论 | 下一步验证 |
|---|---|---|---|---|---|
| 技术 SEO 先排雷 | article_id#K001 | Sample 2: fetch_source | Observed behavior / Inferred internal workflow | 可能是诊断 SOP，但 Skill 文件未证实 | 观察独立 page_coach 调用 |
| 用户提到 GSC | article_id#K007 | Sample 2: GSC 数据文件提示 | Observed Tool UI, implementation unknown | 不能假定 OAuth API 实时直连 | 观察文件导入链路 |
```

若某知识没有黑盒对话佐证，分类 `Knowledge-only`，不要赋予其“原版工具已证实”的标识。

## 对接已有 Blueprint v0.2

- 对齐可能的 Workflow：批量竞品研究、Sitemap 解析、站点体检、新站修复复测、知识库增强回答。
- 对齐已看到的 Tool UI：谷歌搜索、域名概况、域名注册、抓取源码、关键词难度/搜索量、GSC 入口、知识库检索/读全文。
- `serp_review`、`page_coach` 等仍为待证实名称，文章最多证明其所需的 SEO 方法和数据要求。

## RAG Chunk 推荐字段

```
unit_id, article_id, source_url, title, published_at, author,
dimension, kind, claim, conditions, evidence_quote, attribution,
time_scope, confidence, linked_playbooks, counterexamples
```

向量检索可以使用 `claim + conditions + context`，答案必须回带 `article_id/URL` 原文引用。工具获取的实时数据应与 RAG 中历史数字隔离。

## 评测建议

建立三个基准：

- **规则保持**：能否识别正确条件、决策与错误前提。
- **边界意识**：无搜索量/GSC 时是否承认不确定、是否避免编造。
- **复刻相似度**：与已观察样本对照是否有类似工具选择、澄清与执行步骤；不得仅用“语气像”来打分。

留出部分文章与案例做 **holdout**，不要把它们同时放入知识库和测试答案。对需要真实数据才能回答的问题，给假的/缺失的工具响应测试其退化行为。
