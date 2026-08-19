# Research tools

Claude Code plugin for reading papers, building literature reviews, recovering
recent work, and editing technical prose.

## Install

Run these commands in Claude Code:

```text
/plugin marketplace add kdkyum/research-tools
/plugin install research-tools@kdkyum-research-tools
```

## Update

```text
/plugin marketplace update kdkyum-research-tools
/plugin update research-tools@kdkyum-research-tools
```

Restart Claude Code after an update.

## Project directories

The paper skills create these directories when needed:

```text
<project>/
├── knowledge/               # Arxiv paper summaries
└── htmls/                   # Literature review websites
    └── <review-slug>/       # index.html, paper pages, CSS, JavaScript, and figures
```

## Skills

### bro

Run `/research-tools:bro` to restate the last response in plain language. It
cuts jargon and shortens the explanation without changing its meaning.

### recall

Run `/research-tools:recall` to rebuild recent context for the active project.
It searches Claude Code sessions under `~/.claude/projects/`, checks the live
repository and GitHub state, and returns a short brief with the current threads,
problems, and next action.

The skill matches `sessions-index.json` entries by their exact `projectPath`.
It searches only the active project unless you name another workspace.

### technical-writing

Run `/research-tools:technical-writing` when writing or reviewing documentation,
RFCs, readmes, pull request descriptions, or commit messages. It combines
Diataxis document structure, Google developer style, Simplified Technical
English, and Global English rules.

### unslop

This skill applies to writing tasks. It removes common generated-writing
patterns, preserves the intended meaning and tone, and asks for concrete claims
and a human voice.

### review-papers

This skill activates for requests such as "review these papers", "make a
literature review", and lists of several arxiv URLs. It assigns one paper to
each subagent, reads TeX source, extracts real figures, creates one page per
paper, and builds a static review website at `./htmls/<review-slug>/`.

### read-arxiv-paper

This skill activates for arxiv URLs and requests to read or summarize a paper.
It downloads the TeX source and writes a project-specific summary to
`./knowledge/summary_<tag>.md`.

Paper sources are cached at
`~/.cache/arxiv-papers/knowledge/<arxiv-id>/`.

## Third-party code

The `bro`, `recall`, and `technical-writing` skills come from Lauren Tan's
[pstack](https://github.com/cursor/plugins/tree/60c641e4fad674784b30abcf9f8915dea39df38d/pstack)
plugin under the MIT License. The `recall` skill was adapted for Claude Code's
transcript layout. See [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md).
