/**
 * WebSocket hook for real-time command output streaming
 */
import { useEffect, useRef, useState, useCallback } from 'react';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export interface UseCommandStreamReturn {
  output: string;
  isConnected: boolean;
  isExecuting: boolean;
  error: string | null;
  executeCommand: (command: string, executionMode?: 'persistent' | 'background') => void;
  clearOutput: () => void;
  disconnect: () => void;
}

export function useCommandStream(sessionId: string | null): UseCommandStreamReturn {
  const [output, setOutput] = useState<string>('');
  const [isConnected, setIsConnected] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const executionIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    // Connect to WebSocket
    const ws = new WebSocket(`${WS_URL}/ws/session/${sessionId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    ws.onerror = (event) => {
      setError('WebSocket connection error');
      setIsConnected(false);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleMessage(message);
      } catch {
        // Not JSON, treat as plain text
        setOutput((prev) => prev + event.data);
      }
    };

    const handleMessage = (message: any) => {
      switch (message.type) {
        case 'output':
          setOutput((prev) => prev + message.data);
          if (message.execution_id) {
            executionIdRef.current = message.execution_id;
          }
          break;
        case 'status':
          if (message.status === 'running') {
            setIsExecuting(true);
          }
          if (message.execution_id) {
            executionIdRef.current = message.execution_id;
          }
          break;
        case 'complete':
          setIsExecuting(false);
          if (message.data) {
            setOutput((prev) => prev + message.data);
          }
          if (message.error) {
            setError(message.error);
          }
          executionIdRef.current = null;
          break;
        case 'error':
          setError(message.data || 'An error occurred');
          setIsExecuting(false);
          break;
      }
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [sessionId]);

  const executeCommand = useCallback(
    (command: string, executionMode: string = 'background') => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        setError('Not connected to WebSocket');
        return;
      }

      setOutput('');
      setError(null);
      setIsExecuting(true);

      wsRef.current.send(JSON.stringify({
        type: 'execute',
        command,
        execution_mode: executionMode,
      }));
    },
    [isConnected]
  );

  const clearOutput = useCallback(() => {
    setOutput('');
    setError(null);
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  return {
    output,
    isConnected,
    isExecuting,
    error,
    executeCommand,
    clearOutput,
    disconnect,
  };
}

