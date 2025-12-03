/**
 * Command Execution Component
 * Displays command with risk assessment and execution UI
 */
import { useState, useEffect, useCallback } from 'react';
import { Play, X, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import type { ProcessResponse, RiskLevel } from '../types';
import { commandAPI } from '../services/api';

interface CommandExecutorProps {
  response: ProcessResponse;
  sessionId: string;
  onExecute?: () => void;
  onCancel?: () => void;
}

const riskColors: Record<RiskLevel, string> = {
  SAFE: 'risk-safe',
  LOW: 'risk-low',
  MEDIUM: 'risk-medium',
  HIGH: 'risk-high',
  RISKY: 'risk-high',
  CRITICAL: 'risk-critical',
  BLOCKED: 'risk-blocked',
  UNKNOWN: 'risk-unknown',
};

export default function CommandExecutor({
  response,
  sessionId,
  onExecute,
  onCancel,
}: CommandExecutorProps) {
  const { theme } = useTheme();
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<string | null>(null);
  const [showConfirm, setShowConfirm] = useState(false); // Auto-execute, no confirmation needed
  const [autoExecuted, setAutoExecuted] = useState(false);

  const risk = response.risk;
  const command = response.command || '';
  const toolName = response.tool_name || 'Unknown';
  const explanation = response.explanation || '';

  const handleExecute = useCallback(async () => {
    if (!command) return;

    setIsExecuting(true);
    setShowConfirm(false);
    setExecutionResult(null);

    try {
      // Execute command automatically (auto_confirm=true)
      const result = await commandAPI.execute(sessionId, command, true, 'background');
      
      // Start polling for output if execution_id is available
      if (result.execution_id) {
        pollExecutionOutput(result.execution_id);
      } else {
        setExecutionResult(result.output || 'Command executed');
        setIsExecuting(false);
      }
      
      onExecute?.();
    } catch (error: any) {
      setExecutionResult(`Error: ${error.message || 'Execution failed'}`);
      setIsExecuting(false);
    }
  }, [command, sessionId, onExecute]);

  // Auto-execute ONLY in interactive/suggester mode (not in quick mode)
  // Quick mode bypasses CommandExecutor entirely
  useEffect(() => {
    // Only auto-execute if explicitly set (for interactive mode)
    // In quick mode, this component shouldn't even render
    if (command && !autoExecuted && !isExecuting) {
      // Don't auto-execute by default - wait for user confirmation in interactive mode
      // User will click execute button
    }
  }, [command, autoExecuted, isExecuting]);

  const pollExecutionOutput = async (executionId: string) => {
    let attempts = 0;
    const maxAttempts = 120; // 2 minutes max
    
    const poll = async () => {
      try {
        const result = await commandAPI.getStatus(executionId);
        
        if (result.output) {
          setExecutionResult(result.output);
        }
        
        if (result.status === 'completed' || result.status === 'failed') {
          setIsExecuting(false);
          if (result.output) {
            setExecutionResult(result.output);
          }
          if (result.error) {
            setExecutionResult((prev) => `${prev || ''}\n\nError: ${result.error}`);
          }
          return;
        }

        // Continue polling
        if (result.status === 'running' && attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 500); // Poll every 500ms for faster updates
        } else {
          setIsExecuting(false);
        }
      } catch (error) {
        console.error('Polling error:', error);
        setIsExecuting(false);
      }
    };

    poll();
  };

  const handleCancel = () => {
    setIsExecuting(false);
    setExecutionResult(null);
    onCancel?.();
  };

  const riskLevel = risk?.level || 'UNKNOWN';
  const riskColor = riskColors[riskLevel] || riskColors.UNKNOWN;
  const requiresConfirmation = riskLevel === 'HIGH' || riskLevel === 'RISKY' || riskLevel === 'CRITICAL' || riskLevel === 'BLOCKED';

  return (
    <div className="bg-white dark:bg-dark-bg-secondary border-2 border-gray-300 dark:border-dark-border rounded-lg p-2.5 space-y-2 shadow-sm">
      {/* Command Preview */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <h3 className="text-xs font-bold text-gray-900 dark:text-dark-text">Command Preview</h3>
          <span className="text-xs font-semibold text-gray-600 dark:text-dark-text-secondary">Tool: {toolName}</span>
        </div>
        <div className="bg-gray-900 border-2 border-cyber-blue text-terminal-green font-mono p-2 rounded-lg mb-1.5 text-xs">
          <code>{command}</code>
        </div>
        {explanation && (
          <p className="text-xs text-gray-700 dark:text-dark-text-secondary mb-1.5">{explanation}</p>
        )}
      </div>

      {/* Risk Assessment */}
      {risk && (
        <div className={`border-2 rounded-lg p-2 ${riskColor}`}>
          <div className="flex items-center space-x-1.5 mb-1">
            {riskLevel === 'CRITICAL' || riskLevel === 'BLOCKED' ? (
              <AlertTriangle className="w-3 h-3" />
            ) : (
              <CheckCircle className="w-3 h-3" />
            )}
            <span className="font-bold text-xs">Risk: {riskLevel}</span>
          </div>
          {risk.reason && (
            <p className="text-xs mt-1">{risk.reason}</p>
          )}
          {risk.pattern_matched && (
            <p className="text-xs mt-1 opacity-75">Pattern: {risk.pattern_matched}</p>
          )}
        </div>
      )}

      {/* Execute Button - User must click in interactive mode */}
      {!isExecuting && !executionResult && command && (
        <button
          onClick={handleExecute}
          className="w-full px-4 py-2 rounded-lg font-bold text-white transition-all hover:scale-105 shadow-md flex items-center justify-center space-x-2 text-xs"
          style={{
            background: theme === 'dark' 
              ? 'linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)'
              : 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
          }}
        >
          <Play className="w-3 h-3" />
          <span>Execute Command</span>
        </button>
      )}

      {/* Execution Status */}
      {isExecuting && (
        <div className="space-y-2">
          <div className="flex items-center space-x-2 text-cyber-blue">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Executing command...</span>
          </div>
          
          {/* Real-time Output */}
          {executionResult && (
            <div className="terminal max-h-64 overflow-auto custom-scrollbar">
              <pre className="text-terminal-green whitespace-pre-wrap">
                {executionResult}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Execution Result */}
      {!isExecuting && executionResult && (
        <div className="space-y-2">
          <div className="flex items-center space-x-2 text-green-600">
            <CheckCircle className="w-4 h-4" />
            <span>Command completed</span>
          </div>
          <div className="terminal max-h-64 overflow-auto custom-scrollbar">
            <pre className="text-terminal-green whitespace-pre-wrap">{executionResult}</pre>
          </div>
        </div>
      )}
    </div>
  );
}

