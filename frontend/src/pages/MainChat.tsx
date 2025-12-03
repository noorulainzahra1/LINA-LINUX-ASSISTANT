/**
 * Main Chat Interface
 * Primary interface for interacting with LINA
 */
import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, Bot, User, Terminal, BarChart3, Zap, MessageCircle, Lightbulb, Home, ChevronDown } from 'lucide-react';
import { useSession } from '../contexts/SessionContext';
import { useTheme } from '../contexts/ThemeContext';
import { requestAPI, commandAPI, toolsAPI, filesAPI } from '../services/api';
import CommandExecutor from '../components/CommandExecutor';
import TerminalOutput from '../components/TerminalOutput';
import SideNavbar from '../components/SideNavbar';
import ToolExecutor from '../components/ToolExecutor';
import type { ProcessResponse, WorkMode, ToolInfo } from '../types/index';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  response?: ProcessResponse;
}

export default function MainChat() {
  const navigate = useNavigate();
  const { session, clearSession, mode, setMode } = useSession();
  const { theme } = useTheme();
  const [showModeDropdown, setShowModeDropdown] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  
  // Terminal output state
  const [terminalCommand, setTerminalCommand] = useState<string>('');
  const [terminalOutput, setTerminalOutput] = useState<string>('');
  const [terminalTool, setTerminalTool] = useState<string>('');
  const [isTerminalExecuting, setIsTerminalExecuting] = useState(false);
  const [currentExecutionId, setCurrentExecutionId] = useState<string | null>(null);

  // Sidebar state
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedTool, setSelectedTool] = useState<ToolInfo | null>(null);

  // Define pollExecutionResult function with useCallback
  const pollExecutionResult = useCallback(async (executionId: string) => {
    let attempts = 0;
    const maxAttempts = 300;
    let polling = true;

    const poll = async () => {
      if (!polling) return;
      
      try {
        const result = await commandAPI.getStatus(executionId);
        console.log(`📊 Poll #${attempts + 1} - Status: ${result.status}, Has output: ${!!result.output}`);
        
        if (result.output) {
          setTerminalOutput(result.output);
          console.log('✅ Output updated:', result.output.substring(0, 100) + (result.output.length > 100 ? '...' : ''));
        }
        
        if (result.status === 'completed' || result.status === 'failed') {
          console.log(`🏁 Execution ${result.status}:`, result.output ? `${result.output.length} chars` : 'no output');
          polling = false;
          setIsTerminalExecuting(false);
          setCurrentExecutionId(null);
          
          if (result.output) {
            setTerminalOutput(result.output);
          }
          if (result.error) {
            setTerminalOutput((prev) => `${prev || ''}\n\n[ERROR] ${result.error}`);
          }
          return;
        }

        if (result.status === 'running' && attempts < maxAttempts && polling) {
          attempts++;
          setTimeout(() => {
            if (polling) poll();
          }, 500);
        } else {
          console.log(`⏸️ Stopping polling - attempts: ${attempts}, max: ${maxAttempts}, status: ${result.status}`);
          polling = false;
          setIsTerminalExecuting(false);
          setCurrentExecutionId(null);
        }
      } catch (error) {
        console.error('❌ Polling error:', error);
        polling = false;
        setIsTerminalExecuting(false);
        setCurrentExecutionId(null);
      }
    };

    poll();
    return () => { polling = false; };
  }, []);

  // Redirect if no session (but wait a bit for session to load from localStorage)
  useEffect(() => {
    // Give time for SessionContext to load session from localStorage
    const timer = setTimeout(() => {
      if (!session) {
        // Check if we have a pending execution (means we came from tools page)
        const pendingExec = localStorage.getItem('pending_execution');
        if (!pendingExec) {
          navigate('/');
        }
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [session, navigate]);

  // Check for pending execution from tools page
  useEffect(() => {
    const checkPendingExecution = () => {
      const pendingExec = localStorage.getItem('pending_execution');
      console.log('Checking for pending execution:', pendingExec);
      console.log('Session status:', session ? 'Available' : 'Not loaded yet');
      
      if (pendingExec) {
        if (session) {
          try {
            const execData = JSON.parse(pendingExec);
            console.log('✅ Processing pending execution:', execData);
            
            if (execData.execution_id) {
              localStorage.removeItem('pending_execution');
              
              // Set terminal state
              setTerminalCommand(execData.command);
              setTerminalTool(execData.tool_name || 'Tool');
              setTerminalOutput('');
              setIsTerminalExecuting(true);
              
              // Start polling
              setCurrentExecutionId(execData.execution_id);
              console.log('🚀 Starting polling for execution:', execData.execution_id);
              pollExecutionResult(execData.execution_id);
            } else {
              console.error('❌ No execution_id in pending execution data');
            }
          } catch (error) {
            console.error('❌ Failed to process pending execution:', error);
          }
        } else {
          console.log('⏳ Waiting for session to load before processing execution...');
        }
      }
    };
    
    // Check immediately if session exists
    if (session) {
      checkPendingExecution();
    }
    
    // Also check after delays in case session is still loading
    const timer1 = setTimeout(checkPendingExecution, 500);
    const timer2 = setTimeout(checkPendingExecution, 1000);
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [session, pollExecutionResult]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !session || isProcessing) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const userInput = input.trim();
    setInput('');
    setIsProcessing(true);

    try {
      const response = await requestAPI.process(session.session_id, userInput);
      
      // Debug: Log the actual response
      console.log('=== LINA RESPONSE ===', JSON.stringify(response, null, 2));

      // Build message content based on response type
      let messageContent = '';
      if (response.suggestions && response.suggestions.length > 0) {
        // Suggester mode: minimal message, cards will show the details
        messageContent = `Here are ${response.suggestions.length} command option${response.suggestions.length > 1 ? 's' : ''}:`;
      } else if (response.type === 'command' && response.command) {
        messageContent = `I'll execute: \`${response.command}\``;
      } else if (response.type === 'autonomous_plan' && response.plan) {
        // Show plan summary instead of generic "Response received"
        console.log('📋 Has autonomous plan with', response.plan.plan?.length || 0, 'steps');
        messageContent = `Generated a ${response.plan.plan?.length || 0}-step plan: ${response.plan.mission_summary || 'Multi-step operation'}`;
      } else if (response.explanation) {
        messageContent = response.explanation;
      } else if (response.message) {
        messageContent = response.message;
      } else {
        console.log('⚠️ No content found in response, showing fallback');
        console.log('Response type:', response.type);
        console.log('Has explanation:', !!response.explanation);
        console.log('Has message:', !!response.message);
        console.log('Has plan:', !!response.plan);
        messageContent = 'Response received';
      }

      // Mode-specific behavior
      const hasCommand = response.command && response.type === 'command';
      const hasPlan = response.type === 'autonomous_plan' && response.plan?.plan;
      const hasSuggestions = response.suggestions && response.suggestions.length > 0;
      
      // Build assistant message - include response only for interactive/suggester modes
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: messageContent,
        timestamp: new Date(),
        // Include response for interactive/suggester modes (to show CommandExecutor/Cards)
        response: (mode === 'interactive' || mode === 'suggester') && (hasCommand || hasPlan || hasSuggestions) ? response : undefined,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Quick mode: Auto-execute immediately without showing CommandExecutor
      if (hasCommand && mode === 'quick') {
        setTimeout(() => {
          handleAutoExecuteCommand(response);
        }, 100);
      }
      // Interactive/Suggester modes: Show CommandExecutor, don't auto-execute
      // User will click execute button in CommandExecutor component
    } catch (error: any) {
      // Handle session not found - redirect to role selection
      if (error?.response?.status === 404 || error?.response?.data?.detail?.includes('not found')) {
        console.warn('Session not found, redirecting to role selection');
        localStorage.removeItem('lina_session');
        clearSession();
        navigate('/');
        return;
      }
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message || 'Failed to process request'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAutoExecuteCommand = async (response: ProcessResponse) => {
    const command = response.command;
    if (!command || !session) {
      console.error('Cannot execute: missing command or session', { command, hasSession: !!session });
      return;
    }

    console.log('Executing command:', command);

    // Update terminal with command
    setTerminalCommand(command);
    setTerminalTool(response.tool_name || 'LINA');
    setTerminalOutput('');
    setIsTerminalExecuting(true);

    try {
      // Execute command automatically with auto_confirm=true
      console.log('Calling commandAPI.execute...');
      const execution = await commandAPI.execute(
        session.session_id,
        command,
        true, // auto_confirm = true (skip confirmation)
        'separate' // Use 'separate' mode which maps to background execution with output capture
      );

      console.log('Execution started:', execution);

      // Store execution ID for polling
      if (execution?.execution_id) {
        setCurrentExecutionId(execution.execution_id);
        pollExecutionResult(execution.execution_id);
      } else if (execution?.output) {
        // Immediate output available
        setTerminalOutput(execution.output);
        setIsTerminalExecuting(false);
      } else {
        console.warn('No execution_id or output in response:', execution);
        setTerminalOutput('Command submitted but no execution ID received. Check backend logs.');
        setIsTerminalExecuting(false);
      }
    } catch (error: any) {
      console.error('Auto-execution failed:', error);
      console.error('Error details:', error.response?.data);
      setIsTerminalExecuting(false);
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to execute command';
      setTerminalOutput(`Error: ${errorMsg}`);
      // Add error message to chat
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Execution error: ${errorMsg}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };


  const clearTerminal = () => {
    setTerminalCommand('');
    setTerminalOutput('');
    setTerminalTool('');
    setIsTerminalExecuting(false);
    setCurrentExecutionId(null);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleLogout = () => {
    clearSession();
    navigate('/');
  };

  const handleToolSelect = (tool: ToolInfo) => {
    setSelectedTool(tool);
  };

  const handleToolExecute = async (toolName: string, parameters: Record<string, any>) => {
    if (!session) return;

    try {
      // Execute tool via API
      const result = await toolsAPI.execute(toolName, parameters, session.session_id);
      
      // Set terminal output
      setTerminalCommand(result.command || `${toolName} execution`);
      setTerminalTool(toolName);
      setTerminalOutput(result.output || '');
      
      // If there's an execution_id, poll for updates
      if (result.execution_id) {
        setCurrentExecutionId(result.execution_id);
        setIsTerminalExecuting(true);
        pollExecutionResult(result.execution_id);
      } else {
        setIsTerminalExecuting(false);
      }
      
      // Show results message
      if (result.success) {
        const successMessage: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: `${toolName} executed successfully. Check terminal output for results.`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, successMessage]);
      } else {
        const errorMessage: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: `${toolName} execution failed: ${result.errors?.join(', ') || 'Unknown error'}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error: any) {
      console.error('Tool execution error:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Failed to execute ${toolName}: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const handleCloseToolExecutor = () => {
    setSelectedTool(null);
  };

  if (!session) {
    return null;
  }

  const getModeIcon = (m: WorkMode) => {
    switch (m) {
      case 'quick': return <Zap className="w-4 h-4" />;
      case 'interactive': return <MessageCircle className="w-4 h-4" />;
      case 'suggester': return <Lightbulb className="w-4 h-4" />;
    }
  };

  const getModeLabel = (m: WorkMode) => {
    switch (m) {
      case 'quick': return 'Quick Mode';
      case 'interactive': return 'Interactive Mode';
      case 'suggester': return 'Suggester Mode';
    }
  };

  const currentMode = mode || 'interactive';

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-dark-bg overflow-hidden">
      {/* Top: Side Navigation + Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Side Navigation Bar */}
        <SideNavbar
          selectedTool={selectedTool}
          onToolSelect={handleToolSelect}
          isCollapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <header className="bg-white dark:bg-dark-bg-secondary border-b-2 border-gray-200 dark:border-dark-border px-4 py-2.5 shadow-sm flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-1.5 hover:bg-gray-100 dark:hover:bg-dark-bg-hover rounded-lg transition-colors"
              title="Dashboard"
            >
              <Home className="w-4 h-4 text-cyber-blue" />
            </button>
            <div className="flex items-center space-x-2">
              <div className="p-1.5 rounded-lg bg-gradient-button">
                <Terminal className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-base font-black text-gray-900 dark:text-dark-text">LINA Chat</h1>
                <p className="text-xs font-semibold text-gray-600 dark:text-dark-text-secondary">
                  {session.mode ? getModeLabel(session.mode as WorkMode) : 'Chat Session'}
                </p>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-1.5">
            {/* Mode Selector */}
            <div className="relative">
              <button
                onClick={() => setShowModeDropdown(!showModeDropdown)}
                className="px-2.5 py-1.5 bg-white dark:bg-dark-bg-secondary border-2 border-gray-300 dark:border-dark-border text-gray-900 dark:text-dark-text rounded-lg hover:border-cyber-blue transition-all flex items-center space-x-1.5 font-semibold text-xs"
              >
                {getModeIcon(currentMode)}
                <span className="text-xs">{getModeLabel(currentMode)}</span>
                <ChevronDown className="w-3 h-3" />
              </button>
              {showModeDropdown && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowModeDropdown(false)}
                  />
                  <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-dark-bg-secondary border-2 border-gray-300 dark:border-dark-border rounded-xl shadow-2xl z-20 overflow-hidden">
                    {(['quick', 'interactive', 'suggester'] as WorkMode[]).map((m) => (
                      <button
                        key={m}
                        onClick={() => {
                          setMode(m);
                          setShowModeDropdown(false);
                        }}
                        className={`w-full px-5 py-3 text-left hover:bg-gray-50 dark:hover:bg-dark-bg-hover transition-colors flex items-center space-x-3 border-l-4 ${
                          currentMode === m ? 'bg-cyber-blue/5 dark:bg-cyber-blue/10 border-cyber-blue' : 'border-transparent'
                        }`}
                      >
                        {getModeIcon(m)}
                        <span className="text-gray-900 dark:text-dark-text font-semibold">{getModeLabel(m)}</span>
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
            <button
              onClick={() => navigate('/tools')}
              className="px-3 py-1.5 rounded-lg font-bold text-white transition-all hover:scale-105 text-xs"
              style={{
                background: theme === 'dark' 
                  ? 'linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)'
                  : 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
              }}
              title="View All Tools"
            >
              Tools
            </button>
            <button
              onClick={() => navigate('/analytics')}
              className="p-1.5 hover:bg-gray-100 dark:hover:bg-dark-bg-hover rounded-lg transition-colors"
              title="Analytics"
            >
              <BarChart3 className="w-4 h-4 text-cyber-blue" />
            </button>
            <button
              onClick={handleLogout}
              className="px-3 py-1.5 bg-white dark:bg-dark-bg-secondary border-2 border-gray-300 dark:border-dark-border text-gray-900 dark:text-dark-text rounded-lg hover:border-red-500 hover:text-red-500 transition-colors font-semibold text-xs"
            >
              Change Mode
            </button>
          </div>
        </div>
      </header>

          {/* Chat Interface - Simple 2 Column Layout */}
          <div className="flex-1 flex overflow-hidden">
            {/* Left: Chat Messages (Always 60%) */}
            <div className="w-3/5 flex flex-col bg-white dark:bg-dark-bg-secondary border-r-2 border-gray-200 dark:border-dark-border">
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-sm">
              <div className="rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3 shadow-lg text-white"
                style={{
                  background: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)'
                }}
              >
                <Bot className="w-7 h-7" />
              </div>
              <h3 className="text-lg font-black text-gray-900 dark:text-dark-text mb-2">Start a conversation</h3>
              <p className="text-xs text-gray-600 dark:text-dark-text-secondary mb-4">Your AI-powered cybersecurity assistant</p>
              <div className="bg-gray-50 dark:bg-dark-bg-tertiary rounded-lg p-3 border-2 border-gray-200 dark:border-dark-border">
                <p className="text-xs font-semibold text-gray-700 dark:text-dark-text-secondary mb-2">Try:</p>
                <div className="space-y-1.5">
                  <div className="bg-white dark:bg-dark-bg-secondary px-2.5 py-1.5 rounded text-xs font-mono text-gray-800 dark:text-dark-text border border-gray-300 dark:border-dark-border">"scan localhost"</div>
                  <div className="bg-white dark:bg-dark-bg-secondary px-2.5 py-1.5 rounded text-xs font-mono text-gray-800 dark:text-dark-text border border-gray-300 dark:border-dark-border">"explain nmap"</div>
                </div>
              </div>
              <div className="mt-3 inline-block px-3 py-1 bg-cyber-blue/10 dark:bg-cyber-blue/20 rounded-full">
                <span className="text-xs font-bold text-gray-800 dark:text-dark-text">Mode: <span className="text-cyber-blue">{getModeLabel(currentMode)}</span></span>
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start space-x-3 ${
              message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}
          >
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-md text-white"
              style={{
                background: message.role === 'user' 
                  ? (theme === 'dark' 
                      ? 'linear-gradient(135deg, #06B6D4 0%, #F59E0B 100%)'
                      : 'linear-gradient(135deg, #A855F7 0%, #EC4899 100%)')
                  : (theme === 'dark'
                      ? 'linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)'
                      : 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)')
              }}
            >
              {message.role === 'user' ? (
                <User className="w-4 h-4" />
              ) : (
                <Bot className="w-4 h-4" />
              )}
            </div>
            <div
              className={`flex-1 rounded-lg p-2.5 ${
                message.role === 'user'
                  ? 'bg-cyber-blue text-white shadow-md'
                  : 'bg-gray-50 dark:bg-dark-bg-tertiary text-gray-900 dark:text-dark-text shadow-sm border-2 border-gray-200 dark:border-dark-border'
              }`}
              style={{
                ...(message.role === 'user' ? {
                  background: theme === 'dark' 
                    ? 'linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)'
                    : 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
                } : {})
              }}
            >
              <p className="whitespace-pre-wrap font-semibold text-xs leading-relaxed">{message.content}</p>
              
              {/* Show autonomous plan steps as cards */}
              {message.response && message.response.type === 'autonomous_plan' && message.response.plan?.plan && message.response.plan.plan.length > 0 && (
                <div className="mt-4 space-y-3">
                  {/* Plan Summary Header */}
                  <div className="bg-gradient-to-r from-cyber-blue/10 to-cyber-purple/10 dark:from-cyber-blue/10 dark:to-cyber-cyan/10 border-2 border-cyber-blue rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-black text-gray-900 dark:text-dark-text">Mission Plan</h4>
                      <span className={`text-xs px-2 py-0.5 rounded font-bold ${
                        message.response.plan.risk_level === 'LOW' ? 'bg-green-100 text-green-700 border border-green-300' :
                        message.response.plan.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700 border border-yellow-300' :
                        'bg-red-100 text-red-700 border border-red-300'
                      }`}>
                        {message.response.plan.risk_level}
                      </span>
                    </div>
                    <p className="text-xs text-gray-700 dark:text-dark-text-secondary font-medium">{message.response.plan.mission_summary}</p>
                    {message.response.plan.estimated_time && (
                      <p className="text-xs text-gray-600 dark:text-dark-text-muted mt-1">⏱️ Est. Time: {message.response.plan.estimated_time}</p>
                    )}
                  </div>

                  {/* Plan Steps */}
                  {message.response.plan.plan.map((step: any, idx: number) => (
                    <div key={idx} className="bg-white dark:bg-dark-bg-secondary border-2 border-cyber-blue rounded-lg p-2.5 shadow-sm hover:shadow-md transition-all">
                      <div className="flex items-start justify-between mb-1.5">
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-black text-white bg-cyber-blue rounded-full w-5 h-5 flex items-center justify-center">{step.step}</span>
                          <span className="text-xs font-black text-cyber-blue">{step.tool_name}</span>
                          {step.phase && (
                            <span className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-dark-bg-tertiary text-gray-600 dark:text-dark-text-secondary rounded font-semibold">{step.phase}</span>
                          )}
                        </div>
                        <button
                          onClick={() => {
                            console.log('🔵 Execute clicked for step:', step);
                            // Create a modified response with this step's command
                            const modifiedResponse = {
                              ...message.response,
                              type: 'command',
                              command: step.command_template,
                              tool_name: step.tool_name,
                              explanation: step.description
                            };
                            handleAutoExecuteCommand(modifiedResponse as ProcessResponse);
                          }}
                          className="text-xs px-3 py-1.5 rounded-lg font-bold text-white transition-all hover:scale-105 shadow-md flex-shrink-0"
                          style={{
                            background: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
                          }}
                        >
                          Execute
                        </button>
                      </div>
                      <div className="bg-gray-900 border-2 border-cyber-blue text-terminal-green font-mono p-2 rounded text-xs mb-1.5">
                        <code className="font-bold">{step.command_template}</code>
                      </div>
                      <p className="text-xs text-gray-700 dark:text-dark-text-secondary leading-relaxed font-medium mb-1">{step.description}</p>
                      {step.expected_output && (
                        <p className="text-xs text-gray-500 dark:text-dark-text-muted italic">Expected: {step.expected_output}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Show suggestions for suggester mode */}
              {message.response && message.response.suggestions && message.response.suggestions.length > 0 && (
                <div className="mt-4 space-y-3">
                  {message.response.suggestions.map((suggestion, idx) => (
                  <div key={idx} className="bg-white dark:bg-dark-bg-secondary border-2 border-cyber-blue rounded-lg p-2.5 shadow-sm hover:shadow-md transition-all">
                    <div className="flex items-start justify-between mb-1.5">
                      <span className="text-xs font-black text-cyber-blue">Option {idx + 1}</span>
                        <button
                          onClick={() => {
                            // Create a modified response with this suggestion as the command
                            const modifiedResponse = { ...message.response, command: suggestion.command };
                            handleAutoExecuteCommand(modifiedResponse as ProcessResponse);
                          }}
                          className="text-xs px-3 py-1 bg-cyber-blue text-white hover:bg-cyber-blue-deep rounded transition-all font-bold"
                        >
                          Execute
                        </button>
                      </div>
                    <div className="bg-gray-900 border-2 border-cyber-blue text-terminal-green font-mono p-2 rounded text-xs mb-1.5">
                      <code className="font-bold">{suggestion.command}</code>
                    </div>
                      {suggestion.explanation && (
                        <p className="text-xs text-gray-700 dark:text-dark-text-secondary leading-relaxed font-medium">{suggestion.explanation}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
              {/* Show CommandExecutor for single command in interactive/suggester mode */}
              {message.response && message.response.type === 'command' && !message.response.suggestions && !message.response.plan && (
                <div className="mt-4">
                  <CommandExecutor
                    response={message.response}
                    sessionId={session.session_id}
                  />
                </div>
              )}
            </div>
          </div>
        ))}

        {isProcessing && (
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 rounded-full flex items-center justify-center shadow-md text-white"
              style={{
                background: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)'
              }}
            >
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-gray-50 dark:bg-dark-bg-tertiary border-2 border-gray-200 dark:border-dark-border rounded-lg p-3 shadow-sm">
              <div className="flex items-center space-x-1.5">
                <div className="w-1.5 h-1.5 bg-cyber-blue rounded-full animate-bounce" />
                <div className="w-1.5 h-1.5 bg-cyber-purple dark:bg-cyber-cyan rounded-full animate-bounce" style={{animationDelay: '0.1s'}} />
                <div className="w-1.5 h-1.5 bg-cyber-pink dark:bg-cyber-orange rounded-full animate-bounce" style={{animationDelay: '0.2s'}} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
          </div>

              {/* Input Area */}
              <div className="bg-gray-100 dark:bg-dark-bg-tertiary border-t-2 border-gray-200 dark:border-dark-border p-3 flex-shrink-0">
                <div className="flex items-end space-x-2">
                  <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={`Type your command or question...`}
                    rows={1}
                    className="flex-1 resize-none bg-white dark:bg-dark-bg-secondary border-2 border-gray-300 dark:border-dark-border text-gray-900 dark:text-dark-text px-3 py-2 rounded-lg outline-none transition-all font-medium text-xs focus:border-cyber-blue focus:shadow-md"
                    disabled={isProcessing}
                  />
                  <button
                    onClick={handleSend}
                    disabled={!input.trim() || isProcessing}
                    className="px-4 py-2 rounded-lg font-bold text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-105 shadow-md"
                    style={{
                      background: theme === 'dark' 
                        ? 'linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)'
                        : 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
                    }}
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Right Side: Terminal + Tool Executor (40%) */}
            <div className="w-2/5 flex flex-col">
              {/* Terminal Panel (Top or Full) */}
              {(terminalCommand || terminalOutput || isTerminalExecuting) ? (
                <div className={selectedTool ? 'h-1/2 border-b-2 border-gray-700 dark:border-dark-border overflow-hidden' : 'flex-1 overflow-hidden'}>
                  <TerminalOutput
              command={terminalCommand}
              output={terminalOutput}
              isExecuting={isTerminalExecuting}
              toolName={terminalTool || 'LINA'}
              onClear={clearTerminal}
              onSaveToFile={async (filename, content) => {
                try {
                  // Determine directory based on content type
                  const isHash = /^[a-f0-9]{32,128}$/i.test(content.trim());
                  const directory = isHash ? 'hashes' : 'outputs';
                  
                  const result = await filesAPI.save(filename, content, directory);
                  
                  // Show success message
                  const successMessage: Message = {
                    id: Date.now().toString(),
                    role: 'assistant',
                    content: `✅ Saved to: ${result.file_path}\nYou can now use this file with tools like hashcat or john.`,
                    timestamp: new Date(),
                  };
                  setMessages((prev) => [...prev, successMessage]);
                } catch (error: any) {
                  const errorMessage: Message = {
                    id: Date.now().toString(),
                    role: 'assistant',
                    content: `Failed to save file: ${error.response?.data?.detail || error.message}`,
                    timestamp: new Date(),
                  };
                  setMessages((prev) => [...prev, errorMessage]);
                }
              }}
                  />
                </div>
              ) : (
                !selectedTool && (
                  <div className="flex-1 bg-gray-900 dark:bg-dark-bg flex items-center justify-center">
                    <div className="text-center p-6">
                      <Terminal className="w-12 h-12 text-terminal-green mx-auto mb-3 opacity-50" />
                      <p className="text-gray-400 dark:text-dark-text-secondary text-xs font-semibold">Terminal Ready</p>
                      <p className="text-gray-500 dark:text-dark-text-muted text-xs mt-1">Output will appear here</p>
                    </div>
                  </div>
                )
              )}

              {/* Tool Executor Panel (Bottom or Full) */}
              {selectedTool && (
                <div className={(terminalCommand || terminalOutput || isTerminalExecuting) ? 'h-1/2 overflow-hidden' : 'flex-1 overflow-hidden'}>
                  <ToolExecutor
                    tool={selectedTool}
                    onClose={handleCloseToolExecutor}
                    onExecute={handleToolExecute}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

