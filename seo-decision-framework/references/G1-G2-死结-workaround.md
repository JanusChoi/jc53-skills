# G1/G2 死结 + Workaround 清单

> **来源**：2026-10-11 user 5 条筛子实战。当规划师（Keyword Planner）/ Ahrefs / Semrush 不可得时，怎么继续。

## G1 死结：没有规划师精确月搜

### 表现
- 不知道每个候选词的精确月搜
- 不知道每个国家的搜索量分布
- 不知道精确 CPC（广告主出价）

### Workaround 优先级

| 渠道 | 数据 | 限制 | 5 条筛子用法 |
|---|---|---|---|
| **Google Trends 12 月曲线** | 0-100 相对兴趣 | 不等于绝对数；只反映兴趣 | 筛子 1（盘子）/ 3（窗口） |
| **Google Trends 7 天曲线** | 0-100 短期 | 同上 | 筛子 3（窗口） |
| **Google Trends 24h 热搜** | 各国 | 10/10 报告 429 风险 | 找新词阶段用 |
| **Steam / Roblox 在线** | 实时在线人数 | 游戏类 | 筛子 1（玩家基数）|
| **Similarweb 着陆页** | 月访问 / 国家 | 部分需付费 | 筛子 1 + 2 |
| **攻略站 sitemap** | 7 天新页面 | 间接信号 | 筛子 1（趋势）|
| **Reddit/HN upvotes** | 24h / 7d | 间接热度 | 筛子 1 + 3 |
| **AIGCRank 公开榜** | 月访问 + 排名 | 公开 | 筛子 1 + 2 |
| **Product Hunt upvotes** | 周/月 | 公开 | 筛子 1 + 3 |
| **Tracxn 公开榜** | 部分免费 | 间接 | 筛子 1 |

### 标"待补规划师"规则
- **5 条筛子预判可基于上述 workaround 跑完**——**不卡死**
- 输出决策层级：
  - 5 条全过 = "yes（待规划师确认）"
  - 5 条过 3-4 = "待 G1/G2 补全"
  - 5 条过 ≤ 2 = "no"
- 只有筛子 1（盘子）= 0 过才直接出局

## G2 死结：没有 Ahrefs / Semrush 精确 KD

### 表现
- 不知道主词精确 KD
- 不知道下游词 KD
- 不知道 SERP 前 10 站点 DR / 外链

### Workaround 优先级

| 渠道 | 数据 | 限制 | 5 条筛子用法 |
|---|---|---|---|
| **DDG / Bing SERP 前 10** | 域名 / 标题 | 公开 | 筛子 5（盘面）|
| **SERP 形态** | 大站 / 媒体 / wiki 占比 | 公开 | 筛子 5（盘面）|
| **MozBar 公开数据** | 部分 DR | 浏览器插件 | 筛子 5（盘面）|
| **Ahrefs 免费外链检查** | 单页外链 | 限速 | 筛子 5（盘面）|
| **archive.org 首次上线** | 时间 | 公开 | 筛子 3 + 5 |
| **10/10 报告已有 KD** | 38.9 / 59.1 等 | 部分词 | 已知词的筛子 5 |

### 标"待补 KD"规则
- 主词 KD 已知 = 5 条筛子完整
- 主词 KD 未知 + 下游词 KD 未知 = 筛子 5 部分用 SERP 形态判
- 标"KD 待补"——不阻塞决策，但精确度降低

## G3 死结：Google 搜索结果页被 ban（10/10 报告）

### 表现
- Lynx UA 返回 2.4KB 空页
- Chrome UA 返回 JS 跳转页
- Startpage 303 / Brave 429
- DDG lite 被验证码拦住

### Workaround

| 替代渠道 | 数据 | 限制 |
|---|---|---|
| **Bing 搜索** | 公开 | 限速 + 漏词 |
| **DDG lite**（短窗口）| 公开 | 验证码 |
| **Brave Search** | 公开 | 429 |
| **公开 Nitter mirror** | Twitter 间接 | 不稳定 |
| **攻略站站内搜索** | 间接 | 限特定词 |

### 通用规则
- **新词发现任务默认不用浏览器 Google Trends**（G1+G2+G3 三重死结）
- **用 6 个公开 RSS/API 替代**（Reddit/HN/PH/攻略站/AIGCRank/Nitter）
- **Google Trends Trending now** 仍有 429 风险——subagent 跑前先 ping 一次

## G4 死结：Trends 实时曲线（已 ban）

### 表现
- 10/04 报告：Trends 上升词 429
- 10/10 报告：Trends 上升词这轮几乎没跑（429）

### Workaround

| 替代 | 数据 | 限制 |
|---|---|---|
| **HN 算法推荐** | 24h 热门 | 不直接是搜索趋势 |
| **Reddit trending 板块** | 24h 热门 | 不直接是搜索 |
| **攻略站 7 天新页面** | 7 天趋势 | 间接 |
| **Tracxn 公开榜** | 月榜 | 滞后 1-2 月 |

## G5 死结：Chrome Web Store 反爬

### 表现
- Chrome 商店搜索被反爬拦
- 不能批量查 Chrome 插件数据

### Workaround
- 关注宗源/友哥推荐的插件（a_085a52330daf7e#K008）
- 监控 Product Hunt + Reddit 的 r/chrome_extensions 板块
- 用 selenium 模拟（成功率低）

## G6 死结：Twitter/X API 付费

### 表现
- X/Twitter API 付费墙
- 公开搜索被反爬

### Workaround
- **Nitter mirror RSS**（nitter.net / nitter.poast.org）
- 关注大 V 列表（按 gefei-kb a_eaf39f008e3020#K004）：
  - @xiaohu_art（小互）
  - @OrangeAI666
  - @l1ang0_official（歸藏）
  - @dreaming_tulpa
- 公开 RSS 镜像稳定性差——subagent 跑前先 ping

## Subagent 设计原则

任何"找新词"subagent 必须：
1. **开工前先 ping 6 个公开渠道**（5 分钟）——确认能跑通
2. **失败的渠道记 warning 不阻塞**——其他 5 个继续
3. **每个候选词都标"待补 G1/G2"**——不卡死流程
4. **输出"窗口状态 + 5 条筛子预判"**——user 决策
5. **不知道的不编造**——硬要给数字就用 5 档（超大/大/中/小/微）

## 关联文件

- `5-筛子-决策框架.md`：5 条筛子用法
- `任务分类-验证-找新-挖长尾.md`：3 类任务的工作流差异
- 主 SKILL.md：方法论层
