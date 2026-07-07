import os
import re

html_injection = '''
    <!-- Deep Dive Architecture Section -->
    <section id="deep-dive" style="background: rgba(0,0,0,0.4); border-top: 1px solid rgba(0,229,255,0.1); border-bottom: 1px solid rgba(0,229,255,0.1);">
        <div class="section-container">
            <p class="section-tag" style="color: var(--secondary-color);">SYSTEM BLUEPRINTS</p>
            <h2 class="section-title">Deep Dive: Architectures</h2>
            <p class="section-subtitle">Visualizing the flow of data, agents, and models in production.</p>

            <div class="blueprint-container">
                <!-- CLARA AI Blueprint -->
                <div class="blueprint-card glass-card">
                    <h3>1. CLARA AI (Clinical Language Assistant)</h3>
                    <div class="blueprint-diagram">
                        <div class="bp-node user">Patient Audio</div>
                        <div class="bp-arrow">?</div>
                        <div class="bp-node model"><i class="fas fa-microphone"></i> Groq Whisper<br><small>(STT)</small></div>
                        <div class="bp-arrow">?</div>
                        <div class="bp-node core"><i class="fas fa-brain"></i> LLaMA 3.3<br><small>(Clinical Logic)</small></div>
                        <div class="bp-arrow split-arrow">
                            <div class="bp-path">? <div class="bp-node db"><i class="fas fa-database"></i> Triage DB<br><small>(JSON Tool Call)</small></div></div>
                            <div class="bp-path">? <div class="bp-node vision"><i class="fas fa-eye"></i> Vision AI<br><small>(Wound Analysis)</small></div></div>
                        </div>
                        <div class="bp-arrow">?</div>
                        <div class="bp-node output"><i class="fas fa-volume-up"></i> Groq TTS</div>
                    </div>
                </div>

                <!-- DevOps Swarm Blueprint -->
                <div class="blueprint-card glass-card">
                    <h3>2. Autonomous DevOps Swarm</h3>
                    <div class="blueprint-diagram vertical-diagram">
                        <div class="bp-row">
                            <div class="bp-node user">GitHub CI/CD Webhook</div>
                            <div class="bp-arrow-down">?</div>
                            <div class="bp-node core coordinator"><i class="fas fa-project-diagram"></i> Coordinator Agent</div>
                        </div>
                        <div class="bp-row split-row">
                            <div class="bp-col">
                                <div class="bp-arrow-down">?</div>
                                <div class="bp-node agent"><i class="fas fa-search-dollar"></i> Diagnostics Agent<br><small>(Log Parsing)</small></div>
                            </div>
                            <div class="bp-col">
                                <div class="bp-arrow-down">?</div>
                                <div class="bp-node agent"><i class="fas fa-code"></i> Coder Agent<br><small>(Fix Generation)</small></div>
                            </div>
                            <div class="bp-col">
                                <div class="bp-arrow-down">?</div>
                                <div class="bp-node agent"><i class="fas fa-check-circle"></i> Reviewer Agent<br><small>(Validation)</small></div>
                            </div>
                        </div>
                        <div class="bp-row">
                            <div class="bp-arrow-down merge">?</div>
                            <div class="bp-node output"><i class="fas fa-code-branch"></i> Autonomous PR Submission</div>
                        </div>
                    </div>
                </div>

                <!-- PersonaDoc Blueprint -->
                <div class="blueprint-card glass-card">
                    <h3>3. PersonaDoc (Production RAG)</h3>
                    <div class="blueprint-diagram">
                        <div class="bp-node user">User Query</div>
                        <div class="bp-arrow">?</div>
                        <div class="bp-node model"><i class="fas fa-wave-square"></i> Embedding Model<br><small>(Sentence-Transformers)</small></div>
                        <div class="bp-arrow">?</div>
                        <div class="bp-node db"><i class="fas fa-database"></i> FAISS + ChromaDB<br><small>(Vector Search)</small></div>
                        <div class="bp-arrow">?</div>
                        <div class="bp-node core guardrail"><i class="fas fa-shield-alt"></i> Hallucination Guardrail<br><small>(Semantic Reranking)</small></div>
                        <div class="bp-arrow">?</div>
                        <div class="bp-node output">Verified LLM Output</div>
                    </div>
                </div>
            </div>
        </div>
    </section>
'''

