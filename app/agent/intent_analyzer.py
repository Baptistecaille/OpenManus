import json
import re
from typing import Dict, List, Optional

from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.logger import logger
from app.prompt.intent_analyzer import NEXT_STEP_PROMPT, ParsedIntent, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection


class IntentAnalyzer(ToolCallAgent):
    """Agent that analyzes user intents and parses natural language queries."""

    name: str = "IntentAnalyzer"
    description: str = "Analyzes user prompts to extract structured intent, subject, and search parameters"

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 2000
    max_steps: int = 5

    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            Terminate(),
        )
    )

    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._parsed_intent: Optional[ParsedIntent] = None

    async def parse_intent_async(self, prompt: str) -> ParsedIntent:
        """Parse a prompt asynchronously using LLM."""
        from app.llm import LLM

        llm = LLM()

        response = await llm.ask(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this prompt:\n\n{prompt}"},
            ],
            temperature=0.1,
        )

        if response:
            try:
                json_str = self._extract_json(response)
                intent_dict = json.loads(json_str)
                return ParsedIntent(**intent_dict)
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse intent: {e}, using fallback parsing")
        return self._fallback_parse(prompt)

    def parse_intent_sync(self, prompt: str) -> ParsedIntent:
        """Parse a prompt synchronously using LLM (fallback parser only)."""
        return self._fallback_parse(prompt)

        return self._fallback_parse(prompt)

    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response."""
        json_start = text.find("{")
        json_end = text.rfind("}")

        if json_start != -1 and json_end != -1:
            return text[json_start : json_end + 1]

        raise ValueError("No JSON found in response")

    def _fallback_parse(self, prompt: str) -> ParsedIntent:
        """Fallback parser using regex patterns."""
        prompt_lower = prompt.lower().strip()

        site_mapping = {
            "wikipedia": "wikipedia.org",
            "wiki": "wikipedia.org",
            "github": "github.com",
            "mdn": "developer.mozilla.org",
            "reddit": "reddit.com",
            "stackoverflow": "stackoverflow.com",
        }

        target_sites = []
        for keyword, site in site_mapping.items():
            if keyword in prompt_lower:
                target_sites.append(site)

        action = "research"
        search_type = "general"

        if any(p in prompt_lower for p in ["c'est quoi", "qu'est-ce que", "que signifie"]):
            action = "definition"
            search_type = "definition"
        elif "compare" in prompt_lower or " vs " in prompt_lower or " versus " in prompt_lower:
            action = "compare"
            search_type = "comparison"
        elif "explique" in prompt_lower or "explication" in prompt_lower:
            action = "explain"
            search_type = "explanation"
        elif "latest" in prompt_lower or "dernier" in prompt_lower:
            action = "latest"
            search_type = "latest"
        elif "tutorial" in prompt_lower or "tutoriel" in prompt_lower or "apprendre" in prompt_lower:
            action = "tutorial"
            search_type = "tutorial"
        elif "trouve" in prompt_lower or "cherche" in prompt_lower:
            action = "find"

        query = prompt

        for site_keyword in site_mapping.keys():
            pattern = rf"\b{site_keyword}\b"
            query = re.sub(pattern, "", query, flags=re.IGNORECASE)

        if "c'est quoi" in prompt_lower:
            query = re.sub(r"c'est quoi", "", query, flags=re.IGNORECASE)
        if "qu'est-ce que" in prompt_lower:
            query = re.sub(r"qu'est-ce que", "", query, flags=re.IGNORECASE)
        if "que signifie" in prompt_lower:
            query = re.sub(r"que signifie", "", query, flags=re.IGNORECASE)

        query = re.sub(r"^(cherche sur|search on|find|trouve|sur)\s+", "", query, flags=re.IGNORECASE)

        query = re.sub(r"please|could you|would you", "", query, flags=re.IGNORECASE)
        query = " ".join(query.split())
        query = query.strip(":,.- ")

        if not query or len(query) < 2:
            query = prompt

        language = "auto"
        french_words = ["le", "la", "les", "un", "une", "est", "sont", "qu'est-ce", "c'est", "cherche", "trouve"]
        if any(word in prompt_lower.split()[:5] for word in french_words):
            language = "fr"

        num_urls = 5
        if action in ["definition", "compare"]:
            num_urls = 3
        elif action in ["latest"]:
            num_urls = 7

        unique_sites = list(dict.fromkeys(target_sites))
        filters = [f"site:{s}" for s in unique_sites] if unique_sites else []

        return ParsedIntent(
            action_type=action,
            subject=query,
            target_sites=unique_sites,
            optimized_query=query,
            language=language,
            num_urls=num_urls,
            search_type=search_type,
            filters=filters,
        )

    def get_research_params(self, prompt: str) -> Dict:
        """Get research parameters from a prompt."""
        intent = self.parse_intent_sync(prompt)

        params = {
            "query": intent.optimized_query,
            "num_urls": intent.num_urls,
            "extract_goal": self._build_extract_goal(intent),
        }

        if intent.target_sites:
            params["target_sites"] = intent.target_sites

        if intent.language != "auto":
            params["lang"] = intent.language

        return params

    def _build_extract_goal(self, intent: ParsedIntent) -> str:
        """Build extraction goal based on intent."""
        base = f"Extract relevant information about {intent.subject}"

        if intent.search_type == "definition":
            base = f"Define what {intent.subject} is, its origins, and key concepts"
        elif intent.search_type == "comparison":
            base = f"Compare {intent.subject}: differences, similarities, pros/cons"
        elif intent.search_type == "explanation":
            base = f"Explain {intent.subject} in detail with examples"
        elif intent.search_type == "tutorial":
            base = f"Provide tutorial/guide for {intent.subject} with steps"
        elif intent.search_type == "latest":
            base = f"Find the latest developments and news about {intent.subject}"

        return base


if __name__ == "__main__":
    analyzer = IntentAnalyzer()

    test_prompts = [
        "cherche sur wikipedia ce qu'est une algèbre",
        "compare python and javascript for backend",
        "latest AI developments in 2025",
        "explique la recursion en programmation",
        "tutorial React hooks for beginners",
    ]

    for prompt in test_prompts:
        print(f"\n{'='*60}")
        print(f"Prompt: {prompt}")
        print("-" * 60)
        intent = analyzer.parse_intent_sync(prompt)
        print(f"Action: {intent.action}")
        print(f"Subject: {intent.subject}")
        print(f"Target Sites: {intent.target_sites}")
        print(f"Query: {intent.optimized_query}")
        print(f"Language: {intent.language}")
        print(f"Num URLs: {intent.num_urls}")
        print(f"Search Type: {intent.search_type}")
