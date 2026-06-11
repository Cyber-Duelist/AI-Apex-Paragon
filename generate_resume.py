import markdown
import os

md_path = r"C:\Users\adars\.gemini\antigravity\brain\c4b852cf-2429-4cfa-91b5-e9a76c341d65\resume_optimized.md"
html_path = r"D:\Apex_Paragon\AI-APEX-PARAGON\resume.html"

with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Convert markdown to html with basic styling for ATS parsers
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{ font-family: Arial, sans-serif; font-size: 11pt; line-height: 1.5; margin: 40px; }}
    h1 {{ font-size: 16pt; font-weight: bold; text-align: center; text-transform: uppercase; margin-bottom: 5px; }}
    h2 {{ font-size: 13pt; font-weight: bold; text-transform: uppercase; border-bottom: 1px solid black; padding-bottom: 2px; margin-top: 15px; margin-bottom: 10px; }}
    p {{ margin-top: 0; margin-bottom: 8px; }}
    ul {{ margin-top: 0; margin-bottom: 10px; padding-left: 20px; }}
    li {{ margin-bottom: 4px; }}
</style>
</head>
<body>
{markdown.markdown(text)}
</body>
</html>
"""

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML generated.")
