# agent/brain.py
# Architect: The unified Brain for the Phoenix Architecture.
#
# This definitive version consolidates all AI orchestration capabilities into a single,
# powerful controller. It implements the brilliant "Librarian & Scholar" model for
# tool requests and now includes autonomous multi-step planning capabilities as a
# core feature. This is the mastermind that coordinates all AI intelligence.

import os
import json
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime

from rich.prompt import Prompt
from rich.console import Console

from agent.llm_engine import LLMEngine
from agent.agent_core import AgentCore
from agent.intelligence_selector import IntelligenceSelector
from agent.risk_manager import RiskManager
from agent.session_manager import SessionManager
from agent.forensics_manager import ForensicsManager
from agent.system_operations_agent import SystemOperationsAgent
from utils.logger import log
from utils import banner
from core._version import __version__

console = Console()


class Brain:
    """
    The unified central orchestrator for the Phoenix Architecture LINA system.
    
    This definitive Brain consolidates all AI intelligence capabilities:
    1. Intent Analysis: Understanding user requests and routing appropriately
    2. Tool Intelligence: Librarian & Scholar model for tool selection and composition
    3. Natural Language Processing: Command parsing, explanations, conversations
    4. Autonomous Planning: Multi-step plan generation and coordination
    5. Session Management: Context awareness and learning
    6. Risk Management: Safety assessment and guidance
    
    The Brain serves as the mastermind that coordinates all AI agents and
    provides seamless, intelligent cybersecurity assistance.
    """
    
    def __init__(self, config: Dict[str, Any], tool_registry_path: str, 
                 risk_database_path: str, param_registries_path: str,
                 expert_role: str = "Student"):
        """
        Initializes the unified Brain with all Phoenix Architecture components.

        Args:
            config: The global configuration dictionary
            tool_registry_path: Path to the simplified tool_registry.json
            risk_database_path: Path to risk_database.json
            param_registries_path: Path to the 'registries' directory
            expert_role: The user's expert role (e.g., 'Forensic Expert', 'Pentester')
        """
        log.info(f"LINA Brain (Phoenix Architecture) initializing with Cloud AI (Google Gemini)")
        
        # === CORE AI INFRASTRUCTURE (Cloud-Only with Gemini) ===
        self.llm_engine = LLMEngine(config=config)
        
        # === EXPERT ROLE STORAGE ===
        self.expert_role = expert_role
        log.info(f"Expert role set to: {expert_role}")
        
        # === PHOENIX ARCHITECTURE AGENTS ===
        self.agent_core = AgentCore(self.llm_engine, tool_registry_path)
        self.intelligence_selector = IntelligenceSelector(
            self.llm_engine, 
            tool_registry_path, 
            param_registries_path,
            expert_role=expert_role
        )
        self.risk_manager = RiskManager(self.llm_engine, risk_database_path)
        self.session_manager = SessionManager()
        self.forensics_manager = ForensicsManager()
        self.system_operations_agent = SystemOperationsAgent(self.llm_engine)
        
        # === BRAIN STATE ===
        self.triage_prompt_template = self._load_triage_prompt()
        self.planning_prompt_template = self._load_planning_prompt()
        self.introspection_commands = ['/list tools', '/list agents', '/help', '/status']
        
        log.info("Brain initialization complete - all Phoenix agents online")

    def _load_triage_prompt(self) -> str:
        """Loads the intent classification prompt template."""
        try:
            base_dir = os.path.dirname(__file__)
            path = os.path.join(base_dir, "prompts", "triage_prompt.txt")
            with open(path, 'r', encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            log.warning("triage_prompt.txt not found. Using built-in template.")
            return self._get_builtin_triage_prompt()
    
    def _get_builtin_triage_prompt(self) -> str:
        """Returns a built-in triage prompt template."""
        return """You are LINA's advanced AI-powered intent classifier using Google Gemini's full capabilities.

Analyze the user's request deeply considering context, implied meaning, and potential multi-intent scenarios.

**User Input:** "{user_input}"

**CRITICAL ANALYSIS REQUIRED:**
- Detect if the user wants to install/setup something
- Identify if they need help with configuration
- Check for system administration tasks
- Look for troubleshooting requests
- Detect security testing intentions

**Categories:**

1. **general_conversation** - Greetings, casual chat, questions about LINA
   Examples: "hello", "how are you?", "what can you do?", "thanks"

2. **plan_request** - Multi-step operations, comprehensive assessments, strategies
   Examples: "create a plan to test example.com", "full security audit", "assess network security"

3. **tool_request** - Direct cybersecurity tool usage (nmap, gobuster, sqlmap, etc.)
   Examples: "run nmap on example.com", "use nikto", "sqlmap scan", "gobuster on site"

4. **explanation_request** - Learning/educational queries about concepts or tools  
   Examples: "explain SQL injection", "what is nmap?", "how does XSS work?"

5. **command_request** - Generic Linux/Unix commands or operations
   Examples: "list files", "show processes", "check disk space", "find large files"

6. **system_operation** - Installation, configuration, setup, package management
   Examples: "install nmap", "setup metasploit", "install golang", "configure postgresql", "apt update"

7. **troubleshooting_request** - Fixing errors, solving problems, debugging
   Examples: "nmap not working", "fix permission denied", "tool not found error"

8. **forensics_request** - Digital forensics, memory analysis, disk imaging
   Examples: "analyze memory dump", "recover deleted files", "examine disk image"

9. **network_analysis** - Network diagnostics, monitoring, traffic analysis
   Examples: "monitor network traffic", "analyze packets", "check connections"

10. **automation_request** - Scripts, automation, scheduled tasks
    Examples: "automate this scan", "create script for", "schedule daily scan"

**ADVANCED CLASSIFICATION RULES:**
- If user mentions "install", "setup", "configure" → system_operation
- If user mentions specific pentesting tools → tool_request
- If user asks "how to" or "teach me" → explanation_request
- If user mentions "not working", "error", "fix" → troubleshooting_request
- If user wants multiple related tasks → plan_request
- For ambiguous requests, choose the most actionable category

**Response:** Single category name only (e.g., "system_operation")"""
    
    def _load_planning_prompt(self) -> str:
        """Loads the autonomous planning prompt template."""
        try:
            base_dir = os.path.dirname(__file__)
            path = os.path.join(base_dir, "prompts", "planner_prompt.txt")
            with open(path, 'r', encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            log.warning("planner_prompt.txt not found. Using built-in planning template.")
            return self._get_builtin_planning_prompt()
    
    def _get_builtin_planning_prompt(self) -> str:
        """Returns a built-in planning prompt template."""
        return """You are an expert cybersecurity strategist and penetration testing planner.

Your task is to create a detailed, multi-step plan for the user's cybersecurity objective.

USER GOAL: {user_goal}

AVAILABLE TOOLS: {available_tools}

Create a JSON-formatted plan with the following structure:
{{
    "goal": "Brief description of the overall objective",
    "steps": [
        {{
            "step_number": 1,
            "description": "Clear description of what this step accomplishes", 
            "tool_request": "Natural language request that can be processed by LINA",
            "expected_outcome": "What we expect to learn or achieve",
            "dependencies": ["List of previous step numbers this depends on"]
        }}
    ],
    "estimated_time": "Estimated total time (e.g., '15-30 minutes')",
    "risk_level": "low/medium/high",
    "prerequisites": ["Any required setup or information needed"]
}}

Guidelines:
- Each step should be a single, focused task
- Tool requests should be natural language that LINA can understand
- Steps should build logically toward the goal
- Include reconnaissance, analysis, and verification steps as appropriate
- Consider OPSEC and legal/ethical boundaries
- Limit plans to 8 steps maximum for clarity

Respond with ONLY the JSON plan and nothing else."""
    
    # ==========================================
    # INTENT ANALYSIS AND ROUTING
    # ==========================================
    
    def _analyze_intent(self, user_input: str) -> Tuple[bool, str]:
        """
        Analyzes user input to determine the appropriate processing pathway.
        
        Args:
            user_input: The user's natural language request
            
        Returns:
            Tuple of (success, intent) where intent is one of:
            - 'introspection_request': Built-in commands like /help, /status
            - 'plan_request': Multi-step planning requests
            - 'tool_request': Single tool execution requests  
            - 'command_request': Direct command generation requests
            - 'explanation_request': Requests for explanations or guidance
            - 'general_conversation': General dialogue
        """
        # Check for built-in commands first
        if user_input.lower().strip() in self.introspection_commands:
            return True, 'introspection_request'
            
        # Use AI for intent classification
        prompt = self.triage_prompt_template.format(user_input=user_input)
        success, raw_intent_or_error = self.llm_engine.generate_response(prompt)
        
        if not success:
            log.error(f"Intent analysis failed: {raw_intent_or_error}")
            return False, raw_intent_or_error

        # Clean and validate the intent
        intent = raw_intent_or_error.lower().strip().strip('`')
        log.info(f"Intent classified as: '{intent}'")
        
        valid_intents = [
            'plan_request', 'tool_request', 'command_request', 
            'explanation_request', 'general_conversation', 'system_operation',
            'troubleshooting_request', 'forensics_request', 'network_analysis',
            'automation_request'
        ]
        
        if intent in valid_intents:
            return True, intent
        else:
            log.warning(f"Unexpected intent '{intent}', defaulting to conversation")
            return True, 'general_conversation'

    # ==========================================
    # AUTONOMOUS PLANNING CAPABILITIES
    # ==========================================
    
    def _generate_autonomous_plan(self, user_goal: str) -> Dict[str, Any]:
        """
        Generates a comprehensive multi-step plan for achieving a cybersecurity objective.
        
        This method implements the core autonomous planning capability that was
        previously handled by the separate PlannerAgent. The Brain now acts as
        the "Mastermind" for strategic planning.
        
        Args:
            user_goal: The high-level objective the user wants to achieve
            
        Returns:
            Dictionary containing either:
            - On success: {'type': 'plan', 'plan': plan_dict, 'goal': user_goal}
            - On failure: {'type': 'error', 'message': error_description}
        """
        log.info(f"Generating autonomous plan for goal: '{user_goal}'")
        
        # Show progress to user
        with console.status("[bold blue]🧠 Analyzing goal and available tools...", spinner="dots"):
            # Get available tools for context
            available_tools = self.intelligence_selector.get_available_tools()
            tools_summary = [f"- {tool}" for tool in available_tools[:15]]  # Limit for prompt size
            tools_text = "\n".join(tools_summary)
            
            # Construct the planning prompt
            prompt = self.planning_prompt_template.format(
                user_goal=user_goal,
                available_tools=tools_text
            )
        
        # Show AI processing status
        with console.status("[bold green]🤖 AI generating strategic plan (this may take 45-75 seconds)...", spinner="dots"):
            # Use high-quality model for complex planning
            success, response_or_error = self.llm_engine.generate_response(prompt)
        
        if not success:
            log.error(f"Plan generation LLM call failed: {response_or_error}")
            
            # Show user-friendly error message
            console.print("\n[red]❌ Plan Generation Failed[/red]")
            console.print(f"[yellow]Reason: {response_or_error}[/yellow]")
            
            # Check if it's a timeout and provide helpful advice
            if "timeout" in response_or_error.lower() or "504" in response_or_error:
                console.print("\n[cyan]💡 Tip: The AI service is experiencing high load. Please try again in a moment.[/cyan]")
            
            return {
                'type': 'error',
                'message': f"Failed to generate plan due to AI error: {response_or_error}"
            }
        
        console.print("[green]✅ Plan generated successfully![/green]")
        
        # Parse the JSON plan from the response
        try:
            # Extract JSON from response (handle potential markdown formatting)
            response_text = response_or_error.strip()
            if response_text.startswith('```'):
                # Remove markdown code blocks
                lines = response_text.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip().startswith('```'):
                        in_json = not in_json
                        continue
                    if in_json:
                        json_lines.append(line)
                response_text = '\n'.join(json_lines)
            
            plan_data = json.loads(response_text)
            
            # Validate plan structure
            if not self._validate_plan_structure(plan_data):
                return {
                    'type': 'error',
                    'message': "Generated plan has invalid structure. Please try rephrasing your goal."
                }
            
            log.info(f"Successfully generated {len(plan_data.get('steps', []))} step plan")
            
            return {
                'type': 'autonomous_plan',
                'plan': plan_data,
                'goal': user_goal
            }
            
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse plan JSON: {e}")
            log.error(f"Raw response: {response_or_error}")
            return {
                'type': 'error',
                'message': "Generated plan was not in valid JSON format. Please try rephrasing your goal."
            }
        except Exception as e:
            log.error(f"Unexpected error during plan generation: {e}")
            return {
                'type': 'error',
                'message': f"An unexpected error occurred during planning: {str(e)}"
            }
    
    def _validate_plan_structure(self, plan_data: Dict[str, Any]) -> bool:
        """
        Validates that a generated plan follows the enhanced Phoenix Architecture schema.
        
        Args:
            plan_data: The plan dictionary to validate
            
        Returns:
            True if the plan structure is valid, False otherwise
        """
        # Check for new enhanced schema first, fall back to legacy
        if 'mission_summary' in plan_data and 'plan' in plan_data:
            return self._validate_enhanced_plan_structure(plan_data)
        
        # Legacy validation for backward compatibility
        required_fields = ['goal', 'steps']
        
        # Check required top-level fields
        for field in required_fields:
            if field not in plan_data:
                log.error(f"Plan missing required field: {field}")
                return False
        
        # Check steps structure
        steps = plan_data.get('steps', [])
        if not isinstance(steps, list) or len(steps) == 0:
            log.error("Plan has no valid steps")
            return False
        
        # Validate each step
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                log.error(f"Step {i} is not a dictionary")
                return False
            
            required_step_fields = ['step_number', 'description', 'tool_request']
            for field in required_step_fields:
                if field not in step:
                    log.error(f"Step {i} missing required field: {field}")
                    return False
        
        return True
    
    def _validate_enhanced_plan_structure(self, plan_data: Dict[str, Any]) -> bool:
        """
        Validates the enhanced Phoenix Architecture plan schema.
        
        Args:
            plan_data: The enhanced plan dictionary to validate
            
        Returns:
            True if the enhanced plan structure is valid, False otherwise
        """
        required_top_fields = ['mission_summary', 'risk_level', 'estimated_time', 'plan']
        
        # Check required top-level fields
        for field in required_top_fields:
            if field not in plan_data:
                log.error(f"Enhanced plan missing required field: {field}")
                return False
        
        # Validate risk level
        valid_risk_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        if plan_data['risk_level'] not in valid_risk_levels:
            log.error(f"Invalid risk level: {plan_data['risk_level']}")
            return False
        
        # Check plan steps structure
        steps = plan_data.get('plan', [])
        if not isinstance(steps, list) or len(steps) == 0:
            log.error("Enhanced plan has no valid steps")
            return False
        
        # Validate each step in enhanced format
        valid_phases = ['RECONNAISSANCE', 'ENUMERATION', 'SCANNING', 'ANALYSIS', 'EXPLOITATION', 'POST-EXPLOITATION']
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                log.error(f"Enhanced step {i} is not a dictionary")
                return False
            
            # Required fields - accept both old and new field names for compatibility
            if 'step' not in step:
                log.error(f"Enhanced step {i} missing required field: step")
                return False
            if 'phase' not in step:
                log.error(f"Enhanced step {i} missing required field: phase")
                return False
            if 'tool_name' not in step:
                log.error(f"Enhanced step {i} missing required field: tool_name")
                return False
            
            # Accept either 'description' (new) or 'objective' (old) for backward compatibility
            if 'description' not in step and 'objective' not in step:
                log.error(f"Enhanced step {i} missing required field: 'description' or 'objective'")
                return False
            
            # Accept either 'command_template' (new) or 'arguments' (old) for backward compatibility
            if 'command_template' not in step and 'arguments' not in step:
                log.warning(f"Enhanced step {i} missing 'command_template' or 'arguments' - will use tool selector")
            
            # Validate phase
            if step['phase'] not in valid_phases:
                log.warning(f"Step {i} has unusual phase: {step['phase']}")
        
        log.info("Enhanced plan structure validation passed")
        return True
    
    # ==========================================
    # CORE REQUEST PROCESSING
    # ==========================================
    
    def process_request(self, user_input: str, mode: Optional[str] = None) -> Dict[str, Any]:
        """
        The main entry point for all user requests. Orchestrates the entire AI pipeline.
        
        Args:
            user_input: User's natural language request
            mode: Work mode (quick, interactive, suggester) - affects response generation
        
        This method implements the complete Phoenix Architecture workflow:
        1. Intent Analysis: Understand what the user wants
        2. Intelligent Routing: Direct to appropriate processing pathway
        3. AI Processing: Execute using specialized agents
        4. Safety Assessment: Risk analysis for commands
        5. Session Management: Context and learning
        
        Args:
            user_input: The user's natural language request
            
        Returns:
            Dictionary containing the processed response with type and relevant data
        """
        log.info(f"Brain processing request: '{user_input}'")
        
        # Show thinking animation
        print(banner.get_ai_thinking_banner())
        
        # Record the interaction start time for analytics
        start_time = datetime.now()
        
        # === STEP 1: INTENT ANALYSIS ===
        success, intent_or_error = self._analyze_intent(user_input)
        if not success:
            error_msg = f"Could not analyze intent: {intent_or_error}"
            print(banner.get_error_banner("Intent Analysis Failed"))
            self._record_interaction(user_input, "intent_analysis_error", "error", success=False)
            return {'type': 'error', 'message': error_msg}
        
        intent = intent_or_error
        log.info(f"Request intent: {intent}")
        
        # === STEP 2: INTENT-BASED ROUTING ===
        
        if intent == 'introspection_request':
            result = self._handle_introspection(user_input)
            self._record_interaction(user_input, result.get('type', 'introspection'), 'introspection')
            return result

        if intent == 'general_conversation':
            result = self._handle_conversation(user_input)
            self._record_interaction(user_input, "conversation", 'conversation', success=result['type'] != 'error')
            return result

        if intent == 'explanation_request':
            # In suggester mode with "ways/options", treat as suggester request instead
            if mode == 'suggester' and self._wants_multiple_options(user_input):
                result = self._handle_suggester_request(user_input)
            else:
                result = self._handle_explanation(user_input)
            self._record_interaction(user_input, "explanation", 'explanation', success=result['type'] != 'error')
            return result
            
        if intent == 'plan_request':
            # In suggester mode with "ways/options", treat as suggester request instead
            if mode == 'suggester' and self._wants_multiple_options(user_input):
                result = self._handle_suggester_request(user_input)
            else:
                result = self._handle_planning(user_input)
            self._record_interaction(user_input, "autonomous_plan", 'plan', success=result['type'] != 'error')
            return result
        
        if intent == 'tool_request':
            # In suggester mode, check if user wants multiple options
            if mode == 'suggester' and self._wants_multiple_options(user_input):
                result = self._handle_suggester_request(user_input)
            else:
                result = self._handle_tool_request(user_input)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._record_interaction(
                user_input, 
                result.get('command', 'tool_request'), 
                'tool',
                tool_name=result.get('tool_name'),
                execution_time_ms=int(execution_time),
                success=result['type'] != 'error'
            )
            return result
        
        if intent == 'command_request':
            # Check if this is a hash generation request - handle specially
            from agent.hash_handler import HashHandler
            if HashHandler.is_hash_request(user_input):
                result = self._handle_hash_generation(user_input)
            # In suggester mode, check if user wants multiple options
            elif mode == 'suggester' and self._wants_multiple_options(user_input):
                result = self._handle_suggester_request(user_input)
            else:
                result = self._handle_command_request(user_input)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._record_interaction(
                user_input,
                result.get('command', 'command_request'),
                'command',
                execution_time_ms=int(execution_time),
                success=result['type'] != 'error'
            )
            return result
        
        if intent == 'system_operation':
            result = self._handle_system_operation(user_input)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._record_interaction(
                user_input,
                result.get('command', 'system_operation'),
                'system_operation',
                execution_time_ms=int(execution_time),
                success=result['type'] != 'error'
            )
            return result
        
        if intent == 'troubleshooting_request':
            result = self._handle_troubleshooting(user_input)
            self._record_interaction(user_input, "troubleshooting", 'troubleshooting', success=result['type'] != 'error')
            return result
        
        if intent == 'forensics_request':
            result = self._handle_forensics(user_input)
            self._record_interaction(user_input, "forensics", 'forensics', success=result['type'] != 'error')
            return result
        
        if intent == 'network_analysis':
            result = self._handle_network_analysis(user_input)
            self._record_interaction(user_input, "network_analysis", 'network', success=result['type'] != 'error')
            return result
        
        if intent == 'automation_request':
            result = self._handle_automation(user_input)
            self._record_interaction(user_input, "automation", 'automation', success=result['type'] != 'error')
            return result
        
        # Fallback for unexpected intents
        fallback_msg = f"Unhandled intent: {intent}"
        log.warning(fallback_msg)
        self._record_interaction(user_input, "unhandled_intent", "error", success=False)
        return {'type': 'error', 'message': fallback_msg}
    
    # ==========================================
    # SPECIALIZED REQUEST HANDLERS
    # ==========================================
    
    def _handle_introspection(self, user_input: str) -> Dict[str, Any]:
        """Handles built-in system commands like /help, /status."""
        command = user_input.lower().strip()
        
        if command == '/help':
            return {
                'type': 'help',
                'content': self._get_help_content()
            }
        elif command == '/status':
            return {
                'type': 'status', 
                'content': self._get_status_content()
            }
        elif command == '/list tools':
            tools = self.intelligence_selector.get_available_tools()
            return {
                'type': 'tools_list',
                'tools': tools
            }
        elif command == '/list agents':
            return {
                'type': 'agents_list',
                'agents': self._get_agents_info()
            }
        else:
            return {
                'type': 'introspection',
                'task': command
            }
    
    def _handle_conversation(self, user_input: str) -> Dict[str, Any]:
        """Handles general conversational interactions and any type of query."""
        
        # LINA is now a dual-purpose AI: cybersecurity specialist + general assistant
        # Generate intelligent response for any type of query
        
        chat_history = self.session_manager.get_conversation_context()
        
        # Create a comprehensive prompt for general AI assistance with role-based expertise
        role_context = {
            "Student": "You are LINA in Student Mode - provide detailed explanations, educational content, and step-by-step guidance. Focus on learning and understanding with clear examples.",
            "Forensic Expert": "You are LINA in Forensic Expert Mode - provide advanced digital forensics expertise, incident response guidance, and technical analysis. Focus on professional forensic workflows and methodologies.",
            "Penetration Tester": "You are LINA in Penetration Tester Mode - provide offensive security expertise, vulnerability assessment techniques, and red team tactics. Focus on ethical hacking and security testing methodologies."
        }
        
        context = role_context.get(self.expert_role, "You are LINA, a general cybersecurity AI assistant.")
        
        general_prompt = f"""{context}

User Query: "{user_input}"

**CRITICAL FORMATTING REQUIREMENTS:**
- Keep responses VERY short and concise (maximum 100 words)
- Use simple, friendly language
- For greetings like "hi", "hello", respond with a brief, warm greeting
- For simple questions, give direct answers
- Avoid bullet points and long explanations unless specifically requested
- Be conversational and natural
- Focus on being helpful without overwhelming the user

**Instructions:**
- If it's a greeting, respond warmly and briefly
- If it's a simple question, give a concise answer
- If it's cybersecurity-related, provide brief technical guidance
- If it's general knowledge, give a short, helpful response
- Always maintain LINA's friendly personality
- Tailor complexity to {self.expert_role} mode but keep it brief

Respond with a short, clean, friendly message:"""

        success, response_text = self.llm_engine.generate_response(general_prompt)
        
        if not success:
            # Fallback to basic conversation generation
            success, response_text = self.agent_core.generate_conversation(user_input, chat_history)
            
            if not success:
                return {'type': 'error', 'message': 'Sorry, I encountered an issue processing your request. Please try again.'}
        
        # Update conversation context
        self.session_manager.add_conversation_turn("user", user_input)
        self.session_manager.add_conversation_turn("assistant", response_text)
        
        return {'type': 'conversation', 'message': response_text}
    
    def _handle_explanation(self, user_input: str) -> Dict[str, Any]:
        """Handles explanation and guidance requests."""
        # Extract the topic from the user input
        topic = user_input.lower()
        for prefix in ["explain", "what is", "describe", "tell me about", "how does", "how to"]:
            topic = topic.replace(prefix, "").strip()
        
        success, explanation_text = self.agent_core.explain_topic(topic)
        
        if not success:
            print(banner.get_error_banner("Explanation Failed"))
            return {'type': 'error', 'message': explanation_text}
        
        return {'type': 'explanation', 'explanation': explanation_text}
    
    def _handle_planning(self, user_input: str) -> Dict[str, Any]:
        """Handles autonomous multi-step planning requests."""
        log.info("Processing autonomous planning request")
        print(banner.get_planning_banner())
        
        # Extract the goal from the user input
        goal = user_input.lower()
        for prefix in ["create a plan", "plan", "generate plan", "make a plan"]:
            goal = goal.replace(prefix, "").strip()
        
        if not goal or len(goal) < 5:
            goal = user_input  # Use the full input if extraction didn't work
        
        return self._generate_autonomous_plan(goal)
    
    def _handle_tool_request(self, user_input: str) -> Dict[str, Any]:
        """Handles tool-based requests using the Librarian & Scholar model."""
        log.info("Processing tool request via Intelligence Selector")
        
        # Use the unified intelligence pipeline
        success, tool_name, command = self.intelligence_selector.process_tool_request(user_input)
        
        if not success:
            log.info("Tool intelligence failed, attempting autonomous command generation")
            return self._generate_autonomous_command(user_input)
            
            # Show tool selection
            print(banner.get_tool_selection_banner(tool_name, f"Selected for: {user_input[:40]}..."))

        # Apply safety assessment
        explanation = f"AI-composed '{tool_name}' command to achieve your goal"
        return self._prepare_for_execution({
            'type': 'command',
            'command': command,
            'explanation': explanation,
            'tool_name': tool_name
        })
    
    def _handle_hash_generation(self, user_input: str) -> Dict[str, Any]:
        """Handles hash generation requests using HashService."""
        log.info("Processing hash generation request")
        
        from agent.hash_handler import HashHandler
        
        extracted = HashHandler.extract_hash_request(user_input)
        if not extracted:
            # Fall back to regular command generation
            return self._handle_command_request(user_input)
        
        hash_type, input_text, save_to_file, file_path = extracted
        
        # Generate hash and save if requested
        result = HashHandler.generate_hash_response(
            hash_type=hash_type,
            input_text=input_text,
            save_to_file=save_to_file,
            file_path=file_path
        )
        
        return result
    
    def _handle_command_request(self, user_input: str) -> Dict[str, Any]:
        """Handles direct command generation requests."""
        log.info("Processing command generation request")
        
        command, explanation = self.agent_core.parse_command(user_input)
        
        if not command:
            return {'type': 'error', 'message': "Could not generate a command for your request"}
        
        return self._prepare_for_execution({
            'type': 'command',
            'command': command,
            'explanation': explanation or "AI-generated command"
        })

    def _handle_system_operation(self, user_input: str) -> Dict[str, Any]:
        """Handles system operation requests like installations and configurations."""
        log.info("Processing system operation request")
        
        success, command, explanation = self.system_operations_agent.handle_system_operation(user_input)
        
        if not success:
            return {'type': 'error', 'message': explanation}
        
        return self._prepare_for_execution({
            'type': 'command',
            'command': command,
            'explanation': explanation
        })
    
    def _handle_troubleshooting(self, user_input: str) -> Dict[str, Any]:
        """Handles troubleshooting and error fixing requests."""
        log.info("Processing troubleshooting request")
        
        success, solution, explanation = self.system_operations_agent.handle_troubleshooting(user_input)
        
        if not success:
            return {'type': 'error', 'message': explanation}
        
        return self._prepare_for_execution({
            'type': 'command',
            'command': solution,
            'explanation': explanation
        })
    
    def _handle_forensics(self, user_input: str) -> Dict[str, Any]:
        """Handles digital forensics requests."""
        log.info("Processing forensics request")
        # Display forensics header
        print("\n🔍 [FORENSICS MODE] Digital Evidence Analysis 🔍\n")
        
        # Generate forensics command using AI
        forensics_prompt = f"""You are a digital forensics expert. Generate the appropriate command for: "{user_input}"

CRITICAL FORENSICS GUIDELINES:
- For foremost file carving: ALWAYS use "-t all" to recover ALL known file types
- For disk imaging: Use dd or dc3dd with proper block sizes
- For memory analysis: Use volatility3 with appropriate plugins
- For timeline creation: Chain fls with mactime
- For NTFS recovery: Use scrounge-ntfs for deleted files
- For firmware analysis: Use binwalk with extraction flags

FORENSICS TOOLS AND THEIR PROPER USAGE:
- foremost -t all -i [input] -o [output] (comprehensive file carving)
- volatility3 -f [memory.dmp] [plugin] (memory analysis)
- binwalk -e [firmware] -C [output_dir] (firmware extraction)
- fls -r -m [timeline.txt] [image] && mactime -b [timeline.txt] -d (timeline)
- scrounge-ntfs [device] [output_dir] (NTFS deleted file recovery)
- scalpel -c /etc/scalpel/scalpel.conf [image] (advanced file carving)
- photorec [device] (photo and file recovery)
- testdisk [device] (partition recovery)

Respond with ONLY the command(s). Chain with && if needed.

Command:"""
        
        success, command = self.llm_engine.generate_response(forensics_prompt)
        
        if not success:
            return {'type': 'error', 'message': f"Failed to generate forensics command: {command}"}
        
        command = command.strip().strip('`')
        
        return self._prepare_for_execution({
            'type': 'command',
            'command': command,
            'explanation': f"Forensics command for: {user_input}"
        })
    
    def _handle_network_analysis(self, user_input: str) -> Dict[str, Any]:
        """Handles network analysis and monitoring requests."""
        log.info("Processing network analysis request")
        
        # Generate network analysis command
        network_prompt = f"""You are a network security analyst. Generate the command for: "{user_input}"

Consider network tools:
- tcpdump, tshark (packet capture)
- netstat, ss (connections)
- iftop, nethogs (bandwidth monitoring)
- arp-scan (device discovery)
- traceroute (path analysis)

Respond with ONLY the command(s).

Command:"""
        
        success, command = self.llm_engine.generate_response(network_prompt)
        
        if not success:
            return {'type': 'error', 'message': f"Failed to generate network command: {command}"}
        
        command = command.strip().strip('`')
        
        return self._prepare_for_execution({
            'type': 'command',
            'command': command,
            'explanation': f"Network analysis command for: {user_input}"
        })
    
    def _handle_automation(self, user_input: str) -> Dict[str, Any]:
        """Handles automation and scripting requests."""
        log.info("Processing automation request")
        
        # Generate automation solution
        automation_prompt = f"""You are a security automation expert. Create a solution for: "{user_input}"

For simple tasks, provide a one-liner command.
For complex automation, create a small bash script.

Examples:
- "automate nmap scan" → Create a script with proper error handling
- "schedule daily scan" → Use cron syntax

Respond with the command or script.

Solution:"""
        
        success, response = self.llm_engine.generate_response(automation_prompt)
        
        if not success:
            return {'type': 'error', 'message': f"Failed to generate automation: {response}"}
        
        # Check if it's a script or command
        if response.strip().startswith('#!/bin/bash') or '\n' in response:
            # It's a script - return as explanation
            return {
                'type': 'explanation',
                'explanation': f"Automation script for: {user_input}\n\n{response}"
            }
        else:
            # It's a command
            return self._prepare_for_execution({
                'type': 'command',
                'command': response.strip(),
                'explanation': f"Automation command for: {user_input}"
            })

    def _generate_autonomous_command(self, user_input: str) -> Dict[str, Any]:
        """
        Generates autonomous commands when no specific tool is available.
        
        This method serves as an intelligent fallback that uses AI reasoning
        to generate appropriate commands for requests that don't match
        registered tools.
        """
        log.info(f"Generating autonomous command for: '{user_input}'")
        
        autonomous_prompt = f"""You are an expert Kali Linux penetration tester and command-line specialist.

A user has requested: "{user_input}"

Generate the most appropriate Linux/Kali command(s) to accomplish this task. Consider:
- Common penetration testing tools available in Kali Linux
- Proper command syntax and essential flags
- Security best practices
- If multiple commands are needed, chain them with && or ||

Respond with ONLY the command(s) and nothing else. No explanations or markdown formatting.

Examples:
- "scan ports on 10.0.0.1" → nmap -sS -T4 10.0.0.1
- "find subdomains of example.com" → subfinder -d example.com -silent | httpx -silent
- "check for vulnerabilities on website" → nikto -h https://target.com && whatweb https://target.com

Command:"""

        success, generated_command = self.llm_engine.generate_response(autonomous_prompt)
        
        if not success:
            return {'type': 'error', 'message': f"Failed to generate autonomous command: {generated_command}"}
        
        command = generated_command.strip().strip('`').strip('"').strip("'")
        
        if not command or len(command) < 3:
            return {'type': 'error', 'message': "Could not generate a valid command for your request"}
        
        explanation = "AI-generated autonomous command based on your request"
        log.info(f"Generated autonomous command: {command}")
        
        return self._prepare_for_execution({
            'type': 'command',
            'command': command,
            'explanation': explanation
        })
    
    def _wants_multiple_options(self, user_input: str) -> bool:
        """Check if user wants multiple command options."""
        keywords = ['two ways', 'multiple ways', 'different ways', 'alternatives', 
                   'options', 'variations', 'several', 'both ways', 'another way',
                   'ways to', 'how can i', 'show me ways', 'give me options',
                   'different methods', 'various ways']
        lower_input = user_input.lower()
        return any(keyword in lower_input for keyword in keywords)
    
    def _extract_number_of_options(self, user_input: str) -> int:
        """Extract the number of options requested by the user."""
        import re
        lower_input = user_input.lower()
        
        # Check for explicit numbers
        number_patterns = [
            (r'(\d+)\s+ways?', 1),  # "two ways", "3 ways"
            (r'(\d+)\s+options?', 1),  # "two options"
            (r'(\d+)\s+methods?', 1),  # "two methods"
        ]
        
        for pattern, group_idx in number_patterns:
            match = re.search(pattern, lower_input)
            if match:
                num = int(match.group(group_idx))
                return min(max(num, 2), 4)  # Clamp between 2 and 4
        
        # Check for word numbers
        word_numbers = {
            'two': 2, '2': 2,
            'three': 3, '3': 3,
            'four': 4, '4': 4,
            'multiple': 3, 'several': 3, 'few': 3
        }
        
        for word, num in word_numbers.items():
            if word in lower_input:
                return num
        
        # Default to 2 if nothing specified
        return 2
    
    def _handle_suggester_request(self, user_input: str) -> Dict[str, Any]:
        """
        Handle suggester mode requests - generate multiple command options.
        """
        log.info(f"Processing suggester request: '{user_input}'")
        
        # Detect requested number of options
        num_options = self._extract_number_of_options(user_input)
        
        # Use AI to generate multiple command options
        prompt = f"""You are an expert cybersecurity specialist. The user wants {num_options} different way(s) to accomplish their goal.

USER REQUEST: "{user_input}"

Generate EXACTLY {num_options} different command option(s), each using different tools or approaches. For each option, provide:
1. The complete command
2. A brief, concise explanation (1-2 sentences max) of why this approach works

Format your response as:
OPTION 1:
Command: [command here]
Explanation: [brief explanation - 1-2 sentences max]

OPTION 2:
Command: [command here]
Explanation: [brief explanation - 1-2 sentences max]

(Continue for all {num_options} options - NO MORE, NO LESS)

Make sure commands are ready to execute (replace placeholders like [PORT], [IP] with example values like 8080, 127.0.0.1).

Here are your {num_options} option(s):"""

        success, response_or_error = self.llm_engine.generate_response(prompt)
        
        if not success:
            log.error(f"Suggester generation failed: {response_or_error}")
            # Fallback to regular single command
            return self._handle_tool_request(user_input) if 'tool' in user_input.lower() else self._handle_command_request(user_input)
        
        # Parse multiple options from response
        options = self._parse_multiple_options(response_or_error)
        
        # Get requested number to validate we got the right amount
        num_options = self._extract_number_of_options(user_input)
        
        if len(options) >= num_options or (len(options) >= 2 and num_options > 4):
            # We got at least the requested number, or at least 2 options (minimum)
            # Limit to requested number if we got more
            limited_options = options[:num_options] if len(options) > num_options else options
            # Don't include explanation text - just return suggestions
            # Frontend will display only the cards
            return {
                'type': 'command',
                'command': limited_options[0][0],  # First command (for fallback)
                'explanation': None,  # No explanation text - frontend will use suggestions
                'suggestions': [{'command': cmd, 'explanation': expl} for cmd, expl in limited_options]  # All options for frontend
            }
        elif len(options) >= 1:
            # Got at least one option - return it but log a warning
            log.warning(f"Only parsed {len(options)} option(s) when {num_options} were requested. Using what we got.")
            return {
                'type': 'command',
                'command': options[0][0],
                'explanation': None,
                'suggestions': [{'command': cmd, 'explanation': expl} for cmd, expl in options]
            }
        else:
            # Parsing completely failed - fallback to single command
            log.warning(f"Failed to parse any options from suggester response. Falling back to single command.")
            return self._handle_tool_request(user_input) if 'tool' in user_input.lower() else self._handle_command_request(user_input)
    
    def _parse_multiple_options(self, response: str) -> List[Tuple[str, str]]:
        """Parse multiple command options from LLM response."""
        options = []
        lines = response.split('\n')
        
        current_option = None
        current_command = None
        current_explanation = None
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_command and current_explanation:
                    options.append((current_command, current_explanation))
                    current_command = None
                    current_explanation = None
                continue
                
            if line.upper().startswith('OPTION') or line.upper().startswith('METHOD'):
                if current_command and current_explanation:
                    options.append((current_command, current_explanation))
                current_option = line
                current_command = None
                current_explanation = None
            elif line.lower().startswith('command:'):
                current_command = line.split(':', 1)[1].strip().strip('`').strip('"').strip("'")
            elif line.lower().startswith('explanation:'):
                current_explanation = line.split(':', 1)[1].strip()
            elif current_command and not current_explanation:
                # Continue building explanation
                if current_explanation is None:
                    current_explanation = line
                else:
                    current_explanation += " " + line
        
        # Add last option
        if current_command and current_explanation:
            options.append((current_command, current_explanation))
        
        # If parsing failed, try to extract commands directly
        if len(options) < 2:
            import re
            # Try to find command patterns
            command_pattern = r'`([^`]+)`|Command:\s*([^\n]+)'
            commands = re.findall(command_pattern, response)
            for match in commands:
                cmd = match[0] or match[1]
                if cmd and cmd.strip() and len(cmd.strip()) > 5:
                    # Simple explanation
                    options.append((cmd.strip(), "Alternative approach"))
                    if len(options) >= 4:
                        break
        
        # Return all parsed options (will be limited to requested number by caller)
        return options
    
    # ==========================================
    # SAFETY AND RISK MANAGEMENT
    # ==========================================
    
    def _prepare_for_execution(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies mandatory safety assessment to commands before execution.
        
        Args:
            item: Dictionary containing command information
            
        Returns:
            Updated dictionary with risk assessment
        """
        command_to_check = item['command']
        log.info(f"Performing safety assessment on: '{command_to_check}'")
        
        risk_assessment = self.risk_manager.assess_risk(command_to_check)
        item['risk'] = risk_assessment
        
        return item
    
    # ==========================================
    # SESSION MANAGEMENT AND ANALYTICS
    # ==========================================
    
    def _record_interaction(self, user_input: str, executed_action: str, action_type: str,
                          tool_name: str = None, output: str = None, risk_assessment: Any = None,
                          execution_time_ms: int = None, success: bool = True):
        """
        Records interaction in session management system.

        Args:
            user_input: Original user request
            executed_action: Action that was executed
            action_type: Type of action performed
            tool_name: Tool used (if applicable)
            output: Output or result
            risk_assessment: Risk assessment dictionary or string
            execution_time_ms: Execution time in milliseconds
            success: Whether the action succeeded
        """
        # Convert risk assessment dictionary to JSON string for storage
        risk_assessment_str = json.dumps(risk_assessment) if isinstance(risk_assessment, dict) else risk_assessment

        self.session_manager.add_interaction(
            user_input=user_input,
            executed_action=executed_action,
            action_type=action_type,
            tool_name=tool_name,
            output=output,
            risk_assessment=risk_assessment_str,
            execution_time_ms=execution_time_ms,
            success=success
        )
    
    # ==========================================
    # UTILITY AND STATUS METHODS
    # ==========================================
    
    def _get_help_content(self) -> str:
        """Returns comprehensive help content."""
        return """
LINA - Phoenix Architecture Help

Available Commands:
• /help - Show this help message
• /status - Display system status
• /list tools - Show available tools
• /list agents - Show active agents

Natural Language Examples:
• "scan ports on 192.168.1.1"
• "create a plan to test website security"
• "explain SQL injection"
• "find subdomains of example.com"
• "What is nmap?"

System Operations:
• "install nmap" - Install tools via apt/pip/go
• "setup metasploit" - Configure complex tools
• "fix permission denied error" - Troubleshooting
• "configure postgresql" - Service configuration

Forensics & Analysis:
• "analyze memory dump" - Memory forensics
• "recover deleted files" - File recovery
• "monitor network traffic" - Live monitoring
• "create disk image" - Evidence preservation

Automation:
• "automate daily scan" - Create scheduled tasks
• "create script for port scanning" - Generate scripts
• "schedule vulnerability checks" - Cron automation

Planning Examples:
• "create a plan to assess network security"
• "plan a web application penetration test"
• "generate a recon strategy for target.com"

Type any cybersecurity request in natural language!
        """
    
    def _get_status_content(self) -> Dict[str, Any]:
        """Returns comprehensive system status."""
        session_summary = self.session_manager.get_session_summary()
        learning_insights = self.session_manager.get_learning_insights()
        
        return {
            'brain_status': 'ONLINE',
            'architecture': 'Phoenix',
            'agents': {
                'agent_core': 'ACTIVE',
                'intelligence_selector': 'ACTIVE', 
                'session_manager': 'ACTIVE',
                'risk_manager': 'ACTIVE'
            },
            'session': session_summary,
            'insights': learning_insights,
            'tools_available': len(self.intelligence_selector.get_available_tools())
        }
    
    def _get_agents_info(self) -> List[Dict[str, str]]:
        """Returns information about active agents."""
        return [
            {
                'name': 'AgentCore',
                'role': 'Natural Language Processing',
                'capabilities': 'Command parsing, explanations, conversations'
            },
            {
                'name': 'IntelligenceSelector', 
                'role': 'Tool Intelligence (Librarian & Scholar)',
                'capabilities': 'Tool selection and command composition'
            },
            {
                'name': 'RiskManager',
                'role': 'Safety Assessment',
                'capabilities': 'Command risk analysis and guidance'
            },
            {
                'name': 'SessionManager',
                'role': 'Context & Learning',
                'capabilities': 'Session tracking, memory, analytics'
            },
            {
                'name': 'SystemOperationsAgent',
                'role': 'System Operations & Administration',
                'capabilities': 'Tool installation, configuration, troubleshooting'
            },
            {
                'name': 'ForensicsManager',
                'role': 'Digital Forensics',
                'capabilities': 'Memory analysis, disk imaging, evidence handling'
            }
        ]
    
    def get_session_manager(self) -> SessionManager:
        """Returns the session manager for external access."""
        return self.session_manager
    
    def get_brain_summary(self) -> Dict[str, Any]:
        """Returns a comprehensive summary of Brain capabilities."""
        return {
            'architecture': 'Phoenix',
            'version': __version__,
            'capabilities': [
                'Intent Analysis',
                'Autonomous Planning',
                'Tool Intelligence', 
                'Natural Language Processing',
                'Risk Assessment',
                'Session Management'
            ],
            'agents': len(self._get_agents_info()),
            'tools': len(self.intelligence_selector.get_available_tools())
        }