"""Parser for SKILL.md files."""

import re
import yaml
from pathlib import Path
from typing import List, Optional

from .skill import Skill, SkillMetadata
from app.logger import logger


class SkillParser:
    """Parser for SKILL.md files with YAML frontmatter."""

    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    @staticmethod
    def parse_skill_md(skill_path: Path) -> Skill:
        """Parse a SKILL.md file and return a Skill object.

        Args:
            skill_path: Path to the directory containing SKILL.md

        Returns:
            Skill object with parsed metadata and content

        Raises:
            FileNotFoundError: If SKILL.md doesn't exist
            ValueError: If YAML parsing fails or required fields are missing
        """
        skill_md_path = skill_path / "SKILL.md"

        if not skill_md_path.exists():
            raise FileNotFoundError(f"SKILL.md not found in {skill_path}")

        content = skill_md_path.read_text(encoding="utf-8")

        # Extract YAML frontmatter
        frontmatter_match = SkillParser.FRONTMATTER_PATTERN.match(content)

        if not frontmatter_match:
            raise ValueError(
                f"Invalid SKILL.md format in {skill_md_path}. "
                "YAML frontmatter must start with '---' on line 1"
            )

        yaml_content = frontmatter_match.group(1)
        markdown_content = content[frontmatter_match.end() :]

        # Parse YAML metadata
        try:
            metadata_dict = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in SKILL.md frontmatter: {e}")

        if not metadata_dict:
            raise ValueError("SKILL.md frontmatter is empty")

        # Validate required fields
        if "name" not in metadata_dict or "description" not in metadata_dict:
            raise ValueError(
                "SKILL.md must contain 'name' and 'description' fields in frontmatter"
            )

        # Ensure name matches directory name
        metadata_dict["name"] = skill_path.name.lower()

        # Create SkillMetadata
        try:
            metadata = SkillMetadata(**metadata_dict)
        except Exception as e:
            raise ValueError(f"Invalid skill metadata: {e}")

        # Discover supporting files
        supporting_files = SkillParser._discover_supporting_files(
            markdown_content, skill_path
        )

        return Skill(
            metadata=metadata,
            content=markdown_content.strip(),
            path=skill_path,
            supporting_files=supporting_files,
        )

    @staticmethod
    def parse_metadata_only(skill_path: Path) -> Optional[SkillMetadata]:
        """Parse only the metadata from a skill (lightweight for discovery).

        Args:
            skill_path: Path to the directory containing SKILL.md

        Returns:
            SkillMetadata or None if parsing fails
        """
        try:
            skill = SkillParser.parse_skill_md(skill_path)
            return skill.metadata
        except Exception as e:
            logger.warning(f"Failed to parse metadata from {skill_path}: {e}")
            return None

    @staticmethod
    def _discover_supporting_files(content: str, skill_path: Path) -> List[Path]:
        """Discover supporting files referenced in skill content.

        Args:
            content: Markdown content of the skill
            skill_path: Path to the skill directory

        Returns:
            List of paths to supporting files
        """
        supporting_files = []

        # Look for markdown file references
        # Pattern: [link text](filename.md)
        md_links = re.findall(r"\[([^\]]+)\]\(([^)]+\.md)\)", content)
        for link_text, filename in md_links:
            file_path = skill_path / filename
            if file_path.exists() and file_path != skill_path / "SKILL.md":
                supporting_files.append(file_path)

        return supporting_files
