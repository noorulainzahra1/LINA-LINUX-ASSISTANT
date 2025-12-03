# agent/system_operations_agent.py
# Architect: Advanced System Operations Agent for the Phoenix Architecture
#
# This agent handles system-level operations including tool installation,
# configuration, troubleshooting, and system administration tasks.
# It leverages AI to provide intelligent guidance and command generation.

import os
import re
from typing import Dict, Any, Tuple, Optional, List

from agent.llm_engine import LLMEngine
from utils.logger import log


class SystemOperationsAgent:
    """
    Advanced agent for handling system operations with AI intelligence.
    
    This agent specializes in:
    1. Tool Installation: apt, pip, go get, npm, gem, etc.
    2. System Configuration: Setting up services, configuring tools
    3. Troubleshooting: Fixing common errors and issues
    4. System Administration: User management, permissions, services
    5. Environment Setup: Development environments, dependencies
    """
    
    def __init__(self, llm_engine: LLMEngine):
        """
        Initialize the SystemOperationsAgent.
        
        Args:
            llm_engine: The LLM engine for AI operations
        """
        self.llm_engine = llm_engine
        
        # Package managers and their patterns
        self.package_managers = {
            'apt': {
                'install': 'sudo apt update && sudo apt install -y {package}',
                'remove': 'sudo apt remove -y {package}',
                'update': 'sudo apt update',
                'upgrade': 'sudo apt upgrade -y',
                'search': 'apt search {package}',
                'info': 'apt show {package}'
            },
            'pip': {
                'install': 'pip3 install {package}',
                'remove': 'pip3 uninstall -y {package}',
                'update': 'pip3 install --upgrade {package}',
                'list': 'pip3 list',
                'search': 'pip3 search {package}'
            },
            'go': {
                'install': 'go install {package}@latest',
                'get': 'go get -u {package}',
                'list': 'go list -m all'
            },
            'npm': {
                'install': 'npm install -g {package}',
                'remove': 'npm uninstall -g {package}',
                'update': 'npm update -g {package}',
                'list': 'npm list -g'
            },
            'gem': {
                'install': 'sudo gem install {package}',
                'remove': 'sudo gem uninstall {package}',
                'update': 'sudo gem update {package}',
                'list': 'gem list'
            },
            'cargo': {
                'install': 'cargo install {package}',
                'update': 'cargo install --force {package}',
                'list': 'cargo install --list'
            },
            'snap': {
                'install': 'sudo snap install {package}',
                'remove': 'sudo snap remove {package}',
                'list': 'snap list'
            }
        }
        
        # Common tool installation mappings
        self.tool_installations = {
            'nmap': 'sudo apt update && sudo apt install -y nmap',
            'gobuster': 'sudo apt update && sudo apt install -y gobuster',
            'nikto': 'sudo apt update && sudo apt install -y nikto',
            'sqlmap': 'sudo apt update && sudo apt install -y sqlmap',
            'metasploit': 'curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && ./msfinstall',
            'burpsuite': 'sudo apt update && sudo apt install -y burpsuite',
            'wireshark': 'sudo apt update && sudo apt install -y wireshark',
            'hydra': 'sudo apt update && sudo apt install -y hydra',
            'john': 'sudo apt update && sudo apt install -y john',
            'hashcat': 'sudo apt update && sudo apt install -y hashcat',
            'aircrack-ng': 'sudo apt update && sudo apt install -y aircrack-ng',
            'golang': 'sudo apt update && sudo apt install -y golang-go',
            'docker': 'curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh',
            'rust': 'curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y',
            'nodejs': 'curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt install -y nodejs',
            'python3-pip': 'sudo apt update && sudo apt install -y python3-pip',
            'git': 'sudo apt update && sudo apt install -y git',
            'vim': 'sudo apt update && sudo apt install -y vim',
            'tmux': 'sudo apt update && sudo apt install -y tmux',
            'zsh': 'sudo apt update && sudo apt install -y zsh',
            'oh-my-zsh': 'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"'
        }
        
        log.info("SystemOperationsAgent initialized with comprehensive package management support")
    
    def handle_installation(self, user_request: str) -> Tuple[bool, str, str]:
        """
        Handles tool installation requests intelligently.
        
        Args:
            user_request: The user's installation request
            
        Returns:
            Tuple of (success, command, explanation)
        """
        log.info(f"Processing installation request: '{user_request}'")
        
        # First, check if it's a known tool
        tool_name = self._extract_tool_name(user_request)
        if tool_name and tool_name.lower() in self.tool_installations:
            command = self.tool_installations[tool_name.lower()]
            explanation = f"Installing {tool_name} using the recommended method"
            return True, command, explanation
        
        # Use AI to determine the best installation method
        prompt = f"""You are a Linux system administrator expert. A user wants to: "{user_request}"

Determine the BEST way to install this on a Debian/Ubuntu-based system (like Kali Linux).

Consider:
1. Is this a system package (use apt)?
2. Is this a Python package (use pip3)?
3. Is this a Go tool (use go install)?
4. Is this a Node.js package (use npm)?
5. Is this a Ruby gem (use gem)?
6. Does it need a special installation script?

Respond with ONLY the exact command(s) to install it. If multiple commands are needed, chain them with &&.

Examples:
- "install requests library" → pip3 install requests
- "install golang" → sudo apt update && sudo apt install -y golang-go
- "install nuclei" → go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
- "install node" → curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt install -y nodejs

Command:"""

        success, response = self.llm_engine.generate_response(prompt)
        
        if not success:
            return False, "", f"Failed to generate installation command: {response}"
        
        command = response.strip().strip('`').strip('"').strip("'")
        
        if not command or len(command) < 3:
            return False, "", "Could not determine installation method"
        
        explanation = f"AI-generated installation command for: {user_request}"
        return True, command, explanation
    
    def handle_configuration(self, user_request: str) -> Tuple[bool, str, str]:
        """
        Handles configuration requests for tools and services.
        
        Args:
            user_request: The configuration request
            
        Returns:
            Tuple of (success, command/guidance, explanation)
        """
        log.info(f"Processing configuration request: '{user_request}'")
        
        prompt = f"""You are a Linux system configuration expert. A user needs help with: "{user_request}"

Provide the EXACT commands or configuration steps needed. Consider:
1. Service configuration (systemctl, config files)
2. Tool configuration (config files, environment variables)
3. Permission settings (chmod, chown, user groups)
4. Network configuration
5. Security hardening

Respond with the specific commands needed. Chain multiple commands with &&.

Examples:
- "configure postgresql for metasploit" → sudo systemctl start postgresql && sudo msfdb init
- "setup docker permissions" → sudo usermod -aG docker $USER && newgrp docker
- "configure burp proxy" → echo "export http_proxy=http://127.0.0.1:8080" >> ~/.bashrc && source ~/.bashrc

Commands:"""

        success, response = self.llm_engine.generate_response(prompt)
        
        if not success:
            return False, "", f"Failed to generate configuration: {response}"
        
        command = response.strip()
        explanation = f"Configuration steps for: {user_request}"
        
        return True, command, explanation
    
    def handle_troubleshooting(self, user_request: str) -> Tuple[bool, str, str]:
        """
        Handles troubleshooting and error fixing requests.
        
        Args:
            user_request: The troubleshooting request
            
        Returns:
            Tuple of (success, solution, explanation)
        """
        log.info(f"Processing troubleshooting request: '{user_request}'")
        
        prompt = f"""You are a Linux troubleshooting expert. A user has this problem: "{user_request}"

Analyze the issue and provide the EXACT commands to fix it. Common issues:
1. Permission denied → sudo, chmod, chown
2. Command not found → install missing tool, update PATH
3. Service not running → systemctl start/enable
4. Network issues → firewall, routing, DNS
5. Dependency issues → install missing libraries

Provide the fix commands. Use && to chain multiple commands if needed.

Examples:
- "permission denied on /usr/bin/nmap" → sudo chmod +x /usr/bin/nmap
- "docker: command not found" → curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
- "cannot connect to postgresql" → sudo systemctl start postgresql && sudo systemctl enable postgresql

Fix commands:"""

        success, response = self.llm_engine.generate_response(prompt)
        
        if not success:
            return False, "", f"Failed to generate fix: {response}"
        
        solution = response.strip()
        explanation = f"Troubleshooting solution for: {user_request}"
        
        return True, solution, explanation
    
    def handle_system_operation(self, user_request: str) -> Tuple[bool, str, str]:
        """
        Main handler for all system operations.
        
        Args:
            user_request: The user's system operation request
            
        Returns:
            Tuple of (success, command, explanation)
        """
        # Determine operation type
        operation_type = self._classify_operation(user_request)
        
        if operation_type == 'installation':
            return self.handle_installation(user_request)
        elif operation_type == 'configuration':
            return self.handle_configuration(user_request)
        elif operation_type == 'troubleshooting':
            return self.handle_troubleshooting(user_request)
        else:
            # Generic system operation
            return self._handle_generic_operation(user_request)
    
    def _classify_operation(self, request: str) -> str:
        """Classify the type of system operation."""
        request_lower = request.lower()
        
        install_keywords = ['install', 'setup', 'add', 'get']
        config_keywords = ['configure', 'config', 'set up', 'enable', 'disable']
        trouble_keywords = ['error', 'not working', 'fix', 'broken', 'failed', 'permission denied']
        
        for keyword in install_keywords:
            if keyword in request_lower:
                return 'installation'
        
        for keyword in config_keywords:
            if keyword in request_lower:
                return 'configuration'
        
        for keyword in trouble_keywords:
            if keyword in request_lower:
                return 'troubleshooting'
        
        return 'generic'
    
    def _extract_tool_name(self, request: str) -> Optional[str]:
        """Extract tool name from the request."""
        # Remove common words
        words_to_remove = ['install', 'setup', 'please', 'can', 'you', 'help', 'me', 'with', 'the', 'tool']
        
        words = request.lower().split()
        filtered_words = [w for w in words if w not in words_to_remove]
        
        # Check each word against known tools
        for word in filtered_words:
            if word in self.tool_installations:
                return word
        
        # Return the most likely tool name (first non-common word)
        return filtered_words[0] if filtered_words else None
    
    def _handle_generic_operation(self, user_request: str) -> Tuple[bool, str, str]:
        """Handle generic system operations."""
        prompt = f"""You are a Linux system administrator. Generate the exact command for: "{user_request}"

Focus on:
- System administration tasks
- File operations
- User management
- Service management
- Package operations

Respond with ONLY the command(s). Chain with && if multiple commands needed.

Command:"""

        success, response = self.llm_engine.generate_response(prompt)
        
        if not success:
            return False, "", f"Failed to generate command: {response}"
        
        command = response.strip().strip('`').strip('"').strip("'")
        explanation = f"System operation command for: {user_request}"
        
        return True, command, explanation
    
    def get_supported_package_managers(self) -> List[str]:
        """Returns list of supported package managers."""
        return list(self.package_managers.keys())
    
    def get_installable_tools(self) -> List[str]:
        """Returns list of tools with known installation commands."""
        return list(self.tool_installations.keys())
