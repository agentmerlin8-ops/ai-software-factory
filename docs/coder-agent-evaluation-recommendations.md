# Coder Agent Evaluation Recommendations

## Purpose

This document proposes a measurement system for the **Coder** agent. Its purpose is to determine whether a change to the Coder's model settings, prompt, tools, or injected context improves the code it produces.

The existing Code Reviewer score, revision count, test pass rate, and Feature Verifier result are useful starting points. They should be measured as a system: a coding variant is better when it delivers correct, maintainable, secure code with less downstream repair at an acceptable cost and latency.

## What the Coder Is Accountable For

The Coder is not being evaluated for producing the most code or the most elaborate solution. It is evaluated for:

1. Implementing the approved plan and required behavior.
2. Using test-driven development in the required order.
3. Respecting architecture, repository conventions, and scope boundaries.
4. Producing a focused, reviewable pull request.
5. Passing independent build, test, lint, static-analysis, and relevant integration checks.
6. Avoiding unsafe changes, invented dependencies, secrets, and unrelated modifications.
7. Repairing only evidence-backed failures during a self-repair loop.

## Coder Quality Scorecard

Use a fresh-context Code Reviewer to score the pull request diff. The reviewer should receive the approved implementation plan, test plan, architecture constraints, diff, automated-check results, and prior review findings when re-reviewing. It must not receive the Coder's reasoning or treatment label.

| Dimension | Weight | What to Evaluate | Objective or Reviewable Evidence |
|---|---:|---|---|
| Required behavior and plan adherence | 20 | The diff implements each required plan step and acceptance criterion without changing intended behavior. Deviations are only allowed when explicitly escalated and approved. | Acceptance criterion/test case -> plan step -> changed code/test mapping; code-review findings. |
| Test effectiveness and TDD evidence | 15 | Tests cover required happy, error, and edge behavior; tests assert outcomes rather than implementation details; evidence shows fail -> implement -> pass where tooling permits. | Test diff, test execution output, commit chronology or command transcript. |
| Architecture and maintainability | 15 | Layer boundaries, abstractions, naming, error handling, dependency injection, and established repository conventions are respected. | Diff review, static analysis, architecture checks. |
| Build and verification health | 15 | Build, targeted tests, full tests, linters, static analysis/SAST, and relevant integration/API checks pass independently. | Raw command output from Test Executor or CI. |
| Scope control and change minimality | 10 | Files, dependencies, refactors, configuration changes, and migrations are necessary for the story. The self-repair path changes only what the failure evidence requires. | Diff size and file list mapped to plan; unrelated-change count. |
| Security and dependency hygiene | 10 | No secrets, unsafe input handling, authorization gaps, vulnerable patterns, or hallucinated/unapproved dependencies. | Secret scan, SAST/dependency scan, registry and lockfile checks. |
| Reliability and operational readiness | 10 | Appropriate validation, error paths, logging/telemetry, configuration, migration/rollback, concurrency, and performance considerations are implemented when required by the story. | Tests, configuration diff, migrations, reviewer findings. |
| **Total** | **100** |  |  |

### Scoring Method

Score each dimension from 0 to 4, then calculate the weighted Code Quality score:

$$
\text{CodeQualityScore} = 25 \times \sum_i w_i d_i
$$

where $w_i$ is the dimension weight as a fraction of 1 and $d_i$ is the dimension score from 0 to 4. This converts the weighted result to a 0-100 score.

Use these anchors for each dimension:

| Score | Meaning |
|---:|---|
| 4 | Complete, correct, maintainable, and supported by verification evidence. |
| 3 | Correct and usable with a minor issue that does not materially affect behavior, safety, or maintenance. |
| 2 | Partial or weak; a meaningful omission needs repair before the code should be trusted. |
| 1 | Major defect, plan deviation, architectural violation, or unreliable test coverage. |
| 0 | Missing, fundamentally wrong, insecure, or not buildable. |

### Gate Rules

- **Approve:** total score at least 75, no dimension below 3, all required automated checks pass, and no critical finding exists.
- **Changes requested:** total below 75, any dimension below 3, any required check fails, or a critical finding exists.
- **Critical finding:** security vulnerability or leaked secret; a required acceptance criterion missing or behaviorally wrong; build failure; unapproved/hallucinated dependency; data-loss or migration-safety issue; unauthorized access; or an architectural violation that invalidates the system design.

The dimension floor matters. A large amount of correct business behavior cannot compensate for a security score of 1 or a test-effectiveness score of 2.

## Deterministic Evidence and Checks

Do not rely only on an LLM code review. The Test Executor, CI system, repository tools, and bookkeeping layer should produce objective measures for every Coder run where applicable.

