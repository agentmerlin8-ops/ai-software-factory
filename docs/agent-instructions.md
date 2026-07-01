# Agent Instructions Template

Guidelines for writing effective GitHub Copilot `.agent.md` instruction files for the software factory.

## File Format

Each agent is a markdown file with YAML frontmatter:

```yaml
---
name: Agent Name
description: Brief description shown in Copilot dropdown
tools:
  - search/codebase
  - read/*
  - edit/*
user-invocable: false   # Hide from dropdown (subagent only)
---
# Agent instructions
```

## Required Sections

### 1. Identity & Role
Who is this agent? What is its single responsibility?

```markdown
# {Agent Name} Agent

You are the **{Agent Name}** — {one-sentence role}.
Your job is to {specific deliverable}.
```

### 2. Inputs
What does this agent read? Be specific about file paths.

```markdown
## Your Inputs

- File: `path/to/input.md` — Description
- File: `docs/relevant-doc.md` — Relevant sections
- You do NOT see: {what's intentionally excluded}
```

### 3. Output
Where does the output go? What format?

```markdown
## Your Output

Write to: `stories/STORY-{NNN}/output-name.md`
```

### 4. Rules
Hard rules the agent must follow.

### 5. Quality Checklist
Checklist the agent verifies before producing output.

### 6. Anti-Patterns
What NOT to do, with alternatives.

## Tool Scoping Per Role

| Agent | Tools | Why |
|---|---|---|
| Orchestrator | `agent`, `search/*`, `read/*`, `edit/*` | Delegates, reads context, writes state |
| Planners/Reviewers | `search/*`, `read/*`, `edit/*` | Read context, write plan/review files |
| Coder/Test Executor | `search/*`, `read/*`, `edit/*`, `terminal/*` | Write code, run builds/tests |

## Context Isolation for Reviewers

Add `disable-model-invocation: true` to Plan Reviewer and Code Reviewer to prevent other agents from calling them and to ensure they run in fresh context.

```yaml
---
name: Plan Reviewer
description: Reviews plans in fresh context.
tools:
  - search/codebase
  - search/files
  - read/*
  - edit/*
user-invocable: false
disable-model-invocation: true
---
```

## Waza Quality Dimensions

Microsoft's Waza framework scores agent instructions on 5 dimensions:

1. **Clarity** — Is the instruction unambiguous?
2. **Completeness** — Does it cover all scenarios?
3. **Trigger Precision** — When does this agent activate?
4. **Scope** — Does it stay in its lane?
5. **Anti-patterns** — Are there common mistakes the agent avoids?

Run `waza quality agents/<agent-name>/` to score and iterate.

## Anti-Patterns

| Don't | Do Instead |
|---|---|
| Vague instructions ("follow best practices") | Explicit rules, exact commands |
| Duplicate agent definitions in skills/ and .agent.md | Single source of truth in `.github/agents/` |
| Pass full context bundle to every agent | Each agent receives only relevant sections |
| Allow unlimited revision loops | Max 2 per stage, then escalate |
| Skip state tracking | Maintain state.md, update after each stage |
| Contradictory issue-handling rules | ONE consolidated rule: STOP → report → wait |