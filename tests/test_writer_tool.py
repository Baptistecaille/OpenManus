"""Test file for Writer tool."""

import pytest
import asyncio
from pathlib import Path
from app.tool.writer import WriterTool


@pytest.mark.asyncio
async def test_writer_basic():
    """Test basic writer functionality."""
    tool = WriterTool()
    content = """
    Algebra is a branch of mathematics that studies algebraic structures and the operations they use.
    History: Algebra was developed over centuries, with contributions from Babylonian, Greek, and Islamic mathematicians.
    Applications: Used in physics, engineering, computer science, and economics.
    """
    
    result = await tool.execute(
        topic="Algebra",
        content=content,
        output_path="/tmp/test_algebra_report.md"
    )
    
    assert result.error is None
    assert Path("/tmp/test_algebra_report.md").exists()
    assert "Algebra" in result.output
    
    # Cleanup
    Path("/tmp/test_algebra_report.md").unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_language_detection_french():
    """Test language detection for French."""
    tool = WriterTool()
    
    french_request = "écris un rapport sur l'algèbre"
    detected = tool._detect_language(french_request, "", None)
    assert detected == 'fr'


@pytest.mark.asyncio
async def test_language_detection_english():
    """Test language detection for English."""
    tool = WriterTool()
    
    english_request = "write a report about algebra"
    detected = tool._detect_language(english_request, "", None)
    assert detected == 'en'


@pytest.mark.asyncio
async def test_explicit_language():
    """Test explicit language override."""
    tool = WriterTool()
    content = "Algebra is mathematics."
    
    result = await tool.execute(
        topic="Algebra",
        content=content,
        output_path="/tmp/test_explicit_language.md",
        language="en"
    )
    
    assert result.error is None
    assert '"language": "en"' in result.output
    
    # Cleanup
    Path("/tmp/test_explicit_language.md").unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_content_parser_html():
    """Test content parser with HTML content."""
    tool = WriterTool()
    content = """
    <h1>Algebra</h1>
    <h2>Introduction</h2>
    <p>Algebra is a fundamental branch of mathematics.</p>
    <h2>History</h2>
    <p>Algebra has ancient origins.</p>
    """
    
    result = await tool.execute(
        topic="Algebra",
        content=content,
        output_path="/tmp/test_html_parsing.md"
    )
    
    assert result.error is None
    assert Path("/tmp/test_html_parsing.md").exists()
    
    # Cleanup
    Path("/tmp/test_html_parsing.md").unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_empty_content():
    """Test error handling with empty content."""
    tool = WriterTool()
    
    result = await tool.execute(
        topic="Empty",
        content="",
        output_path="/tmp/test_empty.md"
    )
    
    # Should fail after retries
    assert result.error is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
