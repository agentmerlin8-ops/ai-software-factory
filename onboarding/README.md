# Onboarding a Repo to the AI Software Factory

Repeatable, idempotent onboarding for **greenfield** (new) and **brownfield** (existing code) repositories. Same command, same result, every time.

## Quick start

```bash
git clone https://github.com/agentmerlin8-ops/ai-software-factory
cd ai-software-factory
./onboarding/onboard.sh /path/to/your/repo
```

That's it. The script:

1. **Preflights** — `gh` CLI installed and authenticated, target repo exists on GitHub, Copilot coding agent is assignable there
2. **Detects posture** — greenfield (no source code) vs brownfield (existing code) and emits the matching bootstrap checklist
3. **Installs the factory structure** into the target repo (idempotent — never overwrites your existing files):
   - `.github/agents/*.agent.md` — the pipeline's agent prompts (single source of truth)
   - `factory/DASHBOARD.md` — the live visibility dashboard (regenerated after every stage transition)
   - `factory/runbook.md` — batch sizes, checkpoints, timeout recovery, escalation rules
   - `factory/templates/` — story file, issue-handoff, and state templates
   - `stories/` — one directory per story; `stories/{id}/state.md` is the audit trail
4. **Creates the GitHub labels** that power the kanban visibility (`factory:planning` … `factory:done`, `needs-human`)
5. **Verifies the Copilot handoff** — queries `suggestedActors` to confirm coding agents are assignable
6. **Writes `factory/PREFLIGHT.md`** — a PASS/FAIL readiness report you can commit

Re-run it any time; it only adds what's missing.

## Greenfield vs brownfield

| Posture | Detected by | What onboarding adds |
|---|---|---|
| **Greenfield** | no source files / empty repo | Stub context-bundle docs (`docs/prd.md`, `docs/architecture.md`, `docs/ui-design.md`, `docs/test-strategy.md`) for you to fill in. Factory won't decompose until the bundle passes the quality gate. |
| **Brownfield** | existing source tree | `factory/bootstrap-checklist.md` — capture build/test commands, frameworks, conventions, and known debt into the context bundle BEFORE decomposition. The pipeline must never assume a brownfield repo's conventions. |

## Prerequisites

- `gh` CLI authenticated as an account with write access to the target repo
- **Copilot coding agent enabled** on the repo (Settings → Copilot → Coding agent). Free/Pro/Team/Enterprise plans with Copilot access can use it.
- A fine-grained PAT (or `gh auth login`) with: **Contents** read/write, **Issues** read/write, **Pull requests** read/write, **Metadata** read. See `docs/github-native-runtime.md` for the full permission table.

## After onboarding

1. Fill in (or complete) the context bundle in `docs/`
2. Grill the bundle (comprehension verification) — see root README
3. Run story decomposition (Story Decomposer agent)
4. Hand stories to the pipeline — see `factory/runbook.md` in the target repo

## Consistency guarantee

`onboard.sh` is deterministic: same inputs → same files, same labels, same report. It prints a PASS/FAIL line per check and exits non-zero if any required check fails, so it can gate CI.
