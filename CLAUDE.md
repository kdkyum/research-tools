# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code marketplace plugin (`kdkyum-research-tools`) that provides four skills for research workflows:

- **read-arxiv-paper** — Downloads arxiv TeX source, reads the full paper, outputs a project-contextualized summary to `./knowledge/summary_{tag}.md`
- **research-report** — Generates structured markdown reports from experiment artifacts (notebooks, JSON, CSV, figures) into `research_notes/`
- **submit-report** — Submits reports from `research_notes/` to the centralized Research Dashboard via curl API, with auto-detection of figures and support for versioned updates
- **telegram-send** — Sends files to Telegram via Bot API using only Python stdlib

## Repository Layout

```
.claude-plugin/marketplace.json       # Plugin registry metadata
plugins/research-tools/               # Plugin source (referenced by marketplace.json)
  ├── README.md
  └── skills/
      ├── read-arxiv-paper/SKILL.md
      ├── research-report/SKILL.md
      ├── submit-report/SKILL.md
      └── telegram-send/
          ├── SKILL.md
          └── scripts/send_markdown.py
```

All skills live under `plugins/research-tools/skills/`. This is the single source of truth — `marketplace.json` points to `./plugins/research-tools`.

## Key Conventions

- **SKILL.md frontmatter**: Each skill has YAML frontmatter with `name` and `description` fields. The `description` controls auto-triggering — it lists natural language phrases that activate the skill.
- **No external Python deps for telegram-send**: `send_markdown.py` uses only stdlib (`urllib`, `json`). The research-report skill requires `matplotlib` and `markdown` in a project venv.
- **Telegram config**: Bot credentials at `~/.telegram_notify.conf` with `T_TOKEN` and `CHAT_ID`.
- **Arxiv cache**: Paper sources cached at `~/.cache/arxiv-papers/knowledge/{arxiv_id}/`.
- **Report output paths**: Reports go to `research_notes/YYYY-MM-DD-HHMMSS_<title>.md`, figures to `research_notes/attachements/` (note: intentional spelling). Everything lives inside `research_notes/` for self-contained backup and dashboard submission.
- **Dashboard config**: The submit-report skill reads `DASHBOARD_URL` and `DASHBOARD_API_KEY` from env vars or `~/.dashboard.env`. No external scripts needed — the skill calls the dashboard REST API directly via curl.

## Spelling Note

The directory `attachements/` is intentionally spelled with an extra 'e' throughout the codebase. Do not "fix" this to `attachments/` — it would break existing report links.
