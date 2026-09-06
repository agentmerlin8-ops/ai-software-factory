#!/usr/bin/env python3
"""factory/gates/pre_review_gate.py — deterministic pre-review checks (Fable consult #1, rec 3).

Runs BEFORE any LLM reviewer is spawned. Usage:
    python3 factory/gates/pre_review_gate.py <story-dir> [more-story-dirs...]

Each story dir must contain handoff.md (or impl-plan.md). Checks:
  G1  handoff declares a FILES section with CREATE/EXTEND markers
  G2  no two stories in the batch CREATE the same path
  G3  verification commands name an exact test project (no bare "the tests"),
      and do not use VSTest-style --filter with MTP projects (field note 16)
  G4  every acceptance criterion (AC-N) appears in a named test reference
  G5  plan contains a "Decisions" section (consult #1, rec 6)

Exit 0 = gate passed; exit 1 = findings printed (author must fix before review).
This script is intentionally dumb and auditable — extend it as loop tags accumulate.
"""
import re
import sys
from pathlib import Path

findings = []


def check(story_dir: Path, created_paths: dict):
    sid = story_dir.name
    handoff = story_dir / "handoff.md"
    plan = story_dir / "impl-plan.md"
    if not handoff.exists() and not plan.exists():
        findings.append(f"{sid}: no handoff.md or impl-plan.md found")
        return
    text = "\n".join(p.read_text() for p in (handoff, plan) if p.exists())

    # G1 — CREATE/EXTEND file manifest
    creates = re.findall(r"CREATE[:\s]+`?([^\s`,)]+)", text)
    extends = re.findall(r"EXTEND[:\s]+`?([^\s`,)]+)", text)
    if not creates and not extends:
        findings.append(f"{sid}: G1 — no CREATE/EXTEND file manifest found")
    for c in creates:
        if c in created_paths:
            findings.append(
                f"{sid}: G2 — CREATE collision with {created_paths[c]} on `{c}` "
                "(must run SEQUENTIALLY — field note 17)"
            )
        created_paths[c] = sid

    # G3 — verification commands
    for m in re.finditer(r"dotnet test[^\n]*", text):
        cmd = m.group(0)
        if "--filter" in cmd and " -- " not in cmd:
            findings.append(
                f"{sid}: G3 — `--filter` without MTP forwarding (` -- `): "
                "silently matches 0 tests (field note 16)"
            )
        if re.search(r"dotnet test\s*$", cmd.strip()):
            findings.append(f"{sid}: G3 — verification runs bare `dotnet test` (no exact project name, field note 14)")

    # G4 — acceptance criteria mapped to tests
    acs = set(re.findall(r"\bAC-(\d+)\b", text))
    tests = set(re.findall(r"AC-(\d+)\b", text[text.lower().find("test") :])) if "test" in text.lower() else set()
    unmapped = acs - tests
    # crude but honest: flag when an AC appears only once in the whole artifact
    for ac in sorted(acs):
        if len(re.findall(rf"\bAC-{ac}\b", text)) < 2:
            findings.append(f"{sid}: G4 — AC-{ac} appears once (story text) with no test mapping")

    # G5 — decisions section
    if plan.exists() and not re.search(r"^#+\s*.*Decisions", plan.read_text(), re.M):
        findings.append(f"{sid}: G5 — impl-plan missing 'Decisions & rejected alternatives' section")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    created: dict = {}
    for d in sys.argv[1:]:
        check(Path(d), created)
    if findings:
        print("PRE-REVIEW GATE: FAIL")
        for f in findings:
            print(f"  - {f}")
        sys.exit(1)
    print(f"PRE-REVIEW GATE: PASS ({len(sys.argv) - 1} story dir(s), {len(created)} CREATE paths)")
    sys.exit(0)


if __name__ == "__main__":
    main()
