#!/usr/bin/env python3
"""
TicketIQ Documentation & PDF Generator
Converts all Markdown planning documents in /docs to:
1. High-fidelity HTML documents with Mermaid diagrams, KaTeX math rendering, and typography.
2. A unified Master HTML report with Cover Page and Table of Contents.
3. Publication-quality PDFs generated via Headless Google Chrome.
4. An interactive offline-ready Web Reader portal (docs/index.html).
"""

import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("Please install markdown: pip install markdown pygments")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
HTML_DIR = DOCS_DIR / "html"
PDF_DIR = DOCS_DIR / "pdf"

DOC_FILES = [
    ("architecture.md", "System Architecture & Design", "01_architecture"),
    ("phases.md", "5-Phase Implementation Roadmap", "02_phases"),
    ("workflow.md", "Day-by-Day Workflow & Playbook", "03_workflow"),
    ("learning_map.md", "Syllabus & Learning Map", "04_learning_map"),
    ("risks.md", "Production Risks & Mitigations", "05_risks"),
    ("resume_bullets.md", "Resume Bullets & Interview Defense", "06_resume_bullets"),
    ("interview_knowledge_journal.md", "Living Interview Knowledge Journal", "07_interview_knowledge_journal"),
]

CSS_STYLES = """
:root {
  --primary: #4f46e5;
  --primary-dark: #3730a3;
  --text-main: #0f172a;
  --text-muted: #475569;
  --bg-card: #f8fafc;
  --border-color: #e2e8f0;
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: "JetBrains Mono", "SF Mono", Consolas, "Courier New", monospace;
}

* { box-sizing: border-box; }

body {
  font-family: var(--font-sans);
  font-size: 15px;
  line-height: 1.65;
  color: var(--text-main);
  background: #ffffff;
  margin: 0;
  padding: 40px;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

h1, h2, h3, h4, h5, h6 {
  color: #1e1b4b;
  font-weight: 700;
  line-height: 1.3;
  margin-top: 1.8em;
  margin-bottom: 0.6em;
}

h1 {
  font-size: 2.1rem;
  border-bottom: 2px solid #e0e7ff;
  padding-bottom: 0.3em;
  margin-top: 0.5em;
}

h2 {
  font-size: 1.55rem;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 0.25em;
}

h3 { font-size: 1.25rem; }
h4 { font-size: 1.05rem; }

p { margin: 0.9em 0; }

a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}
a:hover { text-decoration: underline; }

table {
  border-collapse: collapse;
  width: 100%;
  margin: 1.4em 0;
  font-size: 0.93rem;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

th, td {
  border: 1px solid var(--border-color);
  padding: 9px 13px;
  text-align: left;
}

th {
  background-color: #f1f5f9;
  font-weight: 600;
  color: #1e293b;
}

tr:nth-child(even) {
  background-color: #f8fafc;
}

blockquote {
  border-left: 4px solid var(--primary);
  background: #f8fafc;
  padding: 10px 18px;
  margin: 1.2em 0;
  border-radius: 0 8px 8px 0;
  color: #334155;
  font-style: normal;
}

blockquote p { margin: 0.4em 0; }

pre {
  background: #0f172a;
  color: #f8fafc;
  padding: 16px 20px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 0.88rem;
  line-height: 1.5;
  border: 1px solid #1e293b;
}

code {
  font-family: var(--font-mono);
  font-size: 0.87em;
  background: #f1f5f9;
  color: #be123c;
  padding: 2px 6px;
  border-radius: 4px;
}

pre code {
  background: transparent;
  color: inherit;
  padding: 0;
  border-radius: 0;
}

.mermaid {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  margin: 1.5em 0;
  text-align: center;
}

ul, ol {
  padding-left: 26px;
  margin: 0.8em 0;
}

li { margin-bottom: 0.35em; }

hr {
  border: 0;
  height: 1px;
  background: #e2e8f0;
  margin: 2em 0;
}

.badge {
  display: inline-block;
  padding: 3px 8px;
  font-size: 0.78rem;
  font-weight: 600;
  border-radius: 12px;
  background: #e0e7ff;
  color: #3730a3;
  margin-right: 6px;
}

.header-banner {
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
  color: #ffffff;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 30px;
}
.header-banner h1 {
  color: #ffffff;
  border: 0;
  margin: 0 0 10px 0;
  font-size: 2rem;
}
.header-banner p {
  color: #c7d2fe;
  margin: 0;
  font-size: 1.05rem;
}

.cover-page {
  min-height: 85vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 60px 30px;
  page-break-after: always;
}
.cover-title {
  font-size: 3rem;
  font-weight: 800;
  color: #1e1b4b;
  margin-bottom: 12px;
}
.cover-subtitle {
  font-size: 1.4rem;
  color: #4f46e5;
  margin-bottom: 24px;
  max-width: 650px;
}
.cover-meta {
  font-size: 1rem;
  color: #64748b;
  margin-top: 40px;
  line-height: 1.8;
}

@page {
  size: A4;
  margin: 16mm 18mm 16mm 18mm;
}

@media print {
  body {
    max-width: 100%;
    padding: 0;
    font-size: 10pt;
    line-height: 1.45;
  }
  h1 { font-size: 1.7rem; margin-top: 1.2em; }
  h2 { font-size: 1.3rem; margin-top: 1.1em; }
  h3 { font-size: 1.1rem; }
  h1, h2, h3 { page-break-after: avoid; }
  table, pre, blockquote, .mermaid { page-break-inside: avoid; }
  .no-print { display: none !important; }
  .page-break { page-break-before: always; }
}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — TicketIQ</title>
  
  <!-- KaTeX for math rendering -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
  
  <!-- Mermaid for diagrams -->
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>
    mermaid.initialize({{
      startOnLoad: true,
      theme: 'neutral',
      securityLevel: 'loose',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }});
  </script>

  <style>
{css}
  </style>
</head>
<body>
  {content}

  <script>
    document.addEventListener("DOMContentLoaded", function() {{
      if (typeof renderMathInElement !== 'undefined') {{
        renderMathInElement(document.body, {{
          delimiters: [
            {{left: '$$', right: '$$', display: true}},
            {{left: '\\\\[', right: '\\\\]', display: true}},
            {{left: '\\\\(', right: '\\\\)', display: false}},
            {{left: '$', right: '$', display: false}}
          ],
          throwOnError: false
        }});
      }}
    }});
  </script>
</body>
</html>
"""

