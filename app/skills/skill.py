"""Skill data models."""

from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class SkillMetadata(BaseModel):
    """Metadata for a skill extracted from YAML frontmatter."""

    name: str = Field(..., description="Skill name. Must match directory name.")
    description: str = Field(
        ...,
        description="What the skill does and when to use it. Used for LLM-based matching.",
    )
    allowed_tools: Optional[List[str]] = Field(
        default=None,
        description="Tools Claude can use without asking when this skill is active.",
    )
    model: Optional[str] = Field(
        default=None,
        description="Model to use when this skill is active (e.g., 'gpt-4o')",
    )
    context: Optional[str] = Field(
        default=None,
        description="Set to 'fork' to run the skill in a forked context.",
    )
    user_invocable: bool = Field(
        default=True,
        description="Whether the skill appears in slash command menu.",
    )
    hooks: Optional[Dict[str, List[Dict[str, Any]]]] = Field(
        default=None, description="Hooks defined in this skill's lifecycle."
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate skill name format."""
        if len(v) > 64:
            raise ValueError("Skill name must be 64 characters or less")
        if not all(c.isalnum() or c in "-_" for c in v.lower()):
            raise ValueError(
                "Skill name must only contain lowercase letters, numbers, and hyphens/underscores"
            )
        return v.lower()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate skill description length."""
        if len(v) > 1024:
            raise ValueError("Skill description must be 1024 characters or less")
        return v


class Skill(BaseModel):
    """Represents a complete skill with metadata and content."""

    metadata: SkillMetadata = Field(..., description="Skill metadata from YAML frontmatter")
    content: str = Field(..., description="Markdown instructions for the agent")
    path: Path = Field(..., description="Directory path where the skill is located")
    supporting_files: List[Path] = Field(
        default_factory=list,
        description="List of supporting files (reference docs, examples, scripts)",
    )

    def get_full_instructions(self) -> str:
        """Get the complete instructions including skill content."""
        return f"# {self.metadata.name}\n\n{self.content}"

    def get_allowed_tools_list(self) -> Optional[List[str]]:
        """Get the list of allowed tools for this skill."""
        return self.metadata.allowed_tools

    def has_hooks(self) -> bool:
        """Check if the skill has any hooks defined."""
        return self.metadata.hooks is not None and len(self.metadata.hooks) > 0

    def __repr__(self) -> str:
        return f"Skill(name='{self.metadata.name}', description='{self.metadata.description[:50]}...')"
