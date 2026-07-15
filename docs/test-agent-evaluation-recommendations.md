# Test Agent Evaluation Recommendations

## Purpose

This document proposes a measurement system for the test-stage agents:

1. **Test Plan Generator**: defines the testable behavioral contract before implementation.
2. **Test Executor**: runs required verification and reports evidence honestly.
3. **Feature Verifier**: validates the assembled feature against the original PRD and cross-story journeys.

These agents should not be measured by test count, number of failures reported, or a high pass rate alone. The desired outcome is meaningful: required defects are detected early, valid code is not blocked unnecessarily, and every result is supported by reproducible evidence.

## Shared Principles

1. Score the output artifact and measure its later effectiveness separately.
2. Pin the evaluator, test environment, fixture data, commands, and policy when testing a model, prompt, tool, or context change.
3. Treat a passing result as valid only when it includes reproducible command-level evidence.
4. Distinguish a test-agent failure from an application failure. A broken build is evidence against the Coder; failing to report that build is evidence against the Test Executor.
5. Use human-adjudicated test specifications and seeded defects to measure what the agents missed.
6. Track false greens and false reds separately. Both are harmful.

## Core Failure Modes

| Agent | False Green | False Red / Noise |
|---|---|---|
| Test Plan Generator | Omits a behavior, error, edge case, or integration risk that should be tested. | Requires a test that is irrelevant, contradictory, impossible, or over-specified by implementation details. |
| Test Executor | Reports PASS despite a failed, skipped, wrong, stale, incomplete, or unverifiable check. | Reports failure because it used the wrong command/environment, misclassified a known flake, or misread valid output. |
| Feature Verifier | Reports `FEATURE VERIFIED` despite an unmet PRD criterion or cross-story failure. | Reports integration failure caused by test-environment setup, unrelated infrastructure, or invalid test interpretation. |

## Test Plan Generator Scorecard

Use a fresh-context Plan Reviewer, QA reviewer, or human adjudicator to score the generated test plan against story context, acceptance criteria, test strategy, and architecture constraints. The evaluator must not see the generator's reasoning or treatment identity.

| Dimension | Weight | What to Evaluate | Evidence |
|---|---:|---|---|
| Acceptance-criteria traceability | 20 | Every acceptance criterion maps to one or more uniquely identified test cases. | Acceptance criterion -> test case mapping. |
| Scenario completeness | 20 | Happy paths, errors, negative cases, boundaries, empty states, and relevant edge cases are covered. | Scenario inventory, including missing-case count. |
| Behavioral correctness | 15 | Expected outcomes follow the product contract and do not invent requirements. | PRD/story evidence and adjudicated expected scenarios. |
| Testability and automation | 15 | Tests are automatable, use the available framework/tooling, and have controllable setup, data, and external dependencies. | Repository/test-strategy conventions; mock/stub strategy. |
| Appropriate test level | 10 | Each scenario is placed sensibly at unit, integration, contract, API, UI, or E2E level. | Test pyramid and architecture constraints. |
| Independence from implementation | 10 | Tests assert observable behavior instead of private methods, incidental structure, or the generator's preferred design. | Test case wording and assertions. |
| Clarity and executability | 10 | IDs, Given/When/Then, data/setup, expected results, and framework conventions are precise enough to implement. | Plan artifact and deterministic schema validation. |
| **Total** | **100** |  |  |

### Test Plan Scoring Method

Score each dimension from 0 to 4, then calculate:

$$
\text{TestPlanScore} = 25 \times \sum_i w_i d_i
$$

where $w_i$ is the weight as a fraction of 1 and $d_i$ is the 0-4 dimension score.

| Score | Meaning |
|---:|---|
| 4 | Complete, correct, automatable, and backed by traceability evidence. |
| 3 | Usable with a minor omission that does not leave material behavior untested. |
| 2 | Important scenario, expected behavior, test data, or automation detail is missing. |
| 1 | Major coverage gap, invalid expected result, or implementation-coupled test design. |
| 0 | Missing, contradictory, untestable, or fundamentally wrong. |

### Test Plan Gate Rules

- **Approve:** total at least 75, no dimension below 3, and no critical coverage gap.
- **Revise:** total below 75, any dimension below 3, or a critical coverage gap.
- **Critical coverage gap:** an untested acceptance criterion; security, authorization, data-loss, or safety behavior omitted; a scenario that cannot be automated despite the available system capability; or an invented test requirement that contradicts the product contract.

## Test Plan Generator Effectiveness Metrics

The plan must be judged by later evidence, not only its review score.

