# Grill Me — Role-Specific Understanding Verification

A structured process to verify that each persona has understood the context bundle at the depth appropriate to their role, memorialize the results, and feed misconceptions back into document improvements.

---

## How It Works

Each persona runs a role-specific "Grill Me" session in their native harness. The AI interrogates them on the specific knowledge points they need to understand from the context bundle. If a misconception surfaces, the root cause is identified (persona misunderstanding vs. document ambiguity), the document is fixed, and the resolution is captured in the audit trail.

> **Scores are learning telemetry, not performance metrics.** Grill sessions run in the persona's own harness with the documents open — they are trivially gameable by anyone motivated to game them. If scores are used for individual performance evaluation, people will optimize for passing rather than understanding, and the signal is destroyed (Goodhart's law). Use the scores to improve *documents and templates* (see Continuous Improvement below), never to rank people. State this explicitly to every participant.

```
PRD drafted by BA/PO
    │
    ├──▶ [Grill: PRD Quality]      ← BA/PO in M365 Copilot
    │       PRD refined
    │
    ├──▶ [Grill: UI/UX Understanding]  ← UI/UX in M365 Copilot
    │       Reads PRD, validates against Figma
    │
    ├──▶ [Grill: DEV Understanding]    ← DEV in GitHub Copilot
    │       Reads PRD + Figma + existing codebase
    │
    └──▶ [Grill: QA Understanding]     ← QA in GitHub Copilot
            Reads PRD + Figma
    │
    ▼
All-persona sign-off → To Factory
```

---

## 1. Persona & Harness Matrix

| Persona | Harness | Context Access | Reads | Produces |
|---|---|---|---|---|
| **BA/PO** | M365 Copilot | Documents only. No code. | Their own PRD draft | Refined PRD + comprehension record |
| **UI/UX** | M365 Copilot | Design docs + PRD. No code. | PRD + their own Figma | Comprehension record |
| **DEV** | GitHub Copilot (VS Code) | Full codebase + docs. | PRD + Figma spec + existing repo | Comprehension record |
| **QA** | GitHub Copilot (VS Code) | Docs + test infrastructure. | PRD + Figma spec | Comprehension record |

---

## 2. The Grill Me Prompt Template (Parameterized by Role)

Each persona gets the same core structure, but the question bank shifts. Below is the universal template, followed by role-specific question banks.

### Universal Structure

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

### Output Record

Every session produces a structured output:

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
      root_cause: "document_ambiguity"  # or "persona_misunderstanding"
      detail: "DEV thought soft delete was permitted. PRD §4.2 says hard delete."
      document_fix:
        file: "PRD.md"
        section: "§4.2 Deletion Behavior"
        change: "Added explicit statement: 'Hard delete only. No recovery.'"
      resolved: true
  
  sign_off:
    status: "approved"  # or "needs_revision"
    by: "DEV"
    notes: "One document fix applied, no re-grill needed."
