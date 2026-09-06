# Factory Field Notes

Operational lessons harvested from live factory runs (MIE project). Newest
first. Numbering continues from the notes referenced in
`media-ingestion-engine/factory/runbook.md` and the
`agentic-software-factory` skill (notes 1–17 predate this file — they were
tracked in session history and runbook citations before the catalog was
committed; this file starts the durable catalog at 18).

## 18 — Planner trusted component names without verifying the render tree (MIE STORY-024B, 2026-09-06, loop 1, `contract`)

- **What:** the impl plan wired acceptance criteria through
  `PodcastResultCard` (dead code in the app path — `FindPodcastsScreen`
  renders its own inline rows) and filed the queue-409 test on `LibraryPage`
  (no queue mutation; the real surface is `EpisodeListPage`). Fresh-context
  plan review caught both; the fixes were targeted manifest/test-placement
  corrections.
- **Lesson:** planner prompts must require verifying that every component in
  an EXTEND/CREATE manifest is on a RENDERED path (trace from App routes) and
  that every test is filed against the file that owns the behavior. Candidate
  script-gate check (G6): manifest paths that are pages/components must be
  import-reachable from the route tree — or at minimum the planner must state
  the import chain per wired surface.
- **Follow-up:** extend `factory/gates/pre_review_gate.py` when loop tags
  accumulate another `contract`-class plan defect of this shape.

## 19 — Destructive-gate state carry-over in always-mounted dialogs (MIE STORY-024B, 2026-09-06, code loop 1, `reasoning`)

- **What:** `UnsubscribeDialog` held `mode`/`confirmed` in component state;
  the page kept the dialog mounted across targets (only `open` toggled), so
  delete-mode + checked destructive-confirm carried over to the next podcast
  — the confirmation gate was pre-satisfied. Every test rendered fresh
  (single open), so the path was never exercised.
- **Lesson:** for any dialog with destructive-confirmation state, the test
  plan MUST include a reopen-on-same-mount regression test (open → arm →
  close → reopen → assert reset). React idiom that passed lint: adjust-state-
  during-render (`prevOpen` comparison) instead of `useEffect`+setState
  (`react/set-state-in-effect` rejects the effect version).
- **Generalization:** component-level state that outlives a logical
  "session" (dialog open) is a defect class; reviewers should ask "what
  resets this when the target changes?"

## 20 — Gate script false positive: intra-story manifest echo (MIE STORY-024B, 2026-09-06)

- **What:** `pre_review_gate.py` G2 (cross-story CREATE collision) fired when
  a story's `handoff.md` re-listed the same CREATE paths as its own
  `impl-plan.md` — same story, not a collision. Fixed by ignoring
  same-story re-listing (`created_paths[c] != sid`).
- **Lesson:** gate scripts concatenate all artifacts in a story dir; any
  duplication across artifacts of the SAME story is normal (handoffs echo
  manifests). Gates must scope collision checks per story-pair, not per path
  occurrence.

## 21 — Doc-sync debt rides along better than it waits (MIE STORY-024B, 2026-09-06)

- **What:** `dashboard/src/contract/types.ts` lagged the merged 024A backend
  DTOs (`purgeRequestedAt`, `previouslySubscribed`). Folding the sync into
  024B's phase-1 scope (typed fixtures needed the fields anyway) beat a
  standalone `docs:` commit — zero extra cost, and the compile gate (`tsc -b`)
  then guards the contract going forward.
- **Lesson:** when the next story needs the stale artifact, make the sync an
  explicit AC of that story (AC-6 pattern), not separate hygiene work.

## 22 — Vitest/Storybook builds do NOT typecheck (MIE STORY-024B, 2026-09-06, nit caught at plan review)

- **What:** a test plan claimed contract drift was "verified by compilation"
  via `vitest run` and `build-storybook` — both transpile with esbuild/vite
  and never run `tsc`. Only `npm run build` (or explicit `npx tsc -b`)
  typechecks.
- **Lesson:** frontend verification blocks must include an explicit
  `npx tsc -b` line whenever type contracts matter. Cheap, deterministic,
  catches DTO/contract drift no test would.
