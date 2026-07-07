import os
import re

html_injection = '''
    <!-- ML & Data Science Projects Section -->
    <section id="ml-ds-projects">
        <div class="section-container">
            <p class="section-tag" style="color: var(--secondary-color);">DATA SCIENCE & ML</p>
            <h2 class="section-title">Predictive Intelligence.</h2>
            <p class="section-subtitle">Extracting signal from noise with classical Machine Learning, Deep Learning, and advanced EDA.</p>
            
            <div class="projects-grid">
                <!-- Kaggle Card -->
                <div class="project-card kaggle-card" style="border-color: #20BEFF;">
                    <div class="project-glow"></div>
                    <span class="project-badge" style="background: rgba(32, 190, 255, 0.2); color: #20BEFF; border: 1px solid rgba(32, 190, 255, 0.4);">KAGGLE CERTIFIED</span>
                    <h3>Advanced Data Science</h3>
                    <p>Proven expertise in exploratory data analysis (EDA), feature engineering, and model tuning via Kaggle competitions and certifications. Proficient with Pandas, NumPy, scikit-learn, and XGBoost.</p>
                    <div class="project-tech">
                        <span style="color: #20BEFF; background: rgba(32,190,255,0.1); border: 1px solid rgba(32,190,255,0.3);">Python</span>
                        <span style="color: #20BEFF; background: rgba(32,190,255,0.1); border: 1px solid rgba(32,190,255,0.3);">Pandas</span>
                        <span style="color: #20BEFF; background: rgba(32,190,255,0.1); border: 1px solid rgba(32,190,255,0.3);">scikit-learn</span>
                        <span style="color: #20BEFF; background: rgba(32,190,255,0.1); border: 1px solid rgba(32,190,255,0.3);">EDA</span>
                    </div>
                    <div class="project-links">
                        <a href="https://www.kaggle.com/" target="_blank">View Kaggle Profile <i class="fas fa-external-link-alt"></i></a>
                    </div>
                </div>

                <!-- ML Project Placeholder -->
                <div class="project-card" style="border-color: var(--accent-color);">
                    <div class="project-glow"></div>
                    <span class="project-badge" style="background: rgba(255, 0, 110, 0.2); color: var(--accent-color); border: 1px solid rgba(255, 0, 110, 0.4);">PREDICTIVE MODELING</span>
                    <h3>Enterprise Risk Predictor (Example)</h3>
                    <p>A supervised machine learning pipeline designed to predict customer churn / risk scoring using ensemble methods (Random Forest, Gradient Boosting). Includes hyperparameter tuning and cross-validation.</p>
                    <div class="project-tech">
                        <span>XGBoost</span><span>Random Forest</span><span>Data Pipeline</span>
                    </div>
                    <div class="project-links">
                        <a href="#" target="_blank">View on GitHub <i class="fab fa-github"></i></a>
                    </div>
                </div>
            </div>
        </div>
    </section>
'''

css_injection = '''
/* =========================================
   ML & DATA SCIENCE PROJECTS
   ========================================= */
#ml-ds-projects {
    padding: 6rem 0;
    position: relative;
    z-index: 2;
}

.kaggle-card h3 {
    color: #20BEFF !important;
}
.kaggle-card .project-links a {
    color: #20BEFF !important;
    border-color: rgba(32, 190, 255, 0.5) !important;
}
.kaggle-card .project-links a:hover {
    background: rgba(32, 190, 255, 0.1) !important;
}
'''

def process_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Hero replacements
    content = content.replace(
        '<p class="hero-tag">&mdash; AI SOFTWARE ENGINEER &mdash;</p>',
        '<p class="hero-tag">&mdash; AI, ML & DATA ENGINEER &mdash;</p>'
    )
    content = content.replace(
        '<p class="hero-subtitle">Multi-Agent Swarms &middot; Production RAG &middot; Enterprise Guardrails</p>',
        '<p class="hero-subtitle">Generative AI &middot; Predictive Machine Learning &middot; Data Science</p>'
    )

    # Nav replacement
    if '<a href="#ml-ds-projects">ML & Data</a>' not in content:
        content = content.replace(
            '<a href="#projects">Projects</a>',
            '<a href="#projects">Projects</a>\n            <a href="#ml-ds-projects">ML & Data</a>'
        )
        
    # Section injection
    if 'id="ml-ds-projects"' not in content:
        # Inject right after deep-dive section
        pattern = r'(</section>\s*)(<!-- Skills Section -->)'
        content = re.sub(pattern, r'\1' + html_injection + r'\2', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def process_css(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'ML & DATA SCIENCE PROJECTS' not in content:
        # Inject right before SKILLS
        pattern = r'(/\* =========================================\s*SKILLS\s*========================================= \*/)'
        content = re.sub(pattern, css_injection + '\n' + r'\1', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def process_app_js(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update system prompt
    content = content.replace(
        '- Core: Python, JavaScript, SQL, Bash\\n- AI/ML: LangChain, LlamaIndex, HuggingFace, OpenAI API, Groq, LLaMA 3',
        '- Core: Python, JavaScript, SQL, Bash\\n- Generative AI: LangChain, LlamaIndex, HuggingFace, OpenAI API, Groq, LLaMA 3\\n- Machine Learning & Data Science: scikit-learn, XGBoost, Pandas, NumPy, Predictive Modeling, Kaggle'
    )
    content = content.replace(
        '- B.Tech student in Computer Science (AI & ML specialization)',
        '- B.Tech student in Computer Science (AI & ML specialization). Highly skilled in Generative AI, Classical Machine Learning, and Data Science.'
    )
    # The actual line in JS has literal backticks and newlines, so we regex it safely.
    # Actually, it's safer to use regex to find and replace the whole TECHNICAL SKILLS block.
    
    # Python regex replacement for system prompt:
    pattern_tech = r'TECHNICAL SKILLS:\n- Core: Python, JavaScript, SQL, Bash\n- AI/ML: LangChain, LlamaIndex, HuggingFace, OpenAI API, Groq, LLaMA 3'
    rep_tech = 'TECHNICAL SKILLS:\\n- Core: Python, JavaScript, SQL, Bash\\n- Generative AI: LangChain, LlamaIndex, HuggingFace, OpenAI API, Groq, LLaMA 3\\n- Machine Learning & Data Science: scikit-learn, XGBoost, Pandas, NumPy, Predictive Modeling, Kaggle'
    content = re.sub(pattern_tech, rep_tech, content, flags=re.MULTILINE)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

dirs = ['docs', 'portfolio_website']
for d in dirs:
    html_path = os.path.join('D:\\Apex_Paragon\\AI-APEX-PARAGON', d, 'index.html')
    css_path = os.path.join('D:\\Apex_Paragon\\AI-APEX-PARAGON', d, 'style.css')
    js_path = os.path.join('D:\\Apex_Paragon\\AI-APEX-PARAGON', d, 'app.js')
    
    if os.path.exists(html_path):
        process_html(html_path)
    if os.path.exists(css_path):
        process_css(css_path)
    if os.path.exists(js_path):
        process_app_js(js_path)

