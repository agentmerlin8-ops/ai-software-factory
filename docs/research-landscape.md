---
created: 2026-06-30
tags: [research, software-factory, agents, report, landscape]
---

# Software Factory Landscape — Research Report

**Date:** 2026-06-30
**Scope:** Open-source AI software factories, multi-agent coding frameworks, MCP integrations, agent instruction best practices
**Methodology:** GitHub API queries (live star counts), README analysis, cross-reference with existing Obsidian knowledge base

---

## Executive Summary

The software factory space has **exploded in 2025-2026**. We're past the era of single-agent coding tools — the industry has converged on **multi-agent orchestration** as the dominant paradigm, with three distinct tiers emerging:

1. **Mega-frameworks** (10k-185k ⭐) — AutoGPT, MetaGPT, OpenHands, AutoGen, CrewAI — general-purpose agent frameworks that can be adapted for software production
2. **Specialized orchestrators** (500-8k ⭐) — Bernstein, AgentWrapper, FSPEC, Donmai, AIWG — purpose-built for multi-agent coding pipelines, often CLI-agent-native
3. **Minimal agents** (5k+ ⭐) — mini-swe-agent, Agentless — prove that simplicity + great evals beats complexity

**Key finding:** Nobody has yet built the *complete* end-to-end factory that:
- Walks the user through context generation from an existing codebase
- Grills for complete understanding via structured interview
- Sets up ADO, GitHub, and Figma MCP integrations
- Generates custom agents tailored to the specific codebase
- Captures and evolves best practices

This is the gap. **This is our opportunity.**

---

## 1. The Landscape — Star-Sorted (Live Data)

