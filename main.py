import argparse
import asyncio

from app.agent.manus import Manus
from app.agent.web_research import WebResearchAgent
from app.logger import logger


async def main():
    parser = argparse.ArgumentParser(description="Run Manus agent with a prompt")
    parser.add_argument(
        "--prompt", type=str, required=False, help="Input prompt for the agent"
    )
    parser.add_argument(
        "--agent",
        type=str,
        default="manus",
        choices=["manus", "research", "web-research"],
        help="Agent to use: 'manus' for general purpose, 'research' for web research",
    )
    args = parser.parse_args()

    if args.agent in ["research", "web-research"]:
        agent = await WebResearchAgent.create()
        logger.info("Using WebResearch agent for comprehensive web research")
    else:
        agent = await Manus.create()
        logger.info("Using Manus agent for general purpose tasks")

    try:
        prompt = args.prompt if args.prompt else input("Enter your prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        logger.warning("Processing your request...")
        await agent.run(prompt)
        logger.info("Request processing completed.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
