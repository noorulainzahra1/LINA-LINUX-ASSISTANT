"""
Session management service
Manages user sessions and their associated LINA components
"""

import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import uuid
from datetime import datetime

from agent.brain import Brain
from api.services.lina_service import LINAService
from utils.logger import log as logger

# Import classes from main.py using same method as lina_service
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

main_path = PROJECT_ROOT / "main.py"
spec = importlib.util.spec_from_file_location("main_module", main_path)
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)

InterfaceState = main_module.InterfaceState
OutputManager = main_module.OutputManager
AsyncTaskManager = main_module.AsyncTaskManager


@dataclass
class SessionData:
    """Container for all session-related data"""
    session_id: str
    role: str
    ai_engine: str
    created_at: datetime
    brain: Optional[Brain]  # Can be None for lazy loading
    interface_state: InterfaceState
    output_manager: OutputManager
    task_manager: AsyncTaskManager
    mode: Optional[str] = None  # Work mode: quick, interactive, suggester
    last_activity: datetime = field(default_factory=datetime.now)
    
    def get_brain(self) -> Brain:
        """Lazy load brain - initialize if not already done"""
        if self.brain is None:
            logger.info(f"Lazy initializing Brain for session {self.session_id}...")
            try:
                self.brain = LINAService.create_brain(expert_role=self.role)
                logger.info(f"Brain lazy-initialized successfully for session {self.session_id}")
            except Exception as e:
                logger.error(f"Failed to lazy-initialize Brain for session {self.session_id}: {e}", exc_info=True)
                raise
        return self.brain


class SessionService:
    """
    Manages user sessions and their associated LINA components.
    Each session maintains its own Brain instance and state.
    Singleton pattern to ensure all routers share the same session store.
    """
    _instance = None
    _sessions: Dict[str, SessionData] = {}
    
    def __new__(cls):
        """Singleton pattern - return same instance"""
        if cls._instance is None:
            cls._instance = super(SessionService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize session service (only once due to singleton)"""
        if self._initialized:
            return
        # Use class variable for persistence - only initialize if empty
        if not hasattr(SessionService, '_sessions') or not SessionService._sessions:
            SessionService._sessions = {}
        self._sessions = SessionService._sessions  # Reference the class variable
        self._initialized = True
        logger.info(f"SessionService initialized (singleton) - {len(self._sessions)} existing sessions")
    
    def create_session(self, role: str, ai_engine: str = "Cloud AI (Google Gemini)", mode: Optional[str] = None) -> str:
        """
        Create a new session with all necessary LINA components
        
        Args:
            role: User role (Student, Forensic Expert, Penetration Tester)
            ai_engine: AI engine to use
            mode: Work mode (quick, interactive, suggester)
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        logger.info(f"Creating new session {session_id} for role: {role}, mode: {mode}")
        
        try:
            # Create interface components first (fast)
            logger.info(f"Creating interface components for session {session_id}...")
            interface_state = LINAService.create_interface_state(expert_role=role, ai_engine=ai_engine)
            output_manager = LINAService.create_output_manager()
            task_manager = LINAService.create_task_manager()
            
            # Skip Brain initialization completely - initialize on first use via get_brain()
            # This makes session creation instant
            logger.info(f"Session {session_id} - Brain will be initialized on first use (lazy loading)")
            brain = None
            
            # Store session data (even if brain is None, we'll initialize it on first use)
            session_data = SessionData(
                session_id=session_id,
                role=role,
                ai_engine=ai_engine,
                created_at=datetime.now(),
                brain=brain,  # May be None if initialization failed
                interface_state=interface_state,
                output_manager=output_manager,
                task_manager=task_manager,
                mode=mode
            )
            
            self._sessions[session_id] = session_data
            
            logger.info(f"Session {session_id} created successfully")
            return session_id
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}", exc_info=True)
            raise
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get session data by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionData if found, None otherwise
        """
        return self._sessions.get(session_id)
    
    def update_mode(self, session_id: str, mode: str) -> bool:
        """
        Update the work mode for a session
        
        Args:
            session_id: Session identifier
            mode: New work mode (quick, interactive, suggester)
            
        Returns:
            True if updated, False if session not found
        """
        session_data = self._sessions.get(session_id)
        if not session_data:
            return False
        
        session_data.mode = mode
        logger.info(f"Updated mode for session {session_id} to {mode}")
        return True
    
    def update_activity(self, session_id: str) -> bool:
        """
        Update last activity timestamp for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session exists, False otherwise
        """
        session = self.get_session(session_id)
        if session:
            session.last_activity = datetime.now()
            session.interface_state.update_activity()
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and cleanup resources
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self._sessions:
            logger.info(f"Deleting session {session_id}")
            # Could add cleanup logic here if needed
            del self._sessions[session_id]
            return True
        return False
    
    def list_sessions(self) -> list:
        """Get list of all active session IDs"""
        return list(self._sessions.keys())
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self._sessions)

