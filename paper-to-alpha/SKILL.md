---
name: paper-to-alpha
description: |
  从 arXiv 量化论文挖掘 alpha 因子 —— 把学术研究转成可落地的 AlphaHypothesis。
  触发：当用户说"挖论文"、"paper to alpha"、"arxiv 挖因子"、"新 alpha 灵感"、
  "从论文找因子"、"看看最新 q-fin 有啥"、"跑一遍 paper_to_alpha"时使用。
  核心：5 步法 SOP（核心提取 → 定位校准 → 价值质疑 → 量化映射 → 实证验证），
  把学术概念映射成可计算的代理因子，写入 AlphaHypothesis 库待审阅。
  不用于：单只股票分析（用 equity-snapshot）、持仓逻辑跟踪（用 thesis-tracker）、
  市场盘面复盘（用 market-daily-review）、公众号论文分析文章（用 wechat-draft-publisher）。
---

# Paper-to-Alpha Skill

> 定位：从 arXiv 量化论文挖 alpha 的标准化工作流。验证过的案例：Alpha-R1 (4/5 推荐)、
> FactorMiner (v0.3.0 核心)、Epiplexity (SOP 测试)、Entropy Regularization (暂不集成)。
> 单篇完整拆解 45-60 分钟（含验证计划）。

## Inputs to collect

- **论文来源**（必填）：arXiv ID / 论文标题 / 关键词方向
- **方向聚焦**（选填）：q-fin.PM/MF/TR/ST 等子类别，或"动量/反转/量价/情绪/多因子/组合优化"
- **资产类别**（必填）：A股 / 港股 / 美股 / 加密货币 / 多资产
- **预期产出**（必填）：只产 AlphaHypothesis / 同时输出公众号文章 / 同时升级为 thesis

## Procedure

### 阶段 0：抓论文（脚本化）

**首次/批量抓取**：
```bash
python3 /Users/januswing/code/agent-cio/strategy_miner/scripts/arxiv_scraper.py
```
输出：`/Users/januswing/code/agent-cio/strategy_miner/data/arxiv_papers.json`（最近 30 天 q-fin 全集）

**单篇精读**：webfetch `https://arxiv.org/abs/{ID}` + `https://arxiv.org/pdf/{ID}.pdf`，读摘要 + 关键章节。

### 阶段 1：核心提取（旧 vs 新）

> 旧常识 → 新概念 → 一句话总结。没"旧"就没有"新"，论文就不值得挖。

```
论文：[标题]
旧常识：[业界/学界此前怎么想]
新概念：[这篇论文提出什么新东西]
一句话：[30 字以内的核心洞见]
```

**纪律**：
- "一句话"必须能讲给 18 年经验的交易员听懂，禁术语堆砌
- 例：Alpha-R1 = "用 8B 推理模型，根据市场新闻动态开关因子"

### 阶段 2：定位校准（边界 + 类比）

```
**理论定位**：[局部修正 / 大一统 / 颠覆 / 跨界迁移]
**适用边界**：
  - ✅ 适用：[场景 A / 场景 B]
  - ❌ 不适用：[场景 C / 场景 D]
**类比**：[用读者已知的概念类比]
```

**纪律**：
- 必须显式说"适用 / 不适用"——这决定能不能落地
- 类比落到交易员熟悉的领域（K 线/形态/趋势/均值回归）

### 阶段 3：价值质疑（So What?）

**三连问**：
1. **解释现象**：[这篇论文能不能解释一个真实市场现象？]
2. **指导实践**：[能直接指导策略开发吗？怎么指导？]
3. **核心视角**：[它挑战/补充了哪个我们之前的假设？]

**判据**：
- 三问全答不上 → 价值低，存档即可
- 答上 1 个 → 继续走阶段 4
- 答上 2-3 个 → 高价值，重点拆解

### 阶段 4：量化映射（学术 → 因子）

> 整个 SOP 的核心：把学术概念翻译成可计算的代理因子。

| 学术概念 | 量化映射 | 可计算代理 |
|---------|---------|-----------|
| [原文术语] | [金融/交易语言] | [Python 公式/库名，要能直接写代码] |

**纪律**：
- **每一行必须三列都填**——填不出"可计算代理"就不是 alpha
- "可计算代理"要写到能直接写代码（例：`Hurst(close, 100) > 0.5`）
- 显式标注：方向（多/空）、频率（日/周/月）、数据要求

