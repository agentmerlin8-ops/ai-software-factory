# Context Bundle Templates

Templates for the four input documents that make up the context bundle.

## 1. PRD (`docs/prd.md`)

### Required Sections
- Executive Summary
- Functional Requirements (numbered FR-X.X) — each with Given/When/Then acceptance criteria
- Non-Functional Requirements
- Out of Scope
- Success Criteria (checklist)
- Assumptions
- Dependencies

### Acceptance Criteria Format

```
*Scenario: {Happy path}*
- **Given** {precondition}
- **When** {action}
- **Then** {outcome}

*Scenario: {Error/edge case}*
- **Given** {precondition}
- **When** {action}
- **Then** {outcome}
```

Every requirement needs at least 2-3 scenarios: happy path, error, edge case.

## 2. UI/UX Design (`docs/ui-design.md`)

### Required Sections
- User Flows (numbered steps)
- Component Hierarchy (tree diagram)
- Component Specifications (props, states, wireframes)
- API Contract (TypeScript interfaces matching the frontend data model)
- Integration Notes (polling, proxy, error handling)

## 3. Architecture (`docs/architecture.md`)

### Required Sections
- Architecture Overview (ASCII diagram)
- Layers (Domain, Application, Infrastructure, Web)
- Data Model (entities + schema)
- API Design (endpoints with request/response)
- External Integrations (API clients, auth, rate limiting)
- Background Services
- Dependency Injection
- Configuration
- Docker Compose

## 4. Test Strategy (`docs/test-strategy.md`)

### Required Sections
- Testing Philosophy
- Test Pyramid (unit/integration/E2E ratios)
- Test Categories (with code examples)
- Test Data Management
- Code Quality Tools
- Test Execution Commands
- Anti-Patterns

## Cross-Document Consistency Checklist

Before finalizing the context bundle:

- [ ] Entity names identical across all 4 documents
- [ ] API paths in PRD match API Design in Architecture
- [ ] API contract in UI/UX matches API response format in Architecture
- [ ] Test Strategy references same frameworks/layers as Architecture
- [ ] Out-of-scope in PRD is respected by Architecture
- [ ] Success criteria in PRD are testable per Test Strategy