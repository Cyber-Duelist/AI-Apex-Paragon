from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "AI_Apex_Paragon_Codex_Blueprint.pdf"


def stylesheet():
    base = getSampleStyleSheet()
    navy = colors.HexColor("#12355B")
    teal = colors.HexColor("#1B998B")
    dark = colors.HexColor("#202020")

    base.add(
        ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=30,
            leading=36,
            alignment=TA_CENTER,
            textColor=navy,
            spaceAfter=18,
        )
    )
    base.add(
        ParagraphStyle(
            "CoverSubtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=13,
            leading=18,
            alignment=TA_CENTER,
            textColor=dark,
            spaceAfter=12,
        )
    )
    base.add(
        ParagraphStyle(
            "SectionTitle",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=23,
            textColor=navy,
            spaceBefore=8,
            spaceAfter=10,
        )
    )
    base.add(
        ParagraphStyle(
            "PhaseTitle",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=teal,
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    base.add(
        ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.6,
            leading=13.5,
            textColor=dark,
            spaceAfter=6,
        )
    )
    base.add(
        ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11.5,
            textColor=dark,
        )
    )
    base.add(
        ParagraphStyle(
            "Callout",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=colors.white,
            backColor=navy,
            borderPadding=8,
            spaceBefore=8,
            spaceAfter=10,
        )
    )
    return base


