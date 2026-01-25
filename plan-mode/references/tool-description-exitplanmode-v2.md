<!--
name: 'Tool Description: ExitPlanMode v2 (Strict)'
description: Strict v2 guidance for ExitPlanMode with quality-gate requirements
ccVersion: 2.1.0
variables:
  - ASK_USER_QUESTION_TOOL_NAME
-->
Use this tool ONLY after the plan file is complete, unambiguous, and has passed the plan quality gates.

## Preconditions (MUST)
1. The plan is written to the plan file specified by the plan mode system reminder.
2. Plan Quality Gates are fully passed (see `references/plan-quality-gates.md`).
3. All user clarifications have been incorporated into the plan file.

## What This Tool Does
- Signals that planning is complete and the user can review the plan.
- Does NOT accept plan content in parameters; it reads the plan file you wrote.
- Ends plan mode after user approval.

## Ambiguity Handling (Strict)
If any ambiguity remains:
1. Ask the user with ${ASK_USER_QUESTION_TOOL_NAME}.
2. Update the plan file with their response.
3. Re-present the updated plan.
4. Only then call ExitPlanMode.

## Examples
1. Task: "Implement SSO" and IdP choice is unclear → Ask first, update plan, THEN ExitPlanMode.
2. Task: "Refactor payment service" with a complete plan + tests → ExitPlanMode.
