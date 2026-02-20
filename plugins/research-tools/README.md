# Research Tools

Claude Code plugin for research workflows: read arxiv papers, generate reports from experiment results, and send them to Telegram.

## Setup

### 1. Telegram bot configuration

Create `~/.telegram_notify.conf` with your bot token and chat ID:

```
T_TOKEN="<your-bot-token>"
CHAT_ID="<your-chat-id>"
```

To get these:
1. Message [@BotFather](https://t.me/BotFather) on Telegram, run `/newbot`, and copy the token.
2. Message your bot, then fetch your chat ID:
   ```bash
   curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates" | python3 -m json.tool | grep '"id"'
   ```

### 2. Python dependencies (per-project)

The `research-report` skill generates matplotlib figures and HTML reports.
Each project needs a venv with the required packages:

```bash
uv venv .venv
uv pip install -p .venv markdown matplotlib
```

Run scripts with `.venv/bin/python`.
The `telegram-send` script uses only stdlib — no extra dependencies needed.

### 3. Project directory conventions

The skills expect this layout (created automatically when used):

```
<project>/
├── research_notes/          # Markdown reports (YYYY-MM-DD-HHMMSS_<title>.md)
├── attachements/            # Figures, generated scripts (.png, .pdf, .py)
└── scripts/
    └── build_research_html.py   # Optional: converts research_notes/*.md to HTML
```

## Skills

### research-report

Auto-triggers on: "write a report", "summarize results", "document the experiment", "create research notes", "analyze these results".

Generates a structured markdown report from any experiment artifacts (JSON, CSV, Jupyter notebooks, figures, logs). Reports are saved to `research_notes/YYYY-MM-DD-HHMMSS_<title>.md` with figures in `attachements/`.

### read-arxiv-paper

Auto-triggers on: arxiv URLs, "read this paper", "summarize this arxiv paper".

Downloads the TeX source of an arxiv paper, reads it fully, and produces a project-contextualized summary at `./knowledge/summary_{tag}.md`. The summary connects the paper's ideas to the current codebase — what techniques apply, what experiments to try, what code would change.

Paper sources are cached at `~/.cache/arxiv-papers/knowledge/{arxiv_id}/` so re-reading is instant.

### telegram-send

Auto-triggers on: "send to Telegram", "notify me", "share on Telegram".

Sends files to your Telegram chat. Two modes:
- **Formatted text** (default): converts markdown to Telegram HTML, splits at 4096-char limit
- **Document** (`--as-document`): sends the raw file as an attachment

## Commands

### /send-telegram

```
/send-telegram <file_path>              # Send as formatted text
/send-telegram <file_path> --as-document  # Send as file attachment
```

If no file is specified, offers to send the most recent file in `research_notes/`.
