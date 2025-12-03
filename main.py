"""
Minimal main.py for LINA API
Provides the required classes and functions for the API layer
"""
import os
from pathlib import Path
from typing import Dict, Any, Set
from datetime import datetime
from dataclasses import dataclass, field


class OutputManager:
    """Manages command output capture and storage"""
    
    def __init__(self, output_dir: str = None):
        """Initialize output manager"""
        if output_dir is None:
            output_dir = os.path.join(Path(__file__).parent, "data", "outputs")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session_outputs = []


class AsyncTaskManager:
    """Manages asynchronous tasks"""
    
    def __init__(self):
        """Initialize task manager"""
        self.tasks = []


@dataclass
class InterfaceState:
    """Manages the interface state for a session"""
    
    expert_role: str
    ai_engine: str
    session_stats: Dict[str, Any] = field(default_factory=lambda: {"commands_executed": 0})
    tools_used: Set[str] = field(default_factory=set)
    conversations: int = 0
    command_history: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def update_activity(self):
        """Update last activity timestamp"""
        pass
    
    def get_session_duration(self) -> float:
        """Get session duration in minutes"""
        return (datetime.now() - self.created_at).total_seconds() / 60.0
    
    def add_command(self, command: str):
        """Add a command to history"""
        self.command_history.append(command)
        self.session_stats["commands_executed"] = self.session_stats.get("commands_executed", 0) + 1
    
    def add_tool_used(self, tool_name: str):
        """Add a tool to the used tools set"""
        self.tools_used.add(tool_name)


def initialize_phoenix_foundation() -> Dict[str, Any]:
    """
    Initialize LINA Phoenix Foundation
    Returns configuration and paths needed for Brain initialization
    """
    from utils.logger import log as logger
    
    PROJECT_ROOT = Path(__file__).parent
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        env_file = PROJECT_ROOT / "env"
        if env_file.exists():
            load_dotenv(env_file)
        elif (PROJECT_ROOT / ".env").exists():
            load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        # Manual loading if dotenv not available
        env_file = PROJECT_ROOT / "env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    
    # Load config
    config_path = PROJECT_ROOT / "core" / "config.yaml"
    config = {}
    if config_path.exists():
        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Could not load config.yaml: {e}")
    
    # Default config if not found
    if not config:
        config = {
            'llm_providers': {
                'google': {
                    'api_key_env_var': 'GOOGLE_API_KEY',
                    'model': 'gemini-2.0-flash'  # Use stable model instead of experimental
                }
            }
        }
    
    # Set up paths
    paths = {
        'tool_registry': str(PROJECT_ROOT / "core" / "registry" / "tool_registry.json"),
        'risk_database': str(PROJECT_ROOT / "core" / "registry" / "risk_database.json"),
        'param_registries': str(PROJECT_ROOT / "core" / "registries")
    }
    
    logger.info("Phoenix Foundation initialized for API")
    
    return {
        'config': config,
        'paths': paths
    }

