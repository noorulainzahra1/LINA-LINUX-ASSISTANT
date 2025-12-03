"""
Hash generation handler for LINA
Handles hash generation requests and file saving automatically
"""
import re
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from utils.logger import log


class HashHandler:
    """Handles hash generation and file saving requests"""
    
    HASH_PATTERNS = [
        (r'hash\s+(md5|sha1|sha224|sha256|sha384|sha512|sha3[-_]?224|sha3[-_]?256|sha3[-_]?384|sha3[-_]?512|blake2b|blake2s)\s+["\']?([^"\']+)["\']?', re.IGNORECASE),
        (r'create\s+(?:a\s+)?(md5|sha1|sha224|sha256|sha384|sha512|sha3[-_]?224|sha3[-_]?256|sha3[-_]?384|sha3[-_]?512|blake2b|blake2s)\s+hash\s+of\s+["\']?([^"\']+)["\']?', re.IGNORECASE),
        (r'generate\s+(?:a\s+)?(md5|sha1|sha224|sha256|sha384|sha512|sha3[-_]?224|sha3[-_]?256|sha3[-_]?384|sha3[-_]?512|blake2b|blake2s)\s+hash\s+of\s+["\']?([^"\']+)["\']?', re.IGNORECASE),
    ]
    
    SAVE_PATTERNS = [
        r'save\s+to\s+["\']?([^"\'\s]+)["\']?',
        r'save\s+as\s+["\']?([^"\'\s]+)["\']?',
        r'to\s+file\s+["\']?([^"\'\s]+)["\']?',
        r'in\s+file\s+["\']?([^"\'\s]+)["\']?',
        r'at\s+["\']?([^"\'\s]+)["\']?',
    ]
    
    @classmethod
    def is_hash_request(cls, user_input: str) -> bool:
        """Check if user input is a hash generation request"""
        user_lower = user_input.lower()
        for pattern, flags in cls.HASH_PATTERNS:
            if re.search(pattern, user_input, flags):
                return True
        return False
    
    @classmethod
    def extract_hash_request(cls, user_input: str) -> Optional[Tuple[str, str, bool, Optional[str]]]:
        """
        Extract hash type, input text, save flag, and file path from request.
        
        Returns:
            Tuple of (hash_type, input_text, save_to_file, file_path) or None
        """
        # First check for hash request
        hash_type = None
        input_text = None
        
        for pattern, flags in cls.HASH_PATTERNS:
            match = re.search(pattern, user_input, flags)
            if match:
                hash_type = match.group(1).lower().replace('-', '_')
                input_text = match.group(2).strip().strip('"\'').strip()
                break
        
        if not hash_type or not input_text:
            return None
        
        # Remove file path from input_text if it was captured incorrectly
        # Check for save request BEFORE extracting input_text
        save_to_file = False
        file_path = None
        
        # Try to find save patterns first
        for pattern in cls.SAVE_PATTERNS:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                save_to_file = True
                file_path = match.group(1).strip().strip('"\'').strip()
                # Remove file path part from input_text if it got captured
                if file_path in input_text:
                    input_text = input_text.replace(f'save to {file_path}', '').replace(f'save as {file_path}', '').strip()
                break
        
        # Also check for generic "save" mention (but no specific path)
        if not save_to_file and re.search(r'\bsave\b', user_input, re.IGNORECASE):
            save_to_file = True
            # Generate default filename
            file_path = None
        
        return (hash_type, input_text, save_to_file, file_path)
    
    @classmethod
    def generate_hash_response(
        cls,
        hash_type: str,
        input_text: str,
        save_to_file: bool = False,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate hash using HashService and optionally save to file.
        
        Returns:
            Dictionary with hash info and execution details
        """
        try:
            # Import here to avoid circular dependencies
            from api.services.hash_service import HashService
            
            # Generate hash
            result = HashService.generate_hash(input_text, hash_type)
            hash_value = result['hash']
            
            # Handle file saving
            saved_file_path = None
            if save_to_file:
                if not file_path:
                    # Generate default path
                    project_root = Path(__file__).parent.parent
                    uploads_dir = project_root / "uploads" / "hashes"
                    uploads_dir.mkdir(parents=True, exist_ok=True)
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_path = str(uploads_dir / f"hash_{hash_type}_{timestamp}.txt")
                
                # Ensure path is absolute
                if not Path(file_path).is_absolute():
                    project_root = Path(__file__).parent.parent
                    if file_path.startswith('/'):
                        file_path = file_path[1:]
                    file_path = str(project_root / file_path)
                
                # Save hash to file
                save_result = HashService.save_hash_to_file(
                    hash_value,
                    hash_type,
                    file_path,
                    input_text
                )
                saved_file_path = save_result['file_path']
                log.info(f"Hash saved to: {saved_file_path}")
            
            # Build response
            message = f"Generated {hash_type.upper()} hash: `{hash_value}`"
            if saved_file_path:
                message += f"\n\n✅ Saved to: `{saved_file_path}`\nYou can now use this file with hashcat, john, or other cracking tools."
            
            return {
                'type': 'command',
                'command': result['command'],
                'message': message,
                'hash': hash_value,
                'hash_type': hash_type,
                'input': input_text,
                'file_path': saved_file_path,
                'saved': bool(saved_file_path),
                'explanation': f"Generated {hash_type.upper()} hash of '{input_text}'"
            }
            
        except Exception as e:
            log.error(f"Hash generation failed: {e}", exc_info=True)
            return {
                'type': 'error',
                'message': f"Failed to generate hash: {str(e)}"
            }

