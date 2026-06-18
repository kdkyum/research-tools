---
name: review-papers
description: >
  Turn a reading list of papers into a polished, citation-rich literature-review
  website. Use this skill when the user gives several papers at once and wants them
  synthesized. Triggers on: "review these papers", "write a review/survey blog post
  about <topic>", "read all these arxiv papers and synthesize/aggregate them", a list
  of multiple arxiv URLs or IDs given together, "make a literature review", "survey of
  <topic>", "compare these papers", or any request to read several papers and aggregate
  them into one long-form HTML write-up. Reads each paper from TeX source via the
  read-arxiv-paper procedure (one subagent per paper), builds a standalone HTML page per
  paper, and aggregates them into a categorized long-form review (index.html) with real
  figures, LaTeX equations, citations + links, and a related-work section.
---

# Review Papers → long-form HTML literature review

Read a whole reading list, build one deep-dive HTML page per paper, and weave them
into a single categorized long-form review website. The output is pure static HTML
(no build step): equations via KaTeX, real figures extracted from each paper's source,
every claim cited and linked.

## What it produces

```
<out>/                       # default: ./htmls/<review-slug>/  (one folder per review)
├── index.html               # the long-form review (hero, categories, timeline, refs)
├── {arxiv_id}.html          # one standalone deep-dive page per paper (linked from index)
└── assets/
    ├── styles.css           # ONE shared design system (themed to the topic)
    ├── app.js               # KaTeX auto-render + scroll reveal + animated bars
    ├── paper_template.html  # per-paper page skeleton (filled per paper)
    ├── index_template.html  # main-review skeleton
    └── {arxiv_id}/figN.png  # real figures extracted from each paper
```

## Inputs (parse from the request)

- **Reading list** (required): arxiv URLs/IDs (`abs` or `pdf` form, or bare IDs).
- **Topic / title** (required): what the review is about. If absent, infer from the papers.
- **Category scheme** (optional): the user may specify the buckets to organize by
  (e.g., *"two categories: pretrained-LLM investigation vs. fine-tuning on new knowledge"*).
  If not given, infer 2–4 thematic categories after reading.
- **Output dir** (optional). Default `./htmls/<review-slug>/` — a kebab-case folder named
  for the topic (e.g. `./htmls/negation-in-llms/`) so multiple reviews coexist under
  `./htmls/`. Pages and their `assets/` live together in this folder, so all links are
  relative and the folder is self-contained/movable.
- **Related work** (default: yes — find ~6–10 relevant papers *not* in the list).

## Workflow

### 1. Verify & inventory
Confirm each ID exists and de-dupe. Scrape `https://arxiv.org/abs/{id}` for the
`citation_title` / `citation_author` / `citation_date` meta tags (or use the export API).
Flag anything that 404s before spending agents on it. Record title/authors/year for each.

### 2. Establish the design system FIRST (this is what guarantees cohesion)
Create `<out>/assets/` and copy the four bundled starter files from this skill's
`assets/` directory into it: `styles.css`, `app.js`, `paper_template.html`,
`index_template.html` (`app.js` needs no edits; copy it verbatim). Then **customize the
identity to the topic** — this is what
makes each review distinctive rather than templated:
- Recolor the `:root` tokens in `styles.css`; choose a deliberate display/body/mono type
  trio; design **one signature element** and a hero that *demonstrates the topic's core
  tension* instead of describing it.
- If the **frontend-design** skill is available, run its planning pass for the identity.
- See `reference/design-system.md` for the token map and the component cheatsheet.
Every per-paper page and the index share this single identity.

### 3. Read every paper with subagents — one per paper
Fan out. **Prefer the Workflow tool** for deterministic parallel fan-out with structured
returns; otherwise launch parallel `Agent` calls; otherwise read sequentially. Hand each
agent the recipe and JSON schema in `reference/orchestration.md`. Each agent must:
1. Read the paper from **TeX source** via the **read-arxiv-paper** procedure
   (`https://arxiv.org/e-print/{id}` → extract → main `.tex` + `\input`/`\include` →
   figures). PDF fallback (`pdftotext` / `pdftoppm`) only if no usable source.
2. Extract the **1–3 most informative real figures**; convert PDF→PNG with
   `pdftocairo -png -singlefile -r 150 IN.pdf <out>/assets/{id}/fig1` (the `-singlefile`
   flag + an extension-less root are required, else a page-number suffix is appended and the
   `figN.png` link 404s) and SVG→PNG with `rsvg-convert`; **view each with Read** so the
   caption is accurate; save to `<out>/assets/{id}/figN.png`.
3. Write `<out>/{id}.html` from `paper_template.html` — fill every `{{PLACEHOLDER}}`,
   delete unused optional blocks, keep classes and asset links intact. Math as
   `$...$` / `$$...$$`.
4. Return the structured JSON (schema in `reference/orchestration.md`).

### 4. (Optional) Related work
One or two search agents find papers **not** in the list, verify them on arxiv, and
return citation + one-line relevance + category. Never fabricate arxiv IDs.

### 5. Aggregate into the main review — `<out>/index.html`
Build from `index_template.html` a long-form post:
- **Hero**: a signature moment that demonstrates the topic's core tension.
- **Framing**: definitions, key equations, a small table if useful.
- **One section per category**: review each paper with its real figure, a key equation,
  1–2 paragraphs of synthesis (not just summary — connect papers, note agreements/conflicts),
  its citation, and a *read more →* link to its deep-dive page. Use the bundled category
  banner (inversion panel) per section.
- **Timeline** (years carry real signal), **synthesis / open problems**, the
  **related-work** list, and a numbered **references** list (full citation + arxiv link +
  per-paper page link).
Professional voice for researchers. Accuracy over flourish — never invent numbers,
figures, or citations.

### 6. Validate
Check every referenced `assets/{id}/figN.png` exists; every per-paper link resolves;
KaTeX delimiters are balanced; the page is responsive at mobile width with visible focus
and reduced-motion respected. Fix problems. Screenshot if a browser/headless tool exists.

## Conventions

- Paper source cache: `~/.cache/arxiv-papers/knowledge/{id}/` (same layout as read-arxiv-paper, so sources de-dupe across the two skills).
- CDNs already linked in the templates: Google Fonts + KaTeX 0.16.x. Pure static HTML.
- Keep ONE design identity across all pages; spend boldness on the single signature element.
- Scale effort to the ask: a 3-paper compare is lighter than a 20-paper survey.
