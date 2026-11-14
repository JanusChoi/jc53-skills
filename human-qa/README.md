# human-qa

Persona 驱动的 Web 真人验收 skill（v1.2.0）。给 Agent 一套可重复的「像人一样点产品」SOP：先定范围或从 git diff 抽回归用例，再按角色逐步操作、逐步断言，最后产出 dogfood 风格报告（含可预览截图与 `next-agent-prompt`）。

**想让自己的 Agent 也用上：** 把本目录（或整个 [`jc53-skills`](https://github.com/JanusChoi/jc53-skills)）装进该 Agent 的 skills 路径，然后在对话里直接说 `human-qa scoped …` 或 `human-qa diff …`（安装见下方「安装与启用」）。

---

## 解决什么问题

常见 Agent「测一下网站」容易变成：打开页面 → 随便点 → 写一段感想。本 skill 强制：

| 原则 | 含义 |
|---|---|
| 两种入口、同一后半程 | 你指定范围（scoped），或从时段 git 变更抽用例（diff），后面都走同一套 Actor → Judge |
| 先写预期再操作 | 每步 `STEP_START` 前必须有可观察期望；无证据禁止 `STEP_DONE` |
| 角色隔离 | Diff 分析师 / Actor / Judge 分阶段，避免「一边找 bug 一边定严重度」 |
| 行为不变量 | 对话/多模型/流式产品默认探针：一条消息几条请求、停止能否再武装、刷新是替换还是追加 |
| 生产安全默认开 | 未授权不注册、不付费、不删数据；登录/OTP 向人要 |

默认用 **Cursor 内置浏览器**（可见标签 + 硬刷新）。不要求 Expect CLI，也不要和 Expect 混跑。

完整协议见同目录 [`SKILL.md`](./SKILL.md)；本 README 是对外说明。

---

## 两种入口

| 入口 | 何时用 | 前半程 |
|---|---|---|
| **A · scoped** | 你已经知道要验哪块（页面/功能/忌讳） | 写 brief + 用例清单 |
| **B · diff** | 近 N 天改了很多，想知道「该回归什么」 | 读 git log/diff → digest → 抽 ≤12 条用户可观察用例 |

触发话术：

```text
human-qa scoped https://tiwen.com 重点：定价页划线价和注册赠送文案

human-qa diff ~/code/tiwen-xphp since:"2 days ago" url:https://tiwen.com
```

---

## 流程概览

```
0. Init          建产出目录、拷模板
1. Intake        scoped → brief+cases ｜ diff → digest+cases
2. Gate          登录/付费/破坏性？先问人
3. Persona       一个具体角色（不是「QA 机器人」）
4. Actor         预期 → STEP → 截图/快照 → DONE/FAILED
5. Judge         标准化 03-report.md（复现两次才升 RED/YELLOW）
6. Wrap          只交 Summary、工单、未覆盖、是否要续跑
```

### 行为不变量探针（对话类产品 P0）

真人录屏里有效的手法，已落成可复用探针（详见 `SKILL.md` §4.1）：

| ID | 名称 | 一句话断言 |
|---|---|---|
| INV-CARD | 刺激–响应基数 | 一次发送 → 每激活泳道至多 1 条新回答 |
| INV-CFG | 配置后再刺激 | 换模型本身不开流；发送后才连接 |
| INV-INT | 途中打断 | 生成中点停止，流真停 |
| INV-ARM | 控件再武装 | 停过一次后，下一轮仍可再停 |
| INV-COPY | 反馈文案一致 | 停止 ≠「正在重新调用…」 |
| INV-REPL | 原地替换 | 刷新本条：气泡数不变，不在下方再长一条 |

Actor 须写 `COUNT|before/after/delta`，禁止用「在转圈」当 pass。

---

## 产出

默认写到 `./human-qa-output/`（可改）：

```text
00-brief.md
00-diff-digest.md   # 仅 Entry=diff
01-cases.md
01-persona.md
02-actor-log.md
03-report.md        # 含 Markdown 嵌入截图
screens/
videos/             # 可选
```

`templates/` 内有 brief / cases / digest / actor-log / report 模板。

---

## 安装与启用

兼容会加载 Agent Skills 目录（含 `SKILL.md`）的环境：Cursor、Claude Code、Codex、Hermes 等。

```bash
git clone https://github.com/JanusChoi/jc53-skills.git
```

任选其一：

```bash
# 只装本 skill（示例：Cursor 用户技能目录）
ln -s "$(pwd)/jc53-skills/human-qa" ~/.cursor/skills/human-qa

# Claude Code / 同类
ln -s "$(pwd)/jc53-skills/human-qa" ~/.claude/skills/human-qa

# 或把整个 jc53-skills 加进 Agent 的额外 skills 搜索路径（视你的 harness 配置）
```

装好后新开一轮对话，直接发上面的 `human-qa scoped …` / `human-qa diff …` 即可；Agent 应读取本目录的 `SKILL.md` 并按 SOP 执行。

若 skill 未自动出现：确认软链目标存在、文件名是 `SKILL.md`，并重启/新开 Agent 会话。

---

## 参数速查

| 参数 | 默认 | 说明 |
|---|---|---|
| Target URL | 必填 | 如 `https://example.com` |
| Output dir | `./human-qa-output/` | 本轮产物根 |
| Entry | 必填 | `scoped` 或 `diff` |
| Repo / Since / Until | diff 时 | 本地 git 与时间窗 |
| Scope / Focus | scoped 时 | 边界与重点（原话可抄进 brief） |
| Auth | 无 | 登录说明；OTP 向人要 |
| Production safety | 开 | 破坏性操作需明确授权 |
| Max cases | 12 | diff 抽用例上限 |

---

## 目录结构

```text
human-qa/
├── README.md          # 本说明
├── SKILL.md           # Agent 执行协议（权威）
└── templates/
    ├── brief-template.md
    ├── cases-template.md
    ├── diff-digest-template.md
    ├── actor-log-template.md
    └── report-template.md
```

---

## 许可

随仓库根目录 [`LICENSE`](../LICENSE)。