| Metric | Definition | Desired Direction |
|---|---|---|
| Acceptance-criteria coverage | Acceptance criteria with at least one valid test case / total criteria. | 100% |
| Adjudicated scenario recall | Required scenarios found by the generated test plan / all required scenarios in a human-adjudicated set. | Higher |
| Scenario precision | Valid, in-scope scenarios / all generated scenarios. | Higher |
| Critical-scenario recall | Required security, data, authorization, and high-risk edge scenarios found / all such scenarios. | Highest priority |
| Implementation rate | Planned test cases implemented as automated tests or justified `not applicable` / planned cases. | Higher |
| Test-plan revision rate | Plans requiring review revision / all test plans. | Lower |
| Downstream coverage escape rate | Defects later found by Code Review, Test Executor, Feature Verifier, human review, or production that were absent from the test plan / approved plans. | Lower |
| Mutation score or seeded-defect detection | Introduced known defects detected by tests derived from the plan / introduced defects. | Higher |
| Plan cost and latency | Generator cost and elapsed time. | Lower, subject to quality gates |

Test count is diagnostic only. Ten redundant tests are not better than one well-designed test that detects a meaningful defect.

## Test Executor Scorecard

The Test Executor primarily produces evidence, not a subjective judgment. Its quality score should assess whether it selected, ran, interpreted, and recorded verification correctly.

| Dimension | Weight | What to Evaluate | Evidence |
|---|---:|---|---|
| Command completeness | 20 | It runs the required build, targeted tests, full tests, lint/static analysis/SAST, dependency checks, and relevant integration/API checks. | Command manifest compared with repository policy and test plan. |
| Execution fidelity | 20 | Commands run in the required revision, environment, configuration, and test-data state, without silently skipping failures. | Exit codes, environment fingerprint, raw logs, test report artifacts. |
| Result accuracy | 20 | PASS/FAIL status, per-case results, pass rate, and check status match raw machine output. | Parsed reports compared to original logs. |
| Evidence completeness | 15 | Results include actual commands, outputs/reports, relevant API responses, and enough context to reproduce a failure. | Stored artifact content and CI links. |
| Failure classification and routing | 10 | Correctly distinguishes application failure, environment/infrastructure failure, flaky failure, and policy failure; routes actionable evidence to the Coder. | Failure taxonomy and repair evidence. |
| Security and dependency verification | 10 | Executes and reports registry/dependency, secret, SAST, and policy checks required by the project. | Tool outputs and policy status. |
| Scope discipline | 5 | Does not modify code, hide errors, disable tests, or change configuration to create a pass. | Clean-diff check and execution transcript. |
| **Total** | **100** |  |  |

### Test Executor Scoring Method

Score each dimension 0 to 4 and calculate:

$$
\text{TestExecutionScore} = 25 \times \sum_i w_i d_i
$$

| Score | Meaning |
|---:|---|
| 4 | Required checks executed faithfully; results and evidence exactly match reproducible outputs. |
| 3 | Complete and accurate with a minor non-material evidence or reporting omission. |
| 2 | A relevant check, evidence item, or failure classification is incomplete; result requires manual confirmation. |
| 1 | Major command/environment/reporting error or incomplete verification. |
| 0 | False result, hidden failure, code modification, or no reproducible evidence. |

### Test Executor Gate Rules

- **Pass:** all required checks executed, raw evidence captured, results accurately reported, and no critical execution finding.
- **Fail and route repair:** an application or policy check fails with reproducible evidence.
- **Block and escalate:** the environment is invalid, required checks cannot run, a result cannot be reproduced, or a critical execution-integrity issue exists.
- **Critical execution finding:** falsely reported pass; omitted required check; altered code or tests; suppressed/ignored failure; wrong repository revision; or missing raw evidence for a claimed result.

## Test Executor Effectiveness Metrics

| Metric | Definition | Desired Direction |
|---|---|---|
| Required-check completion rate | Required checks actually executed with captured exit code / required checks. | 100% |
| Result fidelity | Reported check results exactly matching raw machine reports / reported checks. | 100% |
| False-green rate | Executions reported as pass but later shown by rerun or independent CI to have failed/missed required checks / reported passes. | Near zero |
| False-red rate | Executions reported as application/policy failure but later proven to be valid under the same documented environment / reported failures. | Lower |
| Reproduction rate | Reported failures reproduced from the recorded command/environment / sampled failures. | Higher |
| Flake classification accuracy | Flake labels confirmed by documented retry/history policy / flake labels. | Higher |
| Failure-routing usefulness | Repair attempts receiving sufficient failure evidence to resolve the issue without requesting clarification / routed failures. | Higher |
| Post-executor CI escape rate | Issues found by independent CI/Feature Verifier after Executor pass / Executor passes. | Lower |
| Execution cost and latency | Cost and elapsed time to produce the full evidence package. | Lower, subject to fidelity gates |

