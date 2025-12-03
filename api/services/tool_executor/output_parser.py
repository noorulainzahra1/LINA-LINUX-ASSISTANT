"""
Output Parser
Structured result extraction from tool output (XML, JSON, text parsing)
"""
import json
import xml.etree.ElementTree as ET
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from utils.logger import log as logger


class OutputParser:
    """
    Parses tool output into structured data.
    Handles various output formats: plain text, JSON, XML, CSV.
    """
    
    def __init__(self):
        """Initialize output parser"""
        pass
    
    def parse_output(
        self,
        output: str,
        output_format: str = 'text',
        parsing_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse tool output into structured format.
        
        Args:
            output: Raw output text
            output_format: Format type ('text', 'json', 'xml', 'csv')
            parsing_config: Optional parsing configuration from registry
            
        Returns:
            Structured output dictionary
        """
        if parsing_config:
            return self._parse_with_config(output, parsing_config)
        
        if output_format == 'json':
            return self._parse_json(output)
        elif output_format == 'xml':
            return self._parse_xml(output)
        elif output_format == 'csv':
            return self._parse_csv(output)
        else:
            return self._parse_text(output)
    
    def _parse_with_config(
        self,
        output: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse output using registry-defined configuration."""
        parsed = {
            'raw': output,
            'format': config.get('type', 'text'),
            'structured': {}
        }
        
        # Check for success pattern
        success_pattern = config.get('success_pattern')
        if success_pattern:
            match = re.search(success_pattern, output, re.IGNORECASE)
            parsed['success'] = match is not None
        
        # Extract results using pattern
        result_extraction = config.get('result_extraction')
        if result_extraction:
            extracted = self._extract_results(output, result_extraction)
            parsed['structured']['results'] = extracted
        
        # Extract specific fields
        fields = config.get('fields', [])
        for field in fields:
            pattern = field.get('pattern')
            name = field.get('name')
            if pattern and name:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    parsed['structured'][name] = match.group(1) if match.groups() else match.group(0)
        
        return parsed
    
    def _parse_json(self, output: str) -> Dict[str, Any]:
        """Parse JSON output."""
        try:
            data = json.loads(output)
            return {
                'format': 'json',
                'raw': output,
                'structured': data,
                'success': True
            }
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON output: {e}")
            return {
                'format': 'json',
                'raw': output,
                'structured': {},
                'success': False,
                'error': str(e)
            }
    
    def _parse_xml(self, output: str) -> Dict[str, Any]:
        """Parse XML output."""
        try:
            root = ET.fromstring(output)
            data = self._xml_to_dict(root)
            return {
                'format': 'xml',
                'raw': output,
                'structured': data,
                'success': True
            }
        except ET.ParseError as e:
            logger.warning(f"Failed to parse XML output: {e}")
            return {
                'format': 'xml',
                'raw': output,
                'structured': {},
                'success': False,
                'error': str(e)
            }
    
    def _parse_csv(self, output: str) -> Dict[str, Any]:
        """Parse CSV output."""
        lines = output.strip().split('\n')
        if not lines:
            return {'format': 'csv', 'raw': output, 'structured': {'rows': []}}
        
        # Parse header
        header = lines[0].split(',')
        rows = []
        
        for line in lines[1:]:
            if line.strip():
                values = line.split(',')
                row = dict(zip(header, values))
                rows.append(row)
        
        return {
            'format': 'csv',
            'raw': output,
            'structured': {'rows': rows},
            'success': True
        }
    
    def _parse_text(self, output: str) -> Dict[str, Any]:
        """Parse plain text output."""
        return {
            'format': 'text',
            'raw': output,
            'structured': {'lines': output.split('\n')},
            'success': True
        }
    
    def _extract_results(
        self,
        output: str,
        extraction_config: str
    ) -> List[Dict[str, Any]]:
        """
        Extract specific results from output.
        
        Args:
            output: Output text
            extraction_config: Extraction pattern (e.g., "password:hash")
            
        Returns:
            List of extracted result dictionaries
        """
        results = []
        
        # Parse extraction config format: "key1:key2" means extract pattern that captures both
        if ':' in extraction_config:
            keys = extraction_config.split(':')
            # Try to find patterns that match both keys
            # This is a simple implementation - can be enhanced
            pattern = r'(\S+)\s*[:=]\s*(\S+)'
            matches = re.finditer(pattern, output)
            for match in matches:
                if len(keys) == 2 and len(match.groups()) >= 2:
                    results.append({
                        keys[0]: match.group(1),
                        keys[1]: match.group(2)
                    })
        
        return results
    
    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}
        
        # Attributes
        if element.attrib:
            result['attributes'] = element.attrib
        
        # Text content
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        # Children
        children = {}
        for child in element:
            child_dict = self._xml_to_dict(child)
            tag = child.tag
            if tag in children:
                # Multiple children with same tag - make it a list
                if not isinstance(children[tag], list):
                    children[tag] = [children[tag]]
                children[tag].append(child_dict)
            else:
                children[tag] = child_dict
        
        if children:
            result.update(children)
        
        return result if result else element.text or ''

