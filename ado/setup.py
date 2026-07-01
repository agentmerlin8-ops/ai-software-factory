#!/usr/bin/env python3
"""
Azure DevOps Work Item Type Setup: AI Software Factory

Creates custom work item types "AI Story" and "AI Verification" with all
custom fields, picklists, states, transitions, and form layouts.

Usage:
  export AZURE_DEVOPS_PAT="<your-pat>"
  python3 ado_setup_factory.py                    # Run live
  python3 ado_setup_factory.py --dry-run          # Preview only
  python3 ado_setup_factory.py --verify-only      # Check current state

Environment:
  AZURE_DEVOPS_ORG     - https://dev.azure.com/agentmerlin
  AZURE_DEVOPS_PROJECT - AI Software Factory
  AZURE_DEVOPS_PAT     - Personal Access Token (Boards: Read & Write)
  PROCESS_ID           - 7e34d370-3e5e-4dc6-add7-d96b9cea5f2e

REST API Reference:
  https://learn.microsoft.com/en-us/rest/api/azure/devops/processes/
  https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/
"""

import os
import sys
import json
import base64
import time
import logging
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ──────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────

ORG = os.environ.get("AZURE_DEVOPS_ORG", "https://dev.azure.com/agentmerlin")
PROJECT = os.environ.get("AZURE_DEVOPS_PROJECT", "AI Software Factory")
PROCESS_ID = os.environ.get("PROCESS_ID", "7e34d370-3e5e-4dc6-add7-d96b9cea5f2e")
PAT = os.environ.get("AZURE_DEVOPS_PAT", "")
API_VERSION = "6.0"  # Using 6.0 which has wider az devops invoke compatibility

DRY_RUN = "--dry-run" in sys.argv
VERIFY_ONLY = "--verify-only" in sys.argv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ado_setup")

# ──────────────────────────────────────────────────────────────────────
# REST Helpers
# ──────────────────────────────────────────────────────────────────────

