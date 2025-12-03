"""
File Manager
Handles file uploads, downloads, validation, and path management for tools
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from utils.logger import log as logger


class FileManager:
    """
    Manages file operations for tool execution:
    - File uploads and storage
    - File validation (existence, format, size)
    - Output file management
    - Temporary file cleanup
    """
    
    def __init__(self, upload_dir: Optional[str] = None):
        """
        Initialize file manager.
        
        Args:
            upload_dir: Base directory for uploaded files (default: project/uploads)
        """
        if upload_dir:
            self.upload_dir = Path(upload_dir)
        else:
            # Default to project/uploads directory
            project_root = Path(__file__).parent.parent.parent.parent
            self.upload_dir = project_root / "uploads"
        
        # Ensure upload directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Temporary files tracking for cleanup
        self._temp_files: List[Path] = []
    
    def validate_file(self, file_path: str, file_types: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate that a file exists and optionally check its type.
        
        Args:
            file_path: Path to the file
            file_types: Optional list of allowed file extensions (e.g., ['txt', 'hash'])
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        if not path.is_file():
            return False, f"Path is not a file: {file_path}"
        
        # Check file type if specified
        if file_types:
            ext = path.suffix.lstrip('.').lower()
            if ext not in [ft.lower() for ft in file_types]:
                return False, f"File type '{ext}' not allowed. Expected: {', '.join(file_types)}"
        
        return True, None
    
    def resolve_file_path(self, file_path: str, relative_to: Optional[str] = None) -> Path:
        """
        Resolve a file path, handling relative and absolute paths.
        
        Args:
            file_path: File path (may be relative or absolute)
            relative_to: Base directory for relative paths
            
        Returns:
            Resolved Path object
        """
        path = Path(file_path)
        
        # If absolute, use as-is
        if path.is_absolute():
            return path
        
        # If relative, resolve from upload_dir or relative_to
        if relative_to:
            base = Path(relative_to)
        else:
            base = self.upload_dir
        
        return base / path
    
    def create_temp_file(self, suffix: str = ".tmp", content: Optional[str] = None) -> Path:
        """
        Create a temporary file.
        
        Args:
            suffix: File suffix/extension
            content: Optional content to write to file
            
        Returns:
            Path to temporary file
        """
        fd, temp_path = tempfile.mkstemp(suffix=suffix, dir=self.upload_dir)
        os.close(fd)
        
        temp_file = Path(temp_path)
        self._temp_files.append(temp_file)
        
        if content:
            temp_file.write_text(content)
        
        return temp_file
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> Path:
        """
        Save uploaded file content to disk.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        # Sanitize filename
        safe_filename = self._sanitize_filename(filename)
        file_path = self.upload_dir / safe_filename
        
        # Write file
        file_path.write_bytes(file_content)
        
        logger.info(f"Saved uploaded file: {file_path}")
        return file_path
    
    def get_output_file_path(self, base_name: str, output_dir: Optional[Path] = None) -> Path:
        """
        Generate a path for output file.
        
        Args:
            base_name: Base filename
            output_dir: Optional output directory (default: upload_dir/outputs)
            
        Returns:
            Path for output file
        """
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = self.upload_dir / "outputs"
        
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path / base_name
    
    def cleanup_temp_files(self):
        """Clean up all temporary files created during this session."""
        for temp_file in self._temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    logger.debug(f"Cleaned up temp file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")
        
        self._temp_files.clear()
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal and invalid characters."""
        # Remove path components
        filename = Path(filename).name
        
        # Remove dangerous characters
        dangerous_chars = ['..', '/', '\\']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext
        
        return filename
    
    def ensure_directory(self, dir_path: Path) -> Path:
        """Ensure a directory exists, creating it if necessary."""
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

