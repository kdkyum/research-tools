#!/usr/bin/env python3
"""Convert research_notes/*.md to a single HTML file with embedded figures and MathJax.

Usage:
    python build_research_html.py [--notes-dir DIR] [--out PATH]

Defaults:
    --notes-dir  <cwd>/research_notes
    --out        /tmp/<timestamp>_<project>.html
"""
import argparse
import base64
import datetime
import glob
import os
import re
import sys

try:
    import markdown
except ImportError:
    print("Missing 'markdown' package. Install: uv pip install -p .venv markdown")
    sys.exit(1)


def embed_images(html: str, base_dir: str) -> str:
    """Replace <img src="..."> with base64-embedded data URIs."""
    def replace_img(m):
        attrs_before = m.group(1)
        src = m.group(2)
        attrs_after = m.group(3)

        # Resolve relative path — figures live in research_notes/attachements/
        if src.startswith("../"):
            # Legacy path: ../attachements/foo.png (from when attachements was outside)
            img_path = os.path.normpath(os.path.join(base_dir, src))
        elif src.startswith("/"):
            img_path = src
        else:
            # Current path: attachements/foo.png (relative to research_notes/)
            img_path = os.path.normpath(os.path.join(base_dir, src))

        if not os.path.exists(img_path):
            return m.group(0)  # keep original if file not found

        ext = os.path.splitext(img_path)[1].lower()
        mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".svg": "image/svg+xml", ".gif": "image/gif", ".pdf": "application/pdf"}
        mime_type = mime.get(ext, "application/octet-stream")

        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()

        return f'<img {attrs_before}src="data:{mime_type};base64,{data}"{attrs_after}'

    return re.sub(r'<img\s(.*?)src="([^"]+)"(.*?)/?>', replace_img, html, flags=re.DOTALL)


def build_html(notes_dir: str, out_path: str, title: str = "Research Notes"):
    md_files = sorted(glob.glob(os.path.join(notes_dir, "*.md")))
    if not md_files:
        print(f"No .md files found in {notes_dir}")
        sys.exit(1)

    md_ext = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])

    sections = []
    for md_file in md_files:
        with open(md_file) as f:
            text = f.read()
        md_ext.reset()
        html_section = md_ext.convert(text)
        # Embed images relative to the notes dir
        html_section = embed_images(html_section, notes_dir)
        fname = os.path.basename(md_file)
        sections.append(f'<section id="{fname}">\n{html_section}\n</section>')

    toc_items = []
    for md_file in md_files:
        fname = os.path.basename(md_file)
        # Extract first H1
        with open(md_file) as f:
            for line in f:
                if line.startswith("# "):
                    title_text = line[2:].strip()
                    break
            else:
                title_text = fname
        toc_items.append(f'<li><a href="#{fname}">{title_text}</a></li>')

    toc_html = "<ul>\n" + "\n".join(toc_items) + "\n</ul>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<script>
MathJax = {{
  tex: {{ inlineMath: [['$','$'], ['\\\\(','\\\\)']], displayMath: [['$$','$$'], ['\\\\[','\\\\]']] }}
}};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
         max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; }}
  h1 {{ border-bottom: 2px solid #333; padding-bottom: 8px; }}
  h2 {{ border-bottom: 1px solid #ddd; padding-bottom: 4px; margin-top: 2em; }}
  table {{ border-collapse: collapse; margin: 1em 0; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: center; }}
  th {{ background: #f5f5f5; }}
  img {{ max-width: 100%; height: auto; margin: 1em 0; }}
  code {{ background: #f5f5f5; padding: 2px 5px; border-radius: 3px; font-size: 0.9em; }}
  pre {{ background: #f5f5f5; padding: 12px; border-radius: 5px; overflow-x: auto; }}
  section {{ margin-bottom: 4em; page-break-before: auto; }}
  nav {{ background: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 2em; }}
  nav h2 {{ margin-top: 0; }}
  .warning {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; padding: 10px 15px; margin: 1em 0; }}
</style>
</head>
<body>
<nav>
<h2>Table of Contents</h2>
{toc_html}
</nav>
<hr>
{"<hr>".join(sections)}
</body>
</html>"""

    with open(out_path, "w") as f:
        f.write(html)
    print(f"HTML written to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Build research notes HTML")
    parser.add_argument("--notes-dir", default=None,
                        help="Directory containing .md files (default: <cwd>/research_notes)")
    parser.add_argument("--title", default="Research Notes",
                        help="HTML page title (default: Research Notes)")
    parser.add_argument("--out", default=None,
                        help="Output path (default: /tmp/<timestamp>_<project>.html)")
    args = parser.parse_args()

    notes_dir = args.notes_dir or os.path.join(os.getcwd(), "research_notes")

    if args.out:
        out_path = args.out
    else:
        ts = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        project = os.path.basename(os.getcwd())
        out_path = f"/tmp/{ts}_{project}.html"

    build_html(notes_dir, out_path, title=args.title)


if __name__ == "__main__":
    main()
