# Incremental Story-to-Code Experiments

## Goal

Prove that the factory can take a well-defined story through planning, coding, review, and testing. Then deliberately make that same feature more complex until the factory is no longer reliably producing acceptable results.

For every run, capture enough evidence to answer:

- Did the story pass the factory gates without human code changes?
- How many repair loops were needed?
- What did the AI inference cost to deliver the story?
- Which model, prompt, context package, and settings were used?
- At what story complexity did quality, consistency, cost, or elapsed time become unacceptable?

The immediate experiment target is the benchmark upload application. The existing upload flow already persists file metadata in PostgreSQL, so it is a good controlled starting point.

## Fixed Story Pipeline

Use the existing factory sequence for every experiment:

```text
Test Plan -> Implementation Plan -> Plan Review -> Coder -> Code Review -> Test Execution
```

Run Feature Verification only after a multi-story increment exists. Do not change the pipeline order or let humans silently repair generated code during a measured run. A human may reject a result or clarify the story, but the resulting run is then marked as failed or escalated.

## Starting Story

**Story:** As a user, I want to see a list of the files I uploaded so that I can confirm what has been stored.

**Expected result:** Add a static table to the existing web page that enumerates uploaded files. For this first story, the table content can be hard-coded; it does not need to call the API or reflect new uploads.

**Acceptance criteria:**

1. The page shows a table below the upload experience.
2. The table contains a small static set of uploaded-file rows.
3. Each row shows filename, content type, size, and uploaded date/time.
4. The table has appropriate column headings and remains usable at narrow viewport widths.
5. Existing file upload behavior continues to work.
6. Frontend build and relevant tests pass.

This is intentionally small: one frontend surface, no backend change, no schema change, and no new dependency. It establishes the baseline quality and cost of the story-to-code path before complexity is introduced.

## Complexity Ladder

Each level builds on the previous level. Do not start the next level until the current story has a recorded outcome.

| Level | Incremental story | What it adds |
|---|---|---|
| 1 | Show a static uploaded-files table | Presentational React and CSS change only |
| 2 | Show files from the API | `GET /api/uploads`, API contract, loading/empty/error states |
| 3 | Delete an uploaded file | Delete endpoint, database/blob cleanup, confirmation/error behavior |
| 4 | Sort and filter the file list | Client-side state, query behavior, empty results, interaction tests |
| 5 | Paginate or virtualize a larger file list | API/query contract, performance, state coordination |
| 6 | Combined data grid | Sorting, filtering, delete, pagination, error/retry behavior working together |
| 7 | Multi-story integration scenario | Upload, list, sort/filter, delete, and persistence verified end-to-end |

Each row is a separate story, not one expanding story. This preserves a clean measurement: the complexity change is visible in the acceptance criteria, change surface, tests, and cost.

## One Simple Experiment At A Time

Begin with one baseline factory profile. Keep the same model, inference settings, agent prompts, tool permissions, repository commit, and context package across Levels 1-3 unless the experiment explicitly tests one of them.

For each level:

1. Write the story and acceptance criteria.
2. Run the factory through the fixed pipeline.
3. Record the generated artifacts, pull request diff, test output, review output, and final status.
4. Record direct AI inference cost and elapsed time for every agent invocation.
5. Decide whether the result is acceptable before progressing.

Run each level at least three times from the same starting commit when model output is nondeterministic. Use a clean branch or worktree per run. This reveals whether success was repeatable rather than lucky.

## Minimal Run Record

Store this record with the corresponding ADO AI Story and AI Agent Run items. A simple spreadsheet or Markdown results table is enough for the first experiment; build automation only after the manual process is proven useful.

