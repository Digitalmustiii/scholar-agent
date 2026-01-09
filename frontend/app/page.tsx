"use client";

import { useState } from "react";
import UploadPapers from "@/components/upload-papers";
import ChatInterface from "@/components/chat-interface";
import PaperManager from "@/components/paper-manager";
import { BookOpen, MessageSquare, FileStack, Moon, Sun } from "lucide-react";
import { useTheme } from "@/components/theme-provider";

type View = "upload" | "chat" | "papers";

export default function Home() {
  const [view, setView] = useState<View>("upload");
  const [hasUploaded, setHasUploaded] = useState(false);
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800 transition-colors">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 shadow-sm transition-colors">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                  ScholarAgent
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Phase 3: Chat History + Dark Mode
                </p>
              </div>
            </div>

            {/* Navigation Tabs + Theme Toggle */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setView("upload")}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                  view === "upload"
                    ? "bg-blue-600 text-white shadow-md"
                    : "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
                }`}
              >
                <FileStack className="w-4 h-4" />
                Upload
              </button>
              <button
                onClick={() => setView("papers")}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                  view === "papers"
                    ? "bg-purple-600 text-white shadow-md"
                    : "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
                }`}
              >
                <BookOpen className="w-4 h-4" />
                Manage Papers
              </button>
              <button
                onClick={() => setView("chat")}
                disabled={!hasUploaded}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                  view === "chat"
                    ? "bg-green-600 text-white shadow-md"
                    : hasUploaded
                    ? "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
                    : "bg-slate-100 dark:bg-slate-700 text-slate-400 dark:text-slate-600 cursor-not-allowed"
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                Chat
              </button>

              {/* Theme Toggle */}
              <button
                onClick={() => {
                  console.log("BUTTON CLICKED"); // Debug log
                  toggleTheme();
                }}
                className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 transition-all shadow-sm border-2 border-blue-500"
                aria-label="Toggle theme"
                type="button"
              >
                {theme === "light" ? (
                  <Moon className="w-5 h-5" />
                ) : (
                  <Sun className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {view === "upload" && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 transition-colors">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Upload Research Papers
              </h2>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-6">
                Upload PDF papers to enable multi-paper analysis, comparison, and hybrid search
              </p>
              <UploadPapers onUploadSuccess={() => setHasUploaded(true)} />
            </div>

            {/* Feature Highlights */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-4 transition-colors">
                <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center mb-3">
                  <MessageSquare className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                </div>
                <h3 className="font-semibold text-slate-900 dark:text-white mb-1">
                  Multi-Paper Compare
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400">
                  Compare concepts and findings across multiple papers
                </p>
              </div>
              <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-4 transition-colors">
                <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-3">
                  <FileStack className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 className="font-semibold text-slate-900 dark:text-white mb-1">
                  Hybrid Search
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400">
                  Semantic understanding + exact keyword matching
                </p>
              </div>
              <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-4 transition-colors">
                <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center mb-3">
                  <BookOpen className="w-5 h-5 text-green-600 dark:text-green-400" />
                </div>
                <h3 className="font-semibold text-slate-900 dark:text-white mb-1">
                  Smart Routing
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400">
                  5 specialized tools for different query types
                </p>
              </div>
            </div>
          </div>
        )}

        {view === "papers" && (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 transition-colors">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              Paper Management
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-400 mb-6">
              View and manage your uploaded research papers
            </p>
            <PaperManager />
          </div>
        )}

        {view === "chat" && (
          <ChatInterface onReset={() => setView("upload")} />
        )}
      </main>

      {/* Footer */}
      <footer className="max-w-6xl mx-auto px-4 py-6 text-center text-xs text-slate-500 dark:text-slate-400 transition-colors">
        <p>Phase 3 Features: Chat history • Dark mode • Export (coming soon)</p>
        <p className="mt-1">Try: "Compare the approaches across all papers" or "Find mentions of transformer"</p>
      </footer>
    </div>
  );
}