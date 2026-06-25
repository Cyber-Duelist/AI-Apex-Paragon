"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import styles from "./dashboard.module.css";

interface TriagePatient {
  sessionId: string;
  timestamp: string;
  patient_name: string;
  dob: string;
  complaint: string;
  urgency: "EMERGENCY" | "URGENT" | "ROUTINE" | "ADMIN";
  action: string;
  pharmacy_first: boolean;
  soap_note: {
    subjective: string;
    objective: string;
    assessment: string;
    plan: string;
  };
  red_flags: string[];
  severity: number;
  visionAnalysis?: {
    finding: string;
    clinical_observations: string[];
    risk_indicators: string[];
    urgency_signal: "LOW" | "MODERATE" | "HIGH";
    estimated_severity_out_of_10: number;
    recommended_action: string;
    disclaimer: string;
  };
}

const URGENCY_CONFIG: Record<string, { color: string; bg: string; icon: string; order: number }> = {
  EMERGENCY: { color: "#ef4444", bg: "rgba(239,68,68,0.08)", icon: "🚨", order: 0 },
  URGENT:    { color: "#f97316", bg: "rgba(249,115,22,0.08)", icon: "⚡", order: 1 },
  ROUTINE:   { color: "#22c55e", bg: "rgba(34,197,94,0.08)",  icon: "📋", order: 2 },
  ADMIN:     { color: "#3b82f6", bg: "rgba(59,130,246,0.08)", icon: "📎", order: 3 },
};

// Demo patients to show the dashboard in action
const DEMO_PATIENTS: TriagePatient[] = [
  {
    sessionId: "demo_1",
    timestamp: new Date(Date.now() - 4 * 60000).toISOString(),
    patient_name: "Sarah Thompson",
    dob: "15/03/1985",
    complaint: "Chest tightness and shortness of breath",
    urgency: "URGENT",
    action: "Duty Doctor Callback within 2 hours",
    pharmacy_first: false,
    severity: 7,
    red_flags: ["chest tightness", "shortness of breath"],
    soap_note: {
      subjective: "48-year-old female presenting with 2-day history of chest tightness radiating to left arm, rated 7/10. Associated dyspnoea on exertion.",
      objective: "AI Triage. No visual data.",
      assessment: "Query Acute Coronary Syndrome. High clinical concern.",
      plan: "ECG advised. Same-day clinical review required."
    },
  },
  {
    sessionId: "demo_2",
    timestamp: new Date(Date.now() - 9 * 60000).toISOString(),
    patient_name: "James Patel",
    dob: "22/07/1992",
    complaint: "Sore throat and difficulty swallowing",
    urgency: "ROUTINE",
    action: "Pharmacy First — pharmacist consultation recommended",
    pharmacy_first: true,
    severity: 4,
    red_flags: [],
    soap_note: {
      subjective: "32-year-old male with 3-day sore throat, mild odynophagia, no systemic symptoms. No fever.",
      objective: "AI Triage. Vision AI confirmed mild erythema, no tonsillar exudate.",
      assessment: "Centor score 1. Likely viral pharyngitis.",
      plan: "Pharmacy First referral appropriate. Self-care advice provided."
    },
    visionAnalysis: {
      finding: "Oropharyngeal photograph — posterior pharynx",
      clinical_observations: ["Mild erythema of posterior pharyngeal wall", "No tonsillar exudate", "Uvula midline"],
      risk_indicators: ["none identified"],
      urgency_signal: "LOW",
      estimated_severity_out_of_10: 4,
      recommended_action: "Pharmacy First referral appropriate. No urgent clinical review required.",
      disclaimer: "AI pre-screening only. Clinical assessment required by a qualified practitioner.",
    },
  },
  {
    sessionId: "demo_3",
    timestamp: new Date(Date.now() - 18 * 60000).toISOString(),
    patient_name: "Margaret Wilson",
    dob: "03/11/1948",
    complaint: "Sudden severe headache — worst of life",
    urgency: "EMERGENCY",
    action: "Call 999 immediately — thunderclap headache",
    pharmacy_first: false,
    severity: 10,
    red_flags: ["thunderclap headache", "worst headache of life", "sudden onset"],
    soap_note: {
      subjective: "75-year-old female reporting sudden onset severe headache described as 'worst of life', 10/10. Onset during exertion. No trauma. Neck stiffness reported.",
      objective: "AI Triage. No visual data.",
      assessment: "Subarachnoid haemorrhage cannot be excluded. Emergency.",
      plan: "999 activated immediately."
    },
  },
];