| Check | Measurement | Why It Matters |
|---|---|---|
| Build success | Pass/fail, exit code, and raw build output. | Code that does not build cannot be high quality. |
| Targeted test pass rate | Passed planned/affected tests divided by executed targeted tests. | Confirms the story's behavior directly. |
| Full regression pass rate | Passed full-suite tests divided by executed full-suite tests. | Detects collateral damage. |
| Test-plan implementation coverage | Percentage of planned test cases represented by tests or explicitly justified as not automatable/not applicable. | Detects plans implemented only partially. |
| Acceptance-criteria evidence coverage | Percentage of acceptance criteria with executable evidence: test, API response, UI/E2E result, or justified exception. | Keeps the code connected to the product contract. |
| Lint/static-analysis/SAST findings | Counts by severity, plus new findings introduced by the diff. | Detects correctness, security, and maintainability problems. |
| Secret scan | New secret findings, expected zero. | Prevents credential leakage. |
| Dependency integrity | New dependency count; percentage resolving in the approved registry; lockfile consistency; license/vulnerability policy status. | Detects hallucinated or unsafe supply-chain changes. |
| Diff scope | Files changed, lines changed, unrelated-file count, and unplanned-dependency count. | Detects scope creep and over-refactoring. |
| Architecture policy checks | Layer/import/dependency-rule violations introduced by the diff. | Detects structural erosion. |
| Commit/branch/PR hygiene | Story branch used, no direct main commit, PR present, required commit/CI metadata. | Confirms the Coder followed the delivery contract. |
| TDD evidence | Test-first commit or captured failing-test command before production implementation, when the harness can record it. | Measures the stated coding discipline rather than assuming it. |

Record checks as `not applicable` only when the repository truly lacks the relevant technology or the story does not involve it. An unavailable check is not a passing check.

## Downstream Outcome Metrics

The strongest Coder measurements are the outcomes after its code encounters independent review and execution.

| Metric | Definition | Desired Direction |
|---|---|---|
| First-pass code-review approval rate | Coder runs approved on their first Code Reviewer attempt / all first review attempts. | Higher |
| Code-review revision rate | Stories requiring one or more code-review repair loops / stories reviewed. | Lower |
| Mean code revisions | Mean `CodeRevisionCount` per story. | Lower |
| First-run build success rate | First Coder submissions that build successfully / first submissions. | Higher |
| First-run targeted test pass rate | Targeted tests passed on the first Test Executor run / targeted tests executed. | Higher |
| First-run full-suite pass rate | Full-suite tests passed on the first Test Executor run / full-suite tests executed. | Higher |
| Test self-repair rate | Stories entering a test-failure repair loop / stories entering testing. | Lower |
| Mean test repairs | Mean `TestRevisionCount` per story. | Lower |
| Static-analysis regression rate | Coder submissions introducing new warning/error/SAST findings / submissions. | Lower |
| Feature-verification escape rate | Verified features with integration failures implicating this Coder's stories / verified features. | Lower |
| Post-merge escaped-defect rate | Production or user-acceptance defects attributed to a Coder omission / merged stories. | Lower |
| Human PR override rate | Human reviewers requiring changes after the AI Code Reviewer approved / approved PRs reviewed by humans. | Lower |
| Cost and latency | Coder run cost and elapsed time, reported with token source. | Lower, subject to quality gates |

Keep **first-run** and **final** values separate. A final pass after two repair loops demonstrates recoverability, but first-run success measures the quality of the original Coder output.

## Testing Model, Prompt, Tool, and Context Changes

### Treatment Metadata

Each Coder run needs immutable metadata. This makes it possible to attribute an outcome to the actual change made.

| Field | Examples |
|---|---|
| `ExperimentId` | `coder-context-v3-2026-07` |
| `CoderModelVersion` | model family, deployment, temperature, reasoning/tool setting |
| `CoderPromptVersion` | content hash or tagged instruction version |
| `CoderToolPolicyVersion` | available tools, tool permissions, command allowlist |
| `CoderContextPackageVersion` | which artifacts were supplied and their content hashes |
| `PlannerVersion` | planner model/prompt/context version that produced the approved plan |
| `CodeReviewerModelVersion` | pinned during Coder evaluation |
| `CodeReviewerRubricVersion` | pinned during Coder evaluation |
| `TestExecutorVersion` | pinned commands and verification policy |
| `RepositoryCommit` | exact starting commit for the run |
| `StoryFixtureId` | canonical benchmark case or production-story identifier |
| `TokenSource` | `Reported` or `Estimated`; do not pool sources |

Change exactly one treatment variable per experiment. Examples:

- To test a new model setting, keep the Coder prompt, tool policy, context package, plan version, reviewer, and executor fixed.
- To test a prompt, keep model settings, tools, context, approved plan, reviewer, and executor fixed.
- To test more context, keep model settings and prompt fixed, and define the context package precisely rather than describing it informally.

### Fixed Benchmark and Paired Runs

Build a versioned Coder benchmark set. Each fixture should contain:

- Repository at an exact starting commit
- Approved implementation plan and test plan
- Story context and acceptance criteria
- Architecture constraints
- Test/verification commands and expected relevant outcomes
- A clean branch/worktree for each treatment