**已验证可代理化的概念库**：
- 时间记忆性 → Hurst 指数 / 方差比检验
- 模式重复性 → LZ 复杂度 / 排列熵
- 波动率聚类 → GARCH / 已实现波动率
- 情绪信号 → 新闻嵌入 + 主题聚类
- 因子衰减 → 滚动 IC + 半衰期回归
- 市场状态 → HMM / 隐含波动率分位
- 因子动态选择 → LLM + 新闻嵌入 → 因子权重

### 阶段 5：实证验证（可执行计划）

> 没有验证计划的拆解 = 纸上谈兵。

**三档验证**：
1. **单标测试**：[选哪只标的？为什么？用什么数据？]
2. **多窗口**：[20d / 60d / 250d 滚动，验证什么？]
3. **全市场扫描**：[A股 / 港股 / 美股池子？分组方案？]

**预期结果表**（必填）：
| 场景 | 旧方法 | 新方法（论文思路） |
|------|--------|-----------------|
| 牛市 | [基线] | [预期改进] |
| 熊市 | [基线] | [预期改进] |
| 震荡 | [基线] | [预期改进] |

**数据要求清单**：
- 价格数据：[周期 / 长度 / 来源]
- 基本面数据：[字段 / 频率 / 来源]
- 另类数据：[新闻 / 舆情 / 资金流]

### 阶段 6：写入 AlphaHypothesis 库（脚本化）

```bash
python3 /Users/januswing/code/agent-cio/strategy_miner/scripts/paper_to_alpha.py
```

**自动生成**：
- `potential_score`（20-95）：基于关键词加权（trading +15、sentiment +8、theory -10）
- `confidence_score`（5 维度加权）：logic / market_fit / data_availability / timing
- `key_insight`：摘要前 200 字
- `factor_source`：原始论文 metadata
- 状态：默认 `waiting_review`

**手动补充**（脚本不能自动生成）：
- 5 步法拆解正文 → 写到 `key_insight` 或单独 md 报告
- 验证计划 → 写到 `backtest.config_ref`
- 风险评估 → 写到 `review.notes`

### 阶段 7：审阅与流转（人工闭环）

| 状态 | 含义 | 后续动作 |
|------|------|---------|
| `waiting_review` | 待审 | 用 thesis-tracker 跟踪假设 |
| `reviewing` | 审阅中 | 用 informer-query 找历史先例 |
| `rejected` | 拒绝 | 归档 + 写失败约束到记忆库 |
| `backtesting` | 回测中 | 用 thesis-tracker 跟踪验证进度 |
| `deployed` | 已部署 | 接进 B 策略 / A 股策略体系 |
| `archived` | 已归档 | 失效或退役 |

**审阅 checklist**：
- [ ] potential_score 是否被关键词加权合理（漏算有意义的信号？）
- [ ] 5 步法每一档是否都填了
- [ ] 量化映射表每一行三列是否齐全
- [ ] 验证计划是否具体到数据/时间窗口
- [ ] 失效场景（证伪条件）是否写出

## Output contract

完整 paper-to-alpha 报告（Markdown，参考 Alpha-R1 样板）：

```markdown
# Paper-to-Alpha: [论文简称]

**论文**：[完整标题]
**arXiv**：[ID]
**发布日期**：[YYYY-MM-DD]
**拆解日期**：[YYYY-MM-DD]
**拆解人**：[agent / human]

---

## Step 1: 核心提取

```
论文：[标题]
旧常识：[业界/学界此前怎么想]
新概念：[这篇论文提出什么新东西]
一句话：[30 字以内]
```

**旧 vs 新**：
- **旧**：[旧方法]
- **新**：[新方法]

---

## Step 2: 定位校准

**理论定位**：[局部修正 / 大一统 / 颠覆 / 跨界迁移]
**适用边界**：
- ✅ 适用：[场景]
- ❌ 不适用：[场景]
**类比**：[类比]

---

## Step 3: 价值质疑

**So What?**

1. **解释现象**：[现象 + 论文解释]
2. **指导实践**：[怎么用]
3. **核心视角**：[新认知]

---

## Step 4: 量化映射

| 学术概念 | 量化映射 | 可计算代理 |
|---------|---------|-----------|
| ... | ... | ... |

---

## Step 5: 实证验证

### 验证计划
- [ ] 单标测试
- [ ] 多窗口
- [ ] 全市场

### 预期结果
| 场景 | 旧方法 | 新方法 |
|------|--------|--------|
| ... | ... | ... |

---

## 集成方案

**生态位**：[在策略体系中的位置]
**熔断规则**：[什么情况下停用]
**Cron Job**：[定时任务]

## 风险评估

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| ... | ... | ... | ... |

---

## 结论

**推荐指数**：⭐⭐⭐⭐ (X/5)
**理由**：[3 条]
**下一步**：[3 条可执行]
```