def extract_and_protect_mermaid(md_text):
    """Replaces ```mermaid with <div class="mermaid"> to prevent markdown escaping."""
    pattern = r"```mermaid\n(.*?)```"
    def replacer(match):
        graph_code = match.group(1).strip()
        # Escape any special html tags in graph labels
        return f'<div class="mermaid">\n{graph_code}\n</div>'
    return re.sub(pattern, replacer, md_text, flags=re.DOTALL)

def convert_md_to_html_body(md_path):
    text = md_path.read_text(encoding="utf-8")
    
    # Transform file:// links to standard relative links
    text = re.sub(r'\[([^\]]+)\]\(file://[^\)]+\)', r'<strong>\1</strong>', text)
    
    # Protect mermaid blocks before running markdown parser
    text_with_mermaid = extract_and_protect_mermaid(text)
    
    md = markdown.Markdown(extensions=[
        'tables',
        'fenced_code',
        'nl2br',
        'sane_lists'
    ])
    html_content = md.convert(text_with_mermaid)
    return html_content

def build_individual_html_files():
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    generated = []
    
    for filename, title, prefix in DOC_FILES:
        md_file = DOCS_DIR / filename
        if not md_file.exists():
            print(f"Skipping {filename}: file not found")
            continue
            
        body = convert_md_to_html_body(md_file)
        full_html = HTML_TEMPLATE.format(title=title, css=CSS_STYLES, content=body)
        
        out_path = HTML_DIR / f"{prefix}.html"
        out_path.write_text(full_html, encoding="utf-8")
        generated.append((prefix, title, out_path))
        print(f"✓ Generated HTML: {out_path.name}")
        
    return generated

