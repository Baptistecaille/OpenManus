import asyncio
import pytest
from app.tool.webfetch import WebFetch


class TestWebFetch:
    """Test suite for WebFetch tool to ensure it matches opencode functionality"""

    @pytest.fixture
    def webfetch(self):
        return WebFetch()

    @pytest.mark.asyncio
    async def test_url_validation(self, webfetch):
        """Test URL validation - should reject invalid URLs"""
        result = await webfetch.execute("invalid-url")
        assert result.error == "URL must start with http:// or https://"

    @pytest.mark.asyncio
    async def test_markdown_format(self, webfetch):
        """Test markdown format conversion"""
        result = await webfetch.execute("https://httpbin.org/html", format="markdown")
        assert result.output is not None
        assert "Herman Melville" in result.output
        # Should contain markdown headers
        assert "#" in result.output

    @pytest.mark.asyncio
    async def test_text_format(self, webfetch):
        """Test text format extraction"""
        result = await webfetch.execute("https://httpbin.org/html", format="text")
        assert result.output is not None
        assert "Herman Melville" in result.output
        # Should not contain HTML tags
        assert "<" not in result.output or "<error>" in result.output

    @pytest.mark.asyncio
    async def test_html_format(self, webfetch):
        """Test HTML format preservation"""
        result = await webfetch.execute("https://httpbin.org/html", format="html")
        assert result.output is not None
        # Should contain HTML tags
        assert "<" in result.output and "<html" in result.output

    @pytest.mark.asyncio
    async def test_timeout_parameter(self, webfetch):
        """Test timeout parameter handling"""
        result = await webfetch.execute("https://httpbin.org/html", timeout=10.0)
        assert result.output is not None
        # Should succeed with valid timeout

    @pytest.mark.asyncio
    async def test_default_timeout(self, webfetch):
        """Test default timeout behavior"""
        # This should use DEFAULT_TIMEOUT (30 seconds)
        result = await webfetch.execute("https://httpbin.org/html")
        assert result.output is not None

    @pytest.mark.asyncio
    async def test_tool_schema(self, webfetch):
        """Test that tool schema matches expected structure"""
        schema = webfetch.to_param()
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "webfetch"
        assert "url" in schema["function"]["parameters"]["properties"]
        assert "format" in schema["function"]["parameters"]["properties"]
        assert "timeout" in schema["function"]["parameters"]["properties"]
        assert schema["function"]["parameters"]["required"] == ["url"]

    @pytest.mark.asyncio
    async def test_response_structure(self, webfetch):
        """Test response structure matches expected format"""
        result = await webfetch.execute("https://httpbin.org/html")
        import json
        response_data = json.loads(result.output)
        assert "output" in response_data
        assert "title" in response_data
        assert "metadata" in response_data


if __name__ == "__main__":
    # Run basic functionality tests
    async def run_tests():
        webfetch = WebFetch()

        print("Testing URL validation...")
        result = await webfetch.execute("invalid-url")
        assert result.error == "URL must start with http:// or https://"
        print("✓ URL validation works")

        print("Testing markdown format...")
        result = await webfetch.execute("https://httpbin.org/html", format="markdown")
        assert result.output and "Herman Melville" in result.output
        print("✓ Markdown format works")

        print("Testing text format...")
        result = await webfetch.execute("https://httpbin.org/html", format="text")
        assert result.output and "Herman Melville" in result.output
        print("✓ Text format works")

        print("Testing HTML format...")
        result = await webfetch.execute("https://httpbin.org/html", format="html")
        assert result.output and "<html" in result.output
        print("✓ HTML format works")

        print("All tests passed! WebFetch functionality matches opencode implementation.")

    asyncio.run(run_tests())