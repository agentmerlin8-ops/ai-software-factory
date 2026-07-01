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

Approved features enter an 8-agent automated pipeline:

```
Story Decomposition → Test Plan Generation → Implementation Plan
    → Plan Review (fresh context, no anchoring bias)
    → Code Generation → Code Review
    → Test Execution → Approved | Blocked
```

Each stage has a maximum of 2 revision loops before escalating to a human. Every artifact is a markdown file in the repo — auditable, version-controlled, and comparable across model runs.

## ADO Integration

All state is tracked in Azure DevOps using two custom work item types:

- **AI Story** — One per decomposed story. 8 states (Drafted → In Planning → Plan Review → In Coding → Code Review → In Testing → Approved | Blocked). 10 custom fields for pipeline state.
- **AI Verification** — One per Grill Me session per persona. 4 states (Pending → In Progress → Completed | Needs Revision). 14 custom fields capturing scores, misconceptions, and triggered document fixes.

The work item history *is* the audit trail. No separate system needed.

## Repository Structure

```
ai-software-factory/
├── LICENSE                 # MIT — do whatever you want with this
├── README.md               # This file
├── docs/
│   ├── research-landscape.md   # Landscape analysis of the OSS software factory space
│   ├── architecture.md         # The 8-agent pipeline architecture
│   ├── context-bundle.md       # Templates for PRD, UI/UX, Arch, Test Strategy docs
│   └── agent-instructions.md   # How to write effective agent instructions
├── grill-me/
│   ├── process.md              # The full Grill Me process specification
│   └── prompt-template.md      # Role-specific grill prompt templates
├── ado/
│   ├── design-spec.md          # Complete ADO work item type design
│   └── setup.py                # Python script to create ADO process customizations
├── agents/
│   └── *.agent.md              # GitHub Copilot agent instruction files
└── .github/agents/
    └── *.agent.md              # Same agents (Copilot discovery path)
```

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