# Skills System for OpenManus

## Overview

The Skills System allows OpenManus agents to dynamically load and apply specialized instructions based on user requests, similar to Anthropic's Agent Skills.

## Features

- **Automatic Discovery**: Skills are automatically discovered from the `skills/` directory
- **LLM-based Matching**: Uses the LLM to intelligently match user requests to relevant skills
- **Tool Restrictions**: Skills can specify which tools the agent can use
- **Hooks**: Skills can define lifecycle hooks (PreToolUse, PostToolUse, Stop)
- **Progressive Disclosure**: Supporting files (docs, examples, scripts) are loaded only when needed
- **Multi-Agent Support**: Works with all agents inheriting from `BaseAgent`

## Architecture

```
app/skills/
├── __init__.py              # Public API exports
├── skill.py                 # Skill and SkillMetadata models
├── skill_parser.py          # SKILL.md file parser
├── skill_manager.py         # Discovery and loading manager
├── skill_matcher.py         # LLM-based matching
├── hooks.py                # Hook system for events
└── utils.py                # Utility functions

skills/                       # User skills directory
├── README.md               # This file
└── examples/              # Example skills
    ├── code-review/
    └── commit-message/
```

## Quick Start

### 1. Create a Skill

Create a new directory in `skills/` with a `SKILL.md` file:

```bash
mkdir -p skills/my-skill
touch skills/my-skill/SKILL.md
```

Add content to `SKILL.md`:

```markdown
---
name: my-skill
description: Does X when user mentions Y. Use when user asks about Z.
---

# My Skill

Instructions for the agent...
```

### 2. Use Skills with an Agent

Skills are automatically available to all agents:

```python
from app.agent.manus import Manus
from pathlib import Path

# Agent will automatically discover and use skills
agent = await Manus.create()

# Skills are matched automatically when processing requests
await agent.run("Review my code")
```

### 3. Manual Skill Control

```python
# Enable/disable skills
agent.enable_skills()
agent.disable_skills()

# Clear active skills
agent.clear_active_skills()

# List active skills
active = agent.get_active_skills_names()
```

## Skill Format

### SKILL.md Structure

```markdown
---
name: skill-name
description: What the skill does and when to use it
allowed-tools: Read, Grep, Glob
model: gpt-4o
context: fork
user-invocable: true
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/check.sh $TOOL_INPUT"
          once: true
---

# Skill Title

Instructions and examples...
```

### Metadata Fields

| Field | Type | Required | Description |
|--------|-------|-----------|-------------|
| `name` | string | Yes | Skill name (max 64 chars, lowercase letters/numbers/hyphens) |
| `description` | string | Yes | What skill does and when to use it (max 1024 chars) |
| `allowed-tools` | list | No | Tools agent can use without asking |
| `model` | string | No | Model to use when skill is active |
| `context` | string | No | Set to "fork" to run in isolated context |
| `user-invocable` | bool | No | Whether skill can be invoked manually (default: true) |
| `hooks` | dict | No | Hook definitions for lifecycle events |

### Supporting Files

Skills can include additional files for detailed documentation and scripts:

```
my-skill/
├── SKILL.md              # Main file (required)
├── reference.md          # Detailed documentation
├── examples.md           # Usage examples
└── scripts/
    └── helper.py        # Utility scripts
```

Reference them in `SKILL.md`:

```markdown
For complete API details, see [reference.md](reference.md)
For usage examples, see [examples.md](examples.md)
```

## Hooks

Hooks allow skills to react to events during execution.

### Hook Types

- **PreToolUse**: Before a tool is executed
- **PostToolUse**: After a tool completes
- **Stop**: When agent stops execution

### Hook Configuration

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/check.sh $TOOL_INPUT"
          once: true
  PostToolUse:
    - matcher: "Read"
      hooks:
        - type: function
          # Function handler is registered programmatically
