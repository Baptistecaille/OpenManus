---
name: commit-message
description: Generates clear, conventional commit messages from git diffs. Use when user asks to create a commit message, review staged changes, or format git commits.
---

# Commit Message Generator

## Instructions

Generate commit messages using the Conventional Commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Performance improvement
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

## Format Rules

1. Use imperative mood ("add" not "added" or "adds")
2. Keep subject under 50 characters
3. Do not end subject with period
4. Use body to explain what and why (not how)
5. Reference issues in footer

## Process

1. Run `git diff --staged` to see changes
2. Analyze the diff to understand what changed
3. Generate appropriate commit message
4. Provide explanation of why this format is used

## Example

**Input**: "Create a commit message for my changes"

**Output**:
```
feat(auth): add OAuth2 login support

Implements OAuth2 authentication flow with Google and GitHub providers.
Users can now authenticate using third-party accounts.

Closes #123
```
