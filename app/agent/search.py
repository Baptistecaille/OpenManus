from typing import List

from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.prompt.search import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection, WebSearch


class SearchAgent(ToolCallAgent):
    """An agent that uses web search capabilities to find information."""

    name: str = "search"
    description: str = "An agent that uses web search to find and retrieve information"

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 20

    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(WebSearch(), Terminate())
    )
    tool_choices: str = "auto"
    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])
