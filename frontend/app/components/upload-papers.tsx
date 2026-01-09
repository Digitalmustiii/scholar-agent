"use client";

import { useState } from "react";
import { Upload, FileText, CheckCircle } from "lucide-react";

interface Props {
  onUploadSuccess: () => void;
}

export default function UploadPapers({ onUploadSuccess }: Props) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return; 

    if (!file.name.endsWith(".pdf")) {
      setError("Only PDF files are allowed");
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();
      setSuccess(`${data.filename} uploaded! (${data.num_chunks} chunks)`);
      
      setTimeout(() => onUploadSuccess(), 1500);
    } catch (err) {
      setError("Failed to upload paper. Make sure backend is running.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-8 border border-slate-200 dark:border-slate-700 transition-colors">
        <div className="text-center mb-6">
          <FileText className="w-16 h-16 mx-auto text-blue-600 dark:text-blue-400 mb-4" />
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
            Upload Research Papers
          </h2>
          <p className="text-slate-600 dark:text-slate-400">
            Upload PDF research papers to start asking questions
          </p>
        </div>

        <label
          htmlFor="file-upload"
          className="block w-full cursor-pointer"
        >
          <div className="border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg p-12 text-center hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
            <Upload className="w-12 h-12 mx-auto text-slate-400 dark:text-slate-500 mb-4" />
            <p className="text-slate-600 dark:text-slate-400 mb-2">
              {uploading ? "Uploading..." : "Click to upload PDF"}
            </p>
            <p className="text-sm text-slate-400 dark:text-slate-500">
              PDF files only
            </p>
          </div>
          <input
            id="file-upload"
            type="file"
            accept=".pdf"
            onChange={handleUpload}
            disabled={uploading}
            className="hidden"
          />
        </label>

        {error && (
          <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 transition-colors">
            {error}
          </div>
        )}

        {success && (
          <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-lg text-green-700 dark:text-green-400 flex items-center gap-2 transition-colors">
            <CheckCircle className="w-5 h-5" />
            {success}
          </div>
        )}
      </div>
    </div>
  );
}