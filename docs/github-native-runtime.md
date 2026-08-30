# GitHub-Native Runtime — Proven Field Notes

How the factory runs on plain GitHub with the `gh` CLI and Copilot coding agents. This is the open-internet / personal-lab runtime, complementary to the ADO runtime for locked-down clients.

**Everything in this document was verified live on 2026-08-29 against `agentmerlin8-ops/media-ingestion-engine` — not inferred from docs.**

## The handoff: issue → Copilot coding agent → draft PR

```
Hermes/orchestrator writes approved plan
    ↓
gh issue create  (body = story + impl-plan reference + acceptance criteria)
    ↓
gh issue edit <N> --add-assignee copilot-swe-agent[bot]
    ↓
Copilot works in GitHub's cloud — no local process, no 600s timeout
    ↓
draft PR opened, references "Fixes #N", commits include "Initial plan"
    ↓
fresh-context code review on the PR  →  local test execution  →  gh pr merge
```

### Verified mechanics

| Fact | Evidence |
|---|---|
| Assignment works via REST assignees with exact string `copilot-swe-agent[bot]` | POST `/repos/{o}/{r}/issues/{n}/assignees` returned 200; issue showed assignee "Copilot" |
| The bot picks the issue up within ~minutes | PR #2 opened by `app/copilot-swe-agent`: draft, correct file, correct content, "Fixes #1" trailer |
| Assignable agents are discoverable | GraphQL `suggestedActors(capabilities:[CAN_BE_ASSIGNED])` — returned `copilot-swe-agent`, `anthropic-code-agent`, `openai-code-agent` on one repo |
| `/repos/{o}/{r}/agents/copilot/sessions` returns 404 with fine-grained PATs | Not required — assignment is the handoff; sessions are visible in the GitHub UI |
| Copilot output is reviewable like any PR | `gh pr view/diff` work; commits visible; draft state by default |

### Token permissions needed (fine-grained PAT)

| Permission | Access | Why |
|---|---|---|
| Contents | read/write | branches, code |
| Issues | read/write | handoff issues, labels |
| Pull requests | read/write | review, merge |
| Metadata | read | always required |

A fine-grained PAT **cannot list private repos** via `/users/{u}/repos` — direct access by repo name works fine. Design automation around named repos, not enumeration.

### Why Copilot for the Coder stage

- **No subagent timeout** — sessions run as long as they need in GitHub's cloud
- **Full repo context** — it sees the real code, not an injected excerpt
- **Paid in Copilot credits**, not orchestrator tokens
- **Auditable** — every agent session is linked to the issue in the GitHub UI
- **Benchmarkable** — the same issue can be assigned to different coding agents (`anthropic-code-agent`, `openai-code-agent`) for model comparison with everything else pinned

## Division of labor (hybrid runtime)

| Role | Runs on | Rationale |
|------|---------|-----------|
| Orchestrator, Decomposer, Planners | orchestrator host (Hermes / Copilot Chat) | needs conversation + local context |
| Plan Reviewer, Code Reviewer | fresh-context runs, artifacts only | context isolation is the point |
| **Coder** | **Copilot coding agent via `gh`** | cloud execution, credits, auditability |
| Test Executor | orchestrator host | hardware, docker, compose live there |
| Dashboard | script | regenerated after every stage transition |

## Pitfalls carved from live runs

1. **Reviewers must write reports incrementally to files** (section by section), ending with a one-line verdict. A reviewer composing one giant final message can lose the whole review to a provider timeout after minutes of successful reading.
2. **Check `git status`/`git log` after any timeout** before assuming work was lost.
3. **Batch planning stages 3–5 stories per run**; never one agent per role per story.
4. **Build must be green between batches.**
5. **Storybook-first gate for UI**: stories approved by a human before feature code wires components.
6. Max 2 revision loops per stage, then escalate — never silent failure.
7. **De-risk infrastructure before the first coding batch.** Boot every external service the bundle depends on (emulators, sidecars, databases) with a throwaway compose file and verify the real protocol port answers. Live result (2026-08-30): three config constraints in the Service Bus emulator config were caught pre-build (max TTL 1h, max duplicate-detection window 5m, mandatory Logging section) — crashes that would otherwise have hit a coding agent mid-story, consuming its session and a revision loop each. Crash messages can mislead: the emulator printed "Out of memory" on a config-validation failure.
8. **Planners exhaust iteration budgets on large batches.** A combined Test-Plan + Impl-Plan run for 3 foundation stories died at the iteration cap (~50 min, ~40 calls) after completing 2.5 of 6 artifacts. Mitigations that worked: (a) partial artifacts were already on disk because of write-as-you-go, so a continuation run could resume without redoing work; (b) the continuation prompt declares the prior run's completed files as READ-ONLY context, forbids re-verifying decisions (package versions come from the first plan), sets an explicit tool-call budget, and names the critical-path artifact to finish first. Rule of thumb: **max 2 stories per planning subagent** when impl plans carry full code.
9. **First-planner-in-a-batch sets the convention anchor.** STORY-001's plan carries the frozen package-version table and shared conventions; later stories must reference it verbatim, never re-derive it. Order planning so the foundation story is always planned first.

## Local dashboard contract

`factory/DASHBOARD.md` is regenerated after every stage transition (same commit as `stories/<id>/state.md`). See `onboarding/templates/DASHBOARD.md`. Combined with GitHub's issue labels (`factory:*`) this gives a kanban view in the Issues tab without any external tooling.
