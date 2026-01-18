"""Report generation module for creating structured markdown reports."""

from typing import Dict, Any
from app.logger import logger


class ReportGenerator:
    """Generate structured markdown reports from parsed content."""
    
    def __init__(self, language: str = 'fr'):
        self.language = language
    
    def generate_report(self, topic: str, sections: Dict[str, Any]) -> str:
        """Generate a complete markdown report."""
        report_parts = []
        
        report_parts.append(f"# {topic}\n")
        
        if sections.get('introduction'):
            report_parts.append(f"## 1. Introduction\n")
            report_parts.append(f"{sections['introduction']}\n")
        
        if sections.get('definition'):
            report_parts.append(f"## 2. Definition\n")
            report_parts.append(f"{sections['definition']}\n")
        
        section_num = 3
        
        if sections.get('history'):
            report_parts.append(f"## {section_num}. History\n")
            report_parts.append(f"{sections['history']}\n")
            section_num += 1
        
        if sections.get('branches'):
            report_parts.append(f"## {section_num}. Major Branches\n")
            for i, branch in enumerate(sections['branches'], 1):
                branch_name = branch.get('name', f'Section {i}')
                branch_content = branch.get('content', '')
                report_parts.append(f"### {section_num}.{i} {branch_name}\n")
                report_parts.append(f"{branch_content}\n")
            section_num += 1
        
        if sections.get('applications'):
            report_parts.append(f"## {section_num}. Applications\n")
            for i, app in enumerate(sections['applications'], 1):
                app_name = app.get('name', f'Application {i}')
                app_content = app.get('content', '')
                report_parts.append(f"### {section_num}.{i} {app_name}\n")
                report_parts.append(f"{app_content}\n")
            section_num += 1
        
        if sections.get('conclusion'):
            report_parts.append(f"## {section_num}. Conclusion\n")
            report_parts.append(f"{sections['conclusion']}\n")
        else:
            conclusion = self._generate_default_conclusion(topic)
            report_parts.append(f"## {section_num}. Conclusion\n")
            report_parts.append(f"{conclusion}\n")
        
        return '\n'.join(report_parts)
    
    def _generate_default_conclusion(self, topic: str) -> str:
        """Generate a default conclusion for the report."""
        if self.language == 'fr':
            return f"""
Ce rapport a exploré les concepts clés de {topic}. 
Pour approfondir vos connaissances, nous vous recommandons de consulter les sources primaires 
et d'explorer les applications pratiques de {topic} dans votre domaine d'intérêt.
"""
        else:
            return f"""
This report has explored the key concepts of {topic}. 
To deepen your understanding, we recommend consulting primary sources 
and exploring practical applications of {topic} in your field of interest.
"""
