# Architecture: Factory Kit v0.1

> Status: DRAFT — context bundle (pre-grill). Drafted 2026-09-28.
> Companion docs: `prd.md`, `test-strategy.md`, `target-repo-readiness.md`.

## Overview

The kit puts the process in the repo and keeps every runtime behind an adapter. The control plane is deterministic software; every AI sits behind a **dispatch package**.

```
                 ┌────────────────────────────────────────────────┐
                 │              TARGET REPOSITORY                 │
                 │                                                │
  idea ──▶ issue │  factory/          runbook.md                  │
                 │   ├── tools/       (control plane, python3)    │
                 │   ├── ledger/      (events.jsonl = truth)      │
                 │   ├── gates/       (mechanical checks)         │
                 │   ├── templates/   (dispatch pkg, state, etc.) │
                 │   └── locks/       (OVERRIDE escape hatch)     │
                 │   process/         (process rules, versioned)  │
                 │   agents/          (role packages)             │
                 │   adapters/        (human · hermes · …)        │
                 │   stories/         (specs, plans, evidence)    │
                 └───────────┬───────────────────┬────────────────┘
                             │                   │
              operator (human) │         orchestrator (any runtime)
                             │                   │
                             └──── follows runbook.md ────┐
                                                          ▼
                              dispatch package (one per role, pinned @ SHA)
                                    │                     │
                             human adapter          hermes adapter
                          (paste into any chat)   (subagent dispatch)
                                    │                     │
                                    └──── artifacts + usage ────┘
                                                          │
                                              controller enforces transitions
                                              gates run; renders regenerate;
                                              board syncs; provenance follows
```

Substrate: **git + gh + python3 (stdlib)**. No services, no daemons, no second remote (NFR-1).

## Components

### Kit structure (source of truth, this repo)

| Path | Contents | Ported from |
|---|---|---|
| `agents/` | Role packages: instruction + inputs + outputs + stop rules, runtime-neutral | `agents/*.agent.md` (genericized) |
| `process/` | Process rules moved out of any agent runtime (planning, adversarial reviews, grill, recovery, Storybook gate) | process skills (content → docs, pointers left behind) |
| `tools/` | Control plane (see below) | private reference implementation, genericized |
| `adapters/` | `human/`, `hermes/`, (+ v0.2: `claude-code/`, `codex/`, `api-direct/`) — each with README, model table, prerequisites | new |
| `runbook.md` | idea → completed PR, both modes | private runbook, genericized |
| `onboarding/` | `onboard.sh` (install) + `verify` mode + readiness checks registry | `onboarding/`, extended |

### Control plane (`tools/`)

| Tool | Responsibility | Notes |
|---|---|---|
| `controller.py` | Transition engine: validates every state change against ledger + git + gh; refuses with named checks; claim-lock enforcement; override consultation; claim/handover/override commands | Judgment-free |
| `ledger_lib.py` | Event schema, validation (null+reason), append/read helpers | Schema is the contract |
| `gates/` | Mechanical pre-checks (plan gate incl. contract-seam + coverage checks; pre-review gate; digest gate) with fixtures | Run before any LLM review |
| `make_context_bundle.py` | Deterministic context assembly: inline pinned inputs at base SHA into one bundle | Feeds dispatch packages |
| `dispatch_prep.py` | Seam recon: contract slice, named-test exists/missing inventory, scope boundary, hard-read gate block | Pre-coder/fixer |
| `plan_prep.py` | Planner verify-pack (paste-ready block) | Pre-planner |
| `build_handoff.py` | Story handoff rendering (acceptance, files CREATE/EXTEND, verify commands, resume preamble) | |
| `model_router.py` | Role→tier matrix resolution; **per-adapter model table**; records pre-spawn dispatch event. Never writes runtime config (v0.1 change) | |
| `record_usage.py` | Usage events from executor reports (harvest when available; null+reason otherwise) | No runtime DB dependency |
| `metrics_report.py` | Per-story token/loop reconciliation vs frozen baseline; unrouted-dispatch census | |
| `render_state.py`, `render_dashboard.py`, `render_provenance.py` | Generated renders (never hand-edited); `--check` modes | |
| `sync_board.py` | GitHub Projects v2 Stage writes (explicit, never inferred) | Project id from config |

**Port rules:** keep behavior; genericize names (no product-specific component/file/test names); drop runtime-specific code paths (`hermes config` writes, runtime-DB harvests → replaced per FR-9/FR-10); stdlib only.

## State machine

16 states (ported as-is from the reference spec):

```
BACKLOG → SPEC_FROZEN → PLANNED → GATE_PASSED → PLAN_APPROVED
        → CODING → BUILD_GREEN → DRAFT_OPENED → REVIEWING
        → FIXING → FULL_TESTS_GREEN → READY_FOR_REVIEW
        → MERGE_ELIGIBLE → MERGED → LIVE_PROVEN → CLOSED
(any) → BLOCKED → resumes at originating state
```

