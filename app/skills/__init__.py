"""Skills module for OpenManus.

This module provides a skill-based system similar to Anthropic's Agent Skills,
allowing agents to dynamically load and apply specialized instructions based on
user requests.
"""

from .skill import Skill, SkillMetadata
from .skill_manager import SkillManager
from .skill_matcher import SkillMatcher
from .hooks import HookEvent, Hook, HookManager

__all__ = [
    "Skill",
    "SkillMetadata",
    "SkillManager",
    "SkillMatcher",
    "HookEvent",
    "Hook",
    "HookManager",
]
