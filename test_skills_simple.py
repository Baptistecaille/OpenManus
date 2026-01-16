"""Simple test script for skills system (without full config)."""

import asyncio
from pathlib import Path


async def test_skill_parser():
    """Test skill parser directly."""
    print("=" * 60)
    print("Testing Skill Parser")
    print("=" * 60)

    from app.skills.skill_parser import SkillParser

    # Test parsing a valid skill
    skill_path = Path("skills/examples/code-review")
    print(f"\n📂 Parsing skill at: {skill_path}")

    try:
        skill = SkillParser.parse_skill_md(skill_path)
        print(f"✓ Skill parsed successfully")
        print(f"  Name: {skill.metadata.name}")
        print(f"  Description: {skill.metadata.description[:80]}...")
        print(f"  Allowed tools: {skill.metadata.allowed_tools}")
        print(f"  Content length: {len(skill.content)} chars")
        print(f"  Supporting files: {[str(f.name) for f in skill.supporting_files]}")
    except Exception as e:
        print(f"✗ Failed to parse skill: {e}")


async def test_skill_manager():
    """Test skill manager."""
    print("\n" + "=" * 60)
    print("Testing Skill Manager")
    print("=" * 60)

    from app.skills.skill_manager import SkillManager

    # Create manager
    manager = SkillManager(skills_dir=Path("skills"))
    print(f"\n📦 Created SkillManager with skills_dir: {manager.skills_dir}")

    # Discover skills
    print("\n🔍 Discovering skills...")
    discovered = manager.discover_skills()
    print(f"✓ Discovered {len(discovered)} skills:")
    for name, metadata in discovered.items():
        print(f"  - {name}: {metadata.description[:60]}...")

    # List skills
    print(f"\n📋 Skills list:")
    skills_list = manager.list_skills()
    for name, desc in skills_list.items():
        print(f"  - {name}")

    # Load a skill
    print(f"\n📥 Loading skill: code-review")
    skill = manager.load_skill("code-review")
    if skill:
        print(f"✓ Skill loaded successfully")
        print(f"  Metadata: {skill.metadata}")
        print(f"  Content preview: {skill.content[:200]}...")
    else:
        print("✗ Failed to load skill")


async def test_utils():
    """Test utility functions."""
    print("\n" + "=" * 60)
    print("Testing Utility Functions")
    print("=" * 60)

    from app.skills.utils import (
        apply_string_substitutions,
        normalize_skill_name,
        validate_skill_name,
    )

    # Test name normalization
    print("\n🔤 Testing name normalization:")
    test_names = ["Test Skill", "My_Skill", "ALREADY-NORMALIZED"]
    for name in test_names:
        normalized = normalize_skill_name(name)
        print(f"  '{name}' -> '{normalized}'")

    # Test validation
    print("\n✅ Testing name validation:")
    test_names2 = [
        ("valid-skill", True),
        ("Invalid Skill", False),
        ("x" * 65, False),
    ]
    for name, expected in test_names2:
        result = validate_skill_name(name)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{name[:20]}...' -> {result} (expected {expected})")

    # Test string substitutions
    print("\n🔄 Testing string substitutions:")
    content = "Hello $ARGUMENTS! Session: ${CLAUDE_SESSION_ID}"
    substitutions = {
        "$ARGUMENTS": "World",
        "${CLAUDE_SESSION_ID}": "session-123",
    }
    result = apply_string_substitutions(content, substitutions)
    expected = "Hello World! Session: session-123"
    status = "✓" if result == expected else "✗"
    print(f"  {status} Input: {content}")
    print(f"    Result: {result}")
    print(f"    Expected: {expected}")


async def test_hooks():
    """Test hook system."""
    print("\n" + "=" * 60)
    print("Testing Hook System")
    print("=" * 60)

    from app.skills.hooks import HookManager, Hook, HookEvent

    # Create hook manager
    hook_manager = HookManager()
    print("\n🔗 Created HookManager")

    # Register a test hook
    hook_triggered = []

    async def test_handler(context):
        hook_triggered.append(context)
        print(f"  🎯 Hook triggered with context: {context}")

    hook = Hook(
        event=HookEvent.PRE_TOOL_USE,
        matcher="Bash",
        handler=test_handler,
        once=False,
    )
    hook_manager.register_hook(hook)
    print("✓ Registered test hook for PreToolUse -> Bash")

    # Trigger hooks
    print("\n🔨 Triggering hooks:")
    await hook_manager.trigger_hooks(
        event="PreToolUse",
        tool_name="Bash",
        context={"tool_input": "echo hello"},
    )

    # Verify hook was triggered
    if hook_triggered:
        print(f"✓ Hook triggered successfully: {len(hook_triggered)} times")
    else:
        print("✗ Hook was not triggered")

    # Test once-only hooks
    print("\n🔁 Testing once-only hooks:")
    hook_triggered.clear()

    hook_once = Hook(
        event=HookEvent.POST_TOOL_USE,
        matcher="Read",
        handler=test_handler,
        once=True,
    )
    hook_manager.register_hook(hook_once)
    print("✓ Registered once-only hook")

    # Trigger twice
    await hook_manager.trigger_hooks(
        event="PostToolUse",
        tool_name="Read",
        context={"result": "test"},
    )
    await hook_manager.trigger_hooks(
        event="PostToolUse",
        tool_name="Read",
        context={"result": "test2"},
    )

    print(f"✓ Hook triggered {len(hook_triggered)} time(s) (expected 1)")
    print(f"  Hook executed flag: {hook_once.executed}")


async def main():
    """Run all tests."""
    print("\n🚀 Starting Skills System Tests\n")

    try:
        await test_skill_parser()
        await test_skill_manager()
        await test_utils()
        await test_hooks()

        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
