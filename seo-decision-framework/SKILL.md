---
name: seo-decision-framework
description: Use when 拿蒸馏产物做"该不该上这个词"决策。5 条筛子 + G1/G2 workaround + 任务分类。
version: 1.0.0
author: 哥飞蒸馏实战校准 (2026-10-11)
license: MIT
metadata:
  hermes:
    tags: [seo, decision-framework, keyword-research, gefei]
    related_skills: [gefei-seo-distiller, investor-distiller, expert-lens-reasoning]
---

> **定位**：蒸馏完成后怎么用蒸馏产物做"该不该上"的决策。**不是**蒸馏本身（那是 `gefei-seo-distiller` 等 skill 的活）。
> **来源**：哥飞 2130 knowledge_units + 用户强信号校准（2026-10-11）+ Adsense 单价真实数据 + G1/G2 死结 workaround。

## When to Use

- user 拿一个候选词（japanese ramen simulator / 7 days cat sitting / huss valley / kabuki 等）问"该不该上"
- user 拿到 6 个公开渠道信号（Reddit/HN/PH/攻略站/AIGCRank/Nitter）要求找新词
- user 给 1 个主词要拆下游词族
- user 拿不到规划师（Keyword Planner）/ Ahrefs / Semrush 时跑 SEO 决策
- user 蒸馏完哥飞/其他博主后不知道"接下来怎么用"

**不要用于**：
- 蒸馏本身（→ `gefei-seo-distiller` / `investor-distiller`）
- 已装好的 SEO skill 触发（→ `~/.hermes/profiles/cio/skills/seo/` 下 5 个 skill）

## 任务类型（启动前先确认）

**不要**默认走"挖已知词长尾"——3 种任务的输入/输出/Subagent 完全不同：

| 任务 | 输入 | 输出 | 触发关键词 | Subagent 抓什么 |
|---|---|---|---|---|
| A. 验证已知词 | user 给的候选词（≤10） | 每词"该不该上"决策 | "该不该"/"值不值得" | 已知词数据补全（5 条筛子） |
| B. **找新词** | 6 个公开渠道信号 | 新候选词（20-50） | "找"/"挖新"/"新发现" | Reddit/HN/PH/攻略站/AIGCRank/Nitter RSS |
| C. 挖已知词长尾 | 1 个主词 | 下游词族 | "拆"/"长尾"/"主词 + 后缀" | 主词拆 codes/calculator/tier list/walkthrough |

**user 说"找新词"时默认 B**——不要退化到 A 或 C（user 抓过 2026-10-11 这种误读）。

## 核心：5 条筛子（按顺序跑，前面的不通过直接出局）

详见 `references/5-筛子-决策框架.md`。

| # | 筛子 | 关键判断 | 不通过 = |
|---|---|---|---|
| 1 | **先看盘子在哪、多大** | 规划师多 gl（us/ng/gb/world）——最高量国家只有 50/月 | 出局 |
| 2 | **量按"目标国家 × 单价"折算** | 哥飞 2024-08 Adsense 单价：瑞士 7.34 / 美国 4.34 / 中文秋玉米 0.54 美元/千次展示 | 低单价 10 倍量 ≠ 别人 1 倍 |
| 3 | **看「新词」还是「老词被引爆」** | 12 个月曲线趋势 + 7 天 vs 1 天 | 窗口 1-3 天，错过就过峰 |
| 4 | **拆下游词，别打主词** | 主词 `xxx codes` / `xxx calculator` / `xxx tier list` / `xxx release date` | Roblox codes 类能到 6-7 万月搜（shindo life codes 61k / jjk movie 74k）|
| 5 | **最后才是 KD 和盘面** | DDG SERP 前 10 + MozBar | KD 低是必要非充分，lagos life KD 26.9 卡 1+2 仍出局 |

## 已知错误锚点（避免重蹈覆辙）

### ❌ beebom 不是新词新站锚点
- beebom 是 DR 高的资讯内容站，月访问 600 万→1090 万是其他原因
- **正确锚点 = growagardencalculator.net**（5/28 域名 + 12 外链 + 1 个多月 160 万访问 = 新词新站的形状）

### ❌ EMD 不是新词本质
- 哥飞新词玩法分三级（出处：《2025.10.6 哥飞小课堂》pixelartvillage.com 流量暴涨分析，2025-10-10）：
  - 初级：跟进（别人上什么你也上）
  - 中级：预测（提前注册域名占坑）
  - 高级：创造（自己造词自己占坑）
- **三级里没有一级是"关键词必须做进域名"**——EMD 只是"预测"步骤里的一个动作
- **本质是"信息增量"**——哥飞原话：
  > "此时全网都没有能够满足搜索结果的网页，我们能够快速上线相关网页，即使内容写得没那么好，也是能够拿到排名的"
