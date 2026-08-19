# Research Tools

Claude Code plugin for research and writing: read arxiv papers, turn a reading list into a literature-review website, and remove AI writing tells.

## Installation

In Claude Code, run:

```
/plugin marketplace add kdkyum/research-tools
/plugin install research-tools@kdkyum-research-tools
```

### Updating

```
/plugin marketplace update kdkyum-research-tools
```

## Project directory conventions

The skills expect this layout (created automatically when used):

```
<project>/
├── knowledge/               # Arxiv paper summaries (read-arxiv-paper)
└── htmls/                   # Literature-review sites (review-papers), one folder per review:
    └── <review-slug>/       #   index.html, {arxiv_id}.html pages, assets/ (css/js + figures)
```

## Skills

### unslop

Always applies to writing tasks. It removes common AI patterns, preserves the intended meaning and tone, and rewrites text with a more specific human voice.

### review-papers

Auto-triggers on: a list of several arxiv URLs/IDs given together, "review these papers", "write a review/survey blog post about <topic>", "read all these papers and synthesize them", "make a literature review", "compare these papers".

Reads a whole reading list — one subagent per paper, each using the read-arxiv-paper procedure (TeX source + real figures) — builds a standalone HTML deep-dive page per paper, and aggregates them into a single categorized long-form review at `<out>/index.html` (default `./htmls/<review-slug>/`, one self-contained folder per review). Output is pure static HTML: KaTeX equations, real extracted figures, citations + links, an optional related-work section, and one shared design system across every page. Bundles a starter design system (`assets/`) and an orchestration recipe (`reference/`) that you re-theme per topic.

### read-arxiv-paper

Auto-triggers on: arxiv URLs, "read this paper", "summarize this arxiv paper".

Downloads the TeX source of an arxiv paper, reads it fully, and produces a project-contextualized summary at `./knowledge/summary_{tag}.md`. The summary connects the paper's ideas to the current codebase — what techniques apply, what experiments to try, what code would change.

Paper sources are cached at `~/.cache/arxiv-papers/knowledge/{arxiv_id}/` so re-reading is instant.

