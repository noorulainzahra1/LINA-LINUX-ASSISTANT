# agent/agent_core.py
# Architect: The unified NLP specialist for the Phoenix Architecture.
#
# This definitive agent consolidates command parsing, explanation generation,
# and conversational AI into a single, powerful module. It serves as the
# "linguistic intelligence" layer of LINA, handling all natural language
# processing tasks with elegance and efficiency.

import os
import json
from typing import Tuple, Optional, List, Dict, Any

from agent.llm_engine import LLMEngine
from utils.logger import log


class AgentCore:
    """
    The unified natural language processing specialist for LINA.
    
    This agent consolidates three critical capabilities:
    1. Command Parsing: Translating natural language into executable commands
    2. Explanation Generation: Providing detailed explanations and guidance
    3. Conversational AI: Handling general dialogue and user interaction
    
    By unifying these related NLP tasks, we eliminate redundancy and create
    a more cohesive linguistic intelligence system.
    """
    
    def __init__(self, llm_engine: LLMEngine, tool_registry_path: Optional[str] = None):
        """
        Initializes the AgentCore with all necessary prompt templates.
        
        Args:
            llm_engine: The LLM engine for AI operations
            tool_registry_path: Optional path to tool registry for reference
        """
        self.llm_engine = llm_engine
        self.tool_registry_path = tool_registry_path
        self.tools_reference = self._load_tools_reference() if tool_registry_path else []
        
        # Load all prompt templates during initialization
        self.command_prompt_template = self._load_prompt_template("agent_prompt.txt")
        self.explain_prompt_template = self._load_prompt_template("explain_prompt.txt")
        self.guidance_prompt_template = self._load_prompt_template("guidance_prompt.txt")
        self.chatbot_prompt_template = self._load_prompt_template("chatbot_prompt.txt")
        
        log.info("AgentCore initialized with unified NLP capabilities")
    
    def _load_prompt_template(self, filename: str) -> str:
        """
        Loads a prompt template from the prompts directory.
        
        Args:
            filename: Name of the prompt file to load
            
        Returns:
            The content of the prompt file
            
        Raises:
            FileNotFoundError: If the prompt file cannot be found
        """
        try:
            base_dir = os.path.dirname(__file__)
            path = os.path.join(base_dir, "prompts", filename)
            with open(path, 'r', encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            log.critical(f"FATAL: Prompt file '{filename}' not found. AgentCore cannot function.")
            raise
    
    def _load_tools_reference(self) -> List[str]:
        """
        Loads tool names from the registry as reference for command generation.
        
        Returns:
            List of tool names, or empty list if loading fails
        """
        try:
            with open(self.tool_registry_path, 'r') as f:
                tools_data = json.load(f)
                tool_names = [tool['name'] for tool in tools_data if 'name' in tool]
                log.info(f"Loaded {len(tool_names)} tools as reference for command generation")
                return tool_names
        except Exception as e:
            log.warning(f"Could not load tool registry for reference: {e}")
            return []
    
    # ==========================================
    # COMMAND PARSING CAPABILITIES
    # ==========================================
    
    def parse_command(self, user_input: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parses natural language input into a Linux command and explanation.
        
        This method handles the command generation pathway, translating user
        requests into executable shell commands with detailed explanations.
        
        Args:
            user_input: The natural language request from the user
            
        Returns:
            Tuple of (command, explanation) or (None, None) on failure
        """
        if not user_input.strip():
            log.warning("AgentCore received empty input for command parsing.")
            return None, None
        
        log.info(f"Parsing user input for command generation: '{user_input}'")
        
        # Format tools reference for the prompt
        tools_list = ", ".join(self.tools_reference) if self.tools_reference else "nmap, gobuster, nikto, sqlmap, hydra, etc."
        
        prompt = self.command_prompt_template.format(
            user_input=user_input,
            available_tools=tools_list
        )
        
        # Use conversational response for command parsing (fast and reliable)
        success, response_or_error = self.llm_engine.generate_response(prompt)
        
        if not success:
            log.error(f"AgentCore command parsing LLM call failed: {response_or_error}")
            return None, None
        
        # Extract command and explanation from the response
        return self._extract_command_and_explanation(response_or_error)
    
    def _extract_command_and_explanation(self, response: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extracts command and explanation from LLM response.
        
        Expected format:
        Line 1: The actual command
        Line 2: Explanation: [detailed explanation]
        
        Args:
            response: Raw LLM response string
            
        Returns:
            Tuple of (command, explanation) or (None, None) on parse failure
        """
        try:
            lines = response.strip().split('\n', 1)
            command = lines[0].strip()
            
            if not command:
                log.warning(f"LLM response did not contain a command on the first line. Raw: {response}")
                return None, None
            
            explanation = None
            if len(lines) > 1 and lines[1].strip().lower().startswith("explanation:"):
                explanation = lines[1].replace("Explanation:", "", 1).strip()
            elif len(lines) > 1:
                log.warning(f"Could not parse explanation from LLM response's second line. Raw: {response}")
            
            log.info(f"Successfully parsed command: '{command}'")
            return command, explanation
            
        except Exception as e:
            log.error(f"Unexpected error extracting command from response: '{response}'. Error: {e}")
            return None, None
    
    # ==========================================
    # EXPLANATION CAPABILITIES
    # ==========================================
    
    def explain_topic(self, topic: str) -> Tuple[bool, str]:
        """
        Generates a detailed explanation for a given topic or command.
        
        This method provides deep, educational explanations for cybersecurity
        concepts, Linux commands, or technical topics.
        
        Args:
            topic: The command, concept, or topic to be explained
            
        Returns:
            Tuple of (success, explanation_text)
        """
        if not topic.strip():
            return False, "Cannot explain an empty topic."
        
        log.info(f"Generating explanation for topic: '{topic[:70]}...'")
        prompt = self.explain_prompt_template.format(topic=topic)
        
        # Use explanation response for high-quality, detailed output
        success, response_or_error = self.llm_engine.generate_response(prompt)
        
        if not success:
            log.error(f"AgentCore explanation LLM call failed: {response_or_error}")
            return False, "LINA could not generate an explanation due to an API error."
        
        return True, response_or_error
    
    def provide_guidance(self, tool_name: str) -> Tuple[bool, str]:
        """
        Generates detailed, step-by-step guidance for a complex tool.
        
        This method creates comprehensive tutorials for cybersecurity tools
        that aren't directly integrated into the LINA framework.
        
        Args:
            tool_name: The name of the tool to generate guidance for
            
        Returns:
            Tuple of (success, guidance_text)
        """
        if not tool_name.strip():
            return False, "Cannot provide guidance for an empty tool name."
        
        log.info(f"Generating guidance for tool: '{tool_name}'")
        prompt = self.guidance_prompt_template.format(tool_name=tool_name)
        
        # Use explanation response for high-quality tutorial generation
        success, response_or_error = self.llm_engine.generate_response(prompt)
        
        if not success:
            log.error(f"AgentCore guidance LLM call failed: {response_or_error}")
            return False, f"LINA could not generate guidance for '{tool_name}' due to an API error."
        
        return True, response_or_error
    
    # ==========================================
    # CONVERSATIONAL CAPABILITIES
    # ==========================================
    
    def generate_conversation(self, user_input: str, chat_history: List[Dict[str, str]]) -> Tuple[bool, str]:
        """
        Generates a conversational response for general dialogue.
        
        This method handles non-task-oriented interactions, giving LINA
        a personality and the ability to engage in natural conversation.
        
        Args:
            user_input: The user's latest message
            chat_history: List of previous conversation turns for context
            
        Returns:
            Tuple of (success, response_text)
        """
        if not user_input.strip():
            return True, "Is there something I can help you with?"
        
        log.info(f"Generating conversational response for: '{user_input}'")
        
        # Format chat history for context
        history_str = "\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in chat_history])
        prompt = self.chatbot_prompt_template.format(chat_history=history_str, user_input=user_input)
        
        # Use conversational response for natural dialogue
        success, response_or_error = self.llm_engine.generate_response(prompt)
        
        if not success:
            log.error(f"AgentCore conversation LLM call failed: {response_or_error}")
            return False, "I'm sorry, I seem to be at a loss for words right now."
        
        return True, response_or_error
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def get_capabilities_summary(self) -> Dict[str, Any]:
        """
        Returns a summary of AgentCore capabilities.
        
        Returns:
            Dictionary containing capability information
        """
        return {
            "name": "AgentCore",
            "description": "Unified Natural Language Processing Specialist",
            "capabilities": [
                "Command Parsing",
                "Technical Explanations", 
                "Tool Guidance",
                "Conversational AI"
            ],
            "prompt_templates": [
                "agent_prompt.txt",
                "explain_prompt.txt", 
                "guidance_prompt.txt",
                "chatbot_prompt.txt"
            ]
        }
