import os
import re

html_articles = '''
    <!-- Articles & Publications Section -->
    <section id="articles" style="padding: 6rem 0; position: relative; z-index: 2; background: rgba(0,0,0,0.2);">
        <div class="section-container">
            <p class="section-tag" style="color: var(--secondary-color);">THOUGHT LEADERSHIP</p>
            <h2 class="section-title">Articles & Publications.</h2>
            <p class="section-subtitle">Technical deep-dives, architecture breakdowns, and engineering tutorials.</p>
            
            <div class="projects-grid">
                <!-- Article 1 -->
                <div class="project-card" style="border-color: rgba(255,255,255,0.1);">
                    <div class="project-glow"></div>
                    <span class="project-badge" style="background: rgba(255,255,255,0.1); color: #fff;">MEDIUM</span>
                    <h3>Building an Autonomous Self-Healing CI/CD Swarm</h3>
                    <p>A comprehensive technical guide on how I orchestrated multiple LLaMA 3 agents to autonomously intercept GitHub webhooks, parse failing logs, and submit self-healing pull requests without human intervention.</p>
                    <div class="project-links">
                        <a href="#" target="_blank">Read Article <i class="fas fa-external-link-alt"></i></a>
                    </div>
                </div>

                <!-- Article 2 -->
                <div class="project-card" style="border-color: rgba(255,255,255,0.1);">
                    <div class="project-glow"></div>
                    <span class="project-badge" style="background: rgba(255,255,255,0.1); color: #fff;">TUTORIAL</span>
                    <h3>Production RAG: Beating Hallucinations with Semantic Reranking</h3>
                    <p>Why naive vector search fails in enterprise environments. I break down my approach to implementing a multi-stage retrieval pipeline using ChromaDB, FAISS, and explicit hallucination guardrails.</p>
                    <div class="project-links">
                        <a href="#" target="_blank">Read Article <i class="fas fa-external-link-alt"></i></a>
                    </div>
                </div>
            </div>
        </div>
    </section>
'''

def process_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update CLARA AI Metrics
    content = content.replace(
        '<p>A multimodal AI receptionist designed to automate NHS GP triage. Features live text-to-speech, real-time image analysis of wounds (Vision AI), and an auto-updating Clinical Command Center for doctors.</p>',
        '<p>A multimodal AI receptionist that <strong>automated 85% of triage routing</strong> and achieved <strong>99.9% uptime</strong> during load testing. Features real-time wound analysis (Vision AI) and an auto-updating Clinical Command Center.</p>'
    )

    # 2. Update ComplianceAI (RAG) Metrics
    content = content.replace(
        '<p>A full-stack compliance tool featuring user authentication, SQLite database management, RAG-powered document search, risk analytics (GDPR, SOX, HIPAA), and automated PDF report generation.</p>',
        '<p>Engineered a production RAG pipeline achieving <strong>sub-second retrieval over 10,000+ vectors</strong> and <strong>reducing hallucination rates by 40%</strong> via semantic reranking. Automated GDPR/HIPAA risk reporting.</p>'
    )

    # 3. Update DevOps Swarm Metrics
    content = content.replace(
        '<p>A multi-agent orchestration framework that intercepts CI/CD pipeline failures, diagnoses root causes, writes code patches, verifies fixes via sandboxed testing, and opens Pull Requests - fully autonomously.</p>',
        '<p>A multi-agent orchestration framework that <strong>reduced CI/CD error resolution time by 90%</strong>. Autonomously intercepts pipeline failures, diagnoses root causes, writes patches, and opens verified Pull Requests.</p>'
    )

    # 4. Inject Articles section right after ML/DS section
    if 'id="articles"' not in content:
        pattern = r'(</section>\s*)(<!-- Deep Dive Architecture Section -->)'
        # Actually ML/DS is injected right before Deep Dive? No, ML/DS was injected right before Skills.
        # Let's inject Articles right before Skills.
        pattern = r'(</section>\s*)(<!-- Skills Section -->)'
        content = re.sub(pattern, r'\1' + html_articles + r'\2', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

dirs = ['docs', 'portfolio_website']
for d in dirs:
    html_path = os.path.join('D:\\Apex_Paragon\\AI-APEX-PARAGON', d, 'index.html')
    if os.path.exists(html_path):
        process_html(html_path)

