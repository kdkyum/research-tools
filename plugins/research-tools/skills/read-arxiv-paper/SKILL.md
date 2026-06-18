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


## Paper Cache

```!
mkdir -p ~/.cache/arxiv-papers/knowledge
ls -la ~/.cache/arxiv-papers/knowledge
```

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

- If the file already exists in cache, skip the download.
- If not in the cache, do download:

Download to `~/.cache/arxiv-papers/knowledge/{arxiv_id}.tar.gz`:

```bash
curl -L -o ~/.cache/arxiv-papers/knowledge/{arxiv_id}.tar.gz https://www.arxiv.org/src/{arxiv_id}
```


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
- Appendix
- Figures

