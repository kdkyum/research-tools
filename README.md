# Research Tools

Claude Code plugin for research and writing: read arxiv papers and remove AI writing tells.

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
└── knowledge/               # Arxiv paper summaries
```

## Skills

### unslop

Always applies to writing tasks. It removes common AI patterns, preserves the intended meaning and tone, and rewrites text with a more specific human voice.

### read-arxiv-paper

Auto-triggers on: arxiv URLs, "read this paper", "summarize this arxiv paper".

Downloads the TeX source of an arxiv paper, reads it fully, and produces a project-contextualized summary at `./knowledge/summary_{tag}.md`. The summary connects the paper's ideas to the current codebase — what techniques apply, what experiments to try, what code would change.

Paper sources are cached at `~/.cache/arxiv-papers/knowledge/{arxiv_id}/` so re-reading is instant.

