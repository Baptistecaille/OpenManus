"""Content parsing module for extracting structured information from raw content."""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from app.logger import logger


class ContentParser:
    """Parse and structure raw content for report generation."""
    
    def parse_raw_content(self, content: str) -> Dict[str, any]:
        """Parse raw content into structured sections."""
        sections = {
            'introduction': '',
            'definition': '',
            'history': '',
            'branches': [],
            'applications': [],
            'conclusion': ''
        }
        
        # First try to parse as markdown with # headers
        if self._is_markdown_format(content):
            return self._parse_markdown(content)
        
        # Then try to parse as HTML
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                section_name = heading.get_text().strip().lower()
                section_content = self._extract_section_content(heading)
                
                if any(keyword in section_name for keyword in ['introduction', 'intro']):
                    sections['introduction'] = section_content
                elif any(keyword in section_name for keyword in ['definition', 'what is']):
                    sections['definition'] = section_content
                elif any(keyword in section_name for keyword in ['history', 'historical']):
                    sections['history'] = section_content
                elif any(keyword in section_name for keyword in ['branch', 'type']):
                    sections['branches'].append({
                        'name': heading.get_text().strip(),
                        'content': section_content
                    })
                elif any(keyword in section_name for keyword in ['application', 'use']):
                    sections['applications'].append({
                        'name': heading.get_text().strip(),
                        'content': section_content
                    })
                elif any(keyword in section_name for keyword in ['conclusion', 'summary']):
                    sections['conclusion'] = section_content
            
            return sections
            
        except Exception as e:
            logger.warning(f"HTML parsing failed, treating as plain text: {e}")
            return self._parse_plain_text(content)
    
    def _is_markdown_format(self, content: str) -> bool:
        """Check if content is in markdown format with # headers."""
        return bool('#' in content)
    
    def _parse_markdown(self, content: str) -> Dict[str, any]:
        """Parse markdown-style content with # headers."""
        sections = {
            'introduction': '',
            'definition': '',
            'history': '',
            'branches': [],
            'applications': [],
            'conclusion': ''
        }
        
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for markdown headers
            if line.startswith('### '):
                # H3 header
                if current_section:
                    self._add_parsed_content(sections, current_section, current_content)
                
                header_text = line[3:].strip().lower()
                if any(keyword in header_text for keyword in ['elementary', 'linear', 'abstract']):
                    current_section = 'branches'
                    current_content = [line[3:].strip()]
                elif any(keyword in header_text for keyword in ['physics', 'computer', 'economics', 'engineering']):
                    current_section = 'applications'
                    current_content = [line[3:].strip()]
                else:
                    current_section = None
                    current_content = []
            elif line.startswith('## '):
                # H2 header
                if current_section:
                    self._add_parsed_content(sections, current_section, current_content)
                
                header_text = line[2:].strip().lower()
                if any(keyword in header_text for keyword in ['introduction', 'intro']):
                    current_section = 'introduction'
                    current_content = [line[2:].strip()]
                elif any(keyword in header_text for keyword in ['definition']):
                    current_section = 'definition'
                    current_content = [line[2:].strip()]
                elif any(keyword in header_text for keyword in ['history']):
                    current_section = 'history'
                    current_content = [line[2:].strip()]
                elif any(keyword in header_text for keyword in ['branch', 'type']):
                    current_section = 'branches'
                    current_content = [line[2:].strip()]
                elif any(keyword in header_text for keyword in ['application', 'use']):
                    current_section = 'applications'
                    current_content = [line[2:].strip()]
                elif any(keyword in header_text for keyword in ['conclusion', 'summary']):
                    current_section = 'conclusion'
                    current_content = [line[2:].strip()]
                else:
                    current_section = None
                    current_content = []
            elif line.startswith('# '):
                # H1 header (skip or use as title)
                if current_section:
                    self._add_parsed_content(sections, current_section, current_content)
                current_section = None
                current_content = []
            else:
                # Content line
                if current_section:
                    current_content.append(line)
                else:
                    # No section yet, add to introduction by default
                    sections['introduction'] += ' ' + line
        
        # Don't forget to add the last section
        if current_section:
            self._add_parsed_content(sections, current_section, current_content)
        
        return sections
    
    def _extract_section_content(self, heading) -> str:
        """Extract content between this heading and next heading."""
        content = []
        current = heading.next_sibling
        
        while current and current.name not in ['h1', 'h2', 'h3']:
            if current.name:
                content.append(current.get_text())
            current = current.next_sibling
        
        return ' '.join(content)
    
    def _parse_plain_text(self, content: str) -> Dict[str, any]:
        """Parse plain text content."""
        sections = {
            'introduction': '',
            'definition': '',
            'history': '',
            'branches': [],
            'applications': [],
            'conclusion': ''
        }
        
        # Split by double newlines, but also handle single newlines
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Check if this line is a section header
            if line_lower.startswith('introduction') or line_lower.startswith('intro'):
                if current_section:
                    self._add_parsed_content(sections, current_section, current_content)
                current_section = 'introduction'
                current_content = [line]
            elif line_lower.startswith('definition') or 'what is' in line_lower:
                if current_section:
                    self._add_parsed_content(sections, current_section, current_content)
                current_section = 'definition'
                current_content = [line]
            elif line_lower.startswith('history'):
                if current_section:
                    self._add_parsed_content(sections, current_section, current_content)
                current_section = 'history'
                current_content = [line]
            elif line_lower.startswith('branch') or line_lower.startswith('type'):
                if current_section:
                    self._add_parsed_content(sections, current_section, current_content)
                current_section = 'branches'
                current_content = [line]
            elif line_lower.startswith('application') or 'use' in line_lower:
                if current_section:
                    self._add_parsed_content(sections, current_section, current_content)
                current_section = 'applications'
                current_content = [line]
            elif line_lower.startswith('conclusion') or line_lower.startswith('summary'):
                if current_section:
                    self._add_parsed_content(sections, current_section, current_content)
                current_section = 'conclusion'
                current_content = [line]
            else:
                # Content line
                if current_section:
                    current_content.append(line)
                else:
                    # No section yet, add to introduction by default
                    sections['introduction'] += ' ' + line
        
        # Don't forget to add the last section
        if current_section:
            self._add_parsed_content(sections, current_section, current_content)
        
        return sections
    
    def _add_parsed_content(self, sections: Dict, section_type: str, content_lines: list):
        """Add parsed content to the appropriate section."""
        if not content_lines:
            return
            
        content = ' '.join(content_lines).strip()
        
        if section_type in ['introduction', 'definition', 'history', 'conclusion']:
            sections[section_type] = content
        elif section_type in ['branches', 'applications']:
            sections[section_type].append({'content': content})
