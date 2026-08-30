# Factory Runbook

Operating rules for driving the pipeline in THIS repo. The orchestrator follows this checklist; humans can audit against it.

## Stage flow (per story)

```
decompose → test-plan → impl-plan → PLAN REVIEW (fresh context)
  ├─ APPROVED → hand off to Copilot coding agent → code review on PR
  │               ├─ APPROVED → test execution → merge-ready
  │               └─ CHANGES  → back to agent (max 2)
  └─ REVISIONS → back to planner (max 2)
```

## Batching

- **Planning stages** (decompose, test-plan, impl-plan, reviews): batch 3–5 stories per agent run. Build/test-heavy work is batched separately.
- **Never** one subagent per role per story — that is 6×N calls and burns hours.
- Keep a build/test verification between every batch. If the build is red, stop and fix before the next batch.

## Copilot handoff contract

1. A story enters Copilot ONLY as a GitHub issue whose body contains: story summary, approved impl-plan reference, acceptance criteria, exact files in scope.
2. Assign with: `gh issue edit <N> --add-assignee copilot-swe-agent[bot]`
3. Copilot works in GitHub's cloud (no local timeout), opens a **draft PR** referencing `Fixes #N`.
4. Code review happens on the PR by a **fresh-context reviewer** that never saw the planning conversation.
5. Review feedback goes as PR review comments; Copilot addresses them on the branch.
6. Merge only after local test execution is green: `git pull` the branch, build, run tests, then `gh pr merge`.

## Checkpoints between batches

- [ ] `git log` shows the expected commits
- [ ] Build green (0 errors, 0 warnings where applicable)
- [ ] Tests green
- [ ] `stories/<id>/state.md` updated
- [ ] `factory/DASHBOARD.md` regenerated

## Timeout / failure recovery

1. On any agent timeout: check `git status` and `git log` FIRST — work is often done but uncommitted.
2. Verify partial work compiles; commit it under the story's commit message.
3. Resume the remaining scope with a fresh agent run, not a full redo.

## Escalation (non-negotiable)

- After **2 failed revision loops** at any stage → STOP, mark the story `factory:blocked`, add `needs-human` label, report to the human with: which stage failed, what the failure was, what feedback was given.
- **Never** let an agent silently self-patch a plan or skip a gate.
- **Never** merge a PR without green local tests.

## Storybook-first gate (if the project has a web UI)

1. Dashboard/UI components are drafted as Storybook stories with mock data.
2. Human reviews and approves the stories (checkbox in DASHBOARD.md).
3. Only then may feature code wire the components.

## Visibility contract

- Every stage transition updates `stories/<id>/state.md` AND regenerates `factory/DASHBOARD.md` in the same commit.
- Commit messages always carry the story ID: `STORY-003: ...`
