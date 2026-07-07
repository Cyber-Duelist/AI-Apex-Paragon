import os

mobile_css = '''
/* =========================================
   MOBILE POLISH (ADDED VIA SCRIPT)
   ========================================= */
@media (max-width: 768px) {
    .blueprint-diagram {
        flex-direction: column !important;
        align-items: center !important;
        padding: 10px !important;
    }
    .bp-arrow, .bp-path {
        transform: rotate(90deg) !important;
        margin: 10px 0 !important;
    }
    .vertical-diagram .split-row {
        flex-direction: column !important;
        gap: 10px !important;
    }
    .blueprint-card {
        padding: 15px !important;
    }
}
'''

dirs = ['docs', 'portfolio_website']
for d in dirs:
    css_path = os.path.join('D:\\Apex_Paragon\\AI-APEX-PARAGON', d, 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'a', encoding='utf-8') as f:
            f.write(mobile_css)
