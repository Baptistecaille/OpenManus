"""Unit tests for skills module."""

import pytest
from pathlib import Path
from app.skills.skill import Skill, SkillMetadata
from app.skills.skill_parser import SkillParser
from app.skills.skill_manager import SkillManager
from app.skills.utils import (
    apply_string_substitutions,
    normalize_skill_name,
    validate_skill_name,
)


def test_skill_metadata_validation():
    """Test skill metadata validation."""
    # Valid metadata
    metadata = SkillMetadata(
        name="test-skill",
        description="A test skill for testing",
    )
    assert metadata.name == "test-skill"
    assert metadata.description == "A test skill for testing"
    assert metadata.user_invocable is True

    # Test name normalization
    metadata = SkillMetadata(
        name="Test_Skill",
        description="Test",
    )
    assert metadata.name == "test_skill"

    # Test name length validation
    with pytest.raises(ValueError, match="must be 64 characters or less"):
        SkillMetadata(
            name="x" * 65,
            description="Test",
        )

    # Test description length validation
    with pytest.raises(ValueError, match="must be 1024 characters or less"):
        SkillMetadata(
            name="test",
            description="x" * 1025,
        )


def test_skill_parser_valid():
    """Test parsing a valid SKILL.md file."""
    skill_path = Path("skills/examples/code-review")
    skill = SkillParser.parse_skill_md(skill_path)

    assert skill.metadata.name == "code-review"
    assert skill.metadata.description is not None
    assert len(skill.content) > 0
    assert skill.path == skill_path


def test_skill_parser_missing_file():
    """Test parser with missing SKILL.md."""
    skill_path = Path("nonexistent")

    with pytest.raises(FileNotFoundError):
        SkillParser.parse_skill_md(skill_path)


def test_skill_manager_discovery():
    """Test skill discovery."""
    manager = SkillManager(skills_dir=Path("skills"))

    metadata = manager.discover_skills()

    assert len(metadata) > 0
    assert "code-review" in metadata
    assert "commit-message" in metadata


def test_skill_manager_list_skills():
    """Test listing skills."""
    manager = SkillManager(skills_dir=Path("skills"))
    manager.discover_skills()

    skills_list = manager.list_skills()

    assert isinstance(skills_list, dict)
    assert len(skills_list) > 0


def test_skill_manager_load_skill():
    """Test loading a skill."""
    manager = SkillManager(skills_dir=Path("skills"))
    manager.discover_skills()

    skill = manager.load_skill("code-review")

    assert skill is not None
    assert skill.metadata.name == "code-review"
    assert skill in manager.skills.values()


def test_skill_utils_normalization():
    """Test skill name normalization."""
    assert normalize_skill_name("Test Skill") == "test-skill"
    assert normalize_skill_name("My_Skill") == "my-skill"
    assert normalize_skill_name("ALREADY-NORMALIZED") == "already-normalized"


def test_skill_utils_validation():
    """Test skill name validation."""
    assert validate_skill_name("valid-skill") is True
    assert validate_skill_name("Valid_Skill") is True
    assert validate_skill_name("valid-skill-123") is True
    assert validate_skill_name("Invalid Skill") is False
    assert validate_skill_name("x" * 65) is False


def test_string_substitutions():
    """Test string substitutions."""
    content = "Hello $ARGUMENTS! Session: ${CLAUDE_SESSION_ID}"
    substitutions = {
        "$ARGUMENTS": "World",
        "${CLAUDE_SESSION_ID}": "session-123",
    }

    result = apply_string_substitutions(content, substitutions)

    assert result == "Hello World! Session: session-123"


def test_skill_get_full_instructions():
    """Test getting full instructions from skill."""
    metadata = SkillMetadata(
        name="test",
        description="Test description",
    )
    skill = Skill(
        metadata=metadata,
        content="Instructions here",
        path=Path("test"),
    )

    instructions = skill.get_full_instructions()

    assert "# test" in instructions
    assert "Instructions here" in instructions


def test_skill_allowed_tools():
    """Test getting allowed tools list."""
    metadata = SkillMetadata(
        name="test",
        description="Test",
        allowed_tools=["Read", "Grep"],
    )
    skill = Skill(
        metadata=metadata,
        content="",
        path=Path("test"),
    )

    tools = skill.get_allowed_tools_list()

    assert tools == ["Read", "Grep"]


def test_skill_has_hooks():
    """Test checking if skill has hooks."""
    # Skill without hooks
    metadata1 = SkillMetadata(name="test1", description="Test")
    skill1 = Skill(metadata=metadata1, content="", path=Path("test"))

    assert skill1.has_hooks() is False

    # Skill with hooks
    metadata2 = SkillMetadata(
        name="test2",
        description="Test",
        hooks={"PreToolUse": [{"matcher": "Bash", "type": "command"}]},
    )
    skill2 = Skill(metadata=metadata2, content="", path=Path("test"))

    assert skill2.has_hooks() is True
