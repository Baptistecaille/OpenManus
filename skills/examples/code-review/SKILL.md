---
name: code-review
description: Reviews code for quality, best practices, and potential issues. Use when user asks to review code, check for bugs, or evaluate code quality.
allowed-tools: Read, Grep, Glob
---

# Code Review Skill

## Instructions

When reviewing code, follow this structured approach:

1. **Read and Understand**: First, understand what the code is trying to accomplish
2. **Identify Issues**: Look for:
   - Bugs and logic errors
   - Security vulnerabilities
   - Performance issues
   - Code style violations
   - Missing error handling
   - Documentation gaps

3. **Provide Feedback**:
   - Start with overall assessment (good/poor, strengths/weaknesses)
   - List specific issues with line numbers
   - Suggest concrete improvements
   - Explain why each issue matters

## Best Practices Checklist

- [ ] Variable names are descriptive
- [ ] Functions have single responsibility
- [ ] Error handling is appropriate
- [ ] No hard-coded values (use constants)
- [ ] Code is commented where complex
- [ ] No code duplication (DRY principle)
- [ ] Edge cases are handled
- [ ] No security vulnerabilities (XSS, injection, etc.)

## Example

**Input**: "Review the code in src/main.py"

**Output**:
```
Overall: The code is well-structured but has some issues.

Issues found:
1. Line 15: Missing error handling for file operations
2. Line 23: Hard-coded value "1024" should be a constant
3. Line 45: Potential buffer overflow if input exceeds array size

Recommendations:
- Add try-catch blocks around file I/O (line 15)
- Define MAX_BUFFER_SIZE = 1024 at top of file
- Add input validation before array assignment (line 45)
```
