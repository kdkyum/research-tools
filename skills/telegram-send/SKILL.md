---
name: telegram-send
description: >
  Send a markdown file or message to the user's Telegram chat. Use this skill
  whenever the user asks to send something to Telegram, notify on Telegram,
  share a report/file via Telegram, or push results to their chat. Also use
  when the user says "send this to Telegram", "notify me", "share on Telegram",
  or "telegram this". Reads bot credentials from ~/.telegram_notify.conf.
---

# Telegram Send

Send markdown files or messages to a Telegram chat using the Bot API.
Credentials are read from `~/.telegram_notify.conf` (containing `T_TOKEN`
and `CHAT_ID`).

## How to send

Use the bundled script at `scripts/send_markdown.py` (relative to this
skill's directory).

### Send a markdown file as formatted text

The script converts markdown to Telegram-compatible HTML and splits long
files into multiple messages automatically (4096 char limit per message).

```bash
python <skill-dir>/scripts/send_markdown.py <file_path>
```

Example:
```bash
python <skill-dir>/scripts/send_markdown.py research_notes/2026-02-20_report.md
```

### Send as a document attachment

If the file is large or formatting fidelity matters, send the raw `.md`
file as a Telegram document:

```bash
python <skill-dir>/scripts/send_markdown.py <file_path> --as-document
```

### Custom config path

```bash
python <skill-dir>/scripts/send_markdown.py <file_path> --config /path/to/config
```

## When to use each mode

- **Formatted text** (default): Short-to-medium reports the user wants to
  read inline in Telegram. Good for quick summaries, experiment results,
  status updates.
- **Document attachment** (`--as-document`): Long reports, files with many
  tables or LaTeX that don't render well in Telegram's HTML subset, or
  when the user wants to keep the file for later.

## What the script handles

- Parses `~/.telegram_notify.conf` for `T_TOKEN` and `CHAT_ID`
- Converts markdown headings, bold, italic, inline code, code blocks,
  links, and LaTeX ($...$) to Telegram HTML
- Splits messages at paragraph boundaries to stay under 4096 chars
- Falls back to plain text if HTML parsing fails on Telegram's side
- No external dependencies — uses only Python stdlib (`urllib`, `json`)

## Limitations

- Telegram HTML supports only `<b>`, `<i>`, `<code>`, `<pre>`, `<a>` —
  complex markdown tables render as plain text
- Images/figures are not sent (image references become `[caption]` text);
  send figures separately if needed
- LaTeX is approximated as inline `<code>` blocks
