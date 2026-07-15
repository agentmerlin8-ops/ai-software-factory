# Implementation Planner Evaluation Recommendations

## Purpose

This document proposes a measurement system for the **Implementation Planner** agent. Its purpose is to determine whether a change to the planner's model settings, prompt, or injected context improves the plans it produces.

The existing `ImplPlanScore`, Plan Reviewer, revision counts, code quality score, and test pass rate are useful starting points. They should be treated as part of a measurement system, not as a single score that decides whether a change was successful.

## Evaluation Principles

1. Measure the plan itself and the result it enables. A detailed plan is not high quality if it causes rework or failing code.
2. Keep the evaluator fixed when testing the planner. A changed reviewer cannot distinguish a better planner from a more generous grader.
3. Change one treatment variable at a time: model setting, planner prompt version, or context package.
4. Use the same stories for both variants when possible. Story difficulty is a major confounder.
5. Store the full plan and evaluation evidence with every run so results remain auditable.
6. Treat LLM judging as a leading indicator. Executable and downstream outcomes are the stronger evidence.

## Planner Quality Scorecard

Use a fresh-context Plan Reviewer to assign a score for each dimension below. The reviewer should produce the dimension scores, evidence, and critical findings before calculating the total. This makes the score diagnosable when a treatment changes.

| Dimension | Weight | What to Evaluate | Objective or Reviewable Evidence |
|---|---:|---|---|
| Requirements traceability | 15 | Every story acceptance criterion and planned test case maps to one or more implementation steps. No planned work lacks a story or test-plan rationale. | Traceability matrix: AC/test case -> plan step -> file(s). |
| Architectural fit | 15 | Layers, interfaces, data flow, dependencies, and existing repository conventions are respected. | Referenced symbols and files exist; no prohibited layer crossing; architecture constraints cited. |
| TDD and verification order | 15 | Each behavior follows failing test -> implementation -> passing verification. Regression and relevant integration checks are included. | Ordered steps and commands; test steps precede production changes. |
| Executability | 15 | A competent coder can carry out the plan without inventing missing decisions. File paths, symbols, commands, setup, and expected outcomes are specific and valid. | Files and commands resolve in the checked-out repository; commands are syntactically valid. |
| Test-plan coverage | 15 | The plan implements every planned scenario, including error and edge cases, and identifies the appropriate test level. | Test-plan-to-step mapping; missing-scenario count. |
| Technical correctness | 10 | APIs, types, package names, configuration, data changes, and integration points are plausible and internally consistent. | Repository search or compile-time validation; dependency registry check where applicable. |
| Scope control and minimality | 10 | The plan changes only what is needed, avoids speculative refactors, and sequences dependencies safely. | Unmapped files/steps count; reviewer evidence of scope creep. |
| Operational and security readiness | 5 | Error handling, migrations, configuration, observability, authorization, and security implications are addressed when the story requires them. | Explicit checks when applicable; no secret or unsafe configuration guidance. |

### Scoring Method

Score each dimension from 0 to 4, then calculate the weighted score:

$$
\text{ImplPlanScore} = 25 \times \sum_i w_i d_i
$$

where $w_i$ is the dimension weight as a fraction of 1 and $d_i$ is the dimension score from 0 to 4. The result is a 0-100 score.

Use these anchors for every dimension:

| Score | Meaning |
|---:|---|
| 4 | Complete, correct, and supported by concrete evidence. |
| 3 | Usable with a minor omission that does not force the Coder to make a material design decision. |
| 2 | Partially specified; the Coder must infer an important detail or manually repair an inconsistency. |
| 1 | Major omission, contradiction, or likely-invalid instruction. |
| 0 | Missing, fundamentally wrong, or unsafe. |

### Gate Rules

- **Approve:** total score at least 75, no dimension below 3, and no critical finding.
- **Revise:** total score below 75, any dimension below 3, or a critical finding.
- **Critical finding:** an unimplemented acceptance criterion, an invalid architectural direction, a nonexistent required dependency, an unsafe/security-relevant instruction, or a plan that cannot be executed from the actual repository state.

The existing overall rubric can remain as a concise summary, but the dimension-level evidence should become the primary diagnostic output.

## Deterministic Checks

LLM review should be supplemented by checks that do not depend on a judge model. These can be run by the orchestration or bookkeeping layer before the reviewer scores the plan.

