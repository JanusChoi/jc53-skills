---
name: human-qa
description: >-
  Persona-driven web QA with two entry modes: (1) user-scoped focus testing,
  (2) git-diff regression case extraction over a time range — then the same
  human-simulation SOP and dogfood-style report. Use for human-qa, act-like-human
  test, 真人验收, diff 回归, or regression from recent commits.
version: 1.1.0
---

# Human QA

两种入口，**同一套后半程 SOP**（persona → Actor 逐步预期 → Judge → 标准化 report）。

| 入口 | 何时用 | 前半程多做什么 |
|---|---|---|
| **A · scoped** | 你指定范围与重点 | 把用户意图写成 brief + 用例清单 |
| **B · diff** | 你给仓库 + 时间窗（或 since/until commit） | 读 git log/diff，提取回归用例，再进入同一 SOP |

长板来源：adversarial（persona/过滤）+ dogfood（分级 report/复现两次）+ Expect（STEP 门禁、结构化失败、`next-agent-prompt`）+ 本仓库 round3 的「时段 diff → 诊断测什么」。

默认用 **Cursor 内置浏览器**。不要求 expect-cli。不要和 Expect CLI 混跑。

## 参数

| 参数 | 默认 | 说明 |
|---|---|---|
| Target URL | 必填 | 如 `https://tiwen.com` |
| Output dir | `./human-qa-output/` | 本轮产物根目录 |
| Entry | 必填 | `scoped` 或 `diff` |
| Repo | Entry=`diff` 时必填 | 本地 git 根目录 |
| Since / Until | Entry=`diff` | 如 `2 days ago`、commit SHA；Until 默认 `HEAD` |
| Scope | Entry=`scoped` 时必填 | 页面/路由/功能边界 |
| Focus | 可选 | 测试重点、忌讳、必测句 |
| Auth | 无 | 登录态说明；OTP 向人要码 |
| Production safety | 开 | 禁止注册/付费/删除/改他人数据，除非人明确授权 |
| Persona | 现场生成一个 | 一次一个角色 |
| Max cases | 12 | diff 入口提取用例上限（防膨胀） |

触发话术示例：

- scoped：`human-qa scoped https://tiwen.com 重点：定价页划线价和注册赠送文案`
- diff：`human-qa diff ~/code/tiwen-xphp since:"2 days ago" url:https://tiwen.com`

## 总流程

```
0. Init
1. Intake
   A scoped → 写 00-brief + 01-cases（用户范围/重点 → 用例）
   B diff   → 采 git → 写 00-brief + 00-diff-digest + 01-cases（回归用例）
2. Gate    → 用例需登录/破坏性？停下来问人；通过后继续
3. Persona → 01-persona.md（用例驱动任务，不是空泛「随便点」）
4. Actor   → 02-actor-log.md（预期 → STEP → 证据）
5. Judge   → 03-report.md（dogfood 风格标准化报告）
6. Wrap    → 汇总；未覆盖；是否开下一轮
```

A/B 只在步骤 1 不同；**4～6 完全相同**。

---

## 0. Init

```bash
mkdir -p "{OUTPUT_DIR}/screens" "{OUTPUT_DIR}/videos"
cp "{SKILL_DIR}/templates/report-template.md" "{OUTPUT_DIR}/03-report.md"
cp "{SKILL_DIR}/templates/cases-template.md" "{OUTPUT_DIR}/01-cases.md"
```

---

## 1A. Intake · scoped（指定范围）

写 `{OUTPUT_DIR}/00-brief.md`：

- Entry=`scoped`、URL、Auth、安全红线
- **Scope**：边界（含/不含）
- **Focus**：用户强调的重点（原话抄录）
- 成功看起来像什么（1～3 句）

写 `{OUTPUT_DIR}/01-cases.md`（3～12 条）：

- 每条：ID、标题、入口 URL/路径、前置（登录？）、步骤大纲、**期望**、优先级 P0/P1/P2
- 把 Focus 落成至少一条 P0；不要把范围外的探索塞进来
- 区分 `logged-out` / `logged-in`；后者缺 Auth 时标 `blocked-pending-auth`

