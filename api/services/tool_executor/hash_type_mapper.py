"""
Hash Type Mapper
Maps common hash type names to tool-specific hash mode numbers
"""
from typing import Dict, Optional
from utils.logger import log as logger


class HashTypeMapper:
    """Maps hash type names to tool-specific mode numbers"""
    
    # Hashcat hash type mappings
    HASHCAT_MODES: Dict[str, int] = {
        'md5': 0,
        'md4': 900,
        'sha1': 100,
        'sha224': 1300,
        'sha256': 1400,
        'sha384': 10800,
        'sha512': 1700,
        'sha-256': 1400,
        'sha-512': 1700,
        'sha-1': 100,
        'sha-224': 1300,
        'sha-384': 10800,
        'ntlm': 1000,
        'bcrypt': 3200,
        'sha3_224': 17300,
        'sha3_256': 17400,
        'sha3_384': 17500,
        'sha3_512': 17600,
    }
    
    # John the Ripper format mappings
    JOHN_FORMATS: Dict[str, str] = {
        'md5': 'raw-md5',
        'md4': 'raw-md4',
        'sha1': 'raw-sha1',
        'sha224': 'raw-sha224',
        'sha256': 'raw-sha256',
        'sha384': 'raw-sha384',
        'sha512': 'raw-sha512',
        'sha-256': 'raw-sha256',
        'sha-512': 'raw-sha512',
        'sha-1': 'raw-sha1',
        'ntlm': 'nt',
        'bcrypt': 'bcrypt',
    }
    
    @classmethod
    def get_hashcat_mode(cls, hash_type: str) -> Optional[int]:
        """
        Get hashcat mode number for a hash type.
        
        Args:
            hash_type: Hash type name (e.g., "sha256", "sha-256", "md5")
            
        Returns:
            Hashcat mode number or None if not found
        """
        hash_type_lower = hash_type.lower().replace('_', '-').strip()
        
        # Try exact match first
        if hash_type_lower in cls.HASHCAT_MODES:
            return cls.HASHCAT_MODES[hash_type_lower]
        
        # Try removing dashes
        hash_type_no_dash = hash_type_lower.replace('-', '')
        if hash_type_no_dash in cls.HASHCAT_MODES:
            return cls.HASHCAT_MODES[hash_type_no_dash]
        
        # Try as integer (user might have provided mode directly)
        try:
            mode = int(hash_type)
            return mode
        except (ValueError, TypeError):
            pass
        
        logger.warning(f"Unknown hash type for hashcat: {hash_type}")
        return None
    
    @classmethod
    def get_john_format(cls, hash_type: str) -> Optional[str]:
        """
        Get John the Ripper format for a hash type.
        
        Args:
            hash_type: Hash type name
            
        Returns:
            John format string or None if not found
        """
        hash_type_lower = hash_type.lower().replace('_', '-').strip()
        
        if hash_type_lower in cls.JOHN_FORMATS:
            return cls.JOHN_FORMATS[hash_type_lower]
        
        # Try removing dashes
        hash_type_no_dash = hash_type_lower.replace('-', '')
        if hash_type_no_dash in cls.JOHN_FORMATS:
            return cls.JOHN_FORMATS[hash_type_no_dash]
        
        logger.warning(f"Unknown hash type for john: {hash_type}")
        return None

