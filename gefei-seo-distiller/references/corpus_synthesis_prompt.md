# 跨文章综合蒸馏 Prompt

## 输入

- `compiled/knowledge.jsonl`：逐篇证据验证通过的知识单元。
- `compiled/index.json`：数量、分类及来源目录。
- 不要只输入频次排行榜；尽量保证同主题知识单元的完整文本上下文可读。
- 若有 Blueprint v0.2 或更新版本，其内容只用于 Phase 4 的“架构映射”，不能反向改变原文含义。

## 角色与目标

你是“方法论编译器”，要把零散公众号文章编译成 **供 SEO 教练回答与执行的知识资产**。不可把高度相关当因果；不可把数年前的流量结果当成今天仍可复制的承诺。

## 必须依次处理的六个任务

### 1. 同义规则合并，但保留来源

按实际问题与条件归并，而不只是按关键词聚合。每个合并规则记录：

- `rule_id`，`claim`，`conditions`，`input_data`，`decision`，`next_action`，`stop_or_fallback`
- 证据集合 `[{article_id, unit_id, published_at, source_url}]`
- 是否同一文章多次提及（不可冒充多来源支持）
- `evidence_level`: direct_single / direct_multiple / synthesized / speculative
- 哪些情况不适用、作者是否明确给过失效反例

### 2. 建立分支决策树

对每个高价值决策构造 `If → Check → Then → Else → Verify`。
例如“这个词值不值得建站？”必须明确还需取得哪些真实外部数据，以及数据显示空缺时怎么退化；不能给没证据支持的 KPI 阈值。

### 3. 重建可执行 SOP

SOP 结构：

```
name / intent / when_to_use / inputs / prerequisites
steps: [{action, tool_or_data_required, expected_result, failure_branch}]
exit_conditions / safety_constraints / citations
```

不要把抽象原则“持续优化页面”伪装成已具备数据依赖和验收标准的可执行工作流。

### 4. 建案例账本（Success + Failure）

每个案例：项目/域名，发布时间、来源角色，起因、动作、成本、时间窗、结果、指标口径、可能混杂因素、是否可重复、未核实数据与作者归因。若缺少结果或成本，必须标 `unknown`。

**不要只保留成功学素材**；输出失败案例、反例及作者主动修正的路径。

### 5. 观点演变与冲突

按主题生成时间线表：

```
topic | older_claim | older_date | newer_claim | newer_date |
conflict_type (real contradiction/context-dependent/different timeframe/unknown) |
resolution_or_unknown | evidence_links
```

案例：一篇早期文章鼓励大规模多语言页，较新文章警告批量低质翻译。若无法从原文确认适用条件不同，不要强行和解。

### 6. 知识与能力分包

- `RAG`：事实性案例/解释/带出处的观点。
- `Skill`：可触发可执行 SOP、判断规则和失败分支。
- `Tool Specification`：获取 SERP/KD/GSC/源代码等外部数据接口的输入输出契约。
- `Evaluation`：测试题、必须考虑的反例、预期决策与评分标准。
- `Blueprint Bridge`：与黑盒对话记录相互印证的部分，分别标注 `Observed / Inferred / Speculative`。

## 最终必须生成的文件

1. `synthesis/methodology.md`：八维全景，各章节有关键规则和来源；区分“本人明确主张/综合推断/第三方观点”。
2. `synthesis/decision_rules.md`：规则卡和条件/例外/引用。
3. `synthesis/playbooks.md`：按场景的运行 SOP（选词、站点诊断、页面矩阵、分发、复盘等，**仅写证据足够的场景**）。
4. `synthesis/casebook.md`：正反案例账本。
5. `synthesis/contradictions.md`：冲突、时间线与未决项。
6. `synthesis/unknowns.md`：文章无法给出的数据、缺失工具、未证实归因，下一批最该补哪类文章。

在每个文件开头写 `Corpus articles N / units M / coverage window / known gaps`，防止读者以为材料覆盖所有时期。

## 输出风格

精准、条件化、工程化。不要夸大“可以百分百复制”或“月访问百万必达”；不得提供虚构的 Google 排名/关键词量。引用采取 `article_id#unit_id`，在文末或旁边能回溯 source URL 与日期。
