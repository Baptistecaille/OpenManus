#!/usr/bin/env python
"""
OpenManus Unified Entry Point

This script consolidates all execution modes:
- simple: Single Manus agent (formerly main.py)
- flow: Multi-agent with PlanningFlow (default)
- mcp: MCP-enabled agent (formerly run_mcp.py)

Examples:
    # Interactive mode with PlanningFlow (default)
    python run_flow.py

    # Simple single agent mode
    python run_flow.py --mode simple

    # MCP mode with stdio connection
    python run_flow.py --mode mcp

    # MCP mode with SSE connection
    python run_flow.py --mode mcp --connection sse --server-url http://localhost:8000/sse

    # Single prompt execution (any mode)
    python run_flow.py --prompt "Your task here"
    python run_flow.py --mode simple --prompt "Your task here"

    # Interactive loop mode
    python run_flow.py --interactive
    python run_flow.py --mode mcp --interactive
"""

import argparse
import asyncio
import sys
import time
from enum import Enum
from typing import Optional

from app.agent.data_analysis import DataAnalysis
from app.agent.manus import Manus
from app.agent.mcp import MCPAgent
from app.agent.swe import SWEAgent
from app.config import config
from app.flow.flow_factory import FlowFactory, FlowType
from app.logger import logger


class ExecutionMode(str, Enum):
    """Available execution modes."""
    SIMPLE = "simple"  # Single agent execution
    FLOW = "flow"      # Multi-agent planning flow
    MCP = "mcp"        # MCP-enabled agent


