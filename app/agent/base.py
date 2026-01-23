from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr, model_validator

from app.exceptions import AgentSuspend
from app.llm import LLM
from app.logger import logger
from app.sandbox.client import SANDBOX_CLIENT
from app.schema import ROLE_TYPE, AgentState, Memory, Message
from app.skills.skill_manager import SkillManager
from app.skills.skill_matcher import SkillMatcher
from app.skills.hooks import HookManager
from app.skills.skill import Skill


class BaseAgent(BaseModel, ABC):
    """Abstract base class for managing agent state and execution.

    Provides foundational functionality for state transitions, memory management,
    and a step-based execution loop. Subclasses must implement the `step` method.
    """

    # Core attributes
    name: str = Field(..., description="Unique name of the agent")
    description: Optional[str] = Field(None, description="Optional agent description")

    # Prompts
    system_prompt: Optional[str] = Field(
        None, description="System-level instruction prompt"
    )
    next_step_prompt: Optional[str] = Field(
        None, description="Prompt for determining next action"
    )

    # Dependencies
    llm: LLM = Field(default_factory=LLM, description="Language model instance")
    memory: Memory = Field(default_factory=Memory, description="Agent's memory store")
    state: AgentState = Field(
        default=AgentState.IDLE, description="Current agent state"
    )

    # Execution control
    max_steps: int = Field(default=10, description="Maximum steps before termination")
    current_step: int = Field(default=0, description="Current step in execution")

    duplicate_threshold: int = 2

    # Skills
    skills_dir: Optional[Path] = Field(
        default=None, description="Path to skills directory"
    )
    skill_manager: SkillManager = Field(
        default_factory=SkillManager, description="Manages skill discovery and loading"
    )
    skill_matcher: Optional[SkillMatcher] = Field(
        default=None, description="Matches requests to relevant skills"
    )
    active_skills: List[Skill] = Field(
        default_factory=list, description="Currently active skills"
    )
    hook_manager: HookManager = Field(
        default_factory=HookManager, description="Manages skill lifecycle hooks"
    )

    # Private attributes (use PrivateAttr for underscore-prefixed fields)
    _original_system_prompt: Optional[str] = PrivateAttr(default=None)
    _original_tools_filter: Optional[List[str]] = PrivateAttr(default=None)
    _skills_enabled: bool = PrivateAttr(default=False)

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"  # Allow extra fields for flexibility in subclasses

    @model_validator(mode="after")
    def initialize_agent(self) -> "BaseAgent":
        """Initialize agent with default settings if not provided."""
        if self.llm is None or not isinstance(self.llm, LLM):
            self.llm = LLM(config_name=self.name.lower())
        if not isinstance(self.memory, Memory):
            self.memory = Memory()

        # Initialize skills
        self._initialize_skills()

        return self

    @asynccontextmanager
    async def state_context(self, new_state: AgentState):
        """Context manager for safe agent state transitions.

        Args:
            new_state: The state to transition to during the context.

        Yields:
            None: Allows execution within the new state.

        Raises:
            ValueError: If the new_state is invalid.
        """
        if not isinstance(new_state, AgentState):
            raise ValueError(f"Invalid state: {new_state}")

        previous_state = self.state
        self.state = new_state
        try:
            yield
        except Exception as e:
            self.state = AgentState.ERROR  # Transition to ERROR on failure
            raise e
        finally:
            self.state = previous_state  # Revert to previous state

    def update_memory(
        self,
        role: ROLE_TYPE,  # type: ignore
        content: str,
        base64_image: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Add a message to the agent's memory.

        Args:
            role: The role of the message sender (user, system, assistant, tool).
            content: The message content.
            base64_image: Optional base64 encoded image.
            **kwargs: Additional arguments (e.g., tool_call_id for tool messages).

        Raises:
            ValueError: If the role is unsupported.
        """
        message_map = {
            "user": Message.user_message,
            "system": Message.system_message,
            "assistant": Message.assistant_message,
            "tool": lambda content, **kw: Message.tool_message(content, **kw),
        }

        if role not in message_map:
            raise ValueError(f"Unsupported message role: {role}")

        # Create message with appropriate parameters based on role
        kwargs = {"base64_image": base64_image, **(kwargs if role == "tool" else {})}
        self.memory.add_message(message_map[role](content, **kwargs))

    async def _analyze_prompt_complexity(self, request: str) -> bool:
        """
        Analyze if the prompt requires tools/thinking or can be answered naturally.

        Returns:
            True if tools/thinking are needed, False if natural response suffices
        """
        if not request:
            return False

        # Clean and analyze the request
        req_lower = request.lower().strip() if request else ""

        # Simple greetings - no tools needed
        simple_greetings = ["salut", "hello", "hi", "hey", "bonjour", "hola", "ciao", "greetings", "hi there"]
        if any(greeting in req_lower for greeting in simple_greetings):
            return False

        # Questions about the agent itself - no tools needed
        self_questions = ["who are you", "what are you", "what can you do", "help", "how do you work"]
        if any(question in req_lower for question in self_questions):
            logger.info(f"Detected self-question: {request} - responding naturally")
            return False

        # Conversational/small talk - no tools needed
        conversational = ["how are you", "thank you", "thanks", "good morning", "good afternoon", "good evening"]
        if any(phrase in req_lower for phrase in conversational):
            return False

        # If we have LLM available, use it for more sophisticated analysis
        if self.llm and self.llm.client is not None:
            try:
                analysis_prompt = f"""Analyze this user request and determine if it requires using tools, searching, or complex reasoning.

Request: "{request}"

Respond with only "YES" if tools/reasoning are needed, or "NO" if it can be answered naturally/conversationally.

Examples:
- "Hello" → NO
- "What's the weather?" → YES (needs weather API)
- "Tell me a joke" → NO
- "Search for Python tutorials" → YES (needs search)
- "How are you?" → NO"""

                analysis = await self.llm.ask(
                    messages=[{"role": "user", "content": analysis_prompt}],
                    temperature=0.0
                )
                return analysis and "YES" in analysis.upper()
            except Exception:
                pass  # Fall back to heuristic analysis

        # Heuristic analysis for mock mode
        # Check for action words that suggest tool usage
        action_words = ["search", "find", "create", "write", "calculate", "analyze", "generate", "convert"]
        if any(word in req_lower for word in action_words):
            return True

        # Check for question words that might need research
        question_words = ["what is", "how to", "where can", "when did", "why does"]
        if any(word in req_lower for word in question_words):
            return True

        # Default to natural response for unclear or simple requests
        return False

    async def _generate_natural_response(self, request: str) -> str:
        """
        Generate a natural response for simple requests in mock mode.
        """
        req_lower = request.lower().strip() if request else ""

        # Greetings
        if any(greeting in req_lower for greeting in ["salut", "hello", "hi", "hey", "bonjour", "hola", "ciao"]):
            return "Salut! I'm running in mock mode without an API key. Configure your OpenAI API key in config/config.toml to enable full functionality."

        # Self-introduction
        if any(q in req_lower for q in ["who are you", "what are you", "what can you do"]):
            return "I'm Manus, an AI agent that can help you with various tasks. I'm currently running in mock mode without an API key. Configure your OpenAI API key in config/config.toml to enable full functionality."

        # Help requests
        if "help" in req_lower:
            return "I can help you with many tasks! I'm currently running in mock mode without an API key. Configure your OpenAI API key in config/config.toml to enable full functionality."

        # Default natural response
        return f"I understand you're asking about: '{request}'. I'm currently running in mock mode without an API key. Configure your OpenAI API key in config/config.toml to enable full functionality."

    async def run(self, request: Optional[str] = None) -> str:
        """
        Run the agent with the given request.

        Args:
            request: The user request to process

        Returns:
            The final response from the agent
        """
        results = []
        # Initialize/reset agent state
        self.current_step = 0
        self.state = AgentState.IDLE

        # First determine if this prompt requires tools/thinking or can be answered naturally
        needs_tools = await self._analyze_prompt_complexity(request)

        if not needs_tools:
            # Respond naturally without full reasoning loop
            if self.llm and self.llm.client is None:
                # Mock mode natural responses
                return await self._generate_natural_response(request)
            else:
                try:
                    # Use LLM for natural response
                    natural_response = await self.llm.ask(
                        messages=[{"role": "user", "content": request}],
                        system_msgs=[{"role": "system", "content": "Respond naturally and helpfully to the user's request. Keep your response concise and direct."}]
                    )
                    return natural_response or "I understand your request, but I'm having trouble generating a response right now."
                except Exception as e:
                    logger.warning(f"LLM natural response failed: {e}. Falling back to mock response.")
                    return await self._generate_natural_response(request)

        # Check if this is a simple greeting in mock mode (fallback for complex analysis)
        if request and self.llm and self.llm.client is None:
            request_str = str(request)
            simple_greetings = ["salut", "hello", "hi", "hey", "bonjour", "hola", "ciao", "greetings", "hi there"]
            if any(greeting in request_str.lower().strip() for greeting in simple_greetings):
                return "Salut! I'm running in mock mode without an API key. Configure your OpenAI API key in config/config.toml to enable full functionality."

        try:
            # We don't force state to RUNNING if it's already running/suspended, we manage it
            # But the state_context manager sets it to RUNNING.
            # If we resume, we want to enter RUNNING state.
            
            async with self.state_context(AgentState.RUNNING):
                while (
                    self.current_step < self.max_steps and self.state != AgentState.FINISHED and self.state != AgentState.SUSPENDED
                ):
                    self.current_step += 1
                    logger.info(f"Executing step {self.current_step}/{self.max_steps}")
                    
                    try:
                        step_result = await self.step()
                        
                        # Check for stuck state
                        if self.is_stuck():
                            self.handle_stuck_state()

                        results.append(f"Step {self.current_step}: {step_result}")
                        
                    except AgentSuspend as e:
                        logger.info(f"Agent execution suspended: {e.question}")
                        self.state = AgentState.SUSPENDED
                        # Propagate exception to allow caller (server) to handle it
                        raise e

                if self.current_step >= self.max_steps:
                    self.current_step = 0
                    self.state = AgentState.IDLE
                    results.append(f"Terminated: Reached max steps ({self.max_steps})")
        
        except AgentSuspend:
            # Re-raise to caller
            raise
        except Exception as e:
            # state_context handles setting state to ERROR
            raise e
            
        await SANDBOX_CLIENT.cleanup()
        return "\n".join(results) if results else "No steps executed"

    @abstractmethod
    async def step(self) -> str:
        """Execute a single step in the agent's workflow.

        Must be implemented by subclasses to define specific behavior.
        """

    def handle_stuck_state(self):
        """Handle stuck state by adding a prompt to change strategy"""
        stuck_prompt = "\
        Observed duplicate responses. Consider new strategies and avoid repeating ineffective paths already attempted."
        self.next_step_prompt = f"{stuck_prompt}\n{self.next_step_prompt}"
        logger.warning(f"Agent detected stuck state. Added prompt: {stuck_prompt}")

    def is_stuck(self) -> bool:
        """Check if the agent is stuck in a loop by detecting duplicate content"""
        if len(self.memory.messages) < 2:
            return False

        last_message = self.memory.messages[-1]
        if not last_message.content:
            return False

        # Count identical content occurrences
        duplicate_count = sum(
            1
            for msg in reversed(self.memory.messages[:-1])
            if msg.role == "assistant" and msg.content == last_message.content
        )

        return duplicate_count >= self.duplicate_threshold

    @property
    def messages(self) -> List[Message]:
        """Retrieve a list of messages from the agent's memory."""
        return self.memory.messages

    @messages.setter
    def messages(self, value: List[Message]):
        """Set the list of messages in the agent's memory."""
        self.memory.messages = value

    def _initialize_skills(self) -> None:
        """Initialize skills discovery and matcher."""
        if self.skills_dir is not None:
            self.skill_manager = SkillManager(skills_dir=Path(self.skills_dir))
        else:
            # Use default skills directory
            self.skill_manager = SkillManager()

        # Discover skills
        self.skill_manager.discover_skills()

        # Initialize skill matcher
        self.skill_matcher = SkillMatcher(self.llm)

        logger.info(f"Initialized skills for agent {self.name}")

    async def match_and_apply_skill(self, request: str) -> bool:
        """Match request to relevant skill and apply it.

        Args:
            request: User request text

        Returns:
            True if skill was applied, False otherwise
        """
        if not self._skills_enabled or not self.skill_matcher:
            return False

        # Get available skills
        available_skills = self.skill_manager.get_available_skills()

        if not available_skills:
            logger.debug("No skills available for matching")
            return False

        try:
            skill_name = await self.skill_matcher.match_skill(request, available_skills)
        except Exception as e:
            logger.debug(f"Skill matching failed: {e}")
            return False

        if not skill_name:
            logger.debug("No skill matched the request")
            return False

        # Load and apply skill
        skill = await self.skill_manager.ensure_loaded(skill_name)
        if skill:
            await self.apply_skill(skill)
            return True

        return False

    async def apply_skill(self, skill: Skill) -> None:
        """Apply a skill to the agent.

        Args:
            skill: Skill to apply
        """
        logger.info(f"Applying skill: {skill.metadata.name}")

        # Store original system prompt if not already stored
        if self._original_system_prompt is None:
            self._original_system_prompt = self.system_prompt

        # Inject skill instructions into system prompt
        skill_instructions = skill.get_full_instructions()
        if self.system_prompt:
            self.system_prompt = f"{self.system_prompt}\n\n{skill_instructions}"
        else:
            self.system_prompt = skill_instructions

        # Apply tool restrictions if specified
        if skill.metadata.allowed_tools:
            logger.info(f"Skill restricts tools to: {skill.metadata.allowed_tools}")

        # Register hooks
        if skill.has_hooks():
            self.hook_manager.register_hooks_from_skill(
                skill.metadata.hooks, skill.metadata.name
            )

        # Add to active skills
        if skill not in self.active_skills:
            self.active_skills.append(skill)

    async def remove_skill(self, skill: Skill) -> None:
        """Remove a skill from the agent.

        Args:
            skill: Skill to remove
        """
        logger.info(f"Removing skill: {skill.metadata.name}")

        # Restore original system prompt
        if self._original_system_prompt is not None:
            self.system_prompt = self._original_system_prompt

        # Remove hooks
        if skill.has_hooks():
            self.hook_manager.remove_hooks_by_prefix(skill.metadata.name)

        # Remove from active skills
        if skill in self.active_skills:
            self.active_skills.remove(skill)

    def clear_active_skills(self) -> None:
        """Clear all active skills and restore agent to original state."""
        for skill in self.active_skills.copy():
            if self._original_system_prompt is not None:
                self.system_prompt = self._original_system_prompt

        self.active_skills.clear()
        self.hook_manager.clear_hooks()
        logger.info("Cleared all active skills")

    def enable_skills(self) -> None:
        """Enable skills matching."""
        self._skills_enabled = True
        logger.info("Skills enabled")

    def disable_skills(self) -> None:
        """Disable skills matching."""
        self._skills_enabled = False
        logger.info("Skills disabled")

    def get_active_skills_names(self) -> List[str]:
        """Get names of currently active skills.

        Returns:
            List of skill names
        """
        return [skill.metadata.name for skill in self.active_skills]
