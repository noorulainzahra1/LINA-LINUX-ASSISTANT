/**
 * TypeScript types for LINA Frontend
 */

export type UserRole = "Student" | "Forensic Expert" | "Penetration Tester";

export type WorkMode = "quick" | "interactive" | "suggester";

export type RiskLevel = "SAFE" | "LOW" | "MEDIUM" | "HIGH" | "RISKY" | "CRITICAL" | "BLOCKED" | "UNKNOWN";

export type ResponseType = "command" | "conversation" | "explanation" | "autonomous_plan" | "tools_list" | "error" | "introspection";

export type ExecutionStatus = "running" | "completed" | "failed" | "cancelled";

export interface Session {
  session_id: string;
  role: UserRole;
  mode?: WorkMode;
  ai_engine: string;
  created_at: string;
  status: string;
}

export interface RiskAssessment {
  level: RiskLevel;
  confidence?: number;
  reason?: string;
  database_match?: boolean;
  pattern_matched?: string;
}

export interface CommandPreview {
  command: string;
  tool_name: string;
  explanation: string;
  risk: RiskAssessment;
  requires_confirmation: boolean;
}

export interface ProcessResponse {
  type: ResponseType;
  message?: string;
  command?: string;
  tool_name?: string;
  explanation?: string;
  risk?: RiskAssessment;
  plan?: {
    title: string;
    description: string;
    steps: Array<{
      step: number;
      description: string;
      tool?: string;
      command?: string;
    }>;
  };
  tools?: ToolInfo[];
  error?: string;
  suggestions?: Array<{ command: string; explanation: string }>;  // Multiple command options for suggester mode
}

export interface CommandExecution {
  execution_id: string;
  command: string;
  status: ExecutionStatus;
  output?: string;
  return_code?: number;
  start_time: string;
  end_time?: string;
  error?: string;
}

export interface ToolInfo {
  name: string;
  description: string;
  category: string;
  keywords: string[];
  risk_level: string;
  installed: boolean;
}

export interface SessionStatus {
  session_id: string;
  role: UserRole;
  ai_engine: string;
  created_at: string;
  last_activity: string;
  command_count: number;
  tools_used: string[];
  session_duration: string;
}

export interface SessionAnalytics {
  session_id: string;
  duration_minutes: number;
  commands_executed: number;
  unique_tools_used: number;
  conversations: number;
  explanations_requested: number;
  plans_generated: number;
  tools_used_list: string[];
  learning_insights?: Record<string, any>;
}

export interface CommandHistoryEntry {
  command: string;
  timestamp: string;
  tool_name?: string;
  success?: boolean;
}

