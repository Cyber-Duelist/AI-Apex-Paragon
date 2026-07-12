export const site = {
  name: 'Adarsh Kumar Singh',
  handle: 'Entity',
  role: 'AI Software Engineer (B.Tech student)',
  email: 'adarshentity098@gmail.com',
  phone: '+91-94394-40544',
  github: 'https://github.com/Cyber-Duelist/AI-Apex-Paragon',
  linkedin: 'https://www.linkedin.com/in/i-am-entity',
  resumePdf: 'https://cyber-duelist.github.io/AI-Apex-Paragon/resume.pdf',
  headline: "I build autonomous AI systems that don't fall over in production.",
  subheadline:
    'GENERATIVE AI · MULTI-AGENT ORCHESTRATION · PRODUCTION RAG · ENTERPRISE GUARDRAILS',
  bio: `I'm Adarsh Kumar Singh — an AI Software Engineer and B.Tech student who ships autonomous systems, not demos. Over 14 weeks I've built and deployed 9 production-grade systems spanning multi-agent orchestration, hardened RAG pipelines, and enterprise guardrails. I work under the handle Entity.`,
  stats: {
    weeksBuilding: 14,
    systemsShipped: 9,
    certifications: 3,
  },
} as const;

export const routingRules = [
  {
    domain: 'LLM Architecture',
    condition: 'if domain == "LLM Architecture"',
    routes: ['ReAct loops', 'guardrails', 'RAG pipelines'],
  },
  {
    domain: 'Multi-Agent Orchestration',
    condition: 'if domain == "Multi-Agent Swarm"',
    routes: ['coordinator agents', 'diagnostics agents', 'autonomous PR workflows'],
  },
  {
    domain: 'Production Engineering',
    condition: 'if domain == "Enterprise Deploy"',
    routes: ['I/O guardrails', 'structured logging', 'model failover'],
  },
] as const;

export const capabilityDomains = [
  {
    name: 'LLM & RAG',
    tags: [
      'Groq LLaMA 3.3',
      'ChromaDB',
      'Embeddings',
      'RAG',
      'Vision AI',
      'TTS',
      'Prompt Engineering',
      'JSON Schema',
    ],
  },
  {
    name: 'Systems & Infra',
    tags: [
      'Python',
      'FastAPI',
      'Next.js',
      'Docker',
      'WebSockets',
      'Vercel Serverless',
      'PyQt5',
      'GitHub API',
    ],
  },
  {
    name: 'ML & Ops',
    tags: ['Multi-Agent', 'Guardrails', 'LLMOps', 'XGBoost', 'Pytest', 'Streamlit'],
  },
] as const;

export const certifications = [
  {
    name: 'Generative AI Professional',
    org: 'Oracle Cloud Infrastructure (OCI)',
    year: 2024,
    pdf: 'https://cyber-duelist.github.io/AI-Apex-Paragon/oracle-genai.pdf',
  },
  {
    name: 'Data Science Professional',
    org: 'Oracle Cloud Infrastructure (OCI)',
    year: 2024,
    pdf: 'https://cyber-duelist.github.io/AI-Apex-Paragon/oracle-data-science.pdf',
  },
  {
    name: 'IoT & Industrial Automation',
    org: 'Advanced Sensor Networks',
    year: 2023,
    pdf: 'https://cyber-duelist.github.io/AI-Apex-Paragon/geeksforgeeks-genai.pdf',
  },
] as const;

