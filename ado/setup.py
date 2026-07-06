#!/usr/bin/env python3
"""
Azure DevOps Work Item Type Setup: AI Software Factory

Creates custom work item types "AI Story", "AI Verification", and
"AI Agent Run" with all custom fields, picklists, states, transitions,
and form layouts.

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
    "AgentName": {
        "name": "AgentName",
        "items": [
            {"value": "Story Decomposer"},
            {"value": "Test Plan Generator"},
            {"value": "Implementation Planner"},
            {"value": "Plan Reviewer"},
            {"value": "Coder"},
            {"value": "Code Reviewer"},
            {"value": "Test Executor"},
            {"value": "Feature Verifier"},
            {"value": "Orchestrator"},
        ],
    },
    "StageDecision": {
        "name": "StageDecision",
        "items": [
            {"value": "Approved"},
            {"value": "Revisions Requested"},
            {"value": "Changes Requested"},
            {"value": "Completed"},
            {"value": "Tests Failed"},
            {"value": "Failed"},
            {"value": "Escalated"},
        ],
    },
    "TokenSource": {
        "name": "TokenSource",
        "items": [
            {"value": "Reported"},
            {"value": "Estimated"},
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
    ("Custom.AIStory.TotalCostUSD", "Total Cost (USD)", "double", None,
     "Sum of all child AI Agent Run EstimatedCostUSD values"),
    ("Custom.AIStory.PlanRevisionCount", "Plan Revision Count", "integer", None,
     "Number of plan revision loops (max 2)"),
    ("Custom.AIStory.CodeRevisionCount", "Code Revision Count", "integer", None,
     "Number of code revision loops (max 2)"),
    ("Custom.AIStory.TestRevisionCount", "Test Revision Count", "integer", None,
     "Number of test-failure self-repair loops (max 2)"),
    ("Custom.AIStory.ContextBundleScore", "Context Bundle Score", "integer", None,
     "Quality score of input context bundle (0-100), set by Story Decomposer"),
    ("Custom.AIStory.TestPlanScore", "Test Plan Score", "integer", None,
     "Quality score of generated test plan (0-100), set by Plan Reviewer"),
    ("Custom.AIStory.ImplPlanScore", "Impl Plan Score", "integer", None,
     "Quality score of implementation plan (0-100), set by Plan Reviewer"),
    ("Custom.AIStory.CodeQualityScore", "Code Quality Score", "integer", None,
     "Final code review score (0-100), set by Code Reviewer"),
    ("Custom.AIStory.TestPassRate", "Test Pass Rate", "double", None,
     "Percentage of tests that passed (0.0-100.0), set by Test Executor"),
    ("Custom.AIStory.CodeReviewFindings", "Code Review Findings", "html", None,
     "Structured list of findings from Code Reviewer (violations, severity)"),
    ("Custom.AIStory.EstimatedHumanHours", "Estimated Human Hours", "double", None,
     "Rough estimate of human effort this story would have required"),
    ("Custom.AIStory.PullRequestUrl", "Pull Request URL", "string", None,
     "Link to the story branch PR opened by the Coder"),

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

    # ── AI Agent Run fields ──
    ("Custom.AIAgentRun.AgentName", "Agent Name", "string", "AgentName",
     "Which agent was invoked"),
    ("Custom.AIAgentRun.ModelUsed", "Model Used", "string", "AIFoundryModel",
     "AI model that processed this run"),
    ("Custom.AIAgentRun.InputTokens", "Input Tokens", "integer", None,
     "Prompt tokens consumed"),
    ("Custom.AIAgentRun.OutputTokens", "Output Tokens", "integer", None,
     "Completion tokens generated"),
    ("Custom.AIAgentRun.EstimatedCostUSD", "Estimated Cost (USD)", "double", None,
     "Calculated: (InputTokens x price_in) + (OutputTokens x price_out)"),
    ("Custom.AIAgentRun.DurationSeconds", "Duration (seconds)", "integer", None,
     "Wall-clock seconds from invocation to completion"),
    ("Custom.AIAgentRun.QualityScore", "Quality Score", "integer", None,
     "Rubric-anchored 0-100 score (Plan Reviewer, Code Reviewer runs)"),
    ("Custom.AIAgentRun.StageDecision", "Stage Decision", "string", "StageDecision",
     "The verdict this run produced"),
    ("Custom.AIAgentRun.RevisionAttempt", "Revision Attempt", "integer", None,
     "Which attempt this is (1 = first run)"),
    ("Custom.AIAgentRun.ArtifactContent", "Artifact Content", "html", None,
     "The full output artifact (test plan, impl plan, review, test results)"),
    ("Custom.AIAgentRun.ErrorDetails", "Error Details", "html", None,
     "If Failed: full error description and recommended action"),
    ("Custom.AIAgentRun.ParentStoryTitle", "Parent Story Title", "string", None,
     "Denormalized title of the parent AI Story for cross-story queries"),
    ("Custom.AIAgentRun.AgentVersion", "Agent Version", "string", None,
     "Version/hash of the agent instruction file used for this run"),
    ("Custom.AIAgentRun.TokenSource", "Token Source", "string", "TokenSource",
     "Whether token counts are Reported (exact) or Estimated (chars/4)"),
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

AI_RUN_STATES = [
    {"name": "Running",   "color": "FFCC00", "stateCategory": "InProgress"},
    {"name": "Completed", "color": "00B300", "stateCategory": "Resolved"},
    {"name": "Failed",    "color": "CC0000", "stateCategory": "Removed"},
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
    ("Custom.AIStory.TotalCostUSD", False, "0", "Total cost rolled up from Agent Runs"),
    ("Custom.AIStory.PlanRevisionCount", False, "0", "Plan revision loop counter"),
    ("Custom.AIStory.CodeRevisionCount", False, "0", "Code revision loop counter"),
    ("Custom.AIStory.TestRevisionCount", False, "0", "Test self-repair loop counter"),
    ("Custom.AIStory.ContextBundleScore", False, None, "Context bundle quality (0-100)"),
    ("Custom.AIStory.TestPlanScore", False, None, "Test plan quality (0-100)"),
    ("Custom.AIStory.ImplPlanScore", False, None, "Impl plan quality (0-100)"),
    ("Custom.AIStory.CodeQualityScore", False, None, "Code review score (0-100)"),
    ("Custom.AIStory.TestPassRate", False, None, "Test pass percentage"),
    ("Custom.AIStory.CodeReviewFindings", False, None, "Code review findings"),
    ("Custom.AIStory.EstimatedHumanHours", False, None, "Estimated human effort (hours)"),
    ("Custom.AIStory.PullRequestUrl", False, None, "Story branch PR URL"),
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

AI_RUN_FIELDS = [
    ("Custom.AIAgentRun.AgentName", True, None, "Which agent was invoked"),
    ("Custom.AIAgentRun.ModelUsed", True, "deepseek-v4-flash", "AI model for this run"),
    ("Custom.AIAgentRun.AgentVersion", False, None, "Agent instruction file version/hash"),
    ("Custom.AIAgentRun.RevisionAttempt", True, "1", "Attempt number (1 = first)"),
    ("Custom.AIAgentRun.InputTokens", False, "0", "Prompt tokens consumed"),
    ("Custom.AIAgentRun.OutputTokens", False, "0", "Completion tokens generated"),
    ("Custom.AIAgentRun.TokenSource", False, "Estimated", "Reported (exact) or Estimated"),
    ("Custom.AIAgentRun.EstimatedCostUSD", False, "0", "Calculated run cost"),
    ("Custom.AIAgentRun.DurationSeconds", False, "0", "Wall-clock duration"),
    ("Custom.AIAgentRun.QualityScore", False, None, "Rubric-anchored score (reviewers)"),
    ("Custom.AIAgentRun.StageDecision", False, None, "The verdict this run produced"),
    ("Custom.AIAgentRun.ArtifactContent", False, None, "Full output artifact"),
    ("Custom.AIAgentRun.ErrorDetails", False, None, "Error details if Failed"),
    ("Custom.AIAgentRun.ParentStoryTitle", False, None, "Parent AI Story title"),
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


def create_fields(picklist_ids):
    """
    Phase 1b: Create typed custom fields via the Process Fields API.

    Endpoint: POST https://dev.azure.com/{org}/_apis/work/processes/{processId}/fields

    This must run BEFORE add_field_instances: the field-instance endpoint
    binds existing fields to a WIT but cannot itself create fields with
    the correct type (double, dateTime) or picklist bindings.
    """
    step("Phase 1b: Creating Typed Custom Fields")

    if DRY_RUN:
        for ref, name, ftype, picklist, desc in ALL_FIELDS:
            pl = f", picklist={picklist}" if picklist else ""
            log.info("  [DRY-RUN] POST .../%s/fields -> %s (%s%s)",
                      PROCESS_ID, ref, ftype, pl)
        return

    existing = api_process("GET", f"/{PROCESS_ID}/fields")
    existing_refs = set()
    if existing and "value" in existing:
        for f in existing["value"]:
            existing_refs.add(f.get("referenceName"))

    log.info("Existing custom fields: %d", len(existing_refs))

    for ref, name, ftype, picklist, desc in ALL_FIELDS:
        if ref in existing_refs:
            log.info("  [SKIP] Field '%s' already exists", ref)
            continue

        body = {
            "name": name,
            "referenceName": ref,
            "type": ftype,
            "description": desc,
        }
        if picklist:
            pl_id = picklist_ids.get(picklist)
            if not pl_id or pl_id == "<dryrun-id>":
                log.warning("  Picklist '%s' has no id; creating '%s' without binding",
                             picklist, ref)
            else:
                body["pickList"] = {"id": pl_id}

        log.info("  Creating field '%s' (%s)...", ref, ftype)
        result = api_process("POST", f"/{PROCESS_ID}/fields", body)
        if result:
            log.info("    Created! %s", result.get("referenceName"))
        else:
            log.warning("    Failed to create field '%s'", ref)
        time.sleep(0.3)


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
        {
            "name": "AI Agent Run",
            "description": "Records a single AI agent invocation with cost, model, tokens, quality score, and output artifact. One per sub-agent call, child of AI Story. States: Running -> Completed | Failed.",
            "color": "005A9E",
            "icon": "icon-gear",
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
        ("Custom.AIAgentRun", AI_RUN_STATES),
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
        ("Custom.AIAgentRun", AI_RUN_FIELDS),
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
        log.info("  Picklists (%d):", len(PICKLISTS))
        for name in PICKLISTS:
            vals = [i["value"] for i in PICKLISTS[name]["items"]]
            log.info("    - %s: %s", name, vals)
        log.info("")
        log.info("  Typed custom fields (%d)", len(ALL_FIELDS))
        log.info("")
        log.info("  Work Item Types (3):")
        log.info("    - AI Story (%d states, %d custom fields)",
                  len(AI_STORY_STATES), len(AI_STORY_FIELDS))
        for s in AI_STORY_STATES:
            log.info("        State: %s", s["name"])
        for f in AI_STORY_FIELDS:
            log.info("        Field: %s (req=%s)", f[0], f[1])
        log.info("")
        log.info("    - AI Verification (%d states, %d custom fields)",
                  len(AI_VER_STATES), len(AI_VER_FIELDS))
        for s in AI_VER_STATES:
            log.info("        State: %s", s["name"])
        for f in AI_VER_FIELDS:
            log.info("        Field: %s (req=%s)", f[0], f[1])
        log.info("")
        log.info("    - AI Agent Run (%d states, %d custom fields)",
                  len(AI_RUN_STATES), len(AI_RUN_FIELDS))
        for s in AI_RUN_STATES:
            log.info("        State: %s", s["name"])
        for f in AI_RUN_FIELDS:
            log.info("        Field: %s (req=%s)", f[0], f[1])
        log.info("")
        total_states = len(AI_STORY_STATES) + len(AI_VER_STATES) + len(AI_RUN_STATES)
        total_instances = len(AI_STORY_FIELDS) + len(AI_VER_FIELDS) + len(AI_RUN_FIELDS)
        log.info("  TOTAL: %d picklists, %d custom fields, 3 WITs, %d states, %d field instances",
                  len(PICKLISTS), len(ALL_FIELDS), total_states, total_instances)
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
            if w["name"] in ("AI Story", "AI Verification", "AI Agent Run"):
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

    # Phase 1b: Create typed custom fields (types + picklist bindings)
    create_fields(picklist_ids)

    # Phase 2: Create work item types
    create_work_item_types()

    # Phase 3: Add custom states
    add_states()

    # Phase 4: Add field instances (binds existing fields to each WIT)
    add_field_instances()

    # Final verification
    verify_setup()

    log.info("")
    log.info("=" * 60)
    log.info("  DONE!")
    log.info("=" * 60)
    log.info("")
    log.info("The AI Software Factory work item types are now set up:")
    log.info("  - AI Story  → 8 states, %d custom fields", len(AI_STORY_FIELDS))
    log.info("  - AI Verification → 4 states, %d custom fields", len(AI_VER_FIELDS))
    log.info("  - AI Agent Run → 3 states, %d custom fields (observability)", len(AI_RUN_FIELDS))
    log.info("  - %d picklists for controlled vocabularies", len(PICKLISTS))
    log.info("")
    log.info("Next steps:")
    log.info("  1. Create an Epic for the first feature")
    log.info("  2. Create 4 AI Verification items (one per persona) linked to Epic")
    log.info("  3. After all grill sessions pass → create AI Story items")
    log.info("  4. Run the factory pipeline against each AI Story")
    log.info("  5. The Orchestrator creates AI Agent Run children per invocation")
    log.info("     (put them in a dedicated area path to keep boards clean)")
    log.info("")
    log.info("Implementation script for the pipeline will read/write fields")
    log.info("using the Azure DevOps REST API or az boards CLI.")


if __name__ == "__main__":
    main()