## Failure handling

| 情况 | 应对 |
|------|------|
| 抓不到论文（arXiv API 失败） | 重试 / webfetch abs 页 |
| 摘要太短无法判断 | 读全文 PDF 限前 8 页 |
| 5 步法某一步填不出 | 标记"待补"，不强写 |
| 量化映射表"可计算代理"列写不出 | 强制打回：这不是 alpha，改投 thesis-tracker |
| 验证计划太抽象 | 强制要求"具体标的 + 时间窗口 + 指标" |
| potential_score < 40 | 脚本自动跳过，不写入 |
| 同一论文 30 天内重复 | 脚本基于 title 去重 |
| arXiv ID 读不到 | 标注"待获取"，不进库 |

## Examples

**Input 1**: "从 arxiv 挖一篇动量因子的新论文"
**Output 1**: 跑 arxiv_scraper → 筛关键词 → 完整 5 步法拆解 → 写入 AlphaLibrary

**Input 2**: "这是论文链接 https://arxiv.org/abs/2512.23515，帮我 paper to alpha"
**Output 2**: webfetch → 5 步法拆解 → AlphaHypothesis + Markdown 报告

**Input 3**: "跑一遍 paper_to_alpha.py 看看到底生成了多少 alpha"
**Output 3**: 跑脚本 → 输出统计 + 列出 waiting_review 列表

**Input 4**: "复盘挖过的论文里哪些真的落地了"
**Output 4**: 跨 alpha 库统计 + 推荐指数分布 + 落地率

## 配套资源

### 已挖过的案例（参考样板）
- `~/.openclaw/workspace/nboost/memory/paper-to-alpha-alpha-r1.md` — 194 行完整样板
- `~/.openclaw/workspace/nboost/memory/paper-to-alpha-test-epiplexity.md` — SOP 测试案例
- `~/.openclaw/workspace/nboost/memory/paper-to-alpha-validation-2026-03-05.md` — 验证报告 + v0.3.0 路线图

### 核心脚本（路径固定，不要改）
- `~/code/agent-cio/strategy_miner/scripts/arxiv_scraper.py` — 抓论文
- `~/code/agent-cio/strategy_miner/scripts/paper_to_alpha.py` — 转 Alpha
- `~/code/agent-cio/alpha/schema.py` — AlphaHypothesis 数据结构

### Alpha 库位置
- 主库：`~/code/agent-cio/alpha/library/YYYY-MM-DD/`
- 索引：`~/code/agent-cio/alpha/index.json`
- 状态机：`waiting_review → reviewing → rejected/backtesting/deployed → archived`

### 已挖论文存档
- `~/code/agent-cio/strategy_miner/data/arxiv_papers.json` — 最近 30 天 q-fin 全集
- `~/code/agent-cio/papers/` — 重点论文 PDF

### 关联 skill
- `thesis-tracker` — 把 alpha 升级为正式 thesis 时调用
- `equity-snapshot` — 单标验证时调用
- `informer-query` — 找历史先例，做来源审计
- `druckenmiller-framework` — 宏观主题级论文时联动
- `wechat-draft-publisher` — 同步出公众号论文分析文章时联动

## 关键纪律（再强调）

1. **没"旧 vs 新"就不挖**——过滤水文论文第一道关
2. **可计算代理必须能直接写代码**——填不出就别勉强
3. **验证计划必须具体到数据/时间窗口/标的**——"用历史数据回测"无效
4. **证伪条件必须显式写**——失效场景比适用场景更重要
5. **arXiv 数据要标注抓取日期**——避免数据库滞后陷阱
6. **脚本输出后必须人工审阅**——potential_score 是启发式不是真理
7. **失败案例要记入 memory**——避免重复挖同一篇 / 同一类无效论文