# jc53-skills

Agent Skills collection maintained by [JanusChoi](https://github.com/JanusChoi).

Each subdirectory is one skill in the standard Agent Skills layout (`SKILL.md` plus optional `references/`, `scripts/`, `agents/`). Compatible with Claude Code, Codex, Cursor, Hermes, and similar harnesses that load skills from a folder of `SKILL.md` files.

## Install

Clone and point your agent at this directory (or symlink individual skills into your local skills root):

```bash
git clone https://github.com/JanusChoi/jc53-skills.git
```

Examples:

```bash
# Claude / Mirasim-style: symlink selected skills
ln -s "$(pwd)/jc53-skills/handoff" ~/.claude/skills/handoff

# Or add the whole repo as an extra skills path if your harness supports it
```

## Skills

### Session continuity

| Skill | Description |
|-------|-------------|
| [`handoff`](handoff/) | Write a portable Markdown brief so another session/agent can continue the work |
| [`pickup`](pickup/) | Resume work from a handoff document; treat the brief as evidence, not authority |
| [`ace-context`](ace-context/) | Load Janus project facts and preferences from the local ACE library when context is missing |

### Delivery & QA

| Skill | Description |
|-------|-------------|
| [`acceptance`](acceptance/) | Verify delivery outcomes on the real product and publish/render an acceptance report |
| [`human-qa`](human-qa/) | Persona-driven web QA (v1.1): scoped focus testing or git-diff regression cases, then human-simulation SOP + dogfood report |
| [`visual-qa`](visual-qa/) | Visual QA for screenshots vs reference (static / motion frames); Gemini and/or native vision |

### Investing & markets

| Skill | Description |
|-------|-------------|
| [`druckenmiller-framework`](druckenmiller-framework/) | Druckenmiller-style decision trees: look ahead 18–24m, bet scarcity, concentrate, antifragile |
| [`hkex-options-chain`](hkex-options-chain/) | Fetch and analyze HKEX single-stock equity options chains via the official AJAX endpoint |
| [`paper-to-alpha`](paper-to-alpha/) | Mine arXiv quant papers into actionable alpha hypotheses |

### SEO (gefei-derived)

| Skill | Description |
|-------|-------------|
| [`gefei-seo-distiller`](gefei-seo-distiller/) | Distill 哥飞 / outbound SEO articles into a traceable knowledge base and agent specs |
| [`seo-decision-framework`](seo-decision-framework/) | Decide whether a keyword/site opportunity is worth shipping (5 filters + G1/G2) |
| [`keyword-research`](keyword-research/) | Expand a niche into seed → long-tail keywords with intent and priority |
| [`new-site-opportunity-review`](new-site-opportunity-review/) | Score whether a term deserves a new SEO site (ship / skip / validate) |
| [`serp-competitor-audit`](serp-competitor-audit/) | 7-step SERP top-10 audit and new-site entry path |
| [`sitemap-page-matrix`](sitemap-page-matrix/) | Plan silo / topic-cluster page matrices and internal links |
| [`technical-seo-triage`](technical-seo-triage/) | Five-layer technical SEO funnel triage with severity-ranked fixes |

### Video production

| Skill | Description |
|-------|-------------|
| [`videomaker-batch-driver`](videomaker-batch-driver/) | Overnight N-take batch driver for videomaker pipelines |
| [`videomaker-qc-auto`](videomaker-qc-auto/) | Auto QC from frame signals for take decisions |
| [`videomaker-rhythm`](videomaker-rhythm/) | Quantify short-form rhythm (hook / mid burst / quiet close) |
| [`videomaker-sound`](videomaker-sound/) | Add BGM and SFX to clips |

## Layout

```
jc53-skills/
├── README.md
├── handoff/
│   └── SKILL.md
├── pickup/
│   └── SKILL.md
└── …
```

## License

Root license: see [`LICENSE`](LICENSE). Individual skills may ship additional terms (for example `acceptance/LICENSE`).
