import asyncio
import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.config import config
from app.logger import logger
from app.tool.base import BaseTool, ToolResult
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.web_search import SearchResult, WebSearch


class ResearchSource(BaseModel):
    """Represents a researched source with extracted content."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: str = Field(description="URL of the source")
    title: str = Field(default="", description="Title of the page")
    position: int = Field(description="Position in search results")
    extracted_content: Dict[str, Any] = Field(
        default_factory=dict, description="Extracted content from the page"
    )
    relevance_score: float = Field(
        default=0.0, description="Relevance score of the source to the query"
    )
    error: Optional[str] = Field(default=None, description="Error if extraction failed")


class ResearchResult(ToolResult):
    """Structured result from the web research tool."""

    query: str = Field(description="The research query")
    sources: List[ResearchSource] = Field(
        default_factory=list, description="Researched sources with extracted content"
    )
    synthesis: Optional[str] = Field(
        default=None, description="AI-generated synthesis of all findings"
    )
    total_sources_visited: int = Field(
        default=0, description="Total number of sources visited"
    )
    total_sources_found: int = Field(
        default=0, description="Total number of sources found in search"
    )

    def __str__(self) -> str:
        """String representation of research results."""
        lines = [f"Research results for '{self.query}':"]
        lines.append(f"Total sources found: {self.total_sources_found}")
        lines.append(f"Sources visited: {self.total_sources_visited}")
        lines.append("")

        for source in self.sources:
            status = "ERROR" if source.error else "OK"
            lines.append(f"[{status}] {source.title}")
            lines.append(f"  URL: {source.url}")
            if source.error:
                lines.append(f"  Error: {source.error}")
            else:
                content_str = json.dumps(
                    source.extracted_content, indent=6, ensure_ascii=False
                )
                lines.append(f"  Content: {content_str}")
            lines.append("")

        if self.synthesis:
            lines.append("Synthesis:")
            lines.append(self.synthesis)

        return "\n".join(lines)


class EnhancedWebResearchTool(BaseTool):
    """Advanced web research tool that searches the web and extracts information from multiple sources."""

    name: str = "enhanced_web_research"
    description: str = """Perform comprehensive web research by searching for information and extracting content from multiple sources.
    This tool:
    1. Searches the web using multiple search engines
    2. Visits each search result URL
    3. Extracts relevant content based on your extraction goal
    4. Provides a synthesis of all findings

    Use this when you need to gather information from multiple sources, compare data across websites,
    or perform in-depth research on a topic."""
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "(required) The research question or topic to investigate",
            },
            "num_urls": {
                "type": "integer",
                "description": "(optional) Number of URLs to visit. Default is 5, maximum is 10.",
                "default": 5,
            },
            "extract_goal": {
                "type": "string",
                "description": "(optional) Specific goal for content extraction. Be precise about what information you want.",
                "default": "Summarize the main content and key information relevant to the research query",
            },
            "browse_all": {
                "type": "boolean",
                "description": "(optional) Whether to browse all found URLs. If false, only the first URL is visited. Default is true.",
                "default": True,
            },
            "synthesis": {
                "type": "boolean",
                "description": "(optional) Whether to generate an AI synthesis of all findings. Default is true.",
                "default": True,
            },
            "timeout_per_page": {
                "type": "integer",
                "description": "(optional) Maximum seconds to wait per page. Default is 30.",
                "default": 30,
            },
        },
        "required": ["query"],
    }

    web_search: WebSearch = Field(default_factory=WebSearch, exclude=True)
    browser_use: BrowserUseTool = Field(default_factory=BrowserUseTool, exclude=True)

    async def execute(
        self,
        query: str,
        num_urls: int = 5,
        extract_goal: str = "Summarize the main content and key information relevant to the research query",
        browse_all: bool = True,
        synthesis: bool = True,
        timeout_per_page: int = 30,
        **kwargs,
    ) -> ResearchResult:
        """
        Perform comprehensive web research.

        Args:
            query: The research question or topic to investigate
            num_urls: Number of URLs to visit (1-10, default 5)
            extract_goal: Specific goal for content extraction
            browse_all: Whether to browse all found URLs (default True)
            synthesis: Whether to generate AI synthesis (default True)
            timeout_per_page: Maximum seconds per page (default 30)

        Returns:
            ResearchResult with sources and optional synthesis
        """
        num_urls = min(max(1, num_urls), 10)
        timeout_per_page = min(max(5, timeout_per_page), 120)

        logger.info(f"🔬 Starting web research for: {query}")
        logger.info(f"   - URLs to visit: {num_urls}")
        logger.info(f"   - Browse all: {browse_all}")
        logger.info(f"   - Synthesis: {synthesis}")

        try:
            search_response = await self.web_search.execute(
                query=query,
                num_results=num_urls if browse_all else 1,
                fetch_content=False,
            )

            if search_response.error or not search_response.results:
                return ResearchResult(
                    query=query,
                    error=f"Search failed: {search_response.error or 'No results found'}",
                    total_sources_found=0,
                    total_sources_visited=0,
                )

            sources = []
            results_to_browse = search_response.results[:num_urls]

            for i, result in enumerate(results_to_browse):
                logger.info(
                    f"   [{i+1}/{len(results_to_browse)}] Visiting: {result.url}"
                )

                source = await self._visit_and_extract(
                    result=result,
                    position=result.position,
                    extract_goal=extract_goal,
                    timeout=timeout_per_page,
                )
                sources.append(source)

                if i < len(results_to_browse) - 1:
                    await asyncio.sleep(1)

            synthesis_text = None
            if synthesis and sources:
                logger.info(f"   Generating synthesis from {len(sources)} sources...")
                synthesis_text = await self._generate_synthesis(
                    query=query, sources=sources, extract_goal=extract_goal
                )

            return ResearchResult(
                query=query,
                sources=sources,
                synthesis=synthesis_text,
                total_sources_visited=len(sources),
                total_sources_found=len(search_response.results),
            )

        except Exception as e:
            logger.error(f"Research failed: {e}")
            return ResearchResult(
                query=query,
                error=str(e),
                total_sources_found=0,
                total_sources_visited=0,
            )

    async def _visit_and_extract(
        self,
        result: SearchResult,
        position: int,
        extract_goal: str,
        timeout: int,
    ) -> ResearchSource:
        """Visit a URL and extract content based on the goal."""
        source = ResearchSource(
            url=result.url,
            title=result.title,
            position=position,
        )

        try:
            page_result = await self.browser_use.execute(
                action="go_to_url",
                url=result.url,
            )

            if page_result.error:
                source.error = f"Navigation failed: {page_result.error}"
                return source

            await asyncio.sleep(2)

            extraction_result = await self.browser_use.execute(
                action="extract_content",
                goal=f"""{extract_goal}

