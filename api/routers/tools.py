"""
Tools management endpoints
"""
import json
import subprocess
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status

from api.models import ToolsListResponse, ToolInfo, ToolExecuteRequest, ToolExecutionResponse
from api.services.lina_service import LINAService
from api.services.session_service import SessionService
from api.services.command_service import CommandService
from api.services.tool_executor import UniversalToolExecutor
from utils.logger import log as logger

router = APIRouter(prefix="/api/tools", tags=["tools"])

# Global service instances
session_service = SessionService()
command_service = CommandService()

# Initialize universal tool executor
_uni_executor = None

def get_universal_executor() -> UniversalToolExecutor:
    """Get or create universal tool executor instance"""
    global _uni_executor
    if _uni_executor is None:
        environment = LINAService.get_environment()
        registries_path = environment['paths']['param_registries']
        
        # Create wrapper function for command execution
        def execute_command_wrapper(command: str) -> Dict[str, Any]:
            """Wrapper to execute command via CommandService"""
            result = command_service.execute_stream(
                command=command,
                execution_mode="background"
            )
            
            # Wait a bit for initial output (for synchronous tools)
            import time
            time.sleep(0.5)
            
            # Get current state
            status_result = command_service.get_execution(result.execution_id)
            if status_result:
                return {
                    'success': status_result.status == 'completed',
                    'output': status_result.output or '',
                    'errors': [status_result.error] if status_result.error else [],
                    'return_code': status_result.return_code or 0
                }
            else:
                return {
                    'success': False,
                    'output': '',
                    'errors': ['Execution result not found'],
                    'return_code': 1
                }
        
        _uni_executor = UniversalToolExecutor(
            registries_path=registries_path,
            command_executor_func=execute_command_wrapper
        )
        logger.info("Universal tool executor initialized")
    
    return _uni_executor


def check_tool_installed(tool_name: str) -> bool:
    """Check if a tool is installed on the system"""
    try:
        result = subprocess.run(
            ['which', tool_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2
        )
        return result.returncode == 0
    except Exception:
        return False


@router.get("/list", response_model=ToolsListResponse)
async def list_tools() -> ToolsListResponse:
    """
    Get list of all available tools
    
    Returns all tools from the registry with installation status
    """
    try:
        environment = LINAService.get_environment()
        tool_registry_path = environment['paths']['tool_registry']
        
        # Load tool registry
        with open(tool_registry_path, 'r', encoding='utf-8') as f:
            tools_data = json.load(f)
        
        # Handle both list and dict formats
        tools_list = []
        if isinstance(tools_data, list):
            tools_list = tools_data
        elif isinstance(tools_data, dict):
            tools_list = list(tools_data.values())
        
        # Convert to ToolInfo models
        tools = []
        categories_set = set()
        
        for tool_data in tools_list:
            tool_name = tool_data.get('name', '')
            category = tool_data.get('category', 'unknown')
            categories_set.add(category)
            
            tool_info = ToolInfo(
                name=tool_name,
                description=tool_data.get('description', ''),
                category=category,
                keywords=tool_data.get('keywords', []),
                risk_level=tool_data.get('risk_level', 'UNKNOWN'),
                installed=check_tool_installed(tool_name)
            )
            tools.append(tool_info)
        
        installed_count = sum(1 for tool in tools if tool.installed)
        
        return ToolsListResponse(
            tools=tools,
            total_count=len(tools),
            installed_count=installed_count,
            categories=sorted(list(categories_set))
        )
        
    except Exception as e:
        logger.error(f"Failed to list tools: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}"
        )


@router.get("/{tool_name}", response_model=ToolInfo)
async def get_tool_info(tool_name: str) -> ToolInfo:
    """Get detailed information about a specific tool"""
    try:
        environment = LINAService.get_environment()
        tool_registry_path = environment['paths']['tool_registry']
        
        # Load tool registry
        with open(tool_registry_path, 'r', encoding='utf-8') as f:
            tools_data = json.load(f)
        
        # Handle both list and dict formats
        tools_list = []
        if isinstance(tools_data, list):
            tools_list = tools_data
        elif isinstance(tools_data, dict):
            tools_list = list(tools_data.values())
        
        # Find the tool
        tool_data = None
        for tool in tools_list:
            if tool.get('name', '').lower() == tool_name.lower():
                tool_data = tool
                break
        
        if not tool_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_name}' not found"
            )
        
        return ToolInfo(
            name=tool_data.get('name', ''),
            description=tool_data.get('description', ''),
            category=tool_data.get('category', 'unknown'),
            keywords=tool_data.get('keywords', []),
            risk_level=tool_data.get('risk_level', 'UNKNOWN'),
            installed=check_tool_installed(tool_data.get('name', ''))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tool info: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tool info: {str(e)}"
        )


@router.post("/{tool_name}/execute", response_model=ToolExecutionResponse)
async def execute_tool(tool_name: str, request: ToolExecuteRequest) -> ToolExecutionResponse:
    """
    Execute a tool with provided parameters.
    
    Uses the universal tool executor to:
    - Load tool registry
    - Build command from parameters
    - Execute tool (simple or multi-step workflow)
    - Parse and return structured results
    
    Note: The tool_name in the path should match request.tool_name
    """
    # Validate session
    session_data = session_service.get_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Use tool_name from path, ensure request has matching name
    exec_tool_name = tool_name.lower()
    if request.tool_name.lower() != exec_tool_name:
        # Update request to use path tool_name
        request.tool_name = exec_tool_name
    
    session_service.update_activity(request.session_id)
    
    try:
        # Get universal executor
        executor = get_universal_executor()
        
        # Execute tool
        result = executor.execute_tool(
            tool_name=exec_tool_name,
            user_params=request.parameters,
            session_id=request.session_id
        )
        
        # Add to session history if command was executed
        if result.get('command'):
            session_data.interface_state.add_command(result['command'])
        
        # Return response
        return ToolExecutionResponse(
            success=result.get('success', False),
            tool_name=exec_tool_name,
            command=result.get('command'),
            output=result.get('output', ''),
            parsed_output=result.get('parsed_output'),
            progress=result.get('progress'),
            workflow_results=result.get('workflow_results'),
            errors=result.get('errors', []),
            return_code=result.get('return_code'),
            execution_id=result.get('execution_id')
        )
        
    except Exception as e:
        logger.error(f"Failed to execute tool {tool_name}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute tool: {str(e)}"
        )

