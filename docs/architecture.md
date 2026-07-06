# Architecture: 9-Agent Software Factory Pipeline

## Overview

The factory uses 8 specialized sub-agents orchestrated by the Orchestrator (9 total agents). Each agent has a focused role, produces artifacts stored in ADO work items, and operates within well-defined context boundaries.

## Why Multi-Agent, Despite the Benchmarks

Our own research ([research-synthesis.md](research-synthesis.md)) shows single-agent + tools systems dominating SWE-bench, with multi-agent systems underperforming. We use a multi-agent pipeline anyway — deliberately. The trade:

- **What we give up:** some raw task-completion performance
- **What we get:** auditable stage boundaries, per-stage cost/quality observability, human-legible checkpoints, bounded blast radius per agent, and swappable models per stage

The agent boundaries exist **for the humans**, not for the model. In a locked-down enterprise environment, the ability to show a stakeholder exactly which stage failed, what it cost, and what the reviewer said is worth more than a few benchmark points. We *do* adopt the benchmark literature's #1 finding — self-repair loops — see Revision Loops below.

## Pipeline Flow

```
Context Bundle (PRD + UI/UX + Architecture + Test Strategy)
    ↓
[1. Story Decomposer] → AI Story WITs (+ ContextBundleScore gate)
    ↓
For each story:
    ↓
[2. Test Plan Generator] → AI Story.TestPlan
    ↓
[3. Implementation Planner] → AI Story.ImplPlan
    ↓
[4. Plan Reviewer] ← FRESH CONTEXT (no anchoring bias)
    ↓
    ├─ APPROVED → [5. Coder] → code on story/{id} branch + PR
    │                 ↓
    │             [6. Code Reviewer] ← reviews the PR diff
    │                 ↓
    │                 ├─ APPROVED → [7. Test Executor] → AI Story.TestResults
    │                 │                 ↓
    │                 │                 ├─ PASS → Story Approved
    │                 │                 └─ FAIL → self-repair loop to Coder (max 2)
    │                 └─ CHANGES REQUESTED → loop back to Coder (max 2)
    │
    └─ REVISIONS → loop back to planners (max 2)

When ALL stories Approved:
    ↓
[8. Feature Verifier] → end-to-end validation against PRD acceptance criteria
    ↓
Human merges story PRs → Feature Done
```

## Agent Roles

| # | Agent | Input (from ADO) | Output (to ADO) | Key Constraint |
|---|---|---|---|---|
| 1 | **Story Decomposer** | Context bundle fields on Epic | Individual AI Story WITs with StoryContext, AcceptanceCriteria, ContextBundleScore, EstimatedHumanHours | Vertical slices, dependency ordering; low bundle score halts pipeline |
| 2 | **Test Plan Generator** | AI Story: StoryContext, AcceptanceCriteria | AI Story: TestPlan field | Tests written BEFORE code exists |
| 3 | **Implementation Planner** | AI Story: StoryContext, TestPlan | AI Story: ImplPlan field | Complete code, exact commands |
| 4 | **Plan Reviewer** | AI Story: TestPlan, ImplPlan (fresh context!); prior review on re-review | AI Story: PlanReviewStatus, TestPlanScore, ImplPlanScore | Context isolation; rubric-anchored scores |
| 5 | **Coder** | AI Story: ImplPlan; TestResults on self-repair loop | Code on `story/{id}` branch + PR; AI Story: PullRequestUrl | No scope creep, follow plan mechanically |
| 6 | **Code Reviewer** | AI Story: ImplPlan, TestPlan + PR diff; prior findings on re-review | AI Story: CodeReviewStatus, CodeQualityScore, CodeReviewFindings | SOLID, architecture compliance; rubric-anchored scores |
| 7 | **Test Executor** | AI Story: TestPlan + code in repo | AI Story: TestResults, TestPassRate | Honest reporting, no silent fixes; runs dependency + SAST checks |
| 8 | **Feature Verifier** | Epic PRD acceptance criteria + all approved stories | Epic-level end-to-end verification results | Runs once, after all stories approved, before human PR merges |

**Orchestrator** drives the pipeline and makes all routing decisions. All ADO reads/writes go through a **deterministic bookkeeping layer** (script or ADO MCP server) — the LLM decides, deterministic code writes (see `ado/design-spec.md` §9). It creates one `AI Agent Run` WIT per sub-agent invocation (capturing model, agent version, tokens, cost, quality), rolls up TotalCostUSD to the parent AI Story, and escalates after 2 revision failures per stage.

## Context Isolation Principle

**Critical for reviewers:** Plan Reviewer and Code Reviewer run in fresh context that does NOT see planning agents' internal reasoning or conversation history. A reviewer who read the planner's reasoning is primed to accept the plan's conclusions. A fresh reviewer who sees only the output artifacts catches gaps the planner rationalized away.

Each agent receives ONLY the output artifacts from previous agents — injected verbatim by the Orchestrator, never summarized or annotated with the Orchestrator's own opinions. Never pass conversation history or internal reasoning.

