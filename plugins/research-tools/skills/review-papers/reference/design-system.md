# Design-system reference

The bundled `assets/styles.css` is a **starter identity**, not a fixed theme. Customize it
per topic so each review looks made-for-this-subject (see the `frontend-design` skill).
Keep the *component structure* (classes below) constant so all pages stay cohesive.

## Theme in one place: the `:root` tokens

```
--paper / --paper-2 / --surface   page + band + card backgrounds
--ink / --ink-2 / --ink-3         text / secondary / tertiary
--line / --line-2                 hairlines
--accent / --accent-2             primary accent + hover (the topic's signature color)
--accent-bright                   accent variant for dark panels
--accent-tint                     pale accent wash
--pos / --pos-tint                second semantic color (e.g. true/yes/group-B)
--invert                          dark inversion-panel background
--display / --serif / --mono      the type trio
--col / --col-wide / --col-max    measure (prose ~720px) / wide figures / outer
--contrib-mark                    the glyph before contribution bullets (theme it!)
```

Recolor these, swap the three font families in `styles.css` *and* the Google Fonts `<link>`
in both template `<head>`s, and the whole site re-themes. Avoid the AI-default looks
(warm-cream + serif + terracotta; near-black + acid-green; broadsheet hairlines) unless the
brief asks for one.

## Pick a signature, then a hero that demonstrates it

The most memorable reviews *show* the topic's central tension in the hero rather than
describing it (e.g., twin "compare cards" with prediction bars showing a model failing).
Use the `.cmp` / `.cmp-grid` / `.bar-*` components for that, or invent one. Spend boldness
on this single element; keep everything else quiet.

## Component cheatsheet (classes in `styles.css`)

Layout: `.wrap` (outer), `.col` (prose measure), `.col-wide`, `.band` / `.band--alt`
(vertical sections w/ alternating bg).

Type / structure: `.eyebrow` (mono kicker), `.label`, `.tag` + `.tag--A` / `.tag--B`
(category chips) + `.tag--year`, `.section-head` (with `.kicker`/`.num`), `.lead`, `.muted`,
`.rule` / `.rule--accent`, `.neg`/`.strike` (accent + strikethrough spans).

Hero: `.hero`, `.grid-bg` (faint masked grid backdrop), `.hero .sub`, `.hero .meta-row`.

Compare cards (signature demo): `.cmp-grid`, `.cmp` (+ `.cmp--alt`), `.cmp .q` (the prompt
line) with `.mask` (blanked/redacted token chip) and `.cue` (accent cue word) spans inside
it, `.bar-row`, `.bar-track`, `.bar-fill[data-w]` (animates to its `data-w` width on
scroll-in), `.cmp-note` (the takeaway line). Use `.mask`/`.cue` to make the hero demo read.

Figures: `figure` (+ `.wide` / `.bleed`), `.fig-frame` (bordered box), `figcaption`
(with `.fnum`).

Math: `.eq` (+ `.eq.alt` accent border) wrapping `$$...$$`, `.eq-note`.

Tables: `.data-table` with `.T` / `.F` cells for two-valued coding.

Callouts: `.callout` (+ `.callout--key`) with a `.label`.

Category banner (inversion panel for each section): `.regime` (dark), `.regime .regime-id`
(huge id), `.regime .regime-desc`, `.regime .pill` (paper pills).

Paper review block (in index): `.paper`, `.paper-meta`, `.byline`, `.tldr`, `.contrib`
(uses `--contrib-mark`), `.readmore`.

Contents map: `.map` / `.map-col` / `.map-list`.

Timeline: `.timeline` / `.tl-row` / `.tl-year` / `.tl-body` / `.tl-tag`.

References: `.refs` (auto-numbered) / `.r-title` / `.r-auth` / `.r-links`.

Per-paper page: `.paper-hero`, `.breadcrumb`, `.authors`, `.venue`, `.actions`,
`.btn` / `.btn--accent`, `.stats` / `.stat` (n + k), `.tldr-box`.

Footer: `.site-footer` (+ `.big`, `.footer-grid`).

Motion: add class `.reveal` to any element to fade-in on scroll (respects
`prefers-reduced-motion`); `app.js` also auto-renders KaTeX and animates `.bar-fill`.

## Multiple categories

Two categories ship: **`tag--A` renders in `--pos` (the second/semantic color), `tag--B` in
`--accent` (the primary signature color)**. Assign category→letter with that in mind (or
just swap the two rules in `styles.css` if you want your lead category to carry the accent).
For 3–4 categories, add `tag--C` / `tag--D` rules and matching tints in `:root`, and give
each its own category banner.

## Floating section nav (auto-built)

`app.js` injects a bottom-right **"Contents"** toggle on every page — a collapsible panel
with a three-level table of contents, smooth-scroll, and scroll-spy highlighting of the
current section. You don't build the markup; you just mark targets:

- `data-nav="1"` — top-level section (a `<section>`, a category banner).
- `data-nav="2"` — subsection (a sub-movement, or a paper block when there's no movement).
- `data-nav="3"` — item (a paper block nested under a movement).
- `data-nav-title="…"` — the short label shown in the nav (e.g. `Kassner & Schütze 2019`).
  Falls back to the element's heading/`.label` text if omitted.

Any element type works as long as it has (or is given) an `id` — the nav generates slugged
ids for anything missing one. Pages with **no** `data-nav` markers (e.g. the per-paper
pages) fall back automatically to `<section>` + `.section-head .label` / `h2` / `h3` + `.paper h3`.
Styling lives under `.tocnav*` in `styles.css`; it hides in print and on `[data-nav]` adds
`scroll-margin-top` so anchors aren't clipped.