```

---

## 3. Role-Specific Question Banks

### BA/PO — PRD Quality Grill (M365 Copilot)

*Purpose: Ensure the PRD is complete, unambiguous, and the author has thought through edge cases.*

Context available: The PRD document only.
No access to: Code, Figma designs, eng design.

| # | Question Category | Sample Questions |
|---|---|---|
| 1 | **Scope boundaries** | "What is explicitly out of scope for this feature? Why?" |
| 2 | **Entity definition** | "What are the core entities? What fields does each have? Are there any entities you considered adding but excluded?" |
| 3 | **User flows** | "Walk me through the main happy path from start to finish. Now walk me through the failure path." |
| 4 | **Error handling** | "What happens when the system receives invalid input? What about partial failures?" |
| 5 | **Acceptance criteria** | "How do you know this feature is done? What's the success metric?" |
| 6 | **Edge cases** | "What happens when the queue is empty? Full? What about concurrent users?" |
| 7 | **Dependencies** | "What does this feature depend on that isn't built yet? What's the fallback if that dependency fails?" |
| 8 | **Priority/trade-offs** | "If we had to cut scope by 40%, what goes? If we doubled the timeline, what would you add?" |

**Goal:** Expose vague language, unstated assumptions, and missing edge cases. The BA/PO must *defend* their decisions, not just restate them.

**Structural limitation & mitigation:** With only the PRD as context, the AI can probe *ambiguity* but cannot detect *wrong requirements* — it knows nothing the document doesn't say. Mitigate by generating questions from the **other personas' perspectives**: "What will the developer need to know that this document doesn't say?", "What will the designer have to assume?", "What will QA be unable to test as written?" This forces the PRD to be evaluated against its downstream consumers, not against itself.

---

### UI/UX — Design Comprehension Grill (M365 Copilot)

*Purpose: Verify the designer correctly interpreted the PRD requirements and can articulate how the design addresses them.*

Context available: PRD + their own Figma designs.
No access to: Code, eng design.

| # | Question Category | Sample Questions |
|---|---|---|
| 1 | **Requirement-to-design mapping** | "Show me where in your design you've addressed acceptance criterion #3 from the PRD." |
| 2 | **State coverage** | "What does each component look like in: loading state? empty state? error state? success state?" |
| 3 | **Edge cases in UI** | "What happens when the user submits a form with invalid data? Where do validation errors appear?" |
| 4 | **Flow completeness** | "Walk me through the complete user journey. Are there any paths where the user could get stuck?" |
| 5 | **Component behavior** | "What happens when content overflows its container? Long text? Missing images?" |
| 6 | **PRD gaps caught by design** | "Did you find anything in the PRD that was ambiguous while designing? What did you assume to move forward?" |

**Goal:** Surface where the PRD was ambiguous enough that the designer had to fill gaps with assumptions. Those assumptions go back into the PRD.

---

### DEV — Comprehensive Understanding Grill (GitHub Copilot)

*Purpose: Verify the developer understands the full feature contract — PRD requirements, Figma API implications, codebase integration points, and failure modes.*

Context available: PRD + Figma spec + existing codebase (via repo context in Copilot).
No access to: (Has full context.)

| # | Question Category | Sample Questions |
|---|---|---|
| 1 | **API contract extraction** | "Based on the Figma spec, what API endpoints does the frontend expect? What are the request/response shapes?" |
| 2 | **Data model** | "What new entities or fields does this feature introduce? How do they relate to existing entities in the codebase?" |
| 3 | **Acceptance criteria mapping** | "Walk me through how you would implement acceptance criterion #1. Which files would you touch? What's your approach?" |
| 4 | **Codebase integration** | "Where in the existing codebase does this feature hook in? What existing services or repositories need modification?" |
| 5 | **Failure modes** | "What could go wrong during implementation? What's the riskiest part of this feature architecturally?" |
| 6 | **Performance implications** | "Does this feature introduce any new database queries, API calls, or background jobs? What's the expected load?" |
| 7 | **Edge cases from codebase** | "Are there existing patterns or constraints in the codebase that might conflict with the PRD or Figma spec?" |
| 8 | **Testability** | "How would you test this? Are there parts that are hard to test given the existing test infrastructure?" |

**Goal:** Catch missing details in the eng design before a single line of code is written. The dev should be able to mentally execute the feature before touching the keyboard.

---

### QA — Test Strategy Understanding Grill (GitHub Copilot)

*Purpose: Verify the QA engineer can derive test scenarios from the PRD + Figma, identify edge cases the author and designer missed, and assess testability.*

Context available: PRD + Figma spec. Optionally existing test infrastructure.
No access to: Eng design details (deliberate — QA should derive tests from spec, not implementation).

| # | Question Category | Sample Questions |
|---|---|---|
| 1 | **Test scenario derivation** | "From the PRD acceptance criteria, what are the happy path test cases? How many scenarios does each criterion require?" |
| 2 | **Edge case identification** | "What edge cases exist in the Figma designs that aren't mentioned in the PRD? What about the reverse?" |
| 3 | **Negative testing** | "What invalid inputs or state transitions should produce errors? How should the system behave for each?" |
| 4 | **Integration points** | "What external dependencies does this feature have? How would you mock or stub them for testing?" |
| 5 | **Regression surface** | "What existing functionality could this feature break? How would you detect regression?" |
| 6 | **PRD/design gaps** | "Did you find any scenarios that aren't covered by either the PRD or the Figma spec? What did you assume?" |

**Goal:** Surface gaps in the test plan before implementation. QA should be able to write tests before the code exists (TDD in the large).

---

## 4. The Misconception → Document Fix Loop

This is the key value-add. When a grilling session reveals a gap, it's not just noted — it triggers a document fix.

```
Grill session reveals gap
    │
    ├── Is it a persona misunderstanding?
    │   Yes → Educate persona, note in record. No document change needed.
    │
    └── Is it a document ambiguity?
        Yes → Which document?
            │
            ├── PRD → BA/PO fixes PRD → re-grill only if major
            ├── Figma → UI/UX fixes spec → re-grill only if major
            └── Eng Design → DEV fixes design → re-grill only if major
    
    ▼
Updated document is versioned
Misconception record links to the fix (ADO work item comment)
```

**Rule of thumb:** Minor fixes (typos, clarifications) → fix and move on. Major fixes (architectural changes, scope additions) → re-grill the affected persona.

---

## 5. ADO Integration (Audit Trail)

Each grilling session creates or updates an ADO work item under the feature epic:

```yaml
Work Item: "Grill: DEV Comprehension — Podcast Ingestion Engine"
Type: AI Verification (custom work item type)
Parent Feature: "Podcast Ingestion Engine"

Fields:
  Persona: DEV
  Harness: github-copilot
  Questions Asked: 8
  Fully Correct: 5
  Misunderstandings: 1
  Document Fixes Triggered: 1
  Sign-off Status: Approved
  Model Used: gpt-4o
  Date: 2026-07-01

History (auto-logged by ADO):
  - Question 1: Correct ✅
  - Question 2: Minor gap → PRD clarified §4.2
  - Question 3: Correct ✅
  - ...
  - Sign-off: Approved by DEV
```

The work item history *is* the audit trail. No separate system needed.

---

## 6. Continuous Improvement

Over time, the grilling records reveal patterns:

| Pattern | What It Means | Action |
|---|---|---|
| DEV consistently misunderstands the same PRD section | PRD section is poorly written | Fix the template for that section type |
| UI/UX repeatedly finds PRD ambiguities | PRD lacks UI-specific detail | Add a "UI States" section to PRD template |
| QA finds edge cases the PRD missed | PRD author isn't thinking about errors | Add "Edge Cases" checklist to PRD review |
| One persona always passes with no gaps | Maybe the questions are too easy for that role | Rotate/introduce harder questions |

The question banks evolve. The process gets sharper. The grilling gets more effective over time.

---

## Summary

```
PRD drafted → [Grill: BA/PO] → refined PRD
                              → UI/UX reads PRD → designs Figma → [Grill: UI/UX]
                                                                    ↓
                              → DEV reads PRD + Figma → [Grill: DEV]
                                                          ↓
                              → QA reads PRD + Figma → [Grill: QA]
                                                          ↓
                              → Sign-off → To Factory
                                             ↓
                              Misconception records feed back into docs
                              ADO work items capture the full audit trail
```