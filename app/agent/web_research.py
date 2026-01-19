from typing import Optional

from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.logger import logger
from app.prompt.web_research import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.enhanced_web_research import EnhancedWebResearchTool
from app.tool.web_search import WebSearch
from pydantic import Field


class WebResearchAgent(ToolCallAgent):
    """A specialized agent for comprehensive web research and information gathering."""

    name: str = "WebResearch"
    description: str = "A specialized agent for comprehensive web research that searches the web, visits multiple sources, extracts relevant information, and synthesizes findings"

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 15

    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            EnhancedWebResearchTool(),
            WebSearch(),
            Terminate(),
        )
    )

    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])

    async def cleanup(self):
        """Clean up WebResearch agent resources."""
        logger.info("Cleaning up WebResearch agent...")
        for tool in self.available_tools.tools:
            if hasattr(tool, "cleanup") and callable(getattr(tool, "cleanup")):
                try:
                    if hasattr(tool, "browser_use"):
                        await tool.browser_use.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up tool {tool.name}: {e}")
