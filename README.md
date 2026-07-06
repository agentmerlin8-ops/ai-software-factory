# AI Software Factory

A structured, multi-persona process for building software with AI agents — from specification through comprehension verification, to automated development and deployment.

## What This Is

The AI Software Factory is a **process framework** for producing high-quality software using AI coding agents. It solves two fundamental problems:

1. **Shared understanding** — Ensuring every stakeholder (PO, designer, developer, QA) truly understands the feature before a line of code is written
2. **Structured production** — Running specifications through a verifiable multi-agent pipeline with quality gates

## The Core Insight

The biggest failure mode in AI-assisted development isn't the AI — it's that **humans don't read the documents**. A developer skimming a PRD and making assumptions will produce bad code regardless of how good the AI model is.

Our solution: **role-specific comprehension verification** ("Grill Me") sessions that force each persona to demonstrate understanding at the depth appropriate to their role, before any code is generated.

## How It Works

### Phase 1: Context Bundle Assembly

Four personas contribute structured documents that define what to build:

| Persona | Document | Tool |
|---|---|---|
| **BA/PO** | PRD (requirements, acceptance criteria, scope) | M365 Copilot |
| **UI/UX** | Figma spec (user flows, states, API contract) | M365 Copilot |
| **DEV** | Engineering Design (architecture, data model) | GitHub Copilot |
| **QA** | Test Strategy (test approach, coverage targets) | GitHub Copilot |

### Phase 2: Grill Me — Comprehension Verification

Each persona gets grilled by an AI on their specific understanding of the relevant documents:

```
PRD drafted by BA/PO
    │
    ├──▶ [Grill: PRD Quality]  ← BA/PO defends/refines the PRD
    │
    ├──▶ UI/UX reads PRD → Figma → [Grill: UI/UX Understanding]
    │
    ├──▶ DEV reads PRD + Figma → Eng Design → [Grill: DEV Understanding]
    │
    ├──▶ QA reads PRD + Figma → Test Plan → [Grill: QA Understanding]
    │
    ▼
All-persona sign-off → Approved → To Factory Pipeline
```

Every misconception surfaces either:
- A **persona misunderstanding** (addressed through education)
- A **document ambiguity** (triggers a document fix, creating a closed feedback loop)

### Phase 3: Factory Pipeline

Approved features enter an 8-stage automated pipeline orchestrated by a 9th Orchestrator agent:

```
Story Decomposition (+ bundle quality gate)
    → Test Plan Generation → Implementation Plan
    → Plan Review (fresh context, no anchoring bias)
    → Code Generation (story branch + PR) → Code Review
    → Test Execution → self-repair loop on failure (max 2)
    → Feature Verification (end-to-end vs. PRD)
    → Human merges PRs → Done
```

Every failure mode has an automated repair loop (max 2 per stage) before escalating to a human. All pipeline artifacts (test plans, implementation plans, code review findings, test results) are stored as fields on ADO work items — not committed to the repository. Code lands on `story/{id}` branches via pull requests; **a human merging the PRs is the final quality gate**.

The Orchestrator creates one **AI Agent Run** work item per agent invocation, capturing model used, agent version, token counts, estimated cost, duration, quality score, and the full artifact output. All ADO bookkeeping flows through a deterministic layer — the LLM decides, validated code writes.

## ADO Integration

All state and artifacts are tracked in Azure DevOps using three custom work item types:

- **AI Story** — One per decomposed story. 8 states (Drafted → In Planning → Plan Review → In Coding → Code Review → In Testing → Approved | Blocked). Fields store all pipeline artifacts: StoryContext, TestPlan, ImplPlan, TestResults, CodeReviewFindings. Aggregate observability fields roll up quality scores and total cost from child Agent Runs.
- **AI Verification** — One per Grill Me session per persona. 4 states (Pending → In Progress → Completed | Needs Revision). 14 custom fields capturing scores, misconceptions, and triggered document fixes.
- **AI Agent Run** — One per agent invocation. 3 states (Running → Completed | Failed). Captures: AgentName, ModelUsed, InputTokens, OutputTokens, EstimatedCostUSD, DurationSeconds, QualityScore, StageDecision, and the full ArtifactContent. Every child of its parent AI Story.

The work item history *is* the audit trail. No separate system needed.

## Observability

The AI Agent Run work items enable continuous factory improvement:

- **Cost tracking** — Every token spent, every dollar, per agent and per model (with token source flagged: exact vs. estimated)
- **Quality tracking** — Rubric-anchored quality scores (0–100) per planning and review stage, with objective metrics (test pass rate, revision counts) as ground truth
- **Model comparison** — Run batches with different models while keeping the reviewer model pinned; compare scores and cost in ADO dashboards
- **Value anchoring** — Estimated human hours per story turn raw cost into a cost-vs-value ratio for stakeholders
- **Bottleneck detection** — Identify which agents generate the most revision loops; tune per-stage loop limits from data
- **Attribution** — Agent instruction versions are tracked per run, so quality changes can be attributed to prompt tuning vs. model changes

See `ado/design-spec.md` Section 10 (measurement calibration rules) and Section 11 (dashboard widgets and WIQL query templates).

## Repository Structure

```
ai-software-factory/
├── LICENSE                 # MIT — do whatever you want with this
├── README.md               # This file
├── docs/
│   ├── research-landscape.md   # Landscape analysis of the OSS software factory space
│   ├── architecture.md         # The 9-agent pipeline architecture
│   ├── context-bundle.md       # Templates for PRD, UI/UX, Arch, Test Strategy docs
│   └── agent-instructions.md   # How to write effective agent instructions
├── grill-me/
│   ├── process.md              # The full Grill Me process specification
│   └── prompt-template.md      # Role-specific grill prompt templates
├── ado/
│   ├── design-spec.md          # Complete ADO work item type design (AI Story, AI Verification, AI Agent Run)
│   └── setup.py                # Python script to create ADO process customizations
├── agents/
│   └── *.agent.md              # GitHub Copilot agent instruction files
└── .github/agents/
    └── *.agent.md              # Same agents (Copilot discovery path)
```

> **Note:** Story artifacts (test plans, impl plans, reviews, test results) are stored in ADO work item fields — not in this repository. Only code and agent instruction files are committed to git.

## Environment

This factory is designed for **locked-down client environments**:
- **Runtime:** VS Code devcontainer with GitHub Copilot
- **Models:** Azure AI Foundry (DeepSeek V4 Flash/Pro, GPT-4o, others)
- **State:** Azure DevOps (custom work item types)
- **Code:** Git + GitHub (PR-based workflow)
- **Design:** Figma (exported specs)

## Getting Started

1. Clone this repo
2. Set up an inherited process from "Basic" in your ADO org
3. Run `ado/setup.py` to create the custom work item types
4. Read `grill-me/process.md` to understand the comprehension verification flow
5. Load the `.agent.md` files into GitHub Copilot
6. Start with a PRD and walk through the process

## License

MIT — fully open source. Use it, adapt it, contribute back.