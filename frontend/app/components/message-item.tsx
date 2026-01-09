"use client";

import { User, Bot } from "lucide-react";
import AgentThinking from "./agent-thinking";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: any[];
  reasoning?: any[];
}

interface Props {
  message: Message;
  isStreaming?: boolean;
}

export default function MessageItem({ message, isStreaming = false }: Props) {
  const isUser = message.role === "user";

  // Group sources by paper_id
  const groupedSources = message.sources?.reduce((acc: any, source: any) => {
    const paperId = source.paper_id || "unknown";
    if (!acc[paperId]) {
      acc[paperId] = {
        paper_name: source.paper_name,
        sources: []
      };
    }
    acc[paperId].sources.push(source);
    return acc;
  }, {});

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}
      
      <div className={`max-w-[70%] ${isUser ? "order-first" : ""}`}>
        <div
          className={`rounded-lg p-3 ${
            isUser
              ? "bg-blue-600 text-white"
              : "bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white border border-slate-200 dark:border-slate-600 transition-colors"
          }`}
        >
          <p className="text-sm whitespace-pre-wrap break-words">
            {message.content}
            {isStreaming && <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />}
          </p>
        </div>

        {/* Agent Reasoning */}
        {!isUser && message.reasoning && message.reasoning.length > 0 && (
          <AgentThinking reasoning={message.reasoning} isStreaming={isStreaming} />
        )}

        {/* Sources (grouped by paper) */}
        {!isUser && groupedSources && Object.keys(groupedSources).length > 0 && (
          <div className="mt-3 space-y-2">
            <p className="text-xs font-semibold text-slate-600 dark:text-slate-400">Sources:</p>
            {Object.entries(groupedSources).map(([paperId, data]: [string, any]) => (
              <div key={paperId} className="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded p-2 transition-colors">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 text-xs rounded font-medium">
                    {data.paper_name}
                  </span>
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    {data.sources.length} {data.sources.length === 1 ? "chunk" : "chunks"}
                  </span>
                </div>
                
                {data.sources.map((source: any, idx: number) => (
                  <div key={idx} className="text-xs text-slate-600 dark:text-slate-400 mb-2 last:mb-0">
                    <div className="flex items-center gap-2 mb-1">
                      {source.page && (
                        <span className="text-slate-500 dark:text-slate-500">Page {source.page}</span>
                      )}
                      {source.score && (
                        <span className="px-1.5 py-0.5 bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300 rounded text-[10px]">
                          {(source.score * 100).toFixed(0)}% match
                        </span>
                      )}
                    </div>
                    <p className="text-slate-700 dark:text-slate-300 italic">
                      "{source.content.substring(0, 150)}..."
                    </p>
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-300 dark:bg-slate-600 flex items-center justify-center transition-colors">
          <User className="w-5 h-5 text-slate-700 dark:text-slate-300" />
        </div>
      )}
    </div>
  );
}