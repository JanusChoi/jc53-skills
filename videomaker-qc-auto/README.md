# videomaker-qc-auto

对 take 抽帧信号并辅助 accept/retry/reject 决策。

**安装并使用：** 把 GitHub 仓库 [`JanusChoi/jc53-skills`](https://github.com/JanusChoi/jc53-skills) 里的 [`videomaker-qc-auto/`](https://github.com/JanusChoi/jc53-skills/tree/main/videomaker-qc-auto) 装进你所用 Agent 的 skills 目录（不必克隆整仓），例如：

```bash
npx --yes degit JanusChoi/jc53-skills/videomaker-qc-auto <你的-skills目录>/videomaker-qc-auto
```

然后**新开对话**，用下方触发话术调用。适用于任何会加载 Agent Skills（目录内含 `SKILL.md`）的工具（Cursor、Claude Code、Codex、Hermes 等）。

<details>
<summary>无 npx 时 / 路径示例</summary>

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/JanusChoi/jc53-skills.git /tmp/jc53-skills
cd /tmp/jc53-skills && git sparse-checkout set videomaker-qc-auto
mkdir -p <你的-skills目录>
ln -sfn /tmp/jc53-skills/videomaker-qc-auto <你的-skills目录>/videomaker-qc-auto
```

常见 skills 目录：`~/.cursor/skills/`、`~/.claude/skills/`，其它工具以各自文档为准。
</details>

## 触发话术

```text
videomaker-qc-auto / 跑 qc.py 检查 takes/<seg>/take1/
```

权威执行协议见同目录 [`SKILL.md`](./SKILL.md)（及可选的 `references/`、`scripts/`）。

## 许可

随仓库根目录 [`LICENSE`](../LICENSE)。部分 skill 另有子目录 LICENSE（若存在以该文件为准）。
