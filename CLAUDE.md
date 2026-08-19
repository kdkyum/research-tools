# CLAUDE.md

This repository contains the `kdkyum-research-tools` Claude Code marketplace
plugin.

## Skills

The plugin has six skills:

- `bro` restates the last response in plain language.
- `read-arxiv-paper` reads arxiv TeX source and writes a project-specific
  summary under `./knowledge/`.
- `recall` reconstructs recent work from Claude Code transcripts, repository
  state, and linked GitHub history.
- `review-papers` reads a paper list and builds a static literature review under
  `./htmls/<review-slug>/`.
- `technical-writing` applies document structure and sentence-level rules to
  technical prose.
- `unslop` removes common generated-writing patterns and adds specific human
  voice.

## Repository layout

```text
.claude-plugin/marketplace.json       # Marketplace metadata and plugin version
plugins/research-tools/
├── README.md
├── THIRD_PARTY_NOTICES.md
└── skills/
    ├── bro/SKILL.md
    ├── read-arxiv-paper/SKILL.md
    ├── recall/SKILL.md
    ├── review-papers/
    │   ├── SKILL.md
    │   ├── assets/
    │   └── reference/
    ├── technical-writing/SKILL.md
    └── unslop/SKILL.md
```

All skills live under `plugins/research-tools/skills/`. The marketplace entry
uses `./plugins/research-tools` as the plugin source.

## Conventions

- Each `SKILL.md` starts with YAML frontmatter containing `name` and
  `description`.
- The description controls automatic skill selection. Skills with
  `disable-model-invocation: true` require direct user invocation.
- Cache arxiv source at `~/.cache/arxiv-papers/knowledge/<arxiv-id>/`.
- Claude Code transcripts live under `~/.claude/projects/<project-slug>/`.
  Match `sessions-index.json` entries by `projectPath` instead of guessing the
  slug when possible.
- Keep the MIT notice for the pstack-derived skills in
  `plugins/research-tools/THIRD_PARTY_NOTICES.md`.
- Update the plugin version in `.claude-plugin/marketplace.json` when publishing
  skill changes.
