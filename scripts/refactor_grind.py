import os
import re

html_replacement = '''    <!-- Architecture & Certifications -->
    <section id="expertise">
        <div class="section-container">
            <h2 class="section-title">Credentials & Architecture</h2>
            <p class="section-subtitle">Certified enterprise expertise and scalable AI system design.</p>
            
            <div class="expertise-grid">
                <!-- Certifications -->
                <div class="certifications-column">
                    <h3 class="expertise-heading"><i class="fas fa-certificate"></i> Oracle Certifications</h3>
                    <div class="cert-card glass-card">
                        <div class="cert-icon oracle-ai"><i class="fas fa-brain"></i></div>
                        <div class="cert-details">
                            <h4>Generative AI Professional</h4>
                            <p>Oracle Cloud Infrastructure (OCI)</p>
                            <span class="cert-date">2024</span>
                        </div>
                    </div>
                    <div class="cert-card glass-card">
                        <div class="cert-icon oracle-ds"><i class="fas fa-database"></i></div>
                        <div class="cert-details">
                            <h4>Data Science Professional</h4>
                            <p>Oracle Cloud Infrastructure (OCI)</p>
                            <span class="cert-date">2024</span>
                        </div>
                    </div>
                    <div class="cert-card glass-card">
                        <div class="cert-icon iot"><i class="fas fa-microchip"></i></div>
                        <div class="cert-details">
                            <h4>IoT & Industrial Automation</h4>
                            <p>Advanced Sensor Networks</p>
                            <span class="cert-date">2023</span>
                        </div>
                    </div>
                </div>

                <!-- Architecture -->
                <div class="architecture-column">
                    <h3 class="expertise-heading"><i class="fas fa-sitemap"></i> Enterprise AI Architecture</h3>
                    <div class="arch-card glass-card">
                        <div class="arch-diagram">
                            <div class="arch-node user-node"><i class="fas fa-user"></i> Client API</div>
                            <div class="arch-flow"><i class="fas fa-arrow-down"></i></div>
                            <div class="arch-node gateway-node"><i class="fas fa-shield-alt"></i> Semantic Router & Guardrails</div>
                            <div class="arch-flow split">
                                <div class="arch-path"><i class="fas fa-arrow-right"></i> <div class="arch-node child-node"><i class="fas fa-search"></i> RAG Pipeline (ChromaDB)</div></div>
                                <div class="arch-path"><i class="fas fa-arrow-right"></i> <div class="arch-node child-node"><i class="fas fa-network-wired"></i> Multi-Agent Swarm (LLaMA 3)</div></div>
                                <div class="arch-path"><i class="fas fa-arrow-right"></i> <div class="arch-node child-node"><i class="fas fa-eye"></i> Vision AI / Voice (Groq)</div></div>
                            </div>
                        </div>
                        <div class="arch-description">
                            <h4>Scalable Multi-Layered AI Systems</h4>
                            <p>Expertise in designing production-grade AI architectures with strict input/output guardrails, semantic routing, and highly-concurrent multi-agent swarms.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>'''

css_replacement = '''/* =========================================
   EXPERTISE (Certifications & Architecture)
   ========================================= */
#expertise {
    padding: 8rem 0;
    position: relative;
    z-index: 2;
}

.expertise-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    margin-top: 4rem;
}

.expertise-heading {
    font-size: 1.5rem;
    color: var(--primary-color);
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    letter-spacing: 2px;
}

/* Certifications */
.certifications-column {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.cert-card {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 1.5rem;
    transition: transform 0.3s ease, border-color 0.3s ease;
}

.cert-card:hover {
    transform: translateX(10px);
    border-color: var(--primary-color);
}

.cert-icon {
    width: 50px;
    height: 50px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    background: rgba(0, 229, 255, 0.1);
    color: var(--primary-color);
    border: 1px solid rgba(0, 229, 255, 0.3);
}

.cert-icon.oracle-ds {
    color: var(--secondary-color);
    background: rgba(168, 85, 247, 0.1);
    border-color: rgba(168, 85, 247, 0.3);
}

.cert-icon.iot {
    color: var(--accent-color);
    background: rgba(255, 0, 110, 0.1);
    border-color: rgba(255, 0, 110, 0.3);
}

.cert-details h4 {
    font-size: 1.2rem;
    margin-bottom: 0.3rem;
    color: var(--text-color);
}

.cert-details p {
    font-size: 0.9rem;
    color: var(--text-color-muted);
    margin-bottom: 0.5rem;
}

.cert-date {
    font-size: 0.8rem;
    color: var(--primary-color);
    font-family: 'JetBrains Mono', monospace;
    background: rgba(0, 229, 255, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
}

/* Architecture Diagram */
.arch-card {
    padding: 2rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.arch-diagram {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    border: 1px dashed rgba(255,255,255,0.1);
}

.arch-node {
    padding: 0.8rem 1.5rem;
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    z-index: 2;
    border: 1px solid transparent;
}

.user-node {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-color);
    border-color: rgba(255,255,255,0.2);
}

.gateway-node {
    background: rgba(0, 229, 255, 0.1);
    color: var(--primary-color);
    border-color: var(--primary-color);
    box-shadow: 0 0 15px rgba(0,229,255,0.2);
}

.child-node {
    background: rgba(168, 85, 247, 0.1);
    color: var(--secondary-color);
    border-color: var(--secondary-color);
    margin-left: 1rem;
    padding: 0.6rem 1rem;
    font-size: 0.8rem;
    width: 200px;
    text-align: left;
}

.child-node i {
    width: 20px;
}

.arch-flow {
    color: rgba(255,255,255,0.3);
    font-size: 1.2rem;
    margin: 0.5rem 0;
}

.arch-flow.split {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
    width: 100%;
    padding-left: 20%;
    margin-top: 1rem;
}

.arch-path {
    display: flex;
    align-items: center;
    color: rgba(255,255,255,0.2);
    font-size: 1rem;
}

.arch-description h4 {
    font-size: 1.3rem;
    margin-bottom: 0.8rem;
    color: var(--text-color);
}

.arch-description p {
    color: var(--text-color-muted);
    line-height: 1.6;
    font-size: 0.95rem;
}

@media (max-width: 900px) {
    .expertise-grid {
        grid-template-columns: 1fr;
    }
}
'''

def process_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace nav link
    content = re.sub(r'<a href="#grind">The Grind</a>', r'<a href="#expertise">Expertise</a>', content)
    
    # Replace the Grind section
    # Use regex to find the section by id
    pattern = r'<!-- The Grind Timeline -->.*?</section>'
    content = re.sub(pattern, html_replacement, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def process_css(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the timeline section in CSS and replace it
    # We look for /* =========================================\n   TIMELINE\n   ========================================= */
    # and replace everything up to the next big block (PROJECTS)
    pattern = r'/\* =========================================\s*TIMELINE\s*========================================= \*/.*?/\* =========================================\s*PROJECTS'
    replacement = css_replacement + '\n\n/* =========================================\n   PROJECTS'
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

dirs = ['docs', 'portfolio_website']
for d in dirs:
    html_path = os.path.join('D:\\Apex_Paragon\\AI-APEX-PARAGON', d, 'index.html')
    css_path = os.path.join('D:\\Apex_Paragon\\AI-APEX-PARAGON', d, 'style.css')
    
    if os.path.exists(html_path):
        process_html(html_path)
        print(f'Processed {html_path}')
    if os.path.exists(css_path):
        process_css(css_path)
        print(f'Processed {css_path}')