```

### Variables Available in Hooks

- `$TOOL_NAME`: Name of the tool being executed
- `$TOOL_INPUT`: Arguments passed to the tool
- `$TOOL_RESULT`: Output from the tool (PostToolUse only)

## String Substitutions

Skills support variable substitutions in content and commands:

- `$ARGUMENTS`: Arguments passed when invoking the skill
- `${CLAUDE_SESSION_ID}`: Current session ID
- `$TOOL_NAME`: Tool name (in hooks)
- `$TOOL_INPUT`: Tool input (in hooks)
- `$TOOL_RESULT`: Tool result (in hooks)

Example:

```markdown
Log the following to logs/${CLAUDE_SESSION_ID}.log:

$ARGUMENTS
```

## Skill Matching

The system uses the LLM to match user requests to skills based on descriptions.

### How Matching Works

1. Agent receives a user request
2. On the first step, `match_and_apply_skill()` is called
3. LLM analyzes the request against all skill descriptions
4. If a match is found, the skill is loaded and applied
5. Skill instructions are injected into the system prompt

### Tips for Good Descriptions

Write descriptions that include:
- **What the skill does**: Specific capabilities
- **When to use it**: Trigger phrases users would say
- **Keywords**: Terms that would match user intent

**Bad description:**
```
description: Helps with code
```

**Good description:**
```
description: Reviews code for quality, best practices, and potential issues. Use when user asks to review code, check for bugs, or evaluate code quality.
```

## API Reference

### SkillManager

```python
from app.skills import SkillManager

manager = SkillManager(skills_dir=Path("skills"))

# Discover all skills
metadata = manager.discover_skills()

# Load a specific skill
skill = manager.load_skill("code-review")

# List available skills
skills_list = manager.list_skills()

# Get skill metadata without loading
metadata = manager.get_skill_metadata("code-review")
```

### BaseAgent Skill Methods

```python
# Match and apply skill for a request
applied = await agent.match_and_apply_skill("Review my code")

# Apply a specific skill
skill = await agent.skill_manager.load_skill("code-review")
await agent.apply_skill(skill)

# Remove a skill
await agent.remove_skill(skill)

# Clear all active skills
agent.clear_active_skills()

# Get active skill names
names = agent.get_active_skills_names()

# Enable/disable skill matching
agent.enable_skills()
agent.disable_skills()
```

### HookManager

```python
from app.skills import HookManager, Hook, HookEvent

manager = HookManager()

# Register a hook
hook = Hook(
    event=HookEvent.PRE_TOOL_USE,
    matcher="Bash",
    handler=my_handler_function,
    once=False,
)
manager.register_hook(hook)

# Trigger hooks manually
await manager.trigger_hooks(
    event=HookEvent.PRE_TOOL_USE,
    tool_name="Bash",
    context={"tool_input": "echo hello"},
)

# Clear all hooks
manager.clear_hooks()
```

## Testing

Run the skills test suite:

```bash
python test_skills.py
```

Run unit tests:

```bash
pytest tests/test_skills.py -v
```

## Troubleshooting

### Skill Not Triggering

1. Check the description includes trigger keywords
2. Verify skill is in `skills/` directory
3. Check logs for matching errors
4. Try rephrasing the request

### Skill Not Loading

1. Ensure `SKILL.md` exists in the skill directory
2. Validate YAML frontmatter format (must start with `---`)
3. Check for YAML syntax errors
4. Run with `--debug` flag for detailed errors

### Hooks Not Firing

1. Verify hook event names are correct (PreToolUse, PostToolUse, Stop)
2. Check the matcher matches tool names exactly
3. Ensure hooks are registered before tool execution
4. Check logs for hook errors

## Examples

See `skills/examples/` for complete skill examples:

- **code-review**: Reviews code for quality and best practices
- **commit-message**: Generates conventional commit messages

## Contributing

To contribute a new skill:

1. Create the skill in `skills/examples/your-skill/`
2. Add a comprehensive `SKILL.md` with examples
3. Test the skill with `test_skills.py`
4. Add documentation for the skill
5. Submit a pull request

## License

This skills system is part of OpenManus and follows the same license.
