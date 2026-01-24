import sys
import os
import asyncio

# Add current directory to path
sys.path.append(os.getcwd())

from app.llm import LLM
from app.config import config
import logging

# Configure logging to see outputs
logging.basicConfig(level=logging.INFO)


async def test_llm():
    print("Testing LLM initialization...")

    # Print config details again
    try:
        llm_config = config.llm["default"]
        print(f"Config Model: {llm_config.model}")
        print(f"Config API Type: {llm_config.api_type}")
        print(f"Config Base URL: {llm_config.base_url}")
    except Exception as e:
        print(f"Error checking config: {e}")

    try:
        llm = LLM()
        print(f"LLM instance created.")
        print(f"Client: {llm.client}")
        if llm.client is None:
            print("ERROR: LLM client is None!")
        else:
            print("SUCCESS: LLM client initialized.")

    except Exception as e:
        print(f"LLM initialization raised exception: {e}")


if __name__ == "__main__":
    asyncio.run(test_llm())
