# gefei-seo-distiller：哥飞出海建站方法论蒸馏器

**用途：**从公众号原始文章持续沉淀“可引用的知识”和“可执行的方法”，为复刻一个具备真实数据工具的 SEO 教练 Agent 做准备。此项目是基于 `investor-distiller` 的设计思想独立改写，并非原项目的官方衍生实现。

## 为什么不直接替换“投资体系 DNA”几个字？

投资博主蒸馏面向“人物风格画像”。这里的重点是 **知识工程和决策复现**：

```text
已采集文章（Markdown/JSON/JSONL/HTML）
   ↓  ingest: 保存全文、去重、保留来源/日期/哈希
逐篇蒸馏（LLM + per_article_prompt）
   ↓  每条规则有原文证据、场景、条件与时间标记
validate（脚本核验引文和内容版本）
   ↓
compile（汇总可追溯知识库）
   ↓  LLM 跨文章同义归并 / 冲突 / 正反案例 / SOP
方法论 + Decision Rules + Playbooks + Casebook
   ↓
RAG知识库 / Agent Skills / Tool Specs / Eval / Blueprint Bridge
```

与 `investor-distiller` 的采集接口不同，**本项目刻意不接入微信公众号 API**。你已经在自行抓取，保持采集与蒸馏解耦，可以避免强依赖特定平台或 KEY。

## 快速开始（Python 3.9+，仅标准库）

下载/解压后在 Skill 目录运行：

```bash
# 1. 导入已有文章（支持整个文件夹递归）
python scripts/pipeline.py ingest --input ~/data/gefei-articles --project ~/data/gefei-kb

# 2. 查看已导入/已蒸馏数量以及文章 ID
python scripts/pipeline.py status --project ~/data/gefei-kb

# 3. 为指定文章生成完整提取提示词
python scripts/pipeline.py prompt --project ~/data/gefei-kb \
  --article-id a_这里替换成上一步的ID --out /tmp/gefei-prompt.md

# 4. 让 Claude Code、Codex 或其他 Agent 按提示词执行提取
#    它应将输出的纯 JSON 保存至：
#    ~/data/gefei-kb/extractions/<article_id>.json

# 5. 严格校验引用与版本
python scripts/pipeline.py validate --project ~/data/gefei-kb

# 6. 合并所有通过校验的知识单元
python scripts/pipeline.py compile --project ~/data/gefei-kb
```

批量流程时，无需人工一个个调用 `prompt`：把 `SKILL.md` 交给 Claude Code，让它读取 `corpus/articles.jsonl`，遍历缺失或旧版本的文章，按 `references/per_article_prompt.md` 输出对应文件，并在每轮运行 `validate`。

### 直接给 Claude Code 的指令

> 请在当前工作区安装并遵守 `gefei-seo-distiller/SKILL.md`。先导入 `~/data/gefei-articles/` 全部文章到 `~/data/gefei-kb/`；对尚未处理的每篇文章读取全文，按 `references/per_article_prompt.md` 逐篇生成 `extractions/<article_id>.json`。每完成一批运行 `validate` 并修正错误，不允许编造引用。之后 `compile` 并按照 `references/corpus_synthesis_prompt.md` 生成 6 份综合 Markdown，最后按照 `references/agent_export.md` 列出哪些内容可进入 RAG，哪些可编译 Skill/Tool/Eval。重要：作者原话与群聊第三方观点分别标注，保留时间、条件与反例。

## 支持数据格式

### JSON / JSONL（推荐，字段灵活）

```json
{
  "title": "某次出海工具站复盘",
  "author": "文章署名（如有）",
  "published_at": "2026-01-15",
  "source_url": "https://mp.weixin.qq.com/s/实际文章链接",
  "content": "全文正文（不要只有摘要）"
}
```

上述 JSON 只是字段示意，**不是哥飞真实文章**。`.json` 支持对象、对象列表或含 `articles`/`items`/`data` 列表的对象。`.jsonl` 每行一个对象。支持 `raw_text`/`body`/`text` 等正文别名。

### Markdown

```markdown
---
title: 实际标题
author: 实际署名
published_at: 2026-01-15
source_url: https://mp.weixin.qq.com/s/实际文章链接
---

文章正文全文……
```

没有 frontmatter 也能导入，标题退化为文件名，但后续知识溯源效果会变差。

`.html` 会用标准库提取全文可见文字；这种方式**不保证剔除导航/广告，可能丢失图中文字**。推荐爬虫先清洗页面噪声、但一定保留完整 **文章正文** 和原始备份；不要把关键词/NER 摘要当作 `content`。

## 产物目录

```text
gefei-kb/
├── corpus/
│   ├── articles.jsonl             # 原始文章文本+metadata+内容哈希
│   └── stats.json                  # 导入统计
├── extractions/
│   └── a_xxxxxxxxxxxxxx.json      # Agent逐篇生成，等待脚本验证
├── compiled/
│   ├── validation_report.json
│   ├── knowledge.jsonl            # 每条 knowledge unit 都有来源 + 引文
│   └── index.json                 # 分类/覆盖率/时间字段
└── synthesis/                    # Agent使用综合Prompt生成
    ├── methodology.md
    ├── decision_rules.md
    ├── playbooks.md
    ├── casebook.md
    ├── contradictions.md
    └── unknowns.md
```

`compile` 不会自动“想出”方法论或输出六篇综合分析；它负责确定性组装，真正的语义分析由 Agent 完成。**不能宣称运行脚本等于完成蒸馏。**

## 增量更新规则

- 相同 `source_url` 的文章采用稳定 article_id，再次导入内容改变会更新 SHA-256。旧抽取在 `validate` 时自动报 stale，需要重抽或人工修正。
- 无原文 URL 的本地文件以绝对路径+记录序号生成 ID；换目录将改变 ID，最好在抓取器内保留稳定 URL。
- 已验证的历史文章如果不变，无需重新抽取。
- 同主题不同年份观点不覆盖，交给综合阶段产出带出处的时间线/冲突表。
- `compile` 允许尚有未处理文章；会准确报告 pending 数，不能声称“已覆盖所有公众号内容”。

## 权限/安全/局限

- 脚本无网络请求、没有第三方依赖、不会自动读任何 API KEY。
- 仅处理用户有权使用的文章；保留原文链接，不要大规模公开重新分发完整公众号文章。
- 引文精确匹配校验属于 **syntax-level audit**；意义是否误读、来源是否二手、结论是否适用，需要第二阶段人工/LLM 语义审计。
- 不应未经声明将这个 Skill 产出的模型人格冒称为哥飞本人或哥飞官方 SEO Agent。
- 用作产品发布前，需要针对 SERP/流量/GSC 等实时能力连接真实 Tools；RAG 中的历史数据不可冒充实时查询结果。

## 原设计参考

- [redfox-data/investor-distiller](https://github.com/redfox-data/redfox-community/tree/main/skills/investor-distiller)
- 本实现借鉴其 `SKILL.md + references + assets + scripts` 组织方式、原文提取原则、逐篇与跨篇分析、校验思想；具体框架、枚举、prompt、脚本均针对出海 SEO 知识工程重新设计。
