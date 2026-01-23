"""
Advanced Human-in-the-Loop tool for OpenManus agents.

Implements production-grade HITL patterns based on:
- LangGraph interrupt/resume patterns
- Permit.io approval workflows
- Temporal long-running processes
"""

import asyncio
import time
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, PrivateAttr

from app.logger import logger
from app.tool.base import BaseTool
from app.exceptions import AgentSuspend


class CriticalityLevel(Enum):
    """Action criticality levels requiring different approval thresholds."""
    LOW = "low"          # Auto-approve (logging only)
    MEDIUM = "medium"    # Quick approval needed
    HIGH = "high"        # Requires careful review
    CRITICAL = "critical" # Blocks execution until approval


class HITLRequest(BaseModel):
    """HITL approval request structure."""
    action_description: str = Field(description="Action needing approval")
    criticality: CriticalityLevel = Field(default=CriticalityLevel.MEDIUM)
    context: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = Field(default=300)


class HITLResponse(BaseModel):
    """Human approval response."""
    approved: bool
    feedback: Optional[str] = None
    modified_action: Optional[Dict[str, Any]] = None
    timestamp: float = Field(default_factory=time.time)


class HumanInTheLoop(BaseTool):
    """
    Production-grade Human-in-the-Loop tool.

    Features:
    - Risk-based approval (4 criticality levels)
    - Timeout handling with fallbacks
    - State persistence
    - Multi-channel approval support (console, future: email/Slack)
    - LangGraph-style interrupt/resume patterns
    - General inquiry mode to ask human for help
    """

    name: str = "human_in_the_loop"
    description: str = "Request human approval for actions OR ask the human for help/information. Set 'mode' to 'approval' (default) or 'ask_human'."

    parameters: dict = {
        "type": "object",
        "properties": {
            "action_description": {
                "type": "string",
                "description": "Description of action requiring approval OR the question to ask the human"
            },
            "mode": {
                "type": "string",
                "enum": ["approval", "ask_human"],
                "description": "Mode of interaction. 'approval' for permission to execute an action, 'ask_human' for general questions.",
                "default": "approval"
            },
            "criticality": {
                "type": "string",
                "enum": ["low", "medium", "high", "critical"],
                "description": "Action criticality level (only for approval mode)",
                "default": "medium"
            },
            "context": {
                "type": "object",
                "description": "Additional context",
                "default": {}
            },
            "timeout_seconds": {
                "type": "integer",
                "description": "Seconds to wait for approval/response (default: None for infinite wait)",
                "default": None
            },
            "fallback_action": {
                "type": "string",
                "enum": ["deny", "auto_approve"],
                "description": "Action on timeout (only for approval mode)",
                "default": "deny"
            }
        },
        "required": ["action_description"]
    }

    _pending_requests: Dict[str, HITLRequest] = PrivateAttr(default_factory=dict)

    async def execute(
        self,
        action_description: str,
        mode: str = "approval",
        criticality: str = "medium",
        context: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[int] = None,
        fallback_action: str = "deny"
    ) -> Dict[str, Any]:
        """
        Execute HITL request by suspending execution and asking the human.
        """
        # Instead of printing to console and blocking, we raise a suspension signal.
        # This allows the upstream system (server) to capture the intent and present it to the user.
        # When resumed, the 'answer' will be passed as the result of this tool execution.
        
        raise AgentSuspend(question=action_description)

    async def _ask_human_question(self, question: str, timeout_seconds: Optional[int]) -> Dict[str, Any]:
        """Ask a general question to the human."""
        print(f"\n{'='*70}\nQUESTION DE L'AGENT\n{'='*70}")
        print(f"Question: {question}")
        if timeout_seconds:
            print(f"Timeout: {timeout_seconds} secondes")
        else:
            print("Timeout: Aucun (Attente infinie)")
        print("\nVotre réponse: ", end="", flush=True)

        try:
            if timeout_seconds:
                response_text = await asyncio.wait_for(
                    asyncio.to_thread(input),
                    timeout=timeout_seconds
                )
            else:
                response_text = await asyncio.to_thread(input)
                
            return {
                "answer": response_text.strip(),
                "status": "answered"
            }
        except asyncio.TimeoutError:
            print(f"\nTIMEOUT: Pas de réponse dans {timeout_seconds} secondes")
            return {
                "answer": None,
                "error": "Timeout",
                "status": "timeout"
            }
        except Exception as e:
            return {
                "answer": None,
                "error": str(e),
                "status": "error"
            }

    async def _get_human_approval(
        self,
        request_id: str,
        request: HITLRequest,
        fallback_action: str
    ) -> HITLResponse:
        """Get approval from human via console interface."""
        prompt = self._format_approval_prompt(request_id, request)

        try:
            print(prompt)
            
            if request.timeout_seconds and request.timeout_seconds < 86400: # If explicit small timeout
                 response_text = await asyncio.wait_for(
                    asyncio.to_thread(input, ""),
                    timeout=request.timeout_seconds
                )
            else:
                 # Infinite wait logic if timeout is huge (default behavior now)
                 response_text = await asyncio.to_thread(input, "")

            response_text = response_text.strip().lower()

            if response_text in ['yes', 'y', 'approve', 'approved', 'oui', 'o']:
                return HITLResponse(approved=True)

            elif response_text in ['no', 'n', 'deny', 'denied', 'non']:
                return HITLResponse(approved=False)

            elif response_text.startswith(('modify ', 'modifier ')):
                modification = response_text.split(' ', 1)[1]
                return HITLResponse(
                    approved=True,
                    feedback=f"Modified: {modification}",
                    modified_action={"modification": modification}
                )

            else:
                print(f"\nResponse non reconnue: {response_text}")
                print("Action REFUSÉ pour sécurité.")
                return HITLResponse(
                    approved=False,
                    feedback=f"Response non reconnue: {response_text}"
                )

        except asyncio.TimeoutError:
            logger.warning(f"HITL timeout for request {request_id}")
            print(f"\nTIMEOUT: Pas de réponse dans {request.timeout_seconds} secondes")

            if fallback_action == "auto_approve":
                print("Action APPROUVÉE automatiquement (fallback)")
                return HITLResponse(
                    approved=True,
                    feedback=f"Auto-approved after timeout ({fallback_action})"
                )
            else:
                print("Action REFUSÉE pour sécurité.")
                return HITLResponse(
                    approved=False,
                    feedback=f"Timeout after {request.timeout_seconds} seconds"
                )

        except Exception as e:
            logger.error(f"HITL input error: {e}")
            return HITLResponse(
                approved=False,
                feedback=f"Input error: {str(e)}"
            )

    def _format_approval_prompt(self, request_id: str, request: HITLRequest) -> str:
        """Format approval prompt for user."""
        lines = [
            "\n" + "="*70,
            "DEMANDE D'APPROBATION HUMAIN-EN-BOUCLE",
            "="*70,
            f"ID Requête: {request_id}",
            f"Criticité: {request.criticality.value.upper()}",
            f"Action: {request.action_description}",
        ]

        if request.context:
            lines.append("Contexte:")
            for key, value in request.context.items():
                lines.append(f"  {key}: {value}")

        lines.extend([
            "",
            "Options:",
            "  'oui'/'o' - Approuver l'action",
            "  'non'/'n' - Refuser l'action",
            "  'modifier <description>' - Approuver avec modification",
            "",
            f"Timeout: {request.timeout_seconds if request.timeout_seconds < 86400 else 'Aucun'} secondes",
            "",
            "Votre décision: "
        ])

        return "\n".join(lines)

    async def interrupt_and_wait(
        self,
        action_description: str,
        criticality: str = "medium",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        LangGraph-style interrupt pattern.
        Pauses execution until human approval, then resumes.
        """
        logger.info(f"INTERRUPTION pour HITL: {action_description}")

        result = await self.execute(
            action_description=action_description,
            mode="approval",
            criticality=criticality,
            context=context
        )

        if result.get("approved"):
            logger.info("HITL APPROUVÉ - Reprise de l'exécution")
            return result
        else:
            logger.info("HITL REFUSÉ - Exécution bloquée")
            raise Exception(f"Action refusée par humain: {result.get('feedback', 'Aucun motif fourni')}")

    def get_pending_requests(self) -> Dict[str, HITLRequest]:
        """Get all currently pending approval requests."""
        return self._pending_requests.copy()

    def __str__(self) -> str:
        pending_count = len(self._pending_requests)
        return f"HumanInTheLoop(pending_requests={pending_count})"
