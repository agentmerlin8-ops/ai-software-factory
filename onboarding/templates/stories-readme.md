# stories/

One directory per story. Each contains:

- `STORY-{ID}.md` at the root of this folder (the story itself)
- `STORY-{ID}/test-plan.md`
- `STORY-{ID}/impl-plan.md`
- `STORY-{ID}/state.md` — the per-story audit trail (checklist + history)

The orchestrator updates `state.md` after every stage transition, in the same commit that regenerates `factory/DASHBOARD.md`.
