export type Metric = {
  value: number;
  suffix: string;
  label: string;
};

export type Capability = {
  index: string;
  title: string;
  blurb: string;
  tags: string[];
};

export type Project = {
  id: string;
  name: string;
  kicker: string;
  year: string;
  summary: string;
  stack: string[];
  repo: string;
  live?: string;
  accent: "cyan" | "violet" | "amber";
};

export type SocialLink = {
  label: string;
  handle: string;
  href: string;
};

export const PROFILE = {
  name: "Adarsh Kumar Singh",
  alias: "ENTITY",
  role: "AI \u00b7 ML & Data Engineer",
  location: "India \u00b7 Remote",
  headline: ["I Build", "Autonomous", "AI Systems"],
  intro:
    "I design and ship production-grade AI \u2014 multi-agent systems, RAG pipelines, guardrails and model routing \u2014 engineered to survive the real world, not just a demo.",
  email: "adarshentity098@gmail.com",
  phone: "+91-94394-40544",
  portfolio: "https://cyber-duelist.github.io/AI-Apex-Paragon/",
  github: "https://github.com/Cyber-Duelist/AI-Apex-Paragon",
  linkedin: "https://www.linkedin.com/in/i-am-entity",
};

export const METRICS: Metric[] = [
  { value: 85, suffix: "%", label: "First-pass fix accuracy" },
  { value: 100, suffix: "%", label: "Prompt injections blocked" },
  { value: 14, suffix: "", label: "Weeks relentless building" },
  { value: 3, suffix: "", label: "Professional certifications" },
];

export const CAPABILITIES: Capability[] = [
  {
    index: "01",
    title: "LLM Architecture",
    blurb:
      "ReAct loops, tool calling and orchestration for agents that reason, act and recover instead of hallucinating.",
    tags: ["ReAct", "Tool calling", "Guardrails", "RAG"],
  },
  {
    index: "02",
    title: "Backend Engineering",
    blurb:
      "FastAPI services with SSE streaming, typed REST contracts and Pytest coverage built for throughput and uptime.",
    tags: ["FastAPI", "SSE", "REST", "Pytest"],
  },
  {
    index: "03",
    title: "Production Security",
    blurb:
      "Prompt-injection prevention, scope guardrails and model failover so systems stay safe when users get creative.",
    tags: ["Injection defense", "Scope guards", "Failover"],
  },
  {
    index: "04",
    title: "Data & ML",
    blurb:
      "Predictive modelling, semantic retrieval and evaluation pipelines that turn raw signals into decisions.",
    tags: ["Predictive ML", "Vector search", "Eval"],
  },
];

export const PROJECTS: Project[] = [
  {
    id: "clara",
    name: "CLARA AI",
    kicker: "Multimodal receptionist",
    year: "2025",
    summary:
      "Clinical Language & Adaptive Routing Assistant \u2014 automates triage routing with vision analysis, TTS and a live clinical command center over WebSockets.",
    stack: ["Vision", "TTS", "WebSockets", "Routing"],
    repo: "https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/clara-ai",
    live: "https://ai-apex-paragon-4twi.vercel.app",
    accent: "cyan",
  },
  {
    id: "compliance",
    name: "ComplianceAI Enterprise",
    kicker: "Production RAG",
    year: "2025",
    summary:
      "Sub-second retrieval across 10,000+ vectors with semantic reranking and automated GDPR / HIPAA risk reporting.",
    stack: ["RAG", "Reranking", "GDPR", "HIPAA"],
    repo: "https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/ComplianceAI",
    live: "https://huggingface.co/spaces/IamEntity/ComplianceAI",
    accent: "violet",
  },
  {
    id: "neuralheist",
    name: "NeuralHeist",
    kicker: "Adversarial AI game",
    year: "2025",
    summary:
      "An AI-powered terminal game with an autonomous guard that defends against prompt injection and semantic attacks in real time.",
    stack: ["Agent", "Injection", "Terminal", "Semantic"],
    repo: "https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/api",
    accent: "amber",
  },
  {
    id: "envoy",
    name: "Envoy",
    kicker: "Omni-modal dashboard",
    year: "2025",
    summary:
      "A PyQt5 Chromium desktop app with webcam vision streaming and Kyutai / Pocket-TTS voice interaction over WebSockets.",
    stack: ["PyQt5", "Vision", "Voice", "WebSockets"],
    repo: "https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/week_15_voice_agent",
    accent: "cyan",
  },
  {
    id: "devops-swarm",
    name: "Self-Healing DevOps Swarm",
    kicker: "Autonomous agents",
    year: "2025",
    summary:
      "Diagnoses CI/CD failures, writes patches, verifies fixes in a sandbox and opens pull requests \u2014 with no human in the loop.",
    stack: ["Multi-agent", "CI/CD", "Sandbox", "PRs"],
    repo: "https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/week_14",
    accent: "violet",
  },
  {
    id: "enterprise-agent",
    name: "Enterprise Production Agent",
    kicker: "Governed agent stack",
    year: "2025",
    summary:
      "I/O guardrails, persistent memory, structured logging, LLM-as-a-Judge evaluation and model-failover routing in one deployable stack.",
    stack: ["Guardrails", "Memory", "Eval", "Failover"],
    repo: "https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/week_12",
    live: "https://huggingface.co/spaces/IamEntity/Enterprise_Production_Agent",
    accent: "amber",
  },
  {
    id: "personadoc",
    name: "PersonaDoc",
    kicker: "Cited document RAG",
    year: "2024",
    summary:
      "Upload a PDF and ask anything \u2014 ChromaDB vector search, semantic chunking, reranking and citations with hallucination control.",
    stack: ["ChromaDB", "Chunking", "Citations", "Reranking"],
    repo: "https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/week_09",
    live: "https://personadoc-rag.vercel.app",
    accent: "cyan",
  },
];

export const STACK: string[] = [
  "Python",
  "FastAPI",
  "LangGraph",
  "PyTorch",
  "ChromaDB",
  "PostgreSQL",
  "Docker",
  "TypeScript",
  "React",
  "WebSockets",
  "Hugging Face",
  "Vector Search",
  "LLM Routing",
  "Pytest",
];

export const CERTS: string[] = [
  "Oracle Generative AI Professional",
  "Oracle Data Science Professional",
  "IoT & Industrial Automation",
];

export const SOCIALS: SocialLink[] = [
  {
    label: "GitHub",
    handle: "Cyber-Duelist",
    href: "https://github.com/Cyber-Duelist/AI-Apex-Paragon",
  },
  {
    label: "LinkedIn",
    handle: "i-am-entity",
    href: "https://www.linkedin.com/in/i-am-entity",
  },
  {
    label: "Portfolio",
    handle: "cyber-duelist.github.io",
    href: "https://cyber-duelist.github.io/AI-Apex-Paragon/",
  },
  {
    label: "Email",
    handle: "adarshentity098@gmail.com",
    href: "mailto:adarshentity098@gmail.com",
  },
];

export const NAV_LINKS = [
  { label: "Index", href: "#top" },
  { label: "About", href: "#about" },
  { label: "Work", href: "#work" },
  { label: "Stack", href: "#stack" },
  { label: "Contact", href: "#contact" },
];
