/**
 * Tools List Component
 * Enhanced with categorized dropdowns and smart "Use Tool?" prompts
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Search, 
  CheckCircle, 
  XCircle, 
  ChevronDown,
  ChevronUp,
  Play,
  Loader2
} from 'lucide-react';
import { toolsAPI, requestAPI, commandAPI } from '../services/api';
import { useSession } from '../contexts/SessionContext';
import type { ToolInfo, ProcessResponse } from '../types';

interface UseToolModalProps {
  tool: ToolInfo;
  onClose: () => void;
  onExecute: (command: string) => void;
}

function UseToolModal({ tool, onClose, onExecute }: UseToolModalProps) {
  const { session } = useSession();
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<ProcessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadSuggestions = async () => {
    if (!session || isLoading) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Request command suggestions from backend with specific tool request
      const response = await requestAPI.process(
        session.session_id,
        `Generate a complete command for ${tool.name}. Replace any placeholders like [PORT], [IP], [FILE] with example values or reasonable defaults. Provide a ready-to-execute command.`
      );
      
      // Log the suggested command for debugging
      if (response.command) {
        console.log('💡 AI suggested command:', response.command);
      }
      setSuggestions(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load suggestions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExecute = () => {
    if (suggestions?.command) {
      onExecute(suggestions.command);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-light-bg-secondary dark:bg-dark-bg-secondary border-2 border-cyber-blue rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto custom-scrollbar">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-dark-text flex items-center">
                <span className="text-cyber-blue">{tool.name}</span>
                {tool.installed ? (
                  <CheckCircle className="w-5 h-5 text-green-600 dark:text-cyber-green ml-2" />
                ) : (
                  <XCircle className="w-5 h-5 text-gray-500 dark:text-dark-text-muted ml-2" />
                )}
              </h2>
              <p className="text-sm text-gray-600 dark:text-dark-text-secondary mt-1">{tool.category}</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-600 dark:text-dark-text-secondary hover:text-gray-900 dark:hover:text-dark-text transition-colors"
            >
              ✕
            </button>
          </div>

          {/* Description */}
          <div className="mb-4">
            <p className="text-gray-700 dark:text-dark-text-secondary">{tool.description}</p>
          </div>

          {/* Risk Level */}
          <div className="mb-4">
            <span className={`text-xs px-2 py-1 rounded ${
              tool.risk_level === 'LOW' || tool.risk_level === 'SAFE'
                ? 'risk-low'
                : tool.risk_level === 'MEDIUM'
                ? 'risk-medium'
                : tool.risk_level === 'HIGH' || tool.risk_level === 'RISKY'
                ? 'risk-high'
                : tool.risk_level === 'CRITICAL'
                ? 'risk-critical'
                : 'risk-unknown'
            }`}>
              {tool.risk_level}
            </span>
          </div>

          {/* Load Suggestions Button */}
          {!suggestions && !isLoading && (
            <button
              onClick={loadSuggestions}
              className="w-full cyber-button mb-4"
            >
              <Loader2 className="w-4 h-4 inline mr-2" />
              Get Command Suggestions
            </button>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="w-6 h-6 text-cyber-blue animate-spin" />
              <span className="ml-2 text-gray-700 dark:text-dark-text-secondary">Generating suggestions...</span>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-500/50 dark:border-red-500/30 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          {/* Suggestions */}
          {suggestions && suggestions.command && (
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-dark-text mb-2">Suggested Command</h3>
                <div className="bg-light-bg dark:bg-dark-bg-secondary border border-cyber-blue/30 dark:border-cyber-blue/50 rounded-lg p-4 font-mono text-sm">
                  <code className="text-terminal-green">{suggestions.command}</code>
                </div>
              </div>

              {suggestions.explanation && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-dark-text mb-2">Explanation</h3>
                  <p className="text-gray-700 dark:text-dark-text-secondary text-sm">{suggestions.explanation}</p>
                </div>
              )}

              {suggestions.risk && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-dark-text mb-2">Risk Assessment</h3>
                  <div className={`risk-${suggestions.risk.level.toLowerCase()} px-3 py-2 rounded`}>
                    <p className="font-semibold">{suggestions.risk.level}</p>
                    {suggestions.risk.reason && (
                      <p className="text-sm mt-1">{suggestions.risk.reason}</p>
                    )}
                  </div>
                </div>
              )}

              {/* Execute Button */}
              <button
                onClick={handleExecute}
                disabled={!suggestions.command || !tool.installed}
                className="w-full cyber-button disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Play className="w-4 h-4 inline mr-2" />
                Use Tool
              </button>
            </div>
          )}

          {/* Keywords */}
          {tool.keywords.length > 0 && (
            <div className="mt-4 pt-4 border-t border-light-border dark:border-dark-border">
              <h3 className="text-sm font-semibold text-gray-600 dark:text-dark-text-secondary mb-2">Keywords</h3>
              <div className="flex flex-wrap gap-2">
                {tool.keywords.map((keyword) => (
                  <span
                    key={keyword}
                    className="bg-light-bg dark:bg-dark-bg-secondary border border-light-border dark:border-dark-border text-gray-600 dark:text-dark-text-secondary px-2 py-1 rounded text-xs"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ToolsList() {
  const { session } = useSession();
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [selectedTool, setSelectedTool] = useState<ToolInfo | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['tools'],
    queryFn: () => toolsAPI.list(),
  });

  const tools = data?.tools || [];
  const categories = data?.categories || [];

  // Group tools by category
  const toolsByCategory = tools.reduce((acc, tool) => {
    const category = tool.category || 'uncategorized';
    if (!acc[category]) acc[category] = [];
    acc[category].push(tool);
    return acc;
  }, {} as Record<string, ToolInfo[]>);

  // Filter tools by search term
  const filteredToolsByCategory = Object.entries(toolsByCategory).reduce((acc, [category, categoryTools]) => {
    const filtered = categoryTools.filter((tool) => {
      const matchesSearch =
        tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tool.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tool.keywords.some((kw) => kw.toLowerCase().includes(searchTerm.toLowerCase()));
      return matchesSearch;
    });
    if (filtered.length > 0) {
      acc[category] = filtered;
    }
    return acc;
  }, {} as Record<string, ToolInfo[]>);

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => {
      const next = new Set(prev);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  };

  const handleToolClick = (tool: ToolInfo) => {
    setSelectedTool(tool);
  };

  const handleExecute = async (command: string) => {
    if (!session || !command) {
      console.error('Missing session or command', { hasSession: !!session, hasCommand: !!command });
      return;
    }
    
    console.log('Executing tool command:', command);
    
    try {
      // Execute the command directly
      const execution = await commandAPI.execute(
        session.session_id,
        command,
        true, // auto_confirm
        'separate'
      );
      
      console.log('Execution response:', execution);
      
      // Store execution info to pass to chat page
      if (execution?.execution_id) {
        const execData = {
          execution_id: execution.execution_id,
          command: command,
          tool_name: selectedTool?.name || 'Tool'
        };
        console.log('Storing execution data:', execData);
        localStorage.setItem('pending_execution', JSON.stringify(execData));
        
        // Navigate to chat page to see the execution
        window.location.href = '/chat';
      } else {
        console.error('No execution_id returned from command execution:', execution);
        alert('Command execution started but no execution ID was returned. Check console for details.');
      }
    } catch (error) {
      console.error('Failed to execute tool command:', error);
      alert(`Failed to execute command: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-aqua"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/30 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg">
        Failed to load tools: {error instanceof Error ? error.message : 'Unknown error'}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="cyber-card">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-600 dark:text-dark-text-secondary w-5 h-5" />
          <input
            type="text"
            placeholder="Search tools..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="cyber-input w-full pl-10"
          />
        </div>
        <div className="text-sm text-gray-600 dark:text-dark-text-secondary mt-3">
          Showing {Object.values(filteredToolsByCategory).flat().length} of {data?.total_count || 0} tools
          {data?.installed_count !== undefined && (
            <span className="ml-2 text-green-600 dark:text-cyber-green">
              ({data.installed_count} installed)
            </span>
          )}
        </div>
      </div>

      {/* Categorized Tools */}
      <div className="space-y-2">
        {Object.entries(filteredToolsByCategory).map(([category, categoryTools]) => {
          const isExpanded = expandedCategories.has(category);
          return (
            <div key={category} className="cyber-card">
              <button
                onClick={() => toggleCategory(category)}
                className="w-full flex items-center justify-between text-left"
              >
                <div className="flex items-center space-x-3">
                  {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-cyber-blue" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-cyber-blue" />
                  )}
                  <h2 className="text-lg font-bold text-gray-900 dark:text-dark-text">{category}</h2>
                  <span className="text-sm text-gray-600 dark:text-dark-text-secondary">({categoryTools.length})</span>
                </div>
              </button>

              {isExpanded && (
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {categoryTools.map((tool) => (
                    <ToolCard key={tool.name} tool={tool} onClick={() => handleToolClick(tool)} />
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {Object.keys(filteredToolsByCategory).length === 0 && (
          <div className="text-center text-gray-600 dark:text-dark-text-secondary py-12 cyber-card">
            <p>No tools found matching your criteria.</p>
          </div>
        )}
      </div>

      {/* Use Tool Modal */}
      {selectedTool && (
        <UseToolModal
          tool={selectedTool}
          onClose={() => setSelectedTool(null)}
          onExecute={handleExecute}
        />
      )}
    </div>
  );
}

function ToolCard({ tool, onClick }: { tool: ToolInfo; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="bg-light-bg-secondary dark:bg-dark-bg-secondary border border-light-border dark:border-dark-border rounded-lg p-4 hover:border-cyber-blue/50 dark:hover:border-cyber-blue/70 hover:bg-light-bg-hover dark:hover:bg-dark-bg-hover transition-all text-left group"
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold text-gray-900 dark:text-dark-text text-sm group-hover:text-cyber-blue transition-colors">
          {tool.name}
        </h3>
        {tool.installed ? (
          <CheckCircle className="w-5 h-5 text-green-500 dark:text-cyber-green flex-shrink-0" />
        ) : (
          <XCircle className="w-5 h-5 text-gray-500 dark:text-dark-text-muted flex-shrink-0" />
        )}
      </div>

      <p className="text-xs text-gray-600 dark:text-dark-text-secondary mb-3 line-clamp-2">{tool.description}</p>

      <div className="flex items-center justify-between">
        <span className={`text-xs px-2 py-1 rounded ${
          tool.risk_level === 'LOW' || tool.risk_level === 'SAFE'
            ? 'risk-low'
            : tool.risk_level === 'MEDIUM'
            ? 'risk-medium'
            : tool.risk_level === 'HIGH' || tool.risk_level === 'RISKY'
            ? 'risk-high'
            : tool.risk_level === 'CRITICAL'
            ? 'risk-critical'
            : 'risk-unknown'
        }`}>
          {tool.risk_level}
        </span>
        <span className="text-xs text-cyber-blue/70">
          Click to use
        </span>
      </div>
    </button>
  );
}
