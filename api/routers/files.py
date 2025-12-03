"""
File management endpoints
Save outputs and make them accessible to tools
"""
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from api.services.tool_executor.file_manager import FileManager
from utils.logger import log as logger

router = APIRouter(prefix="/api/files", tags=["files"])

# Initialize file manager
file_manager = FileManager()


class SaveFileRequest(BaseModel):
    """Request to save content to a file"""
    filename: str = Field(..., description="Name of the file to save")
    content: str = Field(..., description="Content to save")
    directory: Optional[str] = Field(default=None, description="Subdirectory within uploads (e.g., 'hashes')")


class SaveFileResponse(BaseModel):
    """Response from file save operation"""
    success: bool
    file_path: str
    message: str


@router.post("/save", response_model=SaveFileResponse)
async def save_file(request: SaveFileRequest) -> SaveFileResponse:
    """
    Save content to a file in the uploads directory.
    Files saved here are accessible to tools like hashcat and john.
    """
    try:
        # Determine save directory
        if request.directory:
            save_dir = file_manager.upload_dir / request.directory
        else:
            save_dir = file_manager.upload_dir
        
        # Ensure directory exists
        file_manager.ensure_directory(save_dir)
        
        # Sanitize filename
        safe_filename = file_manager._sanitize_filename(request.filename)
        file_path = save_dir / safe_filename
        
        # Write content
        file_path.write_text(request.content)
        
        logger.info(f"Saved file: {file_path}")
        
        return SaveFileResponse(
            success=True,
            file_path=str(file_path),
            message=f"File saved to {file_path}"
        )
        
    except Exception as e:
        logger.error(f"Failed to save file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

