"""
Main LINA integration service
Wraps the existing LINA Brain and agents for API use
"""
import os
import sys
import importlib.util
from typing import Dict, Any, Optional
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.brain import Brain
from utils.logger import log as logger

# Import from main.py - need to handle carefully
try:
    # Try importing directly
    import importlib.util
    main_path = PROJECT_ROOT / "main.py"
    spec = importlib.util.spec_from_file_location("main_module", main_path)
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    
    initialize_phoenix_foundation = main_module.initialize_phoenix_foundation
    OutputManager = main_module.OutputManager
    AsyncTaskManager = main_module.AsyncTaskManager
    InterfaceState = main_module.InterfaceState
except Exception as e:
    logger.warning(f"Could not import from main.py directly: {e}")
    # Fallback - define minimal versions if needed
    raise


class LINAService:
    """
    Main service for initializing and managing LINA backend instances.
    Each session gets its own Brain instance.
    """
    
    _environment: Optional[Dict[str, Any]] = None
    
    @classmethod
    def get_environment(cls) -> Dict[str, Any]:
        """Get or initialize the LINA environment"""
        if cls._environment is None:
            logger.info("Initializing LINA Phoenix Foundation for API")
            cls._environment = initialize_phoenix_foundation()
        return cls._environment
    
    @classmethod
    def create_brain(cls, expert_role: str) -> Brain:
        """
        Create a new Brain instance for a session
        
        Args:
            expert_role: User role (Student, Forensic Expert, Penetration Tester)
            
        Returns:
            Initialized Brain instance
        """
        environment = cls.get_environment()
        
        logger.info(f"Creating Brain instance for role: {expert_role}")
        
        brain = Brain(
            config=environment['config'],
            tool_registry_path=environment['paths']['tool_registry'],
            risk_database_path=environment['paths']['risk_database'],
            param_registries_path=environment['paths']['param_registries'],
            expert_role=expert_role
        )
        
        logger.info(f"Brain instance created successfully for {expert_role}")
        return brain
    
    @staticmethod
    def create_output_manager() -> OutputManager:
        """Create a new OutputManager instance"""
        return OutputManager()
    
    @staticmethod
    def create_task_manager() -> AsyncTaskManager:
        """Create a new AsyncTaskManager instance"""
        return AsyncTaskManager()
    
    @staticmethod
    def create_interface_state(expert_role: str, ai_engine: str) -> InterfaceState:
        """Create a new InterfaceState instance"""
        return InterfaceState(expert_role=expert_role, ai_engine=ai_engine)