The Executor's `TestPassRate` measures the application under test, not the quality of the Executor. Executor quality is whether it faithfully discovered and reported that pass rate.

## Feature Verifier Scorecard

Feature Verifier is the final test-stage agent. Score it separately from story-level execution because its purpose is cross-story, end-to-end validation against the PRD.

| Dimension | Weight | What to Evaluate | Evidence |
|---|---:|---|---|
| PRD acceptance-criteria coverage | 25 | Every feature-level criterion is exercised or explicitly justified as not applicable. | PRD criterion -> feature scenario -> evidence mapping. |
| Cross-story journey coverage | 20 | Critical end-to-end workflows, state transitions, and integration boundaries are exercised. | User journey inventory, integration branch/run output. |
| Environment and integration fidelity | 15 | Full stack, services, contracts, auth, data, and configuration reflect the target integration environment. | Compose/deployment manifests, environment fingerprint, API/UI evidence. |
| Result accuracy and evidence | 15 | Verdict and per-criterion status match command, UI, API, or telemetry evidence. | Raw logs, responses, screenshots/report artifacts where relevant. |
| Failure attribution | 10 | Failures identify implicated stories/components without overclaiming causal certainty. | Evidence-backed routing record. |
| Negative and resilience coverage | 10 | Relevant failures, permissions, unavailable dependencies, and recovery flows are checked. | Scenario set and results. |
| Scope discipline | 5 | It verifies rather than edits code, and does not substitute story test reruns for feature validation. | Transcript, commands, clean-diff check. |
| **Total** | **100** |  |  |

### Feature Verification Score and Gate

Score dimensions 0 to 4 using the same weighted formula. `FEATURE VERIFIED` requires a total at least 75, no dimension below 3, every applicable PRD criterion with evidence, and no critical finding. Otherwise return `INTEGRATION FAILURES` or `BLOCKED` when the environment cannot support a trustworthy verdict.

## Feature Verifier Effectiveness Metrics

| Metric | Definition | Desired Direction |
|---|---|---|
| PRD criterion coverage | Applicable PRD criteria with executed feature-level evidence / applicable criteria. | 100% |
| Seeded integration-defect recall | Known cross-story defects detected / seeded integration defects. | Higher |
| Feature false-green rate | Features verified by the agent but later found to violate a PRD criterion in human acceptance or production / verified features. | Lower |
| Feature false-red rate | Reported integration failures later shown invalid under the documented environment / failed features. | Lower |
| Attribution precision | Implicated stories/components confirmed as causal / all implicated stories/components. | Higher |
| Human acceptance agreement | Feature verdicts agreeing with human acceptance testing / features reviewed. | Higher |
| Verification cost and latency | Cost and time per verified feature. | Lower, subject to detection gates |

## Controlled Evaluation Protocol

### 1. Record the Treatment

For every experiment, record exactly one changed variable and pin the remaining system.

| Field | Examples |
|---|---|
| `ExperimentId` | `test-executor-context-v2` |
| `TestAgent` | Test Plan Generator, Test Executor, or Feature Verifier |
| `ModelVersion` | model/deployment/temperature/reasoning configuration |
| `PromptVersion` | content hash or tag |
| `ToolPolicyVersion` | terminal/container/network permissions and command allowlist |
| `ContextPackageVersion` | exact artifacts and hashes supplied to the agent |
| `TestStrategyVersion` | test policy, pyramid, quality gates, command manifest |
| `EnvironmentVersion` | image, dependency lockfiles, service versions, test-data seed |
| `EvaluatorVersion` | pinned reviewer/human adjudication guide and scoring rubric |
| `RepositoryCommit` | exact source revision |
| `FixtureId` | canonical test case or feature fixture |
| `TokenSource` | `Reported` or `Estimated` |

For example, to test a new Test Executor model, keep commands, container image, test data, repository commit, test plan, parsing logic, and evaluation rubric fixed. Otherwise an environment change may be mistaken for an agent improvement.

### 2. Build Test-Agent Benchmarks

Maintain separate, versioned suites for each agent.

**Test Plan Generator fixtures** should include complete and incomplete stories, ambiguous criteria, APIs, UI states, data changes, external dependencies, security/authorization behavior, edge cases, and cases where a requirement is intentionally untestable and should be escalated.

**Test Executor fixtures** should include repositories or runs with known outcomes: clean pass, unit failure, integration failure, build failure, lint/SAST failure, secret/dependency failure, skipped test, stale report, misconfigured environment, and known flaky test. The expected result must identify what ran, what failed, and whether repair, retry, or escalation is correct.