**Isolation ≠ amnesia on re-review:** when a reviewer re-reviews after a revision loop, it receives its own previous review artifact alongside the revised plan/code. This prevents review thrash (raising brand-new objections each round instead of verifying fixes). The prior review is an output artifact, not reasoning — isolation is preserved.

**Guard against shared blind spots:** run reviewers on a *different model family* than the generators they review. Fresh context protects against anchoring; a different model family protects against shared priors.

## Revision Loops

- **Plan Review Loop:** Plan Reviewer returns REVISIONS → Planner regenerates → Reviewer re-reviews (with prior review in context). Max 2 loops (`PlanRevisionCount`).
- **Code Review Loop:** Code Reviewer returns CHANGES REQUESTED → Coder re-implements → Reviewer re-reviews (with prior findings in context). Max 2 loops (`CodeRevisionCount`).
- **Test Self-Repair Loop:** Test Executor reports FAIL → Orchestrator routes the failure evidence back to the Coder → re-test. Max 2 loops (`TestRevisionCount`). The Test Executor never fixes code itself; the Orchestrator routes. This is the highest-leverage loop in the pipeline per the benchmark literature — do not remove it.
- **Escalation:** After 2 failed loops at any stage, STOP and report which agent failed, what the failure was, and recommend manual intervention.
- **Limits are tunable:** max-2 is a starting point. Use the observability data (design-spec §11.7) to tune per-stage limits over time.

## State Tracking

Each story maintains an `AI Story` work item in ADO — the authoritative record. The Orchestrator reads from and writes to ADO at each stage transition. No story artifacts are committed to the repository.

```yaml
# AI Story WIT fields updated at each stage:
StoryContext:       set by Story Decomposer
AcceptanceCriteria: set by Story Decomposer
ContextBundleScore: set by Story Decomposer (0–100)
TestPlan:           set by Test Plan Generator
ImplPlan:           set by Implementation Planner
PlanReviewStatus:   set by Plan Reviewer
TestPlanScore:      set by Plan Reviewer (0–100)
ImplPlanScore:      set by Plan Reviewer (0–100)
CodeReviewStatus:   set by Code Reviewer
CodeQualityScore:   set by Code Reviewer (0–100)
CodeReviewFindings: set by Code Reviewer
TestResults:        set by Test Executor
TestPassRate:       set by Test Executor (0.0–100.0)
TotalCostUSD:       rolled up by Orchestrator from child AI Agent Run items
```

Additionally, one `AI Agent Run` child WIT is created per sub-agent invocation:
```yaml
AgentName, ModelUsed, InputTokens, OutputTokens, EstimatedCostUSD,
DurationSeconds, QualityScore, StageDecision, RevisionAttempt, ArtifactContent
```

For ADO-based environments, all state and artifacts live exclusively in ADO work items, not in the repository.

## Context Bundle Documents

Four input documents required:

1. **PRD** — Product requirements, functional/non-functional requirements, acceptance criteria in Given/When/Then format, scope boundaries
2. **UI/UX Design** — User flows, component hierarchy, states, ASCII wireframes, API contract (TypeScript interfaces)
3. **Architecture** — Clean Architecture layers, data model, API design, DI config, Docker Compose
4. **Test Strategy** — Test pyramid, categories, test data management, anti-patterns

See `docs/context-bundle.md` for full templates.

## Key Design Principles

1. **ADO-as-contract** — All pipeline artifacts (story context, test plans, implementation plans, review output, test results) are stored as fields on ADO work items. The repository contains only code and agent instruction files. Artifacts are version-controlled through ADO work item history, not git history.
2. **Bounded, tunable revision loops** — Every failure mode has an automated repair path (plan revisions, code changes, test self-repair) with a per-stage limit (default 2) before human escalation. Limits are tuned from observability data, not guessed.
3. **DAG-parallel story execution** — Stories are vertical slices ordered by dependency. Stories with no unmet dependencies may run in parallel; never batch horizontally by architectural layer (that would break vertical slicing).
4. **Spec-first, always** — Tests written before code exists. TDD in the large.
5. **Honest failure reporting, automated repair routing** — The Test Executor reports failures honestly and never fixes code; the Orchestrator routes failures back for repair. Reporting and repairing are separate responsibilities.
6. **Full observability** — Every agent invocation creates an `AI Agent Run` ADO work item capturing model, agent version, token counts (with source), estimated cost, duration, quality score, and stage decision. Aggregate cost and quality roll up to each `AI Story`. This enables model benchmarking, cost tracking, and continuous factory improvement through ADO dashboards and queries.
7. **Calibrated measurement** — Reviewer models are pinned during generator A/B tests, scores are rubric-anchored, and objective metrics (TestPassRate, revision counts, escaped defects) are the ground truth. Self-reported LLM scores are leading indicators only.
8. **Deterministic bookkeeping** — The LLM decides; deterministic code writes. All ADO I/O goes through a validated bookkeeping layer with an end-of-story integrity check.
9. **PR as the final human gate** — Code lands on `story/{id}` branches via PRs. A human merging the PR is the last quality gate; the factory never merges to main autonomously.