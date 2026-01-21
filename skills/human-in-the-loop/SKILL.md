---
name: human-in-the-loop
description: Enables agents to ask humans for clarification when faced with ambiguous requests, missing context, or multiple interpretations. Use when user intent is unclear and proceeding would risk incorrect execution.
allowed-tools: ask_human, human_in_the_loop
---

# Human-in-the-Loop Clarification

## Purpose

This skill teaches agents how to effectively use human clarification to ensure accurate task completion. When faced with ambiguity, uncertainty, or missing information, agents should proactively seek clarification rather than making assumptions.

## Tools Available

### ask_human
Simple question-asking tool for basic clarification requests.

Use for:
- Quick questions during planning
- Simple clarification needs
- Non-critical requests

### human_in_the_loop
Production-grade HITL tool with configurable approval levels.

Use for:
- Critical actions requiring approval
- Multi-step operations with risk
- Sensitive operations
- High-cost operations
- Situations requiring accountability

## When to Use Each Tool

### Use `ask_human` when:
- Request is slightly unclear but not critical
- Need quick clarification on one specific point
- Low-stakes clarification needs
- During exploratory phase

### Use `human_in_the_loop` when:
- Executing code changes in production
- Modifying critical files or configurations
- Running potentially dangerous operations
- Actions that could have significant impact
- Multi-step processes where each step should be approved
- Need approval audit trail

## Criticality Levels

When using `human_in_the_loop`, specify appropriate criticality:

- **low**: Informational actions, auto-approved (logging only)
- **medium**: Standard operations requiring quick approval
- **high**: Important actions needing careful review
- **critical**: Blocking actions until explicitly approved

## Clarification Protocol

### Step 1: Recognize Uncertainty
```
I notice [specific ambiguity in the request].
This could mean [option A] or [option B].
```

### Step 2: Choose Right Tool

- Simple clarification → `ask_human`
- Critical action → `human_in_the_loop` with appropriate criticality

### Step 3: Ask Targeted Question

With `ask_human`:
```
ask_human(inquire="Your question here")
```

With `human_in_the_loop`:
```
human_in_the_loop(
    action_description="Clear action description",
    criticality="medium",
    context={"file": "path", "reason": "why"},
    timeout_seconds=300,
    fallback_action="deny"
)
```

### Step 4: Wait for Response
Use the tool's built-in timeout and response handling.

### Step 5: Proceed Based on Response
- Approved → Continue with action
- Denied → Ask for clarification or propose alternative
- Modified → Adjust action according to feedback
- Timeout → Handle according to fallback_action

## Best Practices

### Efficiency
- Ask the minimum questions needed to proceed confidently
- Batch related questions when possible
- Use previous context to avoid redundant questions

### Professionalism
- Explain your reasoning before asking
- Respect user time by being concise
- Acknowledge when clarification resolves the issue

### Error Prevention
- Never assume user intent
- When in doubt, ask
- Document assumptions if clarification isn't possible

### Criticality Management
- Default to `medium` for uncertain actions
- Use `low` for routine, low-risk actions
- Use `high` for significant changes
- Use `critical` for dangerous or irreversible actions

## Examples

### Example 1: Simple Clarification with ask_human

**User**: "Update the config"

**Agent Thinking**: Multiple config files exist, unclear which one.

**Agent Action**:
```
ask_human(inquire="I found 3 config files. Which one should I update: config.toml, settings.json, or app.config?")
```

### Example 2: Critical Action with human_in_the_loop

**User**: "Delete the user database"

**Agent Thinking**: Destructive action requiring approval.

**Agent Action**:
```
human_in_the_loop(
    action_description="Delete the user database file",
    criticality="critical",
    context={"file": "users.db", "backup": "none"},
    timeout_seconds=60
)
```

### Example 3: Multi-step with Approvals

**User**: "Refactor the payment processing code"

**Agent Action**:
```
human_in_the_loop(
    action_description="Replace payment processor with new implementation",
    criticality="high",
    context={"file": "payment.py", "reason": "security upgrade"},
    timeout_seconds=120
)
```

### Example 4: Feature Scope

**User**: "Add authentication"

**Agent Action**:
```
ask_human(inquire="For user authentication, would you like me to implement JWT token-based auth, OAuth with Google/GitHub, or session-based authentication?")
```

## Error Handling

### When User Can't Provide Information
- Use reasonable defaults and document assumptions
- Ask if they want to proceed with assumptions
- Offer to implement with placeholders for later customization

### Tool Failures
- If `ask_human` fails, explain the limitation
- If `human_in_the_loop` times out, respect fallback_action
- If approval is denied, ask for clarification or propose alternatives

## Integration with Workflows

### Planning Phase
- Use `ask_human` for quick clarification needs
- Use `human_in_the_loop` when planning critical operations

### Implementation Phase
- Use `human_in_the_loop` with appropriate criticality for each major step
- Log all approvals for audit trail

### Verification Phase
- Use `human_in_the_loop` for production deployments
- Confirm expectations match results

## Success Criteria

The skill is successfully applied when:
- Agents ask for clarification instead of making wrong assumptions
- Questions are clear and actionable
- Critical actions receive proper approval
- User intent is accurately captured
- Implementation matches user expectations
- Appropriate tools are used based on action criticality