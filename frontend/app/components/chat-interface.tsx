"use client";

import { useState, useEffect } from "react";
import { Send, RotateCcw, History, Save, Trash2, Download, FileText, BookMarked, File } from "lucide-react"; // ADDED: File icon for PDF
import MessageItem from "./message-item";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: any[];
  reasoning?: any[];
}

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  message_count: number;
}

interface Props {
  onReset: () => void;
}

export default function ChatInterface({ onReset }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>("");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/conversations`);
      const data = await res.json();
      setConversations(data.conversations);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  };

  const loadConversation = async (id: string) => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/conversations/${id}`);
      const data = await res.json();
      setMessages(data.messages);
      setConversationId(id);
      setShowHistory(false);
    } catch (err) {
      console.error("Failed to load conversation:", err);
    }
  };

  const saveMessage = async (message: Message) => {
    if (!conversationId) {
      const newId = `conv_${Date.now()}`;
      setConversationId(newId);
      await saveMessageToBackend(newId, message);
    } else {
      await saveMessageToBackend(conversationId, message);
    }
  };

  const saveMessageToBackend = async (id: string, message: Message) => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/conversations/${id}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(message),
      });
      loadConversations();
    } catch (err) {
      console.error("Failed to save message:", err);
    }
  };

  const deleteConversation = async (id: string) => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/conversations/${id}`, {
        method: "DELETE",
      });
      loadConversations();
      if (conversationId === id) {
        setMessages([]);
        setConversationId("");
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setConversationId("");
    setShowHistory(false);
  };

  const exportMarkdown = async () => {
    if (!conversationId) {
      alert("No conversation to export");
      return;
    }
    
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/conversations/${conversationId}/export/markdown`);
      if (!res.ok) throw new Error("Export failed");
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `conversation_${conversationId}.md`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export error:", err);
      alert("Failed to export");
    }
  };

  const exportBibtex = async () => {
    if (!conversationId) {
      alert("No conversation to export");
      return;
    }
    
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/conversations/${conversationId}/export/bibtex`);
      if (!res.ok) throw new Error("Export failed");
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `references_${conversationId}.bib`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export error:", err);
      alert("Failed to export");
    }
  };

  const exportPdf = async () => {
    if (!conversationId) {
      alert("No conversation to export");
      return;
    }
    
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/conversations/${conversationId}/export/pdf`);
      if (!res.ok) throw new Error("Export failed");
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `conversation_${conversationId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export error:", err);
      alert("Failed to export");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    await saveMessage(userMessage);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });

      if (!res.ok) throw new Error("Query failed");

      const data = await res.json();
      const assistantMessage: Message = {
        role: "assistant",
        content: data.answer,
        sources: data.sources,
        reasoning: data.reasoning || []
      };
      setMessages((prev) => [...prev, assistantMessage]);
      await saveMessage(assistantMessage);
    } catch (err) {
      const errorMessage: Message = {
        role: "assistant",
        content: "Error: Failed to get response. Make sure backend is running.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto flex gap-4">
      
      {/* History Sidebar */}
      {showHistory && (
        <div className="w-64 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 p-4 h-[700px] overflow-y-auto transition-colors">
          <h3 className="font-semibold text-slate-900 dark:text-white mb-4">History</h3>
          {conversations.length === 0 ? (
            <p className="text-sm text-slate-400 dark:text-slate-500">No saved chats</p>
          ) : (
            <div className="space-y-2">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  className="p-2 hover:bg-slate-50 dark:hover:bg-slate-700 rounded cursor-pointer border border-slate-200 dark:border-slate-600 group transition-colors"
                >
                  <div onClick={() => loadConversation(conv.id)}>
                    <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                      {conv.title}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      {conv.message_count} messages
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteConversation(conv.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 text-xs mt-1"
                  >
                    <Trash2 className="w-3 h-3 inline" /> Delete
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Main Chat */}
      <div className="flex-1 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 flex flex-col h-[700px] transition-colors">
        
        {/* Header */}
        <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
          <h2 className="font-semibold text-slate-900 dark:text-white">Chat with Papers</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1 px-3 py-1 rounded border border-slate-300 dark:border-slate-600 transition-colors"
            >
              <History className="w-4 h-4" />
              {showHistory ? "Hide" : "History"}
            </button>
            
            {/* Export Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowExportMenu(!showExportMenu)}
                disabled={!conversationId || messages.length === 0}
                className="text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1 px-3 py-1 rounded border border-slate-300 dark:border-slate-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="w-4 h-4" />
                Export
              </button>
              
              {showExportMenu && conversationId && (
                <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-xl z-50">
                  <button
                    onClick={() => {
                      exportMarkdown();
                      setShowExportMenu(false);
                    }}
                    className="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center gap-2 rounded-t-lg transition-colors"
                  >
                    <FileText className="w-4 h-4" />
                    Markdown (.md)
                  </button>
                  <button
                    onClick={() => {
                      exportBibtex();
                      setShowExportMenu(false);
                    }}
                    className="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center gap-2 transition-colors"
                  >
                    <BookMarked className="w-4 h-4" />
                    BibTeX (.bib)
                  </button>
                  <button
                    onClick={() => {
                      exportPdf();
                      setShowExportMenu(false);
                    }}
                    className="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center gap-2 rounded-b-lg transition-colors"
                  >
                    <File className="w-4 h-4" />
                    PDF (.pdf)
                  </button>
                </div>
              )}
            </div>
            
            <button
              onClick={startNewChat}
              className="text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1 px-3 py-1 rounded border border-slate-300 dark:border-slate-600 transition-colors"
            >
              <Save className="w-4 h-4" />
              New Chat
            </button>
            <button
              onClick={onReset}
              className="text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1"
            >
              <RotateCcw className="w-4 h-4" />
              Upload
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-slate-400 dark:text-slate-500 mt-20">
              <p className="text-lg mb-2">Ask a question about your papers</p>
              <p className="text-sm">Try: "What is LoRA?" or "Summarize the paper"</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <MessageItem key={idx} message={msg} />
            ))
          )}
          {loading && (
            <div className="text-slate-400 dark:text-slate-500 italic">Thinking...</div>
          )}
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="p-4 border-t border-slate-200 dark:border-slate-700">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              disabled={loading}
              className="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition-colors"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-2 bg-blue-600 dark:bg-blue-700 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}