import os
import re

def update_routing(base_dir):
    # 1. Update index.html
    index_path = os.path.join(base_dir, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace ?id= with #
        content = content.replace('article.html?id=building-swarm', 'article.html#building-swarm')
        content = content.replace('article.html?id=production-rag', 'article.html#production-rag')
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)

    # 2. Update article.js
    js_path = os.path.join(base_dir, 'article.js')
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Replace URLSearchParams logic with hash logic
        old_logic = "const urlParams = new URLSearchParams(window.location.search);\n    const articleId = urlParams.get('id');"
        new_logic = "const urlParams = new URLSearchParams(window.location.search);\n    const articleId = window.location.hash ? window.location.hash.substring(1) : urlParams.get('id');"
        
        js_content = js_content.replace(old_logic, new_logic)
        
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(js_content)

dirs = ['docs', 'portfolio_website']
for d in dirs:
    base = os.path.join('D:\\Apex_Paragon\\AI-APEX-PARAGON', d)
    update_routing(base)
