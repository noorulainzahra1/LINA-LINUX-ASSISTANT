"""
Parameter Builder
Constructs command-line commands from registry parameters and user input
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from utils.logger import log as logger


class ParameterBuilder:
    """
    Builds command strings from tool registry parameters and user-provided values.
    Handles flags, positional arguments, and parameter validation.
    """
    
    def __init__(self):
        """Initialize parameter builder"""
        pass
    
    def build_command(
        self,
        base_command: str,
        parameters: List[Dict[str, Any]],
        user_params: Dict[str, Any],
        registry_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[str]]:
        """
        Build a command string from registry parameters and user input.
        
        Args:
            base_command: The base command (e.g., "nmap", "hashcat")
            parameters: List of parameter definitions from registry
            user_params: User-provided parameter values
            registry_data: Full registry data (for metadata access)
            
        Returns:
            Tuple of (command_string, validation_errors)
        """
        command_parts = [base_command]
        errors = []
        
        # Track positional arguments (they go at the end)
        positional_args = []
        
        # Track which parameters we've used
        used_params = set()
        
        # Process each parameter definition
        for param in parameters:
            flag = param.get('flag')
            requires_value = param.get('requires_value', False)
            is_positional = param.get('is_positional', False)
            is_bundle = param.get('is_bundle', False)
            
            # Find matching user parameter
            param_key = self._find_param_key(param, user_params)
            
            if param_key is None:
                # Parameter not provided by user
                # Only flag positional parameters as errors - flags are optional
                if is_positional and requires_value:
                    flag_name = param.get('description', 'positional argument').split('.')[0]
                    errors.append(f"Required parameter '{flag_name}' is missing")
                # Don't error on missing flags - they're optional
                continue
            
            used_params.add(param_key)
            value = user_params[param_key]
            
            # Handle positional arguments
            if is_positional:
                if value:
                    positional_args.append(str(value))
                elif requires_value:
                    errors.append(f"Positional argument requires a value")
                continue
            
            # Handle bundle flags (multiple flags together)
            if is_bundle:
                # Split bundle flag like "--risk=3 --level=5"
                if flag:
                    command_parts.append(flag)
                continue
            
            # Handle regular flags
            if flag:
                if requires_value:
                    # Flag with value: -o output.txt
                    if value and value != '':
                        # Handle flags that need special formatting
                        if '=' in flag and flag.endswith('='):
                            command_parts.append(f"{flag}{value}")
                        else:
                            command_parts.extend([flag, str(value)])
                    # Don't add flag if value is empty - it's optional
                else:
                    # Boolean flag: -v, --verbose, -sV, -sC, -A
                    if value or value is True:  # If explicitly set or True
                        command_parts.append(flag)
            else:
                # No flag, just a value - treat as positional
                if value:
                    positional_args.append(str(value))
        
        # Add positional arguments at the end
        command_parts.extend(positional_args)
        
        # Check for unused user parameters (might be typos)
        unused = set(user_params.keys()) - used_params
        if unused:
            logger.warning(f"Unused parameters provided: {unused}")
        
        command = ' '.join(command_parts)
        return command, errors
    
    def _find_param_key(self, param: Dict[str, Any], user_params: Dict[str, Any]) -> Optional[str]:
        """
        Find the key in user_params that matches this parameter definition.
        
        Tries multiple strategies:
        1. Direct match by flag name (without dashes)
        2. Match by keywords
        3. Match by description keywords
        """
        flag = param.get('flag')
        keywords = param.get('keywords', [])
        
        # Strategy 1: Direct flag match
        if flag:
            # Try exact flag match
            flag_clean = flag.lstrip('-').replace('-', '_')
            if flag_clean in user_params:
                return flag_clean
            if flag in user_params:
                return flag
            
            # Try with underscores
            flag_underscore = flag.replace('-', '_')
            if flag_underscore in user_params:
                return flag_underscore
        
        # Strategy 2: Keyword match
        for keyword in keywords:
            keyword_clean = keyword.lower().replace(' ', '_')
            if keyword_clean in user_params:
                return keyword_clean
            if keyword in user_params:
                return keyword
        
        # Strategy 3: Positional parameter (no flag) or common positional args
        if param.get('is_positional') or not flag:
            # Try common positional names
            for key in ['target', 'file', 'input', 'url', 'host', 'domain']:
                if key in user_params:
                    return key
        
        return None
    
    def build_command_from_template(
        self,
        template: str,
        params: Dict[str, Any],
        base_command: Optional[str] = None
    ) -> str:
        """
        Build command from a template string with placeholders.
        
        Args:
            template: Command template with {placeholders}
            params: Values to substitute
            base_command: Base command to use for {base_command} placeholder
            
        Returns:
            Resolved command string
        """
        if base_command:
            params['base_command'] = base_command
        
        # Replace placeholders
        command = template
        for key, value in params.items():
            placeholder = f"{{{key}}}"
            if placeholder in command:
                command = command.replace(placeholder, str(value))
        
        # Remove any unreplaced placeholders (optional params)
        command = re.sub(r'\{[^}]+\}', '', command)
        command = ' '.join(command.split())  # Clean up extra spaces
        
        return command
    
    def validate_required_params(
        self,
        parameters: List[Dict[str, Any]],
        user_params: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all required parameters are provided.
        
        Only positional parameters (without flags) are truly required.
        Flag parameters are optional - they only need values IF provided.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        for param in parameters:
            # Only validate positional parameters (no flag) as truly required
            is_positional = param.get('is_positional', False)
            flag = param.get('flag')
            requires_value = param.get('requires_value', False)
            
            # Positional parameters without flags are required
            if is_positional and not flag:
                param_key = self._find_param_key(param, user_params)
                if param_key is None or not user_params.get(param_key):
                    param_name = param.get('description', 'positional argument').split('.')[0]
                    errors.append(f"Required parameter '{param_name}' is missing")
            
            # If a flag parameter is provided but requires a value, check it has one
            if flag and requires_value:
                param_key = self._find_param_key(param, user_params)
                if param_key is not None:
                    # User is trying to use this flag, ensure it has a value
                    value = user_params.get(param_key)
                    if value is None or value == '':
                        errors.append(f"Flag '{flag}' requires a value")
        
        return len(errors) == 0, errors

