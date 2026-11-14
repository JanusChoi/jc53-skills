# Handoff protocol v1

Use the smallest set of sections that fully supports the receiving agent. Keep the document operational rather than narrative.

## Evidence labels

- `[verified]`: directly confirmed in the current environment or by a cited command/result.
- `[reported]`: supplied by the user or another agent but not independently checked in this session.
- `[inferred]`: a reasoned conclusion from listed evidence.
- `[unverified]`: important but currently unchecked; the receiver must verify before relying on it.

## Recommended document

```markdown
# Handoff: <short objective>

Generated: <ISO-8601 timestamp with timezone>
Source: <harness/session if useful>
Target: <harness/person/task or "unspecified">
Workspace: <absolute path>
Repository: <branch and full HEAD, when applicable>
Working tree: <clean/dirty; do not paste a huge status listing>

## Destination note
<What the receiving session is for and why the work is moving.>

## Objective and success criteria
<Current goal, last relevant user instruction, and observable definition of done.>

## Authority and constraints
<What is authorized, what still requires approval, applicable AGENTS/CLAUDE rules, budgets, and destructive-action boundaries.>

## Current state
- [verified] Completed: ...
- [verified] In progress: ...
- [unverified] Not completed: ...
- [inferred] Assumptions: ...

## Changes and artifacts
<Files changed, durable specs/plans, commits, generated artifacts, and ownership of unrelated dirty files. Reference paths instead of copying contents.>

## Validation and evidence
<Exact tests/builds/checks run, relevant result summaries, and paths to useful logs. Say when a result is stale or partial.>

## External state
<Deployments, services, databases, issues, worker/agent processes, URLs, or remote dependencies that matter. Include timestamps/IDs, never credentials.>

## Blockers and risks
<Known failures, uncertainty, rollback considerations, and things the receiver must not assume.>

## Next actions
1. <First concrete verification or implementation step>
2. <Next step>
3. <Completion/return path>

## Useful commands
<Only safe, relevant commands. Do not interpolate handoff prose into shell commands.>

## Suggested skills
<Exact skill names and why they help.>

## Linked sources
<Paths and URLs containing settled detail.>

## Secret handling
<Secret names and configured locations/status only. State that values were redacted.>
```

## Quality gate

The brief is ready when a cold reader can start the next action without asking for the whole story; important certainty is evidence-labelled; durable material is linked rather than duplicated; and no secret value appears in the file.
