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
10. **Provider non-streaming timeouts kill large single generations.** A planner composing a 12KB+ code-heavy plan in one message died with "Non-streaming API call timed out after 180s" (3 retries) — same failure class as reviewers composing one giant report. The fix is the **skeleton-then-patch technique**: (a) one small write creates the full document skeleton (header + complete task list with empty sections), (b) each section is filled by a small patch replacing its title line, one patch per section, each generation kept under ~150 lines. Works because every individual generation stays under the provider's timeout. Mandate it in planner prompts for any code-heavy artifact; cap generation size explicitly ("never more than ~150 lines per write/patch").
11. **Skeleton-first is not always enough — split review scope instead.** A full-bundle fresh-context plan review (3 stories × 6 artifacts) died twice to the same 180s timeout even with skeleton-first discipline: the *reading + reasoning* over a large bundle is what overflows, not just the writing. Mitigations that work: (a) review per story, not per batch — one fresh reviewer per story keeps the context bounded; (b) for mechanical dimensions (TDD mapping, coverage counts, package/version coherence), fall back to a deterministic orchestrator script — regex/count checks are timeout-proof and auditable. Live result: dimension A (judgment-heavy) succeeded on a 245-line report; dimension B succeeded only as a mechanical audit after two timeout deaths.
12. **Shared working tree + parallel agents + `git add -A` = accidental merge.** Live incident (2026-08-30): a code reviewer checked out a PR branch into the shared repo working tree (`git checkout origin/<branch> -- .`) to build it; the orchestrator then ran `git add -A && git commit` for a dashboard update and swept the uncommitted PR code into main — merging before the review verdict. Outcome happened to be benign (code passed build+tests and was headed for main anyway), but the gate order (review → merge) was violated. Rules: (a) reviewers/coders that need the code checked out must use a separate `git worktree add` directory, never the shared tree; (b) the orchestrator NEVER runs bare `git add -A` while subagents share the repo — stage files explicitly by path; (c) code-review subagent prompts must say "review via git diff/show; if you must build, use a worktree under /tmp".
13. **Planners can invent invalid syntax — code review is the catch net.** Live case (STORY-002): the impl plan mandated C# raw strings in the form `"""$ … $"""` to protect `$$;` sproc terminators — but that form is invalid C# (the interpolation `$` must PREFIX the quotes: `$"""`). The Copilot coder silently used plain `"""` (which works: `$$;` inside a non-interpolated raw string is fine), and the fresh-context code reviewer flagged the deviation as POSITIVE rather than a violation. Lesson: when plans prescribe exact code syntax, the planner's claim is unverified prose — treat "code deviates from plan in a way that compiles and passes tests" as a data point for plan defects, not coder error. Corollary for planners: only mandate syntax you have compiled or quoted from a working example.
14. **Near-identical test-project names invite false "tests lost" alarms.** Live near-miss (STORY-004 merge verification): the repo carries BOTH `tests/Mie.Integration.Tests` (STORY-002's Testcontainers harness) and `tests/Mie.Infrastructure.Tests` (STORY-004's PI client unit tests). After merging, running the familiar `Mie.Integration.Tests` showed 24 tests — the 27 new PI tests appeared "lost" until the right project was run. Rules: (a) verification commands must name the EXACT test project per story, never "the integration tests"; (b) orchestrator merge verification runs the FULL solution test suite (`dotnet test MediaIngestionEngine.sln`) plus each story's named project, and compares totals against the dashboard's expected counts; (c) planners pick project names that can't be confused (Infrastructure.Tests vs Integration.Tests was one letter class apart).

## Local dashboard contract

`factory/DASHBOARD.md` is regenerated after every stage transition (same commit as `stories/<id>/state.md`). See `onboarding/templates/DASHBOARD.md`. Combined with GitHub's issue labels (`factory:*`) this gives a kanban view in the Issues tab without any external tooling.
