from app.tool.base import BaseTool, ToolResult

class APIHumanInTheLoop(BaseTool):
    name: str = "human_in_the_loop"
    description: str = "Request human approval or ask questions. Note: In API mode, this will return a directive to output the question to the user."
    
    parameters: dict = {
        "type": "object",
        "properties": {
            "action_description": {
                "type": "string",
                "description": "The question or action description"
            }
        },
        "required": ["action_description"]
    }

    async def execute(self, action_description: str, **kwargs) -> ToolResult:
        return ToolResult(output=f"SYSTEM: Interactive mode is unavailable. Please output the following question to the user as your final answer: '{action_description}'")
