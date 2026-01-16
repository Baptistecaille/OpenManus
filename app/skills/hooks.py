"""Hook system for skill lifecycle events."""

import asyncio
from enum import Enum
from typing import Callable, Dict, List, Optional, Any
from pydantic import BaseModel, Field
from app.logger import logger


class HookEvent(str, Enum):
    """Events that can trigger hooks."""

    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    STOP = "Stop"


class HookType(str, Enum):
    """Types of hooks."""

    COMMAND = "command"
    FUNCTION = "function"


class Hook(BaseModel):
    """Represents a single hook definition."""

    event: HookEvent = Field(..., description="Event that triggers this hook")
    matcher: str = Field(..., description="Pattern or tool name to match")
    hook_type: HookType = Field(
        default=HookType.FUNCTION, description="Type of hook handler"
    )
    handler: Optional[Callable] = Field(
        default=None, exclude=True, description="Function handler (for function hooks)"
    )
    command: Optional[str] = Field(
        default=None, description="Command to execute (for command hooks)"
    )
    once: bool = Field(default=False, description="Run hook only once per session")
    executed: bool = Field(default=False, description="Track if hook was executed")


class HookManager:
    """Manages hook registration and execution for skill lifecycle events."""

    def __init__(self):
        self.hooks: List[Hook] = []
        self.session_hooks: Dict[str, Hook] = {}

    def register_hook(self, hook: Hook) -> None:
        """Register a hook.

        Args:
            hook: Hook to register
        """
        hook_id = f"{hook.event.value}:{hook.matcher}:{id(hook)}"
        hook.session_id = hook_id
        self.hooks.append(hook)
        logger.debug(f"Registered hook: {hook_id}")

    def register_hooks_from_skill(
        self, hooks_config: Dict[str, List[Dict[str, Any]]], skill_name: str
    ) -> None:
        """Register hooks from skill configuration.

        Args:
            hooks_config: Hooks configuration from skill metadata
            skill_name: Name of the skill registering these hooks
        """
        if not hooks_config:
            return

        for event_name, hook_configs in hooks_config.items():
            try:
                event = HookEvent(event_name)
            except ValueError:
                logger.warning(f"Invalid hook event: {event_name}")
                continue

            for hook_config in hook_configs:
                try:
                    matcher = hook_config.get("matcher", "")
                    hook_type_str = hook_config.get("type", "function")
                    hook_type = HookType(hook_type_str)
                    command = hook_config.get("command")
                    once = hook_config.get("once", False)

                    hook = Hook(
                        event=event,
                        matcher=matcher,
                        hook_type=hook_type,
                        command=command,
                        once=once,
                    )

                    self.register_hook(hook)
                    logger.info(
                        f"Registered {skill_name} hook: {event_name} -> {matcher}"
                    )
                except Exception as e:
                    logger.error(f"Failed to register hook from {skill_name}: {e}")

    async def trigger_hooks(
        self,
        event: HookEvent,
        tool_name: str,
        context: Dict[str, Any],
    ) -> None:
        """Trigger all hooks that match the event and tool.

        Args:
            event: Event that triggered the hook
            tool_name: Name of the tool being executed
            context: Context data for the hook (tool_input, result, etc.)
        """
        matching_hooks = [
            hook
            for hook in self.hooks
            if hook.event == event and hook.matcher.lower() in tool_name.lower()
        ]

        if not matching_hooks:
            return

        for hook in matching_hooks:
            if hook.once and hook.executed:
                continue

            try:
                await self._execute_hook(hook, context)
                hook.executed = True
                logger.debug(f"Executed hook: {hook.event.value} -> {hook.matcher}")
            except Exception as e:
                logger.error(f"Hook execution failed: {e}")

    async def _execute_hook(self, hook: Hook, context: Dict[str, Any]) -> None:
        """Execute a single hook.

        Args:
            hook: Hook to execute
            context: Context data for the hook

        Raises:
            RuntimeError: If hook execution fails
        """
        if hook.hook_type == HookType.FUNCTION and hook.handler:
            # Execute function hook
            result = hook.handler(context)
            if asyncio.iscoroutine(result):
                await result

        elif hook.hook_type == HookType.COMMAND and hook.command:
            # Execute command hook
            import subprocess

            # Apply string substitutions
            command = self._apply_substitutions(hook.command, context)

            try:
                process = await asyncio.create_subprocess_shell(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                if process.returncode != 0:
                    logger.warning(
                        f"Hook command returned non-zero exit code: {stderr.decode()}"
                    )
                else:
                    logger.debug(f"Hook command output: {stdout.decode()}")
            except Exception as e:
                logger.error(f"Failed to execute hook command: {e}")

    @staticmethod
    def _apply_substitutions(template: str, context: Dict[str, Any]) -> str:
        """Apply variable substitutions to command template.

        Args:
            template: Command template with placeholders
            context: Context data for substitutions

        Returns:
            Substituted command string
        """
        substitutions = {
            "$TOOL_NAME": context.get("tool_name", ""),
            "$TOOL_INPUT": context.get("tool_input", ""),
            "$TOOL_RESULT": context.get("result", ""),
        }

        result = template
        for key, value in substitutions.items():
            result = result.replace(key, str(value) if value else "")

        return result

    def clear_hooks(self) -> None:
        """Clear all registered hooks."""
        self.hooks.clear()
        self.session_hooks.clear()
        logger.debug("Cleared all hooks")

    def remove_hooks_by_prefix(self, prefix: str) -> None:
        """Remove hooks whose session_id starts with prefix.

        Args:
            prefix: Prefix to match (e.g., skill name)
        """
        self.hooks = [
            hook
            for hook in self.hooks
            if not getattr(hook, "session_id", "").startswith(prefix)
        ]
        logger.debug(f"Removed hooks with prefix: {prefix}")
