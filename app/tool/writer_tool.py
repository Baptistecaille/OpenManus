"""Writer tool for generating structured markdown reports from research content."""

import asyncio
from pathlib import Path
from typing import Optional

from app.tool.base import BaseTool, ToolResult
from app.tool.writer.content_parser import ContentParser
from app.tool.writer.language_detector import LanguageDetector
from app.tool.writer.report_generator import ReportGenerator
from app.tool.writer.retry_handler import RetryHandler
from app.tool.file_operators import LocalFileOperator, SandboxFileOperator
from app.config import config
from app.logger import logger


class WriterTool(BaseTool):
    """Tool for generating structured markdown reports from research content."""
    
    name: str = "writer"
    description: str = """Generate structured markdown reports from research content.
    Supports automatic language detection, content extraction, and report generation.
    Reports include introduction, variable sections, and conclusion."""
    
    parameters: dict = {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The main topic or subject to write about"
            },
            "content": {
                "type": "string",
                "description": "Raw research content to process"
            },
            "language": {
                "type": "string",
                "description": "Language for the report (fr/en). Default: French."
            },
            "output_path": {
                "type": "string",
                "description": "File path where the report will be saved"
            }
        },
        "required": ["topic", "content", "output_path"]
    }
    
    _local_operator: LocalFileOperator = LocalFileOperator()
    _sandbox_operator: SandboxFileOperator = SandboxFileOperator()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.language_detector = LanguageDetector(default_language='fr')
        self.content_parser = ContentParser()
        self.report_generator = ReportGenerator()
        self.retry_handler = RetryHandler(max_retries=3)
    
    def _get_operator(self):
        """Get appropriate file operator based on execution mode."""
        return (
            self._sandbox_operator
            if config.sandbox.use_sandbox
            else self._local_operator
        )
    
    async def execute(
        self,
        topic: str,
        content: str,
        output_path: str,
        language: Optional[str] = None
    ) -> ToolResult:
        """Execute the writer tool."""
        try:
            logger.info(f"📝 Writer tool: Generating report on '{topic}'")
            
            detected_language = self._detect_language(topic, content, language)
            confirmed_language = self.language_detector.confirm_language(detected_language)
            
            logger.info(f"🌐 Language: {confirmed_language}")
            
            def parse_content():
                return self.content_parser.parse_raw_content(content)
            
            sections = self.retry_handler.execute_with_retry(parse_content)
            
            self.report_generator.language = confirmed_language
            report = self.report_generator.generate_report(topic, sections)
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            async def write_file():
                operator = self._get_operator()
                return await operator.write_file(output_path, report)
            
            self.retry_handler.execute_with_retry(lambda: asyncio.run(write_file()))
            
            logger.info(f"✅ Report saved to {output_path}")
            
            return self.success_response({
                "topic": topic,
                "output_path": output_path,
                "language": confirmed_language,
                "sections_count": len([k for k, v in sections.items() if v])
            })
            
        except ToolError as e:
            logger.error(f"❌ Writer tool failed: {e}")
            return self.fail_response(str(e))
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return self.fail_response(f"Unexpected error: {str(e)}")
    
    def _detect_language(
        self,
        topic: str,
        content: str,
        provided_language: Optional[str]
    ) -> str:
        """Detect or validate language."""
        if provided_language:
            if provided_language.lower() in ['fr', 'en']:
                return provided_language.lower()
            logger.warning(f"Unsupported language '{provided_language}', using auto-detection")
        
        detected = self.language_detector.detect_from_text(content)
        detected_from_topic = self.language_detector.detect_from_request(topic)
        
        if detected == detected_from_topic:
            return detected
        else:
            logger.info(f"Language conflict detected ({detected} vs {detected_from_topic}), using default")
            return 'fr'
