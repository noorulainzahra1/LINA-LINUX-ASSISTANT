# agent/intelligence_selector.py
# Architect: The unified "Librarian & Scholar" for the Phoenix Architecture.
#
# This definitive agent merges the brilliant two-step "Librarian & Scholar" model
# into a single, cohesive intelligence system. It combines the fast tool classification
# capabilities of the ToolSelector with the expert command composition abilities
# of the CommandComposerAgent, creating a seamless and efficient tool intelligence pipeline.

import os
import json
from typing import Optional, List, Dict, Any, Tuple

from agent.llm_engine import LLMEngine
from utils.logger import log


class IntelligenceSelector:
    """
    The unified tool intelligence system for LINA.
    
    This agent combines two critical capabilities:
    1. Tool Selection (Librarian): Fast identification of the appropriate tool
    2. Command Composition (Scholar): Expert crafting of precise shell commands
    
    By unifying these complementary tasks, we create a more efficient and
    maintainable tool intelligence pipeline while preserving the brilliant
    two-step reasoning model.
    """
    
    def __init__(self, llm_engine: LLMEngine, registry_path: str, registries_dir_path: str, expert_role: str = "Student"):
        """
        Initializes the IntelligenceSelector with tool registry and parameter registries.
        
        Args:
            llm_engine: The LLM engine for AI operations
            registry_path: Path to the simplified tool_registry.json file
            registries_dir_path: Path to the detailed parameter registries directory
            expert_role: The user's expert role for tool prioritization
        """
        self.llm_engine = llm_engine
        self.registry_path = registry_path
        self.registries_dir_path = registries_dir_path
        self.expert_role = expert_role
        self.tools = self._load_tool_registry()
        
        log.info(f"IntelligenceSelector initialized with unified Librarian & Scholar capabilities for {expert_role} role")
    
    def _load_tool_registry(self) -> List[Dict[str, Any]]:
        """
        Loads the simplified tool registry for tool classification.
        
        Returns:
            List of tool definitions from the registry
            
        Raises:
            FileNotFoundError: If the registry file cannot be found
            json.JSONDecodeError: If the registry file is invalid JSON
        """
        try:
            with open(self.registry_path, 'r') as f:
                log.info(f"Loading simplified tool registry from {self.registry_path}")
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log.critical(f"FATAL: Could not load tool registry at {self.registry_path}: {e}")
            raise
    
    def _load_parameter_registry(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Loads the detailed parameter registry for a specific tool.
        
        Args:
            tool_name: Name of the tool (e.g., "nmap")
            
        Returns:
            Dictionary containing the tool's parameter registry or None on failure
        """
        registry_file = os.path.join(self.registries_dir_path, f"{tool_name}_registry.json")
        try:
            with open(registry_file, 'r') as f:
                log.info(f"Loading parameter registry: {registry_file}")
                return json.load(f)
        except FileNotFoundError:
            log.error(f"Parameter registry not found for tool '{tool_name}' at {registry_file}")
            return None
        except json.JSONDecodeError:
            log.error(f"Invalid JSON in parameter registry: {registry_file}")
            return None
    
    # ==========================================
    # LIBRARIAN CAPABILITIES (Tool Selection)
    # ==========================================
    
    def select_tool(self, user_input: str) -> Optional[str]:
        """
        Identifies the most appropriate tool for a given user request.
        
        This method uses fast LLM reasoning for efficient tool classification,
        implementing the "Librarian" role from the original architecture.
        
        Args:
            user_input: The user's natural language request
            
        Returns:
            The tool name (e.g., "nmap") or None if no suitable tool is found
        """
        log.info(f"Librarian function: selecting tool for '{user_input}'")
        
        # Construct a focused classification prompt with role consideration
        prompt = (
            f"You are a tool classification librarian for a {self.expert_role}. Analyze the user's request and identify which single tool from the following list is the most appropriate. "
            f"Consider the {self.expert_role} role when selecting tools - prioritize tools that match the user's expertise level and role requirements. "
            "Respond with ONLY the tool's name from the 'name' field and nothing else. Your response must be a single word.\n\n"
            f"USER REQUEST: \"{user_input}\"\n"
            f"USER ROLE: {self.expert_role}\n\n"
            f"AVAILABLE TOOLS: {json.dumps(self.tools, indent=2)}\n\n"
            "TOOL NAME:"
        )
        
        # Use fast triage model for quick classification
        success, response_or_error = self.llm_engine.generate_response(prompt)
        
        if not success:
            log.error(f"Tool selection LLM call failed: {response_or_error}")
            return None
        
        # Clean and validate the response
        tool_name = response_or_error.strip().lower().split()[0]
        
        # Validate that the tool exists in our registry
        if any(t['name'] == tool_name for t in self.tools):
            log.info(f"Tool selected: '{tool_name}'")
            return tool_name
        else:
            log.warning(f"LLM returned unknown tool '{tool_name}'. No match found.")
            return None
    
    # ==========================================
    # SCHOLAR CAPABILITIES (Command Composition)
    # ==========================================
    
    def compose_command(self, user_request: str, tool_name: str) -> Optional[str]:
        """
        Composes a precise, executable shell command for a specific tool.
        
        This method uses sophisticated LLM reasoning to analyze the tool's
        parameter registry and craft the optimal command, implementing the
        "Scholar" role from the original architecture.
        
        Args:
            user_request: The user's natural language request
            tool_name: The name of the tool to use
            
        Returns:
            Complete executable command string or None on failure
        """
        log.info(f"Scholar function: composing '{tool_name}' command for '{user_request}'")
        
        # Load the detailed parameter registry for this tool
        param_registry = self._load_parameter_registry(tool_name)
        if not param_registry:
            log.error(f"Cannot compose command without parameter registry for '{tool_name}'")
            return None
        
        # Check if this tool requires multi-step workflow
        multi_step_tools = ['john', 'hashcat', 'volatility3', 'autopsy']
        is_multi_step = tool_name.lower() in [t.lower() for t in multi_step_tools]
        
        # Construct sophisticated reasoning prompt
        prompt = (
            "You are an expert cybersecurity tool user and command-line specialist. "
            "Your task is to construct a precise, syntactically correct shell command based on a user's request and a detailed JSON registry of the tool's parameters. "
            "Analyze the user's intent, select the appropriate flags and values from the registry, and build the command string.\n\n"
        )
        
        if is_multi_step:
            prompt += (
                "IMPORTANT: For multi-step tools like password crackers or forensics tools, you may need to:\n"
                "- Chain commands using && (sequential execution) or ; (regardless of success)\n"
                "- For password cracking: identify hash type first if needed, then run the cracker, then show results\n"
                "- Example for john: 'john --list=formats | grep -i md5 && john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt && john --show hashes.txt'\n"
                "- Example for hashcat: 'hashcat --example-hashes | grep -i md5 && hashcat -m 0 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt && hashcat -m 0 --show hashes.txt'\n"
                "- Only chain steps that make logical sense for the user's request\n\n"
            )
        
        prompt += (
            "Respond with ONLY the command(s) and nothing else. "
            "If multiple steps are needed, chain them with && or ; as appropriate.\n\n"
            f"USER REQUEST: \"{user_request}\"\n\n"
            f"TOOL PARAMETER REGISTRY: {json.dumps(param_registry, indent=2)}\n\n"
            "FINAL COMMAND:"
        )
        
        # Use high-quality model for complex reasoning
        success, response_or_error = self.llm_engine.generate_response(prompt)
        
        if not success:
            log.error(f"Command composition LLM call failed: {response_or_error}")
            return None
        
        # Clean and validate the response
        command = response_or_error.strip().strip('`')
        
        if not command.startswith(tool_name):
            log.warning(f"Composed command doesn't start with tool name: '{command}'")
            # Continue anyway - trust the high-quality model
        
        log.info(f"Command composed: {command}")
        return command
    
    # ==========================================
    # UNIFIED INTELLIGENCE PIPELINE
    # ==========================================
    
    def process_tool_request(self, user_request: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Processes a complete tool request using the unified Librarian & Scholar pipeline.
        
        This method implements the full two-step intelligence process:
        1. Tool Selection (Librarian): Identify the appropriate tool
        2. Command Composition (Scholar): Craft the precise command
        
        Args:
            user_request: The user's natural language request
            
        Returns:
            Tuple of (success, tool_name, command) where:
            - success: True if both steps completed successfully
            - tool_name: The selected tool name (for logging/display)
            - command: The final executable command string
        """
        log.info(f"Processing unified tool request: '{user_request}'")
        
        # Step 1: Librarian - Select the appropriate tool
        tool_name = self.select_tool(user_request)
        if not tool_name:
            log.warning("Tool selection failed - no appropriate tool found")
            return False, None, None
        
        # Step 2: Scholar - Compose the precise command
        command = self.compose_command(user_request, tool_name)
        if not command:
            log.warning(f"Command composition failed for tool '{tool_name}'")
            return False, tool_name, None
        
        log.info(f"Unified intelligence pipeline completed successfully: {tool_name} -> {command}")
        return True, tool_name, command
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def get_available_tools(self) -> List[str]:
        """
        Returns a list of all available tool names.
        
        Returns:
            List of tool names from the registry
        """
        return [tool['name'] for tool in self.tools]
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Returns information about a specific tool.
        
        Args:
            tool_name: Name of the tool to get info for
            
        Returns:
            Tool information dictionary or None if not found
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                return tool
        return None
    
    def get_capabilities_summary(self) -> Dict[str, Any]:
        """
        Returns a summary of IntelligenceSelector capabilities.
        
        Returns:
            Dictionary containing capability information
        """
        return {
            "name": "IntelligenceSelector",
            "description": "Unified Tool Intelligence (Librarian & Scholar)",
            "capabilities": [
                "Tool Classification",
                "Command Composition",
                "Parameter Registry Analysis",
                "Unified Intelligence Pipeline"
            ],
            "tools_available": len(self.tools),
            "registries_path": self.registries_dir_path
        }
