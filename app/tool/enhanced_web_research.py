import asyncio
import json
import re
import os
from datetime import datetime
from pathlib import Path
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

            research_result = ResearchResult(
                query=query,
                sources=sources,
                synthesis=synthesis_text,
                total_sources_visited=len(sources),
                total_sources_found=len(search_response.results),
            )

            markdown_path = self._save_markdown(query, research_result)
            research_result.output = (
                f"Research report saved to: {markdown_path}\n\n{research_result}"
            )

            return research_result

        except Exception as e:
            logger.error(f"Research failed: {e}")
            error_result = ResearchResult(
                query=query,
                error=str(e),
                total_sources_found=0,
                total_sources_visited=0,
            )
            markdown_path = self._save_markdown(query, error_result)
            error_result.output = (
                f"Research report saved to: {markdown_path}\n\n{error_result}"
            )
            return error_result

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
        """Generate a comprehensive synthesis of all researched sources."""
        from app.llm import LLM

        llm = LLM()

        successful_sources = [s for s in sources if not s.error]
        failed_sources = [s for s in sources if s.error]

        sources_text = []
        for i, source in enumerate(sources):
            status = "SUCCESS" if not source.error else "FAILED"
            content = source.extracted_content or {}

            source_info = {
                "id": i + 1,
                "status": status,
                "title": source.title,
                "url": source.url,
                "relevance_score": source.relevance_score,
                "content": content,
            }
            sources_text.append(source_info)

        prompt = f"""You are an expert research analyst. Your task is to synthesize findings from multiple web sources into a comprehensive, insightful report.

## Research Question
{query}

## Extraction Goal
{extract_goal}

## Sources Analyzed
{json.dumps(sources_text, indent=2, ensure_ascii=False, default=str)}

---

## Required Output Format

### 1. Source Selection Rationale
Explain WHY these specific sources were chosen:
- What made each source relevant to the research question?
- How did the relevance scores influence selection?
- Were certain sources selected for credibility (official docs,权威 sources)?

### 2. Thematic Synthesis
Organize findings by THEME, not by source. For each theme:
- What do the sources collectively say about this topic?
- Highlight agreements and disagreements between sources
- Provide specific attributions (Source X found that...)

### 3. Key Insights
List 3-5 most important takeaways with evidence from the sources.

### 4. Knowledge Gaps
What questions remain unanswered? Which sources would be worth revisiting?

### 5. Conclusion
A concise summary that directly answers the original research question.

---

## Writing Guidelines
- Use prose over lists when possible
- When using lists, keep them to 4 items maximum with substantial content
- Be specific: cite source findings, not generalities
- Explain connections between sources
- Professional, analytical tone
- No citations or references section needed"""

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

    def _slugify(self, text: str) -> str:
        """Convert text to a URL-friendly slug."""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_-]+", "-", text)
        text = re.sub(r"^-+|-+$", "", text)
        return text[:50]

    def _generate_markdown(self, query: str, result: ResearchResult) -> str:
        """Generate a markdown report from research results."""
        lines = [
            "# Web Research Report",
            "",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Query:** {query}",
            f"**Sources Found:** {result.total_sources_found}",
            f"**Sources Visited:** {result.total_sources_visited}",
            "",
            "---",
            "",
            "## Summary",
            "",
            f"**Total Sources:** {result.total_sources_found}",
            f"**Successfully Visited:** {result.total_sources_visited}",
            f"**Failed:** {result.total_sources_found - result.total_sources_visited}",
            "",
            "---",
            "",
            "## Sources",
            "",
        ]

        for source in result.sources:
            status = "❌" if source.error else "✅"
            lines.append(f"### {status} Source {source.position}: {source.title}")
            lines.append("")
            lines.append(f"**URL:** [{source.url}]({source.url})")
            lines.append("")

            if source.error:
                lines.append(f"**Error:** {source.error}")
            else:
                if source.relevance_score > 0:
                    lines.append(f"**Relevance Score:** {source.relevance_score:.1%}")
                    lines.append("")

                content = source.extracted_content
                if content:
                    if isinstance(content, dict):
                        if "summary" in content and content["summary"]:
                            lines.append("**Summary:**")
                            lines.append(content["summary"])
                            lines.append("")

                        if "key_points" in content and content["key_points"]:
                            lines.append("**Key Points:**")
                            for point in content["key_points"]:
                                lines.append(f"- {point}")
                            lines.append("")

                        if "relevant_data" in content and content["relevant_data"]:
                            lines.append("**Relevant Data:**")
                            lines.append(
                                f"```json\n{json.dumps(content['relevant_data'], indent=2)}\n```"
                            )
                            lines.append("")

                        if (
                            "any_other_useful_info" in content
                            and content["any_other_useful_info"]
                        ):
                            lines.append("**Additional Info:**")
                            lines.append(content["any_other_useful_info"])
                            lines.append("")

                        if "raw_text" in content:
                            lines.append("**Raw Content:**")
                            lines.append(
                                content["raw_text"][:500] + "..."
                                if len(content["raw_text"]) > 500
                                else content["raw_text"]
                            )
            lines.append("")
            lines.append("---")
            lines.append("")

        if result.synthesis:
            lines.append("## Synthesis")
            lines.append("")
            lines.append(result.synthesis)
            lines.append("")

        lines.append("")
        lines.append("---")
        lines.append(
            f"*Report generated by WebResearchAgent on {datetime.now().strftime('%Y-%m-%d')}*"
        )

        return "\n".join(lines)

    def _save_markdown(self, query: str, result: ResearchResult) -> str:
        """Save research results to a markdown file and return the path."""
        workspace_root = config.workspace_root
        research_dir = workspace_root / "research"
        research_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = self._slugify(query)
        filename = f"{timestamp}_{slug}.md"
        filepath = research_dir / filename

        markdown_content = self._generate_markdown(query, result)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        logger.info(f"   📄 Research report saved to: {filepath}")
        return str(filepath)


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
