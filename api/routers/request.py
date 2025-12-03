"""
Request processing endpoints
Handle natural language user requests
"""
from fastapi import APIRouter, HTTPException, status

from api.models import ProcessRequest, ProcessResponse, RiskAssessment, ErrorResponse
from api.services.session_service import SessionService
from utils.logger import log as logger

router = APIRouter(prefix="/api/request", tags=["request"])

# Create service instance
session_service = SessionService()


@router.post("/process", response_model=ProcessResponse)
async def process_request(request: ProcessRequest) -> ProcessResponse:
    """
    Process a natural language user request
    
    - **user_input**: Natural language request from the user
    - **session_id**: Session ID to process request within
    
    Returns response based on request type:
    - command: Command to execute
    - conversation: General chat response
    - explanation: Tool or concept explanation
    - autonomous_plan: Multi-step plan
    - tools_list: List of tools
    - error: Error response
    """
    # Get session
    session_data = session_service.get_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Update activity
    session_service.update_activity(request.session_id)
    
    try:
        # Process request through Brain, passing mode for context
        # Use lazy-loaded brain (initializes on first use if needed)
        brain = session_data.get_brain()
        result = brain.process_request(request.user_input, mode=session_data.mode)
        
        # Add command to history if it's a command or tool_request
        command_type = result.get('type')
        if (command_type == 'command' or command_type == 'tool_request') and result.get('command'):
            session_data.interface_state.add_command(result['command'])
            if result.get('tool_name'):
                session_data.interface_state.add_tool_used(result['tool_name'])
        logger.info(f"Processed request. Type: {command_type}, Has command: {bool(result.get('command'))}")
        
        # Convert risk dict to RiskAssessment model if present
        risk = None
        if result.get('risk'):
            risk_dict = result['risk']
            # Handle database_match - it can be a string or bool
            database_match = risk_dict.get('database_match')
            if isinstance(database_match, str):
                # If it's a string, convert to bool (True if not empty/None) or use as pattern_matched
                pattern_matched = database_match if database_match else None
                database_match_bool = bool(database_match) if database_match else None
            else:
                database_match_bool = database_match if isinstance(database_match, bool) else None
                pattern_matched = risk_dict.get('pattern_matched')
            
            risk = RiskAssessment(
                level=risk_dict.get('level', 'UNKNOWN'),
                confidence=risk_dict.get('confidence'),
                reason=risk_dict.get('reason') or risk_dict.get('explanation'),
                database_match=database_match_bool,  # Use boolean version
                pattern_matched=pattern_matched or (database_match if isinstance(database_match, str) else None),
                ai_analysis=risk_dict.get('ai_analysis'),
                explanation=risk_dict.get('explanation') or risk_dict.get('reason')
            )
        
        # Build response
        response = ProcessResponse(
            type=result.get('type', 'error'),
            message=result.get('message'),
            command=result.get('command'),
            tool_name=result.get('tool_name'),
            explanation=result.get('explanation'),
            risk=risk,
            plan=result.get('plan'),
            tools=result.get('tools'),
            error=result.get('message') if result.get('type') == 'error' else None,
            suggestions=result.get('suggestions')  # Multiple command options for suggester mode
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to process request: {e}", exc_info=True)
        return ProcessResponse(
            type="error",
            error=f"Failed to process request: {str(e)}"
        )

