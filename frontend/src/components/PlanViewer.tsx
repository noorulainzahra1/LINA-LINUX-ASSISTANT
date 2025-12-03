/**
 * Plan/Workflow Viewer Component
 * Displays multi-step plans from LINA
 */
import { useState } from 'react';
import { CheckCircle, Circle, Play, ChevronRight } from 'lucide-react';
import type { ProcessResponse } from '../types';

interface PlanViewerProps {
  response: ProcessResponse;
  sessionId: string;
  onExecuteStep?: (step: number, command: string) => void;
}

export default function PlanViewer({ response, sessionId, onExecuteStep }: PlanViewerProps) {
  const plan = response.plan;
  const [executedSteps, setExecutedSteps] = useState<Set<number>>(new Set());

  if (!plan || !plan.steps || plan.steps.length === 0) {
    return (
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800/50 text-yellow-800 dark:text-yellow-400 p-4 rounded-lg">
        No plan steps available
      </div>
    );
  }

  const handleStepExecute = (step: number, command?: string) => {
    if (command && onExecuteStep) {
      onExecuteStep(step, command);
      setExecutedSteps((prev) => new Set(prev).add(step));
    }
  };

  return (
    <div className="bg-white dark:bg-dark-bg-secondary rounded-lg shadow-lg p-6 space-y-4">
      <div>
        <h3 className="text-xl font-bold text-gray-800 dark:text-dark-text mb-2">{plan.title}</h3>
        {plan.description && (
          <p className="text-gray-600 dark:text-dark-text-secondary mb-4">{plan.description}</p>
        )}
      </div>

      <div className="space-y-3">
        {plan.steps.map((step, index) => {
          const isExecuted = executedSteps.has(step.step);
          const stepNumber = step.step || index + 1;

          return (
            <div
              key={stepNumber}
              className={`border-2 rounded-lg p-4 ${
                isExecuted
                  ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800/50'
                  : 'bg-gray-50 dark:bg-dark-bg-tertiary border-gray-200 dark:border-dark-border'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  {isExecuted ? (
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  ) : (
                    <Circle className="w-6 h-6 text-gray-500" />
                  )}
                </div>

                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="font-semibold text-gray-800 dark:text-dark-text">
                      Step {stepNumber}
                    </span>
                    {step.tool && (
                      <span className="text-sm bg-cyan-100 dark:bg-cyan-900/30 text-cyan-800 dark:text-cyan-400 px-2 py-1 rounded">
                        {step.tool}
                      </span>
                    )}
                  </div>

                  <p className="text-gray-700 dark:text-dark-text-secondary mb-2">{step.description}</p>

                  {step.command && (
                    <div className="bg-gray-900 text-green-400 font-mono text-sm p-2 rounded mb-2">
                      <code>{step.command}</code>
                    </div>
                  )}

                  {step.command && !isExecuted && (
                    <button
                      onClick={() => handleStepExecute(stepNumber, step.command)}
                      className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors text-sm"
                    >
                      <Play className="w-4 h-4" />
                      <span>Execute Step</span>
                    </button>
                  )}

                  {isExecuted && (
                    <div className="flex items-center space-x-2 text-green-600 text-sm">
                      <CheckCircle className="w-4 h-4" />
                      <span>Step completed</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="pt-4 border-t border-gray-200 dark:border-dark-border">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600 dark:text-dark-text-secondary">
            Progress: {executedSteps.size} / {plan.steps.length} steps completed
          </span>
          <div className="w-32 bg-gray-200 dark:bg-dark-bg-tertiary rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full transition-all"
              style={{
                width: `${(executedSteps.size / plan.steps.length) * 100}%`,
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

