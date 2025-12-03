/**
 * API client for LINA backend
 */
import axios from 'axios';
import type {
  Session,
  ProcessResponse,
  CommandExecution,
  ToolInfo,
  SessionStatus,
  SessionAnalytics,
  CommandHistoryEntry,
} from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 second timeout for API calls
});

// Add request interceptor for better error handling
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
      console.error('[API] Connection refused - is the backend server running?');
      error.message = 'Cannot connect to backend server. Please ensure the API server is running on ' + API_URL;
    } else if (error.code === 'ETIMEDOUT') {
      console.error('[API] Request timeout');
      error.message = 'Request timed out. The backend may be slow or unavailable.';
    }
    return Promise.reject(error);
  }
);

// Session endpoints
export const sessionAPI = {
  create: async (role: string, ai_engine?: string, mode?: string): Promise<Session> => {
    const response = await apiClient.post('/api/session/create', {
      role,
      ai_engine: ai_engine || 'Cloud AI (Google Gemini)',
      mode: mode,
    });
    return response.data;
  },

  getStatus: async (sessionId: string): Promise<SessionStatus> => {
    const response = await apiClient.get(`/api/session/${sessionId}/status`);
    return response.data;
  },

  getHistory: async (sessionId: string): Promise<CommandHistoryEntry[]> => {
    const response = await apiClient.get(`/api/session/${sessionId}/history`);
    return response.data;
  },

  getAnalytics: async (sessionId: string): Promise<SessionAnalytics> => {
    const response = await apiClient.get(`/api/session/${sessionId}/analytics`);
    return response.data;
  },

  delete: async (sessionId: string): Promise<void> => {
    await apiClient.delete(`/api/session/${sessionId}`);
  },
};

// Request processing endpoints
export const requestAPI = {
  process: async (sessionId: string, userInput: string): Promise<ProcessResponse> => {
    const response = await apiClient.post('/api/request/process', {
      session_id: sessionId,
      user_input: userInput,
    });
    return response.data;
  },
};

// Command execution endpoints
export const commandAPI = {
  execute: async (
    sessionId: string,
    command: string,
    autoConfirm: boolean = false,
    executionMode?: 'persistent' | 'separate' | 'background'
  ): Promise<CommandExecution> => {
    const response = await apiClient.post('/api/command/execute', {
      session_id: sessionId,
      command,
      auto_confirm: autoConfirm,
      execution_mode: executionMode || 'persistent',
    });
    return response.data;
  },

  getStatus: async (executionId: string): Promise<CommandExecution> => {
    const response = await apiClient.get(`/api/command/execution/${executionId}`);
    return response.data;
  },

  cancel: async (executionId: string): Promise<void> => {
    await apiClient.post(`/api/command/execution/${executionId}/cancel`);
  },
};

// Tools endpoints
export const toolsAPI = {
  list: async (): Promise<{ tools: ToolInfo[]; total_count: number; installed_count: number; categories: string[] }> => {
    const response = await apiClient.get('/api/tools/list');
    return response.data;
  },

  getInfo: async (toolName: string): Promise<ToolInfo> => {
    const response = await apiClient.get(`/api/tools/${toolName}`);
    return response.data;
  },

  execute: async (
    toolName: string,
    parameters: Record<string, any>,
    sessionId: string
  ): Promise<any> => {
    const response = await apiClient.post(`/api/tools/${toolName}/execute`, {
      tool_name: toolName,
      parameters,
      session_id: sessionId,
    });
    return response.data;
  },
};

// Hash generation endpoints
export const hashAPI = {
  generate: async (
    inputText: string,
    hashType: string = 'sha256',
    saveToFile: boolean = false,
    outputPath?: string
  ): Promise<any> => {
    const response = await apiClient.post('/api/hash/generate', {
      input_text: inputText,
      hash_type: hashType,
      save_to_file: saveToFile,
      output_path: outputPath,
    });
    return response.data;
  },
};

// File management endpoints
export const filesAPI = {
  save: async (
    filename: string,
    content: string,
    directory?: string
  ): Promise<any> => {
    const response = await apiClient.post('/api/files/save', {
      filename,
      content,
      directory,
    });
    return response.data;
  },
};

export default apiClient;

