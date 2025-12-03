# agent/session_manager.py
# Architect: The unified session state and memory management system for Phoenix Architecture.
#
# This definitive agent consolidates all session-related functionality including
# persistent memory storage, session state tracking, interaction history, and
# learning analytics. It serves as the central nervous system for LINA's context
# awareness and provides a foundation for adaptive behavior.

import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from utils.logger import log


class SessionManager:
    """
    The unified session and memory management system for LINA.
    
    This agent consolidates multiple critical capabilities:
    1. Persistent Memory: SQLite-based storage of interaction history
    2. Session State: Current session tracking and analytics
    3. Context Management: Maintaining conversational context
    4. Learning Analytics: Pattern recognition and adaptation
    
    By unifying these related functions, we create a more cohesive and
    intelligent session management system.
    """
    
    def __init__(self):
        """
        Initializes the SessionManager with database connection and session state.
        """
        # Database setup
        self.db_path = self._setup_database_path()
        self.conn: Optional[sqlite3.Connection] = None
        self._connect_database()
        self._setup_database_schema()
        
        # Session state tracking
        self.session_id = self._generate_session_id()
        self.session_start_time = datetime.now()
        self.session_stats = {
            'commands_executed': 0,
            'tools_used': set(),
            'conversations': 0,
            'explanations_requested': 0,
            'plans_generated': 0,
            'plans_executed': 0,
            'risk_assessments': 0,
            'errors_encountered': 0
        }
        
        # Context management
        self.conversation_history: List[Dict[str, str]] = []
        self.recent_actions: List[Dict[str, Any]] = []
        self.user_preferences: Dict[str, Any] = {}
        
        log.info(f"SessionManager initialized for session {self.session_id}")
    
    def _setup_database_path(self) -> str:
        """
        Sets up the database directory and returns the database file path.
        
        Returns:
            Absolute path to the SQLite database file
        """
        # Create database directory relative to project root
        project_root = os.path.dirname(os.path.dirname(__file__))
        db_dir = os.path.join(project_root, 'data', 'db')
        os.makedirs(db_dir, exist_ok=True)
        
        return os.path.join(db_dir, 'lina_history.sqlite')
    
    def _connect_database(self):
        """
        Establishes connection to the SQLite database.
        
        Raises:
            sqlite3.Error: If database connection fails
        """
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            log.info(f"Connected to session database at {self.db_path}")
        except sqlite3.Error as e:
            log.critical(f"FATAL: Could not connect to database at {self.db_path}: {e}")
            raise
    
    def _setup_database_schema(self):
        """
        Creates or verifies the database schema for session management.
        Includes migration logic for existing databases.
        """
        if not self.conn:
            log.error("Cannot setup database schema: No active connection")
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Check if history table exists and get its schema
            cursor.execute("PRAGMA table_info(history)")
            existing_columns = [column[1] for column in cursor.fetchall()]
            
            # Main history table - create if doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_input TEXT NOT NULL,
                executed_action TEXT NOT NULL,
                action_type TEXT NOT NULL,
                tool_name TEXT,
                output TEXT,
                risk_assessment TEXT,
                execution_time_ms INTEGER,
                success BOOLEAN
            )
            """)
            
            # --- UPDATE: Enhanced schema migration logic for multiple columns ---
            migration_performed = False
            
            # CRITICAL: Schema migration for existing databases
            # If the table exists but doesn't have session_id column, add it
            if existing_columns and 'session_id' not in existing_columns:
                log.info("Migrating database schema: Adding session_id column to history table")
                cursor.execute("ALTER TABLE history ADD COLUMN session_id TEXT DEFAULT 'legacy_session'")
                migration_performed = True
                log.info("Added session_id column to history table")
            
            # --- UPDATE: Add tool_name column migration ---
            # If the table exists but doesn't have tool_name column, add it
            if existing_columns and 'tool_name' not in existing_columns:
                log.info("Migrating database schema: Adding tool_name column to history table")
                cursor.execute("ALTER TABLE history ADD COLUMN tool_name TEXT")
                migration_performed = True
                log.info("Added tool_name column to history table")

            # --- UPDATE: Add execution_time_ms column migration ---
            # If the table exists but doesn't have execution_time_ms column, add it
            if existing_columns and 'execution_time_ms' not in existing_columns:
                log.info("Migrating database schema: Adding execution_time_ms column to history table")
                cursor.execute("ALTER TABLE history ADD COLUMN execution_time_ms INTEGER")
                migration_performed = True
                log.info("Added execution_time_ms column to history table")

            # --- UPDATE: Add success column migration ---
            # If the table exists but doesn't have success column, add it
            if existing_columns and 'success' not in existing_columns:
                log.info("Migrating database schema: Adding success column to history table")
                cursor.execute("ALTER TABLE history ADD COLUMN success BOOLEAN")
                migration_performed = True
                log.info("Added success column to history table")
            
            # Commit all migrations at once
            if migration_performed:
                self.conn.commit()
                log.info("Database schema migration completed successfully")
            
            # Session metadata table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                total_commands INTEGER DEFAULT 0,
                total_tools_used INTEGER DEFAULT 0,
                total_conversations INTEGER DEFAULT 0,
                ai_engine TEXT,
                ai_mode TEXT,
                expert_role TEXT,
                session_metadata TEXT
            )
            """)
            
            # User preferences table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
            """)
            
            self.conn.commit()
            log.info("Database schema verified and ready")
            
        except sqlite3.Error as e:
            log.error(f"Failed to setup database schema: {e}")
    
    def _generate_session_id(self) -> str:
        """
        Generates a unique session identifier.
        
        Returns:
            Unique session ID string
        """
        return f"lina_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # ==========================================
    # SESSION LIFECYCLE MANAGEMENT
    # ==========================================
    
    def start_session(self, ai_engine: str, ai_mode: str, expert_role: str, metadata: Dict[str, Any] = None):
        """
        Officially starts a new session with the given configuration.
        
        Args:
            ai_engine: The AI engine being used (cloud/local)
            ai_mode: The AI operational mode (performance/quality)
            expert_role: The selected expert role
            metadata: Additional session metadata
        """
        if not self.conn:
            log.error("Cannot start session: No database connection")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO sessions (session_id, start_time, ai_engine, ai_mode, expert_role, session_metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.session_id,
                self.session_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                ai_engine,
                ai_mode,
                expert_role,
                json.dumps(metadata or {})
            ))
            self.conn.commit()
            log.info(f"Session {self.session_id} started with {ai_engine}/{ai_mode}/{expert_role}")
            
        except sqlite3.Error as e:
            log.error(f"Failed to start session: {e}")
    
    def end_session(self):
        """
        Ends the current session and updates session statistics.
        """
        if not self.conn:
            log.error("Cannot end session: No database connection")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            UPDATE sessions SET 
                end_time = ?,
                total_commands = ?,
                total_tools_used = ?,
                total_conversations = ?
            WHERE session_id = ?
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.session_stats['commands_executed'],
                len(self.session_stats['tools_used']),
                self.session_stats['conversations'],
                self.session_id
            ))
            self.conn.commit()
            log.info(f"Session {self.session_id} ended successfully")
            
        except sqlite3.Error as e:
            log.error(f"Failed to end session: {e}")
    
    # ==========================================
    # MEMORY AND HISTORY MANAGEMENT
    # ==========================================
    
    def add_interaction(self, user_input: str, executed_action: str, action_type: str, 
                       tool_name: str = None, output: str = None, risk_assessment: str = None,
                       execution_time_ms: int = None, success: bool = True):
        """
        Records a complete user interaction in the persistent memory.
        
        Args:
            user_input: The user's original request
            executed_action: The action that was executed
            action_type: Type of action (command, tool, conversation, etc.)
            tool_name: Name of the tool used (if applicable)
            output: Output or result of the action
            risk_assessment: Risk assessment information
            execution_time_ms: Execution time in milliseconds
            success: Whether the action succeeded
        """
        if not self.conn:
            log.error("Cannot add interaction: No database connection")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO history (session_id, timestamp, user_input, executed_action, 
                               action_type, tool_name, output, risk_assessment, 
                               execution_time_ms, success)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.session_id, timestamp, user_input, executed_action,
                action_type, tool_name, output, risk_assessment,
                execution_time_ms, success
            ))
            self.conn.commit()
            
            # Update session statistics
            self._update_session_stats(action_type, tool_name, success)
            
            # Add to recent actions for context
            self.recent_actions.append({
                'timestamp': timestamp,
                'user_input': user_input,
                'action': executed_action,
                'type': action_type,
                'tool': tool_name,
                'success': success
            })
            
            # Keep only recent actions (last 10)
            self.recent_actions = self.recent_actions[-10:]
            
            log.info(f"Interaction recorded: {action_type} - {executed_action}")
            
        except sqlite3.Error as e:
            log.error(f"Failed to record interaction: {e}")
    
    def _update_session_stats(self, action_type: str, tool_name: str = None, success: bool = True):
        """
        Updates session statistics based on the action performed.
        
        Args:
            action_type: Type of action performed
            tool_name: Name of tool used (if applicable)
            success: Whether the action succeeded
        """
        if action_type == 'command':
            self.session_stats['commands_executed'] += 1
        elif action_type == 'tool' and tool_name:
            self.session_stats['tools_used'].add(tool_name)
        elif action_type == 'conversation':
            self.session_stats['conversations'] += 1
        elif action_type == 'explanation':
            self.session_stats['explanations_requested'] += 1
        elif action_type == 'plan':
            self.session_stats['plans_generated'] += 1
        elif action_type == 'plan_execution':
            self.session_stats['plans_executed'] += 1
        elif action_type == 'risk_assessment':
            self.session_stats['risk_assessments'] += 1
        
        if not success:
            self.session_stats['errors_encountered'] += 1
    
    def get_recent_history(self, limit: int = 5) -> List[Tuple]:
        """
        Retrieves recent interaction history for context awareness.
        
        Args:
            limit: Maximum number of recent entries to retrieve
            
        Returns:
            List of tuples containing recent interaction data
        """
        if not self.conn:
            log.error("Cannot get history: No database connection")
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT timestamp, user_input, executed_action, action_type, tool_name 
            FROM history 
            WHERE session_id = ? 
            ORDER BY id DESC 
            LIMIT ?
            """, (self.session_id, limit))
            
            return cursor.fetchall()
            
        except sqlite3.Error as e:
            log.error(f"Failed to retrieve history: {e}")
            return []
    
    # ==========================================
    # CONVERSATION CONTEXT MANAGEMENT
    # ==========================================
    
    def add_conversation_turn(self, role: str, content: str):
        """
        Adds a turn to the conversation history for context management.
        
        Args:
            role: Role of the speaker (user/assistant)
            content: Content of the message
        """
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep conversation history manageable (last 20 turns)
        self.conversation_history = self.conversation_history[-20:]
    
    def get_conversation_context(self, max_turns: int = 10) -> List[Dict[str, str]]:
        """
        Returns recent conversation history for context.
        
        Args:
            max_turns: Maximum number of turns to return
            
        Returns:
            List of conversation turns
        """
        return self.conversation_history[-max_turns:]
    
    def clear_conversation_context(self):
        """Clears the current conversation context."""
        self.conversation_history.clear()
        log.info("Conversation context cleared")
    
    # ==========================================
    # USER PREFERENCES MANAGEMENT
    # ==========================================
    
    def set_preference(self, key: str, value: Any):
        """
        Sets a user preference with persistent storage.
        
        Args:
            key: Preference key
            value: Preference value
        """
        if not self.conn:
            log.error("Cannot set preference: No database connection")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO user_preferences (key, value, last_updated)
            VALUES (?, ?, ?)
            """, (key, json.dumps(value), datetime.now().isoformat()))
            self.conn.commit()
            
            # Update local cache
            self.user_preferences[key] = value
            log.info(f"Preference set: {key} = {value}")
            
        except sqlite3.Error as e:
            log.error(f"Failed to set preference: {e}")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Gets a user preference value.
        
        Args:
            key: Preference key
            default: Default value if preference doesn't exist
            
        Returns:
            Preference value or default
        """
        # Check local cache first
        if key in self.user_preferences:
            return self.user_preferences[key]
        
        if not self.conn:
            return default
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
            result = cursor.fetchone()
            
            if result:
                value = json.loads(result[0])
                self.user_preferences[key] = value
                return value
            else:
                return default
                
        except (sqlite3.Error, json.JSONDecodeError) as e:
            log.error(f"Failed to get preference {key}: {e}")
            return default
    
    # ==========================================
    # ANALYTICS AND REPORTING
    # ==========================================
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Returns a comprehensive summary of the current session.
        
        Returns:
            Dictionary containing session analytics
        """
        duration = datetime.now() - self.session_start_time
        
        return {
            'session_id': self.session_id,
            'duration_minutes': round(duration.total_seconds() / 60, 2),
            'commands_executed': self.session_stats['commands_executed'],
            'unique_tools_used': len(self.session_stats['tools_used']),
            'tools_list': list(self.session_stats['tools_used']),
            'conversations': self.session_stats['conversations'],
            'explanations_requested': self.session_stats['explanations_requested'],
            'plans_generated': self.session_stats['plans_generated'],
            'plans_executed': self.session_stats['plans_executed'],
            'errors_encountered': self.session_stats['errors_encountered'],
            'recent_actions_count': len(self.recent_actions),
            'conversation_turns': len(self.conversation_history)
        }
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Analyzes session data to provide learning insights.
        
        Returns:
            Dictionary containing learning insights and patterns
        """
        summary = self.get_session_summary()
        
        # Calculate success rate
        total_actions = summary['commands_executed']
        errors = summary['errors_encountered']
        success_rate = ((total_actions - errors) / total_actions * 100) if total_actions > 0 else 100
        
        # Identify most used tools
        tool_usage = {}
        for action in self.recent_actions:
            if action.get('tool'):
                tool_usage[action['tool']] = tool_usage.get(action['tool'], 0) + 1
        
        most_used_tool = max(tool_usage.keys(), key=tool_usage.get) if tool_usage else None
        
        return {
            'session_productivity': 'High' if total_actions > 10 else 'Medium' if total_actions > 5 else 'Low',
            'success_rate': round(success_rate, 1),
            'most_used_tool': most_used_tool,
            'tool_diversity': len(summary['tools_list']),
            'conversation_ratio': round(summary['conversations'] / max(total_actions, 1), 2),
            'learning_engagement': summary['explanations_requested']
        }
    
    # ==========================================
    # CLEANUP AND DESTRUCTION
    # ==========================================
    
    def __del__(self):
        """
        Ensures proper cleanup of database connections.
        """
        if self.conn:
            self.conn.close()
            log.info("SessionManager database connection closed")
