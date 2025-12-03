"""
Simple banner module for LINA
Provides minimal banner display functionality
"""

def display_main_banner():
    """Display main banner - minimal implementation"""
    pass

def display_role_banner(role: str):
    """Display role-specific banner - minimal implementation"""
    pass

def get_ai_thinking_banner():
    """Get AI thinking banner - minimal implementation"""
    return "🤔 AI Processing..."

def get_error_banner(message: str):
    """Get error banner - minimal implementation"""
    return f"❌ Error: {message}"

def get_planning_banner():
    """Get planning banner - minimal implementation"""
    return "📋 Planning..."

def get_tool_selection_banner(tool_name: str, context: str = ""):
    """Get tool selection banner - minimal implementation"""
    return f"🔧 Using: {tool_name}"

