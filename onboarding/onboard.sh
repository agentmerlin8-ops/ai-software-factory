#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# AI Software Factory — repo onboarding (idempotent, deterministic)
# Usage: ./onboarding/onboard.sh /path/to/target/repo
# ─────────────────────────────────────────────────────────────────────────────
set -uo pipefail

FACTORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:?Usage: onboard.sh /path/to/target/repo}"
PASS=0; FAIL=0; WARN=0
ok()   { echo "  PASS  $1"; PASS=$((PASS+1)); }
bad()  { echo "  FAIL  $1"; FAIL=$((FAIL+1)); }
warn() { echo "  WARN  $1"; WARN=$((WARN+1)); }

echo "══ AI Software Factory onboarding ══"
echo "target: $TARGET"

# ── 0. Sanity ────────────────────────────────────────────────────────────────
[ -d "$TARGET" ] || { bad "target directory does not exist"; exit 1; }
cd "$TARGET" || exit 1

if ! command -v gh >/dev/null 2>&1; then
  bad "gh CLI not installed — https://cli.github.com"; exit 1
fi
ok "gh CLI present ($(gh --version | head -1))"

if gh auth status >/dev/null 2>&1; then
  ok "gh authenticated as: $(gh api user -q .login 2>/dev/null)"
else
  bad "gh not authenticated — run: gh auth login"; exit 1
fi

# Is the target a GitHub repo with a remote we can reach?
if gh repo view --json nameWithOwner >/dev/null 2>&1; then
  REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
  ok "GitHub repo: $REPO"
else
  warn "target is not (yet) linked to a GitHub repo — labels & Copilot checks deferred"
  REPO=""
fi

# ── 1. Posture detection ─────────────────────────────────────────────────────
# Posture detection:
#   bundled    — context bundle docs already exist (brownfield OR greenfield-with-spec)
#   brownfield — existing source code, no bundle yet
#   greenfield — neither
SRC_COUNT=$(find . -type f \
  \( -name '*.cs' -o -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' \
     -o -name '*.go' -o -name '*.java' -o -name '*.rs' \) \
  -not -path './.git/*' -not -path './node_modules/*' -not -path './factory/*' 2>/dev/null | wc -l)
BUNDLE_COUNT=$(find ./docs -maxdepth 1 -type f \
  \( -name 'prd*.md' -o -name 'architecture*.md' -o -name 'ui-design*.md' -o -name 'test-strategy*.md' \) \
  2>/dev/null | wc -l)
if [ "$BUNDLE_COUNT" -ge 3 ]; then
  POSTURE=bundled
  echo "  POSTURE: bundled (context bundle present: $BUNDLE_COUNT bundle docs, $SRC_COUNT source files)"
elif [ "$SRC_COUNT" -gt 0 ]; then
  POSTURE=brownfield
  echo "  POSTURE: brownfield ($SRC_COUNT source files)"
else
  POSTURE=greenfield
  echo "  POSTURE: greenfield"
fi

# ── 2. Install factory structure (never overwrite) ──────────────────────────
install_file() {  # $1=template  $2=destination
  if [ -f "$2" ]; then warn "exists, keeping yours: $2"; return; fi
  mkdir -p "$(dirname "$2")"
  cp "$1" "$2" && ok "installed $2"
}

# Agent prompts: single source of truth = this factory repo's agents/
mkdir -p .github/agents
for f in "$FACTORY_ROOT"/agents/*.agent.md; do
  name=$(basename "$f")
  if [ -f ".github/agents/$name" ]; then
    warn "exists, keeping yours: .github/agents/$name"
  else
    cp "$f" ".github/agents/$name" && ok "installed .github/agents/$name"
  fi
done

install_file "$FACTORY_ROOT/onboarding/templates/DASHBOARD.md"        factory/DASHBOARD.md
install_file "$FACTORY_ROOT/onboarding/templates/runbook.md"          factory/runbook.md
install_file "$FACTORY_ROOT/onboarding/templates/story-state.md"      factory/templates/story-state.md
install_file "$FACTORY_ROOT/onboarding/templates/story-handoff-issue.md" factory/templates/story-handoff-issue.md
mkdir -p stories
[ -f stories/README.md ] || cp "$FACTORY_ROOT/onboarding/templates/stories-readme.md" stories/README.md

# Posture-specific extras
case "$POSTURE" in
  greenfield)
    for d in prd architecture ui-design test-strategy; do
      install_file "$FACTORY_ROOT/onboarding/templates/context-bundle-$d.md" "docs/$d.md"
    done
    install_file "$FACTORY_ROOT/onboarding/templates/context-bundle-guide.md" docs/context-bundle-guide.md
    ;;
  brownfield)
    install_file "$FACTORY_ROOT/onboarding/templates/bootstrap-checklist.md" factory/bootstrap-checklist.md
    ;;
  bundled)
    echo "  INFO  context bundle already present — no stubs written"
    ;;
esac

# ── 3. Labels (idempotent via --force) ───────────────────────────────────────
if [ -n "$REPO" ]; then
  declare -A LABELS=(
    ["factory:planning"]="1d76db"
    ["factory:plan-review"]="5319e7"
    ["factory:implementation"]="0e8a16"
    ["factory:code-review"]="fbca04"
    ["factory:testing"]="d93f0b"
    ["factory:done"]="cccccc"
    ["factory:blocked"]="b60205"
    ["needs-human"]="ff69b4"
  )
  for label in "${!LABELS[@]}"; do
    gh label create "$label" --color "${LABELS[$label]}" \
      --description "factory pipeline stage" --force >/dev/null 2>&1 \
      && ok "label: $label" || bad "label: $label"
  done

  # ── 4. Copilot coding-agent assignability ─────────────────────────────────
  OWNER="${REPO%%/*}"; NAME="${REPO##*/}"
  ACTORS=$(gh api graphql -f query='
    query($owner:String!, $repo:String!) {
      repository(owner:$owner, name:$repo) {
        suggestedActors(capabilities:[CAN_BE_ASSIGNED], first:100) {
          nodes { __typename login }
        }
      }
    }' -f owner="$OWNER" -f repo="$NAME" 2>/dev/null \
    | python3 -c "import json,sys
d=json.load(sys.stdin)
print('\n'.join(n['login'] for n in d['data']['repository']['suggestedActors']['nodes']))" 2>/dev/null)
  if echo "$ACTORS" | grep -qi copilot; then
    ok "Copilot coding agent is assignable on this repo"
  else
    bad "Copilot coding agent NOT assignable — enable Settings → Copilot → Coding agent"
  fi
  if echo "$ACTORS" | grep -qi "anthropic-code-agent\|openai-code-agent"; then
    echo "  INFO  additional coding agents available: $(echo "$ACTORS" | grep -i code-agent | tr '\n' ' ')"
  fi
else
  warn "skipped labels + Copilot check (no GitHub remote)"
fi

# ── 5. Readiness report ──────────────────────────────────────────────────────
mkdir -p factory
cat > factory/PREFLIGHT.md <<EOF
# Factory Preflight Report

- target: $TARGET
- posture: $POSTURE ($SRC_COUNT source files)
- repo: ${REPO:-none}
- result: $PASS passed / $FAIL failed / $WARN warnings

$( [ "$FAIL" -eq 0 ] && echo "**READY** — fill in the context bundle in docs/, grill it, then decompose." || echo "**NOT READY** — fix the FAIL items above." )
EOF
ok "wrote factory/PREFLIGHT.md"

echo
echo "══ result: $PASS passed / $FAIL failed / $WARN warnings ══"
[ "$FAIL" -eq 0 ]
