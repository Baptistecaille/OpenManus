from typing import List

from tavily import (
    TavilyClient,
    UsageLimitExceededError,
    BadRequestError,
    InvalidAPIKeyError,
    MissingAPIKeyError,
)

from app.config import config
from app.logger import logger
from app.tool.search.base import SearchItem, WebSearchEngine


class TavilySearchEngine(WebSearchEngine):
    def perform_search(
        self, query: str, num_results: int = 10, *args, **kwargs
    ) -> List[SearchItem]:
        """
        Tavily search engine.

        Returns results formatted according to SearchItem model.
        Falls back to next engine on quota errors.
        """
        try:
            api_key = (
                getattr(config.search_config, "tavily_api_key", "")
                if config.search_config
                else ""
            )

            if not api_key:
                logger.warning("Tavily API key not configured, falling back to next engine")
                return []

            client = TavilyClient(api_key=api_key)
            response = client.search(query, max_results=num_results)

            results = []
            for i, item in enumerate(response.get("results", [])):
                results.append(
                    SearchItem(
                        title=item.get("title", f"Tavily Result {i + 1}"),
                        url=item.get("url", ""),
                        description=item.get("content", None),
                    )
                )

            return results

        except UsageLimitExceededError:
            logger.warning(
                "Tavily usage limit exceeded, falling back to next engine"
            )
            return []

        except (
            BadRequestError,
            InvalidAPIKeyError,
            MissingAPIKeyError,
        ) as e:
            logger.warning(f"Tavily API error: {e}, falling back to next engine")
            return []

        except Exception as e:
            logger.error(f"Unexpected Tavily error: {e}, falling back to next engine")
            return []