然后进 **§2 Gate**。

---

## 1B. Intake · diff（时段 git → 回归用例）

### 1B.1 采集（在 Repo 内执行）

```bash
cd "{REPO}"
# 解析窗口（Until 默认 HEAD）
BASE=$(git rev-list -1 --before="{SINCE}" HEAD)   # 或用户给的 since SHA 的父/本身
TIP=$(git rev-parse "{UNTIL:-HEAD}")

git log --since="{SINCE}" --until="{UNTIL:-now}" --pretty=format:'%h %ad %s' --date=short
git log "${BASE}..${TIP}" --pretty=format: --name-only -- ':(exclude)*.lock' ':(exclude)*lock.yaml' ':(exclude)HANDOFF.md' \
  | sort | uniq -c | sort -rn | head -40
git diff --stat "${BASE}..${TIP}" -- ':(exclude)*.lock' ':(exclude)*lock.yaml' ':(exclude)HANDOFF.md' ':(exclude)*.vfs.txt'
```

规则（来自 Expect 实测坑）：

1. **排除噪音**：`package-lock.json`、`pnpm-lock.yaml`、`HANDOFF.md`、巨型字体/vfs、纯文档刷屏。  
2. **不要依赖「截断后的整包 diff」当唯一输入**：先做 digest（主题 + 热文件 + 高风险句），再按需对**单个热文件** `git diff BASE TIP -- path`。  
3. **未提交改动**：若 `git status` 脏，单独一节 `Unstaged` 列入 digest；默认**纳入**回归，除非用户只要已发布提交。  
4. 提交信息里的「fix / regression / tester」优先升 P0。

### 1B.2 写 digest

`{OUTPUT_DIR}/00-diff-digest.md` 必须含：

| 节 | 内容 |
|---|---|
| Window | BASE..TIP、since/until、分支 |
| Themes | 5～12 个主题簇（人话，不要只贴 commit subject） |
| Hot files | 触达次数/行数最高的 UI 与相关 API |
| Risk hypotheses | 最可能回归的用户可见失败（8 条以内） |
| Auth split | 哪些可未登录验、哪些必须登录 |
| Out of scope | 纯测试文件膨胀、lockfile、无 UI 的内部重构（可注明「已有 ui-offline 覆盖」） |

### 1B.3 提取用例

`{OUTPUT_DIR}/01-cases.md`：从 Themes + Risk 生成 **≤ Max cases** 条可执行用例。

每条必须是**用户可观察行为**，不是「打开 Chat.tsx 看看」：

- 坏：`验证 reconcileSlots`  
- 好：`三模型会话中换掉中间模型后，旧回答仍以历史标签留在该泳道；刷新后仍在`

标注：`source=commit:HASH` 或 `source=theme:泳道历史`；优先级；`logged-out|logged-in`。

写完 `00-brief.md`（Entry=`diff`、Repo、Window、URL、Auth）后进 **§2 Gate**。

---

## 2. Gate（人闸，短）

若 `01-cases.md` 中存在 `logged-in` 且 brief 无 Auth：先问人要登录态/账号，**不要假装测过**。  
若含付费/注册/删除：列出来等人授权。  
用户说「先测未登录部分」→ 只执行对应子集，其余进报告「未覆盖」。

Gate 通过后才能 Persona/Actor。

---

## 3. Persona

`{OUTPUT_DIR}/01-persona.md`（文件名保持；与 cases 并存）：

- 姓名、年龄、职业、技术水平  
- **唯一任务**：必须能覆盖本轮 **P0 用例**（可写成「完成清单上的关键验收」但路径仍受顾虑约束）  
- 放弃条件、顾虑（须改变先点哪）、说话方式  

Entry=`diff` 时 persona 可以是「回归验收的熟客用户」，仍要具体，禁止「QA 机器人」。

---

## 4. Actor（与入口无关）

打开浏览器。用例是清单，**不是**无脑巡游脚本：

