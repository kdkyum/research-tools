# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code marketplace plugin (`kdkyum-research-tools`) that provides three skills for research workflows:

- **read-arxiv-paper** — Downloads arxiv TeX source, reads the full paper, outputs a project-contextualized summary to `./knowledge/summary_{tag}.md`
- **research-report** — Generates structured markdown reports from experiment artifacts (notebooks, JSON, CSV, figures) into `research_notes/`
- **telegram-send** — Sends files to Telegram via Bot API using only Python stdlib

## Repository Layout

```
.claude-plugin/marketplace.json   # Plugin registry metadata
plugins/research-tools/           # Installed plugin copy (skills + README)
skills/                           # Top-level skill definitions (editable source)
  ├── read-arxiv-paper/SKILL.md
  ├── research-report/SKILL.md
  └── telegram-send/
      ├── SKILL.md
      └── scripts/send_markdown.py
commands/send-telegram.md         # /send-telegram slash command definition
```

**Dual layout**: Skills exist in both `skills/` (top-level, editable) and `plugins/research-tools/skills/` (installed copy). The two may diverge — `plugins/` contains the version-controlled copy referenced by `marketplace.json`, while `skills/` is the working source. When editing skills, update both locations or consolidate.

## Key Conventions

- **SKILL.md frontmatter**: Each skill has YAML frontmatter with `name` and `description` fields. The `description` controls auto-triggering — it lists natural language phrases that activate the skill.
- **No external Python deps for telegram-send**: `send_markdown.py` uses only stdlib (`urllib`, `json`). The research-report skill requires `matplotlib` and `markdown` in a project venv.
- **Telegram config**: Bot credentials at `~/.telegram_notify.conf` with `T_TOKEN` and `CHAT_ID`.
- **Arxiv cache**: Paper sources cached at `~/.cache/arxiv-papers/knowledge/{arxiv_id}/`.
- **Report output paths**: Reports go to `research_notes/YYYY-MM-DD-HHMMSS_<title>.md`, figures to `attachements/` (note: intentional spelling).

## Spelling Note

The directory `attachements/` is intentionally spelled with an extra 'e' throughout the codebase. Do not "fix" this to `attachments/` — it would break existing report links.
