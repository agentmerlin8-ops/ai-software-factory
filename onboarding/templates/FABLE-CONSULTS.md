# Fable Consults — process-improvement log

The scarce frontier model (meta-advisor) is used ONLY for bounded
process-improvement consults (runbook policy). Each consult is logged here
with its disposition so the spend is auditable and measurable.

**Cadence:** phase boundaries or every ~5 merged stories, whichever first.
**Budget rule:** one bounded question per consult; input = runbook + field
notes + DASHBOARD metrics only (no code, no full context bundle).
**Kill rule:** two consecutive consults with nothing adopted → stop consulting.

| # | Date | Question asked | Recommendations (summary) | Disposition |
|---|------|----------------|---------------------------|-------------|

## Disposition legend

- **ADOPTED** → patched into runbook/skill; note the commit
- **REJECTED** → record why (cost, gate change vetoed, contradicts field note)
- **DEFERRED** → parked until its gate condition is met
- **PENDING** → awaits the human's decision on a gate change

## Effectiveness review

At each consult, compare revision-loop rate and escalation count in
DASHBOARD.md metrics against the previous consult's window.