| ⭐ | Project | Description | Language | Updated |
|---|---|---|---|---|
| **185,217** | [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | Accessible AI for everyone | Python | 2026-06 |
| **135,143** | [Claude Code](https://github.com/anthropics/claude-code) | Agentic coding tool in your terminal | (proprietary) | 2026-06 |
| **94,650** | [OpenAI Codex CLI](https://github.com/openai/codex) | Lightweight coding agent in terminal | Python | 2026-06 |
| **87,894** | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | MCP reference server implementations | Multiple | 2026-06 |
| **78,845** | [OpenHands](https://github.com/All-Hands-AI/OpenHands) | AI-driven development | Python | 2026-06 |
| **69,128** | [MetaGPT](https://github.com/FoundationAgents/MetaGPT) | First AI Software Company — multi-agent framework | Python | 2026-06 |
| **59,377** | [AutoGen](https://github.com/microsoft/autogen) | Programming framework for agentic AI | Python | 2026-06 |
| **54,637** | [CrewAI](https://github.com/joaomdmoura/crewAI) | Role-playing autonomous AI agents framework | Python | 2026-06 |
| **36,147** | [LangGraph](https://github.com/langchain-ai/langgraph) | Build resilient agents | Python | 2026-06 |
| **19,674** | [SWE-agent](https://github.com/princeton-nlp/SWE-agent) | Takes GitHub issues, auto-fixes them | Python | 2026-06 |
| **5,497** | [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) | ~100 lines, >74% on SWE-bench verified | Python | 2026-06 |
| **5,300** | [SWE-bench](https://github.com/SWE-bench/SWE-bench) | Can LMs resolve real-world GitHub issues? | Python | 2026-06 |
| **4,920** | [Kodezi Chronos](https://github.com/Kodezi/Chronos) | Debugging-first LM, 80.33% SWE-bench Lite | Python | 2026-06 |
| **3,549** | [Refact](https://github.com/smallcloudai/refact) | End-to-end engineering AI agent | Python | 2026-06 |
| **3,092** | [AutoCodeRover](https://github.com/AutoCodeRoverSG/auto-code-rover) | Structure-aware autonomous SWE, 46.2% SWE-bench verified | Python | 2026-06 |
| **2,440** | [Shippie](https://github.com/mattzcarey/shippie) | (MCP: ship software) | — | 2026-06 |
| **1,865** | [Azure DevOps MCP](https://github.com/microsoft/azure-devops-mcp) | ADO-powered MCP server | TypeScript | 2026-06 |
| **1,028** | [Microsoft Waza](https://github.com/microsoft/waza) | CLI/framework for Agent Skills quality | Python | 2026-06 |
| **999** | [Factory](https://github.com/factory-ai/factory) | Agent-native software development | — | 2026-06 |
| **872** | [Augment SWE-bench Agent](https://github.com/augmentcode/augment-swebench-agent) | #1 open-source SWE-bench Verified impl | Python | 2026-06 |
| **814** | [OpenSwarm](https://github.com/unohee/OpenSwarm) | AI dev team orchestrator (Claude Code + Discord + Linear) | — | 2026-06 |
| **697** | [SWE-Gym](https://github.com/SWE-Gym/SWE-Gym) | Training environments for coding agents | Python | 2026-06 |
| **611** | [Bernstein](https://github.com/sipyourdrink-ltd/bernstein) | Audit-grade multi-agent CLI orchestration (40+ agents) | Python | 2026-06 |
| **156** | [AIWG](https://github.com/jmagly/aiwg) | Cognitive architecture — 200+ agents, 10 platforms | TypeScript | 2026-06 |
| **77** | [FSPEC](https://github.com/sengac/fspec) | Spec-driven multi-agent coding factory | TypeScript | 2026-06 |
| **60** | [Donmai](https://github.com/RenseiAI/donmai-libraries) | Open-source coding-agent fleet runtime | TypeScript | 2026-06 |

---

## 2. Architecture Patterns — What's Working

### Pattern A: CLI-Agent Orchestrator (The Rising Star)

Multiple orchestrators that manage **existing CLI coding agents** (Claude Code, Codex, Aider, Gemini CLI) rather than implementing their own agents:

| Project | Approach | Agents Orchestrated | Key Feature |
|---|---|---|---|
| **Bernstein** | Deterministic pipeline orchestration with HMAC-chained audit logs | 40+ (Claude Code, Codex, Gemini CLI, Aider, etc.) | Audit-grade, air-gap deploy, signed agent cards |
| **AgentWrapper** | Plans tasks → spawns parallel agents → autonomous CI fix | Claude Code, Codex | Git worktrees, CI fix handling, merge conflict resolution |
| **OpenSwarm** | Discord-controlled AI dev team | Claude Code CLI | Discord control, Linear integration, cognitive memory |
| **Donmai** | Fleet management — issue backlog → shipped code | Claude, Codex, Spring AI | Linear integration, dashboard UI, MCP server, Redis worker pool |

**Why this pattern works:** It decouples *orchestration intelligence* from *coding capability*. You can swap the underlying coding agent without changing the pipeline. Bernstein's audit logs are production-grade (HMAC-chained, per-artefact lineage).

### Pattern B: Spec-Driven Factory (The New Wave)

Projects that put **specifications first** — you write the spec, the factory implements:

| Project | Approach | Notable |
|---|---|---|
| **FSPEC** | Gherkin/BDD specs → auto-generated tests → TDD-enforced coding | "Stop micromanaging AI. Start shipping tested code." |
| **MetaGPT** | Single prompt → multiple role agents (PM, Architect, Engineer) | 69k ⭐, most popular spec-to-code framework |
| **AgileCoder** | Agile methodology → agents collaborate on complex software | FORGE 2025 paper |

**FSPEC is especially relevant to us.** It uses Given/When/Then scenarios, auto-generates tests, enforces TDD, and links every line of code back to the business rule. Its topics include: `dd-domain-driven-design`, `bdd`, `cucumber`, `example-mapping` — this aligns perfectly with our **specification-interview** skill.

### Pattern C: Mega-Framework Multi-Agent (Mature, Heavy)

| Project | Architecture | Pros | Cons |
|---|---|---|---|
| **AutoGen** | Conversational agent groups, code executors | Microsoft-backed, flexible, 59k stars | Framework overhead, not software-specific |
| **CrewAI** | Role-based agents with tools | Developer-friendly, 54k stars | Not software-factory focused |
| **OpenHands** | Event-driven agent with sandboxed execution | 78k stars, strong community | Single-agent, not pipeline-oriented |
| **MetaGPT** | Role-based (PM/Arch/Eng) → sequential SOP | Most factory-like mega-framework | Heavy, verbose inter-agent communication |

### Pattern D: Minimal Agent + Great Eval (The Proof Point)

| Project | Approach | Performance |
|---|---|---|
| **mini-swe-agent** | ~100 lines of Python agent class | >74% SWE-bench Verified, beats Claude Code and Codex on DeepSWE |
| **Agentless** | No agent framework, just targeted prompting | Competitive SWE-bench results |
| **AutoCodeRover** | Structure-aware code search + targeted patching | 46.2% SWE-bench Verified |

**Lesson:** Simplicity + a great eval harness beats complexity + no evals.

---

## 3. MCP Ecosystem for Software Development

### Platform MCP Servers (Production-Ready)

| MCP Server | ⭐ | What It Does | Relevance |
|---|---|---|---|
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | 87,894 | Reference implementations (filesystem, GitHub, Git, Postgres, etc.) | **Foundation** |
| [Azure DevOps MCP](https://github.com/microsoft/azure-devops-mcp) | 1,865 | Full ADO API surface — work items, PRs, pipelines, boards | **Directly relevant — our factory needs this** |
| [Tiberriver256 MCP Azure DevOps](https://github.com/Tiberriver256/mcp-server-azure-devops) | 377 | Alternative ADO MCP server | Alternative |
| [Donmai MCP Server](https://github.com/RenseiAI/donmai-libraries) (included) | — | Exposes fleet capabilities to external MCP clients | Novel architecture |

**Missing pieces:**
- No dedicated **Figma MCP** server in the modelcontextprotocol org (the main MCP servers repo likely includes it, but it's not a standalone repo)
- No dedicated **GitHub MCP** standalone server (it's inside the servers monorepo)
- No unified **software factory MCP** that ties all of these together with a factory-specific protocol

### MCP SDK Maturity

| SDK | ⭐ | Status |
|---|---|---|
| Python SDK | 23,491 | Production-ready |
| TypeScript SDK | 12,764 | Production-ready |
| Inspector (testing) | 10,229 | Production-ready |
| Registry | 6,971 | Growing |
| Go / C# / Java / Kotlin / PHP / Swift SDKS | 1,500-4,700 | All active |

**Takeaway:** MCP is mature enough to build on. The SDKs are stable, the registry is active, and major players (Microsoft, Anthropic, OpenAI) back it.

---

## 4. Agent Instruction Quality — The Emerging Standards

### Microsoft Waza (⭐ 1,028)

Microsoft's **Waza** is the first systematic framework for agent instruction quality:

- CLI tool that scores agent skills on **5 dimensions**:
  1. **Clarity** — Is the instruction unambiguous?
  2. **Completeness** — Does it cover all scenarios?
  3. **Trigger Precision** — When does this agent activate?
  4. **Scope** — Does it stay in its lane?
  5. **Anti-patterns** — Does it avoid common mistakes?
- Uses **LLM-as-Judge** for scoring
- Can be integrated into CI pipelines
- Supports iterative improvement (score → fix → rescore)

**We already use this** in our agentic-software-factory skill's references.

### Agent Format Convergence

The ecosystem is converging on **three formats** for agent instructions:

| Format | Used By | File | When to Use |
|---|---|---|---|
| **.agent.md** | GitHub Copilot | `.github/agents/*.agent.md` | Copilot-specific agents |
| **CLAUDE.md** | Claude Code | `CLAUDE.md`, `CLAUDE_GLOBAL.md` | Claude Code context |
| **AGENTS.md** | Cursor | `AGENTS.md`, `.cursor/rules/` | Cursor-specific rules |
| **SKILL.md** | Hermes Agent | `~/.hermes/skills/*/SKILL.md` | Hermes reusable procedures |

**No unified format exists.** A project that wants to support all agents needs to maintain ~4 copies. This is a real pain point.

### Best Practices Emerging (Across Projects)

From analyzing the READMEs and architectures of the top projects:

1. **Context isolation for reviewers** — Every successful pipeline does this. Plan Reviewer must NOT see planner's reasoning.
2. **Markdown-as-contract** — All artifacts between agents are markdown files in the repo. Version-controllable, auditable, comparable across models.
3. **Max 2 revision loops** — Beyond that, escalate. Prevents infinite token burn.
4. **Phase-based batching** — Don't run one agent per story. Batch by phase (infrastructure, API, frontend).
5. **Spec-first, always** — Write tests before code. FSPEC, MetaGPT, AgileCoder all agree.
6. **Deterministic audit trails** — Bernstein's HMAC-chained logs are the gold standard.
7. **Evals determine success** — mini-swe-agent proves that a simple agent + great benchmark beats a complex agent with none.

---

## 5. SWE-bench — The Benchmark Landscape

### Current State (2026)

| Approach | SWE-bench Lite | SWE-bench Verified | Notes |
|---|---|---|---|
| **Kodezi Chronos** | 80.33% | — | Debugging-first model, purpose-built |
| **Ramp SWE-bench** (mini-swe-agent powered) | — | ~74%+ | Production usage at Ramp |
| **AutoCodeRover** | 37.3% | 46.2% | Structure-aware, open-source |
| **Augment** | — | #1 OSS implementation | Corporate-backed |
| **Claude Code** | — | — | Beaten by mini-swe-agent on DeepSWE |
| **Codex CLI** | — | — | Beaten by mini-swe-agent on DeepSWE |

**Key insight:** The top results come from **minimal agents + great task representation**, not complex multi-agent systems. mini-swe-agent's 100-line agent class outperforms Claude Code and Codex CLI on the DeepSWE benchmark.

---

## 6. The Gap Analysis — What Nobody Has Built

### Our Current Position

We already have:
- **8-agent factory architecture** (agentic-software-factory skill)
- **Specification interview workflow** (specification-interview skill)
- **Context bundle templates** (PRD, UI/UX, Architecture, Test Strategy)
- **Context isolation principle** embedded in the pipeline
- **Phase-based batching** for practical execution
- **Benchmark methodology** (model comparison via identical context bundles)
- **Waza evaluation** integration for agent quality

### What's Missing (The Gap)

| Need | Existing Solutions | Gap |
|---|---|---|
| **Codebase context generation** | FSPEC, AIWG have elements | No tool that walks through existing codebase → generates full context bundle (PRD + Arch + Test Strategy) automatically |
| **Structured specification interview** | Our skill is the closest | No standalone tool with MCP integration for this |
| **ADO/GitHub/Figma MCP setup** | Individual MCP servers exist | No factory that auto-configures all three, generates instructions for each |
| **Custom agent generation per codebase** | AIWG generates from templates | No system that **analyzes a specific repo** and generates tailored agents matching its tech stack, patterns, and conventions |
| **Best practice capture** | Waza evaluates quality | No system that learns from usage and evolves agent instructions based on outcomes |
| **Cross-platform agent format** | Fragmented (.agent.md, CLAUDE.md, AGENTS.md, SKILL.md) | No unified source of truth that generates all formats from one definition |
| **Multi-platform deployment** | AIWG supports 10 platforms | Different approach — we need one factory that deploys to any agent runtime |

### The Opportunity

**What a complete software factory bootstrap tool would do:**

1. **Analyze existing repo** — Scan structure, language, frameworks, dependencies, patterns
2. **Interview the user** — Structured Q&A to capture intent, clarify ambiguity, document decisions (our specification-interview skill is the model)
3. **Generate context bundle** — PRD, architecture doc, test strategy, user stories
4. **Configure MCP tools** — Auto-setup ADO (work items, PRs), GitHub (issues, PRs), Figma (design tokens, specs)
5. **Generate custom agents** — Create .agent.md / CLAUDE.md / AGENTS.md tailored to the codebase
6. **Evolve with usage** — Track what works, update agent instructions via feedback loops
7. **Run the factory** — Decompose stories → plan → review → code → test → ship

---

## 7. Project Deep Dives — The Most Relevant to Our Work

### FSPEC (⭐ 77) — Spec-Driven Factory
- **URL:** https://github.com/sengac/fspec
- **License:** MIT
- **Tech:** TypeScript, npm package
- **Architecture:** Gherkin/BDD specs → auto-generated tests → TDD enforcement
- **Tags:** agentic-ai, ai-guardrails, bdd, cucumber, dark-factory, ddd, domain-driven-design, example-mapping
- **Why relevant:** Their approach aligns with ours (spec-first, test-first). They've built a VSCode extension and MCP server. At 77 stars it's small but the concept is right.

### Bernstein (⭐ 611) — Audit-Grade Orchestration
- **URL:** https://github.com/sipyourdrink-ltd/bernstein
- **License:** Apache-2.0
- **Tech:** Python, PyPI
- **Architecture:** Deterministic pipeline orchestrator for 40+ CLI coding agents
- **Key features:** HMAC-chained audit log, signed agent cards, per-artefact lineage, air-gap deploy
- **Why relevant:** If we want production-grade audit trails, this is the model. Their deterministic orchestration + zero-trust deployment model is enterprise-ready.

### Donmai (⭐ 60) — Fleet Management
- **URL:** https://github.com/RenseiAI/donmai-libraries
- **License:** MIT
- **Tech:** TypeScript, npm monorepo (8 packages)
- **Architecture:** Issue backlog → coding agent fleet → shipped code
- **Key packages:** Core orchestrator, Linear plugin, MCP server, Dashboard UI, CLI, Next.js integration
- **Why relevant:** Monorepo with MCP server baked in. Linear integration is exactly what we'd need for issue tracking.

### AIWG (⭐ 156) — Cognitive Architecture
- **URL:** https://github.com/jmagly/aiwg
- **License:** MIT
- **Tech:** TypeScript, npm
- **Architecture:** 200+ agents + 67 CLI commands + 400+ deployable artifacts across 10 platforms
- **Key feat:** Single command (`aiwg use sdlc`) deploys full SDLC framework to any supported platform
- **Why relevant:** Cross-platform deployment (Claude Code, Copilot, Cursor, Warp, 6 more) is what we'd eventually need. At 156 stars, growing.

### AgentWrapper/Agent-Orchestrator (⭐ 7,820) — Parallel Coding
- **URL:** https://github.com/AgentWrapper/agent-orchestrator
- **License:** Not specified
- **Architecture:** Plans tasks, spawns parallel coding agents, handles CI fixes and merge conflicts
- **Key features:** Git worktrees for parallel coding, autonomous CI fix handling
- **Why relevant:** Parallel agent execution with git worktree isolation is the right pattern for batch processing.

### Ouroboros (⭐ 1) — Self-Feedbacking Factory
- **URL:** https://github.com/the-forever-loop/ouroboros
- **Architecture:** Hermes schedules scans → identifies problems → writes handoff markdown → dispatches Claude Code → validates results
- **Key insight:** Uses **Hermes** + Egregore (shared memory layer) + Claude Code. Git and markdown only — no custom servers.
- **Why relevant:** Directly uses Hermes as the orchestrator/scanner. Proves the concept.
- **From the README:** "28 handoffs processed. 54 commits. 101 knowledge files accumulated. Code has been found broken, described in a handoff, picked up by an agent, fixed, committed, pushed, and validated — all without a human typing a single command."

### Mini-SWE-Agent (⭐ 5,497) — The Minimal Benchmark
- **URL:** https://github.com/SWE-agent/mini-swe-agent
- **Tech:** Python, PyPI
- **What it is:** ~100 lines of Python agent class. Used by Meta, NVIDIA, Essential AI, IBM, Anyscale, Princeton, Stanford.
- **Performance:** >74% SWE-bench Verified. Beats Claude Code and Codex on DeepSWE.
- **Why relevant:** Proof that **simplicity wins**. The agent is minimal but the eval is rigorous. This should inform our agent design philosophy.

---

## 8. Recommendations — Where We Should Go

### Immediate Actions

1. **Update our Key Players vault note** with the complete data from this report
2. **Adopt FSPEC's spec-driven approach** — Our specification-interview skill + their Gherkin-to-tests pipeline would be powerful together
3. **Integrate Microsoft Waza** (already in our references) — Make it a standard step in agent instruction development
4. **Evaluate Bernstein** for audit trail patterns — Their HMAC-chained logging is what production deployments need

### Next Phase for Our Factory

1. **Build the bootstrap tool** — Analyze an existing repo → interview the user → generate full context bundle
2. **MCP integration layer** — Auto-configure ADO, GitHub, Figma MCP servers for the factory pipeline
3. **Multi-format agent generation** — One source → .agent.md / CLAUDE.md / AGENTS.md / SKILL.md
4. **Feedback loop** — Track factory outcomes → update agent instructions → Waza scores improve

### Architecture Principles to Keep

✅ **Context isolation for reviewers** — Already built in, keep it
✅ **Markdown-as-contract** — Already built in, keep it
✅ **Max 2 revision loops** — Already built in, keep it
✅ **Phase-based batching** — Already built in, keep it
✅ **Spec-first / TDD enforcement** — Already built in, keep it
✅ **Waza integration** — Already in references, promote to standard step

### New Principles to Adopt

➕ **Deterministic audit trails** — From Bernstein
➕ **Simplicity > complexity** — From mini-swe-agent
➕ **Evals determine success** — Invest more in evaluation harness than agent capabilities
➕ **Cross-platform deployment** — From AIWG
➕ **Fleet runtime pattern** — From Donmai (multiple coding agents, not just one)

---

## 9. Appendix — GitHub Star Trends (Key Context)

These star counts were queried live on 2026-06-30. They represent the **current** landscape, not 2024 data.

| Tier | Star Range | Projects | Implication |
|---|---|---|---|
| **Hyper-scale** | 50k-185k | AutoGPT, Claude Code, Codex CLI, OpenHands, MetaGPT, AutoGen, CrewAI | Consumer adoption, ecosystem anchors |
| **Framework** | 5k-40k | LangGraph, SWE-agent, mini-swe-agent, Chronos, Refact | Developer tools, professional usage |
| **Emerging** | 500-5k | AgentWrapper, Bernstein, Augment, OpenSwarm, SWE-Gym | Active development, funded |
| **Early** | <500 | FSPEC, Donmai, AIWG, Ouroboros | Picks and shovels — highest risk/reward |

**Our factory sits in the "Emerging" tier conceptually** — building on these foundations but with a differentiated focus on **codebase-adaptive bootstrapping** that nobody else has cracked.

---

## 10. Sources

Live GitHub API queries at 2026-06-30T21:00Z:
- GitHub Search API: `search/repositories?q=...` (star counts, descriptions, topics)
- Individual repo endpoints: `repos/{owner}/{name}` (metadata, license, creation dates)
- Raw READMEs: `repos/{owner}/{name}/readme` (architecture descriptions)

Existing Obsidian vault notes referenced:
- `Projects/AI Software Factory.md`
- `Resources/AI Agents/Key Players.md`
- `Resources/AI Agents/Agent Architectures.md`
- `Resources/AI Agents/Eval Frameworks.md`
- `Projects/Agentic Software Factory — Benchmark Architecture.md`
- `software-development/agentic-software-factory/SKILL.md`