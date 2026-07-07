import os

html_replacement = '''    <!-- Deep Dive Architecture Section -->
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
                        <div class="bp-arrow">&#10140;</div>
                        <div class="bp-node model"><i class="fas fa-microphone"></i> Groq Whisper<br><small>(STT)</small></div>
                        <div class="bp-arrow">&#10140;</div>
                        <div class="bp-node core"><i class="fas fa-brain"></i> LLaMA 3.3<br><small>(Clinical Logic)</small></div>
                        <div class="bp-arrow split-arrow">
                            <div class="bp-path">&#10140; <div class="bp-node db"><i class="fas fa-database"></i> Triage DB<br><small>(JSON Tool Call)</small></div></div>
                            <div class="bp-path">&#10140; <div class="bp-node vision"><i class="fas fa-eye"></i> Vision AI<br><small>(Wound Analysis)</small></div></div>
                        </div>
                        <div class="bp-arrow">&#10140;</div>
                        <div class="bp-node output"><i class="fas fa-volume-up"></i> Groq TTS</div>
                    </div>
                </div>

                <!-- DevOps Swarm Blueprint -->
                <div class="blueprint-card glass-card">
                    <h3>2. Autonomous DevOps Swarm</h3>
                    <div class="blueprint-diagram vertical-diagram">
                        <div class="bp-row">
                            <div class="bp-node user">GitHub CI/CD Webhook</div>
                            <div class="bp-arrow-down">&#8595;</div>
                            <div class="bp-node core coordinator"><i class="fas fa-project-diagram"></i> Coordinator Agent</div>
                        </div>
                        <div class="bp-row split-row">
                            <div class="bp-col">
                                <div class="bp-arrow-down">&#8601;</div>
                                <div class="bp-node agent"><i class="fas fa-search-dollar"></i> Diagnostics Agent<br><small>(Log Parsing)</small></div>
                            </div>
                            <div class="bp-col">
                                <div class="bp-arrow-down">&#8595;</div>
                                <div class="bp-node agent"><i class="fas fa-code"></i> Coder Agent<br><small>(Fix Generation)</small></div>
                            </div>
                            <div class="bp-col">
                                <div class="bp-arrow-down">&#8600;</div>
                                <div class="bp-node agent"><i class="fas fa-check-circle"></i> Reviewer Agent<br><small>(Validation)</small></div>
                            </div>
                        </div>
                        <div class="bp-row">
                            <div class="bp-arrow-down merge">&#8595;</div>
                            <div class="bp-node output"><i class="fas fa-code-branch"></i> Autonomous PR Submission</div>
                        </div>
                    </div>
                </div>

                <!-- PersonaDoc Blueprint -->
                <div class="blueprint-card glass-card">
                    <h3>3. PersonaDoc (Production RAG)</h3>
                    <div class="blueprint-diagram">
                        <div class="bp-node user">User Query</div>
                        <div class="bp-arrow">&#10140;</div>
                        <div class="bp-node model"><i class="fas fa-wave-square"></i> Embedding Model<br><small>(Sentence-Transformers)</small></div>
                        <div class="bp-arrow">&#10140;</div>
                        <div class="bp-node db"><i class="fas fa-database"></i> FAISS + ChromaDB<br><small>(Vector Search)</small></div>
                        <div class="bp-arrow">&#10140;</div>
                        <div class="bp-node core guardrail"><i class="fas fa-shield-alt"></i> Hallucination Guardrail<br><small>(Semantic Reranking)</small></div>
                        <div class="bp-arrow">&#10140;</div>
                        <div class="bp-node output">Verified LLM Output</div>
                    </div>
                </div>
            </div>
        </div>
    </section>'''

def fix_arrows(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    start_str = '<!-- Deep Dive Architecture Section -->'
    end_str = '</section>'
    
    if start_str in content:
        start_idx = content.find(start_str)
        # Find the first </section> after start_idx
        end_idx = content.find(end_str, start_idx) + len(end_str)
        
        # Replace the broken block with the clean one
        new_content = content[:start_idx] + html_replacement + content[end_idx:]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")
    else:
        print(f"Section not found in {filepath}")

for d in ['docs', 'portfolio_website']:
    path = os.path.join('D:\\Apex_Paragon\\AI-APEX-PARAGON', d, 'index.html')
    if os.path.exists(path):
        fix_arrows(path)