| Field | Record |
|---|---|
| Experiment and run ID | For example, `upload-list-L1-run-01` |
| Story level | The level from the complexity ladder |
| Starting repository commit | Exact Git SHA |
| Model and deployment | Azure AI Foundry model family, deployment, and provider version if available |
| Inference settings | Temperature, maximum output tokens, reasoning/tool settings when supported |
| Agent prompt versions | Hash or tag of each `.agent.md` file used |
| Context package | Exact inputs supplied to each agent, including relevant file/artifact hashes |
| Token usage and source | Input/output tokens; `Reported` or `Estimated` |
| Per-agent and total AI cost | Calculated from the current Foundry price table |
| Duration | Per agent and complete story elapsed time |
| First-run results | Plan approval, code-review approval, build/test result, revisions |
| Final result | Approved, blocked, or escalated after repair loops |
| Failure notes | Requirement, plan, code, review, test, environment, or context failure |
| Human intervention | Clarification/review time; never silently edit AI output |

Do not combine `Reported` and `Estimated` token data in a cost comparison. Preserve raw provider usage, command output, and the final diff whenever possible.

## Acceptance Gate

A run is acceptable when all of the following are true:

- No critical or security issue is found.
- The generated code builds and passes required checks.
- The Code Reviewer approves the result and its findings are evidence-based.
- The story behaves according to its acceptance criteria.
- No human code repair was required.
- The run stays within the configured maximum of two repair loops per stage.

Track both first-run success and final success. A story that passes after repair is deliverable, but it is not as reliable as a story that succeeds on its first attempt.

The factory has started to struggle when any of these becomes repeated rather than exceptional at a given level:

- A story blocks or needs human code repair.
- First-run build/test or code-review success falls materially across repeated runs.
- Repair loops regularly reach the limit.
- Reviews miss defects later found by testing or feature verification.
- Cost or duration rises sharply without a matching improvement in reliability.

The previous level is then the supported boundary for that factory profile. Record the failure mode before choosing a response: split the story, improve the prompt/context, use a stronger model, or accept that this level needs human implementation.

## Cost Calculation

For each Azure AI Foundry invocation, calculate:

$$
\text{AI Cost} = \frac{\text{input tokens}}{1000} \times \text{input price} + \frac{\text{output tokens}}{1000} \times \text{output price}
$$

The story cost is the sum of all agent invocations, including retries:

$$
\text{Story AI Cost} = \sum \text{agent-run AI costs}
$$

Report the first-run story cost separately from the final story cost. The difference is the cost of repair. Also report human review or clarification time separately; direct inference cost and total delivery effort answer different questions.

## Tuning After A Baseline

Do not tune everything at once. First, complete Levels 1-3 with a single baseline profile. Then use the same story level and starting commit to test one change at a time:

1. **Prompt:** Revise one agent instruction, starting with the Implementation Planner or Coder.
2. **Context:** Compare the minimum approved plan/test inputs with a targeted package of relevant source and test files.
3. **Model:** Compare Azure AI Foundry deployments while holding prompt, context, reviewer, and tests fixed.
4. **Inference settings:** Change temperature, output limit, or reasoning settings only when supported by the selected deployment, with all other inputs fixed.
5. **Tools and repair policy:** Test terminal/search permissions or repair context separately from model and prompt changes.

When evaluating a generator such as the Planner or Coder, pin the Plan Reviewer, Code Reviewer, test commands, environment, and acceptance criteria. Otherwise a changed evaluator or environment can be mistaken for a better model.

Choose a model/profile for an agent only when it produces repeatable acceptable results at the intended level for lower or justified cost. Record the selection as a small matrix:

| Agent | Model/deployment | Settings | Prompt | Context package | Supported levels | Median story cost contribution |
|---|---|---|---|---|---|---:|
| Coder | To be determined | To be determined | Version | Version | L1-L? | $0.00 |

## First Experiment Checklist

1. Capture the current commit of `benchmark-app` as the Level 1 baseline.
2. Create the Level 1 static-table story using the acceptance criteria above.
3. Select one initial Foundry model/configuration per agent and record it before the run.
4. Run the complete story pipeline three times from clean worktrees.
5. Record quality, repair loops, raw test evidence, duration, tokens, and cost for all three runs.
6. Review whether the outputs are consistent enough to proceed to Level 2.
7. Add only the next capability after the Level 1 result is understood.

The first decision is deliberately modest: whether this profile can reliably deliver a small, static React table without breaking the existing upload flow, and what that delivery costs. Everything else follows from that evidence.