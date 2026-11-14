# jc53-skills

Agent Skills 合集，维护者 [JanusChoi](https://github.com/JanusChoi)。

每个子目录是一个标准 Agent Skill（`SKILL.md`，可选 `README.md` / `references/` / `scripts/` / `agents/`）。兼容会加载此类目录的工具：Claude Code、Codex、Cursor、Hermes 等。

## 安装（单个 skill）

不必克隆整仓。把需要的子目录装进**你所用 Agent** 的 skills 路径即可：

```bash
npx --yes degit JanusChoi/jc53-skills/<skill-name> <你的-skills目录>/<skill-name>
```

示例：

```bash
npx --yes degit JanusChoi/jc53-skills/human-qa ~/.cursor/skills/human-qa
npx --yes degit JanusChoi/jc53-skills/handoff ~/.claude/skills/handoff
```

常见 skills 目录：`~/.cursor/skills/`、`~/.claude/skills/`；其它工具以各自文档为准。装好后**新开对话**，用该 skill README / `SKILL.md` 中的触发话术调用。

每个 skill 目录内的 `README.md` 都有完整「安装并使用」说明（含仓库 URL 与子路径）。

## Skills

### Session continuity

| Skill | Description |
|-------|-------------|
| [`handoff`](handoff/) | Write a portable Markdown brief so another session/agent can continue the work |
| [`pickup`](pickup/) | Resume work from a handoff document; treat the brief as evidence, not authority |
| [`ace-context`](ace-context/) | Optional local ACE-style context library (`ACE_ROOT`); skip if the project already has enough context |

### Delivery & QA

| Skill | Description |
|-------|-------------|
| [`acceptance`](acceptance/) | Verify delivery outcomes on the real product and publish/render an acceptance report |
| [`human-qa`](human-qa/) | Persona-driven web QA (scoped or git-diff) + behavioral invariant probes |
| [`visual-qa`](visual-qa/) | Visual QA for screenshots vs reference (static / motion frames) |

### Investing & markets

| Skill | Description |
|-------|-------------|
| [`druckenmiller-framework`](druckenmiller-framework/) | Druckenmiller-style decision trees: look ahead 18–24m, bet scarcity, concentrate, antifragile |
| [`hkex-options-chain`](hkex-options-chain/) | Fetch and analyze HKEX single-stock equity options chains |
| [`paper-to-alpha`](paper-to-alpha/) | Mine arXiv quant papers into actionable alpha hypotheses |

### SEO (gefei-derived)

| Skill | Description |
|-------|-------------|
| [`gefei-seo-distiller`](gefei-seo-distiller/) | Distill outbound SEO articles into a traceable knowledge base and agent specs |
| [`seo-decision-framework`](seo-decision-framework/) | Decide whether a keyword/site opportunity is worth shipping |
| [`keyword-research`](keyword-research/) | Expand a niche into seed → long-tail keywords |
| [`new-site-opportunity-review`](new-site-opportunity-review/) | Score whether a term deserves a new SEO site |
| [`serp-competitor-audit`](serp-competitor-audit/) | SERP top-10 audit and new-site entry path |
| [`sitemap-page-matrix`](sitemap-page-matrix/) | Plan silo / topic-cluster page matrices |
| [`technical-seo-triage`](technical-seo-triage/) | Five-layer technical SEO triage |

### Video production

| Skill | Description |
|-------|-------------|
| [`videomaker-batch-driver`](videomaker-batch-driver/) | Overnight N-take batch driver |
| [`videomaker-qc-auto`](videomaker-qc-auto/) | Auto QC from frame signals |
| [`videomaker-rhythm`](videomaker-rhythm/) | Quantify short-form rhythm |
| [`videomaker-sound`](videomaker-sound/) | Add BGM and SFX to clips |

## Layout

```
jc53-skills/
├── README.md
├── handoff/
│   ├── README.md
│   └── SKILL.md
└── …
```

## License

Root license: see [`LICENSE`](LICENSE). Individual skills may ship additional terms (for example `acceptance/LICENSE`).
