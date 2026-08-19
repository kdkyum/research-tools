---
name: review-papers
description: >
  Build a static literature review website from a list of papers. Use this
  skill when the user supplies several papers and wants one review that
  compares or synthesizes them. Common requests include "review these
  papers", "write a review or survey about <topic>", "read these arxiv
  papers and synthesize them", "make a literature review", and "compare
  these papers". Also use it when the user supplies several arxiv URLs or
  IDs together. The skill reads TeX source, assigns one paper to each
  subagent, creates one HTML page per paper, and builds an index with
  citations, equations, extracted figures, and related work.
---

# Review papers

Turn a reading list into a static website. Each paper gets its own page. The
index groups the papers by topic and explains where their methods and findings
agree or conflict. Every factual claim needs a citation and link.

## Output files

```
<out>/                       # Default is ./htmls/<review-slug>/
├── index.html               # Main review
├── {arxiv_id}.html          # One page for each paper
└── assets/
    ├── styles.css           # Shared styles
    ├── app.js               # KaTeX rendering and page behavior
    ├── paper_template.html  # Template for paper pages
    ├── index_template.html  # Template for the main review
    └── {arxiv_id}/figN.png  # Figures extracted from each paper
```

The website uses static HTML and needs no build step.

## Inputs

- **Reading list.** Required. Accept arxiv URLs, `abs` or `pdf` URLs, and bare
  arxiv IDs.
- **Topic and title.** Infer them from the papers when the user does not supply
  them.
- **Categories.** Use the user's categories when supplied. Otherwise, infer two
  to four categories after reading the papers.
- **Output directory.** Use `./htmls/<review-slug>/` unless the user gives a
  path. Choose a kebab-case slug based on the topic. Keep every page and asset
  inside this directory so the website can be moved as one folder.
- **Related work.** Enabled by default. Find six to ten relevant papers that
  are not in the reading list.

## Workflow

### 1. Check the reading list

Confirm that each arxiv ID exists and remove duplicates. Read the
`citation_title`, `citation_author`, and `citation_date` metadata from
`https://arxiv.org/abs/{id}` or use the arxiv export API. Report missing papers
before spawning subagents. Record the title, authors, and year for every valid
paper.

### 2. Create the shared design

Create `<out>/assets/`. Copy these bundled files into it:

- `styles.css`
- `app.js`
- `paper_template.html`
- `index_template.html`

Copy `app.js` without changes. Adapt the other files to the subject before
writing any pages.

- Change the `:root` color tokens in `styles.css`.
- Choose display, body, and monospace fonts that fit the subject.
- Add one visual device tied to the papers, such as a diagram of the main
  disagreement or a comparison used throughout the review.
- If the `frontend-design` skill is available, use it to plan this direction.
- Read `reference/design-system.md` for the token map and component reference.

Every page must use the same styles, fonts, navigation, and visual device.

### 3. Read the papers in parallel

Assign one paper to each subagent. Use the Workflow tool when available so each
agent returns the same JSON structure. Otherwise, launch `Agent` calls in
parallel. Read papers sequentially only when neither tool is available.

Give each agent the instructions and JSON schema in
`reference/orchestration.md`. Each agent must complete the following work.

1. Read the paper from TeX source. Download
   `https://arxiv.org/e-print/{id}`, locate the main `.tex` file, and follow all
   `\input` and `\include` directives. Use `pdftotext` or `pdftoppm` only when
   the source has no usable TeX.
2. Extract the one to three figures that best explain the paper. Convert PDF
   figures with:

   ```bash
   pdftocairo -png -singlefile -r 150 IN.pdf <out>/assets/{id}/fig1
   ```

   Keep `-singlefile` and use a destination without an extension. Otherwise,
   `pdftocairo` adds a page number and the expected `figN.png` path will not
   exist. Convert SVG figures with `rsvg-convert`. Open every converted image
   with Read and check its caption before using it.
3. Create `<out>/{id}.html` from `paper_template.html`. Replace every
   `{{PLACEHOLDER}}`, remove unused optional blocks, and preserve the existing
   classes and asset paths. Write inline math as `$...$` and display math as
   `$$...$$`.
4. Return the JSON structure defined in `reference/orchestration.md`.

### 4. Find related work

Unless the user opts out, use one or two search agents to find papers outside the reading list. Verify
each arxiv ID. Return the full citation, one sentence explaining its relevance,
and the category where it belongs. Never invent an arxiv ID.

### 5. Build the main review

Create `<out>/index.html` from `index_template.html`.

- **Opening.** Start with a concrete example, figure, or question that shows
  what problem the papers address or where they disagree.
- **Background.** Define the terms and equations needed to understand the
  comparison. Add a small table only when it clarifies the setup.
- **Category sections.** Write one section for each category. Cover every paper
  with a real figure, a key equation when relevant, and one or two paragraphs
  that compare it with the other papers. Note agreements and conflicts. Add
  the citation and a `read more` link to the paper page. Use the bundled
  inversion banner for each category.
- **Ending.** Add a timeline when publication order matters. Then write the
  synthesis, open problems, related work, and a numbered reference list. Each
  reference needs a full citation, an arxiv link, and a link to its paper page.

Write for researchers. Prefer exact claims to dramatic language. Never invent
numbers, figures, or citations.

### 6. Validate the website

Check all of the following before finishing:

- Every `assets/{id}/figN.png` path exists.
- Every paper and citation link resolves.
- KaTeX delimiters are balanced.
- The pages fit a mobile viewport without horizontal page scrolling.
- Keyboard focus remains visible.
- Reduced-motion preferences disable nonessential motion.

Fix every failure. Take screenshots when a browser or headless browser is
available.

## Conventions

- Cache paper sources at `~/.cache/arxiv-papers/knowledge/{id}/`. The
  `read-arxiv-paper` skill uses the same cache.
- The templates already link to Google Fonts and KaTeX 0.16.x.
- Keep one set of shared styles and templates across the website.
- Match the amount of work to the reading list. A three-paper comparison needs
  less detail than a twenty-paper survey.
