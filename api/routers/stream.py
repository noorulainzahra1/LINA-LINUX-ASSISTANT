"""
WebSocket streaming endpoint for real-time command output
"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
from typing import Dict, Set

from api.services.session_service import SessionService
from api.services.command_service import CommandService
from utils.logger import log as logger

# Global service instances
session_service = SessionService()
command_service = CommandService()

router = APIRouter(tags=["stream"])

# Store active WebSocket connections per session
_active_connections: Dict[str, Set[WebSocket]] = {}


@router.websocket("/ws/session/{session_id}")
async def websocket_stream(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time command output streaming
    
    Connects to a session and streams command execution output in real-time.
    
    Message format (client -> server):
    {
        "type": "execute",
        "command": "nmap -sV target.com",
        "execution_mode": "background"
    }
    
    Message format (server -> client):
    {
        "type": "output" | "status" | "error" | "complete",
        "data": "...",
        "execution_id": "..."
    }
    """
    # Verify session exists
    session_data = session_service.get_session(session_id)
    if not session_data:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    # Accept connection
    await websocket.accept()
    
    # Add to active connections
    if session_id not in _active_connections:
        _active_connections[session_id] = set()
    _active_connections[session_id].add(websocket)
    
    logger.info(f"WebSocket connected for session {session_id}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get('type')
                
                if message_type == 'execute':
                    # Execute command and stream output
                    command = message.get('command', '')
                    execution_mode = message.get('execution_mode', 'background')
                    
                    if not command:
                        await websocket.send_json({
                            "type": "error",
                            "data": "No command provided"
                        })
                        continue
                    
                    # Update session activity
                    session_service.update_activity(session_id)
                    
                    # Execute command with streaming
                    result = command_service.execute_stream(
                        command=command,
                        execution_mode=execution_mode
                    )
                    
                    # Send execution started
                    await websocket.send_json({
                        "type": "status",
                        "execution_id": result.execution_id,
                        "data": "Command execution started",
                        "status": "running"
                    })
                    
                    # Stream output (simplified - in production would use async generator)
                    # For now, poll the result and send updates
                    import asyncio
                    
                    last_output_length = 0
                    while result.status == "running":
                        await asyncio.sleep(0.1)  # Poll every 100ms
                        
                        # Send new output chunks
                        current_output = result.output
                        if len(current_output) > last_output_length:
                            new_chunk = current_output[last_output_length:]
                            await websocket.send_json({
                                "type": "output",
                                "execution_id": result.execution_id,
                                "data": new_chunk
                            })
                            last_output_length = len(current_output)
                    
                    # Send completion
                    await websocket.send_json({
                        "type": "complete",
                        "execution_id": result.execution_id,
                        "data": result.output,
                        "status": result.status,
                        "return_code": result.return_code,
                        "error": result.error
                    })
                    
                elif message_type == "ping":
                    # Heartbeat
                    await websocket.send_json({
                        "type": "pong",
                        "data": "ok"
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": "Invalid JSON message"
                })
            except Exception as e:
                logger.error(f"WebSocket error: {e}", exc_info=True)
                await websocket.send_json({
                    "type": "error",
                    "data": f"Error: {str(e)}"
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        # Remove from active connections
        if session_id in _active_connections:
            _active_connections[session_id].discard(websocket)
            if not _active_connections[session_id]:
                del _active_connections[session_id]

