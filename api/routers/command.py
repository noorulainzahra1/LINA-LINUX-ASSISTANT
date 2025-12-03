"""
Command execution endpoints
"""
from fastapi import APIRouter, HTTPException, status

from api.models import CommandExecuteRequest, CommandExecutionResponse, ErrorResponse
from api.services.session_service import SessionService
from api.services.command_service import CommandService
from utils.logger import log as logger

router = APIRouter(prefix="/api/command", tags=["command"])

# Global service instances
session_service = SessionService()
command_service = CommandService()


@router.post("/execute", response_model=CommandExecutionResponse)
async def execute_command(request: CommandExecuteRequest) -> CommandExecutionResponse:
    """
    Execute a command
    
    - **command**: Command to execute
    - **session_id**: Session ID
    - **auto_confirm**: Skip confirmation prompts
    - **execution_mode**: persistent (tmux) or separate (background with output)
    """
    # Get session
    session_data = session_service.get_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    session_service.update_activity(request.session_id)
    
    try:
        # Execute command with streaming
        # Map 'separate' to 'background' for output capture, 'persistent' stays as tmux
        exec_mode = "background" if request.execution_mode == "separate" else request.execution_mode or "background"
        result = command_service.execute_stream(
            command=request.command,
            execution_mode=exec_mode
        )
        
        # Add to session history
        session_data.interface_state.add_command(request.command)
        
        # Return immediately with execution_id - client will poll for results
        return CommandExecutionResponse(
            execution_id=result.execution_id,
            command=result.command,
            status=result.status,  # Will be "running" initially
            output=result.output,  # Will be empty initially, populate as execution progresses
            return_code=result.return_code,
            start_time=result.start_time,
            end_time=result.end_time,
            error=result.error if result.status == "failed" else None
        )
        
    except Exception as e:
        logger.error(f"Failed to execute command: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute command: {str(e)}"
        )


@router.get("/execution/{execution_id}", response_model=CommandExecutionResponse)
async def get_execution_status(execution_id: str) -> CommandExecutionResponse:
    """Get status of a command execution"""
    result = command_service.get_execution(execution_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found"
        )
    
    # Return current state (output may be accumulating in real-time)
    return CommandExecutionResponse(
        execution_id=result.execution_id,
        command=result.command,
        status=result.status,
        output=result.output,  # This will have accumulated output
        return_code=result.return_code,
        start_time=result.start_time,
        end_time=result.end_time,
        error=result.error
    )


@router.post("/execution/{execution_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_execution(execution_id: str):
    """Cancel a running command execution"""
    success = command_service.cancel_execution(execution_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found or not cancellable"
        )
    
    return {"message": f"Execution {execution_id} cancelled"}

