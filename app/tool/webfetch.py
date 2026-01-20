import asyncio
import json
from typing import ClassVar, Optional

import httpx
import markdownify
from bs4 import BeautifulSoup

from app.tool.base import BaseTool, ToolResult


_WEBFETCH_DESCRIPTION = """Fetches content from a specified URL
- Takes a URL and optional format as input
- Fetches the URL content, converts to requested format (markdown by default)
- Returns the content in the specified format
- Use this tool when you need to retrieve and analyze web content

Usage notes:
  - IMPORTANT: if another tool is present that offers better web fetching capabilities, is more targeted to the task, or has fewer restrictions, prefer using that tool instead of this one.
  - The URL must be a fully-formed valid URL
  - HTTP URLs will be automatically upgraded to HTTPS
  - Format options: "markdown" (default), "text", or "html"
  - This tool is read-only and does not modify any files
  - Results may be summarized if the content is very large
"""


class WebFetch(BaseTool):
    """A tool for fetching web content and converting it to different formats"""

    name: str = "webfetch"
    description: str = _WEBFETCH_DESCRIPTION
    parameters: dict = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to fetch content from",
            },
            "format": {
                "type": "string",
                "enum": ["text", "markdown", "html"],
                "default": "markdown",
                "description": "The format to return the content in (text, markdown, or html). Defaults to markdown.",
            },
            "timeout": {
                "type": "number",
                "description": "Optional timeout in seconds (max 120)",
            },
        },
        "required": ["url"],
    }

    MAX_RESPONSE_SIZE: ClassVar[int] = 5 * 1024 * 1024
    DEFAULT_TIMEOUT: ClassVar[float] = 30.0
    MAX_TIMEOUT: ClassVar[float] = 120.0

    async def execute(
        self, url: str, format: str = "markdown", timeout: Optional[float] = None, **kwargs
    ) -> ToolResult:
        if not url.startswith("http://") and not url.startswith("https://"):
            return self.fail_response("URL must start with http:// or https://")

        actual_timeout = min(timeout or self.DEFAULT_TIMEOUT, self.MAX_TIMEOUT)
        accept_header = self._get_accept_header(format)

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(actual_timeout),
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                    "Accept": accept_header,
                    "Accept-Language": "en-US,en;q=0.9",
                },
            ) as client:
                response = await client.get(url)

                if not response.is_success:
                    return self.fail_response(f"Request failed with status code: {response.status_code}")

                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > self.MAX_RESPONSE_SIZE:
                    return self.fail_response("Response too large (exceeds 5MB limit)")

                content = response.content
                if len(content) > self.MAX_RESPONSE_SIZE:
                    return self.fail_response("Response too large (exceeds 5MB limit)")

                content_str = content.decode("utf-8", errors="ignore")
                content_type = response.headers.get("content-type", "")

                title = f"{url} ({content_type})"
                if format == "markdown":
                    if "text/html" in content_type:
                        result_content = self._html_to_markdown(content_str)
                    else:
                        result_content = content_str
                elif format == "text":
                    if "text/html" in content_type:
                        result_content = self._extract_text_from_html(content_str)
                    else:
                        result_content = content_str
                elif format == "html":
                    result_content = content_str
                else:
                    result_content = content_str

                return self.success_response({
                    "output": result_content,
                    "title": title,
                    "metadata": {},
                })

        except httpx.TimeoutException:
            return self.fail_response(f"Request timed out after {actual_timeout} seconds")
        except httpx.RequestError as e:
            return self.fail_response(f"Request failed: {str(e)}")
        except Exception as e:
            return self.fail_response(f"Unexpected error: {str(e)}")

    def _get_accept_header(self, format: str) -> str:
        """Build Accept header based on requested format with q parameters for fallbacks."""
        if format == "markdown":
            return "text/markdown;q=1.0, text/x-markdown;q=0.9, text/plain;q=0.8, text/html;q=0.7, */*;q=0.1"
        elif format == "text":
            return "text/plain;q=1.0, text/markdown;q=0.9, text/html;q=0.8, */*;q=0.1"
        elif format == "html":
            return "text/html;q=1.0, application/xhtml+xml;q=0.9, text/plain;q=0.8, text/markdown;q=0.7, */*;q=0.1"
        else:
            return "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"

    def _extract_text_from_html(self, html: str) -> str:
        """Extract readable text from HTML content."""
        try:
            soup = BeautifulSoup(html, "html.parser")
            for element in soup(["script", "style", "noscript", "iframe", "object", "embed"]):
                element.decompose()
            return soup.get_text(separator="\n", strip=True)
        except Exception:
            return html

    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to markdown."""
        try:
            md = markdownify.MarkdownConverter(
                heading_style="atx",
                bullets="-",
                code_language_callback=lambda el: "",
            )
            return md.convert(html)
        except Exception:
            return f"<error>Failed to convert HTML to markdown</error>\n\n{html}"


if __name__ == "__main__":
    webfetch = WebFetch()
    result = asyncio.run(webfetch.execute("https://httpbin.org/html"))
    print(result)