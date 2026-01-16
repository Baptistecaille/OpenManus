"""Test script for skills system."""

import asyncio
from pathlib import Path

from app.agent.toolcall import ToolCallAgent
from app.logger import logger


async def test_skill_discovery():
    """Test skill discovery."""
    print("=" * 60)
    print("Testing Skill Discovery")
    print("=" * 60)

    # Create a test agent
    agent = ToolCallAgent(
        name="test-agent",
        skills_dir=Path("skills"),
    )

    # Discover skills
    available_skills = agent.skill_manager.get_available_skills()
    print(f"\n✓ Found {len(available_skills)} skills:")
    for skill_metadata in available_skills:
        print(f"  - {skill_metadata.name}: {skill_metadata.description}")

    # List skills
    skills_list = agent.skill_manager.list_skills()
    print(f"\n✓ Skills list:")
    for name, desc in skills_list.items():
        print(f"  - {name}: {desc[:60]}...")

    return agent


async def test_skill_matching(agent: ToolCallAgent):
    """Test skill matching."""
    print("\n" + "=" * 60)
    print("Testing Skill Matching")
    print("=" * 60)

    test_requests = [
        "Review this code for me",
        "Create a commit message",
        "What's the weather today?",
    ]

    for request in test_requests:
        print(f"\n📝 Request: '{request}'")
        matched_skill = await agent.match_and_apply_skill(request)
        if matched_skill:
            active_skills = agent.get_active_skills_names()
            print(f"✓ Matched skill: {active_skills}")
        else:
            print("✗ No skill matched")

        # Clear active skills for next test
        agent.clear_active_skills()


async def test_skill_loading(agent: ToolCallAgent):
    """Test skill loading."""
    print("\n" + "=" * 60)
    print("Testing Skill Loading")
    print("=" * 60)

    # Load a specific skill
    skill_name = "code-review"
    print(f"\n📂 Loading skill: {skill_name}")

    skill = await agent.skill_manager.ensure_loaded(skill_name)
    if skill:
        print(f"✓ Skill loaded successfully")
        print(f"  Name: {skill.metadata.name}")
        print(f"  Description: {skill.metadata.description}")
        print(f"  Allowed tools: {skill.metadata.allowed_tools}")
        print(f"  Content length: {len(skill.content)} chars")
        print(f"  Supporting files: {len(skill.supporting_files)}")
    else:
        print(f"✗ Failed to load skill: {skill_name}")


async def test_hooks(agent: ToolCallAgent):
    """Test hook system."""
    print("\n" + "=" * 60)
    print("Testing Hook System")
    print("=" * 60)

    # Register a test hook
    async def test_handler(context):
        print(f"🔗 Hook triggered! Context: {context}")

    hook = agent.hook_manager.Hook(
        event="PreToolUse",
        matcher="test",
        handler=test_handler,
        once=False,
    )

    agent.hook_manager.register_hook(hook)
    print("\n✓ Registered test hook")

    # Trigger hook
    await agent.hook_manager.trigger_hooks(
        event="PreToolUse",
        tool_name="test",
        context={"tool_input": "test input"},
    )
    print("✓ Hook triggered successfully")


async def main():
    """Run all tests."""
    logger.info("Starting skills system tests")

    # Test discovery
    agent = await test_skill_discovery()

    # Test loading
    await test_skill_loading(agent)

    # Test hooks
    await test_hooks(agent)

    # Test matching
    await test_skill_matching(agent)

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
