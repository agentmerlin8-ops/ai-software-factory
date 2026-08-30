# Context Bundle — {PROJECT}

Four documents define WHAT gets built. The factory will not decompose until these pass the quality gate (score ≥ 70).

## docs/prd.md — Product Requirements (BA/PO)
- Functional requirements (numbered FR-1…)
- Acceptance criteria per requirement (Given/When/Then)
- Success metrics
- Explicit in/out of scope

## docs/architecture.md — Engineering Design (DEV)
- Layering / clean architecture boundaries
- Data model (tables, key fields)
- API contract (endpoints, DTOs)
- External integrations + auth posture
- Known open questions → MUST be resolved before the pipeline starts

## docs/ui-design.md — Interface Spec (UI/UX)
- Screens and component hierarchy
- User flows
- States (empty, loading, error, success)
- API contract as consumed by the UI (must match architecture.md)

## docs/test-strategy.md — Test Strategy (QA)
- Test pyramid targets
- What gets unit / integration / e2e coverage
- Mocking strategy for external services
- Coverage targets and anti-patterns

## Cross-document rules
- API contracts must agree between ui-design.md and architecture.md field-for-field
- Every PRD requirement must be traceable to a test in test-strategy.md
- Grilling (comprehension verification) happens BEFORE decomposition — document ambiguities get fixed and versioned here