def build_master_html():
    """Combines all 6 planning documents into a single master document with cover page."""
    sections_html = []
    
    # Cover Page
    cover = """
    <div class="cover-page">
      <div style="font-size: 1.1rem; letter-spacing: 2px; font-weight: 700; color: #6366f1; text-transform: uppercase; margin-bottom: 12px;">Engineering Design & Execution Blueprint</div>
      <div class="cover-title">TicketIQ</div>
      <div class="cover-subtitle">AI-Powered IT Helpdesk Triage & Grounded RAG Resolution Assistant</div>
      <div style="width: 80px; height: 4px; background: #4f46e5; border-radius: 2px; margin: 20px auto;"></div>
      <div class="cover-meta">
        <strong>Author:</strong> Aditya Pandey<br>
        <strong>Program:</strong> B.Tech in Mathematics & Computing (3rd Year)<br>
        <strong>Focus Areas:</strong> Applied Machine Learning, FastAPI Microservices, pgvector, LangChain RAG, Flutter Web<br>
        <strong>Date:</strong> November 2026<br>
        <strong>Deployment Target:</strong> Supabase (PostgreSQL + pgvector) & Render
      </div>
    </div>
    """
    sections_html.append(cover)
    
    # Table of Contents
    toc = """
    <div class="page-break"></div>
    <div style="margin: 40px 0;">
      <h1 style="border-bottom: 2px solid #4f46e5; padding-bottom: 8px;">Table of Contents</h1>
      <table style="margin-top: 24px;">
        <thead>
          <tr>
            <th style="width: 15%;">Section</th>
            <th style="width: 60%;">Document Title</th>
            <th style="width: 25%;">Focus Area</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>01</strong></td>
            <td><a href="#section-1">System Architecture & Design Specification</a></td>
            <td>Architecture, DB Schema, Contracts</td>
          </tr>
          <tr>
            <td><strong>02</strong></td>
            <td><a href="#section-2">5-Phase Implementation Roadmap</a></td>
            <td>Milestones, Deliverables, MVP Scope</td>
          </tr>
          <tr>
            <td><strong>03</strong></td>
            <td><a href="#section-3">Day-by-Day Workflow & Engineering Playbook</a></td>
            <td>28-Day Plan, Git Strategy, DoD Checklists</td>
          </tr>
          <tr>
            <td><strong>04</strong></td>
            <td><a href="#section-4">Syllabus & Learning Map</a></td>
            <td>ML Foundations, LangChain, Small Extras</td>
          </tr>
          <tr>
            <td><strong>05</strong></td>
            <td><a href="#section-5">Production Risks & Mitigation Strategies</a></td>
            <td>Imbalance, Hallucination, Rate Limits</td>
          </tr>
          <tr>
            <td><strong>06</strong></td>
            <td><a href="#section-6">Resume Bullets & Interview Defense Guide</a></td>
            <td>Google XYZ Bullets & High-Yield Q&A</td>
          </tr>
          <tr>
            <td><strong>07</strong></td>
            <td><a href="#section-7">Living Interview Knowledge Journal</a></td>
            <td>Placement Cheat-Sheet, Math & Decisions</td>
          </tr>
        </tbody>
      </table>
    </div>
    """
    sections_html.append(toc)
    
    # Append each section
    for idx, (filename, title, _) in enumerate(DOC_FILES, start=1):
        md_file = DOCS_DIR / filename
        if not md_file.exists():
            continue
        body = convert_md_to_html_body(md_file)
        section_wrapper = f"""
        <div class="page-break" id="section-{idx}"></div>
        <div style="margin-top: 20px;">
          <div style="font-size: 0.9rem; font-weight: 700; color: #6366f1; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 4px;">Section {idx:02d}</div>
          {body}
        </div>
        """
        sections_html.append(section_wrapper)
        
    master_body = "\n".join(sections_html)
    master_html = HTML_TEMPLATE.format(
        title="TicketIQ Complete Engineering Guide",
        css=CSS_STYLES,
        content=master_body
    )
    
    master_out = HTML_DIR / "TicketIQ_Complete_Guide.html"
    master_out.write_text(master_html, encoding="utf-8")
    print(f"✓ Generated Master HTML: {master_out.name}")
    return master_out

