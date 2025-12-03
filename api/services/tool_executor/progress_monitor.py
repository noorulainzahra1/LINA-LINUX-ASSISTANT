"""
Progress Monitor
Real-time output parsing and progress extraction from tool execution
"""
import re
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from utils.logger import log as logger


class ProgressMonitor:
    """
    Monitors tool execution output in real-time and extracts progress information.
    Uses regex patterns to identify progress indicators from tool output.
    """
    
    def __init__(self):
        """Initialize progress monitor"""
        self.progress_patterns: List[re.Pattern] = []
        self.current_progress: Dict[str, Any] = {
            'percentage': 0,
            'status': 'running',
            'message': '',
            'last_update': datetime.now()
        }
    
    def compile_patterns(self, patterns: List[str]) -> None:
        """
        Compile regex patterns for progress detection.
        
        Args:
            patterns: List of regex pattern strings
        """
        self.progress_patterns = []
        for pattern in patterns:
            try:
                compiled = re.compile(pattern)
                self.progress_patterns.append(compiled)
            except re.error as e:
                logger.warning(f"Invalid progress pattern '{pattern}': {e}")
    
    def extract_progress(self, output: str) -> Optional[Dict[str, Any]]:
        """
        Extract progress information from tool output.
        
        Args:
            output: Tool output text
            
        Returns:
            Progress dictionary with percentage, status, message, or None
        """
        if not output or not self.progress_patterns:
            return None
        
        # Try each pattern
        for pattern in self.progress_patterns:
            match = pattern.search(output)
            if match:
                progress_info = self._parse_progress_match(match, output)
                if progress_info:
                    self.current_progress.update(progress_info)
                    self.current_progress['last_update'] = datetime.now()
                    return self.current_progress
        
        return None
    
    def _parse_progress_match(self, match: re.Match, output: str) -> Optional[Dict[str, Any]]:
        """
        Parse a regex match to extract progress information.
        
        Args:
            match: Regex match object
            output: Full output text
            
        Returns:
            Progress dictionary or None
        """
        try:
            progress_info = {}
            
            # Extract percentage if available
            percentage_match = re.search(r'(\d+)%', match.group(0))
            if percentage_match:
                progress_info['percentage'] = int(percentage_match.group(1))
            
            # Extract status keywords
            status_text = match.group(0).lower()
            if 'complete' in status_text or 'done' in status_text or 'finished' in status_text:
                progress_info['status'] = 'completed'
                if 'percentage' not in progress_info:
                    progress_info['percentage'] = 100
            elif 'error' in status_text or 'failed' in status_text:
                progress_info['status'] = 'error'
            elif 'running' in status_text or 'processing' in status_text:
                progress_info['status'] = 'running'
            else:
                progress_info['status'] = 'running'
            
            # Extract message
            progress_info['message'] = match.group(0).strip()
            
            # Extract numbers for progress calculation
            numbers = re.findall(r'\d+', match.group(0))
            if len(numbers) >= 2:
                # Assume format like "10/100" or "10 of 100"
                try:
                    current = int(numbers[0])
                    total = int(numbers[1])
                    if total > 0:
                        progress_info['percentage'] = min(100, int((current / total) * 100))
                        progress_info['current'] = current
                        progress_info['total'] = total
                except ValueError:
                    pass
            
            return progress_info
            
        except Exception as e:
            logger.warning(f"Error parsing progress match: {e}")
            return None
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information."""
        return self.current_progress.copy()
    
    def reset(self):
        """Reset progress monitor."""
        self.current_progress = {
            'percentage': 0,
            'status': 'running',
            'message': '',
            'last_update': datetime.now()
        }
    
    def update_from_output(self, output: str) -> Dict[str, Any]:
        """
        Update progress from output and return current state.
        
        Args:
            output: Latest tool output
            
        Returns:
            Current progress dictionary
        """
        extracted = self.extract_progress(output)
        if extracted:
            return extracted
        
        # If no pattern matched, return current state
        return self.current_progress

