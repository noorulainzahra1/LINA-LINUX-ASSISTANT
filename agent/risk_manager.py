# agent/risk_manager.py
# Architect: This component acts as a crucial safety layer for the framework.
#
# This definitive version implements a two-layered, hybrid risk assessment system:
# - Layer 1 (Static Guard): Instantly checks commands against a local database
#   of known risky patterns using regex. This is extremely fast and costs nothing.
# - Layer 2 (Intelligent Analyst): If no static match is found, it queries the
#   LLM for a dynamic, intelligent assessment of the command's potential risk.
# It correctly receives its dependencies (router, paths) via injection from the Brain
# and provides more context-aware assessments for tools with arguments.

import os
import json
import re
from typing import Optional, Dict, Any

from agent.llm_engine import LLMEngine
from utils.logger import log

class RiskManager:
    """
    Assesses command risk using a two-layered static and dynamic approach.
    It is the final safety gate before any command is executed.
    """
    def __init__(self, llm_engine: LLMEngine, risk_database_path: str):
        """
        Initializes the RiskManager.
        Args:
            llm_engine: An instance of the LLMEngine for AI reasoning.
            risk_database_path: The absolute path to the risk_database.json file.
        """
        self.llm_engine = llm_engine
        self.risk_database_path = risk_database_path
        self.risk_database = self._load_risk_database()
        self.prompt_template = self._load_prompt_template()

    def _load_risk_database(self) -> Dict[str, Any]:
        """Loads the static risk database from the provided path."""
        try:
            with open(self.risk_database_path, 'r') as f:
                log.info(f"Static risk database loaded from {self.risk_database_path}.")
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log.error(f"Could not load or parse static risk database at {self.risk_database_path}: {e}. Static checks will be disabled.")
            return {}

    def _load_prompt_template(self) -> str:
        """Loads the prompt used for dynamic, LLM-based risk analysis."""
        try:
            base_dir = os.path.dirname(__file__)
            path = os.path.join(base_dir, "prompts", "risk_prompt.txt")
            with open(path, 'r', encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            log.critical("FATAL: risk_prompt.txt not found. Dynamic risk analysis is impossible.")
            raise

    def _check_static_database(self, command: str) -> Optional[str]:
        """Layer 1: Checks the command against pre-defined regex patterns."""
        for pattern, risk_info in self.risk_database.items():
            try:
                if re.search(pattern, command):
                    log.info(f"Static risk match found for command '{command}' with pattern '{pattern}'.")
                    return f"{risk_info.get('risk', 'UNKNOWN')}: {risk_info.get('explanation', 'No explanation provided.')}"
            except re.error as e:
                log.warning(f"Invalid regex pattern in risk_database.json: '{pattern}'. Error: {e}")
        return None

    def assess_risk(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Performs a comprehensive two-layered risk assessment on a given command or tool.
        
        Enhanced Flow:
        1. Check static risk database for known dangerous patterns (instant)
        2. Use LLM for intelligent context-aware analysis (comprehensive)
        3. Combine both assessments for maximum safety

        Args:
            command: The command string or tool name to be assessed.
            args: Optional dictionary of arguments if a tool is being assessed.

        Returns:
            A dictionary with 'level', 'reason', 'explanation', 'database_match', and 'ai_analysis' keys.
        """
        if not command:
            return {
                'level': 'UNKNOWN',
                'reason': 'No command provided for risk assessment.',
                'explanation': 'No command provided for risk assessment.',
                'database_match': None,
                'ai_analysis': None
            }

        # === LAYER 1: STATIC DATABASE CHECK (FAST) ===
        database_match = None
        static_risk_level = None
        static_risk_reason = None
        
        if not args:  # Only check database for raw shell commands
            static_result = self._check_static_database(command)
            if static_result:
                database_match = static_result
                if "SAFE" in static_result.upper():
                    static_risk_level = 'SAFE'
                    static_risk_reason = 'Command matched safe pattern in risk database'
                else:
                    static_risk_level = static_result.split(": ", 1)[0] if ": " in static_result else "UNKNOWN"
                    static_risk_reason = static_result.split(": ", 1)[1] if ": " in static_result else static_result
                
                log.info(f"Database Match Found - Level: {static_risk_level}, Reason: {static_risk_reason}")

        # === LAYER 2: AI INTELLIGENT ANALYSIS (COMPREHENSIVE) ===
        # Always perform AI analysis for comprehensive assessment
        ai_analysis = None
        ai_risk_level = None
        ai_risk_reason = None
        
        if args is not None:
            prompt_context = f"Assess the risk of running the tool '{command}' with the arguments: {json.dumps(args)}"
        else:
            prompt_context = f"Assess the risk of running the Linux command: `{command}`"
        
        log.info(f"Performing AI risk assessment for: {prompt_context}")
        prompt = self.prompt_template.format(command=prompt_context)
        
        success, response_or_error = self.llm_engine.generate_response(prompt)

        if success:
            response = response_or_error
            if "GENERATION_BLOCKED" in response:
                ai_analysis = "AI safety filter blocked the assessment"
                ai_risk_level = 'BLOCKED'
                ai_risk_reason = 'AI safety filter blocked the risk assessment; treat as potentially risky.'
            elif response.lower().startswith("risky:"):
                ai_risk_reason = response[len("Risky:"):].strip()
                ai_risk_level = 'RISKY'
                ai_analysis = ai_risk_reason
                log.warning(f"AI Risk Detected: {ai_risk_reason}")
            elif response.lower().strip() == "safe":
                ai_risk_level = 'SAFE'
                ai_risk_reason = 'AI analysis confirms command is safe'
                ai_analysis = 'Safe operation confirmed by AI analysis'
                log.info(f"AI Assessment: Command is SAFE")
            else:
                ai_analysis = response
                ai_risk_level = 'UNKNOWN'
                ai_risk_reason = f'Unexpected AI response format'
                log.warning(f"Unexpected AI response: '{response}'")
        else:
            log.error(f"AI risk assessment failed: {response_or_error}")
            ai_analysis = f"AI analysis failed: {response_or_error}"
            ai_risk_level = 'UNKNOWN'
            ai_risk_reason = 'Risk assessment failed due to an API error'

        # === LAYER 3: COMBINED ASSESSMENT ===
        # Combine both assessments with priority to highest risk
        final_level = self._determine_final_risk_level(static_risk_level, ai_risk_level)
        final_reason = self._combine_risk_reasons(static_risk_reason, ai_risk_reason, final_level)
        
        log.info(f"Final Risk Assessment - Level: {final_level}")
        
        return {
            'level': final_level,
            'reason': final_reason,
            'explanation': final_reason,  # Add explanation field for compatibility
            'database_match': database_match,
            'ai_analysis': ai_analysis
        }

    def _determine_final_risk_level(self, static_level: Optional[str], ai_level: Optional[str]) -> str:
        """
        Determines the final risk level by combining static and AI assessments.
        Priority: CRITICAL > BLOCKED > RISKY > HIGH > MEDIUM > LOW > UNKNOWN > SAFE
        """
        risk_priority = {
            'CRITICAL': 7,
            'BLOCKED': 6,
            'RISKY': 5,
            'HIGH': 4,
            'MEDIUM': 3,
            'LOW': 2,
            'UNKNOWN': 1,
            'SAFE': 0
        }
        
        static_priority = risk_priority.get(static_level, -1) if static_level else -1
        ai_priority = risk_priority.get(ai_level, -1) if ai_level else -1
        
        # Return the higher risk level
        if static_priority >= ai_priority:
            return static_level if static_level else 'UNKNOWN'
        else:
            return ai_level if ai_level else 'UNKNOWN'
    
    def _combine_risk_reasons(self, static_reason: Optional[str], ai_reason: Optional[str], final_level: str) -> str:
        """
        Combines reasons from both assessment layers into a comprehensive explanation.
        """
        reasons = []
        
        if static_reason:
            reasons.append(f"Database: {static_reason}")
        
        if ai_reason:
            reasons.append(f"AI Analysis: {ai_reason}")
        
        if not reasons:
            return "No specific risk information available"
        
        return " | ".join(reasons)