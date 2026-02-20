---
name: read-arxiv-paper
description: >
  Use this skill when asked to read an arxiv paper given an arxiv URL.
  Triggers on arxiv URLs, "read this paper", "summarize this arxiv paper",
  or any request involving an arxiv link. Also use when the user pastes
  an arxiv URL and asks what it's about or how it relates to the project.
---

# Read ArXiv Paper

Read an arxiv paper from its TeX source, understand it, and produce a
project-contextualized summary.

## Workflow

### Part 1: Normalize the URL

Extract the arxiv ID from whatever URL format the user provides and
construct the TeX source URL. The source URL always looks like:

```
https://www.arxiv.org/src/{arxiv_id}
```

Examples:
- `https://arxiv.org/abs/2601.07372` -> `https://www.arxiv.org/src/2601.07372`
- `https://arxiv.org/pdf/2601.07372` -> `https://www.arxiv.org/src/2601.07372`
- `2601.07372` -> `https://www.arxiv.org/src/2601.07372`

Always fetch the **TeX source**, never the PDF.

### Part 2: Download the paper source

Download to `~/.cache/arxiv-papers/knowledge/{arxiv_id}.tar.gz`:

```bash
mkdir -p ~/.cache/arxiv-papers/knowledge
curl -L -o ~/.cache/arxiv-papers/knowledge/{arxiv_id}.tar.gz https://www.arxiv.org/src/{arxiv_id}
```

If the file already exists, skip the download.

### Part 3: Unpack the source

Unpack into `~/.cache/arxiv-papers/knowledge/{arxiv_id}/`:

```bash
mkdir -p ~/.cache/arxiv-papers/knowledge/{arxiv_id}
tar xzf ~/.cache/arxiv-papers/knowledge/{arxiv_id}.tar.gz -C ~/.cache/arxiv-papers/knowledge/{arxiv_id}
```

### Part 4: Locate the entrypoint

Find the main LaTeX file. Common patterns:
1. Look for `main.tex`, `paper.tex`, or `ms.tex`
2. If not found, look for the `.tex` file containing `\documentclass`
3. If multiple candidates, pick the one that contains `\begin{document}`

### Part 5: Read the paper

Read the entrypoint file, then follow `\input{...}` and `\include{...}`
directives to read all referenced source files. Read the full paper
content including:
- Abstract, introduction, methodology
- Key equations, algorithms, theorems
- Experiments and results
- Related work and references

### Part 6: Report

Produce a summary at `./knowledge/summary_{tag}.md` where:
- `./knowledge/` is a **local** directory in the current project (create
  if needed) — not in `~/.cache`
- `{tag}` is a descriptive slug derived from the paper's topic (e.g.
  `conditional_memory`, `tucker_decomposition`, `bilinear_relational`)
- Check that the filename doesn't already exist to avoid overwriting

Before writing the summary, read the relevant parts of the current
project's codebase. The summary should be contextualized — connecting the
paper's ideas to the project at hand.

#### Summary structure

```markdown
# {Paper Title}

**ArXiv**: {arxiv_id}
**Authors**: {author list}
**Date**: {publication date}

## Key Idea

{1-3 sentence distillation of the paper's core contribution.}

## Method

{Concise description of the approach, key equations, architecture.
Include LaTeX notation where it aids clarity.}

## Results

{Main experimental findings. What benchmarks, what improvements.}

## Relevance to This Project

{This is the most important section. Explicitly connect the paper's
ideas to the current codebase:
- What concepts/techniques could be applied here?
- What experiments could we try inspired by this?
- What code would need to change?
Reference specific files and functions in the project.}

## Key References

{Notable references from the paper worth following up on.}
```
