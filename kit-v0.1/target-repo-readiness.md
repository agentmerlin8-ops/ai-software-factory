# Target-Repo Readiness Checklist (First Pass)

> Status: DRAFT — first pass, drafted 2026-09-28, to be grounded during the kit context-bundle grill against the private reference implementation's PREFLIGHT flow and this repo's `onboarding/onboard.sh`.
> Purpose: everything a target repository needs for the factory to be **runtime-agnostic** — and the basis for the future `onboard verify` mode (per-check PASS/FAIL, fail-closed, non-zero exit).

## How this list is used

1. **Before onboarding**: the operator (or the orchestrator) works the checklist top to bottom.
2. **Onboard verify** (to build): each item becomes a machine check with a PASS/FAIL line and a remedy printed on failure. Required items gate; advisories warn.
3. **Re-check on every significant change** (new board field, changed branch protection, new adapter) — verify is re-runnable and CI-gateable.

Check categories: **CORE** (required for any factory run) · **UI** (only when stories touch UI) · **ADAPTER** (required only when that adapter executes work) · **ADVISORY** (recommended).

## CORE — required in every target repo

| # | Check | Why | Verify method |
|---|---|---|---|
| C-1 | Git repository with a GitHub remote | Everything hangs off git + GitHub | `git remote -v`, `gh repo view` |
| C-2 | `gh` CLI authenticated with required scopes: Contents RW, Issues RW, Pull requests RW, Metadata R (+ Projects for board sync) | All forge operations | `gh auth status`; API probe call |
| C-3 | Main branch protected (no direct pushes; PR required) | The merge gate must be real | GitHub API (branch protection) |
| C-4 | Labels for the lifecycle (idea/planning/…/done, needs-human) created | Kanban visibility, automation hooks | `gh label list` |
| C-5 | Idea front door: issue form + `idea` label | Standard intake path | Issue form in `.github/ISSUE_TEMPLATE/`, label exists |
| C-6 | GitHub Projects v2 board linked to the repo, with the `Stage` field (and derived group/status fields) | Board mirrors the lifecycle; stage writes are explicit | GraphQL probe of project fields |
| C-7 | Kit installed under `factory/` (runbook, tools, gates, templates, ledger seed) | The process lives here | `factory/runbook.md` present; `tools/` executable |
| C-8 | Empty, schema-valid ledger seeded (`factory/ledger/events.jsonl`) + renders pass | Source of truth exists and renders clean | `render_state --check`, `render_dashboard --check`, ledger validation |
| C-9 | Toolchain present: `python3` (stdlib), `git`, `gh` | Control plane baseline | `command -v` trio + versions |
| C-10 | Config: canonical repo path, board/project id, default branch, identity (owner names, agent identity) | Tools are path/project-parameterized — no hardcoding | Config file present + parsed by verify |
| C-11 | `KICKOFF.md` + `PREFLIGHT.md` present (run entry + readiness report) | Cold-start discipline | Files exist; preflight re-runs |
| C-12 | Secrets posture documented: where creds live, what is never committed, how a fresh machine gets them | Locked-down portability | Secrets doc present; `.gitignore` sane |
| C-13 | Test environment runnable (project's own: docker compose, test DB, etc.) — or an explicit "manual" declaration | The coder's exit condition is build+tests green | Project-defined command, executed once by verify with the project's health check |
| C-14 | Working agreement recorded (human touchpoints: Storybook approvals, merge gate, escalations; override file location) | The run's rules must be discoverable without tribal knowledge | Documented in runbook/config |

## UI — when stories touch UI

| # | Check | Why | Verify method |
|---|---|---|---|
| U-1 | Storybook builds locally | Storybook-first gate has a harness | Project build command |
| U-2 | Visual review path defined (how a human sees a screen: story deployed, screenshot, local run) | Approvals need a surface | Documented + one dry-run |

## ADAPTER — required only when the adapter runs work

| # | Adapter | Prerequisites |
|---|---|---|
| A-1 | `human` | Editor + shell + git identity with push access to story branches; **any** AI chat (or human peers) for role work; the operator reads/writes artifacts directly |
| A-2 | `hermes` | Hermes runtime available to the operator; `delegate_task` usable; model routing table installed (`adapters/hermes/models`) |
| A-3 | `claude-code` (v0.2) | CLI installed + authenticated; non-interactive invocation documented |
| A-4 | `codex` (v0.2) | CLI installed + authenticated; non-interactive invocation documented |
| A-5 | `api-direct` (v0.2) | OpenAI-compatible endpoint + token; used for locked-down/Foundry targets |
| A-6 | (historical) `copilot` | "Coding agent assignable" style checks belong **here** — optional adapter, never core |

## ADVISORY — recommended

- A-7 | CI workflow that runs the control-plane test suite + gate scripts on PRs (the repo's own quality line).
- A-8 | Branch naming convention documented (`story/<id>-<slug>`) and enforced by the worktree convention (one story = one branch = one worktree).
- A-9 | Machines that work the repo have the workspace layout the runbook assumes (canonical path per machine; worktrees disposable).

## Notes

- **Adapter-awareness is the point**: the current onboarding flow in this repo treats a specific coding-agent product's assignability as a core prerequisite. In the kit model that becomes adapter check A-6. Core stays runtime-neutral.
- Every CORE check must be checkable **by script**; if a check cannot be automated yet, it gets a scripted **manual attest** (operator marks PASS with name/date recorded) so the list stays complete and honest.
- The list version is recorded in the target repo alongside the kit so drift is visible.