---
name: security-check
description: Performs security checks and vulnerability scanning when working with code or files. Use when user asks about security, vulnerabilities, or wants to audit code.
allowed-tools: Read, Grep, Glob
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "echo \"Security check: Executing Bash command: $TOOL_INPUT\""
          once: false
---

# Security Check Skill

## Purpose

This skill helps agents perform security-related tasks including:
- Vulnerability scanning
- Security best practices review
- Dependency checking
- Sensitive data detection
- Common vulnerability patterns

## Instructions

When performing security checks:

1. **Code Review**: Look for:
   - SQL injection vulnerabilities
   - XSS (cross-site scripting) risks
   - Hard-coded credentials or API keys
   - Insecure file permissions
   - Unsafe use of eval() or exec()
   - Missing input validation

2. **Dependencies**: Check for:
   - Known vulnerable packages
   - Outdated dependencies
   - Unnecessary dependencies with security risks

3. **Files**: Scan for:
   - Exposed configuration files (.env, .config)
   - Backup files with sensitive data
   - Temporary files with secrets
   - Log files containing credentials

4. **Reporting**: Always provide:
   - Severity level (Critical, High, Medium, Low)
   - Location of issue
   - Recommendation for fix
   - References to CVE if applicable

## Common Security Patterns

### Hard-coded Secrets
```
# BAD
api_key = "sk-1234567890"
password = "admin123"
db_url = "postgres://user:pass@localhost"

# GOOD
api_key = os.getenv("API_KEY")
password = get_password_from_vault()
db_url = get_database_url()
```

### SQL Injection
```
# BAD
query = f"SELECT * FROM users WHERE id = {user_id}"

# GOOD
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

### XSS Vulnerabilities
```
# BAD
html = f"<div>{user_input}</div>"

# GOOD
html = escape(user_input)
html = f"<div>{html}</div>"
```

## Check Commands

Use these patterns to scan for issues:

```bash
# Check for API keys in code
grep -r "sk-[a-zA-Z0-9]{32,}" --include="*.py" --include="*.js"

# Check for hardcoded passwords
grep -r "password\s*=\s*['\"]" --include="*.py"

# Check for eval/exec usage
grep -r "\.eval\(" --include="*.py"
grep -r "\.exec\(" --include="*.py"
```

## Example Usage

**User request**: "Check this file for security issues"

**Agent response**:
```
Performing security scan of main.py...

🔍 Found 2 security issues:

1. [HIGH] Hard-coded API key (line 42)
   - File: main.py:42
   - Issue: API key is directly stored in code
   - Fix: Use environment variable or secret manager

2. [MEDIUM] eval() usage (line 156)
   - File: main.py:156
   - Issue: Using eval() with user input
   - Fix: Use json.loads() for JSON parsing or ast.literal_eval() for literals

📋 Security Score: 6/10 (Critical issues found)

Recommendations:
- Move all secrets to environment variables
- Implement input validation and sanitization
- Use dependency checker: pip-audit
```

## Additional Resources

For more security patterns, see [reference.md](reference.md)
