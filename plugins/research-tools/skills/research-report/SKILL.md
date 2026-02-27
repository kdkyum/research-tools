---
name: research-report
description: >
  Generate a structured research report from completed experiment results.
  Use this skill whenever the user wants to create a report, write up findings,
  summarize experiments, document results, or generate research notes — even
  if they don't say "report" explicitly. Triggers on: "write a report",
  "summarize results", "document the experiment", "create research notes",
  "write up findings", "what did we find", "analyze these results". Works
  with any result format: JSON, CSV, Jupyter notebooks (.ipynb), figures,
  log files, or mixed artifacts. The primary workflow is notebook-centric:
  the user runs an experiment in a Jupyter notebook, and this skill extracts
  findings, figures, and tables into a standalone markdown report.
---

# Research Report Generator

Generate a structured markdown research report from completed experiment
results. Reports go in `research_notes/`, figures and generated files go
in `research_notes/attachements/`. This keeps everything self-contained in
one folder for easy backup and submission to the dashboard.

## Arguments

The skill accepts these positional arguments:

- `$0` (required): The notebook name (without `.ipynb` extension), e.g.
  `experiment_01`. The notebook is expected at `notebooks/$0.ipynb`.
- `$1` (optional): A custom report title. If omitted, derive the title
  from the notebook's first H1 heading.

If the source is not a notebook (e.g. a directory of JSON results, a CSV),
the user will specify the path directly — adapt accordingly.

## Workflow

### 1. Read the source material

**For notebooks** (`notebooks/$0.ipynb`):
- Read all cells — markdown cells provide motivation and method context,
  code cells show what was run, output cells contain metrics and figures
- Identify the notebook's H1 heading for the report title
- Catalog all figures already saved to `research_notes/attachements/$0_*`
- Extract any printed metric tables from cell outputs

**For other result formats**:
- JSON: parse and extract metrics, hyperparameters, configuration fields
- CSV: load and identify columns, independent/dependent variables
- Existing figures: catalog `.png`, `.pdf`, `.svg` files
- Log files: extract final metrics, training curves, errors

Build a mental inventory: what experiments were run, what varied between
them, and what was measured.

### 2. Identify the experimental structure

Group results by experimental dimensions. Common patterns:
- **Ablation study**: one variable changes, everything else fixed
- **Comparison**: different methods/baselines on the same task
- **Scaling study**: performance as a function of size/compute
- **Grid search**: multiple variables crossed

If the grouping is ambiguous, ask the user. If filenames or notebook
structure make it clear, infer automatically.

### 3. Generate figures

If the notebook already produced figures saved to `research_notes/attachements/$0_*`,
use those directly — don't regenerate unless the user asks.

When new figures are needed, create matplotlib visualizations:

- **Bar charts**: comparing discrete configurations
- **Line plots**: trends over a continuous variable
- **Grouped bars**: multi-metric comparisons
- **Scatter plots**: correlations between metrics
- **Heatmaps**: two-dimensional parameter sweeps

Figure conventions:
- Clean style (`plt.style.use('seaborn-v0_8-whitegrid')` or similar)
- Clear axis labels with units
- Legends when comparing multiple series
- Consistent colors across related figures
- Figure size typically 8x5 or 10x6 inches
- Save as PNG (markdown preview) and PDF (publication quality)
- Naming: `research_notes/attachements/$0_NN_description.png` where `NN`
  is a zero-padded sequence number
- Write a reproducible script at `research_notes/attachements/generate_figures_$0.py`
  when generating new figures

### 4. Write the report

Create the report at:
```
research_notes/YYYY-MM-DD-HHMMSS_<title>.md
```

where `YYYY-MM-DD-HHMMSS` is the current timestamp (use
`date '+%Y-%m-%d-%H%M%S'`) and `<title>` is derived from the notebook's
H1 heading (lowercased, spaces to underscores, strip special characters).
If the user provided `$1`, use that as the title instead.

Ensure `research_notes/` and `research_notes/attachements/` exist (create if needed).

### Report template

```markdown
# <Experiment Title>

**Date**: YYYY-MM-DD-HHMMSS
**Notebook**: `notebooks/$0.ipynb`
**Models**: <model descriptions from notebook context>

## Motivation

<Why this experiment was run. Summarize from the notebook's introductory
markdown cells. 2-5 sentences.>

## Method

<Concise description of the experimental procedure. Reference specific
techniques, hyperparameters, and evaluation protocol. 2-5 sentences
unless complexity warrants more.>

## Results

### <Result Section Title>

<Description of what was measured.>

| Config | Metric 1 | Metric 2 | ... |
|--------|----------|----------|-----|
| ...    | ...      | ...      | ... |

![Figure description](attachements/$0_NN_description.png)

<Interpretation of the result.>

### <Next Result Section>

<Repeat for each major finding.>

## Conclusions

<Numbered list of key takeaways. Be specific about what was confirmed
or refuted and what it means for the broader research question.>
```

### 5. Adapt to what's actually there

- Single experiment? Write a narrative report, skip multi-section layout
- Notebook source? Extract findings rather than mirroring notebook structure
- User-provided figures? Embed directly rather than regenerating
- Preliminary results? Frame as a progress update, not final write-up
- Mathematical content? Use `$...$` for inline and `$$...$$` for display

## Guidelines

- **Be concise**: each section should be 2-5 sentences unless the results
  warrant more detail
- **Include all figures**: every figure in `research_notes/attachements/$0_*`
  should appear in the report with a descriptive caption
- **Reproduce key tables**: printed metric tables from cell outputs
  become markdown tables in the report
- **Note methodological changes**: if cells were modified during the
  session, mention what was fixed and why
- **Relative figure paths**: use `attachements/` for figure links
  since both the report and the attachements folder live in `research_notes/`
- **No speculation**: only report what the data shows; flag ambiguous
  results as such
- **Bold best values** in comparison tables for quick scanning
- **Round appropriately**: 3 decimal places for metrics (MRR, accuracy),
  integers with K/M suffixes for parameter counts
- **Interpret, don't just present**: after every table or figure, explain
  what it means and why it matters
- **Line breaks**: to force a line break within a paragraph, end the line
  with two trailing spaces. A bare newline without trailing spaces is
  treated as a soft wrap (no `<br>`) by standard markdown renderers

## After writing the report

Once the report is written, suggest submitting it to the Research Dashboard:
> "Report saved. Want me to submit it to the dashboard? (`/submit-report`)"

If the user already submitted a previous version of this report and wants
to resubmit, use `--force` to skip the duplicate check (there is no
update-in-place — each submission creates a new report entry).
