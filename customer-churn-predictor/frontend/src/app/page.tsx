'use client';

import React, { useState, useRef } from 'react';
import axios from 'axios';
import Papa from 'papaparse';
import { 
  BarChart3, 
  Users, 
  AlertTriangle, 
  Upload, 
  Sparkles,
  Download,
  Filter
} from 'lucide-react';
import { PieChart, Pie, Cell, BarChart as RechartsBarChart, Bar, XAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface Prediction {
  index: number;
  churn_probability: number;
  is_high_risk: boolean;
  dataset_type: string;
  data?: any; // To hold original row data
  explanation?: string;
  loadingExplanation?: boolean;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const DEMO_DATA = [
  { industry: "SaaS", company_size: 150, mrr_usd: 12000, contract_type: "Month-to-Month", tenure_months: 4, active_users: 120, api_calls_per_month: 45000, support_tickets_last_30d: 8, feature_adoption_rate: 0.3, last_login_days_ago: 16 },
  { industry: "Finance", company_size: 400, mrr_usd: 35000, contract_type: "1 Year", tenure_months: 24, active_users: 350, api_calls_per_month: 120000, support_tickets_last_30d: 2, feature_adoption_rate: 0.85, last_login_days_ago: 1 },
];

export default function Dashboard() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [showHighRiskOnly, setShowHighRiskOnly] = useState(false);
  const [visibleCount, setVisibleCount] = useState(50);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processData = async (data: any[]) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/predict`, { customers: data });
      const enriched = response.data.predictions.map((p: any, i: number) => ({
        ...p,
        data: data[i]
      }));
      setPredictions(enriched);
    } catch (error) {
      console.error("Failed to fetch predictions", error);
      alert("Failed to process data. Ensure backend is running.");
    }
    setLoading(false);
  };

  const loadDemoData = () => processData(DEMO_DATA);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    Papa.parse(file, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results) => {
        const data = results.data as any[];
        
        // Remove CustomerID if it exists so we don't send it to the backend for ML
        const cleanedData = data.map(row => {
            const { CustomerID, ...rest } = row;
            return rest;
        });
        
        processData(cleanedData);
      }
    });
  };

  const explainChurn = async (index: number) => {
    if (expandedIndex === index) {
      setExpandedIndex(null);
      return;
    }
    
    setExpandedIndex(index);
    const pred = predictions[index];
    if (pred.explanation) return; 
    
    const newPreds = [...predictions];
    newPreds[index].loadingExplanation = true;
    setPredictions(newPreds);
    
    try {
      const res = await axios.post(`${API_URL}/explain`, pred.data);
      newPreds[index].explanation = res.data.result;
    } catch (e) {
      newPreds[index].explanation = "Failed to generate AI action plan. Is Groq API key set?";
    }
    
    newPreds[index].loadingExplanation = false;
    setPredictions([...newPreds]);
  };

  const exportToCSV = () => {
    const exportData = predictions.map(p => ({
      ...p.data,
      churn_probability_percent: (p.churn_probability * 100).toFixed(1),
      is_high_risk: p.is_high_risk,
      ai_action_plan: p.explanation || "Not generated"
    }));
    
    const csv = Papa.unparse(exportData);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', 'churn_risk_report.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const highRiskCount = predictions.filter(p => p.is_high_risk).length;
  
  // Dynamic Metric Selection (SaaS vs Telecom)
  const isSaaS = predictions.length > 0 && predictions[0].dataset_type === "SaaS";
  const revenueKey = isSaaS ? 'mrr_usd' : 'Total Spend';
  const categoryKey = isSaaS ? 'industry' : 'Subscription Type';
  const metricLabel = isSaaS ? 'MRR At Risk' : 'Total Spend At Risk';

  const revenueAtRisk = predictions.filter(p => p.is_high_risk).reduce((acc, curr) => acc + (curr.data?.[revenueKey] || 0), 0);

  const pieData = [
    { name: 'High Risk', value: highRiskCount },
    { name: 'Safe', value: predictions.length - highRiskCount },
  ];
  const COLORS = ['#ef4444', '#10b981'];

  const categoryRiskMap: Record<string, number> = {};
  predictions.filter(p => p.is_high_risk).forEach(p => {
    const cat = p.data?.[categoryKey] || 'Unknown';
    categoryRiskMap[cat] = (categoryRiskMap[cat] || 0) + (p.data?.[revenueKey] || 0);
  });
  
  const barData = Object.keys(categoryRiskMap).map(key => ({
    category: key,
    revenue: categoryRiskMap[key]
  }));

  const displayedPredictions = showHighRiskOnly 
    ? predictions.filter(p => p.is_high_risk) 
    : predictions;

  // Extract dynamic headers for the table
  const tableHeaders = predictions.length > 0 ? Object.keys(predictions[0].data).slice(0, 4) : [];

  return (
    <div className="min-h-screen p-8 bg-zinc-950 text-zinc-50 font-sans selection:bg-indigo-500/30">
      
      {/* Header */}
      <header className="mb-12 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-2">
            <BarChart3 className="text-indigo-500" />
            Nexus <span className="text-zinc-500 font-normal">| Predict & Prevent</span>
          </h1>
          <p className="text-zinc-400 mt-1">Universal Churn Engine • Auto-detects B2B & B2C Schemas</p>
        </div>
        <div className="flex gap-3 items-center">
          {predictions.length > 0 && (
              <span className="bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 px-3 py-1.5 rounded-full text-xs font-semibold mr-4 flex items-center gap-1.5">
                  <Sparkles size={12} />
                  {predictions[0].dataset_type} Dataset Detected
              </span>
          )}
          <input 
            type="file" 
            accept=".csv" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            className="hidden" 
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={loading}
            className="bg-zinc-800 hover:bg-zinc-700 text-white px-6 py-2.5 rounded-full text-sm font-medium transition-all flex items-center gap-2 border border-zinc-700"
          >
            <Upload size={16} />
            Upload Any CSV
          </button>
          <button 
            onClick={loadDemoData}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-full text-sm font-medium transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] flex items-center gap-2"
          >
            {loading ? "Analyzing..." : "Load SaaS Demo"}
          </button>
        </div>
      </header>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-2xl">
          <div className="flex items-center gap-3 text-zinc-400 mb-2">
            <Users size={18} />
            <h3 className="text-sm font-medium uppercase tracking-wider">Total Evaluated</h3>
          </div>
          <p className="text-4xl font-semibold text-white">{predictions.length}</p>
        </div>
        
        <div className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/10 blur-3xl rounded-full translate-x-10 -translate-y-10"></div>
          <div className="flex items-center gap-3 text-red-400 mb-2 relative z-10">
            <AlertTriangle size={18} />
            <h3 className="text-sm font-medium uppercase tracking-wider">High Risk Churners</h3>
          </div>
          <p className="text-4xl font-semibold text-white relative z-10">{highRiskCount}</p>
        </div>

        <div className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-2xl">
          <div className="flex items-center gap-3 text-green-400 mb-2">
            <span className="text-lg font-bold">$</span>
            <h3 className="text-sm font-medium uppercase tracking-wider">{metricLabel}</h3>
          </div>
          <p className="text-4xl font-semibold text-white">${revenueAtRisk.toLocaleString()}</p>
        </div>
      </div>

      {/* Analytics Dashboard */}
      {predictions.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 h-64">
            <h3 className="text-zinc-400 text-sm font-medium uppercase tracking-wider mb-4">Risk Distribution</h3>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 h-64">
            <h3 className="text-zinc-400 text-sm font-medium uppercase tracking-wider mb-4">{metricLabel} by Category</h3>
            <ResponsiveContainer width="100%" height="100%">
              <RechartsBarChart data={barData}>
                <XAxis dataKey="category" stroke="#52525b" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip cursor={{ fill: '#27272a' }} contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', color: '#fff' }} />
                <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </RechartsBarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Data Table */}
      {predictions.length > 0 && (
        <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl overflow-hidden backdrop-blur-xl">
          <div className="p-6 border-b border-zinc-800 flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold text-white">Universal Retention Queue</h2>
              <p className="text-sm text-zinc-400 mt-1">Dynamic ML Predictions + Generative AI Strategies</p>
            </div>
            <div className="flex gap-3">
              <button 
                onClick={() => setShowHighRiskOnly(!showHighRiskOnly)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 border ${
                  showHighRiskOnly ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-zinc-800 text-zinc-300 border-zinc-700 hover:bg-zinc-700'
                }`}
              >
                <Filter size={14} />
                {showHighRiskOnly ? 'High Risk Only' : 'All Customers'}
              </button>
              <button 
                onClick={exportToCSV}
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2"
              >
                <Download size={14} />
                Export CSV
              </button>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-zinc-900/80 text-zinc-400 text-xs uppercase tracking-wider">
                  {tableHeaders.map(header => (
                    <th key={header} className="p-4 font-medium">{header.replace(/_/g, ' ')}</th>
                  ))}
                  <th className="p-4 font-medium">Churn Probability</th>
                  <th className="p-4 font-medium">Action</th>
                </tr>
              </thead>
              <tbody className="text-sm divide-y divide-zinc-800/50">
                {displayedPredictions.slice(0, visibleCount).map((pred, i) => (
                  <React.Fragment key={pred.index}>
                    <tr className="hover:bg-zinc-800/30 transition-colors">
                      {tableHeaders.map(header => (
                        <td key={header} className="p-4 text-zinc-300">
                          {String(pred.data[header])}
                        </td>
                      ))}
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <span className={`font-bold ${pred.is_high_risk ? 'text-red-400' : 'text-green-400'}`}>
                            {(pred.churn_probability * 100).toFixed(1)}%
                          </span>
                          {pred.is_high_risk && <AlertTriangle size={14} className="text-red-500" />}
                        </div>
                      </td>
                      <td className="p-4">
                        <button 
                          onClick={() => explainChurn(i)}
                          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                            pred.is_high_risk 
                              ? 'bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 border border-indigo-500/20' 
                              : 'bg-zinc-800 text-zinc-500 cursor-not-allowed opacity-50'
                          }`}
                          disabled={!pred.is_high_risk}
                        >
                          <Sparkles size={12} />
                          {pred.loadingExplanation ? "Generating..." : "AI Strategy"}
                        </button>
                      </td>
                    </tr>
                    
                    {/* Explanatory AI Expandable Row */}
                    {expandedIndex === i && pred.is_high_risk && (
                      <tr>
                        <td colSpan={tableHeaders.length + 2} className="p-0 border-b-0">
                          <div className="bg-indigo-950/20 border-y border-indigo-500/20 p-6 shadow-inner">
                            <div className="flex gap-4">
                              <div className="mt-1">
                                <Sparkles className="text-indigo-400" size={20} />
                              </div>
                              <div>
                                <h4 className="text-indigo-300 font-semibold mb-2">LLaMA-3 Action Plan</h4>
                                {pred.loadingExplanation ? (
                                  <div className="animate-pulse flex flex-col gap-2">
                                    <div className="h-4 bg-indigo-900/50 rounded w-3/4"></div>
                                    <div className="h-4 bg-indigo-900/50 rounded w-1/2"></div>
                                  </div>
                                ) : (
                                  <div className="text-indigo-100/80 text-sm leading-relaxed whitespace-pre-wrap">
                                    {pred.explanation}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
          
          {visibleCount < displayedPredictions.length && (
            <div className="p-4 border-t border-zinc-800 text-center">
              <button 
                onClick={() => setVisibleCount(prev => prev + 50)}
                className="text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors"
              >
                Load More ({displayedPredictions.length - visibleCount} remaining)
              </button>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {predictions.length === 0 && (
        <div className="mt-20 text-center flex flex-col items-center">
          <div className="w-16 h-16 bg-zinc-900 border border-zinc-800 rounded-2xl flex items-center justify-center mb-4 text-zinc-600">
            <BarChart3 size={32} />
          </div>
          <h2 className="text-xl font-medium text-white mb-2">Universal Churn Prediction Engine</h2>
          <p className="text-zinc-500 max-w-md mt-2">Upload any standard B2B SaaS or B2C Telecom churn CSV. The backend API will automatically detect the schema and route to the correct XGBoost machine learning model.</p>
        </div>
      )}
    </div>
  );
}
