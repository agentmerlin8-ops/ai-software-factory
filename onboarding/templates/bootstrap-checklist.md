# Brownfield Bootstrap Checklist

Existing code detected. Before the pipeline decomposes anything, capture the repo's reality into the context bundle — the agents must never assume conventions they haven't been told.

## Capture before decomposing

- [ ] **Build command** — exact command, SDK version, where it lives (`docs/architecture.md`)
- [ ] **Test command** — exact command, how to run a single test, known-flaky tests
- [ ] **Run command** — how the app starts locally; ports; env vars
- [ ] **Frameworks & versions** — language runtime, frameworks, major libraries
- [ ] **Conventions** — naming, folder layout, DI pattern, error handling style
- [ ] **Existing tests** — coverage state, test framework, fixtures/mocks in use
- [ ] **CI** — what runs on push/PR, required checks
- [ ] **Known debt** — broken things, TODOs, areas NOT to touch

## Boundaries for the pipeline

- [ ] List directories/files that are OFF LIMITS to story implementations
- [ ] List integration points the stories must preserve (public APIs, DB schema compat, config formats)
- [ ] Note any migration policy (schema changes allowed? backward compat required?)

## Context-bundle additions

Brownfield context bundles get one extra document:

- `docs/codebase-map.md` — the capture above, plus a module map with one-line purpose per top-level directory

The Story Decomposer receives `codebase-map.md` alongside the standard bundle so stories respect existing structure.
