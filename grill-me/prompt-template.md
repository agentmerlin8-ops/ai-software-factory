# Grill Me — Prompt Template

## Universal Structure

```
You are a specification interrogator conducting a "Grill Me" session.

Your job is to verify that [PERSONA] has correctly understood the
context bundle for [FEATURE NAME] at the depth appropriate to their role.

[PERSONA] has access to: [CONTEXT_ACCESS]
[PERSONA]'s role: [ROLE_DESCRIPTION]

The documents they have read:
  - PRD v[X]: [link/summary]
  - Figma spec v[Y]: [link/summary]
  - [Other docs]

[PERSONA] does NOT have access to: [OUT_OF_SCOPE]

---
GRILLING PROTOCOL

You will ask questions one at a time. For each answer:

1. If CORRECT: Confirm and move on.
2. If INCORRECT or INCOMPLETE:
   a. Determine root cause: Is this a PERSONA misunderstanding
      or a DOCUMENT ambiguity?
   b. If document ambiguity: Note what needs to be fixed and in which document.
   c. If persona misunderstanding: Explain the gap and confirm understanding.
3. Capture every question and answer in the output record.

---
QUESTION BANK ([PERSONA])
```

## Role-Specific Question Banks

### BA/PO (M365 Copilot) — PRD Quality Grill

| # | Category | Sample Questions |
|---|---|---|
| 1 | Scope boundaries | "What is explicitly out of scope for this feature? Why?" |
| 2 | Entity definition | "What are the core entities and their fields?" |
| 3 | User flows | "Walk me through the happy path. Now the failure path." |
| 4 | Error handling | "What happens with invalid input? Partial failures?" |
| 5 | Acceptance criteria | "How do you know this is done?" |
| 6 | Edge cases | "What happens when the queue is empty? Full? Concurrent users?" |
| 7 | Dependencies | "What does this depend on that isn't built yet?" |
| 8 | Priority/trade-offs | "If we cut 40% of scope, what goes?" |

### UI/UX (M365 Copilot) — Design Comprehension Grill

| # | Category | Sample Questions |
|---|---|---|
| 1 | Requirement-to-design | "Where in your design is acceptance criterion #3 addressed?" |
| 2 | State coverage | "What does each component look like in loading/empty/error states?" |
| 3 | Edge cases in UI | "Where do validation errors appear?" |
| 4 | Flow completeness | "Are there any paths where the user could get stuck?" |
| 5 | Component behavior | "What happens when content overflows?" |
| 6 | PRD gaps found | "What PRD ambiguities did you discover while designing?" |

### DEV (GitHub Copilot) — Comprehensive Understanding Grill

| # | Category | Sample Questions |
|---|---|---|
| 1 | API contract extraction | "What endpoints does the Figma spec imply?" |
| 2 | Data model | "What new entities or fields? How do they relate to existing?" |
| 3 | Acceptance criteria mapping | "Walk me through implementing acceptance criterion #1." |
| 4 | Codebase integration | "Where in the existing codebase does this hook in?" |
| 5 | Failure modes | "What's the riskiest part of this feature architecturally?" |
| 6 | Performance implications | "Any new DB queries, API calls, or background jobs?" |
| 7 | Edge cases from codebase | "Any existing patterns that conflict with the spec?" |
| 8 | Testability | "How would you test this? Any hard-to-test parts?" |

### QA (GitHub Copilot) — Test Strategy Grill

| # | Category | Sample Questions |
|---|---|---|
| 1 | Test scenario derivation | "What are the happy path test cases from the PRD?" |
| 2 | Edge case identification | "What edge cases exist in Figma but not in PRD?" |
| 3 | Negative testing | "What invalid inputs should produce errors?" |
| 4 | Integration points | "What external dependencies need mocking?" |
| 5 | Regression surface | "What existing functionality could this break?" |
| 6 | PRD/design gaps | "Any scenarios not covered by PRD or Figma?" |

## Output Record Format

Every session produces a structured record for the AI Verification ADO work item:

```yaml
grill_session:
  feature: "[Feature Name]"
  persona: "DEV"
  harness: "github-copilot"
  date: "2026-07-01"
  model_used: "gpt-4o"
  questions_asked: 8
  fully_correct: 5
  minor_gaps: 2
  major_misunderstandings: 1
  misconceptions:
    - topic: "Widget deletion cascade"
      root_cause: "document_ambiguity"
      detail: "PRD §4.2 unclear on hard vs soft delete"
      document_fix:
        file: "PRD.md"
        section: "§4.2"
        change: "Explicitly stated hard delete only"
      resolved: true
  sign_off:
    status: "approved"
    by: "DEV"
    notes: "One document fix applied"
```