class ToolError(Exception):
    """Raised when a tool encounters an error."""

    def __init__(self, message):
        self.message = message


class OpenManusError(Exception):
    """Base exception for all OpenManus errors"""


class TokenLimitExceeded(OpenManusError):
    """Exception raised when the token limit is exceeded"""


class AgentSuspend(OpenManusError):
    """Exception raised when agent needs to suspend execution for human input"""
    def __init__(self, question: str):
        self.question = question
        super().__init__(question)
