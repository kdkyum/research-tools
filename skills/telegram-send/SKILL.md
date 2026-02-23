---
name: telegram-send
description: >
  Send a file to the user's Telegram chat. Use this skill
  whenever the user asks to send something to Telegram, notify on Telegram,
  share a report/file via Telegram, or push results to their chat. Also use
  when the user says "send this to Telegram", "notify me", "share on Telegram",
  or "telegram this". Reads bot credentials from ~/.telegram_notify.conf.
---

# Telegram Send

Send files to a Telegram chat using the Bot API.
Credentials are read from `~/.telegram_notify.conf` (containing `T_TOKEN`
and `CHAT_ID`).

## How to send

Use the bundled scripts in `scripts/` (relative to this skill's directory).

### Sending research reports (recommended workflow)

When the file is a markdown report from `research_notes/`, first build a
self-contained HTML version with embedded figures and MathJax, then send
that HTML as a document. This preserves tables, figures, and LaTeX
rendering.

```bash
# 1. Build HTML from research_notes/*.md
.venv/bin/python <skill-dir>/scripts/build_research_html.py \
    --notes-dir research_notes \
    --title "My Experiment" \
    --out /tmp/report.html

# 2. Send the HTML as a document
python <skill-dir>/scripts/send_markdown.py /tmp/report.html
```

The `build_research_html.py` script requires the `markdown` package
(install with `uv pip install -p .venv markdown`). It:
- Converts all `*.md` files in `--notes-dir` into a single HTML page
- Embeds images as base64 data URIs (self-contained, no broken links)
- Adds MathJax for LaTeX rendering
- Generates a table of contents

### Sending any file as a document

```bash
python <skill-dir>/scripts/send_markdown.py <file_path>
```

This sends the file as-is as a Telegram document attachment. Works with
any file type (HTML, PDF, PNG, CSV, JSON, markdown, etc.).

### Sending markdown as formatted text

```bash
python <skill-dir>/scripts/send_markdown.py <file_path> --no-document
```

Converts markdown to Telegram-compatible HTML and sends inline. Splits
long files into multiple messages at the 4096-char limit. Use this for
short messages or status updates — for reports with figures, prefer the
HTML workflow above.

### Custom config path

```bash
python <skill-dir>/scripts/send_markdown.py <file_path> --config /path/to/config
```

## When to use each mode

- **HTML document** (recommended for reports): Build HTML first, send as
  document. Preserves tables, figures, LaTeX. The recipient opens it in a
  browser and sees everything rendered.
- **Raw document**: Send any file as-is when the recipient needs the
  original format (PDF, CSV, notebook, etc.).
- **Formatted text** (`--no-document`): Short messages, quick summaries,
  status updates that read well inline in Telegram.

## What the scripts handle

`send_markdown.py`:
- Parses `~/.telegram_notify.conf` for `T_TOKEN` and `CHAT_ID`
- Sends files as Telegram document attachments (default)
- Optionally converts markdown to Telegram HTML for inline messages
- Splits messages at paragraph boundaries to stay under 4096 chars
- Falls back to plain text if HTML parsing fails on Telegram's side
- No external dependencies — uses only Python stdlib (`urllib`, `json`)

`build_research_html.py`:
- Converts `research_notes/*.md` to a single self-contained HTML file
- Embeds all referenced images as base64 data URIs
- Adds MathJax for `$...$` and `$$...$$` LaTeX rendering
- Generates a table of contents from H1 headings
- Requires `markdown` package (`uv pip install -p .venv markdown`)
