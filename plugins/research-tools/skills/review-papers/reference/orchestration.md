# Orchestration reference

How to fan out one subagent per paper, what each must do, the JSON it returns, and a
ready-to-adapt Workflow script. Read this when running step 3 of `SKILL.md`.

---

## Per-paper agent prompt (template)

Give each reader agent a prompt built from this template. Substitute `{id}`, `{title}`,
`{authors}`, `{year}`, `{category_id}`, `{category_name}`, `{category_hint}`, `{topic}`,
and `{OUT}` (the absolute output dir, e.g. `/abs/path/htmls`). Note **`{{ARXIV_ID}}` in the
HTML template == `{id}`**, and the figure directory you create must match it.

```
You are a meticulous ML research analyst and frontend builder. Read ONE paper from its
LaTeX source and produce (a) a standalone styled HTML page and (b) a structured JSON
summary. ACCURACY IS PARAMOUNT — never invent numbers, results, figures, or claims; if
unsure, omit.

PAPER: arXiv {id}  —  "{title}" by {authors} ({year}).
Assigned category: {category_id} = "{category_name}" ({category_hint}). Confirm this fits
as you read; if clearly wrong, set category to the correct id and say so in notes.

STEP 1 — Source (read-arxiv-paper procedure; cache is shared with the read-arxiv-paper skill):
  ARXIV_ID={id}
  SRC=~/.cache/arxiv-papers/knowledge/$ARXIV_ID.tar.gz
  DIR=~/.cache/arxiv-papers/knowledge/$ARXIV_ID
  mkdir -p "$DIR"
  # Download once. Guard on NON-EMPTY: wget/curl leave a 0-byte file on HTTP errors,
  # which a plain [ -f ] test would wrongly treat as "already cached".
  if [ ! -s "$SRC" ]; then
    curl -L -sS -o "$SRC" "https://arxiv.org/e-print/$ARXIV_ID" || wget -q -O "$SRC" "https://arxiv.org/e-print/$ARXIV_ID"
  fi
  # Unpack by real file type (explicit case — no fragile && / || chains).
  T=$(file -b "$SRC")
  case "$T" in
    *gzip*) tar xzf "$SRC" -C "$DIR" 2>/dev/null || gzip -dc "$SRC" > "$DIR/main.tex" ;;  # tar.gz, or a single gzipped .tex
    *tar*)  tar xf  "$SRC" -C "$DIR" 2>/dev/null ;;                                        # uncompressed tar
    *)      cp "$SRC" "$DIR/main.tex" ;;                                                   # bare uncompressed .tex
  esac
  Fallback if no usable .tex: download the PDF and read it instead —
    PDF=~/.cache/arxiv-papers/knowledge/$ARXIV_ID.pdf
    [ -s "$PDF" ] || curl -L -sS -o "$PDF" "https://arxiv.org/pdf/$ARXIV_ID"
    pdftotext -layout "$PDF" "$DIR/_fulltext.txt"      # read this for the text
  (note this PDF fallback in `notes`).

STEP 2 — Read: find the main .tex (\documentclass + \begin{document}) under "$DIR"; follow
  \input/\include. Read abstract, intro, method, key equations, experiments/results
  (extract REAL numbers), limitations, conclusion.

STEP 3 — Figures (REAL images only): list *.png/*.jpg/*.pdf/*.svg under "$DIR". Pick the 1–3
  most informative. Convert into {OUT}/assets/$ARXIV_ID/ (mkdir -p first). IMPORTANT: pass a
  root with NO extension and use -singlefile, or pdftocairo/pdftoppm append a page number
  (`fig1.png` -> `fig1-1.png`) and the HTML's `assets/$ARXIV_ID/fig1.png` link 404s:
    PDF -> PNG:  pdftocairo -png -singlefile -r 150 IN.pdf {OUT}/assets/$ARXIV_ID/fig1   # writes fig1.png
       fallback: pdftoppm  -png -singlefile -r 150 IN.pdf {OUT}/assets/$ARXIV_ID/fig1   # writes fig1.png
    SVG -> PNG:  rsvg-convert -w 1500 IN.svg -o {OUT}/assets/$ARXIV_ID/fig1.png
    PNG/JPG:     cp IN.png {OUT}/assets/$ARXIV_ID/fig1.png     (EPS / failed convert -> skip, pick another)
  USE THE Read TOOL to view each candidate so the caption/alt are accurate (don't grab a
  logo). Match each to its real \caption{...}. If a PNG is huge (check `wc -c fig1.png`;
  >1.8MB), re-render the source at -r 110 with the same -singlefile form. If no usable
  figure exists, return key_figures:[] and delete the figure blocks from the HTML.

STEP 4 — HTML: read {OUT}/assets/paper_template.html and skim {OUT}/assets/styles.css.
  Write {OUT}/$ARXIV_ID.html filling EVERY {{PLACEHOLDER}} and deleting optional blocks you
  don't use. Fill {{ARXIV_ID}} with $ARXIV_ID (must match the figure dir). Keep <head>,
  class names, and relative asset links exact. Category tag class tag--A / tag--B (extend if
  more categories). Equations as real $...$ / $$...$$ LaTeX. Precise technical voice,
  ~700–1100 words. Cover: TL;DR, Contributions, key figure, Method (+eq), Results
  (+figure/table), "Why it matters for {topic}", Limitations, BibTeX.

STEP 5 — Return JSON via StructuredOutput matching the schema. key_figures[].path must be
  relative ("assets/$ARXIV_ID/fig1.png") and the file MUST exist. status="ok" when the page
  + figures are written.
Do the work with your tools now; your FINAL message must be the StructuredOutput call.
```

