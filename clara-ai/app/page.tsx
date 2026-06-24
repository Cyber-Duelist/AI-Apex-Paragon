"use client";
import { useRouter } from "next/navigation";
import styles from "./page.module.css";

export default function Home() {
  const router = useRouter();

  return (
    <main className={styles.main}>
      {/* Ambient glow orbs */}
      <div className={styles.orb1} />
      <div className={styles.orb2} />

      <div className={styles.container}>
        {/* Logo / Brand */}
        <div className={styles.brand}>
          <div className={styles.logoMark}>
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <path d="M14 2L26 8V20L14 26L2 20V8L14 2Z" stroke="#38bdf8" strokeWidth="1.5" fill="rgba(14,165,233,0.08)" />
              <path d="M14 8V20M8 11L20 17M8 17L20 11" stroke="#38bdf8" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </div>
          <span className={styles.logoText}>CLARA</span>
          <span className={styles.logoBadge}>NHS AI</span>
        </div>

        {/* Hero */}
        <h1 className={styles.hero}>
          <span className="gradient-text">Clinical Language &</span>
          <br />
          <span className="gradient-text">Adaptive Routing Assistant</span>
        </h1>
        <p className={styles.subtitle}>
          AI-powered triage and reception for NHS GP surgeries.
          Multi-modal intelligence — text and vision diagnostics.
        </p>

        {/* Role selector cards */}
        <div className={styles.cards}>
          <button
            id="patient-portal-btn"
            className={`${styles.card} glass`}
            onClick={() => router.push("/patient")}
          >
            <div className={styles.cardIcon}>🩺</div>
            <div className={styles.cardContent}>
              <h2>I am a Patient</h2>
              <p>Speak with CLARA about your symptoms. Get triaged instantly.</p>
            </div>
            <div className={styles.cardArrow}>→</div>
          </button>

          <button
            id="doctor-dashboard-btn"
            className={`${styles.card} ${styles.cardDoctor} glass`}
            onClick={() => router.push("/dashboard")}
          >
            <div className={styles.cardIcon}>🏥</div>
            <div className={styles.cardContent}>
              <h2>Doctor&apos;s Dashboard</h2>
              <p>View live triage queue, AI summaries, and vision reports.</p>
            </div>
            <div className={styles.cardArrow}>→</div>
          </button>
        </div>

        {/* Stats bar */}
        <div className={styles.stats}>
          {[
            { value: "8am", label: "Rush handled" },
            { value: "< 3s", label: "Triage time" },
            { value: "100%", label: "Calls answered" },
            { value: "AI+Vision", label: "Multi-modal" },
          ].map((s) => (
            <div key={s.label} className={styles.stat}>
              <span className={styles.statValue}>{s.value}</span>
              <span className={styles.statLabel}>{s.label}</span>
            </div>
          ))}
        </div>

        <p className={styles.footer}>
          Powered by Groq · Llama 3 · Vision AI &nbsp;|&nbsp; Built for QuantumLoop AI
        </p>
      </div>
    </main>
  );
}