export default function DashboardPage() {
  const router = useRouter();
  const [patients, setPatients] = useState<TriagePatient[]>([]);
  const [selected, setSelected] = useState<TriagePatient | null>(null);
  const [filter, setFilter] = useState<string>("ALL");
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const generatePDF = (patient: TriagePatient) => {
    const printWindow = window.open('', '_blank', 'width=800,height=900');
    if (!printWindow) return;

    const visionHtml = patient.visionAnalysis ? `
      <div style="margin-top: 20px; border: 1px solid #c7d2fe; padding: 15px; border-radius: 8px; background: #f0f4ff;">
        <h3 style="margin-top: 0; color: #3730a3; font-size: 14px; text-transform: uppercase;">Vision AI Analysis</h3>
        <p style="margin-bottom: 5px;"><strong>Finding:</strong> ${patient.visionAnalysis.finding}</p>
        <p style="margin-bottom: 10px;"><strong>Urgency Signal:</strong> <span style="color: #ea580c; font-weight: bold;">${patient.visionAnalysis.urgency_signal}</span></p>
        <ul style="margin-bottom: 15px; padding-left: 20px;">
          ${patient.visionAnalysis.clinical_observations.map((o: string) => `<li>${o}</li>`).join('')}
        </ul>
        <p style="margin-bottom: 5px; font-size: 13px;"><strong>Risk Indicators:</strong> ${patient.visionAnalysis.risk_indicators.join(', ')}</p>
        <p style="margin-bottom: 0; font-size: 13px;"><strong>GP Note:</strong> ${patient.visionAnalysis.recommended_action}</p>
      </div>
    ` : '';

    const html = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Clinical Handover - ${patient.patient_name}</title>
          <style>
            body { font-family: system-ui, -apple-system, sans-serif; color: #1e293b; padding: 40px; line-height: 1.6; max-width: 800px; margin: 0 auto; }
            h1 { color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; font-size: 24px; }
            .header-info { display: flex; justify-content: space-between; margin-bottom: 30px; font-size: 14px; }
            .box { background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            h3 { color: #475569; margin-top: 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
          </style>
        </head>
        <body>
          <h1>CLARA Clinical Handover</h1>
          <div class="header-info">
            <div><strong>Patient Name:</strong> ${patient.patient_name}</div>
            <div><strong>DOB:</strong> ${patient.dob}</div>
            <div><strong>Date Generated:</strong> ${new Date().toLocaleString()}</div>
          </div>
          
          <div style="margin-bottom: 10px; font-size: 15px;">
            <strong>Triage Urgency:</strong> <span style="font-weight: bold;">${patient.urgency}</span>
          </div>
          <div style="margin-bottom: 25px; font-size: 15px;">
            <strong>Recommended Action:</strong> ${patient.action}
          </div>

          <div class="box">
            <h3>Clinical Summary (SOAP)</h3>
            <p style="margin: 0; padding-bottom: 5px;"><strong>S:</strong> ${patient.soap_note?.subjective || patient.clinical_summary || 'N/A'}</p>
            <p style="margin: 0; padding-bottom: 5px;"><strong>O:</strong> ${patient.soap_note?.objective || 'N/A'}</p>
            <p style="margin: 0; padding-bottom: 5px;"><strong>A:</strong> ${patient.soap_note?.assessment || 'N/A'}</p>
            <p style="margin: 0;"><strong>P:</strong> ${patient.soap_note?.plan || 'N/A'}</p>
          </div>

          <div class="box" style="background: ${patient.red_flags.length > 0 ? '#fef2f2' : '#f8fafc'}; border-color: ${patient.red_flags.length > 0 ? '#fecaca' : '#e2e8f0'};">
            <h3>Red Flags</h3>
            ${patient.red_flags.length > 0 ? `<ul style="margin: 0; padding-left: 20px;">${patient.red_flags.map((r: string) => `<li style="color: #991b1b;">${r}</li>`).join('')}</ul>` : '<p style="margin: 0;">None identified</p>'}
          </div>
          
          <div class="box" style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin: 0;">Patient Severity Score</h3>
            <span style="font-size: 24px; font-weight: bold; color: #334155;">${patient.severity}/10</span>
          </div>

          ${visionHtml}
          
          <div style="margin-top: 50px; border-top: 1px solid #e2e8f0; padding-top: 20px; font-size: 12px; color: #64748b; text-align: center;">
            Generated automatically by CLARA AI. Clinical assessment required by a qualified practitioner.
          </div>
          
          <script>
            window.onload = function() { window.print(); window.onafterprint = function() { window.close(); } };
          </script>
        </body>
      </html>
    `;

    printWindow.document.open();
    printWindow.document.write(html);
    printWindow.document.close();
  };

  useEffect(() => {
    loadPatients();
    const interval = setInterval(loadPatients, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadPatients = () => {
    const stored: TriagePatient[] = JSON.parse(
      localStorage.getItem("clara_patients") || "[]"
    );
    // Merge demo + real, dedupe by sessionId
    const all = [...DEMO_PATIENTS, ...stored].filter(
      (p, i, arr) => arr.findIndex((x) => x.sessionId === p.sessionId) === i
    );
    // Sort by urgency priority then time
    all.sort((a, b) => {
      const ao = URGENCY_CONFIG[a.urgency]?.order ?? 4;
      const bo = URGENCY_CONFIG[b.urgency]?.order ?? 4;
      if (ao !== bo) return ao - bo;
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    });
    setPatients(all);
    setLastRefresh(new Date());
  };

  const filtered = filter === "ALL" ? patients : patients.filter((p) => p.urgency === filter);

  const counts = {
    ALL: patients.length,
    EMERGENCY: patients.filter((p) => p.urgency === "EMERGENCY").length,
    URGENT: patients.filter((p) => p.urgency === "URGENT").length,
    ROUTINE: patients.filter((p) => p.urgency === "ROUTINE").length,
    ADMIN: patients.filter((p) => p.urgency === "ADMIN").length,
  };

  const timeAgo = (iso: string) => {
    const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return `${mins}m ago`;
    return `${Math.floor(mins / 60)}h ago`;
  };

  return (
    <div className={styles.page}>
      <div className={styles.orb1} />
      <div className={styles.orb2} />

      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <button className={styles.backBtn} onClick={() => router.push("/")}>← Back</button>
          <div>
            <div className={styles.headerTitle}>
              <span className={styles.claraLogo}>CLARA</span>
              <span className={styles.headerSub}>Doctor&apos;s Command Center</span>
            </div>
            <p className={styles.refreshTime}>
              Last updated: {lastRefresh.toLocaleTimeString()}
            </p>
          </div>
        </div>
        <div className={styles.headerRight}>
          <div className={styles.liveIndicator}>
            <div className={styles.liveDot} />
            LIVE
          </div>
          <button
            id="new-patient-btn"
            className={styles.newPatientBtn}
            onClick={() => router.push("/patient")}
          >
            + New Patient
          </button>
        </div>
      </header>

      {/* Stats row */}
      <div className={styles.statsRow}>
        {Object.entries(URGENCY_CONFIG).map(([key, cfg]) => (
          <div
            key={key}
            className={styles.statCard}
            style={{ borderColor: cfg.color + "30" }}
          >
            <span className={styles.statIcon}>{cfg.icon}</span>
            <span className={styles.statNum} style={{ color: cfg.color }}>
              {counts[key as keyof typeof counts] ?? 0}
            </span>
            <span className={styles.statLabel}>{key}</span>
          </div>
        ))}
        {/* Quick Analytics Panel */}
        <div className={styles.statCard} style={{ borderColor: "#8b5cf630" }}>
          <span className={styles.statIcon}>⏱️</span>
          <span className={styles.statNum} style={{ color: "#8b5cf6" }}>
            {patients.length * 5}m
          </span>
          <span className={styles.statLabel}>GP TIME SAVED</span>
        </div>
        <div className={styles.statCard} style={{ borderColor: "#10b98130" }}>
          <span className={styles.statIcon}>👥</span>
          <span className={styles.statNum} style={{ color: "#10b981" }}>
            {patients.length}
          </span>
          <span className={styles.statLabel}>TOTAL TRIAGED</span>
        </div>
      </div>

      <div className={styles.body}>
        {/* Left: queue */}
        <div className={styles.queue}>
          {/* Filter tabs */}
          <div className={styles.filterTabs}>
            {["ALL", "EMERGENCY", "URGENT", "ROUTINE", "ADMIN"].map((f) => (
              <button
                key={f}
                id={`filter-${f.toLowerCase()}`}
                className={`${styles.filterTab} ${filter === f ? styles.activeTab : ""}`}
                onClick={() => setFilter(f)}
                style={
                  filter === f && f !== "ALL"
                    ? {
                        background: URGENCY_CONFIG[f]?.bg,
                        borderColor: URGENCY_CONFIG[f]?.color + "50",
                        color: URGENCY_CONFIG[f]?.color,
                      }
                    : {}
                }
              >
                {URGENCY_CONFIG[f]?.icon ?? "📋"} {f}{" "}
                <span className={styles.tabCount}>{counts[f as keyof typeof counts] ?? 0}</span>
              </button>
            ))}
          </div>

          {/* Patient cards */}
          <div className={styles.patientList}>
            {filtered.map((p) => {
              const cfg = URGENCY_CONFIG[p.urgency];
              return (
                <button
                  key={p.sessionId}
                  id={`patient-${p.sessionId}`}
                  className={`${styles.patientCard} ${selected?.sessionId === p.sessionId ? styles.selectedCard : ""} ${p.urgency === "EMERGENCY" ? styles.emergencyPulse : ""}`}
                  onClick={() => setSelected(p)}
                  style={
                    selected?.sessionId === p.sessionId
                      ? { borderColor: cfg.color + "60", background: cfg.bg }
                      : {}
                  }
                >
                  <div className={styles.cardTop}>
                    <div>
                      <span className={styles.patientName}>{p.patient_name}</span>
                      <span className={styles.patientDob}>{p.dob}</span>
                    </div>
                    <span
                      className={styles.urgencyPill}
                      style={{ background: cfg.bg, color: cfg.color, borderColor: cfg.color + "40" }}
                    >
                      {cfg.icon} {p.urgency}
                    </span>
                  </div>
                  <p className={styles.cardComplaint}>{p.complaint}</p>
                  <div className={styles.cardMeta}>
                    <span>{timeAgo(p.timestamp)}</span>
                    {p.pharmacy_first && <span className={styles.pharmacyTag}>💊 Pharmacy First</span>}
                    {p.visionAnalysis && <span className={styles.visionTag}>🔬 Vision AI</span>}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right: detail panel */}
        <div className={styles.detail}>
          {selected ? (
            <div className={styles.detailContent}>
              {/* Patient header */}
              <div className={styles.detailHeader}>
                <div>
                  <h2 className={styles.detailName}>{selected.patient_name}</h2>
                  <p className={styles.detailDob}>DOB: {selected.dob} · Triaged {timeAgo(selected.timestamp)}</p>
                </div>
                <span
                  className={styles.detailUrgency}
                  style={{
                    background: URGENCY_CONFIG[selected.urgency].bg,
                    color: URGENCY_CONFIG[selected.urgency].color,
                    borderColor: URGENCY_CONFIG[selected.urgency].color + "40",
                  }}
                >
                  {URGENCY_CONFIG[selected.urgency].icon} {selected.urgency}
                </span>
              </div>

              {/* Action banner */}
              <div
                className={styles.actionBanner}
                style={{ borderColor: URGENCY_CONFIG[selected.urgency].color + "30" }}
              >
                <span className={styles.actionLabel}>Recommended Action</span>
                <span className={styles.actionValue}>{selected.action}</span>
              </div>

              {/* Clinical summary (SOAP) */}
              <div className={styles.section}>
                <h3 className={styles.sectionTitle}>📄 Clinical Summary (SOAP)</h3>
                <div className={styles.soapGrid}>
                  <div className={styles.soapBlock}><strong>S:</strong> {selected.soap_note?.subjective || (selected as any).clinical_summary || 'N/A'}</div>
                  <div className={styles.soapBlock}><strong>O:</strong> {selected.soap_note?.objective || 'N/A'}</div>
                  <div className={styles.soapBlock}><strong>A:</strong> {selected.soap_note?.assessment || 'N/A'}</div>
                  <div className={styles.soapBlock}><strong>P:</strong> {selected.soap_note?.plan || 'N/A'}</div>
                </div>
              </div>

              {/* Severity + red flags */}
              <div className={styles.twoCol}>
                <div className={styles.section}>
                  <h3 className={styles.sectionTitle}>🔴 Red Flags</h3>
                  {selected.red_flags.length > 0 ? (
                    <ul className={styles.redFlagList}>
                      {selected.red_flags.map((f, i) => (
                        <li key={i}>{f}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className={styles.noFlags}>None identified</p>
                  )}
                </div>
                <div className={styles.section}>
                  <h3 className={styles.sectionTitle}>📊 Severity Score</h3>
                  <div className={styles.severityBar}>
                    <div
                      className={styles.severityFill}
                      style={{
                        width: `${(selected.severity / 10) * 100}%`,
                        background:
                          selected.severity >= 8
                            ? "#ef4444"
                            : selected.severity >= 5
                            ? "#f97316"
                            : "#22c55e",
                      }}
                    />
                  </div>
                  <p className={styles.severityNum}>{selected.severity}/10</p>
                </div>
              </div>

              {/* Pharmacy First */}
              {selected.pharmacy_first && (
                <div className={styles.pharmacyBanner}>
                  💊 <strong>Pharmacy First Eligible</strong> — Patient may be directed to a local pharmacist without a GP appointment.
                </div>
              )}

              {/* Vision AI analysis */}
              {selected.visionAnalysis && (
                <div className={styles.section}>
                  <h3 className={styles.sectionTitle}>🔬 Vision AI Analysis</h3>
                  <div className={styles.visionCard}>
                    <div className={styles.visionMeta}>
                      <span>{selected.visionAnalysis.finding}</span>
                      <span
                        className={styles.visionSignal}
                        style={{
                          color:
                            selected.visionAnalysis.urgency_signal === "HIGH"
                              ? "#ef4444"
                              : selected.visionAnalysis.urgency_signal === "MODERATE"
                              ? "#f97316"
                              : "#22c55e",
                        }}
                      >
                        {selected.visionAnalysis.urgency_signal} SIGNAL
                      </span>
                    </div>
                    <ul className={styles.visionObs}>
                      {selected.visionAnalysis.clinical_observations.map((o, i) => (
                        <li key={i}>{o}</li>
                      ))}
                    </ul>
                    {selected.visionAnalysis.risk_indicators[0] !== "none identified" && (
                      <div className={styles.riskIndicators}>
                        <span className={styles.riskLabel}>Risk Indicators:</span>
                        {selected.visionAnalysis.risk_indicators.map((r, i) => (
                          <span key={i} className={styles.riskTag}>{r}</span>
                        ))}
                      </div>
                    )}
                    <p className={styles.visionRec}><strong>GP Note:</strong> {selected.visionAnalysis.recommended_action}</p>
                    <p className={styles.visionDisclaimer}>{selected.visionAnalysis.disclaimer}</p>
                  </div>
                </div>
              )}

              {/* Action buttons */}
              <div className={styles.actionButtons}>
                <button
                  id="copy-emis-btn"
                  className={styles.emisBtn}
                  onClick={() => {
                    const soap = selected.soap_note || { subjective: (selected as any).clinical_summary || "N/A", objective: "N/A", assessment: "N/A", plan: "N/A" };
                    const text = `CLARA Clinical Summary\n\nPatient: ${selected.patient_name} | DOB: ${selected.dob}\nUrgency: ${selected.urgency}\nAction: ${selected.action}\n\nS: ${soap.subjective}\nO: ${soap.objective}\nA: ${soap.assessment}\nP: ${soap.plan}\n\nRed Flags: ${selected.red_flags?.join(", ") || "None"}\nSeverity: ${selected.severity}/10`;
                    
                    if (navigator.clipboard) {
                      navigator.clipboard.writeText(text).then(() => {
                        alert("Copied to clipboard!");
                      }).catch((err) => {
                        alert("Failed to copy. Your browser might block clipboard access.");
                        console.error(err);
                      });
                    } else {
                      alert("Clipboard API not available. Please copy manually.");
                    }
                  }}
                >
                  📋 Copy to EMIS
                </button>
                <button
                  id="pdf-btn"
                  className={styles.pdfBtn}
                  onClick={() => generatePDF(selected)}
                >
                  📄 Download PDF
                </button>
              </div>
            </div>
          ) : (
            <div className={styles.emptyDetail}>
              <div className={styles.emptyIcon}>🏥</div>
              <h3>Select a patient</h3>
              <p>Click any patient in the queue to view their AI-generated clinical summary and triage details.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
