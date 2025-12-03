"""
Session management endpoints
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from api.models import (
    SessionCreateRequest,
    SessionResponse,
    SessionStatusResponse,
    SessionAnalyticsResponse,
    CommandHistoryEntry,
    ErrorResponse
)
from api.services.session_service import SessionService
from utils.logger import log as logger

router = APIRouter(prefix="/api/session", tags=["session"])

# Use singleton instance - all routers will share the same session store
session_service = SessionService()


@router.post("/create", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: SessionCreateRequest) -> SessionResponse:
    """
    Create a new LINA session with role selection
    
    - **role**: User role (Student, Forensic Expert, Penetration Tester)
    - **ai_engine**: AI engine to use (defaults to Google Gemini)
    """
    try:
        session_id = session_service.create_session(
            role=request.role,
            ai_engine=request.ai_engine or "Cloud AI (Google Gemini)",
            mode=request.mode
        )
        
        session_data = session_service.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created session"
            )
        
        return SessionResponse(
            session_id=session_id,
            role=session_data.role,
            ai_engine=session_data.ai_engine,
            created_at=session_data.created_at,
            status="active"
        )
    except Exception as e:
        logger.error(f"Failed to create session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(session_id: str) -> SessionStatusResponse:
    """Get current status of a session"""
    session_data = session_service.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    session_service.update_activity(session_id)
    
    duration_minutes = session_data.interface_state.get_session_duration()
    duration_str = f"{duration_minutes:.2f} minutes" if isinstance(duration_minutes, (int, float)) else str(duration_minutes)
    
    return SessionStatusResponse(
        session_id=session_id,
        role=session_data.role,
        ai_engine=session_data.ai_engine,
        created_at=session_data.created_at,
        last_activity=session_data.last_activity,
        command_count=session_data.interface_state.session_stats.get("commands_executed", 0),
        tools_used=list(session_data.interface_state.tools_used),
        session_duration=duration_str
    )


@router.get("/{session_id}/history", response_model=list[CommandHistoryEntry])
async def get_command_history(session_id: str) -> list[CommandHistoryEntry]:
    """Get command history for a session"""
    session_data = session_service.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # Convert command history to response model
    # Note: interface_state.command_history is a list of strings
    # We'd need to enhance it to store more metadata for full history
    history = []
    for cmd in session_data.interface_state.command_history[-100:]:  # Last 100 commands
        history.append(CommandHistoryEntry(
            command=cmd,
            timestamp=session_data.last_activity  # Would need to track individual timestamps
        ))
    
    return history


@router.get("/{session_id}/analytics", response_model=SessionAnalyticsResponse)
async def get_session_analytics(session_id: str) -> SessionAnalyticsResponse:
    """Get analytics and statistics for a session"""
    session_data = session_service.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # Try to get analytics from session manager, but don't fail if it's not available
    session_summary = {}
    learning_insights = None
    try:
        # Use lazy-loaded brain (may be None if not initialized yet)
        if session_data.brain is None:
            logger.debug("Brain not initialized yet for analytics - skipping session manager data")
        else:
            session_manager = session_data.brain.get_session_manager()
            session_summary = session_manager.get_session_summary()
            learning_insights = session_manager.get_learning_insights()
    except AttributeError:
        # Session manager might not exist yet for new sessions
        logger.debug("Session manager not available yet for analytics")
    except Exception as e:
        logger.warning(f"Failed to get session analytics: {e}")
    
    duration = (session_data.last_activity - session_data.created_at).total_seconds() / 60.0
    
    return SessionAnalyticsResponse(
        session_id=session_id,
        duration_minutes=duration,
        commands_executed=session_data.interface_state.session_stats.get("commands_executed", 0),
        unique_tools_used=len(session_data.interface_state.tools_used),
        conversations=session_data.interface_state.conversations,
        explanations_requested=session_summary.get("explanations_requested", 0),
        plans_generated=session_summary.get("plans_generated", 0),
        tools_used_list=list(session_data.interface_state.tools_used),
        learning_insights=learning_insights
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str):
    """Delete a session"""
    if not session_service.delete_session(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

