# Research Tools

Claude Code plugin for research workflows: read arxiv papers, generate reports from experiment results, submit them to a centralized dashboard, and send them to Telegram.

## Installation

In Claude Code, run:

```
/plugin marketplace add kdkyum/research-tools
/plugin install research-tools@kdkyum-research-tools
```

### Per-skill setup

**telegram-send** — Create `~/.telegram_notify.conf`:

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

**submit-report** — Create `~/.dashboard.env`:

```
DASHBOARD_URL="https://<your-dashboard-ip>:3000"
DASHBOARD_API_KEY="<your-api-key>"
```

Ask the dashboard admin for the API key.

**research-report** — Needs matplotlib in a project venv:

```bash
uv venv .venv
uv pip install -p .venv markdown matplotlib
```

## Project directory conventions

The skills expect this layout (created automatically when used):

```
<project>/
├── research_notes/          # Self-contained report folder
│   ├── *.md                 # Markdown reports (YYYY-MM-DD-HHMMSS_<title>.md)
│   └── attachements/        # Figures, generated scripts (.png, .pdf, .py)
└── knowledge/               # Arxiv paper summaries
```

## Skills

### research-report

Auto-triggers on: "write a report", "summarize results", "document the experiment", "create research notes", "analyze these results".

Generates a structured markdown report from any experiment artifacts (JSON, CSV, Jupyter notebooks, figures, logs). Reports are saved to `research_notes/YYYY-MM-DD-HHMMSS_<title>.md` with figures in `research_notes/attachements/`.

### read-arxiv-paper

Auto-triggers on: arxiv URLs, "read this paper", "summarize this arxiv paper".

Downloads the TeX source of an arxiv paper, reads it fully, and produces a project-contextualized summary at `./knowledge/summary_{tag}.md`. The summary connects the paper's ideas to the current codebase — what techniques apply, what experiments to try, what code would change.

Paper sources are cached at `~/.cache/arxiv-papers/knowledge/{arxiv_id}/` so re-reading is instant.

### submit-report

Auto-triggers on: "submit report", "upload to dashboard", "push this report", "resubmit", "sync report to dashboard".

Submits a research report (and associated figures from `research_notes/attachements/`) to the centralized Research Dashboard. Supports:
- Auto-detection of the latest report in `research_notes/`
- Automatic inference of project name and tags from report content
- Versioned updates (`--update`) for re-submitting modified reports
- Environment and git metadata collection

Requires `DASHBOARD_URL` and `DASHBOARD_API_KEY` in `~/.dashboard.env`.

### telegram-send

Auto-triggers on: "send to Telegram", "notify me", "share on Telegram".

Sends files to your Telegram chat. Two modes:
- **Formatted text** (default): converts markdown to Telegram HTML, splits at 4096-char limit
- **Document** (`--as-document`): sends the raw file as an attachment