css_injection = '''
/* =========================================
   DEEP DIVE ARCHITECTURES
   ========================================= */
#deep-dive {
    padding: 6rem 0;
    position: relative;
    z-index: 2;
}

.blueprint-container {
    display: flex;
    flex-direction: column;
    gap: 3rem;
    margin-top: 3rem;
}

.blueprint-card {
    padding: 2.5rem;
    background: rgba(10, 15, 30, 0.6);
    border-left: 4px solid var(--secondary-color);
}

.blueprint-card h3 {
    color: var(--secondary-color);
    margin-bottom: 2rem;
    font-size: 1.4rem;
    letter-spacing: 1px;
}

.blueprint-diagram {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 1rem;
    padding: 2.5rem;
    background: rgba(0, 0, 0, 0.4);
    border-radius: 12px;
    border: 1px dashed rgba(255, 255, 255, 0.15);
    font-family: 'JetBrains Mono', monospace;
}

.blueprint-diagram.vertical-diagram {
    flex-direction: column;
}

.bp-node {
    padding: 1rem 1.5rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    line-height: 1.2;
}

.bp-node i {
    font-size: 1.3rem;
    margin-bottom: 0.2rem;
}

.bp-node small {
    font-weight: 400;
    opacity: 0.8;
    font-size: 0.75rem;
}

.bp-node.user { background: rgba(255,255,255,0.05); color: #fff; }
.bp-node.model { background: rgba(0,229,255,0.1); color: #00e5ff; border-color: #00e5ff; }
.bp-node.core { background: rgba(168,85,247,0.15); color: #a855f7; border-color: #a855f7; box-shadow: 0 0 20px rgba(168,85,247,0.2); }
.bp-node.db { background: rgba(255,165,0,0.1); color: #ffa500; border-color: #ffa500; }
.bp-node.vision { background: rgba(255,0,110,0.1); color: #ff006e; border-color: #ff006e; }
.bp-node.output { background: rgba(0,255,136,0.1); color: #00ff88; border-color: #00ff88; }
.bp-node.agent { background: rgba(59,130,246,0.15); color: #3b82f6; border-color: #3b82f6; }
.bp-node.guardrail { background: rgba(255,0,0,0.1); color: #ff4444; border-color: #ff4444; }

.bp-arrow {
    color: rgba(255, 255, 255, 0.4);
    font-size: 1.5rem;
    display: flex;
    align-items: center;
}

.split-arrow {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
}

.bp-path {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: rgba(255,255,255,0.4);
}

.bp-row {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}

.split-row {
    flex-direction: row;
    justify-content: center;
    gap: 3rem;
    margin: 1.5rem 0;
}

.bp-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
}

.bp-arrow-down {
    color: rgba(255, 255, 255, 0.4);
    font-size: 1.5rem;
    margin: 0.5rem 0;
}

@media (max-width: 900px) {
    .blueprint-diagram { flex-direction: column; padding: 1.5rem; }
    .bp-arrow { transform: rotate(90deg); margin: 0.5rem 0; }
    .split-arrow { align-items: center; }
    .bp-path { flex-direction: column; }
    .split-row { flex-direction: column; gap: 1.5rem; }
}
'''

def inject_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to inject right after the end of <section id="projects">
    # We find <!-- Skills Section --> or <section id="skills"> and insert before it
    pattern = r'(\s*<!-- Skills Section -->\s*<section id="skills">)'
    
    if "id=\"deep-dive\"" not in content:
        content = re.sub(pattern, html_injection + r'\1', content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Injected HTML into {filepath}")
    else:
        print(f"Deep dive already in {filepath}")

def inject_css(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to inject right after PROJECTS section CSS
    # Find /* =========================================\n   SKILLS
    pattern = r'(/\* =========================================\s*SKILLS\s*========================================= \*/)'
    
    if "DEEP DIVE ARCHITECTURES" not in content:
        content = re.sub(pattern, css_injection + '\n' + r'\1', content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Injected CSS into {filepath}")
    else:
        print(f"Deep dive CSS already in {filepath}")

dirs = ['docs', 'portfolio_website']
for d in dirs:
    html_path = os.path.join('D:\\Apex_Paragon\\AI-APEX-PARAGON', d, 'index.html')
    css_path = os.path.join('D:\\Apex_Paragon\\AI-APEX-PARAGON', d, 'style.css')
    
    if os.path.exists(html_path):
        inject_html(html_path)
    if os.path.exists(css_path):
        inject_css(css_path)