Include a mix of small and medium changes; defects in existing code; new behavior; API/data/UI/integration work; error-handling-heavy stories; migrations/configuration; external dependency changes; and examples where the correct behavior is to stop and report a plan gap.

For each fixture, run baseline and candidate in separate clean worktrees from the same commit. Do not let one variant's output influence the other. Randomize the order in which blind reviewers receive each diff.

Use the same approved plan for both treatments when evaluating the Coder. Otherwise a better plan can be incorrectly credited to the Coder.

### Success Criteria

Before seeing results, set promotion criteria. A candidate Coder should be promoted only if all conditions below hold over the benchmark or a sufficiently large production sample:

1. First-pass code-review approval rate improves by at least 10 percentage points, or median `CodeQualityScore` improves by at least 5 points.
2. First-run build and test-pass rates do not decline.
3. Critical findings, new security findings, and dependency-integrity failures do not increase.
4. Mean code revisions and test self-repair rate decrease or remain flat.
5. The gain appears in at least two independent signals: blind-review rubric, deterministic verification, or downstream feature outcomes.
6. Cost and latency remain within the agreed budget, unless the quality improvement justifies an explicit tradeoff.

Use medians and distribution summaries alongside means. Do not approve a candidate that raises average scores while increasing severe failures or widening outcome variance.

## Evaluator Reliability Controls

The evaluation pipeline must remain stable while the Coder changes.

| Control | Recommendation |
|---|---|
| Fresh-context reviewer | Pin the Code Reviewer model, prompt, rubric, and context boundary for the whole experiment. |
| Blind treatment labels | Hide baseline/candidate identity and randomize review order. |
| Calibration set | Maintain human-adjudicated diffs with expected findings and severity. Re-run it whenever the reviewer or rubric changes. |
| Dual-review sample | Independently review 10-20% of diffs with a second reviewer or a human; measure agreement by dimension, severity, and decision. |
| Objective executor | Pin Test Executor commands, environment, seed/test data, SAST policy, and dependency policy. |
| Flake handling | Identify and rerun known flaky checks under a documented policy; report both raw and normalized outcomes. |
| Human confirmation | Track human reviewer overrides of AI approvals and rejections. This is the strongest ongoing calibration signal. |
| Rationale audit | Require finding ID, severity, dimension, changed-file reference, evidence, and required correction for every score below 4. |

## Recommended Reviewer Output

The existing review decision and overall score are useful, but structured detail makes a change diagnosable:

```yaml
evaluation:
  rubric_version: coder-v1
  scores:
    required_behavior_and_plan_adherence: 4
    test_effectiveness_and_tdd_evidence: 3
    architecture_and_maintainability: 4
    build_and_verification_health: 4
    scope_control_and_change_minimality: 3
    security_and_dependency_hygiene: 4
    reliability_and_operational_readiness: 3
  total_score: 91.25
  decision: APPROVED
  critical_findings: []
  deterministic_checks:
    build: pass
    targeted_test_pass_rate: 100
    full_suite_pass_rate: 100
    acceptance_criteria_evidence_coverage: 100
    test_plan_implementation_coverage: 100
    new_sast_findings: 0
    new_secret_findings: 0
    dependency_integrity: pass
    unplanned_files_changed: 0
    tdd_evidence: present
  findings:
    - id: CR-001
      severity: minor
      dimension: scope_control_and_change_minimality
      file: src/example.ts
      evidence: "One helper rename is unrelated to the approved plan."
      required_change: "Revert the unrelated rename or document an approved dependency."
```

Scores and decision must agree with gate rules. For example, a score of 2 in Security requires `CHANGES REQUESTED` even if the weighted total is above 75.

## Minimal Initial Dashboard

Show the following by Coder model version, prompt version, tool policy version, and context package version:

1. Median Code Quality score and each scorecard dimension.
2. First-pass code-review approval rate, mean code revisions, and severity distribution of findings.
3. First-run build success, targeted/full test pass rates, and test self-repair rate.
4. Acceptance-criteria evidence coverage, test-plan implementation coverage, and TDD-evidence rate.
5. New lint, SAST, secret, dependency, and architecture-policy findings.
6. Feature-verification escape rate, post-merge escaped-defect rate, and human PR override rate.
7. Coder cost and latency, with token source visible in every comparison.

## Adoption Sequence

1. Require structured dimension scores and evidence from the Code Reviewer while retaining the existing overall score and decision.
2. Capture deterministic checks from CI/Test Executor for every Coder run; start with build, test pass rates, SAST, secret scan, and dependency integrity.
3. Add treatment metadata and preserve the exact repository commit, approved plan, and context package for each run.
4. Create a benchmark set of 20-30 fixed Coder fixtures and run blinded, paired baseline-versus-candidate comparisons.
5. Compare rubric scores with first-run verification, review loops, feature verification, and post-merge defects; adjust dimensions or weights only when the data supports it.

Do not change the Coder treatment and the Code Reviewer, test environment, or benchmark set in the same experiment. That would make any outcome impossible to attribute confidently.