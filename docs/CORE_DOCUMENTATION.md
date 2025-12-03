# LINA Core System Documentation
## Foundation Components and Data Management Systems

---

## Table of Contents

1. [Core System Overview](#1-core-system-overview)
2. [Configuration Management](#2-configuration-management)
3. [Tool Registry System](#3-tool-registry-system)
4. [Individual Tool Registries](#4-individual-tool-registries)
5. [Risk Database System](#5-risk-database-system)
6. [Version Management](#6-version-management)
7. [Data Storage Architecture](#7-data-storage-architecture)

---

## 1. Core System Overview

### 1.1 Core Architecture

The LINA Core system provides the foundational data structures, configuration management, and knowledge bases that power the entire platform. It serves as the central repository for:

- **System Configuration**: Application settings and parameters
- **Tool Knowledge**: Comprehensive database of 82+ cybersecurity tools
- **Risk Intelligence**: 102+ dangerous command patterns and safety rules
- **Version Control**: System versioning and compatibility management

### 1.2 Core Directory Structure

```
core/
├── config/                    # Configuration Management
│   └── lina_config.json      # Main system configuration
├── registry/                  # Core Data Systems
│   ├── tool_registry.json    # Master tool database (82+ tools)
│   └── risk_database.json    # Risk patterns and assessments (102+ patterns)
├── registries/               # Individual Tool Registries (76+ files)
│   ├── nmap_registry.json    # Network mapping tool registry
│   ├── gobuster_registry.json # Directory enumeration tool registry
│   ├── volatility3_registry.json # Memory forensics tool registry
│   └── ... (73+ more specialized registries)
├── config.yaml              # Alternative configuration format
└── _version.py              # Version management system
```

### 1.3 Core System Responsibilities

```python
class CoreSystem:
    """
    Central management system for LINA's foundational components.
    """
    
    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.tool_registry = ToolRegistryManager()
        self.risk_database = RiskDatabaseManager()
        self.version_manager = VersionManager()
    
    def initialize_core_systems(self) -> bool:
        """
        Initializes all core system components with validation.
        
        Initialization Order:
        1. Version validation and compatibility check
        2. Configuration loading and validation
        3. Tool registry loading and indexing
        4. Risk database loading and pattern compilation
        5. Cross-system validation and integrity checks
        """
```

---

## 2. Configuration Management

### 2.1 Main Configuration (lina_config.json)

**Purpose**: Central configuration file containing system-wide settings, AI parameters, and operational preferences.

**File Location**: `core/config/lina_config.json`

**Configuration Structure**:

```json
{
  "system": {
    "name": "LINA",
    "version": "2.0.0",
    "description": "AI-Powered Cybersecurity Assistant",
    "debug_mode": false,
    "log_level": "INFO"
  },
  
  "ai": {
    "provider": "gemini",
    "model": "gemini-pro",
    "temperature": 0.1,
    "max_tokens": 4096,
    "timeout": 30,
    "retry_attempts": 3
  },
  
  "security": {
    "risk_assessment_enabled": true,
    "user_confirmation_required": true,
    "high_risk_blocking": true,
    "audit_logging": true
  },
  
  "execution": {
    "default_timeout": 30,
    "max_concurrent_commands": 3,
    "resource_monitoring": true,
    "sandbox_mode": false
  },
  
  "ui": {
    "theme": "cybersec",
    "show_banners": true,
    "verbose_output": true,
    "color_enabled": true
  },
  
  "paths": {
    "tool_registry": "core/registry/tool_registry.json",
    "risk_database": "core/registry/risk_database.json",
    "individual_registries": "core/registries/",
    "log_directory": "data/logs/",
    "output_directory": "data/outputs/"
  }
}
```

### 2.2 Configuration Management System

#### 2.2.1 Configuration Loader
```python
class ConfigurationManager:
    """
    Advanced configuration management with validation and hierarchy support.
    """
    
    def load_configuration(self, config_path: str) -> Dict[str, Any]:
        """
        Loads and validates system configuration with hierarchy support.
        
        Configuration Hierarchy:
        1. Default configuration (hardcoded fallbacks)
        2. System configuration (lina_config.json)
        3. User configuration (.env overrides)
        4. Runtime configuration (command-line arguments)
        """
        
    def validate_configuration(self, config: Dict) -> Tuple[bool, List[str]]:
        """
        Comprehensive configuration validation.
        
        Validation Checks:
        - Required fields presence
        - Data type validation
        - Value range validation
        - Path existence validation
        - Cross-field dependency validation
        """
```

#### 2.2.2 Dynamic Configuration Updates
```python
def update_configuration(self, section: str, key: str, value: Any) -> bool:
    """
    Runtime configuration updates with validation.
    
    Features:
    - Hot configuration reloading
    - Validation before application
    - Rollback on failure
    - Change notification to dependent systems
    """
```

### 2.3 Alternative Configuration (config.yaml)

**Purpose**: YAML-based configuration for users who prefer YAML syntax over JSON.

**Features**:
- Human-readable format with comments
- Hierarchical structure support
- Environment variable interpolation
- Include file support for modular configuration

---

## 3. Tool Registry System

### 3.1 Master Tool Registry (tool_registry.json)

**Purpose**: Comprehensive database of all 82+ cybersecurity tools integrated into LINA.

**File Location**: `core/registry/tool_registry.json`

**Registry Structure**:

```json
{
  "nmap": {
    "name": "nmap",
    "description": "Network discovery and port scanning tool",
    "category": "network_security",
    "keywords": ["scan", "port", "network", "discovery", "reconnaissance"],
    "risk_level": "low",
    "installation": {
      "apt": "nmap",
      "brew": "nmap",
      "pacman": "nmap"
    },
    "examples": [
      "nmap -sS target.com",
      "nmap -sV -sC target.com",
      "nmap -p- target.com"
    ]
  },
  
  "gobuster": {
    "name": "gobuster",
    "description": "Directory and file enumeration tool",
    "category": "web_security",
    "keywords": ["directory", "enumeration", "web", "brute force"],
    "risk_level": "low",
    "installation": {
      "apt": "gobuster",
      "go": "github.com/OJ/gobuster/v3@latest"
    },
    "examples": [
      "gobuster dir -u http://target.com -w wordlist.txt",
      "gobuster dns -d target.com -w subdomains.txt"
    ]
  }
}
```

### 3.2 Tool Categories and Classification

#### 3.2.1 Network Security Tools
```json
{
  "network_security": {
    "tools": ["nmap", "masscan", "rustscan", "arp-scan"],
    "description": "Network discovery, port scanning, and reconnaissance",
    "risk_levels": ["low", "medium"],
    "common_use_cases": [
      "Network discovery and mapping",
      "Port scanning and service enumeration",
      "Network security assessment"
    ]
  }
}
```

#### 3.2.2 Web Security Tools
```json
{
  "web_security": {
    "tools": ["gobuster", "dirb", "wfuzz", "sqlmap", "nikto", "wpscan"],
    "description": "Web application security testing and analysis",
    "risk_levels": ["low", "medium", "high"],
    "common_use_cases": [
      "Directory and file enumeration",
      "SQL injection testing",
      "Web vulnerability scanning"
    ]
  }
}
```

#### 3.2.3 Digital Forensics Tools
```json
{
  "digital_forensics": {
    "tools": ["volatility3", "foremost", "autopsy", "sleuthkit", "binwalk"],
    "description": "Digital evidence analysis and investigation",
    "risk_levels": ["low", "medium"],
    "common_use_cases": [
      "Memory dump analysis",
      "File carving and recovery",
      "Timeline analysis and reconstruction"
    ]
  }
}
```

### 3.3 Tool Registry Management

#### 3.3.1 Registry Loading and Indexing
```python
class ToolRegistryManager:
    """
    Advanced tool registry management with indexing and search capabilities.
    """
    
    def load_tool_registry(self, registry_path: str) -> Dict[str, Any]:
        """
        Loads and indexes the master tool registry.
        
        Indexing Features:
        - Keyword-based search index
        - Category-based classification
        - Risk level grouping
        - Installation method mapping
        """
        
    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """
        Intelligent tool search with fuzzy matching.
        
        Search Features:
        - Keyword matching with scoring
        - Category-based filtering
        - Fuzzy string matching
        - Relevance ranking
        """
```

#### 3.3.2 Tool Validation and Verification
```python
def validate_tool_availability(self, tool_name: str) -> Dict[str, Any]:
    """
    Validates tool availability and installation status.
    
    Validation Checks:
    - Binary existence in PATH
    - Version compatibility
    - Dependency satisfaction
    - Permission requirements
    """
```

---

## 4. Individual Tool Registries

### 4.1 Registry Architecture

**Purpose**: Detailed specifications for each individual tool, providing comprehensive parameter definitions, usage examples, and safety guidelines.

**Location**: `core/registries/`

**Registry Count**: 76+ individual tool registries

### 4.2 Individual Registry Structure

#### 4.2.1 Network Tools Registry Example (nmap_registry.json)

```json
{
  "tool_info": {
    "name": "nmap",
    "full_name": "Network Mapper",
    "version_support": "7.0+",
    "official_website": "https://nmap.org",
    "documentation": "https://nmap.org/book/"
  },
  
  "parameters": {
    "scan_types": {
      "-sS": {
        "description": "TCP SYN scan (stealth scan)",
        "risk_level": "low",
        "requires_root": true,
        "example": "nmap -sS target.com"
      },
      "-sT": {
        "description": "TCP connect scan",
        "risk_level": "low", 
        "requires_root": false,
        "example": "nmap -sT target.com"
      },
      "-sU": {
        "description": "UDP scan",
        "risk_level": "medium",
        "requires_root": true,
        "example": "nmap -sU target.com"
      }
    },
    
    "timing_templates": {
      "-T0": "Paranoid (very slow)",
      "-T1": "Sneaky (slow)",
      "-T2": "Polite (slower)",
      "-T3": "Normal (default)",
      "-T4": "Aggressive (faster)",
      "-T5": "Insane (very fast)"
    },
    
    "output_formats": {
      "-oN": "Normal output to file",
      "-oX": "XML output to file",
      "-oG": "Grepable output to file",
      "-oA": "All formats to file"
    }
  },
  
  "common_combinations": [
    {
      "command": "nmap -sS -T4 -p- target.com",
      "description": "Fast comprehensive port scan",
      "use_case": "Initial reconnaissance"
    },
    {
      "command": "nmap -sV -sC -O target.com",
      "description": "Service version detection with default scripts",
      "use_case": "Service enumeration"
    }
  ],
  
  "safety_guidelines": [
    "Always ensure you have permission to scan the target",
    "Use appropriate timing templates to avoid detection",
    "Be mindful of network load and target system resources",
    "Consider legal and ethical implications"
  ]
}
```

#### 4.2.2 Forensics Tools Registry Example (volatility3_registry.json)

```json
{
  "tool_info": {
    "name": "volatility3",
    "full_name": "Volatility Framework 3",
    "category": "memory_forensics",
    "version_support": "3.0+",
    "python_requirement": "3.6+"
  },
  
  "plugins": {
    "windows": {
      "windows.pslist": {
        "description": "List running processes",
        "output_format": "table",
        "example": "volatility3 -f memory.dmp windows.pslist"
      },
      "windows.pstree": {
        "description": "Show process tree",
        "output_format": "tree",
        "example": "volatility3 -f memory.dmp windows.pstree"
      },
      "windows.netstat": {
        "description": "Show network connections",
        "output_format": "table",
        "example": "volatility3 -f memory.dmp windows.netstat"
      }
    },
    
    "linux": {
      "linux.pslist": {
        "description": "List running processes (Linux)",
        "output_format": "table",
        "example": "volatility3 -f memory.dmp linux.pslist"
      }
    }
  },
  
  "workflows": {
    "basic_analysis": [
      "volatility3 -f memory.dmp windows.info",
      "volatility3 -f memory.dmp windows.pslist",
      "volatility3 -f memory.dmp windows.pstree",
      "volatility3 -f memory.dmp windows.netstat"
    ],
    
    "malware_analysis": [
      "volatility3 -f memory.dmp windows.malfind",
      "volatility3 -f memory.dmp windows.hollowfind",
      "volatility3 -f memory.dmp windows.injections"
    ]
  }
}
```

### 4.3 Registry Categories

#### 4.3.1 Network Security Registries
- **nmap_registry.json**: Network mapping and port scanning
- **masscan_registry.json**: High-speed port scanning
- **rustscan_registry.json**: Fast port scanner written in Rust
- **arp-scan_registry.json**: ARP network discovery

#### 4.3.2 Web Security Registries
- **gobuster_registry.json**: Directory and DNS enumeration
- **dirb_registry.json**: Web content scanner
- **wfuzz_registry.json**: Web application fuzzer
- **sqlmap_registry.json**: SQL injection testing tool
- **nikto_registry.json**: Web vulnerability scanner

#### 4.3.3 Digital Forensics Registries
- **volatility3_registry.json**: Memory forensics framework
- **foremost_registry.json**: File carving tool
- **autopsy_registry.json**: Digital forensics platform
- **sleuthkit_registry.json**: Forensics toolkit
- **binwalk_registry.json**: Firmware analysis tool

#### 4.3.4 System Tools Registries
- **curl_registry.json**: HTTP client tool
- **wget_registry.json**: File download utility
- **netcat_registry.json**: Network utility
- **tcpdump_registry.json**: Network packet analyzer

### 4.4 Registry Management System

#### 4.4.1 Individual Registry Loader
```python
class IndividualRegistryManager:
    """
    Management system for individual tool registries.
    """
    
    def load_tool_registry(self, tool_name: str) -> Dict[str, Any]:
        """
        Loads detailed registry for a specific tool.
        
        Loading Features:
        - Automatic registry file detection
        - Schema validation
        - Parameter normalization
        - Example validation
        """
        
    def get_tool_parameters(self, tool_name: str) -> Dict[str, Any]:
        """
        Extracts parameter definitions for intelligent command generation.
        
        Parameter Types:
        - Required parameters
        - Optional parameters with defaults
        - Mutually exclusive options
        - Parameter validation rules
        """
```

#### 4.4.2 Registry Validation System
```python
def validate_registry_schema(self, registry_data: Dict) -> Tuple[bool, List[str]]:
    """
    Validates individual registry against schema requirements.
    
    Validation Checks:
    - Required sections presence
    - Parameter format validation
    - Example command syntax validation
    - Safety guideline completeness
    """
```

---

## 5. Risk Database System

### 5.1 Risk Database (risk_database.json)

**Purpose**: Comprehensive database of 102+ dangerous command patterns and safety assessments for cybersecurity operations.

**File Location**: `core/registry/risk_database.json`

**Database Structure**:

```json
{
  "critical_risks": {
    "rm -rf /": {
      "risk_level": "critical",
      "description": "Complete system file deletion",
      "impact": "Total system destruction, unrecoverable data loss",
      "detection_pattern": "rm\\s+-rf\\s+/",
      "alternatives": [
        "Use specific directory paths instead of root",
        "Use trash/recycle bin commands for safety",
        "Create backups before deletion operations"
      ],
      "prevention": "Block execution, require explicit confirmation"
    },
    
    "dd if=/dev/zero of=/dev/sda": {
      "risk_level": "critical",
      "description": "Disk overwrite with zeros",
      "impact": "Complete disk data destruction",
      "detection_pattern": "dd\\s+if=/dev/(zero|urandom)\\s+of=/dev/[a-z]+",
      "alternatives": [
        "Use specific partition instead of entire disk",
        "Use secure erase utilities with confirmation",
        "Create disk images before overwrite operations"
      ],
      "prevention": "Block execution, suggest safer alternatives"
    }
  },
  
  "high_risks": {
    "chmod 777 /": {
      "risk_level": "high",
      "description": "Recursive permission change to world-writable",
      "impact": "Severe security vulnerability, system compromise",
      "detection_pattern": "chmod\\s+777\\s+/",
      "alternatives": [
        "Use specific directories with appropriate permissions",
        "Apply principle of least privilege",
        "Use ACLs for complex permission requirements"
      ],
      "prevention": "Warn user, require confirmation"
    }
  },
  
  "medium_risks": {
    "nmap -A": {
      "risk_level": "medium",
      "description": "Aggressive scan with OS detection",
      "impact": "Potential detection by security systems",
      "detection_pattern": "nmap.*-A",
      "alternatives": [
        "Use individual scan options for stealth",
        "Implement timing controls (-T2 or -T3)",
        "Consider target network policies"
      ],
      "prevention": "Display warning, allow with confirmation"
    }
  },
  
  "low_risks": {
    "nmap -sS": {
      "risk_level": "low",
      "description": "Standard SYN scan",
      "impact": "Minimal detection risk with proper authorization",
      "detection_pattern": "nmap.*-sS",
      "alternatives": [],
      "prevention": "Allow with standard logging"
    }
  }
}
```

### 5.2 Risk Assessment Categories

#### 5.2.1 Critical Risk Patterns (Immediate Block)
```json
{
  "critical_patterns": [
    "rm\\s+-rf\\s+/",
    "dd\\s+if=.*of=/dev/[a-z]+",
    ":(){ :|:& };:",
    "mkfs\\.",
    "fdisk.*-w",
    "parted.*rm"
  ],
  "action": "block_execution",
  "user_notification": "critical_warning"
}
```

#### 5.2.2 High Risk Patterns (Strong Warning)
```json
{
  "high_patterns": [
    "chmod\\s+777\\s+/",
    "chown\\s+.*:.*\\s+/",
    "iptables\\s+-F",
    "ufw\\s+--force\\s+reset",
    "systemctl\\s+disable\\s+ssh"
  ],
  "action": "require_confirmation",
  "user_notification": "high_risk_warning"
}
```

#### 5.2.3 Medium Risk Patterns (Standard Warning)
```json
{
  "medium_patterns": [
    "nmap.*-A",
    "sqlmap.*--risk=3",
    "hydra.*-t\\s+[5-9][0-9]",
    "gobuster.*-t\\s+[5-9][0-9]"
  ],
  "action": "display_warning",
  "user_notification": "medium_risk_info"
}
```

### 5.3 Risk Assessment Engine

#### 5.3.1 Pattern Matching System
```python
class RiskPatternMatcher:
    """
    Advanced pattern matching system for risk detection.
    """
    
    def compile_risk_patterns(self, risk_database: Dict) -> Dict[str, Pattern]:
        """
        Compiles regex patterns for efficient risk detection.
        
        Compilation Features:
        - Regex pattern optimization
        - Case-insensitive matching
        - Multi-pattern compilation
        - Performance optimization
        """
        
    def match_risk_patterns(self, command: str) -> List[Dict[str, Any]]:
        """
        Matches command against all risk patterns.
        
        Matching Features:
        - Multi-pattern simultaneous matching
        - Risk level prioritization
        - Context-aware matching
        - Performance optimization
        """
```

#### 5.3.2 Context-Aware Risk Assessment
```python
def assess_contextual_risk(self, command: str, context: Dict) -> Dict[str, Any]:
    """
    Performs context-aware risk assessment beyond pattern matching.
    
    Context Factors:
    - User role and expertise level
    - Target environment (production vs. lab)
    - Previous command history
    - Time and frequency patterns
    """
```

---

## 6. Version Management

### 6.1 Version System (_version.py)

**Purpose**: Centralized version management and compatibility tracking for LINA system components.

**File Location**: `core/_version.py`

**Version Structure**:

```python
"""
LINA Version Management System
Centralized version control and compatibility tracking.
"""

# Core System Version
__version__ = "2.0.0"
__version_info__ = (2, 0, 0)

# Component Versions
COMPONENT_VERSIONS = {
    "agent_system": "2.0.0",
    "core_system": "2.0.0", 
    "utils_system": "2.0.0",
    "prompt_templates": "2.0.0",
    "tool_registry": "2.0.0",
    "risk_database": "2.0.0"
}

# Compatibility Matrix
COMPATIBILITY_MATRIX = {
    "python": {
        "minimum": "3.8.0",
        "recommended": "3.11.0",
        "maximum": "3.13.0"
    },
    
    "dependencies": {
        "rich": ">=13.0.0",
        "google-generativeai": ">=0.3.0",
        "requests": ">=2.28.0",
        "psutil": ">=5.9.0"
    },
    
    "tools": {
        "nmap": ">=7.0",
        "volatility3": ">=2.0.0",
        "gobuster": ">=3.0.0"
    }
}

# API Compatibility
API_VERSIONS = {
    "google_gemini": "v1",
    "internal_api": "2.0",
    "tool_registry_schema": "2.0"
}
```

### 6.2 Version Management Functions

#### 6.2.1 Version Validation
```python
def validate_system_compatibility() -> Tuple[bool, List[str]]:
    """
    Validates system compatibility across all components.
    
    Validation Checks:
    - Python version compatibility
    - Dependency version requirements
    - Tool version compatibility
    - API version alignment
    """
    
def check_component_versions() -> Dict[str, str]:
    """
    Checks and reports versions of all system components.
    
    Component Categories:
    - Core system components
    - Agent system versions
    - Utility system versions
    - External tool versions
    """
```

#### 6.2.2 Update Management
```python
def check_for_updates() -> Dict[str, Any]:
    """
    Checks for available updates to system components.
    
    Update Categories:
    - Core system updates
    - Tool registry updates
    - Risk database updates
    - Dependency updates
    """
```

---

## 7. Data Storage Architecture

### 7.1 Data Directory Structure

```
data/
├── db/                       # Database Storage
│   └── lina_history.sqlite   # Session and interaction history
├── logs/                     # Logging System
│   └── lina_activity.log     # Activity and audit logs
└── outputs/                  # Command Output Storage
    ├── session_[id]/         # Session-specific outputs
    └── reports/              # Generated reports
```

### 7.2 Database Management

#### 7.2.1 SQLite Database (lina_history.sqlite)
```sql
-- Session Management Table
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    user_role TEXT,
    total_interactions INTEGER,
    success_rate REAL
);

-- Interaction History Table
CREATE TABLE interactions (
    interaction_id TEXT PRIMARY KEY,
    session_id TEXT,
    timestamp TIMESTAMP,
    user_input TEXT,
    executed_action TEXT,
    action_type TEXT,
    tool_name TEXT,
    success BOOLEAN,
    execution_time_ms INTEGER,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Risk Assessment Log Table
CREATE TABLE risk_assessments (
    assessment_id TEXT PRIMARY KEY,
    interaction_id TEXT,
    command TEXT,
    risk_level TEXT,
    risk_factors TEXT,
    user_decision TEXT,
    FOREIGN KEY (interaction_id) REFERENCES interactions(interaction_id)
);
```

#### 7.2.2 Database Management System
```python
class DatabaseManager:
    """
    Comprehensive database management for LINA data storage.
    """
    
    def initialize_database(self, db_path: str) -> bool:
        """
        Initializes SQLite database with proper schema.
        
        Initialization Features:
        - Schema creation and validation
        - Index creation for performance
        - Foreign key constraint setup
        - Data integrity validation
        """
        
    def store_session_data(self, session_data: Dict) -> bool:
        """
        Stores session information and interaction history.
        
        Storage Features:
        - Transactional data integrity
        - Efficient batch operations
        - Data compression for large outputs
        - Automatic cleanup of old data
        """
```

### 7.3 Logging System Integration

#### 7.3.1 Activity Logging (lina_activity.log)
```
2025-01-02 10:30:15 [INFO] Session started: session_abc123, Role: Student
2025-01-02 10:30:20 [INFO] Intent classified: tool_request for 'nmap scan'
2025-01-02 10:30:22 [INFO] Tool selected: nmap, Command generated: nmap -sS target.com
2025-01-02 10:30:23 [INFO] Risk assessment: LOW, Command approved
2025-01-02 10:30:25 [INFO] Command executed successfully, Duration: 2.1s
2025-01-02 10:30:26 [INFO] Output parsed: 3 open ports found
```

#### 7.3.2 Log Management System
```python
class LogManager:
    """
    Advanced logging system with structured output and rotation.
    """
    
    def configure_logging(self, config: Dict) -> None:
        """
        Configures comprehensive logging system.
        
        Logging Features:
        - Structured JSON logging
        - Log rotation and archival
        - Performance metrics logging
        - Security event logging
        """
```

---

## Summary

The LINA Core System provides a robust foundation with:

- **Comprehensive Configuration Management** with hierarchical overrides
- **Master Tool Registry** with 82+ cybersecurity tools
- **Individual Tool Registries** with detailed specifications (76+ files)
- **Risk Database** with 102+ dangerous command patterns
- **Version Management** with compatibility tracking
- **Data Storage Architecture** with SQLite and structured logging

**Core System Statistics**:
- **Configuration Files**: 3 (JSON, YAML, Python)
- **Tool Registries**: 82+ tools in master registry + 76+ individual registries
- **Risk Patterns**: 102+ dangerous command patterns
- **Database Tables**: 3 (sessions, interactions, risk_assessments)
- **Total Core Files**: 80+ files managing system foundation

This foundation enables LINA to operate reliably with comprehensive tool knowledge, safety awareness, and robust data management capabilities.
