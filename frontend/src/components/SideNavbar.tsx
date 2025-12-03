/**
 * Side Navigation Bar for Tools
 * Collapsible sidebar with categorized tool list
 */
import { useState, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChevronLeft, ChevronRight, Search, Wrench, CheckCircle, XCircle } from 'lucide-react';
import { toolsAPI } from '../services/api';
import ThemeToggle from './ThemeToggle';
import type { ToolInfo } from '../types/index';

interface SideNavbarProps {
  selectedTool: ToolInfo | null;
  onToolSelect: (tool: ToolInfo) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export default function SideNavbar({
  selectedTool,
  onToolSelect,
  isCollapsed,
  onToggleCollapse
}: SideNavbarProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['Network Security']));

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

  if (isCollapsed) {
    return (
      <div className="w-12 bg-light-bg-secondary dark:bg-dark-bg-secondary border-r border-light-border dark:border-dark-border flex flex-col items-center py-4">
        <button
          onClick={onToggleCollapse}
          className="p-2 hover:bg-light-bg-hover dark:hover:bg-dark-bg-hover rounded-lg transition-colors mb-4"
          title="Expand Tools"
        >
          <ChevronRight className="w-5 h-5 text-cyber-blue" />
        </button>
        <Wrench className="w-6 h-6 text-cyber-blue mb-4" />
        <ThemeToggle />
      </div>
    );
  }

  return (
    <div className="w-80 bg-light-bg-secondary dark:bg-dark-bg-secondary border-r border-light-border dark:border-dark-border flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-light-border dark:border-dark-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900 dark:text-dark-text flex items-center">
            <Wrench className="w-5 h-5 text-cyber-blue mr-2" />
            Tools
          </h2>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <button
              onClick={onToggleCollapse}
              className="p-1 hover:bg-light-bg-hover dark:hover:bg-dark-bg-hover rounded transition-colors"
              title="Collapse"
            >
              <ChevronLeft className="w-4 h-4 text-gray-600 dark:text-dark-text-secondary" />
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-600 dark:text-dark-text-secondary w-4 h-4" />
          <input
            type="text"
            placeholder="Search tools..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="cyber-input w-full pl-10 text-sm"
          />
        </div>

        {/* Tool count */}
        <div className="text-xs text-gray-600 dark:text-dark-text-secondary mt-2">
          {Object.values(filteredToolsByCategory).flat().length} tools
          {data?.installed_count !== undefined && (
            <span className="ml-2 text-green-600 dark:text-cyber-green">
              ({data.installed_count} installed)
            </span>
          )}
        </div>
      </div>

      {/* Tools List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {isLoading && (
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyber-blue"></div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-500/50 dark:border-red-500/30 text-red-700 dark:text-red-400 px-4 py-3 m-4 rounded-lg text-sm">
            Failed to load tools
          </div>
        )}

        {!isLoading && !error && (
          <div className="p-2 space-y-1">
            {Object.entries(filteredToolsByCategory).map(([category, categoryTools]) => {
              const isExpanded = expandedCategories.has(category);
              return (
                <div key={category} className="cyber-card">
                  <button
                    onClick={() => toggleCategory(category)}
                    className="w-full flex items-center justify-between text-left p-2 hover:bg-light-bg-hover dark:hover:bg-dark-bg-hover rounded"
                  >
                    <span className="text-sm font-semibold text-gray-900 dark:text-dark-text">{category}</span>
                    <span className="text-xs text-gray-600 dark:text-dark-text-secondary">({categoryTools.length})</span>
                  </button>

                  {isExpanded && (
                    <div className="mt-1 space-y-1 pl-2">
                      {categoryTools.map((tool) => {
                        const isSelected = selectedTool?.name === tool.name;
                        return (
                          <button
                            key={tool.name}
                            onClick={() => onToolSelect(tool)}
                            className={`w-full text-left p-2 rounded transition-colors ${
                              isSelected
                                ? 'bg-cyber-blue/20 dark:bg-cyber-blue/30 border-l-2 border-cyber-blue'
                                : 'hover:bg-light-bg-hover dark:hover:bg-dark-bg-hover'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-medium text-gray-900 dark:text-dark-text">{tool.name}</span>
                              {tool.installed ? (
                                <CheckCircle className="w-3 h-3 text-green-600 dark:text-cyber-green flex-shrink-0" />
                              ) : (
                                <XCircle className="w-3 h-3 text-gray-500 dark:text-dark-text-muted flex-shrink-0" />
                              )}
                            </div>
                            <p className="text-xs text-gray-600 dark:text-dark-text-secondary mt-1 line-clamp-1">{tool.description}</p>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}

            {Object.keys(filteredToolsByCategory).length === 0 && (
              <div className="text-center text-gray-600 dark:text-dark-text-secondary py-8 px-4">
                <p className="text-sm">No tools found matching "{searchTerm}"</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

