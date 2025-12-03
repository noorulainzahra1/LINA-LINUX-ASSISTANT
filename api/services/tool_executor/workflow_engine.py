"""
Workflow Engine
Generic multi-step workflow processor for tools that require sequential operations
"""
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Tuple
from utils.logger import log as logger


class WorkflowEngine:
    """
    Processes multi-step workflows defined in tool registry execution_metadata.
    Handles sequential, conditional, and loop-based workflows.
    """
    
    def __init__(self, parameter_builder, command_executor, file_manager):
        """
        Initialize workflow engine.
        
        Args:
            parameter_builder: ParameterBuilder instance for command construction
            command_executor: Function to execute commands
            file_manager: FileManager instance for file operations
        """
        self.parameter_builder = parameter_builder
        self.command_executor = command_executor
        self.file_manager = file_manager
        self.step_results: Dict[str, Any] = {}
    
    def execute_workflow(
        self,
        workflow: List[Dict[str, Any]],
        base_command: str,
        user_params: Dict[str, Any],
        registry_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Execute a multi-step workflow.
        
        Args:
            workflow: List of workflow step definitions
            base_command: Base command name
            user_params: User-provided parameters
            registry_data: Full registry data
            
        Returns:
            Tuple of (success, results_dict, errors_list)
        """
        self.step_results = {}
        errors = []
        
        logger.info(f"Executing workflow with {len(workflow)} steps")
        
        for i, step in enumerate(workflow):
            step_name = step.get('step', f'step_{i}')
            logger.info(f"Executing workflow step: {step_name}")
            
            try:
                # Check if step should run (conditional steps)
                if not self._should_run_step(step, user_params):
                    logger.info(f"Skipping step {step_name} (condition not met)")
                    continue
                
                # Execute the step
                success, result = self._execute_step(
                    step,
                    base_command,
                    user_params,
                    registry_data
                )
                
                self.step_results[step_name] = {
                    'success': success,
                    'result': result,
                    'output': result.get('output', '') if isinstance(result, dict) else str(result)
                }
                
                # Check if step is required and failed
                if not success and not step.get('optional', False):
                    errors.append(f"Workflow step '{step_name}' failed")
                    logger.error(f"Required step {step_name} failed, stopping workflow")
                    break
                
                # Update user_params with step results (for dependent steps)
                if success and isinstance(result, dict):
                    user_params.update(result.get('params', {}))
                
            except Exception as e:
                error_msg = f"Error in workflow step '{step_name}': {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg, exc_info=True)
                
                if not step.get('optional', False):
                    break
        
        overall_success = len(errors) == 0
        
        return overall_success, self.step_results, errors
    
    def _should_run_step(
        self,
        step: Dict[str, Any],
        user_params: Dict[str, Any]
    ) -> bool:
        """
        Determine if a step should run based on conditions.
        
        Checks:
        - 'runs_after': Step only runs if previous step succeeded
        - 'requires': Step only runs if required parameters are present
        - 'condition': Custom condition function
        """
        # Check 'runs_after' condition
        runs_after = step.get('runs_after')
        if runs_after:
            if runs_after not in self.step_results:
                return False
            if not self.step_results[runs_after].get('success', False):
                return False
        
        # Check 'requires' condition
        requires = step.get('requires', [])
        if requires:
            for param in requires:
                if param not in user_params:
                    return False
        
        # Check 'condition' (custom function or expression)
        condition = step.get('condition')
        if condition:
            # Simple evaluation for now (can be extended)
            if isinstance(condition, bool):
                return condition
            if isinstance(condition, str):
                # Evaluate as Python expression (be careful with security)
                try:
                    # Replace params with values
                    for key, value in user_params.items():
                        condition = condition.replace(f'{{{key}}}', str(value))
                    return bool(eval(condition))  # Simple eval for boolean expressions
                except:
                    return False
        
        return True
    
    def _execute_step(
        self,
        step: Dict[str, Any],
        base_command: str,
        user_params: Dict[str, Any],
        registry_data: Dict[str, Any]
    ) -> Tuple[bool, Any]:
        """
        Execute a single workflow step.
        
        Returns:
            Tuple of (success, result)
        """
        step_type = step.get('type', 'command')
        command_template = step.get('command_template', '')
        
        if step_type == 'validate':
            return self._execute_validation_step(step, user_params)
        
        elif step_type == 'command' or command_template:
            return self._execute_command_step(
                step,
                base_command,
                user_params,
                registry_data
            )
        
        elif step_type == 'file_operation':
            return self._execute_file_step(step, user_params)
        
        else:
            logger.warning(f"Unknown step type: {step_type}, treating as command")
            return self._execute_command_step(
                step,
                base_command,
                user_params,
                registry_data
            )
    
    def _execute_validation_step(
        self,
        step: Dict[str, Any],
        user_params: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Execute a validation step."""
        validation_type = step.get('validation_type', 'file_exists')
        
        if validation_type == 'file_exists':
            file_param = step.get('file_param', 'file')
            # Handle both single param name or list of possible names
            if isinstance(file_param, list):
                file_path = None
                for param_name in file_param:
                    file_path = user_params.get(param_name)
                    if file_path:
                        break
            else:
                file_path = user_params.get(file_param)
            
            # Also check positional parameters (first positional is usually the file)
            if not file_path:
                # Try to find any positional argument that looks like a file path
                for key, value in user_params.items():
                    if value and isinstance(value, str) and ('/' in value or value.endswith('.txt') or value.endswith('.hash')):
                        # Check if it's actually a file
                        test_path = Path(value)
                        if test_path.exists() and test_path.is_file():
                            file_path = value
                            break
            
            if not file_path:
                param_names = file_param if isinstance(file_param, list) else [file_param]
                return False, {'error': f'File parameter not provided. Tried: {", ".join(param_names)}'}
            
            # Resolve relative paths (handle both absolute and relative)
            if Path(file_path).is_absolute():
                resolved_path = Path(file_path)
            else:
                resolved_path = self.file_manager.resolve_file_path(str(file_path))
            
            is_valid, error = self.file_manager.validate_file(str(resolved_path))
            
            # Update user_params with resolved path for use in command template
            if is_valid:
                if isinstance(file_param, list):
                    for param_name in file_param:
                        if param_name in user_params or user_params.get(param_name):
                            user_params[param_name] = str(resolved_path)
                            break
                    # Also set hash_file as fallback
                    user_params['hash_file'] = str(resolved_path)
                else:
                    user_params[file_param] = str(resolved_path)
            
            return is_valid, {'valid': is_valid, 'error': error, 'resolved_path': str(resolved_path)}
        
        # Add more validation types as needed
        return True, {'valid': True}
    
    def _execute_command_step(
        self,
        step: Dict[str, Any],
        base_command: str,
        user_params: Dict[str, Any],
        registry_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Execute a command step."""
        command_template = step.get('command_template', '')
        
        if not command_template:
            return False, {'error': 'No command_template provided for step'}
        
        # Build command from template
        command = self.parameter_builder.build_command_from_template(
            command_template,
            user_params,
            base_command
        )
        
        logger.info(f"Executing workflow command: {command}")
        
        # Execute command
        try:
            result = self.command_executor(command)
            
            # Handle both dict and string results
            if isinstance(result, dict):
                output = result.get('output', '')
                success = result.get('success', True)
            else:
                output = str(result)
                success = True  # Assume success if executor returns string
            
            # Extract additional data from output if specified
            extract_pattern = step.get('extract_pattern')
            extracted_data = {}
            if extract_pattern and output:
                match = re.search(extract_pattern, output)
                if match:
                    extracted_data = match.groupdict()
            
            return success, {
                'output': output,
                'command': command,
                'extracted': extracted_data
            }
        except Exception as e:
            logger.error(f"Command execution failed: {e}", exc_info=True)
            return False, {'error': str(e), 'command': command}
    
    def _execute_file_step(
        self,
        step: Dict[str, Any],
        user_params: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Execute a file operation step."""
        operation = step.get('operation', 'copy')
        
        if operation == 'copy':
            source = step.get('source')
            destination = step.get('destination')
            # Implement file copy
            return True, {'operation': 'copy'}
        
        # Add more file operations as needed
        return True, {'operation': operation}