| Check | Measurement | Why It Matters |
|---|---|---|
| File-path validity | Percentage of referenced existing files that resolve; separate create versus modify paths. | Detects invented repository knowledge. |
| Symbol/API validity | Percentage of referenced existing symbols, endpoints, configuration keys, and test helpers that resolve. | Detects technically impossible plans. |
| Command validity | Percentage of commands that parse and are appropriate for the repository's toolchain. | Tests whether the plan is executable rather than merely descriptive. |
| Acceptance-criteria coverage | Number and percentage of acceptance criteria mapped to a test and implementation step. | Detects missing behavior. |
| Test-plan coverage | Number and percentage of planned tests mapped to implementation and verification steps. | Ensures the implementation plan honors the test plan. |
| TDD-order violations | Count of production-change steps that occur before their corresponding failing-test step. | Tests the planner's core contract. |
| Unjustified scope items | Count of files, dependencies, migrations, or commands with no mapping to an acceptance criterion, test, or stated architectural constraint. | Detects scope creep. |
| Dependency resolution | Percentage of newly proposed dependencies that exist in the approved package registry and fit the repository's package manager. | Detects hallucinated dependencies. |

Not every repository exposes enough structured metadata for all checks. Record a check as `not applicable` rather than treating unavailable evidence as a pass.

## Downstream Outcome Metrics

The plan should also be evaluated by what happens after the Coder follows it. These are delayed but more trustworthy indicators.

| Metric | Definition | Desired Direction |
|---|---|---|
| First-pass plan approval rate | Plans approved by the Plan Reviewer on attempt one / all submitted plans. | Higher |
| Plan revision rate | Plans requiring one or more planning revisions / all submitted plans. | Lower |
| Mean plan revisions | Mean `PlanRevisionCount` per story. | Lower |
| First-pass code review approval rate | Code approved on its first review after an approved plan. | Higher |
| Mean code revisions | Mean `CodeRevisionCount` for stories produced from the plan variant. | Lower |
| Test self-repair rate | Stories requiring test-failure repair / stories entering testing. | Lower |
| Test pass rate | Passed tests / executed tests. Report both first-run and final rates. | Higher |
| Feature-verification escape rate | Features with integration failures after all story plans were approved / verified features. | Lower |
| Escaped-defect rate | Defects discovered after human merge and attributable to a plan omission / merged stories. | Lower |
| Planner cost and latency | Cost and elapsed time for the planner invocation, using a consistent token source. | Lower, subject to quality gates |

Report first-run and final outcomes separately. Final green status after repair is useful delivery information, but it can conceal a plan that created avoidable rework.

## Experiment Protocol

### 1. Define the Treatment

Create an immutable experiment identifier and record exactly one changed variable:

| Field | Examples |
|---|---|
| `PlannerModelVersion` | model family, deployment, temperature, reasoning setting |
| `PlannerPromptVersion` | content hash or tagged prompt version |
| `ContextPackageVersion` | context selection policy and content hashes |
| `ReviewerModelVersion` | pinned during planner comparison |
| `ReviewerRubricVersion` | pinned during planner comparison |
| `RepositoryCommit` | exact baseline commit used for planning |
| `StoryFixtureId` | canonical story/context case identifier |
| `TokenSource` | `Reported` or `Estimated`; never pool the two |

For a model-setting experiment, hold prompt and context package constant. For a prompt experiment, hold model settings and context package constant. For a context experiment, hold model settings and prompt constant.

### 2. Use a Benchmark Set

Build a fixed, versioned set of representative planning fixtures. Each fixture should include the repository commit, story context, acceptance criteria, test plan, architecture constraints, and an expected evaluation checklist.

Include a mix of:

- Small and medium stories
- New behavior and modifications to existing behavior
- API, data, UI, background-work, and integration work where applicable
- Error-handling and edge-case-heavy stories
- Stories requiring a migration or configuration change
- Stories that should be rejected because their context is incomplete or contradictory

Start with 20-30 fixtures for rapid regression testing. Use 50 or more completed production stories per variant before making a durable operational decision. Stratify results by story type and complexity; a variant should not appear better simply because it received easier work.

### 3. Generate and Grade Blindly

For each fixture, run the baseline and candidate planner from the same repository commit and inputs. Randomize their presentation order to the reviewer and hide which treatment generated each plan.

The reviewer must receive only the required artifacts: story context, test plan, architecture constraints, plan output, rubric, and deterministic-check results. It must not receive planner reasoning, prior conversational context, or treatment labels.

### 4. Compare Paired Results