def bullets(items, styles):
    rows = [["-", Paragraph(item, styles["Body"])] for item in items]
    t = Table(rows, colWidths=[0.18 * inch, 6.25 * inch], hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1B998B")),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    return t


def table(data, widths):
    t = Table(data, colWidths=widths, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12355B")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.3),
                ("LEADING", (0, 0), (-1, -1), 10.5),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D6DEE8")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8FA")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(inch * 0.65, 0.45 * inch, "AI Apex Paragon - Codex Blueprint")
    canvas.drawRightString(A4[0] - inch * 0.65, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build():
    styles = stylesheet()
    story = []

    story.append(Spacer(1, 1.15 * inch))
    story.append(Paragraph("AI APEX PARAGON", styles["CoverTitle"]))
    story.append(Paragraph("Codex Job-Focused Blueprint", styles["CoverTitle"]))
    story.append(
        Paragraph(
            "From Python foundations to production AI systems, RAG, agents, evaluation, deployment, and a high-paying AI engineering job.",
            styles["CoverSubtitle"],
        )
    )
    story.append(Spacer(1, 0.25 * inch))
    meta = [
        ["Student", "Adarsh - AI Apex Paragon"],
        ["Teacher", "Codex"],
        ["Duration", "12 to 14 weeks full-time"],
        ["Goal", "Job-ready AI Engineer / GenAI Engineer by July-August 2026"],
        ["Core Strategy", "3 excellent portfolio projects, daily commits, DeepML + DSA in parallel"],
        ["North Star", "ENTITY - a local, private, voice-controlled AI PC agent"],
    ]
    story.append(table(meta, [1.6 * inch, 4.8 * inch]))
    story.append(Spacer(1, 0.35 * inch))
    story.append(
        Paragraph(
            "Rule: We do not learn everything. We learn what compounds into job skill, portfolio proof, and interview confidence.",
            styles["Callout"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("Daily Operating System", styles["SectionTitle"]))
    daily = [
        ["Time", "Track", "Outcome"],
        ["6:00 - 8:00 AM", "DSA or DeepML", "Interview patterns or ML math muscle"],
        ["8:00 AM - 1:00 PM", "Main AI Engineering", "Best five hours for coding and building"],
        ["2:00 - 4:00 PM", "Concepts + implementation", "Understand, code, debug, explain"],
        ["4:00 - 6:00 PM", "Project work", "Portfolio features, docs, tests, deploys"],
        ["7:00 - 8:00 PM", "Review + GitHub", "Notes, explain-back, commit, push"],
    ]
    story.append(table(daily, [1.55 * inch, 1.85 * inch, 3.1 * inch]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Parallel Tracks", styles["PhaseTitle"]))
    story.append(
        bullets(
            [
                "<b>Project 3:</b> Main AI Engineering - Python, APIs, SQL, FastAPI, LLMs, RAG, agents, deployment.",
                "<b>Project 4:</b> DeepML - vector math, NumPy, metrics, regression, similarity, embeddings.",
                "<b>Project 5:</b> DSA - arrays, strings, hash maps, two pointers, recursion, trees, graphs, interview explanations.",
            ],
            styles,
        )
    )
    story.append(Paragraph("Execution Loop", styles["PhaseTitle"]))
    story.append(Paragraph("Understand - Code - Break - Debug - Explain - Commit - Push - Publish.", styles["Callout"]))
    story.append(PageBreak())

    story.append(Paragraph("Phase 0 - Current Checkpoint And Week 2 Patch", styles["SectionTitle"]))
    story.append(
        Paragraph(
            "You have already built beginner Python, Git, files, JSON, APIs, Pandas practice, merging, pivot tables, Matplotlib, Seaborn, and charts. We do not restart. We patch gaps and move forward.",
            styles["Body"],
        )
    )
    story.append(Paragraph("Week 2 Completion Sprint", styles["PhaseTitle"]))
    story.append(
        bullets(
            [
                "Add NumPy linear algebra: arrays, vector operations, dot product, matrix multiplication, cosine similarity.",
                "Add statistics basics: mean, median, standard deviation, correlation, probability counts.",
                "Build a real EDA project folder with dataset, cleaned analysis, charts, findings, and README.",
                "Clean minor script issues and push the repo.",
            ],
            styles,
        )
    )
    story.append(Paragraph("Exit Criteria", styles["PhaseTitle"]))
    story.append(
        bullets(
            [
                "Can explain DataFrame cleaning, grouping, merging, pivoting, and charting.",
                "Can implement dot product and cosine similarity in NumPy.",
                "Can present 5 clear findings from a real dataset.",
            ],
            styles,
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("Phase 1 - Foundation And Data", styles["SectionTitle"]))
    phase1 = [
        ["Week", "Focus", "Topics", "Output"],
        ["1", "Python + Git + APIs", "Loops, dictionaries, functions, files, JSON, requests, venv, GitHub", "Clean foundation repo with API scripts"],
        ["2", "NumPy + Pandas + EDA", "Arrays, linear algebra, statistics, cleaning, merge, groupby, pivot, charts", "Polished EDA project"],
    ]
    story.append(table(phase1, [0.55 * inch, 1.35 * inch, 3.15 * inch, 1.65 * inch]))
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "This phase makes you fluent enough to handle data and API-shaped objects without fear. It is the base layer for every AI system.",
            styles["Body"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("Phase 2 - Classical Machine Learning", styles["SectionTitle"]))
    phase2 = [
        ["Week", "Focus", "Topics", "Output"],
        ["3", "ML Fundamentals", "Train-test split, regression, classification, trees, random forest, metrics", "Supervised ML project"],
        ["4", "ML Project + Kaggle", "Feature engineering, encoding, scaling, cross-validation, tuning, model comparison", "Kaggle-style project with README"],
    ]
    story.append(table(phase2, [0.55 * inch, 1.35 * inch, 3.15 * inch, 1.65 * inch]))
    story.append(Spacer(1, 10))
    story.append(
        bullets(
            [
                "DeepML alignment: metrics, MSE, accuracy, precision, recall, vector operations.",
                "Interview alignment: explain bias, variance, overfitting, leakage, and why a metric was chosen.",
                "Portfolio rule: one polished notebook beats five unfinished experiments.",
            ],
            styles,
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("Phase 3 - Backend For AI", styles["SectionTitle"]))
    phase3 = [
        ["Week", "Focus", "Topics", "Output"],
        ["5", "SQL + FastAPI", "SQL basics, SQLite/Postgres, REST APIs, Pydantic, CRUD, status codes", "Database-backed API project"],
        ["6", "Production Python", "Env vars, logging, pytest, Docker basics, background tasks, deploy basics", "Deployed FastAPI mini-service"],
    ]
    story.append(table(phase3, [0.55 * inch, 1.35 * inch, 3.15 * inch, 1.65 * inch]))
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "This is where you start looking like an engineer, not just an ML learner. Most GenAI products are backend systems with LLM calls inside.",
            styles["Callout"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("Phase 4 - LLM Engineering And RAG", styles["SectionTitle"]))
    phase4 = [
        ["Week", "Focus", "Topics", "Output"],
        ["7", "LLM APIs", "Prompting, structured outputs, streaming, tool calling, retries, rate limits, cost tracking", "LLM assistant API"],
        ["8", "RAG Fundamentals", "Embeddings, chunking, vector search, metadata, citations, document ingestion", "PersonaDoc RAG begins"],
        ["9", "RAG Production", "Hybrid search, reranking, hallucination control, eval datasets, FastAPI integration", "Portfolio Project 1"],
    ]
    story.append(table(phase4, [0.55 * inch, 1.35 * inch, 3.15 * inch, 1.65 * inch]))
    story.append(Spacer(1, 10))
    story.append(
        bullets(
            [
                "RAG must include citations, source tracking, chunk strategy, and failure cases.",
                "Evaluation is mandatory: golden questions, retrieval checks, answer checks, latency and cost.",
                "PersonaDoc is the first public-grade portfolio project.",
            ],
            styles,
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("Phase 5 - Agents, Evaluation, And LLMOps", styles["SectionTitle"]))
    phase5 = [
        ["Week", "Focus", "Topics", "Output"],
        ["10", "AI Agents", "Tools, function calling, planning loops, memory/state, human approval, failure recovery", "Agent workflow prototype"],
        ["11", "LLMOps + Evals", "Prompt versioning, golden datasets, LLM-as-judge, traces, latency, cost, safety", "Portfolio Project 2"],
        ["12", "Production Agent", "Tools, memory, APIs, deployment, UI/logs, case study", "Portfolio Project 3"],
    ]
    story.append(table(phase5, [0.55 * inch, 1.35 * inch, 3.15 * inch, 1.65 * inch]))
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "A real agent is not a chatbot. It is an LLM plus tools, memory, state, guardrails, logs, evaluation, and recovery behavior.",
            styles["Callout"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("Phase 6 - Portfolio And Job Attack", styles["SectionTitle"]))
    phase6 = [
        ["Week", "Focus", "Actions", "Output"],
        ["13", "Portfolio Polish", "READMEs, architecture diagrams, demo videos, deployment, case studies", "Three job-ready projects"],
        ["14", "Job Attack", "Resume, LinkedIn, outreach, mock interviews, AI system design, applications", "Daily applications and interviews"],
    ]
    story.append(table(phase6, [0.55 * inch, 1.35 * inch, 3.35 * inch, 1.45 * inch]))
    story.append(Spacer(1, 10))
    story.append(
        bullets(
            [
                "Apply before you feel ready. Readiness grows through interviews.",
                "Every project needs a business problem, architecture, screenshots, demo, tradeoffs, and what you would improve.",
                "Target roles: AI Engineer, GenAI Engineer, LLM Application Engineer, ML Engineer, AI Backend Engineer.",
            ],
            styles,
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("The 3 Main Portfolio Projects", styles["SectionTitle"]))
    projects = [
        ["Project", "What It Proves", "Required Features"],
        ["1. PersonaDoc RAG", "You can build document intelligence systems.", "Upload/ingest docs, chunking, embeddings, vector search, citations, evals, deployed demo"],
        ["2. Multi-LLM Router + Eval Dashboard", "You understand cost, latency, quality, fallbacks, and production judgment.", "Model routing, retries, token/cost logging, eval set, dashboard, fallback logic"],
        ["3. Agentic Workflow App", "You can build agents that do useful work, not just chat.", "Tool use, memory/state, human approval, logs, error handling, deployment"],
    ]
    story.append(table(projects, [1.55 * inch, 2.15 * inch, 2.95 * inch]))
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "Quality rule: 3 excellent projects beat 30 small scripts. Each project must be understandable by a recruiter and respected by an engineer.",
            styles["Callout"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("ENTITY - The North Star", styles["SectionTitle"]))
    story.append(
        Paragraph(
            "ENTITY is the advanced capstone: a local, private, voice-controlled PC agent. It is not the first job project. It is the final boss that our portfolio components prepare us to build.",
            styles["Body"],
        )
    )
    entity = [
        ["Component", "Technology Direction", "When We Build It"],
        ["Voice", "Whisper local speech-to-text", "After RAG and agents"],
        ["Brain", "Local LLM via Ollama or similar", "After LLM API mastery"],
        ["Memory", "RAG over notes, history, documents", "During PersonaDoc"],
        ["Tools", "Python functions and APIs", "During agent phase"],
        ["Eyes", "Screenshots and computer vision", "Advanced extension"],
        ["Hands", "Safe OS automation", "Advanced extension with guardrails"],
    ]
    story.append(table(entity, [1.15 * inch, 2.65 * inch, 2.85 * inch]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("ENTITY build order: RAG memory - tool calling - agent state - local LLM - voice - vision - OS control.", styles["Callout"]))
    story.append(PageBreak())

    story.append(Paragraph("The Code Of Paragon", styles["SectionTitle"]))
    rules = [
        "<b>Rule 1 - Ship weekly.</b> Every week ends with something committed, documented, or deployed.",
        "<b>Rule 2 - Explain it back.</b> If you cannot explain it simply, you do not own it yet.",
        "<b>Rule 3 - Daily commit ritual.</b> Code, commit, push. Momentum becomes visible proof.",
        "<b>Rule 4 - DeepML stays small but daily.</b> 20 to 60 minutes. It sharpens the math behind AI.",
        "<b>Rule 5 - DSA is targeted.</b> Enough to pass interviews, not enough to derail AI engineering.",
        "<b>Rule 6 - Evaluation is not optional.</b> Every serious LLM project needs tests, evals, logs, and failure analysis.",
        "<b>Rule 7 - Rest protects ambition.</b> Sleep is part of memory, judgment, and speed.",
        "<b>Rule 8 - ENTITY is the north star.</b> We build toward it piece by piece without letting it consume the job path.",
    ]
    story.append(bullets(rules, styles))
    story.append(Spacer(1, 16))
    story.append(
        Paragraph(
            "The blueprint is not the victory. The commits, projects, interviews, and shipped systems are the victory.",
            styles["Callout"],
        )
    )

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.7 * inch,
        title="AI Apex Paragon Codex Blueprint",
        author="Codex",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