def build_interactive_web_reader():
    """Creates a responsive, offline-ready web reader portal at docs/index.html."""
    
    sections_data = []
    for filename, title, prefix in DOC_FILES:
        md_file = DOCS_DIR / filename
        if md_file.exists():
            body = convert_md_to_html_body(md_file)
            sections_data.append({
                "id": prefix,
                "title": title,
                "filename": filename,
                "html": body
            })

    reader_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TicketIQ — Interactive Documentation Reader</title>
  
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
  
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>
    mermaid.initialize({ startOnLoad: false, theme: 'neutral' });
  </script>

  <style>
    :root {
      --primary: #4f46e5;
      --primary-hover: #4338ca;
      --sidebar-bg: #0f172a;
      --sidebar-text: #94a3b8;
      --sidebar-text-active: #ffffff;
      --main-bg: #f8fafc;
      --content-bg: #ffffff;
      --text-main: #0f172a;
      --border-color: #e2e8f0;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: "JetBrains Mono", monospace;
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--font-sans);
      background: var(--main-bg);
      color: var(--text-main);
      display: flex;
      height: 100vh;
      overflow: hidden;
    }

    /* Sidebar */
    #sidebar {
      width: 320px;
      background: var(--sidebar-bg);
      color: var(--sidebar-text);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      border-right: 1px solid #1e293b;
    }
    .sidebar-header {
      padding: 24px 20px;
      border-bottom: 1px solid #1e293b;
    }
    .brand-title {
      font-size: 1.4rem;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .brand-badge {
      font-size: 0.7rem;
      background: #4f46e5;
      color: #fff;
      padding: 2px 7px;
      border-radius: 10px;
    }
    .brand-desc {
      font-size: 0.82rem;
      color: #64748b;
      margin-top: 6px;
    }

    .nav-list {
      list-style: none;
      padding: 16px 12px;
      overflow-y: auto;
      flex: 1;
    }
    .nav-item {
      padding: 12px 14px;
      margin-bottom: 6px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 0.92rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      transition: all 0.15s ease;
      color: #cbd5e1;
    }
    .nav-item:hover {
      background: #1e293b;
      color: #ffffff;
    }
    .nav-item.active {
      background: var(--primary);
      color: #ffffff;
      font-weight: 600;
    }
    .nav-item-num {
      font-size: 0.78rem;
      opacity: 0.6;
      margin-right: 8px;
    }

    .sidebar-footer {
      padding: 16px 20px;
      border-top: 1px solid #1e293b;
      font-size: 0.8rem;
      color: #64748b;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .pdf-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: #312e81;
      color: #e0e7ff;
      padding: 9px 12px;
      border-radius: 6px;
      text-decoration: none;
      font-weight: 600;
      font-size: 0.82rem;
      transition: background 0.15s ease;
    }
    .pdf-btn:hover {
      background: #4338ca;
      color: #fff;
      text-decoration: none;
    }

    /* Main Container */
    #main {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .topbar {
      height: 60px;
      background: #ffffff;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 32px;
      flex-shrink: 0;
    }
    .topbar-title {
      font-weight: 700;
      font-size: 1.1rem;
      color: #1e1b4b;
    }
    .topbar-actions {
      display: flex;
      gap: 12px;
    }
    .action-btn {
      background: #f1f5f9;
      color: #334155;
      border: 1px solid #e2e8f0;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }
    .action-btn:hover {
      background: #e2e8f0;
      color: #0f172a;
    }
    .action-btn.primary {
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }
    .action-btn.primary:hover {
      background: var(--primary-hover);
    }

    .content-area {
      flex: 1;
      overflow-y: auto;
      padding: 40px 48px;
      background: var(--main-bg);
      display: flex;
      justify-content: center;
    }
    .content-card {
      background: #ffffff;
      padding: 48px 56px;
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -2px rgba(0,0,0,0.05);
      width: 100%;
      max-width: 900px;
      line-height: 1.68;
    }

    /* Content styling */
    .content-card h1 { font-size: 2.1rem; color: #1e1b4b; border-bottom: 2px solid #e0e7ff; padding-bottom: 8px; margin-bottom: 20px; }
    .content-card h2 { font-size: 1.5rem; color: #1e293b; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; margin: 32px 0 14px 0; }
    .content-card h3 { font-size: 1.25rem; color: #334155; margin: 24px 0 10px 0; }
    .content-card p { margin: 12px 0; color: #334155; }
    .content-card table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.92rem; }
    .content-card th, .content-card td { border: 1px solid #e2e8f0; padding: 10px 14px; text-align: left; }
    .content-card th { background: #f8fafc; font-weight: 600; color: #0f172a; }
    .content-card tr:nth-child(even) { background: #f8fafc; }
    .content-card blockquote { border-left: 4px solid var(--primary); background: #f8fafc; padding: 12px 18px; margin: 16px 0; border-radius: 0 6px 6px 0; color: #334155; }
    .content-card pre { background: #0f172a; color: #f8fafc; padding: 18px; border-radius: 8px; overflow-x: auto; font-size: 0.88rem; line-height: 1.5; margin: 18px 0; }
    .content-card code { font-family: var(--font-mono); background: #f1f5f9; color: #e11d48; padding: 2px 6px; border-radius: 4px; font-size: 0.88em; }
    .content-card pre code { background: transparent; color: inherit; padding: 0; }
    .content-card ul, .content-card ol { padding-left: 28px; margin: 14px 0; color: #334155; }
    .content-card li { margin-bottom: 6px; }
    .content-card .mermaid { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 24px 0; text-align: center; }

    @media (max-width: 900px) {
      #sidebar { width: 240px; }
      .content-card { padding: 24px; }
    }
  </style>
</head>
<body>

  <div id="sidebar">
    <div class="sidebar-header">
      <div class="brand-title">TicketIQ <span class="brand-badge">DOCS</span></div>
      <div class="brand-desc">AI IT-Helpdesk Assistant Blueprint</div>
    </div>
    
    <ul class="nav-list" id="navList">
      <!-- Injected dynamically -->
    </ul>

    <div class="sidebar-footer">
      <div>📄 <strong>Master PDF</strong></div>
      <a class="pdf-btn" href="pdf/TicketIQ_Complete_Guide.pdf" target="_blank">
        <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
          <path d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"/>
          <path d="M4.603 14.087a.81.81 0 0 1-.438-.42c-.195-.388-.13-.776.08-1.127.184-.306.49-.556.883-.755.393-.198.887-.34 1.455-.42.23-.033.473-.053.722-.06.27-.008.537-.006.8-.002.263.004.516.015.753.033.238.019.45.044.636.075.186.031.34.068.463.11.123.043.21.092.261.148.05.056.07.12.06.192a.63.63 0 0 1-.212.443.98.98 0 0 1-.482.23 2.6 2.6 0 0 1-.722.062 6.5 6.5 0 0 1-.925-.067 11 11 0 0 1-1.077-.183 14 14 0 0 1-1.168-.328 6 6 0 0 1-.776-.328c-.126-.067-.227-.14-.305-.221z"/>
        </svg>
        Download Complete PDF
      </a>
      <div style="font-size: 0.75rem; color: #475569; margin-top: 4px;">Aditya Pandey · B.Tech MnC</div>
    </div>
  </div>

  <div id="main">
    <div class="topbar">
      <div class="topbar-title" id="currentDocTitle">System Architecture & Design</div>
      <div class="topbar-actions">
        <a class="action-btn" id="openIndividualPdfBtn" href="#" target="_blank">
          <span>📄 Open PDF</span>
        </a>
        <button class="action-btn primary" onclick="window.print()">
          <span>🖨️ Print / Save PDF</span>
        </button>
      </div>
    </div>

    <div class="content-area">
      <div class="content-card" id="contentCard">
        <!-- Injected dynamically -->
      </div>
    </div>
  </div>

  <script>
    const sections = {SECTIONS_JSON};

    let activeId = sections[0].id;

    function renderSidebar() {
      const navList = document.getElementById("navList");
      navList.innerHTML = "";
      sections.forEach((sec, idx) => {
        const li = document.createElement("li");
        li.className = "nav-item " + (sec.id === activeId ? "active" : "");
        li.innerHTML = `
          <span><span class="nav-item-num">${String(idx + 1).padStart(2, '0')}</span>${sec.title}</span>
        `;
        li.onclick = () => switchSection(sec.id);
        navList.appendChild(li);
      });
    }

    function switchSection(id) {
      activeId = id;
      renderSidebar();
      const sec = sections.find(s => s.id === id);
      if (!sec) return;

      document.getElementById("currentDocTitle").textContent = sec.title;
      document.getElementById("openIndividualPdfBtn").href = "pdf/" + sec.id + ".pdf";

      const card = document.getElementById("contentCard");
      card.innerHTML = sec.html;

      // Render math
      if (typeof renderMathInElement !== 'undefined') {
        renderMathInElement(card, {
          delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '\\\\[', right: '\\\\]', display: true},
            {left: '\\\\(', right: '\\\\)', display: false},
            {left: '$', right: '$', display: false}
          ],
          throwOnError: false
        });
      }

      // Render mermaid
      if (typeof mermaid !== 'undefined') {
        mermaid.run({
          nodes: card.querySelectorAll('.mermaid')
        });
      }

      // Scroll top
      document.querySelector(".content-area").scrollTop = 0;
    }

    // Initialize
    window.addEventListener("DOMContentLoaded", () => {
      renderSidebar();
      switchSection(activeId);
    });
  </script>
</body>
</html>
"""

    import json
    reader_html = reader_template.replace("{SECTIONS_JSON}", json.dumps(sections_data))
    
    reader_out = DOCS_DIR / "index.html"
    reader_out.write_text(reader_html, encoding="utf-8")
    print(f"✓ Generated Interactive Web Reader: {reader_out.name}")
    return reader_out

def compile_pdf_with_chrome(html_path, pdf_path):
    """Executes Chrome Headless to compile an HTML file to PDF with math and diagrams."""
    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not os.path.exists(chrome_bin):
        print(f"Chrome binary not found at {chrome_bin}")
        return False
        
    cmd = [
        chrome_bin,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=6000",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        str(html_path.resolve())
    ]
    
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            print(f"✓ Generated PDF: {pdf_path.name} ({pdf_path.stat().st_size // 1024} KB)")
            return True
        else:
            print(f"Failed to generate PDF for {html_path.name}: {res.stderr.decode('utf-8')[:300]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"Timeout compiling PDF for {html_path.name}")
        return False

def compile_all_pdfs(individual_htmls, master_html):
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Compile Master PDF
    master_pdf = PDF_DIR / "TicketIQ_Complete_Guide.pdf"
    print("\n--- Compiling Master PDF ---")
    compile_pdf_with_chrome(master_html, master_pdf)
    
    # 2. Compile Individual PDFs
    print("\n--- Compiling Individual PDFs ---")
    for prefix, title, html_path in individual_htmls:
        pdf_path = PDF_DIR / f"{prefix}.pdf"
        compile_pdf_with_chrome(html_path, pdf_path)

def main():
    print("=" * 60)
    print("TicketIQ: Documentation & PDF Build System")
    print("=" * 60)
    
    # Step 1: Individual HTMLs
    individual_htmls = build_individual_html_files()
    
    # Step 2: Master HTML
    master_html = build_master_html()
    
    # Step 3: Interactive Web Reader Portal
    build_interactive_web_reader()
    
    # Step 4: Compile PDFs via Headless Chrome
    compile_all_pdfs(individual_htmls, master_html)
    
    print("\n" + "=" * 60)
    print("BUILD COMPLETE! Artifacts available in:")
    print(f"  • Interactive Web Reader: {DOCS_DIR / 'index.html'}")
    print(f"  • PDFs Directory:        {PDF_DIR}")
    print(f"  • HTML Directory:       {HTML_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