- Every arrow = a controller transition with evidence + checks.
- `READY_FOR_REVIEW` (forge flag) ≠ `MERGE_ELIGIBLE` (factory state). Never conflated.
- Loop caps: 2 per stage; escalation beyond.

## Data model — the ledger

`factory/ledger/events.jsonl` — append-only, one JSON object per event, UTC timestamps, stable IDs.

Event types (v0.1): `transition`, `dispatch`, `usage`, `stage`, `finding`, `loop`, `correction`, `assignment` (claim lifecycle), `handover`, `human_gate`, `recovery`, `outcome`, `override_used` (annotation payload on the transition it permitted).

Conventions (unchanged from the reference):
- Missing value = `null` + sibling `<field>_reason` (non-empty), mechanically validated per type.
- Corrections are events, never edits.
- Dispatch IDs are pre-spawn: `<story>-<role>-<attempt>-<unix>`.
- Every dispatch lifecycle closes (outcome + usage or null+reason).

### Claim lifecycle (assignment event, extended)

| Op | Fields | Rule |
|---|---|---|
| claim | `owner`, `host`, `session`, `start_sha`, `claimed_at` | Required before the first active transition after BACKLOG; refused if an open claim exists (unless override) |
| handover | `from`, `to`, `reason`, `flagged` (bool) | The only sanctioned transfer; abrupt takeover = flagged handover |
| release | implicit at CLOSED; record persists | The durable ownership record |

### Override file (`factory/locks/OVERRIDE`)

```
scope: STORY-012   # or ALL
by: <human name>
reason: <why — required, no placeholders>
date: <UTC>
```

- Valid + committed + scoped → claim-lock checks pass for the scope; every permitted transition carries an `override_used` annotation incl. the file's blob SHA at use time.
- Fail-closed: absent/malformed/uncommitted/placeholder = not an override (refusal names the field).
- Narrow: never bypasses evidence, gate, or order checks. Renders show active overrides.

## Dispatch package (universal interface)

One generated markdown per dispatch. Schema:

| Section | Content |
|---|---|
| Header | story, role, attempt, tier, producer, timestamp |
| Role instruction | the role's task definition (from `agents/`) |
| Pinned inputs | every input inlined or referenced **at recorded SHA** (bundle pattern) |
| Expected outputs | exact artifact paths (+ contract shape where applicable) |
| Stop rules | when to stop and report rather than improvise |
| Resume preamble | check git status/log/artifacts first; READ-ONLY priors; budget; first edit within N calls |

Generation: by the prep tools (`plan_prep`, `dispatch_prep`, `build_handoff`, `make_context_bundle`). Consumption: **any** executor — adapter or human. Parity rule: same package through any adapter → same artifact paths + same contract shape.

## Adapter interface

Each adapter directory declares:

| Part | Content |
|---|---|
| `README.md` | prerequisites, identity, step-by-step execution of a dispatch package |
| `models.md` | tier (T1/T2/T3) → concrete model/effort table for this runtime |
| usage | how execution reports usage back (or null+reason) |

v0.1 adapters: **`human`** (operator pastes package into any AI chat; commits artifacts; usage usually null+reason) and **`hermes`** (delegate_task dispatch; per-role model applied at spawn; usage harvested). Constraint (FR-8): adding an adapter touches no control-plane code.

## Routing

Role→tier matrix by difficulty (S/M/L) stays static and complete (any unrouted role = process defect, counted). Tier→model is adapter config. Routing records to the ledger pre-spawn (`requested_model`), adapters report `reported_model`; mismatch → `model_unverified: true`.

## Onboarding architecture

- `onboard.sh <target>`: idempotent install (kit files, labels, templates, ledger seed); never overwrites; prints PASS/FAIL/WARN per check.
- `onboard.sh verify <target>` (v0.1): runs the **readiness check registry** — each check = id, category (CORE/UI/ADAPTER/ADVISORY), verify method (script), remedy text. Adapter checks live under `adapters/*/checks`.
- Registry version recorded in the target; re-runnable and CI-gateable.

## Integrations

- **git**: branches `story/<id>-<slug>`; one story = one branch = one worktree; push-per-gate (closing gates), claims/handovers push-on-write; preflight fetch + staleness check stops the run on divergence.
- **GitHub via gh**: issues (idea front door), PRs, labels, Projects v2 board (Stage writes explicit via `sync_board.py`).
- **CI (advisory)**: control-plane test suite + gate scripts on PRs.

## Configuration

Target repo config (`factory/config.yaml` or equivalent, v0.1 draft): canonical repo path, board/project id, default branch, identity (owner names, agent identity), adapter registry, kit version. No hardcoded paths in tools — all resolved from config + repo root.

## Out of scope for this architecture doc

Docker Compose (kit has no services — target projects define their own), UI design doc (kit's surfaces are generated markdown + GitHub; no app UI), ADO integration (separate future question).

## Open items (for grill)

- Exact config file schema and precedence.
- Whether `record_usage.py` keeps a manual `--token` entry path for human mode or relies solely on executors appending usage events.
- Gate catalog naming (keep G12/G13/G14 identifiers vs. rename to descriptive slugs).