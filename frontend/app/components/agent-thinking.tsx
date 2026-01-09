"use client";

import { Brain, Search, Sparkles, CheckCircle } from "lucide-react";

interface ReasoningStep {
  step: string;
  description: string;
}

interface Props {
  reasoning: ReasoningStep[];
  isStreaming?: boolean;
}

export default function AgentThinking({ reasoning, isStreaming = false }: Props) {
  const getIcon = (step: string) => {
    if (step.includes("Analysis")) return Brain;
    if (step.includes("Selection") || step.includes("Tool")) return Search;
    if (step.includes("Synthesis")) return Sparkles;
    return CheckCircle;
  };

  return (
    <div className="mt-3 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-3 transition-colors">
      <div className="flex items-center gap-2 mb-2">
        <Brain className={`w-4 h-4 text-purple-600 dark:text-purple-400 ${isStreaming ? 'animate-pulse' : ''}`} />
        <p className="text-xs font-semibold text-purple-900 dark:text-purple-300">
          Agent Reasoning {isStreaming && <span className="text-purple-500">●</span>}
        </p>
      </div>
      
      <div className="space-y-2">
        {reasoning.map((step, idx) => {
          const Icon = getIcon(step.step);
          const isLast = idx === reasoning.length - 1;
          
          return (
            <div 
              key={idx} 
              className={`flex items-start gap-2 ${isStreaming && isLast ? 'animate-fadeIn' : ''}`}
            >
              <div className="mt-0.5">
                <Icon className={`w-3.5 h-3.5 text-purple-600 dark:text-purple-400 ${isStreaming && isLast ? 'animate-spin' : ''}`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-purple-900 dark:text-purple-300">
                  {step.step}
                </p>
                <p className="text-xs text-purple-700 dark:text-purple-400">
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
