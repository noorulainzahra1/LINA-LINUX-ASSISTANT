/**
 * Terminal Output Component
 * Displays command execution output in a terminal-like interface
 */
import { useState } from 'react';
import { useEffect, useRef } from 'react';
import { Terminal as TerminalIcon, X, Copy, Download, Save } from 'lucide-react';

interface TerminalOutputProps {
  command?: string;
  output?: string;
  isExecuting?: boolean;
  toolName?: string;
  onClear?: () => void;
  onSaveToFile?: (filename: string, content: string) => Promise<void>;
}

export default function TerminalOutput({
  command,
  output = '',
  isExecuting = false,
  toolName = 'LINA',
  onClear,
  onSaveToFile,
}: TerminalOutputProps) {
  const outputRef = useRef<HTMLDivElement>(null);
  const [saving, setSaving] = useState(false);

  // Auto-scroll to bottom when output updates
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output, isExecuting]);

  const handleCopy = () => {
    if (output) {
      navigator.clipboard.writeText(output);
    }
  };

  const handleDownload = () => {
    if (output) {
      const blob = new Blob([output], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `lina-output-${Date.now()}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const handleSaveToFile = async () => {
    if (!output || !onSaveToFile) return;
    
    setSaving(true);
    try {
      // Extract hash from output if it looks like a hash
      const hashMatch = output.trim().match(/^[a-f0-9]{32,128}$/i);
      const filename = hashMatch 
        ? `hash_${Date.now()}.txt`
        : `output_${toolName.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}.txt`;
      
      await onSaveToFile(filename, output.trim());
    } catch (error) {
      console.error('Failed to save file:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 text-terminal-green font-mono text-sm min-h-0">
      {/* Terminal Header */}
      <div className="flex items-center justify-between bg-gray-800 border-b-2 border-gray-700 px-4 py-2 flex-shrink-0">
        <div className="flex items-center space-x-2">
          <TerminalIcon className="w-4 h-4 text-terminal-green" />
          <span className="text-gray-300 font-semibold">Terminal - {toolName}</span>
          {isExecuting && (
            <span className="ml-2 px-2 py-0.5 bg-yellow-500/20 border border-yellow-500/50 text-yellow-400 text-xs rounded font-semibold">
              Running...
            </span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {output && (
            <>
              <button
                onClick={handleCopy}
                className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-cyber-blue transition-colors"
                title="Copy output"
              >
                <Copy className="w-4 h-4" />
              </button>
              {onSaveToFile && (
                <button
                  onClick={handleSaveToFile}
                  disabled={saving}
                  className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-green-500 transition-colors disabled:opacity-50"
                  title="Save to file (accessible to tools)"
                >
                  <Save className={`w-4 h-4 ${saving ? 'animate-pulse' : ''}`} />
                </button>
              )}
              <button
                onClick={handleDownload}
                className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-cyber-blue transition-colors"
                title="Download output"
              >
                <Download className="w-4 h-4" />
              </button>
            </>
          )}
          {onClear && (
            <button
              onClick={onClear}
              className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-red-500 transition-colors"
              title="Clear output"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Terminal Content */}
      <div
        ref={outputRef}
        className="flex-1 overflow-y-auto p-4 space-y-1 custom-scrollbar min-h-0"
        style={{ fontFamily: 'Monaco, "Courier New", monospace' }}
      >
        {command && (
          <div className="mb-2">
            <span className="text-cyber-blue">$ </span>
            <span className="text-terminal-green">{command}</span>
          </div>
        )}

        {isExecuting && !output && (
          <div className="text-yellow-400">
            <span className="animate-pulse">Executing command...</span>
          </div>
        )}

        {output ? (
          <pre className="whitespace-pre-wrap text-terminal-green break-words">
            {output}
          </pre>
        ) : !isExecuting && !command ? (
          <div className="text-gray-600 italic">
            Command output will appear here when you execute a command...
          </div>
        ) : null}

        {isExecuting && output && (
          <div className="text-yellow-700 mt-2">
            <span className="animate-pulse">█</span>
          </div>
        )}
      </div>
    </div>
  );
}