class AgentType(str, Enum):
    """Available agent types for simple mode."""
    MANUS = "manus"
    SWE = "swe"
    DATA_ANALYSIS = "data_analysis"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="OpenManus - Unified AI Agent Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_flow.py                              # Interactive flow mode (default)
  python run_flow.py --mode simple                # Simple single agent
  python run_flow.py --mode mcp                   # MCP agent with stdio
  python run_flow.py --mode mcp --connection sse  # MCP agent with SSE
  python run_flow.py --prompt "Do something"      # Execute single prompt
  python run_flow.py --interactive                # Interactive loop mode
        """
    )

    # Mode selection
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=[m.value for m in ExecutionMode],
        default=ExecutionMode.FLOW.value,
        help="Execution mode: 'simple' (single agent), 'flow' (multi-agent planning), 'mcp' (MCP-enabled)"
    )

    # Agent selection (for simple mode)
    parser.add_argument(
        "--agent", "-a",
        type=str,
        choices=[a.value for a in AgentType],
        default=AgentType.MANUS.value,
        help="Agent type for simple mode: 'manus', 'swe', or 'data_analysis'"
    )

    # Prompt options
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        help="Single prompt to execute (skips interactive input)"
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive loop mode (type 'exit' to quit)"
    )

    # MCP-specific options
    mcp_group = parser.add_argument_group("MCP Options")
    mcp_group.add_argument(
        "--connection", "-c",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP connection type: 'stdio' or 'sse'"
    )
    mcp_group.add_argument(
        "--server-url",
        default="http://127.0.0.1:8000/sse",
        help="URL for MCP SSE connection"
    )

    # Flow-specific options
    flow_group = parser.add_argument_group("Flow Options")
    flow_group.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Timeout in seconds for flow execution (default: 3600)"
    )
    flow_group.add_argument(
        "--no-data-analysis",
        action="store_true",
        help="Disable DataAnalysis agent in flow mode (overrides config)"
    )

    return parser.parse_args()


async def run_simple_mode(args: argparse.Namespace) -> None:
    """Run in simple single-agent mode."""
    # Create the appropriate agent
    if args.agent == AgentType.MANUS.value:
        agent = await Manus.create()
        logger.info("Using Manus agent for general purpose tasks")
    elif args.agent == AgentType.SWE.value:
        agent = SWEAgent()
        logger.info("Using SWE agent for software engineering tasks")
    elif args.agent == AgentType.DATA_ANALYSIS.value:
        agent = DataAnalysis()
        logger.info("Using DataAnalysis agent for data analysis tasks")
    else:
        raise ValueError(f"Unknown agent type: {args.agent}")

    try:
        if args.interactive:
            await run_interactive_loop(agent)
        else:
            prompt = args.prompt if args.prompt else input("Enter your prompt: ")
            if not prompt.strip():
                logger.warning("Empty prompt provided.")
                return

            logger.info("Processing your request...")
            result = await agent.run(prompt)
            logger.info("Request processing completed.")
            if result:
                print(f"\nResult:\n{result}")
    finally:
        if hasattr(agent, 'cleanup'):
            await agent.cleanup()


async def run_flow_mode(args: argparse.Namespace) -> None:
    """Run in multi-agent planning flow mode."""
    # Build agents dictionary
    agents = {"manus": await Manus.create()}

    # Add DataAnalysis agent if enabled
    use_data_analysis = config.run_flow_config.use_data_analysis_agent and not args.no_data_analysis
    if use_data_analysis:
        agents["data_analysis"] = DataAnalysis()
        logger.info("DataAnalysis agent enabled")

    try:
        if args.interactive:
            await run_interactive_flow_loop(agents, args.timeout)
        else:
            prompt = args.prompt if args.prompt else input("Enter your prompt: ")
            if not prompt.strip():
                logger.warning("Empty prompt provided.")
                return

            await execute_flow(agents, prompt, args.timeout)
    finally:
        # Cleanup all agents
        for agent in agents.values():
            if hasattr(agent, 'cleanup'):
                await agent.cleanup()


async def execute_flow(agents: dict, prompt: str, timeout: int) -> Optional[str]:
    """Execute a single flow with the given prompt."""
    flow = FlowFactory.create_flow(
        flow_type=FlowType.PLANNING,
        agents=agents,
    )
    logger.info("Processing your request...")

    try:
        start_time = time.time()
        result = await asyncio.wait_for(
            flow.execute(prompt),
            timeout=timeout,
        )
        elapsed_time = time.time() - start_time
        logger.info(f"Request processed in {elapsed_time:.2f} seconds")
        if result:
            print(f"\nResult:\n{result}")
        return result
    except asyncio.TimeoutError:
        logger.error(f"Request processing timed out after {timeout} seconds")
        print("Operation terminated due to timeout. Please try a simpler request.")
        return None


async def run_interactive_flow_loop(agents: dict, timeout: int) -> None:
    """Run flow mode in interactive loop."""
    print("\nOpenManus Flow Mode - Interactive (type 'exit' to quit)\n")
    while True:
        try:
            user_input = input("\nEnter your request: ").strip()
            if user_input.lower() in ["exit", "quit", "q"]:
                break
            if not user_input:
                continue
            await execute_flow(agents, user_input, timeout)
        except KeyboardInterrupt:
            break
    print("\nGoodbye!")


async def run_mcp_mode(args: argparse.Namespace) -> None:
    """Run in MCP-enabled agent mode."""
    agent = MCPAgent()
    server_reference = config.mcp_config.server_reference

    try:
        # Initialize MCP connection
        logger.info(f"Initializing MCPAgent with {args.connection} connection...")

        if args.connection == "stdio":
            await agent.initialize(
                connection_type="stdio",
                command=sys.executable,
                args=["-m", server_reference],
            )
        else:  # sse
            await agent.initialize(
                connection_type="sse",
                server_url=args.server_url
            )

        logger.info(f"Connected to MCP server via {args.connection}")

        # Execute based on mode
        if args.prompt:
            await agent.run(args.prompt)
        elif args.interactive:
            await run_interactive_loop(agent)
        else:
            prompt = input("Enter your prompt: ")
            if not prompt.strip():
                logger.warning("Empty prompt provided.")
                return

            logger.info("Processing your request...")
            await agent.run(prompt)
            logger.info("Request processing completed.")

    finally:
        await agent.cleanup()
        logger.info("MCP session ended")


async def run_interactive_loop(agent) -> None:
    """Run any agent in interactive loop mode."""
    print(f"\nOpenManus Interactive Mode - {agent.name} (type 'exit' to quit)\n")
    while True:
        try:
            user_input = input("\nEnter your request: ").strip()
            if user_input.lower() in ["exit", "quit", "q"]:
                break
            if not user_input:
                continue

            response = await agent.run(user_input)
            if response:
                print(f"\nAgent: {response}")

            # Reset agent state for next iteration
            if hasattr(agent, 'memory'):
                agent.memory.messages.clear()
            if hasattr(agent, 'current_step'):
                agent.current_step = 0

        except KeyboardInterrupt:
            break

    print("\nGoodbye!")


async def main() -> None:
    """Main entry point."""
    args = parse_args()

    try:
        if args.mode == ExecutionMode.SIMPLE.value:
            await run_simple_mode(args)
        elif args.mode == ExecutionMode.FLOW.value:
            await run_flow_mode(args)
        elif args.mode == ExecutionMode.MCP.value:
            await run_mcp_mode(args)
        else:
            raise ValueError(f"Unknown mode: {args.mode}")

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user.")
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
