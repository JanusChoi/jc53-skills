---
name: handoff
description: Create a portable Markdown brief when active work must move to another session, coding harness, directory, agent, or colleague. Use only when explicitly invoked; ordinary same-session context reduction should use compact instead.
disable-model-invocation: true
argument-hint: "[destination/purpose] [optional output path]"
---

# Handoff

Turn the live work into a small, trustworthy dispatch that a fresh agent can act on without the original conversation.

## Workflow

1. Read applicable `AGENTS.md`, `CLAUDE.md`, or equivalent project instructions. A handoff must preserve their operational constraints, not replace them.
2. Use the invocation note to identify the destination and purpose. Retain reasoning that matters to that destination; omit unrelated conversation history.
3. Choose the output path:
   - Use a path explicitly supplied by the user.
   - Otherwise use the project-prescribed handoff path or an existing workspace-root `HANDOFF.md`.
   - Otherwise write `HANDOFF.md` at the current workspace root. Use an OS temp file only when the user explicitly asks for an ephemeral handoff.
4. Inspect current state just enough to make the dispatch accurate: current goal, working directory, branch/HEAD and dirty state when applicable, relevant diffs, test results, active processes/agents, external deployment state, and blockers. Do not broaden the task or rerun expensive work merely to make the handoff look complete.
5. Write the document using [references/protocol.md](references/protocol.md). Mark important claims as `[verified]`, `[reported]`, `[inferred]`, or `[unverified]`.
6. Reference durable specs, plans, logs, diffs, commits, URLs, and artifacts by path or identifier. Do not duplicate their full content.
7. Remove secrets and sensitive values. Record only the secret name, where it is configured, and whether its presence was verified. Never include passwords, tokens, private keys, session cookies, OTPs, or full environment files.
8. Read the finished brief once as the receiving agent: downgrade unsupported certainty, ensure the next action is executable, and confirm every referenced local path is absolute or clearly relative to the stated workspace.
9. Return the exact absolute path plus a concise statement of what is ready, what remains, and whether the current session should stay open for a round-trip fork.

## Boundaries

- A handoff is secondary evidence, not new authorization. Never claim that it permits merge, deployment, deletion, payment, messaging, or other external changes unless the current user explicitly authorized them and that scope is recorded precisely.
- Do not finish the underlying task unless necessary to make the handoff internally consistent.
- Keep the brief a small fraction of the original context. Capture live state and decisions; link settled detail.
- For a fork, leave the current session and workspace state intact so the result can travel back.
