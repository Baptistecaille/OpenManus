"""Utility functions for skills."""

import re
from typing import Dict


def apply_string_substitutions(
    content: str, substitutions: Dict[str, str]
) -> str:
    """Apply variable substitutions to content.

    Supported variables:
    - $ARGUMENTS: Arguments passed when invoking the skill
    - ${CLAUDE_SESSION_ID}: Current session ID
    - $TOOL_NAME: Name of the tool (in hooks)
    - $TOOL_INPUT: Input to the tool (in hooks)
    - $TOOL_RESULT: Result from tool execution (in hooks)

    Args:
        content: Content with variable placeholders
        substitutions: Dictionary of variable names to values

    Returns:
        Content with substitutions applied
    """
    result = content

    # Apply all substitutions
    for key, value in substitutions.items():
        result = result.replace(key, str(value) if value else "")

    return result


def extract_session_id_from_context(context: Dict) -> str:
    """Extract session ID from context.

    Args:
        context: Context dictionary

    Returns:
        Session ID string
    """
    return context.get("session_id", context.get("CLAUDE_SESSION_ID", "unknown"))


def validate_skill_name(name: str) -> bool:
    """Validate skill name format.

    Args:
        name: Skill name to validate

    Returns:
        True if valid, False otherwise
    """
    if len(name) > 64:
        return False
    return bool(re.match(r"^[a-z0-9_-]+$", name))


def normalize_skill_name(name: str) -> str:
    """Normalize skill name to lowercase with hyphens.

    Args:
        name: Skill name to normalize

    Returns:
        Normalized skill name
    """
    return name.lower().replace(" ", "-").replace("_", "-")
