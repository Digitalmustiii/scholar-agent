"use client";

import { useState, useEffect } from "react";
import { Trash2, FileText, CheckCircle, XCircle } from "lucide-react";

interface Paper {
  filename: string;
  paper_id: string;
  size_mb: number;
  indexed: boolean;
}

export default function PaperManager() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);

  const fetchPapers = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/papers`);
      const data = await res.json();
      setPapers(data.papers || []);
    } catch (error) {
      console.error("Failed to fetch papers:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, []);

  const deletePaper = async (filename: string) => {
    if (!confirm(`Delete "${filename}"?`)) return;

    setDeleting(filename);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/papers/${filename}`,
        { method: "DELETE" }
      );
      if (res.ok) {
        setPapers((prev) => prev.filter((p) => p.filename !== filename));
      } else {
        alert("Failed to delete paper");
      }
    } catch (error) {
      alert("Error deleting paper");
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return (
      <div className="p-4 text-slate-600 dark:text-slate-400">Loading papers...</div>
    );
  }

  if (papers.length === 0) {
    return (
      <div className="p-4 text-slate-500 dark:text-slate-400 text-center">
        No papers uploaded yet
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-3">
        Uploaded Papers ({papers.length})
      </h3>
      {papers.map((paper) => (
        <div
          key={paper.paper_id}
          className="flex items-center justify-between p-3 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg hover:border-purple-300 dark:hover:border-purple-600 transition-colors"
        >
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <FileText className="w-5 h-5 text-purple-600 dark:text-purple-400 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                {paper.filename}
              </p>
              <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400 mt-1">
                <span>{paper.size_mb.toFixed(2)} MB</span>
                <span>•</span>
                <span className="font-mono text-xs">
                  {paper.paper_id}
                </span>
                {paper.indexed ? (
                  <span className="flex items-center gap-1 text-green-600 dark:text-green-400">
                    <CheckCircle className="w-3 h-3" />
                    Indexed
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-orange-600 dark:text-orange-400">
                    <XCircle className="w-3 h-3" />
                    Not indexed
                  </span>
                )}
              </div>
            </div>
          </div>
          <button
            onClick={() => deletePaper(paper.filename)}
            disabled={deleting === paper.filename}
            className="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors disabled:opacity-50"
            title="Delete paper"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      ))}
    </div>
  );
}