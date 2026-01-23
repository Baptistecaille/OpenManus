import sys
import traceback
from app.config import config
from app.llm import LLM


def debug_config():
    print("--- Debugging Config ---")
    try:
        print(f"Config initialized: {config._initialized}")
        print(f"LLM Config Keys: {config.llm.keys()}")

        default_config = config.llm.get("default")
        if default_config:
            print("Default LLM Config:")
            print(f"  Model: {default_config.model}")
            print(f"  Base URL: {default_config.base_url}")
            print(f"  API Type: '{default_config.api_type}'")
            print(f"  API Key Present: {bool(default_config.api_key)}")
            print(
                f"  API Key Length: {len(default_config.api_key) if default_config.api_key else 0}"
            )
        else:
            print("No 'default' LLM config found.")

        print("\n--- Instantiating LLM ---")
        try:
            # Replicate agent initialization
            print("Attempting: LLM(config_name='manus')")
            llm_instance = LLM(config_name="manus")
            print(f"LLM instantiated successfully.")
            print(f"LLM Model: {llm_instance.model}")
            print(f"LLM API Type: '{llm_instance.api_type}'")
            print(f"LLM Base URL: {llm_instance.base_url}")

            client = llm_instance.client
            print(f"LLM Client type: {type(client)}")
            print(f"LLM Client is None: {client is None}")

            if client is None:
                print("Checking _client private attr:", llm_instance._client)

        except Exception as e:
            print(f"Failed to instantiate LLM: {e}")
            traceback.print_exc()

    except Exception as e:
        print(f"Error inspecting config: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    debug_config()
