"""LLM-based skill matching."""

from typing import List, Optional
from app.llm import LLM
from app.logger import logger
from app.skills.skill import SkillMetadata


class SkillMatcher:
    """Matches user requests to relevant skills using LLM."""

    def __init__(self, llm: LLM):
        """Initialize skill matcher.

        Args:
            llm: LLM instance for matching
        """
        self.llm = llm

    def match_skill(
        self, request: str, available_skills: List[SkillMetadata]
    ) -> Optional[str]:
        """Find the most relevant skill for a user request.

        Args:
            request: User request text
            available_skills: List of available skill metadata

        Returns:
            Name of matching skill, or None if no skill matches
        """
        if not available_skills:
            return None

        # Build skills list for the prompt
        skills_list = "\n".join(
            [
                f"- {skill.name}: {skill.description}"
                for skill in available_skills
            ]
        )

        # Construct matching prompt
        prompt = self._build_matching_prompt(request, skills_list)

        try:
            # Use LLM to select the best matching skill
            response = await self.llm.ask(
                messages=[{"role": "user", "content": prompt}],
                system_msgs=[],
                stream=False,
                temperature=0.0,
            )

            # Parse response
            return self._parse_match_response(response, available_skills)

        except Exception as e:
            logger.error(f"Skill matching failed: {e}")
            return None

    def _build_matching_prompt(self, request: str, skills_list: str) -> str:
        """Build the prompt for LLM-based skill matching.

        Args:
            request: User request
            skills_list: Formatted list of available skills

        Returns:
            Complete prompt for LLM
        """
        return f"""You are a skill selector. Your task is to select the most relevant skill for a user request.

Available skills:
{skills_list}

User request: "{request}"

Analyze the user request and select the skill that best matches their intent. Consider:
- What the user is asking for
- The skill's description and capabilities
- Keywords and phrases in both the request and descriptions

Return ONLY the skill name (e.g., "my-skill-name"), or "none" if no skill is relevant.
Do not include any explanation or additional text."""

    def _parse_match_response(
        self, response: str, available_skills: List[SkillMetadata]
    ) -> Optional[str]:
        """Parse LLM response to extract skill name.

        Args:
            response: LLM response text
            available_skills: List of available skill metadata

        Returns:
            Matched skill name or None
        """
        # Clean up response
        skill_name = response.strip().strip('"\'').lower()

        # Check for "none" response
        if skill_name == "none" or skill_name == "no match":
            return None

        # Validate against available skills
        available_names = {skill.name.lower() for skill in available_skills}

        if skill_name in available_names:
            return skill_name

        # Try fuzzy matching if exact match fails
        for available_name in available_names:
            if skill_name in available_name or available_name in skill_name:
                return available_name

        logger.warning(
            f"LLM returned invalid skill name '{skill_name}'. Available: {available_names}"
        )
        return None
