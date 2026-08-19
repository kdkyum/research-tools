# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code marketplace plugin (`kdkyum-research-tools`) that provides three skills for research and writing:

- **read-arxiv-paper** — Downloads arxiv TeX source, reads the full paper, outputs a project-contextualized summary to `./knowledge/summary_{tag}.md`
- **review-papers** — Reads a whole reading list (one subagent per paper, via the read-arxiv-paper procedure) and aggregates them into a categorized long-form literature-review website under `./htmls/<review-slug>/` (one self-contained folder per review: index.html + per-paper pages + shared design system). Ships starter `assets/` (css/js/templates) and a `reference/` orchestration recipe.
- **unslop** — Removes common AI writing patterns and rewrites text with a more specific human voice

## Repository Layout

```
.claude-plugin/marketplace.json       # Plugin registry metadata
plugins/research-tools/               # Plugin source (referenced by marketplace.json)
  ├── README.md
  └── skills/
      ├── read-arxiv-paper/SKILL.md
      ├── review-papers/               # SKILL.md + reference/ (orchestration, design-system) + assets/ (css/js/templates)
      └── unslop/SKILL.md
```

All skills live under `plugins/research-tools/skills/`. This is the single source of truth — `marketplace.json` points to `./plugins/research-tools`.

## Key Conventions

- **SKILL.md frontmatter**: Each skill has YAML frontmatter with `name` and `description` fields. The `description` controls auto-triggering — it lists natural language phrases that activate the skill.
- **Arxiv cache**: Paper sources cached at `~/.cache/arxiv-papers/knowledge/{arxiv_id}/`.
