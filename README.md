# Research Tools

Claude Code plugin for research workflows: read arxiv papers and generate reports from experiment results.

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

### Per-skill setup

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

