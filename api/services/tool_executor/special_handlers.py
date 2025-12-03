"""
Special Handlers
Custom execution logic for tools that cannot be handled generically
"""
from typing import Dict, Any, Optional
from utils.logger import log as logger


class SpecialHandlers:
    """
    Collection of special handlers for tools with unique requirements.
    Most tools should use the universal executor, but some need custom logic.
    """
    
    @staticmethod
    def get_handler(tool_name: str):
        """
        Get a special handler for a tool if one exists.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Handler function or None
        """
        handlers = {
            'hashcat': SpecialHandlers.handle_hashcat,
            'john': SpecialHandlers.handle_john,
            'sqlmap': SpecialHandlers.handle_sqlmap,
        }
        
        handler = handlers.get(tool_name.lower())
        if handler:
            logger.info(f"Using special handler for {tool_name}")
        return handler
    
    @staticmethod
    def handle_hashcat(params: Dict[str, Any], executor_func) -> Dict[str, Any]:
        """
        Special handler for hashcat with hash type detection.
        
        This is a placeholder - the universal executor should handle most cases,
        but this can be extended for very specific hashcat workflows.
        """
        # For now, delegate to universal executor
        # Can be enhanced later if needed
        return None
    
    @staticmethod
    def handle_john(params: Dict[str, Any], executor_func) -> Dict[str, Any]:
        """
        Special handler for John the Ripper.
        
        Placeholder for future custom logic.
        """
        return None
    
    @staticmethod
    def handle_sqlmap(params: Dict[str, Any], executor_func) -> Dict[str, Any]:
        """
        Special handler for SQLMap with session management.
        
        Placeholder for future custom logic.
        """
        return None

