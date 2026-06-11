import os

txt_path = r"D:\Apex_Paragon\AI-APEX-PARAGON\resume_ats.txt"
html_path = r"D:\Apex_Paragon\AI-APEX-PARAGON\resume_ats.html"

with open(txt_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Generate raw, unstyled HTML to force ATS parsers to read exactly what they want
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{ font-family: "Times New Roman", Times, serif; font-size: 12pt; line-height: 1.2; margin: 40px; }}
    h1 {{ font-size: 14pt; font-weight: bold; text-align: center; text-transform: uppercase; margin-bottom: 2px; }}
    h2 {{ font-size: 12pt; font-weight: bold; text-transform: uppercase; border-bottom: 1px solid black; padding-bottom: 2px; margin-top: 15px; margin-bottom: 10px; }}
    p {{ margin: 0; padding: 0; }}
    .contact {{ text-align: center; margin-bottom: 15px; }}
</style>
</head>
<body>
"""

lines = text.split("\n")
i = 0
while i < len(lines):
    line = lines[i].strip()
    if line == "ADARSH KUMAR SINGH":
        html_content += f"<h1>{line}</h1><div class='contact'>"
    elif line in ["SUMMARY", "SKILLS", "WORK EXPERIENCE", "EDUCATION", "CERTIFICATIONS"]:
        if "</div>" not in html_content:
            html_content += "</div>"
        html_content += f"<h2>{line}</h2>"
    elif line.startswith("- "):
        html_content += f"<ul><li>{line[2:]}</li></ul>"
    elif line == "":
        pass
    else:
        # Standard text (Company, Job Title, Dates)
        if i > 0 and lines[i-1] in ["WORK EXPERIENCE", "EDUCATION"] or (i > 0 and lines[i-1] == ""):
            html_content += f"<p><strong>{line}</strong></p>"
        else:
            html_content += f"<p>{line}</p>"
    i += 1

html_content += "</body></html>"

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("ATS HTML generated.")
