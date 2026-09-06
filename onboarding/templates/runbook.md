# Factory Runbook

Operating rules for driving the pipeline in THIS repo. The orchestrator follows this checklist; humans can audit against it.

## Stage flow (per story)

```
decompose → test-plan → impl-plan → PLAN REVIEW (fresh context)
  ├─ APPROVED → coder (delegate_task subagent on story branch) → code review on diff
  │               ├─ APPROVED → test execution → merge-ready
  │               └─ CHANGES  → back to coder (max 2)
  └─ REVISIONS → back to planner (max 2)
```

## Model allocation policy

Use the cheapest model sufficient for each role. Scarce frontier-model budget
is reserved for a **meta-advisor**: bounded process-improvement consults at
phase boundaries, logged with dispositions in `factory/FABLE-CONSULTS.md`,
with a kill rule (two consecutive consults with nothing adopted → stop).

## Batching

- **Planning stages** (decompose, test-plan, impl-plan, reviews): max 2 stories per planning subagent when impl plans carry full code; 3–5 for lightweight artifacts.
- **Coder batches:** 3–5 stories max per subagent (2–3 for test-heavy).
- **Never** one subagent per role per story — that is 6×N calls and burns hours.
- Keep a build/test verification between every batch. If the build is red, stop and fix before the next batch.

## Coder handoff contract

1. A story enters the coder ONLY with a written handoff at `stories/<id>/handoff.md`: story summary, approved impl-plan path, acceptance criteria, exact files in scope (CREATE vs EXTEND), verification commands with expected output, exact commit message.
2. The coder subagent prompt must be **mechanical**: read ONLY listed files, write the first edit within 10 tool calls, STOP and report if anything else is needed. Never "study the repo then fix."
3. Coder works on a `story/<id>-<slug>` branch, commits as it goes.
4. Code review happens on the branch diff by a **fresh-context reviewer** that never saw the planning conversation; if it must build, it uses a worktree under /tmp — never the shared tree.
5. Review feedback goes back as copy-paste-ready diffs, or the orchestrator applies small fixes directly.
6. Stories that CREATE the same file run **sequentially**; EXTEND-only stories may parallelize.
7. Merge only after local test execution is green (full suite + the story's named test project).

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
