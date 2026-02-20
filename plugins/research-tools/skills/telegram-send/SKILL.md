---
name: telegram-send
description: >
  Send a file to the user's Telegram chat as a document. Use this skill
  whenever the user asks to send something to Telegram, notify on Telegram,
  share a report/file via Telegram, or push results to their chat. Also use
  when the user says "send this to Telegram", "notify me", "share on Telegram",
  or "telegram this". Reads bot credentials from ~/.telegram_notify.conf.
---

# Telegram Send

Send files to a Telegram chat as document attachments using the Bot API.
Credentials are read from `~/.telegram_notify.conf` (containing `T_TOKEN`
and `CHAT_ID`).

## How to send

Use the bundled script at `scripts/send_markdown.py` (relative to this
skill's directory).

```bash
python <skill-dir>/scripts/send_markdown.py <file_path>
```

Example:
```bash
python <skill-dir>/scripts/send_markdown.py research_notes/index.html
```

### Custom config path

```bash
python <skill-dir>/scripts/send_markdown.py <file_path> --config /path/to/config
```

## Workflow

When sending experiment results or reports to Telegram:

1. First build the HTML report using the project's build script
   (e.g. `.venv/bin/python scripts/build_research_html.py`)
2. Then send the generated HTML file — it renders nicely in any browser
   and is self-contained with embedded figures

Always send the **HTML version**, not raw markdown. HTML files preserve
tables, figures, and formatting that Telegram's inline rendering would lose.

## What the script handles

- Parses `~/.telegram_notify.conf` for `T_TOKEN` and `CHAT_ID`
- Sends any file type as a Telegram document attachment (HTML, PDF, PNG,
  CSV, JSON, etc.)
- Auto-detects MIME type from file extension
- No external dependencies — uses only Python stdlib (`urllib`, `json`)
