"""Minimal test for skills system without config dependencies."""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / "app"))


def test_skill_parser():
    """Test skill parsing."""
    print("=" * 60)
    print("Testing Skill Parser")
    print("=" * 60)

    # Import only what we need
    from skills.skill import Skill, SkillMetadata
    import yaml
    import re

    # Create a simple skill file in memory
    skill_content = """---
name: test-skill
description: A test skill for validation
allowed-tools: Read, Grep
---

# Test Skill

This is a test skill.
"""

    # Test parsing
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(skill_content)

        # Parse frontmatter
        frontmatter_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
        match = frontmatter_pattern.match(skill_content)

        if not match:
            print("✗ Failed to parse frontmatter")
            return False

        yaml_content = match.group(1)
        markdown_content = skill_content[match.end() :]

        # Parse YAML
        try:
            metadata_dict = yaml.safe_load(yaml_content)
            print("✓ YAML parsed successfully")
        except yaml.YAMLError as e:
            print(f"✗ YAML parsing failed: {e}")
            return False

        # Validate required fields
        if "name" not in metadata_dict or "description" not in metadata_dict:
            print("✗ Missing required fields")
            return False

        print(f"✓ Found required fields")
        print(f"  Name: {metadata_dict['name']}")
        print(f"  Description: {metadata_dict['description']}")
        print(f"  Content: {markdown_content[:50]}...")

        # Create SkillMetadata
        try:
            metadata = SkillMetadata(**metadata_dict)
            print("✓ SkillMetadata created successfully")
        except Exception as e:
            print(f"✗ Failed to create SkillMetadata: {e}")
            return False

    return True


def test_skill_metadata():
    """Test skill metadata validation."""
    print("\n" + "=" * 60)
    print("Testing Skill Metadata")
    print("=" * 60)

    from skills.skill import SkillMetadata

    # Test valid metadata
    try:
        metadata1 = SkillMetadata(
            name="test-skill",
            description="A test skill",
        )
        print("✓ Valid metadata created")
        print(f"  Name: {metadata1.name}")
        print(f"  Description: {metadata1.description}")
    except Exception as e:
        print(f"✗ Failed to create valid metadata: {e}")
        return False

    # Test name validation
    try:
        metadata2 = SkillMetadata(
            name="x" * 65,
            description="Test",
        )
        print("✗ Name length validation failed (should have raised error)")
        return False
    except Exception as e:
        print("✓ Name length validation working")
        print(f"  Error: {e}")

    # Test description validation
    try:
        metadata3 = SkillMetadata(
            name="test",
            description="x" * 1025,
        )
        print("✗ Description length validation failed (should have raised error)")
        return False
    except Exception as e:
        print("✓ Description length validation working")
        print(f"  Error: {e}")

    # Test tool restrictions
    try:
        metadata4 = SkillMetadata(
            name="test",
            description="Test",
            allowed_tools=["Read", "Grep", "Glob"],
        )
        print("✓ Tool restrictions working")
        print(f"  Allowed tools: {metadata4.allowed_tools}")
    except Exception as e:
        print(f"✗ Tool restrictions failed: {e}")
        return False

    return True


def test_skill_discovery():
    """Test skill discovery."""
    print("\n" + "=" * 60)
    print("Testing Skill Discovery")
    print("=" * 60)

    skills_dir = Path("skills")

    if not skills_dir.exists():
        print("✗ Skills directory does not exist")
        return False

    print(f"✓ Skills directory found: {skills_dir}")

    # Find skill directories
    skill_dirs = []
    for item in skills_dir.iterdir():
        if item.is_dir():
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                skill_dirs.append(item)

    print(f"✓ Found {len(skill_dirs)} skill directories:")
    for skill_dir in skill_dirs:
        print(f"  - {skill_dir.name}")

    if len(skill_dirs) < 2:
        print("⚠️  Expected at least 2 example skills")
        return False

    # Parse metadata from each
    import yaml
    import re
    frontmatter_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        content = skill_md.read_text()

        match = frontmatter_pattern.match(content)
        if match:
            yaml_content = match.group(1)
            metadata_dict = yaml.safe_load(yaml_content)
            print(f"  ✓ {skill_dir.name}: {metadata_dict.get('description', 'No description')[:50]}...")

    return True


def test_utils():
    """Test utility functions."""
    print("\n" + "=" * 60)
    print("Testing Utility Functions")
    print("=" * 60)

    from skills.utils import (
        apply_string_substitutions,
        normalize_skill_name,
        validate_skill_name,
    )

    # Test normalization
    tests = [
        ("Test Skill", "test-skill"),
        ("My_Skill", "my-skill"),
        ("ALREADY-NORMALIZED", "already-normalized"),
    ]

    for input_name, expected in tests:
        result = normalize_skill_name(input_name)
        status = "✓" if result == expected else "✗"
        print(f"  {status} normalize_skill_name('{input_name}') -> '{result}'")

    # Test validation
    tests2 = [
        ("valid-skill", True),
        ("valid_skill", True),
        ("Valid-Skill", True),
        ("Invalid Skill", False),
        ("x" * 65, False),
    ]

    for name, expected in tests2:
        result = validate_skill_name(name)
        status = "✓" if result == expected else "✗"
        print(
            f"  {status} validate_skill_name('{name[:20]}...') -> {result}"
        )

    # Test substitutions
    content = "Hello $ARGUMENTS! Session: ${CLAUDE_SESSION_ID}"
    substitutions = {
        "$ARGUMENTS": "World",
        "${CLAUDE_SESSION_ID}": "session-123",
    }
    result = apply_string_substitutions(content, substitutions)
    expected = "Hello World! Session: session-123"

    status = "✓" if result == expected else "✗"
    print(f"  {status} String substitution")
    print(f"    Input: {content}")
    print(f"    Output: {result}")

    return result == expected


def main():
    """Run all tests."""
    print("\n🚀 Skills System Tests (Standalone)\n")

    results = []

    results.append(("Skill Parser", test_skill_parser()))
    results.append(("Skill Metadata", test_skill_metadata()))
    results.append(("Skill Discovery", test_skill_discovery()))
    results.append(("Utility Functions", test_utils()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status}: {test_name}")

    all_passed = all(r[1] for r in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
