/**
 * Tool Executor Component
 * Parameter form generation and tool execution interface
 */
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Play, Loader2, X, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { toolsAPI } from '../services/api';
import { useSession } from '../contexts/SessionContext';
import { useTheme } from '../contexts/ThemeContext';
import type { ToolInfo } from '../types/index';

interface ToolExecutorProps {
  tool: ToolInfo;
  onClose: () => void;
  onExecute: (toolName: string, parameters: Record<string, any>) => void;
}

interface RegistryParameter {
  flag: string | null;
  description: string;
  keywords: string[];
  requires_value: boolean;
  is_positional?: boolean;
  is_bundle?: boolean;
}

interface ToolRegistry {
  tool_name: string;
  base_command: string;
  parameters: RegistryParameter[];
  execution_metadata?: {
    workflow_type?: string;
    workflow?: any[];
  };
}

export default function ToolExecutor({ tool, onClose, onExecute }: ToolExecutorProps) {
  const { session } = useSession();
  const { theme } = useTheme();
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isExecuting, setIsExecuting] = useState(false);

  // Load tool registry for parameter definitions
  // For now, we'll use a simple approach - in the future, we can add a registry endpoint
  const [registry, setRegistry] = useState<ToolRegistry | null>(null);

  // Initialize with sensible defaults based on tool
  useEffect(() => {
    const defaults = getDefaultParameters(tool);
    setParameters(defaults);
  }, [tool]);

  // Get default parameters for a tool that guarantee a working command
  const getDefaultParameters = (toolInfo: ToolInfo): Record<string, any> => {
    const defaults: Record<string, any> = {};

    // Nmap defaults
    if (toolInfo.name.toLowerCase() === 'nmap') {
      defaults.target = '127.0.0.1';
      defaults.sV = true; // -sV for version detection
      defaults.sC = true; // -sC for default scripts
      // Ports are optional - if not specified, nmap scans top 1000 ports
      // No need to require -p flag
    }

    // Hashcat defaults
    if (toolInfo.name.toLowerCase() === 'hashcat') {
      defaults.hash_file = '/path/to/hashes.txt';
      defaults.wordlist = '/usr/share/wordlists/rockyou.txt';
      defaults.hash_type = '0'; // MD5
      defaults.attack_mode = '0'; // Straight/dictionary
    }

    // John the Ripper defaults
    if (toolInfo.name.toLowerCase() === 'john') {
      defaults.target = '/path/to/hashes.txt';
      defaults.wordlist = '/usr/share/wordlists/rockyou.txt';
      defaults.format = 'raw-md5';
    }

    // SQLMap defaults
    if (toolInfo.name.toLowerCase() === 'sqlmap') {
      defaults.url = 'http://example.com/page.php?id=1';
      defaults.batch = true; // --batch for non-interactive
    }

    // Gobuster defaults
    if (toolInfo.name.toLowerCase() === 'gobuster') {
      defaults.url = 'http://example.com';
      defaults.wordlist = '/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt';
    }

    // Nikto defaults
    if (toolInfo.name.toLowerCase() === 'nikto') {
      defaults.h = 'http://example.com';
    }

    // Network scanning tools (nmap, masscan, rustscan, etc.)
    if (toolInfo.category === 'Network Security' && !defaults.target) {
      defaults.target = '127.0.0.1';
    }

    // Web security tools
    if (toolInfo.category === 'Web Security' && !defaults.url) {
      defaults.url = 'http://example.com';
    }

    // Password cracking tools
    if (toolInfo.category === 'Password Cracking') {
      if (!defaults.hash_file && !defaults.target) {
        defaults.target = '/path/to/hashes.txt';
      }
      if (!defaults.wordlist) {
        defaults.wordlist = '/usr/share/wordlists/rockyou.txt';
      }
    }

    return defaults;
  };

  const handleParameterChange = (key: string, value: any) => {
    setParameters(prev => ({
      ...prev,
      [key]: value
    }));
    
    // Clear error for this field
    if (errors[key]) {
      setErrors(prev => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
    }
  };

  const validateParameters = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    // Basic validation - check required positional args
    if (!parameters.target && !parameters.file && !parameters.url && !parameters.host) {
      // Try to find a positional parameter
      const hasPositional = Object.keys(parameters).some(key => 
        ['target', 'file', 'url', 'host', 'domain'].includes(key)
      );
      if (!hasPositional) {
        newErrors.target = 'Target is required';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleExecute = async () => {
    if (!validateParameters()) {
      return;
    }

    setIsExecuting(true);
    try {
      await onExecute(tool.name, parameters);
      // Don't close automatically - let user see results
    } catch (error) {
      console.error('Execution error:', error);
    } finally {
      setIsExecuting(false);
    }
  };

  // Generate parameter fields based on common tool patterns
  const renderParameterFields = () => {
    const fields: JSX.Element[] = [];

    // Common parameters based on tool category
    if (tool.category === 'Network Security' || tool.name.toLowerCase().includes('scan')) {
      fields.push(
        <div key="target" className="space-y-1.5">
          <label className="text-xs font-bold text-gray-800 dark:text-dark-text">
            Target (IP/Hostname/URL) <span className="text-red-600">*</span>
          </label>
          <input
            type="text"
            value={parameters.target || parameters.host || parameters.url || ''}
            onChange={(e) => {
              const value = e.target.value;
              handleParameterChange('target', value);
              handleParameterChange('host', value);
              handleParameterChange('url', value);
            }}
            className="cyber-input w-full"
            placeholder="e.g., 127.0.0.1, localhost, 192.168.1.1"
          />
          {errors.target && (
            <p className="text-xs text-red-600">{errors.target}</p>
          )}
            <p className="text-xs text-gray-600 dark:text-dark-text-secondary">Required. This is the target to scan.</p>
        </div>
      );

      // Nmap-specific options
      if (tool.name.toLowerCase() === 'nmap') {
        fields.push(
          <div key="nmap_options" className="space-y-1.5">
            <label className="text-xs font-bold text-gray-800 dark:text-dark-text">Scan Options</label>
            <div className="space-y-1.5">
              <label className="flex items-center space-x-2 text-xs text-gray-700 dark:text-dark-text-secondary cursor-pointer hover:text-cyber-blue transition-colors">
                <input
                  type="checkbox"
                  checked={parameters.sV || false}
                  onChange={(e) => handleParameterChange('sV', e.target.checked)}
                  className="w-4 h-4 rounded border-2 border-light-border text-cyber-blue focus:ring-2 focus:ring-cyber-blue focus:ring-offset-2 cursor-pointer"
                />
                <span>-sV: Version detection</span>
              </label>
              <label className="flex items-center space-x-2 text-xs text-gray-700 dark:text-dark-text-secondary cursor-pointer hover:text-cyber-blue transition-colors">
                <input
                  type="checkbox"
                  checked={parameters.sC || false}
                  onChange={(e) => handleParameterChange('sC', e.target.checked)}
                  className="w-4 h-4 rounded border-2 border-light-border text-cyber-blue focus:ring-2 focus:ring-cyber-blue focus:ring-offset-2 cursor-pointer"
                />
                <span>-sC: Default scripts</span>
              </label>
              <label className="flex items-center space-x-2 text-xs text-gray-700 dark:text-dark-text-secondary cursor-pointer hover:text-cyber-blue transition-colors">
                <input
                  type="checkbox"
                  checked={parameters.A || false}
                  onChange={(e) => handleParameterChange('A', e.target.checked)}
                  className="w-4 h-4 rounded border-2 border-light-border text-cyber-blue focus:ring-2 focus:ring-cyber-blue focus:ring-offset-2 cursor-pointer"
                />
                <span>-A: Aggressive scan (OS, version, script, traceroute)</span>
              </label>
            </div>
          </div>
        );

        fields.push(
          <div key="ports" className="space-y-2">
            <label className="text-sm font-semibold text-gray-800 dark:text-dark-text">Ports (optional)</label>
            <input
              type="text"
              value={parameters.ports || parameters.port || ''}
              onChange={(e) => {
                const value = e.target.value;
                handleParameterChange('ports', value);
                handleParameterChange('port', value);
              }}
              className="cyber-input w-full"
              placeholder="e.g., 80,443 or 1-1000 (leave empty for default 1000 ports)"
            />
            <p className="text-xs text-gray-600 dark:text-dark-text-secondary">Optional. If empty, nmap scans top 1000 ports.</p>
          </div>
        );
      } else {
        // Other network scanning tools
        fields.push(
          <div key="ports" className="space-y-2">
            <label className="text-sm font-semibold text-gray-800 dark:text-dark-text">Ports (optional)</label>
            <input
              type="text"
              value={parameters.ports || parameters.port || ''}
              onChange={(e) => {
                const value = e.target.value;
                handleParameterChange('ports', value);
                handleParameterChange('port', value);
              }}
              className="cyber-input w-full"
              placeholder="e.g., 80,443 or 1-1000"
            />
          </div>
        );
      }
    }

    if (tool.category === 'Password Cracking') {
      fields.push(
        <div key="hash_file" className="space-y-1.5">
          <label className="text-xs font-bold text-gray-800 dark:text-dark-text">Hash File</label>
          <input
            type="text"
            value={parameters.hash_file || parameters.target || ''}
            onChange={(e) => {
              const value = e.target.value;
              handleParameterChange('hash_file', value);
              handleParameterChange('target', value);
            }}
            className="cyber-input w-full"
            placeholder="Path to hash file"
          />
          {errors.hash_file && (
            <p className="text-xs text-red-600">{errors.hash_file}</p>
          )}
        </div>
      );

      fields.push(
        <div key="wordlist" className="space-y-2">
          <label className="text-sm font-semibold text-gray-800">Wordlist</label>
          <input
            type="text"
            value={parameters.wordlist || ''}
            onChange={(e) => handleParameterChange('wordlist', e.target.value)}
            className="cyber-input w-full"
            placeholder="e.g., /usr/share/wordlists/rockyou.txt"
          />
        </div>
      );

      fields.push(
        <div key="hash_type" className="space-y-2">
          <label className="text-sm font-semibold text-gray-800">Hash Type</label>
          <input
            type="text"
            value={parameters.hash_type || parameters.format || ''}
            onChange={(e) => {
              const value = e.target.value;
              handleParameterChange('hash_type', value);
              handleParameterChange('format', value);
            }}
            className="cyber-input w-full"
            placeholder="e.g., 0 (MD5), 1000 (NTLM), raw-md5"
          />
        </div>
      );

      fields.push(
        <div key="attack_mode" className="space-y-2">
          <label className="text-sm font-semibold text-gray-800">Attack Mode</label>
          <select
            value={parameters.attack_mode || '0'}
            onChange={(e) => handleParameterChange('attack_mode', e.target.value)}
            className="cyber-input w-full"
          >
            <option value="0">0 - Straight (Dictionary)</option>
            <option value="1">1 - Combination</option>
            <option value="3">3 - Brute-force</option>
          </select>
        </div>
      );
    }

    if (tool.category === 'Web Security') {
      fields.push(
        <div key="url" className="space-y-2">
          <label className="text-sm font-semibold text-gray-800">Target URL</label>
          <input
            type="text"
            value={parameters.url || parameters.target || ''}
            onChange={(e) => {
              const value = e.target.value;
              handleParameterChange('url', value);
              handleParameterChange('target', value);
            }}
            className="cyber-input w-full"
            placeholder="e.g., http://example.com/page.php?id=1"
          />
          {errors.url && (
            <p className="text-xs text-red-600">{errors.url}</p>
          )}
        </div>
      );
    }

    // Generic file input
    if (tool.keywords.some(kw => kw.includes('file') || kw.includes('input'))) {
      fields.push(
        <div key="file" className="space-y-2">
          <label className="text-sm font-semibold text-gray-800">Input File</label>
          <input
            type="text"
            value={parameters.file || ''}
            onChange={(e) => handleParameterChange('file', e.target.value)}
            className="cyber-input w-full"
            placeholder="Path to input file"
          />
        </div>
      );
    }

    return fields;
  };

  return (
    <div className="h-full flex flex-col bg-white overflow-hidden">
      {/* Header */}
      <div className="bg-white border-b-2 border-gray-200 px-4 py-2.5 shadow-sm flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div>
              <h2 className="text-base font-bold text-gray-900 flex items-center">
                <span className="text-cyber-blue font-extrabold">{tool.name}</span>
                {tool.installed ? (
                  <CheckCircle className="w-4 h-4 text-green-600 ml-2" />
                ) : (
                  <XCircle className="w-4 h-4 text-gray-500 ml-2" />
                )}
              </h2>
              <p className="text-xs text-gray-700 mt-0.5 font-medium">{tool.category}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-600 hover:text-cyber-blue hover:bg-gray-100 transition-all p-1.5 rounded-lg"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3 custom-scrollbar bg-gray-50">
        {/* Description */}
        <div className="mb-3 bg-white p-3 rounded-lg border-2 border-gray-200 shadow-sm">
          <p className="text-gray-700 text-xs font-medium leading-relaxed">{tool.description}</p>
        </div>

        {/* Risk Level */}
        <div className="mb-3">
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

        {/* Warning if not installed */}
        {!tool.installed && (
          <div className="bg-yellow-50 border-2 border-yellow-500 text-yellow-800 px-3 py-2 rounded-lg mb-3 flex items-start">
            <AlertTriangle className="w-4 h-4 mr-2 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-xs">Tool not installed</p>
              <p className="text-xs mt-1">Install: apt install {tool.name}</p>
            </div>
          </div>
        )}

        {/* Parameter Form */}
        <div className="space-y-2 bg-white dark:bg-dark-bg-secondary p-3 rounded-lg border-2 border-gray-200 dark:border-dark-border shadow-sm">
          <h3 className="text-sm font-bold text-gray-900 dark:text-dark-text mb-2 flex items-center">
            <span className="w-1 h-4 bg-gradient-button rounded-full mr-2"></span>
            Parameters
          </h3>
          {renderParameterFields()}

          {/* Additional Options */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-dark-text-secondary">Additional Options (optional)</label>
            <textarea
              value={parameters.additional || ''}
              onChange={(e) => handleParameterChange('additional', e.target.value)}
              className="cyber-input w-full h-24"
              placeholder="Additional command-line options..."
            />
            <p className="text-xs text-gray-600 dark:text-dark-text-secondary">Add any extra flags or options here</p>
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="bg-white dark:bg-dark-bg-secondary border-t-2 border-gray-200 dark:border-dark-border px-3 py-2.5 flex-shrink-0">
        <div className="flex items-center justify-end space-x-2">
          <button
            onClick={onClose}
            className="px-3 py-1.5 bg-white dark:bg-dark-bg-secondary border-2 border-gray-300 dark:border-dark-border text-gray-900 dark:text-dark-text rounded-lg hover:border-red-500 hover:text-red-500 transition-colors font-semibold text-xs"
          >
            Cancel
          </button>
          <button
            onClick={handleExecute}
            disabled={!tool.installed || isExecuting || Object.keys(errors).length > 0}
            className="px-4 py-1.5 rounded-lg font-bold text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-105 shadow-md flex items-center text-xs"
            style={{
              background: theme === 'dark' 
                ? 'linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)'
                : 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
            }}
          >
            {isExecuting ? (
              <>
                <Loader2 className="w-3 h-3 mr-1.5 animate-spin" />
                Executing...
              </>
            ) : (
              <>
                <Play className="w-3 h-3 mr-1.5" />
                Execute
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

