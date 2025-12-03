# agent/llm_engine.py
# Architect: Simplified Cloud-Only AI Engine for Phoenix Architecture
#
# This streamlined version uses ONLY Google Gemini for all AI operations,
# providing a stable, reliable, and high-performance cloud AI solution.

import os
from typing import Dict, Any, Tuple

import google.generativeai as genai

from utils.logger import log


class LLMEngine:
    """
    Cloud-Only AI engine using Google Gemini.
    
    This simplified architecture provides a stable, reliable interface
    for all AI operations using only Google's Gemini models.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the LLM engine with Google Gemini.
        
        Args:
            config: The global configuration dictionary
        """
        log.info("Initializing Cloud-Only LLM Engine with Google Gemini")
        
        self.config = config
        self.google_model = None
        
        # Setup Google Gemini
        self._setup_google_gemini()
    
    def _setup_google_gemini(self):
        """Sets up Google Gemini for cloud AI operations."""
        try:
            google_config = self.config.get('llm_providers', {}).get('google', {})
            api_key = os.getenv(google_config.get('api_key_env_var', 'GOOGLE_API_KEY'))
            
            if not api_key:
                log.warning("Google API key not found. LLM operations will fail. Please set GOOGLE_API_KEY environment variable.")
                self.google_model = None
                # Don't raise error - allow session creation but warn user
                return
            
            log.info("Configuring Google Gemini API...")
            genai.configure(api_key=api_key)
            model_name = google_config.get('model', 'gemini-2.0-flash')
            log.info(f"Creating GenerativeModel: {model_name}")
            self.google_model = genai.GenerativeModel(model_name)
            
            log.info(f"✅ Google Gemini configured successfully with model: {model_name}")
            
        except Exception as e:
            log.error(f"Failed to configure Google Gemini: {e}", exc_info=True)
            self.google_model = None
            # Don't raise - allow session creation even if LLM setup fails
            # User will get errors when trying to use AI features
    
    def is_ready(self) -> bool:
        """
        Checks if the engine is ready to process requests.
        
        Returns:
            True if Gemini is properly configured, False otherwise
        """
        return self.google_model is not None
    
    def generate_response(self, prompt: str, is_json: bool = False) -> Tuple[bool, str]:
        """
        Generates a response using Google Gemini.
        
        Args:
            prompt: The prompt to send to the AI
            is_json: If True, instructs the AI to format response as JSON
            
        Returns:
            Tuple of (success: bool, content: str)
        """
        if not self.is_ready():
            return False, "Google Gemini is not configured. Please check your GOOGLE_API_KEY."
        
        # Add JSON formatting instruction if requested
        if is_json:
            prompt = f"{prompt}\n\nPlease format your response as valid JSON."
        
        return self._call_google_gemini(prompt)
    
    def _call_google_gemini(self, prompt: str) -> Tuple[bool, str]:
        """
        Calls Google Gemini API with proper error handling, timeout, and retry logic.
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            Tuple of (success: bool, response: str)
        """
        if not self.google_model:
            return False, "Google Gemini not configured"
        
        # Retry configuration
        max_retries = 3
        base_timeout = 45  # Increased from 30 to 45 seconds
        
        for attempt in range(max_retries):
            try:
                # Progressive timeout increase for retries
                timeout = base_timeout + (attempt * 15)  # 45s, 60s, 75s
                
                log.info(f"Gemini API call attempt {attempt + 1}/{max_retries} (timeout: {timeout}s)")
                
                # Configure request with progressive timeout
                request_options = {"timeout": timeout}
                response = self.google_model.generate_content(prompt, request_options=request_options)
                
                # Handle blocked responses
                if not response.parts:
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                        return False, f"Content blocked by Gemini: {response.prompt_feedback.block_reason}"
                    return False, "Gemini returned empty response"
                
                log.info(f"✅ Gemini API call successful on attempt {attempt + 1}")
                return True, response.text
                
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a timeout or rate limit error that we should retry
                is_retryable = any(keyword in error_msg.lower() for keyword in [
                    'timeout', 'timed out', '504', '503', '502', '429', 'rate limit', 'quota'
                ])
                
                if attempt < max_retries - 1 and is_retryable:
                    wait_time = (attempt + 1) * 2  # 2s, 4s, 6s
                    log.warning(f"Retryable error on attempt {attempt + 1}: {error_msg}")
                    log.info(f"Retrying in {wait_time} seconds...")
                    
                    import time
                    time.sleep(wait_time)
                    continue
                else:
                    # Final attempt failed or non-retryable error
                    final_error = f"Google Gemini API call failed after {attempt + 1} attempts: {error_msg}"
                    log.error(final_error)
                    return False, final_error
        
        # This should never be reached, but just in case
        return False, "Google Gemini API call failed: Maximum retries exceeded"
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Returns information about the current provider configuration.
        
        Returns:
            Dictionary with provider information
        """
        return {
            'mode': 'Cloud AI',
            'provider': 'Google Gemini',
            'model': self.config.get('llm_providers', {}).get('google', {}).get('model', 'gemini-2.0-flash'),
            'ready': self.google_model is not None
        }