# human-qa

Persona 驱动的 Web 真人验收 skill（v1.2.0）。给 Agent 一套可重复的「像人一样点产品」SOP：先定范围或从 git diff 抽回归用例，再按角色逐步操作、逐步断言，最后产出 dogfood 风格报告（含可预览截图与 `next-agent-prompt`）。

**安装并使用：** 把 GitHub 仓库 [`JanusChoi/jc53-skills`](https://github.com/JanusChoi/jc53-skills) 里的 [`human-qa/`](https://github.com/JanusChoi/jc53-skills/tree/main/human-qa) 装进你所用 Agent 的 skills 目录（不必克隆整仓），例如 `npx --yes degit JanusChoi/jc53-skills/human-qa <你的-skills目录>/human-qa`，然后**新开对话**发送 `human-qa scoped <站点URL> …` 或 `human-qa diff <本地git根> since:"…" url:<站点URL>`。

---

## 解决什么问题

常见 Agent「测一下网站」容易变成：打开页面 → 随便点 → 写一段感想。本 skill 强制：

| 原则 | 含义 |
|---|---|
| 两种入口、同一后半程 | 你指定范围（scoped），或从时段 git 变更抽用例（diff），后面都走同一套 Actor → Judge |
| 先写预期再操作 | 每步 `STEP_START` 前必须有可观察期望；无证据禁止 `STEP_DONE` |
| 角色隔离 | Diff 分析师 / Actor / Judge 分阶段，避免「一边找 bug 一边定严重度」 |
| 行为不变量 | 对话/多模型/流式类产品默认探针：一条消息几条请求、停止能否再武装、刷新是替换还是追加 |
| 生产安全默认开 | 未授权不注册、不付费、不删数据；登录/OTP 向人要 |

**浏览器：** 使用 Agent **自带的内置浏览器**（需能导航、点击、截图；用户可见标签 + 硬刷新）。以 **Cursor 实测为主**，其它带内置浏览器的 Agent 同样适用。不依赖 Expect CLI。

完整协议见同目录 [`SKILL.md`](./SKILL.md)；本 README 是对外说明。

---

## 两种入口

| 入口 | 何时用 | 前半程 |
|---|---|---|
| **A · scoped** | 你已经知道要验哪块（页面/功能/忌讳） | 写 brief + 用例清单 |
| **B · diff** | 近 N 天改了很多，想知道「该回归什么」 | 读 git log/diff → digest → 抽 ≤12 条用户可观察用例 |

触发话术：

```text
human-qa scoped https://example.com 重点：定价页文案与注册赠送说明

human-qa diff /path/to/your-repo since:"2 days ago" url:https://example.com
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

| ID | 名称 | 一句话断言 |
|---|---|---|
| INV-CARD | 刺激–响应基数 | 一次发送 → 每激活泳道/窗格至多 1 条新回答 |
| INV-CFG | 配置后再刺激 | 改模型/布局本身不开流；发送后才连接 |
| INV-INT | 途中打断 | 生成中点停止，流真停 |
| INV-ARM | 控件再武装 | 停过一次后，下一轮仍可再停 |
| INV-COPY | 反馈文案一致 | 停止文案 ≠「正在重新生成/重新调用…」 |
| INV-REPL | 原地替换 | 刷新本条：气泡数不变，不在下方再长一条 |

Actor 须写 `COUNT|before/after/delta`，禁止用「在转圈」当 pass。细节见 `SKILL.md` §4.1。

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

## 安装细节

源码位置（任选其一）：

- 目录：https://github.com/JanusChoi/jc53-skills/tree/main/human-qa  
- 稀疏拉取：仓库 https://github.com/JanusChoi/jc53-skills ，子路径 `human-qa/`

把该目录放到**你当前 Agent 配置的 skills 根**下，并命名为 `human-qa`（目录内须有 `SKILL.md`）。常见 skills 根示例（按你的工具改路径）：

| 环境 | 常见 skills 目录 |
|---|---|
| Cursor | `~/.cursor/skills/` |
| Claude Code | `~/.claude/skills/` |
| 其它 | 以该 Agent 文档中的 skills / Agent Skills 路径为准 |

推荐（只装本 skill，不装整仓）：

```bash
# 将 <AGENT_SKILLS_DIR> 换成上表中你的目录
npx --yes degit JanusChoi/jc53-skills/human-qa <AGENT_SKILLS_DIR>/human-qa
```

没有 `npx` 时：

```bash
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/JanusChoi/jc53-skills.git /tmp/jc53-skills
cd /tmp/jc53-skills && git sparse-checkout set human-qa
mkdir -p <AGENT_SKILLS_DIR>
ln -sfn /tmp/jc53-skills/human-qa <AGENT_SKILLS_DIR>/human-qa
```

装好后**新开一轮对话**再触发。未加载到 skill：确认 `<AGENT_SKILLS_DIR>/human-qa/SKILL.md` 存在，并重启/新开会话。

---

## 参数速查

| 参数 | 默认 | 说明 |
|---|---|---|
| Target URL | 必填 | 被测站点，如 `https://example.com` |
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