export const projects = [
  {
    index: '01/09',
    category: 'NHS AI Prototype',
    title: 'CLARA AI — Clinical Language & Adaptive Routing Assistant',
    desc: 'Multimodal AI receptionist. Automated 85% of triage routing, 99.9% uptime under load testing. Real-time wound analysis via vision AI.',
    tags: ['Next.js', 'Groq LLaMA 3.3', 'Vision AI', 'TTS', 'WebSockets'],
    code: 'https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/clara-ai',
    demo: 'https://ai-apex-paragon-4twi.vercel.app',
  },
  {
    index: '02/09',
    category: 'MVP Product',
    title: 'ComplianceAI Enterprise',
    desc: 'Production RAG pipeline. Sub-second retrieval over 10,000+ vectors, 40% hallucination reduction via semantic reranking. Automated GDPR/HIPAA risk reporting.',
    tags: ['Python', 'Streamlit', 'ChromaDB', 'Groq', 'Docker'],
    code: 'https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/ComplianceAI',
    demo: 'https://huggingface.co/spaces/IamEntity/ComplianceAI',
  },
  {
    index: '03/09',
    category: 'Game Backend',
    title: 'NeuralHeist',
    desc: 'Terminal game where players prompt-inject an autonomous AI guard. Vercel serverless function, dynamic guard defenses.',
    tags: ['Python', 'Vercel Serverless', 'OpenAI API', 'Prompt Engineering'],
    code: 'https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/api',
    demo: 'https://cyber-duelist.github.io/AI-Apex-Paragon/neural-heist/index.html',
  },
  {
    index: '04/09',
    category: 'Desktop App',
    title: 'Envoy — Omni-Modal AI Dashboard',
    desc: 'PyQt5 Chromium browser. Live webcam vision streaming, WebGL glass UI, zero-latency voice over WebSockets.',
    tags: ['PyQt5', 'FastAPI', 'Kyutai TTS', 'WebSockets', 'LLaMA-3.2-Vision'],
    code: 'https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/week_15_voice_agent',
    demo: null,
  },
  {
    index: '05/09',
    category: 'Capstone',
    title: 'Autonomous Self-Healing DevOps Swarm',
    desc: 'Multi-agent framework that intercepts CI/CD failures, diagnoses root cause, writes patches, verifies in sandbox, opens PRs — fully autonomously.',
    tags: ['Python', 'Groq', 'LLaMA 3', 'Pytest', 'Multi-Agent'],
    code: 'https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/week_14',
    demo: null,
  },
  {
    index: '06/09',
    category: 'Production Agent',
    title: 'Enterprise Production Agent',
    desc: 'Hardened compliance agent. I/O guardrails, persistent memory, structured logging, LLM-as-a-Judge eval dashboard, automatic model failover.',
    tags: ['Python', 'FastAPI', 'Guardrails', 'LLMOps'],
    code: 'https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/week_12',
    demo: 'https://huggingface.co/spaces/IamEntity/Enterprise_Production_Agent',
  },
  {
    index: '07/09',
    category: 'Production RAG',
    title: 'PersonaDoc',
    desc: 'Upload a PDF, ask questions, get cited answers. ChromaDB vector search, semantic chunking, reranking, hallucination control.',
    tags: ['RAG', 'ChromaDB', 'Embeddings', 'FastAPI'],
    code: 'https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/week_09',
    demo: 'https://personadoc-rag.vercel.app',
  },
  {
    index: '08/09',
    category: 'Dev Tooling',
    title: 'AI Code Review Service',
    desc: 'Submit a GitHub PR URL, get a structured LLM code review — bugs, security issues, severity ratings, approval decision.',
    tags: ['GitHub API', 'LLaMA 3', 'JSON Schema'],
    code: 'https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/week_12',
    demo: 'https://huggingface.co/spaces/IamEntity/Enterprise_Production_Agent',
  },
  {
    index: '09/09',
    category: 'Predictive Modeling',
    title: 'Nexus — Enterprise Churn Predictor',
    desc: 'B2B SaaS churn prediction. XGBoost model + LLaMA-3 explainable-AI risk mitigation strategies.',
    tags: ['XGBoost', 'Next.js', 'FastAPI', 'LLaMA-3'],
    code: 'https://github.com/Cyber-Duelist/AI-Apex-Paragon/tree/main/customer-churn-predictor',
    demo: 'https://ai-apex-paragon-2ysi.vercel.app/',
  },
] as const;

export const architecturePipelines = [
  {
    name: 'CLARA AI',
    flow: [
      'Patient Audio',
      'Groq Whisper (STT)',
      'LLaMA 3.3 (Clinical Logic)',
      'Triage DB (JSON Tool Call)',
      'Vision AI (Wound Analysis)',
      'Groq TTS',
    ],
  },
  {
    name: 'Autonomous DevOps Swarm',
    flow: [
      'GitHub CI/CD Webhook',
      'Coordinator Agent',
      'Diagnostics Agent',
      'Coder Agent',
      'Reviewer Agent',
      'Autonomous PR',
    ],
  },
  {
    name: 'PersonaDoc RAG',
    flow: [
      'User Query',
      'Embedding Model',
      'FAISS + ChromaDB',
      'Hallucination Guardrail',
      'Verified Output',
    ],
  },
  {
    name: 'Envoy Omni-Modal',
    flow: [
      'PyQt5 Chromium UI',
      'WebSockets',
      'FastAPI Backend',
      'Kyutai TTS',
      'Vision AI (LLaMA-3.2)',
    ],
  },
] as const;

export const pipelineStages = [
  'Client',
  'Semantic Router & Guardrails',
  'RAG Pipeline',
  'Multi-Agent Swarm',
  'Verified Output',
] as const;
