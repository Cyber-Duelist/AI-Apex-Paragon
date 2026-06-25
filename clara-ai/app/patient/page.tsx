"use client";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import styles from "./patient.module.css";

interface Message {
  role: "user" | "assistant";
  content: string;
  hiddenContext?: string;
  timestamp: Date;
}

interface TriageData {
  patient_name: string;
  dob: string;
  complaint: string;
  urgency: "EMERGENCY" | "URGENT" | "ROUTINE" | "ADMIN";
  action: string;
  pharmacy_first: boolean;
  clinical_summary: string;
  red_flags: string[];
  severity: number;
  needs_image?: boolean;
}

interface VisionAnalysis {
  finding: string;
  clinical_observations: string[];
  risk_indicators: string[];
  urgency_signal: "LOW" | "MODERATE" | "HIGH";
  estimated_severity_out_of_10: number;
  recommended_action: string;
  disclaimer: string;
}

const URGENCY_COLORS: Record<string, string> = {
  EMERGENCY: "#ef4444",
  URGENT: "#f97316",
  ROUTINE: "#22c55e",
  ADMIN: "#3b82f6",
};

export default function PatientPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [triageData, setTriageData] = useState<TriageData | null>(null);
  const [needsImage, setNeedsImage] = useState(false);
  const [visionAnalysis, setVisionAnalysis] = useState<VisionAnalysis | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [analyzingImage, setAnalyzingImage] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const speakText = (text: string) => {
    if (isMuted || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const voices = window.speechSynthesis.getVoices();
    const ukVoice = voices.find((v) => v.lang === "en-GB" && v.name.includes("Female")) || 
                    voices.find((v) => v.lang === "en-GB");
    if (ukVoice) utterance.voice = ukVoice;
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  const startListening = () => {
    // @ts-ignore
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support speech recognition. Please use Chrome or Edge.");
      return;
    }
    
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-GB';
    recognition.interimResults = false;
    
    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) => prev + (prev ? " " : "") + transcript);
    };
    recognition.onerror = (event: any) => {
      console.error("Speech error", event.error);
      setIsListening(false);
    };
    recognition.onend = () => setIsListening(false);
    
    recognition.start();
  };

  useEffect(() => {
    // Auto-start: CLARA greets the patient
    sendMessage("", true);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (text: string, isInit = false) => {
    if (!isInit && (!text.trim() || loading)) return;

    const userMessage: Message = {
      role: "user",
      content: text,
      timestamp: new Date(),
    };

    const newMessages = isInit ? [] : [...messages, userMessage];
    if (!isInit) setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: isInit
            ? [{ role: "user", content: "Hello" }]
            : newMessages.map((m) => ({ 
                role: m.role, 
                content: m.hiddenContext ? `${m.content}\n\n[SYSTEM KNOWLEDGE INJECTION]: ${m.hiddenContext}` : m.content 
              })),
          sessionId,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "API returned an error");

      const assistantMessage: Message = {
        role: "assistant",
        content: data.message,
        timestamp: new Date(),
      };

      setMessages((prev) => (isInit ? [assistantMessage] : [...prev, assistantMessage]));
      speakText(data.message);

      if (data.triageData) {
        setTriageData(data.triageData);
        // Save to localStorage for dashboard
        const existing = JSON.parse(localStorage.getItem("clara_patients") || "[]");
        const newPatient = {
          ...data.triageData,
          sessionId,
          timestamp: new Date().toISOString(),
          visionAnalysis,
        };
        localStorage.setItem(
          "clara_patients",
          JSON.stringify([newPatient, ...existing].slice(0, 20))
        );
      }

      if (data.needsImage) setNeedsImage(true);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `ERROR: ${err.message}`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
      if (!isInit) inputRef.current?.focus();
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const preview = URL.createObjectURL(file);
    setImagePreview(preview);
    setAnalyzingImage(true);

    const userMsg: Message = {
      role: "user",
      content: "📷 [Image uploaded for clinical analysis]",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const formData = new FormData();
      formData.append("image", file);

      const res = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setVisionAnalysis(data.analysis);

      const analysisMsg: Message = {
        role: "assistant",
        content: `Thank you for the image. I've completed a preliminary visual assessment. The analysis has been added to your case file. I'll continue with a couple more questions to complete your triage.`,
        hiddenContext: `The user just uploaded an image. Vision AI Analysis: Finding: ${data.analysis.finding}. Estimated Severity: ${data.analysis.estimated_severity_out_of_10}/10. CRITICAL INSTRUCTION: DO NOT ask the user to rate their severity out of 10. You ALREADY have the severity score from the Vision AI (${data.analysis.estimated_severity_out_of_10}/10). Use this severity score to complete the triage JSON now without asking the patient to rate it.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, analysisMsg]);
      speakText(analysisMsg.content);
      setNeedsImage(false);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I couldn't process the image. Please continue with your description.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setAnalyzingImage(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className={styles.page}>
      {/* Ambient orb */}
      <div className={styles.orb} />

      {/* Header */}
      <header className={styles.header}>
        <button className={styles.backBtn} onClick={() => router.push("/")}>
          ← Back
        </button>
        <div className={styles.headerCenter}>
          <div className={styles.statusDot} />
          <span className={styles.headerTitle}>CLARA</span>
          <span className={styles.headerSub}>AI Receptionist</span>
        </div>
        <div className={styles.headerRight}>
          <button 
            onClick={() => setIsMuted(!isMuted)} 
            style={{ background: 'none', border: 'none', color: '#475569', cursor: 'pointer', fontSize: '1.2rem', marginRight: '12px' }}
            title={isMuted ? "Unmute Voice" : "Mute Voice"}
          >
            {isMuted ? "🔇" : "🔊"}
          </button>
          <span className={styles.nhsBadge}>NHS AI</span>
        </div>
      </header>

      {/* Triage result card */}
      {triageData && (
        <div
          className={styles.triageCard}
          style={{ borderColor: URGENCY_COLORS[triageData.urgency] + "40" }}
        >
          <div className={styles.triageTop}>
            <span className={styles.triageTitle}>✅ Triage Complete</span>
            <span
              className={styles.urgencyBadge}
              style={{
                background: URGENCY_COLORS[triageData.urgency] + "20",
                color: URGENCY_COLORS[triageData.urgency],
                borderColor: URGENCY_COLORS[triageData.urgency] + "40",
              }}
            >
              {triageData.urgency}
            </span>
          </div>
          <div className={styles.triageGrid}>
            <div className={styles.triageItem}>
              <span className={styles.triageLabel}>Patient</span>
              <span className={styles.triageValue}>{triageData.patient_name}</span>
            </div>
            <div className={styles.triageItem}>
              <span className={styles.triageLabel}>Action</span>
              <span className={styles.triageValue}>{triageData.action}</span>
            </div>
            {triageData.pharmacy_first && (
              <div className={styles.triageItem} style={{ gridColumn: "1 / -1" }}>
                <span className={styles.triagePill}>💊 Pharmacy First Eligible</span>
              </div>
            )}
          </div>
          <p className={styles.triageSummary}>{triageData.clinical_summary}</p>
        </div>
      )}

      {/* Vision analysis card */}
      {visionAnalysis && (
        <div className={styles.visionCard}>
          <div className={styles.visionHeader}>
            <span>🔬 Vision AI Analysis</span>
            <span
              className={styles.visionBadge}
              style={{
                color: visionAnalysis.urgency_signal === "HIGH" ? "#ef4444" : visionAnalysis.urgency_signal === "MODERATE" ? "#f97316" : "#22c55e",
              }}
            >
              {visionAnalysis.urgency_signal} SIGNAL
            </span>
          </div>
          <p className={styles.visionType}>{visionAnalysis.finding}</p>
          <ul className={styles.visionList}>
            {visionAnalysis.clinical_observations.map((o, i) => (
              <li key={i}>{o}</li>
            ))}
          </ul>
          <p className={styles.visionDisclaimer}>{visionAnalysis.disclaimer}</p>
        </div>
      )}

      {/* Chat messages */}
      <div className={styles.chat}>
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`${styles.bubble} ${msg.role === "user" ? styles.userBubble : styles.assistantBubble} fade-in`}
          >
            {msg.role === "assistant" && (
              <div className={styles.avatarDot}>C</div>
            )}
            <div
              className={`${styles.bubbleContent} ${msg.role === "user" ? styles.userContent : styles.assistantContent}`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className={`${styles.bubble} ${styles.assistantBubble} fade-in`}>
            <div className={styles.avatarDot}>C</div>
            <div className={`${styles.bubbleContent} ${styles.assistantContent}`}>
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        )}

        {imagePreview && (
          <div className={`${styles.bubble} ${styles.userBubble} fade-in`}>
            <div className={styles.imagePreviewWrap}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={imagePreview} alt="Uploaded" className={styles.imagePreview} />
              {analyzingImage && (
                <div className={styles.analyzingOverlay}>
                  <span>🔬 Analyzing...</span>
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className={styles.inputArea}>
        {needsImage && (
          <button
            id="upload-image-btn"
            className={styles.imageBtn}
            onClick={() => fileInputRef.current?.click()}
          >
            📷 Upload Photo
          </button>
        )}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleImageUpload}
          accept="image/*"
          capture="environment"
          style={{ display: "none" }}
        />
        <div className={styles.inputRow}>
          {isListening ? (
            <div className={styles.visualizerWrap}>
              <div className={styles.bar}></div>
              <div className={styles.bar}></div>
              <div className={styles.bar}></div>
              <div className={styles.bar}></div>
              <div className={styles.bar}></div>
              <button className={styles.stopMicBtn} onClick={() => {
                // @ts-ignore
                window.SpeechRecognition?.abort?.();
                setIsListening(false);
              }}>
                🛑
              </button>
            </div>
          ) : (
            <button
              onClick={startListening}
              className={styles.micBtn}
              title="Speak"
              disabled={loading}
            >
              🎤
            </button>
          )}
          <input
            id="patient-input"
            ref={inputRef}
            className={styles.input}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your response..."
            disabled={loading}
          />
          <button
            id="send-btn"
            className={styles.sendBtn}
            onClick={() => sendMessage(input)}
            disabled={loading || !input.trim()}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
