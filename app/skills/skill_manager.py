"""Skill manager for discovering and loading skills."""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from app.logger import logger
from app.skills.skill import Skill, SkillMetadata
from app.skills.skill_parser import SkillParser


class SkillManager:
    """Manages skill discovery, loading, and caching.

    Skills are discovered from:
    - Project-level: <project>/skills/
    - Supports automatic discovery from nested directories
    """

    def __init__(self, skills_dir: Optional[Path] = None):
        """Initialize skill manager.

        Args:
            skills_dir: Path to skills directory. Defaults to 'skills/' in current directory.
        """
        if skills_dir is None:
            skills_dir = Path("skills")

        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}
        self.metadata_cache: Dict[str, SkillMetadata] = {}

        logger.info(f"SkillManager initialized with skills directory: {self.skills_dir}")

    def discover_skills(self) -> Dict[str, SkillMetadata]:
        """Discover all available skills and cache their metadata.

        This method only parses metadata for fast startup.
        Full skill content is loaded on demand.

        Returns:
            Dictionary mapping skill names to their metadata
        """
        if not self.skills_dir.exists():
            logger.warning(f"Skills directory does not exist: {self.skills_dir}")
            return {}

        discovered = {}

        # Scan for skill directories
        for skill_path in self._find_skill_directories():
            try:
                metadata = SkillParser.parse_metadata_only(skill_path)
                if metadata:
                    self.metadata_cache[metadata.name] = metadata
                    discovered[metadata.name] = metadata
                    logger.debug(f"Discovered skill: {metadata.name}")
            except Exception as e:
                logger.error(f"Failed to discover skill at {skill_path}: {e}")

        logger.info(f"Discovered {len(discovered)} skills: {list(discovered.keys())}")
        return discovered

    def load_skill(self, name: str) -> Optional[Skill]:
        """Load full skill content including supporting files.

        Args:
            name: Name of skill to load

        Returns:
            Skill object or None if not found
        """
        # Check if already loaded
        if name in self.skills:
            return self.skills[name]

        # Check if skill exists in cache
        if name not in self.metadata_cache:
            logger.warning(f"Skill not found in cache: {name}")
            return None

        # Get skill path from cache
        skill_path = None
        for path in self._find_skill_directories():
            if path.name.lower() == name.lower():
                skill_path = path
                break

        if not skill_path:
            logger.warning(f"Skill directory not found: {name}")
            return None

        try:
            # Parse full skill
            skill = SkillParser.parse_skill_md(skill_path)
            self.skills[name] = skill
            logger.info(f"Loaded skill: {name}")
            return skill
        except Exception as e:
            logger.error(f"Failed to load skill {name}: {e}")
            return None

    def get_available_skills(self) -> List[SkillMetadata]:
        """Get list of all available skill metadata.

        Returns:
            List of skill metadata
        """
        return list(self.metadata_cache.values())

    def get_skill_metadata(self, name: str) -> Optional[SkillMetadata]:
        """Get skill metadata without loading full content.

        Args:
            name: Name of skill

        Returns:
            SkillMetadata or None
        """
        return self.metadata_cache.get(name)

    def unload_skill(self, name: str) -> bool:
        """Unload a skill from memory.

        Args:
            name: Name of skill to unload

        Returns:
            True if unloaded, False if not loaded
        """
        if name in self.skills:
            del self.skills[name]
            logger.info(f"Unloaded skill: {name}")
            return True
        return False

    def reload_skill(self, name: str) -> Optional[Skill]:
        """Reload a skill from disk.

        Args:
            name: Name of skill to reload

        Returns:
            Reloaded Skill object or None if reload failed
        """
        # Unload if loaded
        self.unload_skill(name)

        # Remove from cache
        if name in self.metadata_cache:
            del self.metadata_cache[name]

        # Discover and load again
        self.discover_skills()
        return self.load_skill(name)

    def _find_skill_directories(self) -> List[Path]:
        """Find all skill directories in the skills folder.

        A skill directory must contain a SKILL.md file.

        Returns:
            List of paths to skill directories
        """
        if not self.skills_dir.exists():
            return []

        skill_dirs = []

        # Look for subdirectories containing SKILL.md
        for item in self.skills_dir.iterdir():
            if item.is_dir():
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    skill_dirs.append(item)

        return sorted(skill_dirs, key=lambda p: p.name)

    def list_skills(self) -> Dict[str, str]:
        """Get a dictionary of skill names and their descriptions.

        Returns:
            Dictionary mapping skill names to descriptions
        """
        return {
            name: metadata.description
            for name, metadata in self.metadata_cache.items()
        }

    async def ensure_loaded(self, name: str) -> Optional[Skill]:
        """Ensure skill is loaded, load if necessary.

        Args:
            name: Name of skill

        Returns:
            Loaded Skill or None
        """
        if name in self.skills:
            return self.skills[name]

        return self.load_skill(name)
