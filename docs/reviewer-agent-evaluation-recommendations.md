# Plan and Code Reviewer Evaluation Recommendations

## Purpose

This document proposes a way to evaluate changes to the **Plan Reviewer** and **Code Reviewer** agents. Reviewers are different from planners and coders: their job is to make correct decisions about somebody else's artifact.

Therefore, a reviewer cannot be validated by its own score, its own decision, or the number of findings it writes. A reviewer that approves everything will create few revision loops but miss defects. A reviewer that rejects everything will find many issues but create unnecessary cost and delay.

A reviewer change is effective only when it improves the detection of material defects while avoiding unnecessary rejections, and when its approved artifacts have better independent downstream outcomes.

## The Two Reviewer Failure Modes

Every review decision has two costly failure modes:

| Failure | Meaning | Example |
|---|---|---|
| False approval | The reviewer approves an artifact that contains a material defect. | A Plan Reviewer approves a plan missing an acceptance criterion; a Code Reviewer approves a security flaw. |
| False rejection | The reviewer requests changes to an artifact that is acceptable, or raises an invalid/non-actionable finding. | The reviewer insists on a refactor not required by the story or claims a valid dependency is nonexistent. |

The evaluation must measure both. A reviewer is not better merely because it finds more issues, produces lower scores, or forces more revisions.

## Definition of Ground Truth

The practical reference standard is an **adjudicated review set**: plans and pull-request diffs independently labeled by knowledgeable humans using a stable rubric.

For every artifact in the set, the adjudication record should state:

- Whether the artifact should be approved or revised.
- Each material defect or required change.
- Severity: `critical`, `major`, `minor`, or `informational`.
- Rubric dimension or policy violated.
- Evidence: artifact section, file, diff hunk, test output, repository fact, or deterministic-check result.
- Whether the finding is actionable and within the reviewer's scope.

Use a two-person human review with a third adjudicator for disagreements on a representative sample. The reference set does not need to be huge to begin: 50-100 diverse artifacts is a usable calibration set. Expand it continuously with production examples and human-review overrides.

Downstream outcomes are supporting ground truth, not a full replacement for adjudication. For example, a test failure after code approval proves that a problem escaped the Code Reviewer, but a passing test suite does not prove that the reviewer found every relevant maintainability or security issue.

## Shared Reviewer Metrics

### Finding-Level Accuracy

Compare each reviewer finding with the adjudicated findings.

| Metric | Definition | Desired Direction |
|---|---|---|
| Finding precision | Valid, actionable reviewer findings / all reviewer findings. | Higher |
| Finding recall | Adjudicated material findings detected by reviewer / all adjudicated material findings. | Higher |
| Critical/major recall | Critical and major adjudicated findings detected / all critical and major adjudicated findings. | Highest priority |
| Critical/major precision | Reviewer critical/major findings confirmed by adjudication / all reviewer critical/major findings. | Higher |
| Severity agreement | Findings assigned the same or an acceptable adjacent severity / matched findings. | Higher |
| Duplicate/noise rate | Duplicate, unsupported, out-of-scope, or non-actionable findings / all findings. | Lower |
| Finding evidence rate | Findings containing a valid artifact reference and concrete correction / all findings. | Higher |

For a binary decision, define:

$$
\text{Precision} = \frac{TP}{TP + FP}
$$

$$
\text{Recall} = \frac{TP}{TP + FN}
$$

where:

- $TP$ is a valid material issue the reviewer correctly identified.
- $FP$ is an invalid or immaterial issue the reviewer raised as requiring change.
- $FN$ is a material issue present in the artifact that the reviewer missed.

For reviewers, **critical/major recall** should outweigh overall recall. Missing one security flaw is more important than missing several naming issues.

### Decision-Level Accuracy

Measure whether the final decision matches adjudication.

| Metric | Definition | Desired Direction |
|---|---|---|
| Approval precision | Correct approvals / all reviewer approvals. | Higher |
| Approval escape rate | Artifacts approved by reviewer but judged as requiring revision / all reviewer approvals. | Lower |
| Revision precision | Correct revision decisions / all reviewer revision decisions. | Higher |
| Unnecessary revision rate | Artifacts sent back by reviewer but adjudicated acceptable / all revision decisions. | Lower |
| Decision accuracy | Decisions matching adjudication / all decisions. | Higher |
| Decision agreement | Cohen's kappa or similar agreement statistic against human adjudication. | Higher |