- 抢的是**首发**，不是域名

## G1/G2 死结 + Workaround

详见 `references/G1-G2-死结-workaround.md`。

| 死结 | 表现 | Workaround |
|---|---|---|
| G1（无规划师）| 不知道精确月搜 | Trends 12 月 + Steam/Roblox 在线 + 攻略站 sitemap RSS |
| G2（无 Ahrefs）| 不知道 KD | DDG SERP 前 10 形态 + MozBar 公开 + 10/10 报告已知 KD |
| G3（Google 搜索被 ban）| Lynx/Chrome UA 失效 | Bing + DDG lite 短窗口 + 攻略站站内搜索 |
| G4（Trends 实时曲线被 ban）| 上升词 429 | HN/Reddit trending + 攻略站 7 天新页 |
| G5（Chrome Web Store 反爬）| 不能批量查插件 | PH + Reddit r/chrome_extensions |
| G6（Twitter API 付费）| X 搜索反爬 | Nitter mirror RSS |

**通用规则**：subagent 跑前先 ping 6 个公开渠道（5 分钟），失败记 warning 不阻塞，**每个候选词都标"待补 G1/G2"**——不卡死流程。

## 关键概念

### 数据 vs 例子要分清
- 蒸馏产物给方法论，**真实数据才是决策依据**
- KD 26.9 ≠ 能赚钱——盘面小/单价低直接出局

### 新词窗口 = 1-3 天
- 数据 24h 内必看
- 案例：lagos life 1 天从 74% 跌到 39%（2026-10-08 → 10-10）

### 失败案例学习
- **lagos life**：盘面松（KD 26.9）但盘子小（美国 50/月）+ 单价低（尼日利亚）→ 出局
- **kabuki codes**：2 周窗口已过，DR72/78 已铺满 → 红海
- **dressmaker game**：跟风侵权 = 高风险
- **anyps5 主词**：版权灰色 + 媒体铺满 → 不上；**盯长尾**（compatibility list / games list / download）

## Pitfalls（必避）

1. **数据 vs 例子要分清**——蒸馏产物给方法论，**真实数据才是决策依据**
2. **不要"挖长尾"当"找新词"**——user 抓过这种误读。**启动前先确认任务类型**（A/B/C）
3. **不要默认用浏览器 Google Trends**——被 ban/验证码。用 6 个公开 RSS/API 替代
4. **不要引用 beebom 当新词新站锚点**——正确锚点是 growagardencalculator.net
5. **不要把"信息增量"简化成"抢域名"**——EMD 只是中级玩法的一个动作
6. **不要给缺 G1/G2 的词假装有数据**——标"待补"即可
7. **user 反馈错时不要抬杠**——立即认 + 改 + 沉淀
8. **❌ "SERP 空白 ≠ 新词窗口"**（2026-10-11 Talorys 教训）—— SERP 完全空白也可能是"**根本没人搜**"，不一定是"新词可抢"。**必须先查 GitHub stars + 创建时间预筛**（见 references/5-筛子-决策框架.md "GitHub 预筛" 段）
9. **❌ 深挖新工具前必查 GitHub**——`创建 ≤ 7 天 + stars < 1000` 直接降级 🔴，不深挖
10. **❌ 派发 subagent 别甩手**——user 强信号"派发后要盯着，不要放在那就不管"。派完立即 list 确认 running；3-5 分钟轮询 list；遇 503/超时立即 steer 或 stop；**完成才回**

## 决策层级（不是非黑即白）

```
主词
├ 5 条全过 = yes
├ 5 条过 4 = 待 G1/G2 补全
├ 5 条过 3 + KD 死 = no（主词不上）
└ 5 条过 ≤ 2 = no（出）

下游词族
├ 6 个候选各跑 5 条
├ 1 个全过 = 抢注 + 1-2 天上站
└ 全部 ≤ 2 过 = 词族放弃
```

## 关联文件

- `references/5-筛子-决策框架.md`：5 条筛子详细（每条数据源 + workaround + 案例）
- `references/任务分类-验证-找新-挖长尾.md`：3 类任务的输入/输出/Subagent 差异
- `references/G1-G2-死结-workaround.md`：6 类死结的具体 workaround 清单

## 配套 skill

- **`gefei-seo-distiller`**（research/）：蒸馏哥飞 + 任何出海建站/SEO 公众号
- **`investor-distiller`**（research/）：蒸馏投资博主（7 维 DNA）
- **`~/.hermes/profiles/cio/skills/seo/`** 下 5 个 skill（new-site-opportunity-review 等）：执行层
- **`expert-lens-reasoning`**（research/）：从公开事实到付费级判断
