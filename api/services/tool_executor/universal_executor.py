"""
Universal Tool Executor
Main executor that reads ANY registry JSON and executes tools properly
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Callable
from utils.logger import log as logger

from .parameter_builder import ParameterBuilder
from .workflow_engine import WorkflowEngine
from .progress_monitor import ProgressMonitor
from .file_manager import FileManager
from .output_parser import OutputParser
from .hash_type_mapper import HashTypeMapper


class UniversalToolExecutor:
    """
    Universal tool executor that handles ALL tools by reading their registry files.
    Automatically detects execution patterns and routes to appropriate handlers.
    """
    
    def __init__(
        self,
        registries_path: str,
        command_executor_func: Callable[[str], Dict[str, Any]]
    ):
        """
        Initialize universal executor.
        
        Args:
            registries_path: Path to tool registries directory
            command_executor_func: Function to execute commands (takes command string, returns result dict)
        """
        self.registries_path = Path(registries_path)
        self.command_executor = command_executor_func
        
        # Initialize components
        self.parameter_builder = ParameterBuilder()
        self.file_manager = FileManager()
        self.progress_monitor = ProgressMonitor()
        self.output_parser = OutputParser()
        
        # Create workflow engine with dependencies
        self.workflow_engine = WorkflowEngine(
            self.parameter_builder,
            command_executor_func,
            self.file_manager
        )
        
        logger.info(f"UniversalToolExecutor initialized with registries: {registries_path}")
    
    def execute_tool(
        self,
        tool_name: str,
        user_params: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool using its registry definition.
        
        Args:
            tool_name: Name of the tool to execute
            user_params: User-provided parameters (flags, values, files)
            session_id: Optional session ID for tracking
            
        Returns:
            Execution result dictionary with:
            - success: bool
            - command: str (actual command executed)
            - output: str (raw output)
            - parsed_output: dict (structured output)
            - progress: dict (progress information)
            - errors: list (any errors encountered)
        """
        logger.info(f"Executing tool: {tool_name} with params: {user_params}")
        
        try:
            # Load tool registry
            registry_data = self._load_registry(tool_name)
            if not registry_data:
                return {
                    'success': False,
                    'errors': [f"Tool registry not found: {tool_name}"],
                    'output': ''
                }
            
            # Get base command
            base_command = registry_data.get('base_command', tool_name)
            
            # Map hash types for hashcat/john if needed
            if tool_name.lower() in ['hashcat', 'john']:
                user_params = self._map_hash_types(tool_name, user_params)
            
            # Check for execution metadata (multi-step workflow)
            execution_metadata = registry_data.get('execution_metadata')
            
            if execution_metadata and execution_metadata.get('workflow_type') == 'multi-step':
                # Multi-step workflow execution
                return self._execute_multi_step_workflow(
                    tool_name,
                    base_command,
                    registry_data,
                    user_params,
                    execution_metadata
                )
            else:
                # Simple single command execution
                return self._execute_simple_command(
                    tool_name,
                    base_command,
                    registry_data,
                    user_params
                )
        
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return {
                'success': False,
                'errors': [str(e)],
                'output': ''
            }
    
    def _load_registry(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Load tool registry JSON file.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Registry dictionary or None if not found
        """
        # Try different possible registry file names
        possible_names = [
            f"{tool_name}_registry.json",
            f"{tool_name}.json",
            f"{tool_name}_registry.json"
        ]
        
        for name in possible_names:
            registry_file = self.registries_path / name
            if registry_file.exists():
                try:
                    with open(registry_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        logger.info(f"Loaded registry: {registry_file}")
                        return data
                except Exception as e:
                    logger.error(f"Failed to load registry {registry_file}: {e}")
        
        logger.warning(f"Registry not found for tool: {tool_name}")
        return None
    
    def _map_hash_types(self, tool_name: str, user_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map hash type names to tool-specific format/mode numbers.
        
        Args:
            tool_name: Name of the tool (hashcat or john)
            user_params: User-provided parameters
            
        Returns:
            Updated user_params with mapped hash types
        """
        params = user_params.copy()
        
        # Find hash_type parameter (could be named hash_type, format, mode, etc.)
        hash_type_keys = ['hash_type', 'format', 'mode', 'hash_type_param', 'm']
        hash_type = None
        hash_key = None
        
        for key in hash_type_keys:
            if key in params:
                hash_type = params.get(key)
                hash_key = key
                break
        
        if hash_type:
            if tool_name.lower() == 'hashcat':
                mode = HashTypeMapper.get_hashcat_mode(str(hash_type))
                if mode is not None:
                    params[hash_key] = str(mode)
                    logger.info(f"Mapped hash type '{hash_type}' to hashcat mode {mode}")
                else:
                    logger.warning(f"Could not map hash type '{hash_type}' for hashcat")
            elif tool_name.lower() == 'john':
                format_str = HashTypeMapper.get_john_format(str(hash_type))
                if format_str:
                    params[hash_key] = format_str
                    logger.info(f"Mapped hash type '{hash_type}' to john format '{format_str}'")
                else:
                    logger.warning(f"Could not map hash type '{hash_type}' for john")
        
        return params
    
    def _execute_simple_command(
        self,
        tool_name: str,
        base_command: str,
        registry_data: Dict[str, Any],
        user_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a simple single-command tool."""
        logger.info(f"Executing simple command for {tool_name}")
        
        # Get parameters from registry
        parameters = registry_data.get('parameters', [])
        
        # Validate required parameters
        is_valid, validation_errors = self.parameter_builder.validate_required_params(
            parameters,
            user_params
        )
        
        if not is_valid:
            return {
                'success': False,
                'errors': validation_errors,
                'output': ''
            }
        
        # Build command
        command, build_errors = self.parameter_builder.build_command(
            base_command,
            parameters,
            user_params,
            registry_data
        )
        
        if build_errors:
            return {
                'success': False,
                'errors': build_errors,
                'output': '',
                'command': command
            }
        
        logger.info(f"Built command: {command}")
        
        # Execute command
        execution_result = self.command_executor(command)
        
        # Parse output
        output = execution_result.get('output', '')
        output_format = registry_data.get('output_format', 'text')
        parsing_config = None
        
        if execution_metadata := registry_data.get('execution_metadata'):
            parsing_config = execution_metadata.get('output_parsing')
        
        parsed_output = self.output_parser.parse_output(
            output,
            output_format,
            parsing_config
        )
        
        # Extract progress if available
        progress = None
        if execution_metadata:
            progress_patterns = execution_metadata.get('progress_patterns', [])
            if progress_patterns:
                self.progress_monitor.compile_patterns(progress_patterns)
                progress = self.progress_monitor.update_from_output(output)
        
        return {
            'success': execution_result.get('success', True),
            'command': command,
            'output': output,
            'parsed_output': parsed_output,
            'progress': progress,
            'errors': execution_result.get('errors', []),
            'return_code': execution_result.get('return_code', 0)
        }
    
    def _execute_multi_step_workflow(
        self,
        tool_name: str,
        base_command: str,
        registry_data: Dict[str, Any],
        user_params: Dict[str, Any],
        execution_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a multi-step workflow tool."""
        logger.info(f"Executing multi-step workflow for {tool_name}")
        
        # Get workflow definition
        workflow = execution_metadata.get('workflow', [])
        
        if not workflow:
            return {
                'success': False,
                'errors': ['No workflow steps defined in execution_metadata'],
                'output': ''
            }
        
        # Setup progress monitoring if configured
        progress_patterns = execution_metadata.get('progress_patterns', [])
        if progress_patterns:
            self.progress_monitor.compile_patterns(progress_patterns)
        
        # Execute workflow
        success, workflow_results, errors = self.workflow_engine.execute_workflow(
            workflow,
            base_command,
            user_params,
            registry_data
        )
        
        # Collect all output
        all_output = []
        for step_name, step_result in workflow_results.items():
            step_output = step_result.get('output', '')
            if step_output:
                all_output.append(f"[{step_name}]\n{step_output}")
        
        combined_output = '\n\n'.join(all_output)
        
        # Parse final output
        output_parsing = execution_metadata.get('output_parsing', {})
        parsed_output = self.output_parser.parse_output(
            combined_output,
            output_parsing.get('type', 'text'),
            output_parsing
        )
        
        # Get final progress
        progress = None
        if progress_patterns:
            progress = self.progress_monitor.update_from_output(combined_output)
            if success:
                progress['status'] = 'completed'
                progress['percentage'] = 100
        
        return {
            'success': success,
            'command': f"Multi-step workflow: {tool_name}",
            'output': combined_output,
            'parsed_output': parsed_output,
            'workflow_results': workflow_results,
            'progress': progress,
            'errors': errors,
            'return_code': 0 if success else 1
        }
    
    def detect_execution_pattern(self, registry_data: Dict[str, Any]) -> str:
        """
        Detect the execution pattern for a tool.
        
        Returns:
            'simple', 'multi-step', or 'interactive'
        """
        execution_metadata = registry_data.get('execution_metadata', {})
        workflow_type = execution_metadata.get('workflow_type')
        
        if workflow_type == 'multi-step' or execution_metadata.get('workflow'):
            return 'multi-step'
        
        # Check for interactive indicators
        parameters = registry_data.get('parameters', [])
        for param in parameters:
            if param.get('flag') == '--batch' and param.get('requires_value') == False:
                # Tool has batch flag, might be interactive
                return 'interactive'
        
        return 'simple'