Do not optimize a single number. Approval escape rate is a risk metric, while unnecessary revision rate is a throughput and cost metric; both must remain visible.

### Score Calibration

The reviewers produce numeric scores, so evaluate whether those scores mean what they claim.

| Metric | Measurement | Desired Direction |
|---|---|---|
| Score-to-decision consistency | Percentage of scores whose decision obeys the published gate rules. | 100% |
| Mean absolute score error | Average absolute difference between reviewer and adjudicator score. | Lower |
| Dimension-score agreement | Agreement for each scorecard dimension, not only the total. | Higher |
| Calibration by score band | For each band, compare predicted approval quality with actual adjudicated or downstream pass rate. | Scores should be monotonic and meaningful |
| Reviewer drift | Change in calibration-set scores without a corresponding artifact change. | Near zero |

An overall score is useful only if, for example, artifacts scored 90-100 are materially safer than artifacts scored 75-89. If both bands have similar escape rates, the scoring scale is not calibrated.

### Operational Metrics

| Metric | Definition | Desired Direction |
|---|---|---|
| Review latency | Time from review start to decision. | Lower, subject to accuracy |
| Review cost | Model cost per review, with token source recorded. | Lower, subject to accuracy |
| Revision convergence rate | Revision loops that reach a justified approval within the allowed attempts / loops started. | Higher |
| Review thrash rate | Re-reviews that add unrelated new findings, reverse prior positions without artifact changes, or fail to disposition prior findings. | Lower |
| Finding density | Valid material findings per artifact size/complexity. | Diagnostic only, not a target |

Never make finding count a success metric. It incentivizes noise.

## Plan Reviewer Evaluation

### What Counts as a Material Plan Defect

Plan Reviewer ground truth should label defects such as:

- Acceptance criteria or test-plan scenarios with no implementation or verification path.
- Invalid file paths, commands, dependencies, symbols, or repository assumptions.
- Architecture violations or contradictory design directions.
- Missing data migration, error path, security, configuration, or integration requirement when the story requires it.
- TDD ordering that cannot validate required behavior.
- Scope expansion or unsupported design decisions that force the Coder to improvise.

### Independent Evidence for Plan Review

Run deterministic checks before judging the reviewer:

| Evidence | Use |
|---|---|
| Acceptance-criteria and test-plan traceability matrix | Confirms whether required behavior has a planned test and implementation path. |
| File, symbol, API, command, and dependency validation | Confirms whether a plan is executable in the stated repository revision. |
| Architecture policy validation | Identifies prohibited layer/dependency directions. |
| Coder stop/escalation rate | A Coder stopping because the approved plan has a gap is evidence of a Plan Reviewer escape. |
| First-pass code-review and test outcomes | Weak downstream signal that an approved plan was complete enough to implement. |

### Plan Reviewer Outcome Metrics

| Metric | Definition | Desired Direction |
|---|---|---|
| Plan approval escape rate | Approved plans later found by adjudication or deterministic checks to contain a major/critical defect / approved plans. | Lower |
| Coder plan-gap escape rate | Coder runs that correctly stop/report an approved-plan gap / runs from approved plans. | Lower |
| Post-approval plan revision rate | Approved plans later returned for a plan defect before code completion / approved plans. | Lower |
| First-pass implementation readiness | Approved plans whose Coder completes without plan clarification/escalation / approved plans. | Higher |
| Downstream plan-attributable defects | Code-review, test, or feature failures traced to a plan omission / approved plans. | Lower |
| Unnecessary plan revision rate | Plans returned by reviewer but adjudicated acceptable / returned plans. | Lower |

The last two measures require root-cause tagging. Distinguish a plan omission from a Coder implementation error; otherwise the reviewer will be blamed for defects it could not have detected.

## Code Reviewer Evaluation

### What Counts as a Material Code Defect

Code Reviewer ground truth should label defects such as:

- Required behavior missing, wrong, or inconsistent with the approved plan and acceptance criteria.
- Missing or ineffective tests for required behavior, errors, or edge cases.
- Build, test, lint, static-analysis, architecture, or dependency-integrity failures.
- Security issues, leaked secrets, unsafe authorization/input handling, or vulnerable dependency changes.
- Material architecture, reliability, data-migration, configuration, observability, concurrency, or performance faults relevant to the change.
- Unrelated scope expansion or unsafe self-repair changes.

### Independent Evidence for Code Review

| Evidence | Use |
|---|---|
| CI build, targeted tests, full regression, linters, SAST, secret scan, dependency scan | Detects defects that should make approval impossible. |
| Requirement and test-plan traceability | Confirms that accepted code has evidence for required behavior. |
| Feature Verifier results | Detects cross-story and end-to-end issues missed by story-level review. |
| Human PR review outcomes | Strong calibration evidence for reviewer decisions and findings. |
| Post-merge bugs and security incidents | Delayed but high-value evidence of false approvals. |

### Code Reviewer Outcome Metrics

| Metric | Definition | Desired Direction |
|---|---|---|
| Code approval escape rate | Reviewer-approved diffs with a later major/critical defect found by CI, Test Executor, Feature Verifier, human review, or post-merge investigation / approved diffs. | Lower |
| Critical escape rate | Reviewer-approved diffs with later confirmed critical/security issue / approved diffs. | Near zero |
| CI-after-approval failure rate | Approved diffs that subsequently fail required independent checks / approved diffs. | Lower |
| Feature-verification escape rate | Approved code implicated in a Feature Verifier integration failure / approved code. | Lower |
| Human override rate | AI approvals changed to requests for changes by human PR reviewers, plus AI rejections overturned by humans. | Lower |
| Unnecessary code revision rate | Code sent back by reviewer but adjudicated acceptable / code revision decisions. | Lower |
| Fix verification rate | Prior findings correctly resolved on re-review / valid prior findings. | Higher |

For a code-review model change, `TestPassRate` alone is insufficient. Tests may pass while the reviewer misses security, architecture, test-quality, or untested integration defects.

## Controlled Experiment Protocol

### 1. Freeze the System Under Review

When evaluating a reviewer, change one variable and pin everything else that can change its judgment.

| Field | Examples |
|---|---|
| `ExperimentId` | `code-reviewer-prompt-v4` |
| `ReviewerAgent` | `Plan Reviewer` or `Code Reviewer` |
| `ReviewerModelVersion` | model/deployment/temperature/reasoning settings |
| `ReviewerPromptVersion` | content hash or tagged instruction version |
| `ReviewerContextPackageVersion` | exact allowed artifacts and their content hashes |
| `ReviewerRubricVersion` | scoring rules and gate thresholds |
| `DeterministicCheckVersion` | CI/SAST/traceability policy and tool versions |
| `AdjudicationGuideVersion` | human labeling standard |
| `RepositoryCommit` | source revision used by a plan or diff fixture |
| `FixtureId` | benchmark artifact identifier |
| `TokenSource` | `Reported` or `Estimated` |

For example, to test a Code Reviewer prompt change, hold its model, context package, rubric, benchmark diffs, deterministic checks, and adjudication guide constant. Do not also change the Coder or CI configuration.

### 2. Build Reviewer Benchmarks

Maintain separate, versioned plan and code review suites. Each artifact must contain both clean and defective examples. Include known defects that are easy, moderate, and difficult to detect.

The suites should include:

- Correct artifacts that should be approved, to measure false rejections.
- Missing acceptance-criterion coverage.
- Invalid paths, commands, dependencies, and assumed repository facts.
- Architecture/layer violations and scope creep.
- Missing error paths, migrations, configuration, or integration work.
- Ineffective tests and behaviorally wrong implementations whose superficial tests pass.
- Security, secret, authorization, and dependency-risk examples.
- Re-review cases with a mixture of fixed and unfixed prior findings.
- Deliberately ambiguous cases that humans mark as `needs human escalation`, not simply approve/reject.

Seed the suite with historical incidents, human PR review comments, and escaped defects. Keep a held-out set that is not used to tune the reviewer prompt.

Start with 50-100 adjudicated examples per reviewer. Use a stratified sample so that ordinary clean artifacts do not hide poor recall for rare critical issues.

### 3. Run Blind, Paired Comparison

Run the baseline and candidate reviewer on the exact same artifact and deterministic evidence. Randomize output order for human evaluation and hide the treatment identity.

