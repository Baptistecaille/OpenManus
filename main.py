import argparse
import asyncio

from app.agent.manus import Manus
from app.agent.research_master import ResearchMasterPro
from app.logger import logger


async def main():
    parser = argparse.ArgumentParser(description="Run OpenManus agent with a prompt")
    parser.add_argument(
        "--prompt", type=str, required=False, help="Input prompt for the agent"
    )
    parser.add_argument(
        "--search", action="store_true", help="Use ResearchMaster Pro agent for internet search and structured research"
    )
    args = parser.parse_args()

    if args.search:
        agent = ResearchMasterPro()
    else:
        agent = await Manus.create()
    
    try:
        prompt = args.prompt if args.prompt else None
        if prompt is None:
            logger.error("No prompt provided. Use --prompt to specify a prompt.")
            return
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
