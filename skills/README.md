# Skills Directory

This directory contains skills for OpenManus agents.

## What is a Skill?

A Skill is a markdown file (SKILL.md) that teaches the agent how to perform specific tasks. When you ask the agent something that matches a skill's description, it will automatically apply that skill's instructions.

## Creating a New Skill

1. Create a new directory: `skills/my-skill/`
2. Add a `SKILL.md` file with the following structure:

```markdown
---
name: my-skill
description: Brief description of what this skill does and when to use it
allowed-tools: Read, Grep, Glob
---

# My Skill

Instructions for the agent...


```

## Skill Metadata Fields

- **name**: Skill name (must match directory name)
- **description**: What the skill does and when to use it (max 1024 chars)
- **allowed-tools**: Tools the agent can use without asking (optional)
- **model**: Model to use when skill is active (optional)
- **context**: Set to "fork" to run in isolated context (optional)
- **user-invocable**: Whether skill can be invoked manually (default: true)
