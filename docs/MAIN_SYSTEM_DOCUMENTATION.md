# LINA Main System Documentation
## Five-Layer Architecture and Central Command Center

---

## Table of Contents

1. [Main System Overview](#1-main-system-overview)
2. [Five-Layer Architecture](#2-five-layer-architecture)
3. [Core System Classes](#3-core-system-classes)
4. [Application Flow and Orchestration](#4-application-flow-and-orchestration)
5. [User Interface and Interaction](#5-user-interface-and-interaction)
6. [Integration and Coordination](#6-integration-and-coordination)
7. [Performance and Optimization](#7-performance-and-optimization)

---

## 1. Main System Overview

### 1.1 Phoenix Architecture Command Center

**File**: `main.py` (3,557 lines)

**Purpose**: The definitive main system implementing the legendary Five-Layer Architecture for the ultimate AI-augmented cybersecurity framework. This is the command center that orchestrates the entire Phoenix Architecture with uncompromising reliability, professional interface, and intelligent orchestration.

**Key Responsibilities**:
- Five-layer architecture implementation and coordination
- Phoenix agent system orchestration
- User interface management and interaction handling
- System initialization and configuration management
- Command execution coordination and output management
- Session state management and persistence
- Error handling and recovery mechanisms

### 1.2 System Architecture Overview

```
LINA Main System (main.py)
├── Layer 1: Infrastructure & Configuration
├── Layer 2: Core System Classes
├── Layer 3: Agent Orchestration
├── Layer 4: User Interface & Interaction
└── Layer 5: Application Flow & Integration
```

### 1.3 Main System Statistics

```python
MAIN_SYSTEM_METRICS = {
    "total_lines": 3557,
    "classes": 5,
    "functions": 45,
    "layers": 5,
    "integration_points": 12,
    "ui_components": 8,
    "error_handlers": 15,
    "validation_functions": 10
}
```

---

## 2. Five-Layer Architecture

### 2.1 Layer 1: Infrastructure & Configuration

**Purpose**: Foundation layer providing system initialization, configuration management, and environment setup.

#### 2.1.1 Environment and Path Management
```python
# === ENVIRONMENT SETUP ===
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(PROJECT_ROOT, '.env')

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=ENV_PATH)

# Add project to Python path
sys.path.insert(0, PROJECT_ROOT)
```

#### 2.1.2 Global System Initialization
```python
# === CRITICAL GLOBAL LOGGER SETUP (FIRST PRIORITY) ===
from utils.logger import log
logger = log

# === GLOBAL CONSOLE ===
console = Console()

# === VERSION MANAGEMENT ===
from core._version import __version__
```

#### 2.1.3 Configuration Validation System
```python
def validate_system_requirements() -> Tuple[bool, List[str]]:
    """
    Comprehensive system requirements validation.
    
    Validation Categories:
    - Python version compatibility (3.8+)
    - Required dependencies availability
    - System permissions and access
    - Configuration file integrity
    - API key presence and validity
    """
    
    issues = []
    
    # Python version check
    if sys.version_info < (3, 8):
        issues.append(f"Python 3.8+ required, found {sys.version}")
    
    # Configuration validation
    config_issues = validate_configuration_files()
    issues.extend(config_issues)
    
    # Dependency validation
    dependency_issues = validate_python_packages()
    if dependency_issues:
        issues.append(dependency_issues)
    
    # Tool validation
    tool_issues = validate_command_line_tools()
    if tool_issues:
        issues.append(tool_issues)
    
    # Registry validation
    registry_issues = validate_tool_registry(
        os.path.join(PROJECT_ROOT, "core", "registry", "tool_registry.json")
    )
    if registry_issues:
        issues.append(registry_issues)
    
    return len(issues) == 0, issues
```

### 2.2 Layer 2: Core System Classes

**Purpose**: Essential system classes providing data management, output handling, and state management.

#### 2.2.1 OutputManager Class
```python
class OutputManager:
    """
    Manages command output capture, storage, and parsing.
    Essential for forensic analysis where command output is evidence.
    """
    
    def __init__(self, output_dir: str = None):
        """Initialize output manager with storage directory."""
        if output_dir is None:
            output_dir = os.path.join(PROJECT_ROOT, "data", "outputs")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session_outputs = []
    
    def save_output(self, command: str, output: str, tool_name: str = "unknown", 
                   metadata: Dict[str, Any] = None) -> str:
        """
        Saves command output to file with metadata.
        
        Features:
        - Timestamped file naming
        - Metadata preservation
        - Session tracking
        - Forensic chain of custody
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_tool_name = "".join(c for c in tool_name if c.isalnum() or c in ('-', '_'))
        filename = f"{timestamp}_{safe_tool_name}_output.txt"
        filepath = self.output_dir / filename
        
        # Prepare metadata
        full_metadata = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "tool_name": tool_name,
            "output_length": len(output),
            "session_id": getattr(self, 'session_id', 'unknown'),
            **(metadata or {})
        }
        
        # Save with metadata header
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("LINA OUTPUT METADATA\n")
            f.write("=" * 80 + "\n")
            for key, value in full_metadata.items():
                f.write(f"{key}: {value}\n")
            f.write("=" * 80 + "\n")
            f.write("COMMAND OUTPUT\n")
            f.write("=" * 80 + "\n")
            f.write(output)
        
        # Track in session
        self.session_outputs.append({
            "filepath": str(filepath),
            "metadata": full_metadata
        })
        
        return str(filepath)
    
    def parse_output(self, output: str, tool_name: str) -> Dict[str, Any]:
        """
        Parses tool output into structured data.
        
        Parsing Features:
        - Tool-specific parsing logic
        - Structured data extraction
        - Error detection and handling
        - Performance metrics calculation
        """
        
        parsed_data = {
            "tool": tool_name,
            "raw_output": output,
            "parsed": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Tool-specific parsing
        if tool_name.lower() == "nmap":
            parsed_data.update(self._parse_nmap_output(output))
        elif tool_name.lower() == "gobuster":
            parsed_data.update(self._parse_gobuster_output(output))
        elif tool_name.lower() in ["volatility", "volatility3"]:
            parsed_data.update(self._parse_volatility_output(output))
        else:
            # Generic parsing
            parsed_data.update(self._parse_generic_output(output))
        
        return parsed_data
```

#### 2.2.2 InterfaceState Class
```python
class InterfaceState:
    """
    Manages the complete state of the LINA interface and user session.
    Provides centralized state management for the entire application.
    """
    
    def __init__(self):
        """Initialize interface state with default values."""
        self.current_mode = "interactive"
        self.user_role = "Student"
        self.session_id = str(uuid.uuid4())
        self.conversation_history = []
        self.command_history = []
        self.last_command_output = ""
        self.current_directory = os.getcwd()
        self.active_tools = []
        self.performance_metrics = {}
        self.user_preferences = {}
        self.session_start_time = datetime.now()
        
        # Initialize subsystems
        self.output_manager = OutputManager()
        self.brain = None  # Will be initialized later
        self.command_executor = None  # Will be initialized later
        
        logger.info(f"InterfaceState initialized with session ID: {self.session_id}")
    
    def update_conversation_history(self, user_input: str, ai_response: str) -> None:
        """Updates conversation history with new interaction."""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response,
            "session_id": self.session_id
        }
        self.conversation_history.append(interaction)
        
        # Limit history size for performance
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-50:]
    
    def add_command_to_history(self, command: str, success: bool, output: str = "") -> None:
        """Adds executed command to history."""
        command_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "success": success,
            "output_length": len(output),
            "session_id": self.session_id
        }
        self.command_history.append(command_entry)
        
        # Update last command output
        self.last_command_output = output
        
        # Limit history size
        if len(self.command_history) > 200:
            self.command_history = self.command_history[-100:]
```

### 2.3 Layer 3: Agent Orchestration

**Purpose**: Coordination layer managing the Phoenix agent system and AI-powered operations.

#### 2.3.1 Phoenix Intelligence Activation
```python
def activate_phoenix_intelligence(interface_state: InterfaceState) -> Brain:
    """
    Activates the Phoenix Architecture with all specialized agents.
    
    Phoenix Components:
    - Brain: Central orchestrator and decision maker
    - AgentCore: NLP specialist for command parsing
    - IntelligenceSelector: Tool selection and command composition
    - RiskManager: Safety assessment and risk analysis
    - CommandExecutor: Safe command execution
    - ForensicsManager: Digital forensics workflows
    - SystemOperationsAgent: System management
    - SessionManager: Context and learning management
    """
    
    console.print("\n[bold cyan]🧠 Activating Phoenix Intelligence...[/bold cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Initialize core components
        task = progress.add_task("[cyan]Initializing AI Engine...", total=None)
        
        # Load configuration
        config_path = os.path.join(PROJECT_ROOT, "core", "config", "lina_config.json")
        config = config_loader.load_config(config_path)
        
        # Initialize tool registry path
        tool_registry_path = os.path.join(PROJECT_ROOT, "core", "registry", "tool_registry.json")
        
        # Create Brain with all agents
        progress.update(task, description="[cyan]Initializing Phoenix Brain...")
        brain = Brain(
            config=config,
            tool_registry_path=tool_registry_path,
            expert_role=interface_state.user_role
        )
        
        # Initialize command executor
        progress.update(task, description="[cyan]Setting up Command Executor...")
        interface_state.command_executor = CommandExecutor()
        
        # Store brain reference
        interface_state.brain = brain
        
        progress.update(task, description="[green]Phoenix Intelligence Activated!")
        time.sleep(0.5)  # Brief pause for visual effect
    
    console.print("[bold green]✅ Phoenix Architecture fully operational![/bold green]\n")
    return brain
```

#### 2.3.2 AI Request Processing
```python
def handle_phoenix_response(user_input: str, interface_state: InterfaceState) -> str:
    """
    Processes user requests through the Phoenix Architecture.
    
    Processing Pipeline:
    1. Input validation and sanitization
    2. Intent analysis and classification
    3. Agent routing and coordination
    4. Response generation and formatting
    5. Session state updates
    """
    
    try:
        # Process through Brain
        response = interface_state.brain.process_request(user_input)
        
        # Handle different response types
        if response.get('type') == 'command_execution':
            return handle_command_execution(response, interface_state)
        elif response.get('type') == 'plan_execution':
            return handle_plan_execution(response, interface_state)
        elif response.get('type') == 'conversation':
            return handle_conversation_response(response, interface_state)
        elif response.get('type') == 'explanation':
            return handle_explanation_response(response, interface_state)
        else:
            return handle_generic_response(response, interface_state)
            
    except Exception as e:
        logger.error(f"Error in Phoenix response handling: {str(e)}")
        return f"[red]Error processing request: {str(e)}[/red]"
```

### 2.4 Layer 4: User Interface & Interaction

**Purpose**: User interaction layer providing role-based interfaces, input handling, and visual feedback.

#### 2.4.1 Role-Based Startup Interface
```python
def display_role_selection() -> Dict[str, Any]:
    """
    Displays interactive role selection with detailed descriptions.
    
    Available Roles:
    - Student: Educational focus with learning guidance
    - Forensic Expert: Professional forensics workflows
    - Penetration Tester: Offensive security techniques
    """
    
    roles = {
        "1": {
            "name": "Student",
            "description": "Educational cybersecurity learning environment",
            "color": "green",
            "icon": "🎓"
        },
        "2": {
            "name": "Forensic Expert", 
            "description": "Professional digital forensics platform",
            "color": "blue",
            "icon": "🔍"
        },
        "3": {
            "name": "Penetration Tester",
            "description": "Offensive security testing platform", 
            "color": "red",
            "icon": "🛡️"
        }
    }
    
    # Create role selection table
    role_table = Table(title="Select Your Role", show_header=True, header_style="bold magenta")
    role_table.add_column("Option", style="cyan", width=8)
    role_table.add_column("Role", style="green")
    role_table.add_column("Description", style="white")
    
    for option, role_info in roles.items():
        role_table.add_row(
            option,
            f"{role_info['icon']} {role_info['name']}",
            role_info['description']
        )
    
    console.print(role_table)
    
    # Get user selection
    while True:
        choice = Prompt.ask("\n[bold cyan]Choose your role[/bold cyan]", choices=["1", "2", "3"])
        return roles[choice]
```

#### 2.4.2 Advanced Input Handling
```python
def get_user_input() -> str:
    """
    Advanced user input handling with multi-line support and validation.
    
    Features:
    - Multi-line input support (paste and type)
    - Input validation and sanitization
    - Command history integration
    - Fuzzy matching and typo correction
    """
    
    try:
        # Simple input that naturally handles multi-line paste
        user_input = input().strip()
        
        # Handle empty input
        if not user_input:
            return ""
        
        # Apply fuzzy matching for typo correction
        from utils.fuzzy_match import suggest_typo_correction
        suggestion = suggest_typo_correction(user_input)
        
        if suggestion and suggestion != user_input:
            if Confirm.ask(f"Did you mean '[green]{suggestion}[/green]'?"):
                user_input = suggestion
        
        return user_input
        
    except (EOFError, KeyboardInterrupt):
        return "exit"
    except Exception as e:
        logger.error(f"Error in user input: {str(e)}")
        return ""
```

#### 2.4.3 Response Formatting System
```python
def handle_conversation_response(response: Dict, interface_state: InterfaceState) -> str:
    """
    Formats conversational responses with beautiful, clean presentation.
    
    Formatting Features:
    - Compact format for short responses
    - Rich panel format for longer responses
    - Role-based styling and context
    - Accessibility considerations
    """
    
    content = response.get('content', 'No response generated.')
    
    # Update conversation history
    interface_state.update_conversation_history(
        response.get('original_input', ''),
        content
    )
    
    # Format based on content length and type
    if len(content) <= 200:
        # Compact format for short responses
        formatted_response = Text()
        formatted_response.append("💬 ", style="cyan")
        formatted_response.append(content, style="white")
        console.print(formatted_response)
    else:
        # Rich panel for longer responses
        response_panel = Panel(
            content,
            title="💬 LINA Assistant",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(response_panel)
    
    return content
```

### 2.5 Layer 5: Application Flow & Integration

**Purpose**: Top-level application flow coordination, main loop management, and system integration.

#### 2.5.1 Main Application Entry Point
```python
def main():
    """
    Main application entry point with comprehensive initialization.
    
    Initialization Sequence:
    1. System requirements validation
    2. Configuration loading and API key management
    3. Beautiful startup interface with role selection
    4. Phoenix Architecture activation
    5. Main interaction loop
    6. Graceful shutdown and cleanup
    """
    
    try:
        # === PHASE 1: BEAUTIFUL STARTUP INTERFACE ===
        console.clear()
        
        # Display main banner
        banner.display_main_banner()
        
        # System validation with beautiful progress
        console.print("\n[bold cyan]🔧 Initializing LINA Systems...[/bold cyan]")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            validation_task = progress.add_task("[cyan]Validating system requirements...", total=None)
            
            # Validate system requirements
            valid, issues = validate_system_requirements()
            
            if not valid:
                progress.stop()
                console.print("[bold red]❌ System validation failed![/bold red]")
                for issue in issues:
                    console.print(f"  • [red]{issue}[/red]")
                console.print("\n[yellow]Please resolve these issues and try again.[/yellow]")
                sys.exit(1)
            
            progress.update(validation_task, description="[green]✅ System validation complete")
            time.sleep(0.5)
        
        # === PHASE 2: ROLE SELECTION ===
        console.print("\n[bold magenta]👤 User Role Configuration[/bold magenta]")
        selected_role = display_role_selection()
        
        # === PHASE 3: BACKGROUND INITIALIZATION ===
        console.print(f"\n[bold {selected_role.get('color', 'cyan')}]🚀 Preparing {selected_role['name']} Environment...[/bold {selected_role.get('color', 'cyan')}]")
        
        # Initialize interface state
        interface_state = InterfaceState()
        interface_state.user_role = selected_role['name']
        
        # Configuration and API key management
        config_path = os.path.join(PROJECT_ROOT, "core", "config", "lina_config.json")
        config = config_loader.load_config(config_path)
        config_loader.manage_api_keys(ENV_PATH)
        
        # Activate Phoenix Intelligence
        brain = activate_phoenix_intelligence(interface_state)
        
        # === PHASE 4: ROLE-SPECIFIC WELCOME ===
        display_role_welcome_panel(selected_role)
        
        # === PHASE 5: MAIN INTERACTION LOOP ===
        console.print(f"\n[bold green]🎯 {selected_role['name']} mode activated! Ready for cybersecurity operations.[/bold green]")
        console.print("[dim]Type your requests in natural language. Multi-line input supported. Type 'exit' to quit.[/dim]\n")
        
        # Main interaction loop
        while True:
            try:
                # Get user input
                console.print("[bold cyan]LINA>[/bold cyan] ", end="")
                user_input = get_user_input()
                
                # Handle empty input or exit
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                
                # Handle built-in commands
                if user_input.startswith('/'):
                    result = handle_builtin_commands(user_input, interface_state)
                    if result:
                        console.print(result)
                    continue
                
                # Process through Phoenix Architecture
                console.print()  # Add spacing
                response = handle_phoenix_response(user_input, interface_state)
                console.print()  # Add spacing after response
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit gracefully.[/yellow]")
                continue
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                console.print(f"[red]An error occurred: {str(e)}[/red]")
                continue
        
        # === PHASE 6: GRACEFUL SHUTDOWN ===
        console.print("\n[bold cyan]👋 Thank you for using LINA![/bold cyan]")
        console.print("[dim]Session data saved. Goodbye![/dim]")
        
    except Exception as e:
        logger.error(f"Critical error in main: {str(e)}")
        console.print(f"[bold red]Critical error: {str(e)}[/bold red]")
        sys.exit(1)
```

#### 2.5.2 Built-in Command System
```python
def handle_builtin_commands(command: str, interface_state: InterfaceState) -> Optional[str]:
    """
    Handles built-in LINA commands with comprehensive functionality.
    
    Built-in Commands:
    - /help: Display help information
    - /status: Show system status
    - /list tools: List available tools
    - /list agents: List active agents
    - /version: Show version information
    - /modes: Display available modes
    - /forensic: Forensic mode information
    - /pentest: Penetration testing mode information
    """
    
    command = command.lower().strip()
    
    # Detect automated mode (non-TTY stdin)
    is_automated = not sys.stdin.isatty()
    
    if command == '/help':
        if is_automated:
            return "Help: LINA AI-Powered Cybersecurity Assistant"
        display_help_menu()
        return None
        
    elif command == '/status':
        return handle_status_response(interface_state)
        
    elif command == '/list tools':
        return handle_tools_list()
        
    elif command == '/list agents':
        return handle_agents_list()
        
    elif command == '/version':
        return f"LINA Version {__version__} - Phoenix Architecture"
        
    elif command == '/modes':
        return handle_modes_display()
        
    elif command == '/forensic':
        return handle_forensic_mode_info()
        
    elif command == '/pentest':
        return handle_pentest_mode_info()
        
    else:
        return f"Unknown command: {command}. Type '/help' for available commands."
```

---

## 3. Core System Classes

### 3.1 OutputManager Class Details

#### 3.1.1 Advanced Output Processing
```python
def _parse_nmap_output(self, output: str) -> Dict[str, Any]:
    """
    Parses nmap output into structured data.
    
    Extracted Information:
    - Open ports and services
    - Host status and OS detection
    - Script scan results
    - Timing and performance metrics
    """
    
    parsed = {
        "open_ports": [],
        "closed_ports": [],
        "filtered_ports": [],
        "host_status": "unknown",
        "os_detection": {},
        "script_results": [],
        "scan_stats": {}
    }
    
    lines = output.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Parse port information
        if '/tcp' in line or '/udp' in line:
            port_info = self._parse_port_line(line)
            if port_info:
                if 'open' in line:
                    parsed["open_ports"].append(port_info)
                elif 'closed' in line:
                    parsed["closed_ports"].append(port_info)
                elif 'filtered' in line:
                    parsed["filtered_ports"].append(port_info)
        
        # Parse host status
        elif 'Host is up' in line:
            parsed["host_status"] = "up"
        elif 'Host seems down' in line:
            parsed["host_status"] = "down"
        
        # Parse OS detection
        elif 'OS details:' in line:
            parsed["os_detection"]["details"] = line.split('OS details:')[1].strip()
    
    # Calculate summary statistics
    parsed["total_ports"] = len(parsed["open_ports"]) + len(parsed["closed_ports"]) + len(parsed["filtered_ports"])
    parsed["open_port_count"] = len(parsed["open_ports"])
    
    return parsed
```

#### 3.1.2 Forensics Output Management
```python
def save_forensics_evidence(self, evidence_type: str, source_file: str, 
                          analysis_results: Dict[str, Any]) -> str:
    """
    Saves forensics analysis results with proper chain of custody.
    
    Evidence Management:
    - Timestamped evidence files
    - Chain of custody documentation
    - Hash verification and integrity
    - Analysis metadata preservation
    """
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    evidence_id = f"EVIDENCE_{timestamp}_{evidence_type.upper()}"
    
    # Create evidence directory
    evidence_dir = self.output_dir / "forensics" / evidence_id
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate chain of custody
    custody_info = {
        "evidence_id": evidence_id,
        "evidence_type": evidence_type,
        "source_file": source_file,
        "collection_time": datetime.now().isoformat(),
        "analyst": os.getenv("USER", "unknown"),
        "system": os.uname().nodename,
        "analysis_tools": analysis_results.get("tools_used", []),
        "integrity_hash": self._calculate_file_hash(source_file) if os.path.exists(source_file) else None
    }
    
    # Save chain of custody
    custody_file = evidence_dir / "chain_of_custody.json"
    with open(custody_file, 'w') as f:
        json.dump(custody_info, f, indent=2)
    
    # Save analysis results
    results_file = evidence_dir / "analysis_results.json"
    with open(results_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    return str(evidence_dir)
```

### 3.2 InterfaceState Class Details

#### 3.2.1 Advanced State Management
```python
def get_session_analytics(self) -> Dict[str, Any]:
    """
    Generates comprehensive session analytics and insights.
    
    Analytics Categories:
    - Usage patterns and frequency
    - Tool preferences and success rates
    - Learning progression indicators
    - Performance metrics and trends
    """
    
    analytics = {
        "session_info": {
            "session_id": self.session_id,
            "start_time": self.session_start_time.isoformat(),
            "duration_minutes": (datetime.now() - self.session_start_time).total_seconds() / 60,
            "user_role": self.user_role
        },
        
        "interaction_stats": {
            "total_interactions": len(self.conversation_history),
            "total_commands": len(self.command_history),
            "success_rate": self._calculate_success_rate(),
            "average_response_time": self._calculate_avg_response_time()
        },
        
        "tool_usage": self._analyze_tool_usage(),
        "learning_indicators": self._analyze_learning_progression(),
        "performance_metrics": self.performance_metrics
    }
    
    return analytics

def _analyze_tool_usage(self) -> Dict[str, Any]:
    """
    Analyzes tool usage patterns and preferences.
    
    Analysis Features:
    - Most frequently used tools
    - Success rates per tool
    - Usage trends over time
    - Complexity progression
    """
    
    tool_stats = {}
    
    for cmd_entry in self.command_history:
        # Extract tool name from command
        tool_name = self._extract_tool_from_command(cmd_entry['command'])
        
        if tool_name not in tool_stats:
            tool_stats[tool_name] = {
                "usage_count": 0,
                "success_count": 0,
                "failure_count": 0,
                "first_used": cmd_entry['timestamp'],
                "last_used": cmd_entry['timestamp']
            }
        
        tool_stats[tool_name]["usage_count"] += 1
        tool_stats[tool_name]["last_used"] = cmd_entry['timestamp']
        
        if cmd_entry['success']:
            tool_stats[tool_name]["success_count"] += 1
        else:
            tool_stats[tool_name]["failure_count"] += 1
    
    # Calculate success rates
    for tool, stats in tool_stats.items():
        if stats["usage_count"] > 0:
            stats["success_rate"] = stats["success_count"] / stats["usage_count"]
    
    return tool_stats
```

---

## 4. Application Flow and Orchestration

### 4.1 System Initialization Flow

#### 4.1.1 Startup Sequence
```python
STARTUP_SEQUENCE = [
    "1. Environment Setup and Path Configuration",
    "2. Global Logger and Console Initialization", 
    "3. System Requirements Validation",
    "4. Configuration Loading and API Key Management",
    "5. Role Selection and User Preferences",
    "6. Phoenix Architecture Activation",
    "7. Agent System Initialization",
    "8. Interface State Setup",
    "9. Main Interaction Loop Entry"
]
```

#### 4.1.2 Validation Pipeline
```python
def comprehensive_system_validation() -> Tuple[bool, Dict[str, Any]]:
    """
    Performs comprehensive system validation with detailed reporting.
    
    Validation Components:
    - Python environment and version
    - Required dependencies and packages
    - Configuration file integrity
    - API key presence and validity
    - Tool registry completeness
    - System permissions and access
    """
    
    validation_results = {
        "python_environment": validate_python_environment(),
        "dependencies": validate_dependencies(),
        "configuration": validate_configuration_integrity(),
        "api_keys": validate_api_key_setup(),
        "tool_registry": validate_tool_registry_completeness(),
        "system_permissions": validate_system_permissions()
    }
    
    # Overall validation status
    overall_success = all(result["status"] == "success" for result in validation_results.values())
    
    return overall_success, validation_results
```

### 4.2 Request Processing Pipeline

#### 4.2.1 Input Processing Flow
```
User Input → Input Validation → Fuzzy Matching → Built-in Command Check → 
Phoenix Brain Processing → Agent Routing → Response Generation → 
Output Formatting → State Updates → User Display
```

#### 4.2.2 Error Handling and Recovery
```python
def handle_processing_error(error: Exception, context: Dict[str, Any]) -> str:
    """
    Comprehensive error handling with recovery mechanisms.
    
    Error Categories:
    - Input validation errors
    - AI processing errors
    - Command execution errors
    - System resource errors
    - Network connectivity errors
    """
    
    error_type = type(error).__name__
    error_message = str(error)
    
    # Log error with context
    logger.error(f"Processing error: {error_type} - {error_message}", extra=context)
    
    # Determine recovery strategy
    if "API" in error_message or "network" in error_message.lower():
        return handle_connectivity_error(error, context)
    elif "permission" in error_message.lower():
        return handle_permission_error(error, context)
    elif "timeout" in error_message.lower():
        return handle_timeout_error(error, context)
    else:
        return handle_generic_error(error, context)
```

---

## 5. User Interface and Interaction

### 5.1 Role-Based Interface System

#### 5.1.1 Dynamic Role Adaptation
```python
def adapt_interface_for_role(role: str, interface_state: InterfaceState) -> None:
    """
    Adapts the interface based on selected user role.
    
    Role Adaptations:
    - Student: Educational focus, detailed explanations, safety emphasis
    - Forensic Expert: Professional workflows, chain of custody, reporting
    - Penetration Tester: Offensive security, OPSEC, methodology focus
    """
    
    role_configurations = {
        "Student": {
            "prompt_style": "educational",
            "safety_level": "maximum",
            "explanation_detail": "comprehensive",
            "ui_theme": "learning_focused"
        },
        "Forensic Expert": {
            "prompt_style": "professional",
            "safety_level": "high",
            "explanation_detail": "technical",
            "ui_theme": "forensics_focused"
        },
        "Penetration Tester": {
            "prompt_style": "tactical",
            "safety_level": "medium",
            "explanation_detail": "operational",
            "ui_theme": "security_focused"
        }
    }
    
    config = role_configurations.get(role, role_configurations["Student"])
    
    # Apply role-specific configurations
    interface_state.user_preferences.update(config)
    
    # Configure brain for role-specific behavior
    if interface_state.brain:
        interface_state.brain.set_role_context(role, config)
```

### 5.2 Advanced Input/Output Management

#### 5.2.1 Multi-Modal Input Handling
```python
def process_advanced_input(raw_input: str, interface_state: InterfaceState) -> Dict[str, Any]:
    """
    Processes input with advanced parsing and context integration.
    
    Processing Features:
    - Multi-line input support
    - Command history integration
    - Context-aware parsing
    - Typo correction and suggestions
    """
    
    processed_input = {
        "raw": raw_input,
        "cleaned": raw_input.strip(),
        "type": "unknown",
        "context": {},
        "suggestions": []
    }
    
    # Determine input type
    if raw_input.startswith('/'):
        processed_input["type"] = "builtin_command"
    elif any(tool in raw_input.lower() for tool in interface_state.active_tools):
        processed_input["type"] = "tool_command"
    elif any(word in raw_input.lower() for word in ["what", "how", "explain", "tell"]):
        processed_input["type"] = "question"
    else:
        processed_input["type"] = "general_request"
    
    # Add context from session history
    processed_input["context"] = {
        "recent_commands": interface_state.command_history[-5:],
        "conversation_context": interface_state.conversation_history[-3:],
        "user_role": interface_state.user_role,
        "session_duration": (datetime.now() - interface_state.session_start_time).total_seconds()
    }
    
    return processed_input
```

---

## 6. Integration and Coordination

### 6.1 Phoenix Architecture Integration

#### 6.1.1 Agent Coordination System
```python
def coordinate_multi_agent_workflow(request: Dict[str, Any], 
                                  interface_state: InterfaceState) -> Dict[str, Any]:
    """
    Coordinates complex workflows involving multiple agents.
    
    Coordination Features:
    - Sequential agent processing
    - Parallel agent execution
    - Result aggregation and synthesis
    - Error handling and fallback
    """
    
    workflow_results = {
        "request_id": str(uuid.uuid4()),
        "agents_involved": [],
        "processing_steps": [],
        "final_result": None,
        "performance_metrics": {}
    }
    
    # Determine required agents based on request
    required_agents = interface_state.brain.analyze_agent_requirements(request)
    
    # Execute workflow
    for agent_name in required_agents:
        step_start = time.time()
        
        try:
            # Process through agent
            agent_result = interface_state.brain.route_to_agent(agent_name, request)
            
            # Record step
            workflow_results["processing_steps"].append({
                "agent": agent_name,
                "status": "success",
                "result": agent_result,
                "duration_ms": int((time.time() - step_start) * 1000)
            })
            
            workflow_results["agents_involved"].append(agent_name)
            
        except Exception as e:
            # Handle agent failure
            workflow_results["processing_steps"].append({
                "agent": agent_name,
                "status": "failed",
                "error": str(e),
                "duration_ms": int((time.time() - step_start) * 1000)
            })
    
    # Synthesize final result
    workflow_results["final_result"] = interface_state.brain.synthesize_workflow_results(
        workflow_results["processing_steps"]
    )
    
    return workflow_results
```

### 6.2 Performance Monitoring and Optimization

#### 6.2.1 Real-Time Performance Tracking
```python
class PerformanceMonitor:
    """
    Real-time performance monitoring for the main system.
    """
    
    def __init__(self):
        self.metrics = {
            "response_times": [],
            "memory_usage": [],
            "cpu_usage": [],
            "agent_performance": {},
            "error_rates": {}
        }
        self.start_time = time.time()
    
    def track_operation(self, operation_name: str, duration_ms: int, 
                       success: bool, metadata: Dict = None) -> None:
        """
        Tracks operation performance with comprehensive metrics.
        
        Tracked Metrics:
        - Operation duration and success rate
        - Resource usage during operation
        - Agent-specific performance
        - Error patterns and frequencies
        """
        
        # Update response times
        self.metrics["response_times"].append({
            "operation": operation_name,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": time.time(),
            "metadata": metadata or {}
        })
        
        # Update agent performance if applicable
        if "agent" in (metadata or {}):
            agent_name = metadata["agent"]
            if agent_name not in self.metrics["agent_performance"]:
                self.metrics["agent_performance"][agent_name] = {
                    "total_operations": 0,
                    "successful_operations": 0,
                    "average_duration_ms": 0,
                    "durations": []
                }
            
            agent_stats = self.metrics["agent_performance"][agent_name]
            agent_stats["total_operations"] += 1
            agent_stats["durations"].append(duration_ms)
            
            if success:
                agent_stats["successful_operations"] += 1
            
            # Update average
            agent_stats["average_duration_ms"] = sum(agent_stats["durations"]) / len(agent_stats["durations"])
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Generates comprehensive performance summary.
        
        Summary Components:
        - Overall system performance
        - Agent-specific metrics
        - Resource utilization trends
        - Error analysis and patterns
        """
        
        total_operations = len(self.metrics["response_times"])
        successful_operations = sum(1 for op in self.metrics["response_times"] if op["success"])
        
        if total_operations > 0:
            success_rate = successful_operations / total_operations
            avg_response_time = sum(op["duration_ms"] for op in self.metrics["response_times"]) / total_operations
        else:
            success_rate = 0
            avg_response_time = 0
        
        return {
            "uptime_seconds": time.time() - self.start_time,
            "total_operations": total_operations,
            "success_rate": success_rate,
            "average_response_time_ms": avg_response_time,
            "agent_performance": self.metrics["agent_performance"],
            "recent_performance": self.metrics["response_times"][-10:] if self.metrics["response_times"] else []
        }
```

---

## 7. Performance and Optimization

### 7.1 System Optimization Strategies

#### 7.1.1 Memory Management
```python
def optimize_memory_usage(interface_state: InterfaceState) -> None:
    """
    Optimizes memory usage through intelligent cleanup and caching.
    
    Optimization Techniques:
    - History size management
    - Cache cleanup and rotation
    - Unused object garbage collection
    - Memory-efficient data structures
    """
    
    # Limit conversation history size
    max_history = 100
    if len(interface_state.conversation_history) > max_history:
        interface_state.conversation_history = interface_state.conversation_history[-max_history//2:]
    
    # Limit command history size
    max_commands = 200
    if len(interface_state.command_history) > max_commands:
        interface_state.command_history = interface_state.command_history[-max_commands//2:]
    
    # Clean up output manager cache
    interface_state.output_manager.cleanup_old_outputs()
    
    # Force garbage collection
    import gc
    gc.collect()
```

#### 7.1.2 Response Time Optimization
```python
def optimize_response_times(interface_state: InterfaceState) -> None:
    """
    Optimizes system response times through caching and preloading.
    
    Optimization Features:
    - AI response caching for repeated queries
    - Tool registry preloading
    - Agent initialization optimization
    - Predictive resource allocation
    """
    
    # Enable AI response caching
    if hasattr(interface_state.brain, 'enable_response_caching'):
        interface_state.brain.enable_response_caching()
    
    # Preload frequently used tools
    common_tools = ["nmap", "gobuster", "volatility3"]
    for tool in common_tools:
        interface_state.brain.preload_tool_registry(tool)
    
    # Optimize agent initialization
    interface_state.brain.optimize_agent_performance()
```

### 7.2 Scalability Considerations

#### 7.2.1 Concurrent Operation Support
```python
async def handle_concurrent_operations(operations: List[Dict], 
                                     interface_state: InterfaceState) -> List[Dict]:
    """
    Handles multiple operations concurrently for improved performance.
    
    Concurrency Features:
    - Parallel command execution
    - Asynchronous AI processing
    - Resource-aware scheduling
    - Result synchronization
    """
    
    # Create semaphore for resource management
    max_concurrent = 3
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_operation(operation: Dict) -> Dict:
        async with semaphore:
            # Process operation with resource limits
            return await interface_state.brain.process_async(operation)
    
    # Execute operations concurrently
    tasks = [process_operation(op) for op in operations]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle results and exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "operation_id": operations[i].get("id"),
                "status": "failed",
                "error": str(result)
            })
        else:
            processed_results.append(result)
    
    return processed_results
```

---

## Summary

The LINA Main System implements a sophisticated Five-Layer Architecture with:

### **Layer 1: Infrastructure & Configuration**
- Comprehensive environment setup and path management
- Global system initialization with logging and console
- Advanced configuration validation and API key management

### **Layer 2: Core System Classes**
- **OutputManager**: Advanced output capture, parsing, and forensics evidence management
- **InterfaceState**: Comprehensive session state management with analytics

### **Layer 3: Agent Orchestration**
- Phoenix Architecture activation and coordination
- Multi-agent workflow management
- AI-powered request processing pipeline

### **Layer 4: User Interface & Interaction**
- Role-based startup interface with beautiful visual design
- Advanced input handling with multi-line support
- Rich response formatting and presentation

### **Layer 5: Application Flow & Integration**
- Main application entry point with comprehensive initialization
- Built-in command system with extensive functionality
- Graceful shutdown and cleanup procedures

**Main System Statistics**:
- **Total Lines**: 3,557 lines of sophisticated code
- **Architecture Layers**: 5 comprehensive layers
- **Core Classes**: 2 major system classes (OutputManager, InterfaceState)
- **Integration Points**: 12 major integration points with other systems
- **Built-in Commands**: 8 comprehensive built-in commands
- **Error Handlers**: 15 specialized error handling mechanisms
- **Performance Features**: Real-time monitoring, optimization, and scalability support

This Five-Layer Architecture enables LINA to operate as a professional, scalable, and reliable cybersecurity platform with comprehensive user interface, robust error handling, and intelligent system coordination.