- 用 persona 的顾虑决定**顺序**（例如怕扣费 → 先看定价相关 P0）。  
- 每条 case 至少一个 `STEP_*` 组；可拆多步。

每步强制顺序：

1. 写 **预期**（操作前）  
2. `STEP_START|<id>|<标题>`  
3. 操作  
4. 截图或 a11y 快照（失败交互尽量逐步截图）  
5. `STEP_DONE` / `ASSERTION_FAILED` / `STEP_SKIPPED`（无证据禁止 DONE）

`ASSERTION_FAILED` 字段：

`category=…; domain=…; expected=…; actual=…; url=…; evidence=…; repro=…; likely-scope=…; next-agent-prompt=…`

日志：`02-actor-log.md`（模板 `templates/actor-log-template.md`）。  
结束：`RUN_COMPLETED|passed|failed|incomplete|<一行摘要>`。

阻塞：登录墙 / OTP / 付费 → 停或 SKIPPED，写进未覆盖。

---

## 5. Judge → 标准化 report

输入：brief、cases、persona、actor-log、screens（+ videos）。  
**新上下文**；不要继续用 persona 口吻点站点（除非复现核实）。

报告 `03-report.md` 对齐 round2 dogfood 骨架：

1. 表头：Target、Entry、Scope/Window、Persona、Auth、Status、计数  
2. **Summary** 严重度表（Critical/High/Medium/Low 或 RED/YELLOW；本 skill 用 RED/YELLOW/WHITE/GREEN + 待确认）  
3. **Issues**：每条含严重度、分类、URL、期望/实际、复现步骤（可配截图路径）、`next-agent-prompt`  
4. **待确认**（只观察到一次）  
5. **未覆盖**（含未执行的 `01-cases` ID）  
6. **Cases 结果矩阵**：case-id → pass/fail/skip/not-run  

规则：

- 复现两次（或 Actor 已写两次）才进 RED/YELLOW  
- 零 `STEP_DONE`/`ASSERTION_FAILED` → Status=`incomplete`，禁止报 passed  
- 务实过滤：定位/口味类降 WHITE/YELLOW  

---

## 6. Wrap

向用户只交付：Summary 计数、工单列表、未覆盖 cases、是否需要登录/授权续跑。  
Diff 入口可附 3～5 行「本窗工作主题」——来自 digest，勿贴整段 git log。

---

## 角色隔离（强制）

| 角色 | 可看 | 不可看/不可做 |
|---|---|---|
| Diff 分析师（仅 Entry B 步骤 1） | git、digest | 不扮演用户、不写最终严重度 |
| Actor | persona、cases 标题与步骤、URL、安全红线 | 开发意图说教、严重度量表、历史工单口径 |
| Judge | 全部产物文件 | 用「我再感受一下」否定 Actor（除非复现） |

可用 Task 子代理拆开；否则严格分阶段并重读文件。

---

## 标记协议

```
STEP_START|<step-id>|<title>
STEP_DONE|<step-id>|<summary with evidence>
ASSERTION_FAILED|<step-id>|category=…; domain=…; expected=…; actual=…; url=…; evidence=…; repro=…; likely-scope=…; next-agent-prompt=…
STEP_SKIPPED|<step-id>|<reason>
RUN_COMPLETED|passed|failed|incomplete|<session-summary>
```

## 反合理化

- 页面打开了 ≠ 验过  
- 差不多能用 ≠ `STEP_DONE`  
- Actor 阶段假装不知道「在找 bug」  
- Diff 入口禁止只交 digest 就当测试完成——必须跑 Actor/Judge，或明示 `incomplete` 仅交付用例待跑  
- 没有 STEP 结果 ≠ passed  
- 巨型 lock/字体 diff ≠ 产品回归点  

## 产出清单

```
{OUTPUT_DIR}/
  00-brief.md
  00-diff-digest.md   # 仅 Entry=diff
  01-cases.md
  01-persona.md
  02-actor-log.md
  03-report.md
  screens/
  videos/             # 可选
```