Compare:

- Decision: approve, revise/changes requested, or escalate.
- Matched findings and severity.
- Dimension scores and total score.
- Invalid, duplicate, vague, and non-actionable findings.
- Latency and cost.

Use a separate human adjudicator, or the fixed pre-adjudicated label, to determine which reviewer was correct. Do not ask the reviewer to grade itself.

### 4. Promotion Criteria

Define promotion before observing results. A reviewer candidate should be promoted only when all conditions below hold on the held-out benchmark and continue to hold in a monitored production sample:

1. Critical/major finding recall improves, or remains at least as high as baseline.
2. Critical/major precision does not decline by more than an agreed small tolerance.
3. Approval escape rate does not increase; critical approval escapes remain zero on the benchmark.
4. Unnecessary revision rate does not increase materially.
5. Score calibration and decision-to-gate consistency do not regress.
6. At least one independent downstream signal improves or remains stable: plan-gap escape, CI-after-approval failure, Feature Verifier escape, human override, or post-merge defects.
7. Cost and latency remain within the stated operating budget, unless an explicit risk reduction justifies the increase.

There is no universally correct threshold. A security-focused Code Reviewer may accept more false positives to achieve higher critical recall. Record that policy explicitly rather than allowing it to emerge accidentally from prompt wording.

## Production Monitoring and Root Cause Attribution

Benchmarks test known examples. Production monitoring tests whether the reviewer remains useful under changing repositories and story types.

For every later defect found after an approval, record:

- The artifact and reviewer run that approved it.
- Defect severity and discovery stage.
- Whether the defect was in the reviewer's allowed scope and visible context.
- Whether the reviewer had enough evidence to detect it.
- Whether the defect traces to a planner, Coder, reviewer, test environment, or context-bundle failure.
- Whether the issue was genuinely new or was introduced after the reviewed artifact changed.

Only count a defect as a reviewer false approval when it was within scope, visible in the reviewer input, and should reasonably have been detected under the documented rubric. This keeps the metric fair and makes root causes actionable.

## Recommended Reviewer Output Format

Require structured output so findings can be matched and adjudicated:

```yaml
review:
  reviewer: Code Reviewer
  rubric_version: code-review-v1
  decision: CHANGES_REQUESTED
  scores:
    behavior_and_plan_adherence: 2
    tests: 3
    architecture: 4
    security: 4
  total_score: 72
  gate_consistent: true
  findings:
    - id: CR-001
      severity: major
      rubric_dimension: behavior_and_plan_adherence
      artifact_reference: src/orders/handler.ts:42
      evidence: "The cancellation path returns success before the repository call and never deletes the order."
      required_change: "Perform deletion before returning success and add the planned cancellation test."
      actionable: true
  prior_findings:
    - id: CR-000
      disposition: addressed
```

The equivalent Plan Reviewer output should reference plan sections, steps, test IDs, files, and commands rather than code lines.

## Minimal Reviewer Dashboard

Show Plan Reviewer and Code Reviewer metrics separately, grouped by reviewer model, prompt, context package, rubric version, and deterministic-check version:

1. Critical/major finding precision and recall on the adjudicated benchmark.
2. Approval escape rate and unnecessary revision rate.
3. Decision accuracy, severity agreement, and score calibration by score band.
4. Invalid/duplicate/non-actionable finding rate and review-thrash rate.
5. Plan-gap, CI-after-approval, Feature Verifier, human override, and post-merge escape rates.
6. Review cost and latency.

Do not rank reviewers by average score assigned or findings generated. Rank them by the risk they prevent, the unnecessary work they avoid, and the quality of the evidence they provide.

## Adoption Sequence

1. Define a shared human-adjudication guide and structured finding schema.
2. Build separate plan and code review benchmark sets, including clean artifacts and seeded known defects.
3. Pin reviewer inputs, rubric, deterministic checks, and adjudication guide while comparing one reviewer treatment at a time.
4. Add precision, recall, false-approval, false-rejection, calibration, cost, and latency measurements.
5. Monitor downstream escapes with fair root-cause attribution and periodically add confirmed incidents to the held-out benchmark after evaluation.

Changing a reviewer without an independent reference set only tells you that its behavior changed. It does not tell you whether its judgment improved.