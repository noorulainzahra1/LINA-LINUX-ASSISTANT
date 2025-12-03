"""
Pydantic models for LINA API request/response schemas
"""
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ==========================================
# Request Models
# ==========================================

class SessionCreateRequest(BaseModel):
    """Request to create a new session"""
    role: Literal["Student", "Forensic Expert", "Penetration Tester"] = Field(
        ..., 
        description="User role for the session"
    )
    ai_engine: Optional[str] = Field(
        default="Cloud AI (Google Gemini)",
        description="AI engine to use"
    )
    mode: Optional[Literal["quick", "interactive", "suggester"]] = Field(
        default=None,
        description="Work mode (quick, interactive, suggester)"
    )


class ProcessRequest(BaseModel):
    """Request to process a user's natural language input"""
    user_input: str = Field(
        ...,
        min_length=1,
        description="Natural language request from the user"
    )
    session_id: str = Field(
        ...,
        description="Session ID to process request within"
    )


class CommandExecuteRequest(BaseModel):
    """Request to execute a command"""
    command: str = Field(
        ...,
        min_length=1,
        description="Command to execute"
    )
    session_id: str = Field(
        ...,
        description="Session ID"
    )
    auto_confirm: bool = Field(
        default=False,
        description="Skip confirmation prompts (for automated execution)"
    )
    execution_mode: Optional[Literal["persistent", "separate", "background"]] = Field(
        default="persistent",
        description="Execution mode (persistent tmux session, separate terminal, or background with output capture)"
    )


# ==========================================
# Response Models
# ==========================================

class SessionResponse(BaseModel):
    """Session information response"""
    session_id: str
    role: str
    ai_engine: str
    created_at: datetime
    status: str = Field(default="active")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RiskAssessment(BaseModel):
    """Risk assessment information"""
    level: str = Field(..., description="Risk level: SAFE, LOW, MEDIUM, HIGH, RISKY, CRITICAL, BLOCKED")
    confidence: Optional[float] = Field(None, description="Confidence score (0-1)")
    reason: Optional[str] = Field(None, description="Reason for the risk level")
    database_match: Optional[Any] = Field(None, description="Database match information (can be string or bool)")
    pattern_matched: Optional[str] = Field(None, description="Matched risk pattern if applicable")
    ai_analysis: Optional[str] = Field(None, description="AI analysis of the risk")
    explanation: Optional[str] = Field(None, description="Risk explanation")


class CommandPreview(BaseModel):
    """Command preview before execution"""
    command: str
    tool_name: str
    explanation: str
    risk: RiskAssessment
    requires_confirmation: bool = Field(..., description="Whether user confirmation is required")


class ProcessResponse(BaseModel):
    """Response from processing a user request"""
    type: Literal["command", "conversation", "explanation", "autonomous_plan", "tools_list", "error", "introspection"]
    message: Optional[str] = None
    command: Optional[str] = None
    tool_name: Optional[str] = None
    explanation: Optional[str] = None
    risk: Optional[RiskAssessment] = None
    plan: Optional[Dict[str, Any]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    suggestions: Optional[List[Dict[str, str]]] = None  # For suggester mode: multiple command options


class CommandExecutionResponse(BaseModel):
    """Response from command execution"""
    execution_id: str
    command: str
    status: Literal["running", "completed", "failed", "cancelled"]
    output: Optional[str] = None
    return_code: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionStatusResponse(BaseModel):
    """Session status information"""
    session_id: str
    role: str
    ai_engine: str
    created_at: datetime
    last_activity: datetime
    command_count: int
    tools_used: List[str]
    session_duration: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CommandHistoryEntry(BaseModel):
    """Single command history entry"""
    command: str
    timestamp: datetime
    tool_name: Optional[str] = None
    success: Optional[bool] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionAnalyticsResponse(BaseModel):
    """Session analytics and statistics"""
    session_id: str
    duration_minutes: float
    commands_executed: int
    unique_tools_used: int
    conversations: int
    explanations_requested: int
    plans_generated: int
    tools_used_list: List[str]
    learning_insights: Optional[Dict[str, Any]] = None


class ToolInfo(BaseModel):
    """Information about a cybersecurity tool"""
    name: str
    description: str
    category: str
    keywords: List[str]
    risk_level: str
    installed: bool = Field(default=False, description="Whether the tool is installed on the system")


class ToolsListResponse(BaseModel):
    """Response containing list of available tools"""
    tools: List[ToolInfo]
    total_count: int
    installed_count: int
    categories: List[str]


class ToolExecuteRequest(BaseModel):
    """Request to execute a tool with parameters"""
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool parameters (flags, values, file paths, etc.)"
    )
    session_id: str = Field(..., description="Session ID")


class ToolExecutionResponse(BaseModel):
    """Response from tool execution"""
    success: bool
    tool_name: str
    command: Optional[str] = None
    output: Optional[str] = None
    parsed_output: Optional[Dict[str, Any]] = None
    progress: Optional[Dict[str, Any]] = None
    workflow_results: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    return_code: Optional[int] = None
    execution_id: Optional[str] = None  # If execution is asynchronous


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None

