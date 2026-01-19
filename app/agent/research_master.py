from typing import List

from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.prompt.research_master import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection, WebSearch


class ResearchMasterPro(ToolCallAgent):
    """An advanced research agent that follows a 5-phase structured research methodology with citation requirements."""

    name: str = "ResearchMasterPro"
    description: str = "A research agent that conducts structured, multi-phase research with mandatory citations and detailed reporting"

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 15000
    max_steps: int = 30

    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(WebSearch(), Terminate())
    )
    tool_choices: str = "auto"
    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])
