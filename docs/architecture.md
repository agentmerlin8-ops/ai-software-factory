# Architecture: 8-Agent Software Factory Pipeline

## Overview

The factory uses 8 specialized agents running in sequence within GitHub Copilot's agent mode. Each agent has a focused role, produces markdown artifacts, and operates within well-defined context boundaries.

## Pipeline Flow

```
Context Bundle (PRD + UI/UX + Architecture + Test Strategy)
    ↓
[1. Story Decomposer] → stories/STORY-001.md, STORY-002.md, ...
    ↓
For each story:
    ↓
[2. Test Plan Generator] → stories/STORY-001/test-plan.md
    ↓
[3. Implementation Planner] → stories/STORY-001/impl-plan.md
    ↓
[4. Plan Reviewer] ← FRESH CONTEXT (no anchoring bias)
    ↓
    ├─ APPROVED → [5. Coder] → code files
    │                 ↓
    │             [6. Code Reviewer]
    │                 ↓
    │                 ├─ APPROVED → [7. Test Executor] → test-results.md
    │                 └─ CHANGES REQUESTED → loop back to Coder (max 2)
    │
    └─ REVISIONS → loop back to planners (max 2)
```

## Agent Roles

| # | Agent | Input | Output | Key Constraint |
|---|---|---|---|---|
| 1 | **Story Decomposer** | Context bundle (PRD + UI/UX + Arch + Test) | Individual story files with acceptance criteria | Vertical slices, dependency ordering |
| 2 | **Test Plan Generator** | Single story + test strategy | Test cases (happy path, edge, error, negative) | Tests written BEFORE code exists |
| 3 | **Implementation Planner** | Story + test plan + architecture | Step-by-step TDD plan with exact code | Complete code, exact commands |
| 4 | **Plan Reviewer** | Test plan + impl plan (fresh context!) | APPROVED or REVISIONS with feedback | Context isolation enforced |
| 5 | **Coder** | Approved impl plan + existing code | Code files following TDD | No scope creep, follow plan mechanically |
| 6 | **Code Reviewer** | Code + impl plan + test plan | APPROVED or CHANGES REQUESTED | SOLID, architecture compliance |
| 7 | **Test Executor** | Code + test plan + Docker Compose | Build/test results + proof artifacts | Honest reporting, no silent fixes |

**Orchestrator** drives the pipeline, tracks state in `stories/{id}/state.md`, handles revision loops, escalates after 2 failures.

## Context Isolation Principle

**Critical for reviewers:** Plan Reviewer and Code Reviewer run in fresh context that does NOT see planning agents' internal reasoning or conversation history. A reviewer who read the planner's reasoning is primed to accept the plan's conclusions. A fresh reviewer who sees only the output artifacts catches gaps the planner rationalized away.

Each agent receives ONLY the markdown artifacts from previous agents. Never pass conversation history or internal reasoning.

## Revision Loops

- **Plan Review Loop:** Plan Reviewer returns REVISIONS → Planner regenerates → Reviewer re-reviews. Max 2 loops.
- **Code Review Loop:** Code Reviewer returns CHANGES REQUESTED → Coder re-implements → Reviewer re-reviews. Max 2 loops.
- **Escalation:** After 2 failed loops, STOP and report which agent failed, what the failure was, and recommend manual intervention.

## State Tracking

Each story maintains `stories/{id}/state.md`:

```markdown
## Story: STORY-001
- [ ] Story decomposed
- [ ] Test plan generated
- [ ] Implementation plan generated
- [ ] Plan review: APPROVED / REVISIONS (count: 0)
- [ ] Code implemented
- [ ] Code review: APPROVED / CHANGES REQUESTED (count: 0)
- [ ] Tests executed: PASS / FAIL
```

For ADO-based environments, the same state is mirrored in the AI Story work item's custom fields and state machine.

## Context Bundle Documents

Four input documents required:

1. **PRD** — Product requirements, functional/non-functional requirements, acceptance criteria in Given/When/Then format, scope boundaries
2. **UI/UX Design** — User flows, component hierarchy, states, ASCII wireframes, API contract (TypeScript interfaces)
3. **Architecture** — Clean Architecture layers, data model, API design, DI config, Docker Compose
4. **Test Strategy** — Test pyramid, categories, test data management, anti-patterns

See `docs/context-bundle.md` for full templates.

## Key Design Principles

1. **Markdown-as-contract** — All artifacts between agents are markdown files in the repo. Version-controllable, auditable, comparable across model runs.
2. **Max 2 revision loops** — Prevents infinite token burn. Escalate to human.
3. **Phase-based batching** — Batch stories by phase (infrastructure, API, frontend) rather than running one agent per story.
4. **Spec-first, always** — Tests written before code exists. TDD in the large.
5. **Honest failure reporting** — Test Executor reports failures honestly, does not silently fix code.