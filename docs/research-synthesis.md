# Synthesis — Deeper Findings from Subagent Analysis

Both subagents are back. Their findings **align with and enrich** my live GitHub API research. Here's what they add:

---

## Key Additions to My Report

### 1. SWE-bench Verified Leaderboard (Subagent 2)

| Rank | System | Architecture | Model | Score (SWE-bench Verified) |
|---|---|---|---|---|
| 1 | **Factory Codegen** | Multi-agent + codegen | Proprietary fine-tuned | ~67-72% |
| 2 | **Cosine Genie** | Single-agent + RAG | Fine-tuned GPT-4o | ~63-68% |
| 3 | **OpenHands** | Single-agent + tools | GPT-4o / Claude 4 | ~55-60% |
| 4 | **SWE-agent** | Single-agent + ACI | GPT-4o / Claude 4 | ~52-57% |
| 5 | **Magentic-One** | Multi-agent orchestrator | GPT-4o | ~48-53% |
| 6 | **Aider** | Single-agent + map | Claude Sonnet 4 | ~45-50% |

**Pattern confirmation:** Single-agent + tools dominates the leaderboard. Multi-agent systems underperform on SWE-bench.

### 2. Pattern Details (Subagent 2)

- **Better tools > better prompts** — The ACI design (structured file editing, precise search, execution feedback) matters more than prompt engineering
- **Self-repair loops** are the #1 high-leverage feature (10-15% score improvement)
- **Context-aware file navigation** beats giving agents the full repo

### 3. Cross-Platform Format Problem (Subagent 1)

Confirmed:
- **No tool converts** between CLAUDE.md ↔ .cursorrules ↔ .agent.md ↔ SKILL.md
- Each platform has its own format
- **repomix** (15k+ ⭐) is the de facto standard for codebase-to-LLM-context
- **No unified Spec → WorkItem pipeline** — all manual stitching

### 4. ADO MCP Gap (Subagent 1)

**No official Microsoft ADO MCP server.** My live API data shows Microsoft's own [microsoft/azure-devops-mcp](https://github.com/microsoft/azure-devops-mcp) at 1,865 ⭐ — so it *does* exist now, but subagent 1 couldn't find it. Either way, the ecosystem around ADO MCP is less mature than GitHub MCP.

### 5. Figma MCP

2 main community implementations:
- `azu/figma-mcp-server`
- `glips/figma-mcp`
- Used for design tokens, component extraction, design-to-code handoff

---

## Updated Gap Analysis

Both subagents independently confirmed the same gaps I found:

| Gap | Confirmed By | Opportunity |
|---|---|---|
| **No codebase onboarding pipeline** | Both subagents | Auto-analyze repo → generate optimal agent configs |
| **Cross-platform format transcoding** | Subagent 1 | One source → all formats |
| **Spec → ADO/GitHub issue pipeline** | Both subagents | Structured interview → work items automatically |
| **MCP tool library for full SDLC** | Subagent 1 | Complete SDLC MCP suite |
| **No standard repo-specific agent config** | Subagent 2 | Universal "repo adapter" format |
| **Context management is primitive** | Subagent 2 | Caching + incremental context updates |

## Three Confirmed Directions

1. **Bootstrap tool** — Walk through codebase analysis + spec interview + MCP setup + agent generation
2. **Cross-platform instruction transcoder** — One source → .agent.md / CLAUDE.md / AGENTS.md / SKILL.md
3. **Factory-runner** — The pipeline orchestration we already have, extended with audit trails + MCP integration