Research query: {extract_goal}

Please extract all relevant information from this page. Return a structured JSON object with:
- summary: Brief summary of the page content
- key_points: List of important points
- relevant_data: Any data relevant to the research query
- any_other_useful_info: Additional useful information

If the page doesn't contain relevant information, return an empty object {{}}.""",
            )

            if extraction_result.error:
                source.error = f"Extraction failed: {extraction_result.error}"
                return source

            try:
                output_text = extraction_result.output or ""

                json_start = output_text.find("{")
                json_end = output_text.rfind("}")

                if json_start != -1 and json_end != -1:
                    json_str = output_text[json_start : json_end + 1]
                    extracted = json.loads(json_str)
                    source.extracted_content = extracted
                elif output_text:
                    source.extracted_content = {"raw_text": output_text[:2000]}
                else:
                    source.extracted_content = {}

            except json.JSONDecodeError:
                source.extracted_content = {"raw_text": output_text[:2000]}

            if source.extracted_content:
                source.relevance_score = self._calculate_relevance(
                    source.extracted_content, extract_goal
                )

        except Exception as e:
            source.error = str(e)

        return source

    def _calculate_relevance(
        self, extracted_content: Dict[str, Any], query: str
    ) -> float:
        """Calculate a simple relevance score based on content presence."""
        if not extracted_content or extracted_content == {}:
            return 0.0

        query_lower = query.lower()
        content_str = str(extracted_content).lower()

        words = [w for w in query_lower.split() if len(w) > 3]
        if not words:
            return 0.5

        matches = sum(1 for word in words if word in content_str)
        return min(1.0, matches / len(words) * 2)

    async def _generate_synthesis(
        self,
        query: str,
        sources: List[ResearchSource],
        extract_goal: str,
    ) -> str:
        """Generate an AI synthesis of all researched sources."""
        from app.llm import LLM

        llm = LLM()

        sources_text = []
        for i, source in enumerate(sources):
            status = "ERROR" if source.error else "SUCCESS"
            sources_text.append(
                f"Source {i+1} [{status}]: {source.title}"
                f"\nURL: {source.url}"
                f"\nExtracted: {json.dumps(source.extracted_content, indent=2, ensure_ascii=False)}"
            )

        prompt = f"""You are a research assistant. Synthesize the following research findings:

Research Query: {query}
Extraction Goal: {extract_goal}

Sources:
{'='*60}
{sources_text}

{'='*60}

Please provide a comprehensive synthesis that:
1. Summarizes the key findings from all successful sources
2. Notes any contradictions or differences between sources
3. Provides a final assessment or conclusion

If some sources failed, note which ones and why they might be important to revisit.

Write in clear, professional prose. Be thorough but concise."""

        try:
            response = await llm.ask(
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.5,
            )
            return response if response else "Failed to generate synthesis."
        except Exception as e:
            logger.error(f"Synthesis generation failed: {e}")
            return f"Synthesis generation failed: {str(e)}"


if __name__ == "__main__":
    import asyncio

    async def test():
        tool = EnhancedWebResearchTool()
        result = await tool.execute(
            query="What are the latest developments in AI agents in 2025?",
            num_urls=3,
            synthesis=True,
        )
        print(result)

    asyncio.run(test())
