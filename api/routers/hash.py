"""
Hash generation endpoints
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from api.services.hash_service import HashService
from utils.logger import log as logger

router = APIRouter(prefix="/api/hash", tags=["hash"])


class HashRequest(BaseModel):
    """Request to generate a hash"""
    input_text: str = Field(..., description="Text to hash")
    hash_type: str = Field(default="sha256", description="Type of hash (md5, sha1, sha256, sha512, etc.)")
    save_to_file: bool = Field(default=False, description="Whether to save hash to a file")
    output_path: str = Field(default=None, description="Path to save hash file (optional)")


class HashResponse(BaseModel):
    """Response from hash generation"""
    hash: str
    hash_type: str
    input: str
    input_length: int
    command: str
    file_path: Optional[str] = None
    saved: bool = False


@router.post("/generate", response_model=HashResponse)
async def generate_hash(request: HashRequest) -> HashResponse:
    """
    Generate a hash from input text.
    
    Example: Generate SHA256 hash of "Noorulayn"
    """
    try:
        if request.save_to_file and not request.output_path:
            # Generate default filename
            from pathlib import Path
            from datetime import datetime
            project_root = Path(__file__).parent.parent.parent
            uploads_dir = project_root / "uploads" / "hashes"
            uploads_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            request.output_path = str(uploads_dir / f"hash_{request.hash_type}_{timestamp}.txt")
        
        result = HashService.generate_and_save(
            input_text=request.input_text,
            hash_type=request.hash_type,
            output_path=request.output_path if request.save_to_file else None
        )
        
        return HashResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to generate hash: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate hash: {str(e)}"
        )