For the same fixture, compare candidate and baseline:

$$
\Delta Q = Q_{candidate} - Q_{baseline}
$$

where $Q$ is the weighted Implementation Plan score. Also compare each dimension score, deterministic-check failure count, and downstream outcomes.

Use medians and distribution summaries, not only averages. A variant that raises the mean while creating more critical failures is not an improvement.

### 5. Declare Success in Advance

A candidate should be considered better only when all of the following hold over the evaluation set:

1. Median `ImplPlanScore` improves by at least 5 points, or the first-pass approval rate improves by at least 10 percentage points.
2. Critical-finding rate does not increase.
3. First-run test pass rate and feature-verification escape rate do not regress.
4. The improvement occurs in at least two independent signals: rubric score, deterministic checks, or downstream results.
5. Cost or latency remains within an agreed budget, unless the quality gain justifies the increase.

For small samples, label results as directional. Do not claim a model or prompt is better solely from a few high scores.

## Evaluation Reliability

The evaluator itself needs monitoring. Otherwise a score movement may be a reviewer drift rather than a planner improvement.

| Control | Recommendation |
|---|---|
| Reviewer pinning | Pin reviewer model, prompt, rubric, and deterministic-check implementation for an experiment. |
| Calibration set | Keep a small set of plans with human-adjudicated expected scores and critical findings. Re-run it when changing the reviewer. |
| Dual review sample | Independently score 10-20% of plans with a second reviewer or human reviewer. Track agreement by dimension and approval decision. |
| Disagreement handling | Human-adjudicate material disagreement; update rubric examples rather than silently averaging conflicting scores. |
| Reviewer drift | Monitor score distributions and calibration-set performance over time. Re-baseline after a reviewer/model/rubric change. |
| Rationale audit | Require finding IDs, severity, dimension, evidence, and referenced plan step for every score below 4. |

## Recommended Artifact Format

Require the planner to include a traceability section in every plan. This is both a planning aid and a machine-checkable evaluation surface.

```markdown
## Traceability

| Acceptance criterion | Test case(s) | Plan step(s) | Files |
|---|---|---|---|
| AC-1 | TC-1, TC-2 | 1, 3, 5 | tests/widget.test.ts, src/widget.ts |
```

Require the reviewer to return structured findings alongside its narrative:

```yaml
evaluation:
  rubric_version: impl-plan-v1
  scores:
    requirements_traceability: 4
    architectural_fit: 3
    tdd_and_verification_order: 4
    executability: 2
    test_plan_coverage: 3
    technical_correctness: 3
    scope_control_and_minimality: 4
    operational_and_security_readiness: 3
  total_score: 82.5
  decision: REVISIONS
  critical_findings: []
  deterministic_checks:
    acceptance_criteria_coverage: 100
    test_plan_coverage: 100
    file_path_validity: 86
    command_validity: 100
    tdd_order_violations: 0
  findings:
    - id: IP-001
      severity: major
      dimension: executability
      evidence: "Plan step 4 modifies a path that does not exist and does not state that it is to be created."
      required_change: "Correct the path or mark it as a new file."
```

The decision should be mechanically consistent with the gate rules. In the example, a score below 3 in Executability requires `REVISIONS`, even though the weighted total exceeds 75.

## Minimal Initial Dashboard

For a first implementation, display these metrics by planner model version, prompt version, and context package version:

1. Median Implementation Plan score and each rubric dimension.
2. First-pass plan approval rate and mean plan revision count.
3. Acceptance-criteria coverage, test-plan coverage, and TDD-order violations.
4. First-pass code review approval rate and mean code revision count.
5. First-run test pass rate, test self-repair rate, and feature-verification escape rate.
6. Planner cost and latency, with token source shown beside each comparison.

This dashboard answers the operational question directly: whether a change produced plans that are more complete and executable, while also reducing downstream repair work at an acceptable cost.

## Adoption Sequence

1. Add dimension scores and structured findings to the existing Plan Reviewer output while retaining the current overall score.
2. Add traceability requirements to planner output and automate acceptance-criteria/test-plan coverage checks.
3. Capture experiment metadata and freeze a 20-30 fixture benchmark set.
4. Run paired, blinded baseline-versus-candidate experiments before promoting changes.
5. Correlate rubric scores with downstream revisions, test results, feature verification, and escaped defects; adjust weights only with evidence.

Do not change score weights, reviewer prompt, and planner treatment in the same experiment. That would make the measured outcome uninterpretable.