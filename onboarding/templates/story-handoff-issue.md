## Story: STORY-{ID} — {title}

You are implementing one story from an approved plan. Follow it mechanically; no scope creep.

### Context
{story summary from stories/STORY-{ID}.md}

### Approved implementation plan
See `stories/STORY-{ID}/impl-plan.md`. It is the contract: exact files, exact steps, TDD order.

### Acceptance criteria
{copy from story file}

### Files in scope
{list — do not touch files outside this list}

### Definition of done
- [ ] Tests written first, failing, then passing
- [ ] Build green
- [ ] No changes outside the files-in-scope list
- [ ] Commit messages prefixed `STORY-{ID}:`

If the plan is impossible as written (missing dependency, contradiction), STOP and say so in a PR comment — do not improvise a different design.
