"""
Tool loading utility to automatically discover and instantiate tools.
"""

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import List

from app.tool.base import BaseTool
from app.logger import logger

def load_all_tools() -> List[BaseTool]:
    """
    Automatically discover and instantiate all tool classes in app.tool package.
    
    Returns:
        List[BaseTool]: List of instantiated tool objects.
    """
    tools = []
    tool_package_path = Path(__file__).parent
    tool_package_name = "app.tool"

    logger.info(f"Discovering tools in {tool_package_path}...")

    # Iterate through all modules in app/tool/
    for module_info in pkgutil.iter_modules([str(tool_package_path)]):
        if module_info.name in ["base", "tool_collection", "__init__"]:
            continue
            
        try:
            # Import the module
            module = importlib.import_module(f"{tool_package_name}.{module_info.name}")
            
            # Find all classes in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if it's a subclass of BaseTool, but not BaseTool itself
                if (issubclass(obj, BaseTool) and 
                    obj is not BaseTool and 
                    not inspect.isabstract(obj)):
                    
                    # Avoid duplicates if multiple modules import the same tool
                    # and avoid private/internal classes (starting with _)
                    if not name.startswith("_"):
                        try:
                            # Try to instantiate with default arguments
                            # Some tools might fail if they require arguments
                            # We can try to handle specific cases or skip
                            if name == "SandboxBrowserTool":
                                # Skip sandbox tools for now if they require complex setup
                                # or handle them if we can
                                pass 
                            elif name == "PlanningTool":
                                tools.append(obj())
                            else:
                                tools.append(obj())
                                logger.debug(f"Loaded tool: {name}")
                        except Exception as e:
                            logger.warning(f"Could not instantiate tool {name}: {e}")
                            
        except Exception as e:
            logger.warning(f"Error loading module {module_info.name}: {e}")

    # Also check subpackages like 'search'
    # This is a simple implementation, a recursive one would be better for deep structures
    # But for now, app.tool.search seems to be the main one
    
    search_path = tool_package_path / "search"
    if search_path.exists() and search_path.is_dir():
         for module_info in pkgutil.iter_modules([str(search_path)]):
            if module_info.name in ["base", "__init__"]:
                continue
            try:
                module = importlib.import_module(f"{tool_package_name}.search.{module_info.name}")
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BaseTool) and 
                        obj is not BaseTool and 
                        not inspect.isabstract(obj)):
                         if not name.startswith("_"):
                            try:
                                tools.append(obj())
                                logger.debug(f"Loaded search tool: {name}")
                            except Exception as e:
                                logger.warning(f"Could not instantiate search tool {name}: {e}")
            except Exception as e:
                logger.warning(f"Error loading search module {module_info.name}: {e}")

    logger.info(f"Total tools loaded: {len(tools)}")
    return tools