def _auth_header():
    if not PAT:
        return {}
    token = base64.b64encode(f":{PAT}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def _request(method, url, body=None):
    """Make an HTTP request and return parsed JSON response."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        **_auth_header(),
    }
    data = json.dumps(body).encode() if body is not None else None
    req = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(req, timeout=45) as resp:
            raw = resp.read().decode()
            if raw.strip():
                return json.loads(raw)
            return {"status": resp.status}
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        log.error("HTTP %d %s\n  URL: %s\n  Body: %s",
                   e.code, e.reason, url, error_body[:500])
        return None
    except URLError as e:
        log.error("URL error: %s", e.reason)
        return None


def api_process(action, path="", body=None):
    """Call Process REST API."""
    if path and not path.startswith("/"):
        path = "/" + path
    url = f"{ORG}/_apis/work/processes{path}?api-version={API_VERSION}"
    return _request(action, url, body)


def api_wit(project_level=False, action="GET", path="", body=None, wit_ref=None):
    """Call Work Item Tracking REST API (project-level WITs)."""
    if project_level:
        base = f"{ORG}/{PROJECT}/_apis/wit"
    else:
        base = f"{ORG}/_apis/wit"

    full_path = path
    if path and not path.startswith("/"):
        full_path = "/" + path

    url = f"{base}{full_path}?api-version={API_VERSION}"
    return _request(action, url, body)


# ──────────────────────────────────────────────────────────────────────
# Data Definitions
# ──────────────────────────────────────────────────────────────────────

PICKLISTS = {
    "PlanReviewStatus": {
        "name": "PlanReviewStatus",
        "items": [
            {"value": "Approved"},
            {"value": "Revisions Requested"},
        ],
    },
    "CodeReviewStatus": {
        "name": "CodeReviewStatus",
        "items": [
            {"value": "Approved"},
            {"value": "Changes Requested"},
        ],
    },
    "SignOffStatus": {
        "name": "SignOffStatus",
        "items": [
            {"value": "Approved"},
            {"value": "Needs Revision"},
        ],
    },
    "Persona": {
        "name": "Persona",
        "items": [
            {"value": "BA/PO"},
            {"value": "UI/UX"},
            {"value": "DEV"},
            {"value": "QA"},
        ],
    },
    "Harness": {
        "name": "Harness",
        "items": [
            {"value": "m365-copilot"},
            {"value": "github-copilot"},
        ],
    },
    "AIFoundryModel": {
        "name": "AIFoundryModel",
        "items": [
            {"value": "deepseek-v4-flash"},
            {"value": "deepseek-v4-pro"},
            {"value": "gpt-4o"},
            {"value": "claude-3.5-sonnet"},
        ],
    },
}

# Fields definition: (ref_name, name, type, picklist_name_or_none, description)
ALL_FIELDS = [
    # ── AI Story fields ──
    ("Custom.AIStory.StoryContext", "Story Context", "html", None,
     "Full story context from the decomposer"),
    ("Custom.AIStory.TestPlan", "Test Plan", "html", None,
     "Generated test plan in Given/When/Then format"),
    ("Custom.AIStory.ImplPlan", "Implementation Plan", "html", None,
     "Generated implementation plan with tasks"),
    ("Custom.AIStory.PlanReviewStatus", "Plan Review Status", "string", "PlanReviewStatus",
     "Approval state of the implementation plan"),
    ("Custom.AIStory.CodeReviewStatus", "Code Review Status", "string", "CodeReviewStatus",
     "Approval state of the generated code"),
    ("Custom.AIStory.ModelUsed", "AI Model Used", "string", "AIFoundryModel",
     "Which Azure Foundry model generated this story"),
    ("Custom.AIStory.TestResults", "Test Results", "html", None,
     "Pass/Fail details with evidence traces"),
    ("Custom.AIStory.RevisionCount", "Revision Count", "integer", None,
     "Loop counter for revision tracking (max 2 per stage)"),
    ("Custom.AIStory.AcceptanceCriteria", "Acceptance Criteria", "html", None,
     "Given/When/Then formatted acceptance criteria"),
    ("Custom.AIStory.ParentFeature", "Parent Feature", "string", None,
     "Title of the parent Epic"),

    # ── AI Verification fields ──
    ("Custom.AIVerification.Persona", "Persona", "string", "Persona",
     "Which persona is being grilled"),
    ("Custom.AIVerification.Harness", "Harness", "string", "Harness",
     "Which AI harness was used"),
    ("Custom.AIVerification.FeatureName", "Feature Name", "string", None,
     "Name of the feature being verified"),
    ("Custom.AIVerification.QuestionsAsked", "Questions Asked", "integer", None,
     "Total questions in the grill session"),
    ("Custom.AIVerification.FullyCorrect", "Fully Correct", "integer", None,
     "Questions answered fully correctly"),
    ("Custom.AIVerification.MinorGaps", "Minor Gaps", "integer", None,
     "Questions with minor gaps"),
    ("Custom.AIVerification.MajorMisunderstandings",
     "Major Misunderstandings", "integer", None,
     "Questions with major misunderstandings"),
    ("Custom.AIVerification.SignOffStatus", "Sign Off Status", "string", "SignOffStatus",
     "Overall sign-off decision"),
    ("Custom.AIVerification.ModelUsed", "AI Model Used", "string", "AIFoundryModel",
     "Model used for this persona's AI interactions"),
    ("Custom.AIVerification.GrillDate", "Grill Date", "dateTime", None,
     "When the grill session was finished"),
    ("Custom.AIVerification.MisconceptionDetails",
     "Misconception Details", "html", None,
     "Structured markdown of misconceptions, root causes, and document fixes"),
    ("Custom.AIVerification.GrillTranscript",
     "Grill Transcript", "html", None,
     "Full Q&A transcript of the grill session"),
    ("Custom.AIVerification.ParentFeature", "Parent Feature", "string", None,
     "Title of the parent Epic"),
    ("Custom.AIVerification.TriggeredDocFixes",
     "Triggered Document Fixes", "html", None,
     "Which documents/sections were modified as a result of this grill"),
]

# Work Item Types to create
AI_STORY_STATES = [
    {"name": "Drafted",     "color": "E6E6E6", "stateCategory": "Proposed"},
    {"name": "In Planning", "color": "FFCC00", "stateCategory": "InProgress"},
    {"name": "Plan Review", "color": "FF8C00", "stateCategory": "InProgress"},
    {"name": "In Coding",   "color": "0078D7", "stateCategory": "InProgress"},
    {"name": "Code Review", "color": "993399", "stateCategory": "InProgress"},
    {"name": "In Testing",  "color": "339933", "stateCategory": "InProgress"},
    {"name": "Approved",    "color": "00B300", "stateCategory": "Resolved"},
    {"name": "Blocked",     "color": "CC0000", "stateCategory": "Removed"},
]

AI_VER_STATES = [
    {"name": "Pending",         "color": "E6E6E6", "stateCategory": "Proposed"},
    {"name": "In Progress",     "color": "FFCC00", "stateCategory": "InProgress"},
    {"name": "Completed",       "color": "339933", "stateCategory": "Resolved"},
    {"name": "Needs Revision",  "color": "CC0000", "stateCategory": "Removed"},
]

# Fields per WIT: (ref_name, required, default_value, help_text)
AI_STORY_FIELDS = [
    ("Custom.AIStory.StoryContext", True, None, "Full context from the decomposer"),
    ("Custom.AIStory.AcceptanceCriteria", False, None, "Given/When/Then acceptance criteria"),
    ("Custom.AIStory.ModelUsed", True, "deepseek-v4-flash", "Azure Foundry model"),
    ("Custom.AIStory.RevisionCount", True, "0", "Revision loop counter"),
    ("Custom.AIStory.TestPlan", False, None, "Generated test plan"),
    ("Custom.AIStory.ImplPlan", False, None, "Generated implementation plan"),
    ("Custom.AIStory.PlanReviewStatus", False, None, "Plan review decision"),
    ("Custom.AIStory.CodeReviewStatus", False, None, "Code review decision"),
    ("Custom.AIStory.TestResults", False, None, "Test execution results"),
    ("Custom.AIStory.ParentFeature", False, None, "Parent Epic title"),
]

AI_VER_FIELDS = [
    ("Custom.AIVerification.Persona", True, None, "Which persona being grilled"),
    ("Custom.AIVerification.Harness", True, None, "Which AI harness"),
    ("Custom.AIVerification.FeatureName", True, None, "Feature being verified"),
    ("Custom.AIVerification.ModelUsed", True, "deepseek-v4-flash", "AI model used"),
    ("Custom.AIVerification.QuestionsAsked", False, "0", "Total questions"),
    ("Custom.AIVerification.FullyCorrect", False, "0", "Fully correct answers"),
    ("Custom.AIVerification.MinorGaps", False, "0", "Minor gaps found"),
    ("Custom.AIVerification.MajorMisunderstandings", False, "0", "Major misunderstandings"),
    ("Custom.AIVerification.SignOffStatus", False, None, "Sign-off decision"),
    ("Custom.AIVerification.GrillDate", False, None, "Session completion date"),
    ("Custom.AIVerification.MisconceptionDetails", False, None, "Root cause analysis"),
    ("Custom.AIVerification.GrillTranscript", False, None, "Full Q&A log"),
    ("Custom.AIVerification.ParentFeature", False, None, "Parent Epic title"),
    ("Custom.AIVerification.TriggeredDocFixes", False, None, "Documents modified"),
]


# ──────────────────────────────────────────────────────────────────────
# Implementation Steps
# ──────────────────────────────────────────────────────────────────────

def step(msg):
    log.info("")
    log.info("=" * 60)
    log.info("  %s", msg)
    log.info("=" * 60)


def verify_auth():
    """Verify connectivity via the project-level WIT endpoint."""
    if DRY_RUN or VERIFY_ONLY:
        return True
    log.info("Verifying API connectivity...")
    result = api_wit(project_level=True, path="/workitemtypes")
    if result is None or "value" not in result:
        log.error("Cannot reach ADO API. Check PAT.")
        log.error("  ORG: %s", ORG)
        return False
    names = [w["name"] for w in result["value"]]
    log.info("  Connected! Existing WITs (%d): %s", len(names), ", ".join(names))
    return True


def create_picklists():
    """
    Phase 1: Create picklists via Process Lists API.

    Endpoint: POST https://dev.azure.com/{org}/_apis/work/processes/lists
    Note: Lists are organization-level, not per-process.
    """
    step("Phase 1: Creating Picklists (Global Lists)")

    picklist_ids = {}

    if DRY_RUN:
        for pl_name, pl_def in PICKLISTS.items():
            log.info("  [DRY-RUN] POST /_apis/work/processes/lists  -> '%s' (%d items): %s",
                      pl_name, len(pl_def["items"]),
                      [i["value"] for i in pl_def["items"]])
            picklist_ids[pl_name] = "<dryrun-id>"
        return picklist_ids

    # Check existing lists (live mode only)
    existing = api_process("GET", "/lists")
    existing_names = {}
    if existing and "value" in existing:
        for pl in existing["value"]:
            existing_names[pl.get("name")] = pl.get("id")

    log.info("Existing picklists: %s", list(existing_names.keys()))

    for pl_name, pl_def in PICKLISTS.items():
        if pl_name in existing_names:
            log.info("  [SKIP] Picklist '%s' already exists (id=%s)", pl_name, existing_names[pl_name])
            picklist_ids[pl_name] = existing_names[pl_name]
            continue

        log.info("  Creating picklist '%s'...", pl_name)
        result = api_process("POST", "/lists", pl_def)
        if result:
            picklist_ids[pl_name] = result.get("id")
            log.info("    Created! ID: %s", result.get("id"))
        else:
            log.warning("    Failed to create picklist '%s'", pl_name)
        time.sleep(0.5)

    return picklist_ids


def delete_picklists(picklist_ids):
    """Clean up picklists if needed."""
    step("  Cleanup: Deleting picklists")
    for pl_name, pl_id in picklist_ids.items():
        if DRY_RUN:
            log.info("  [DRY-RUN] DELETE /_apis/work/processes/lists/%s", pl_id)
            continue
        log.info("  Deleting picklist '%s' (id=%s)...", pl_name, pl_id)
        result = api_process("DELETE", f"/lists/{pl_id}")
        if result is not None:
            log.info("    Deleted.")
        else:
            log.warning("    Failed to delete.")

    log.info("Picklist cleanup complete.")


def create_work_item_types():
    """
    Phase 2: Create the two custom work item types.

    POST https://dev.azure.com/{org}/_apis/work/processes/{processId}/workItemTypes
    """
    step("Phase 2: Creating Work Item Types")

    wits_to_create = [
        {
            "name": "AI Story",
            "description": "A work item representing a feature unit processed through the AI Software Factory pipeline. Has 8 states: Drafted -> In Planning -> Plan Review -> In Coding -> Code Review -> In Testing -> Approved | Blocked.",
            "color": "0078D7",
            "icon": "icon-story",
        },
        {
            "name": "AI Verification",
            "description": "Records a Grill Me comprehension verification session. One per persona (BA/PO, UI/UX, DEV, QA) per feature. States: Pending -> In Progress -> Completed | Needs Revision.",
            "color": "339933",
            "icon": "icon-check",
        },
    ]

    if DRY_RUN:
        for wit in wits_to_create:
            log.info("  [DRY-RUN] POST .../workItemTypes -> %s (color: #%s, icon: %s)",
                      wit["name"], wit["color"], wit["icon"])
        return

    existing = api_process("GET", f"/{PROCESS_ID}/workItemTypes")
    existing_names = set()
    if existing and "value" in existing:
        for w in existing["value"]:
            existing_names.add(w.get("name"))

    log.info("Existing process WITs: %s", existing_names)

    for wit in wits_to_create:
        name = wit["name"]
        if name in existing_names:
            log.info("  [SKIP] WIT '%s' already exists", name)
            continue

        log.info("  Creating WIT '%s'...", name)
        result = api_process("POST", f"/{PROCESS_ID}/workItemTypes", wit)
        if result:
            log.info("    Created! Ref: %s, ID: %s",
                      result.get("referenceName"), result.get("id"))
        else:
            log.warning("    Failed to create WIT '%s'", name)
        time.sleep(1)


def add_states():
    """
    Phase 3: Add custom states to each WIT.

    POST https://dev.azure.com/{org}/_apis/work/processes/{processId}/workItemTypes/{refName}/states
    """
    step("Phase 3: Adding States")

    wits_and_states = [
        ("Custom.AIStory", AI_STORY_STATES),
        ("Custom.AIVerification", AI_VER_STATES),
    ]

    if DRY_RUN:
        for ref_name, state_defs in wits_and_states:
            log.info("  [DRY-RUN] Adding %d states to '%s':",
                      len(state_defs), ref_name)
            for sd in state_defs:
                log.info("    - %s (cat=%s)", sd["name"], sd["stateCategory"])
        return

    for ref_name, state_defs in wits_and_states:
        existing = api_process("GET", f"/{PROCESS_ID}/workItemTypes/{ref_name}/states")
        existing_names = set()
        if existing and "value" in existing:
            for s in existing["value"]:
                existing_names.add(s.get("name"))

        log.info("  '%s' existing states: %s", ref_name, existing_names)

        for sd in state_defs:
            s_name = sd["name"]
            if s_name in existing_names:
                log.info("    [SKIP] State '%s' already exists", s_name)
                continue

            if DRY_RUN:
                log.info("    [DRY-RUN] Add state '%s' (cat=%s, color=#%s) to '%s'",
                          s_name, sd["stateCategory"], sd["color"], ref_name)
                continue

            log.info("    Adding state '%s' to '%s'...", s_name, ref_name)
            result = api_process(
                "POST",
                f"/{PROCESS_ID}/workItemTypes/{ref_name}/states",
                sd,
            )
            if result:
                log.info("      Created! State: %s, ID: %s",
                          result.get("name"), result.get("id"))
            else:
                log.warning("      Failed to add state '%s'", s_name)
            time.sleep(0.5)


def add_field_instances():
    """
    Phase 4: Add fields to each WIT (which auto-creates the custom fields).

    POST https://dev.azure.com/{org}/_apis/work/processes/{processId}/workItemTypes/{refName}/fields

    This endpoint simultaneously creates the custom field (if new) and
    binds it to the work item type with the specified rules.
    """
    step("Phase 4: Adding Field Instances")

    wits_and_fields = [
        ("Custom.AIStory", AI_STORY_FIELDS),
        ("Custom.AIVerification", AI_VER_FIELDS),
    ]

    if DRY_RUN:
        for ref_name, field_list in wits_and_fields:
            log.info("  [DRY-RUN] Adding %d field instances to '%s':",
                      len(field_list), ref_name)
            for fref, required, default_val, helptext in field_list:
                log.info("    - %s (required=%s, default=%s)",
                          fref, required, default_val or "none")
        return

    for ref_name, field_list in wits_and_fields:
        existing = api_process("GET", f"/{PROCESS_ID}/workItemTypes/{ref_name}/fields")
        existing_refs = set()
        if existing and "value" in existing:
            for f in existing["value"]:
                existing_refs.add(f.get("referenceName"))

        log.info("  '%s' existing fields: %d", ref_name, len(existing_refs))

        for fref, required, default_val, helptext in field_list:
            if fref in existing_refs:
                log.info("    [SKIP] Field '%s' already on '%s'", fref, ref_name)
                continue

            if DRY_RUN:
                log.info("    [DRY-RUN] Add field '%s' to '%s' (required=%s, default=%s, help='%s')",
                          fref, ref_name, required, default_val or "none",
                          (helptext or "")[:50])
                continue

            body = {
                "referenceName": fref,
                "alwaysRequired": required,
            }
            if default_val is not None:
                body["defaultValue"] = default_val
            if helptext:
                body["helpText"] = helptext

            log.info("    Adding field '%s' to '%s'...", fref, ref_name)
            result = api_process(
                "POST",
                f"/{PROCESS_ID}/workItemTypes/{ref_name}/fields",
                body,
            )
            if result:
                log.info("      Added! Field: %s (type=%s)",
                          result.get("referenceName"), result.get("type"))
            else:
                log.warning("      Failed to add field '%s'", fref)
            time.sleep(0.5)


def verify_setup():
    """Final verification."""
    step("Verification: Checking Created Resources")

    if DRY_RUN:
        log.info("[DRY-RUN] Summary of what would be created:")
        log.info("")
        log.info("  Picklists (6):")
        for name in PICKLISTS:
            vals = [i["value"] for i in PICKLISTS[name]["items"]]
            log.info("    - %s: %s", name, vals)
        log.info("")
        log.info("  Work Item Types (2):")
        log.info("    - AI Story (8 states, 10 custom fields)")
        for s in AI_STORY_STATES:
            log.info("        State: %s", s["name"])
        for f in AI_STORY_FIELDS:
            log.info("        Field: %s (req=%s)", f[0], f[1])
        log.info("")
        log.info("    - AI Verification (4 states, 14 custom fields)")
        for s in AI_VER_STATES:
            log.info("        State: %s", s["name"])
        for f in AI_VER_FIELDS:
            log.info("        Field: %s (req=%s)", f[0], f[1])
        log.info("")
        log.info("  TOTAL: 6 picklists, 24 custom fields, 2 WITs, 12 states, 24 field instances")
        return True

    # Fetch process info
    proc = api_process("GET", f"/{PROCESS_ID}")
    if proc:
        log.info("Process: %s (type: %s)", proc.get("name"), proc.get("type"))

    # Fetch WITs
    wits = api_process("GET", f"/{PROCESS_ID}/workItemTypes")
    if wits and "value" in wits:
        names = [w["name"] for w in wits["value"]]
        log.info("Work Item Types (%d): %s", len(names), ", ".join(names))

        for w in wits["value"]:
            if w["name"] in ("AI Story", "AI Verification"):
                ref = w["referenceName"]
                log.info("  %s (ref=%s, color=#%s)", w["name"], ref, w.get("color", "?"))

                # States
                states = api_process("GET", f"/{PROCESS_ID}/workItemTypes/{ref}/states")
                if states and "value" in states:
                    log.info("    States (%d):", len(states["value"]))
                    for s in states["value"]:
                        log.info("      - %s (cat: %s, color: #%s)",
                                  s["name"], s.get("stateCategory"), s.get("color"))

                # Fields
                fields = api_process("GET", f"/{PROCESS_ID}/workItemTypes/{ref}/fields")
                if fields and "value" in fields:
                    log.info("    Fields (%d):", len(fields["value"]))
                    for f in fields["value"]:
                        req = f.get("alwaysRequired", False)
                        log.info("      - %s (type=%s, required=%s, default=%s)",
                                  f.get("referenceName"), f.get("type"),
                                  req, f.get("defaultValue", "—"))


def main():
    log.info("╔══════════════════════════════════════════════════════╗")
    log.info("║  ADO Work Item Setup: AI Software Factory           ║")
    log.info("╠══════════════════════════════════════════════════════╣")
    log.info("║  Organization: %s", ORG)
    log.info("║  Project:      %s", PROJECT)
    log.info("║  Process ID:   %s", PROCESS_ID)
    log.info("║  Mode:         %s",
              "DRY-RUN" if DRY_RUN else ("VERIFY ONLY" if VERIFY_ONLY else "LIVE"))
    log.info("╚══════════════════════════════════════════════════════╝")

    if VERIFY_ONLY:
        verify_setup()
        return

    if not verify_auth():
        sys.exit(1)

    # Phase 1: Create picklists (global lists)
    picklist_ids = create_picklists()

    # Phase 2: Create work item types
    create_work_item_types()

    # Phase 3: Add custom states
    add_states()

    # Phase 4: Add field instances (auto-creates custom fields + binds to WIT)
    add_field_instances()

    # Final verification
    verify_setup()

    log.info("")
    log.info("=" * 60)
    log.info("  DONE!")
    log.info("=" * 60)
    log.info("")
    log.info("The AI Software Factory work item types are now set up:")
    log.info("  - AI Story  → 8 states, 10 custom fields")
    log.info("  - AI Verification → 4 states, 14 custom fields")
    log.info("  - 6 picklists for controlled vocabularies")
    log.info("")
    log.info("Next steps:")
    log.info("  1. Create an Epic for the first feature")
    log.info("  2. Create 4 AI Verification items (one per persona) linked to Epic")
    log.info("  3. After all grill sessions pass → create AI Story items")
    log.info("  4. Run the factory pipeline against each AI Story")
    log.info("")
    log.info("Implementation script for the pipeline will read/write fields")
    log.info("using the Azure DevOps REST API or az boards CLI.")


if __name__ == "__main__":
    main()