"""
Hash Generation Service
Generates various hash types from input strings or files
"""
import hashlib
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path
from utils.logger import log as logger


class HashService:
    """Service for generating hashes of various types"""
    
    SUPPORTED_HASHES = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha224': hashlib.sha224,
        'sha256': hashlib.sha256,
        'sha384': hashlib.sha384,
        'sha512': hashlib.sha512,
        'sha3_224': hashlib.sha3_224,
        'sha3_256': hashlib.sha3_256,
        'sha3_384': hashlib.sha3_384,
        'sha3_512': hashlib.sha3_512,
        'blake2b': hashlib.blake2b,
        'blake2s': hashlib.blake2s,
    }
    
    @classmethod
    def generate_hash(cls, input_text: str, hash_type: str = 'sha256') -> Dict[str, Any]:
        """
        Generate a hash from input text.
        
        Args:
            input_text: Text to hash
            hash_type: Type of hash (md5, sha256, etc.)
            
        Returns:
            Dictionary with hash, hash_type, and input info
        """
        hash_type_lower = hash_type.lower().replace('-', '_')
        
        if hash_type_lower not in cls.SUPPORTED_HASHES:
            raise ValueError(f"Unsupported hash type: {hash_type}. Supported: {', '.join(cls.SUPPORTED_HASHES.keys())}")
        
        hash_func = cls.SUPPORTED_HASHES[hash_type_lower]
        hash_obj = hash_func(input_text.encode('utf-8'))
        hash_value = hash_obj.hexdigest()
        
        return {
            'hash': hash_value,
            'hash_type': hash_type_lower,
            'input': input_text,
            'input_length': len(input_text),
            'command': f"echo -n '{input_text}' | {hash_type_lower}sum | cut -d' ' -f1"
        }
    
    @classmethod
    def save_hash_to_file(
        cls,
        hash_value: str,
        hash_type: str,
        output_path: str,
        input_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save hash to a file.
        
        Args:
            hash_value: The hash value to save
            hash_type: Type of hash
            output_path: Path where to save the hash
            input_text: Optional original input text
            
        Returns:
            Dictionary with file path and info
        """
        output_file = Path(output_path)
        
        # Ensure directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write hash to file (format: hash or hash:input)
        if input_text:
            content = f"{hash_value}\n"
        else:
            content = f"{hash_value}\n"
        
        output_file.write_text(content)
        
        logger.info(f"Saved {hash_type} hash to {output_file}")
        
        return {
            'file_path': str(output_file.absolute()),
            'hash_type': hash_type,
            'hash': hash_value,
            'saved': True
        }
    
    @classmethod
    def generate_and_save(
        cls,
        input_text: str,
        hash_type: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate hash and optionally save to file.
        
        Args:
            input_text: Text to hash
            hash_type: Type of hash
            output_path: Optional path to save hash file
            
        Returns:
            Dictionary with hash info and file path if saved
        """
        result = cls.generate_hash(input_text, hash_type)
        
        if output_path:
            file_result = cls.save_hash_to_file(
                result['hash'],
                hash_type,
                output_path,
                input_text
            )
            result.update(file_result)
        
        return result