**Feature Verifier fixtures** should include integration branches with seeded cross-story defects that story tests do not detect: contract mismatch, authorization boundary failure, configuration mismatch, data migration problem, asynchronous timing failure, and incomplete user journey.

Use a human-adjudicated label for expected scenarios, expected commands/results, and expected verdict. Include clean fixtures to measure false-red behavior. Keep a held-out suite that is never used while tuning prompts.

### 3. Run Blind, Paired Comparisons

Run baseline and candidate against exactly the same fixture, repository commit, environment, test data, and input artifacts. For LLM-scored artifacts, hide treatment identity and randomize output order for the evaluator.

Compare:

- Dimension score and gate decision.
- Scenario/finding precision and recall.
- Command/check completion and result fidelity.
- False-green and false-red rates.
- Downstream defect escapes and repair efficiency.
- Cost and latency.

Do not let baseline output alter candidate input, and do not use the same test fixtures both to tune a prompt and to claim a final improvement.

### 4. Promotion Criteria

Before reviewing results, define promotion rules. A test-agent candidate should be promoted only when all applicable conditions hold:

1. Critical scenario or defect recall improves, or remains at least as high as the baseline.
2. False-green rate does not increase; it should be zero for trusted executor and feature-verifier benchmark passes.
3. False-red/noise rate does not increase materially.
4. Output score and decision obey the published gate rules.
5. At least one independent downstream signal improves or remains stable: mutation/seeded-defect detection, post-executor CI escape, Feature Verifier escape, human acceptance agreement, or escaped defects.
6. Cost and latency remain within the agreed budget, unless a documented risk reduction justifies the expense.

For the Test Plan Generator, a higher scenario count is not enough. For the Test Executor, a higher pass rate is not enough. For the Feature Verifier, more reported failures are not enough. Each must improve accurate defect prevention and evidence quality.

## Recommended Structured Outputs

### Test Plan Evaluation

```yaml
evaluation:
  rubric_version: test-plan-v1
  scores:
    acceptance_criteria_traceability: 4
    scenario_completeness: 3
    behavioral_correctness: 4
    testability_and_automation: 3
    appropriate_test_level: 4
    independence_from_implementation: 4
    clarity_and_executability: 3
  total_score: 88.75
  decision: APPROVED
  coverage:
    acceptance_criteria: 100
    required_scenarios: 92
  critical_gaps: []
  findings: []
```

### Test Execution Evaluation

```yaml
evaluation:
  rubric_version: test-executor-v1
  scores:
    command_completeness: 4
    execution_fidelity: 4
    result_accuracy: 4
    evidence_completeness: 3
    failure_classification_and_routing: 4
    security_and_dependency_verification: 4
    scope_discipline: 4
  total_score: 96.25
  verdict: PASS
  required_checks:
    build: { status: pass, exit_code: 0, evidence: build.log }
    full_test_suite: { status: pass, exit_code: 0, evidence: test-results.xml }
    sast: { status: pass, exit_code: 0, evidence: sast.json }
  integrity:
    repository_commit: abc123
    code_modified_during_execution: false
```

### Feature Verification Evaluation

```yaml
evaluation:
  rubric_version: feature-verifier-v1
  total_score: 90
  verdict: FEATURE_VERIFIED
  criteria:
    - id: PRD-AC-1
      result: pass
      evidence: integration-run-42.log
  implicated_stories: []
  environment_fingerprint: compose-sha-123
```

## Minimal Dashboard

Show the three agents separately, grouped by model, prompt, context package, tool policy, environment version, and evaluator version:

1. Test Plan score dimensions, acceptance-criteria coverage, required-scenario precision/recall, and downstream coverage escapes.
2. Test Executor score dimensions, required-check completion, result fidelity, false-green/false-red rate, reproduction rate, and post-executor escapes.
3. Feature Verifier score dimensions, PRD coverage, seeded integration-defect recall, false-green/false-red rate, attribution precision, and human acceptance agreement.
4. Mutation or seeded-defect detection, test self-repair rate, escaped defects, cost, and latency across each agent.

## Adoption Sequence

1. Define scorecards and structured output schemas for all three test agents.
2. Add a test-command manifest and environment fingerprint so Executor results are reproducible.
3. Build a small human-adjudicated benchmark for each test agent, including clean and deliberately defective fixtures.
4. Pin evaluator, environment, artifacts, and commands while testing one model/prompt/tool/context change at a time.
5. Promote changes only when they preserve or improve critical detection, reduce false greens, and remain acceptable on false-red rate, cost, and latency.

The test-stage objective is not "more tests" or "more failures." It is trustworthy evidence that the intended behavior works and that meaningful defects cannot silently pass through the factory.