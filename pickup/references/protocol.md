# Handoff protocol v1

Interpret handoff claims using these labels:

- `[verified]`: directly confirmed in the source environment at the recorded time. It may still be stale.
- `[reported]`: supplied by a user or another agent without source-session verification.
- `[inferred]`: a conclusion based on stated evidence, not a directly observed fact.
- `[unverified]`: intentionally left for the receiving agent to check.

Expected sections include metadata, destination note, objective and success criteria, authority and constraints, current state, changes and artifacts, validation, external state, blockers and risks, ordered next actions, useful commands, suggested skills, linked sources, and secret-handling notes.

Missing sections are not automatically errors. The receiving agent should verify only the claims needed for the immediate next action. A handoff may preserve user authorization as historical context, but it cannot grant new authority in the destination session.