---

## Return JSON schema

Topic-agnostic by default. The relevance field is `topic_relevance` (it holds the
"why it matters for <topic>" blurb the index and the per-paper template consume).

```jsonc
{
  "type": "object", "additionalProperties": false,
  "required": ["id","title","authors_short","authors_full","year","venue","category",
    "subthread","tldr","contributions","method_summary","key_results","key_figures",
    "key_equations","topic_relevance","limitations","bibtex","html_path","status"],
  "properties": {
    "id": {"type":"string"}, "title": {"type":"string"},
    "authors_short": {"type":"string"}, "authors_full": {"type":"string"},
    "year": {"type":"string"}, "venue": {"type":"string"},
    "category": {"type":"string"}, "subthread": {"type":"string"},
    "tldr": {"type":"string"},
    "contributions": {"type":"array","items":{"type":"string"}},
    "method_summary": {"type":"string"},
    "key_equations": {"type":"array","items":{"type":"object","additionalProperties":false,
      "required":["latex","note"],"properties":{"latex":{"type":"string"},"note":{"type":"string"}}}},
    "key_results": {"type":"string"},
    "key_figures": {"type":"array","items":{"type":"object","additionalProperties":false,
      "required":["path","caption","alt"],"properties":{"path":{"type":"string"},
      "caption":{"type":"string"},"alt":{"type":"string"}}}},
    "limitations": {"type":"string"},
    "topic_relevance": {"type":"string"},
    "quote": {"type":"string"},
    "headline_stats": {"type":"array","items":{"type":"object","additionalProperties":false,
      "required":["n","k"],"properties":{"n":{"type":"string"},"k":{"type":"string"}}}},
    "bibtex": {"type":"string"},
    "html_path": {"type":"string"},
    "status": {"type":"string","enum":["ok","partial","failed"]},
    "notes": {"type":"string"}
  }
}
```

The main review (step 5 of SKILL.md) consumes per paper: `tldr`, the top `contributions`,
one of `key_figures`, one of `key_equations`, `topic_relevance`, `category`, and the
citation fields (`title`/`authors_full`/`year`/`venue`/`id`). `key_equations` is required
but may be `[]` (delete the template's equation block when empty). `headline_stats` (0–4)
feeds the per-paper stat strip; delete the strip when empty.

---

## Workflow script skeleton (adapt and run via the Workflow tool)

```js
export const meta = {
  name: 'paper-review-fanout',
  description: 'Read N papers from TeX source, build a per-paper HTML page for each, find related work',
  phases: [ { title: 'Read papers' }, { title: 'Related' } ],
}
const OUT = '/abs/path/htmls'
const PAPER_SCHEMA = { /* paste the JSON schema above (strip // comments) */ }
const RELATED_SCHEMA = { type:'object', additionalProperties:false, required:['papers'],
  properties:{ papers:{ type:'array', items:{ type:'object', additionalProperties:false,
    required:['title','authors','year','url','category','why'],
    properties:{ title:{type:'string'}, authors:{type:'string'}, year:{type:'string'},
      venue:{type:'string'}, url:{type:'string'}, category:{type:'string'}, why:{type:'string'} } } } } }
const PAPERS = [ { id:'XXXX.XXXXX', title:'...', authors:'...', year:'20XX', cat:'A', thread:'...' }, /* ... */ ]

function promptFor(p){ return `...per-paper template above, with ${p.id} etc...` }

phase('Read papers')
const tasks = [
  ...PAPERS.map(p => () => agent(promptFor(p), { schema: PAPER_SCHEMA, label: `read:${p.id}`, phase: 'Read papers' })),
  () => agent(`Find related papers not in [${PAPERS.map(p=>p.id)}] about <topic>; verify on arxiv; return JSON`,
    { schema: RELATED_SCHEMA, label: 'related', phase: 'Related' }),
]
const all = await parallel(tasks)
return { papers: all.slice(0, PAPERS.length).filter(Boolean), related: all.slice(PAPERS.length).filter(Boolean) }
```

After the workflow returns, the main loop writes `index.html` from `index_template.html`
using the aggregated `papers` + `related` data, then validates (step 6).

### If the Workflow tool is unavailable
Launch the paper agents as parallel `Agent` tool calls in a single message (one per paper),
each given the per-paper prompt, and collect their structured replies. Sequential reading is
the last resort.
