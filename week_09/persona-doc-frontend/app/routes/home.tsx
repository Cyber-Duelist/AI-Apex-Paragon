import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { 
  Send, Upload, FileText, Trash2, ShieldAlert, Bot, User, Loader2, Sparkles, Database 
} from "lucide-react";
import type { Route } from "./+types/home";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "PersonaDoc AI" },
    { name: "description", content: "Production RAG System" },
  ];
}

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "supersecretkey";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  grounded?: boolean;
  citations?: Array<{ source: string; page: number }>;
}

export default function Home() {
  const [documents, setDocuments] = useState<string[]>([]);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Welcome to PersonaDoc! Upload a document in the sidebar to get started, or ask a question if documents are already indexed.",
      grounded: true
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch documents on load
  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const headers = { "X-API-Key": API_KEY };

  const fetchDocuments = async () => {
    try {
      const res = await axios.get(`${API_URL}/documents`, { headers });
      setDocuments(res.data.documents || []);
    } catch (error) {
      console.error("Failed to fetch documents", error);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post(`${API_URL}/upload`, formData, { headers });
      await fetchDocuments();
      
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: "assistant",
        content: `Successfully indexed **${file.name}**! I've chunked it semantically and added it to ChromaDB. What would you like to know about it?`,
        grounded: true
      }]);
    } catch (error: any) {
      console.error("Upload failed", error);
      alert(error.response?.data?.detail || "Failed to upload document");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (filename: string) => {
    if (!confirm(`Are you sure you want to delete ${filename}?`)) return;
    
    try {
      await axios.delete(`${API_URL}/documents/${filename}`, { headers });
      await fetchDocuments();
    } catch (error) {
      console.error("Delete failed", error);
      alert("Failed to delete document");
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg: Message = { id: Date.now().toString(), role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await axios.post(`${API_URL}/search`, {
        query: userMsg.content,
        top_k: 3
      }, { headers });

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: res.data.answer,
        grounded: res.data.grounded,
        citations: res.data.citations
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (error: any) {
      console.error("Search failed", error);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error communicating with the backend API.",
        grounded: false
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-50 font-sans selection:bg-indigo-500/30">
      
      {/* Sidebar */}
      <div className="w-80 bg-zinc-900/50 border-r border-zinc-800/80 flex flex-col backdrop-blur-xl">
        <div className="p-6 border-b border-zinc-800/80">
          <div className="flex items-center gap-3 text-indigo-400 mb-2">
            <Database size={24} />
            <h1 className="text-xl font-bold tracking-tight text-white">PersonaDoc</h1>
          </div>
          <p className="text-sm text-zinc-400">Production RAG System</p>
        </div>
        
        <div className="p-6 flex-1 overflow-y-auto">
          <div className="mb-6">
            <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">Knowledge Base</h2>
            
            <div className="space-y-2">
              {documents.length === 0 ? (
                <div className="text-sm text-zinc-500 italic p-3 border border-dashed border-zinc-800 rounded-lg text-center">
                  No documents indexed yet.
                </div>
              ) : (
                documents.map(doc => (
                  <div key={doc} className="group flex items-center justify-between p-3 bg-zinc-800/40 hover:bg-zinc-800/80 border border-zinc-700/50 rounded-lg transition-colors">
                    <div className="flex items-center gap-3 overflow-hidden">
                      <FileText size={16} className="text-indigo-400 shrink-0" />
                      <span className="text-sm truncate" title={doc}>{doc}</span>
                    </div>
                    <button 
                      onClick={() => handleDelete(doc)}
                      className="text-zinc-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="p-6 border-t border-zinc-800/80 bg-zinc-900/80">
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleUpload}
            className="hidden" 
            accept=".pdf,.txt"
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="w-full flex items-center justify-center gap-2 bg-indigo-500 hover:bg-indigo-600 disabled:bg-indigo-500/50 text-white py-2.5 rounded-lg text-sm font-medium transition-colors"
          >
            {isUploading ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}
            {isUploading ? 'Indexing Document...' : 'Upload Document'}
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-zinc-950 relative">
        <div className="flex-1 overflow-y-auto p-6 md:p-12 scroll-smooth">
          <div className="max-w-3xl mx-auto space-y-8">
            
            {messages.map((msg) => (
              <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                
                {msg.role === 'assistant' && (
                  <div className="w-10 h-10 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center shrink-0 mt-1">
                    <Bot size={20} className="text-indigo-400" />
                  </div>
                )}
                
                <div className={`max-w-[80%] ${msg.role === 'user' ? 'bg-zinc-800 text-white rounded-2xl rounded-tr-sm px-5 py-3' : 'bg-transparent text-zinc-300 px-2 py-3'}`}>
                  
                  {/* Hallucination Warning */}
                  {msg.role === 'assistant' && msg.grounded === false && (
                    <div className="flex items-center gap-2 text-amber-500 mb-3 bg-amber-500/10 border border-amber-500/20 px-3 py-2 rounded-md text-sm">
                      <ShieldAlert size={16} />
                      <span className="font-medium">Guardrail Triggered:</span> This answer could not be grounded in the documents.
                    </div>
                  )}

                  <div className="prose prose-invert prose-indigo max-w-none text-sm md:text-base leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </div>

                  {/* Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {msg.citations.map((cite, i) => (
                        <div key={i} className="inline-flex items-center gap-1.5 text-xs font-medium bg-zinc-900 border border-zinc-700/50 text-zinc-400 px-2.5 py-1 rounded-md">
                          <Sparkles size={12} className="text-indigo-400" />
                          {cite.source} <span className="opacity-50">|</span> Pg {cite.page}
                        </div>
                      ))}
                    </div>
                  )}
                  
                </div>

                {msg.role === 'user' && (
                  <div className="w-10 h-10 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center shrink-0 mt-1">
                    <User size={20} className="text-zinc-400" />
                  </div>
                )}

              </div>
            ))}

            {isLoading && (
              <div className="flex gap-4">
                <div className="w-10 h-10 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center shrink-0 mt-1">
                  <Bot size={20} className="text-indigo-400" />
                </div>
                <div className="px-2 py-4 flex items-center gap-2">
                  <Loader2 size={16} className="text-indigo-400 animate-spin" />
                  <span className="text-sm text-zinc-500 font-medium animate-pulse">Synthesizing answer...</span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="p-6 md:p-8 bg-gradient-to-t from-zinc-950 via-zinc-950 to-transparent pt-12">
          <div className="max-w-3xl mx-auto relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask anything about your documents..."
              className="w-full bg-zinc-900/80 border border-zinc-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-2xl px-6 py-4 pr-16 text-white placeholder-zinc-500 shadow-xl backdrop-blur-sm transition-all"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-indigo-500 hover:bg-indigo-600 disabled:bg-zinc-800 disabled:text-zinc-500 text-white rounded-xl transition-colors"
            >
              <Send size={18} />
            </button>
          </div>
          <div className="text-center mt-4">
            <p className="text-xs text-zinc-600">
              PersonaDoc AI uses LLaMA-3 and ChromaDB. Verify critical information.
            </p>
          </div>
        </div>
      </div>
      
    </div>
  );
}
