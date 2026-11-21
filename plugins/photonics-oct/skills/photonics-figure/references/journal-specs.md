# Journal figure specifications

Compiled 2026-11-21. The numbers in `scripts/pubfig.py` come from this table.

**How far to trust each number.** The publishers' sites could not be opened from the session
that compiled this, so nothing here was read on a live author page.

- **T** — read from the publisher's own LaTeX class or template file. Reliable for geometry.
- **S** — text returned by a web search restricted to the publisher's domain. Probably right;
  confirm on the live page before a final submission.
- **C** — field convention or a conservative choice, not a published rule.

## Optica Publishing Group

| Item | Value | Basis |
|---|---|---|
| Two-column journals (Optica, Optics Letters, Photonics Research, AO, JOSA): column / text width | 87.9 mm / 184.3 mm | T: `opticajnl.cls` margins 48 pt and 42 pt on letter paper, 24 pt column gap |
| Single-column journals (Optics Express, Biomedical Optics Express): text width | 133.4 mm (5.25 in) | T: `optica-article.cls` margins 1.625 in |
| Express caption width | 108 mm (4.25 in) | T: `\captionsetup{width=4.25in}`; used as the default "single" width for `oe` |
| Maximum height | 230 mm (two-column), 200 mm (Express) | C: text height minus room for a caption |
| Caption font | 8 pt, label "Fig. 1." | S: style guide; T: class |
| In-figure font | 8 pt, never below 6 pt | C; a legacy OSA page says "no smaller than 6-8 point" after reduction (S) |
| Panel labels | (a), (b) in regular weight | C: what Optica journals print; no current rule found |
| File formats | PDF or EPS with a LaTeX submission, one file per figure | T, S |
| Resolution | 300 dpi, 600 dpi with text or line art | S: legacy page only |
| Colour | Do not rely on colour alone; add line styles, markers or labels | S: current style guide |
| Rule | "No part of a figure should go beyond the text margins." | S |

Older OSA guidance gives a one-column width of 8.4 cm (S). `pubfig` uses the template value of
88 mm; a figure made at 84 mm is also fine.

## Nature Portfolio

| Item | Nature, Nature Photonics | Nature Communications, LSA | Basis |
|---|---|---|---|
| Single / 1.5 / double column | 89 / 120–136 / 183 mm | 88 / — / 180 mm | S |
| Maximum height | 170 mm, to leave room for the legend | not found; `pubfig` uses 225 mm | S / C |
| Text | 5–7 pt, sans-serif, Helvetica or Arial | 5–8 pt, Arial or Helvetica | S |
| Panel labels | 8 pt bold upright lowercase: a, b, c | lowercase bold, same size as other text | S |
| Line weight | 0.25–1 pt | 0.25 pt minimum (older guide) | S |
| Formats | .ai, .eps, .pdf with editable text | .ai, .eps, .pdf, .ps, .svg; TIFF for photos | S |
| Resolution | 300 dpi at final size | 300 dpi; 1200 dpi for rasterized line art | S |
| Colour | RGB; avoid red-green contrast and rainbow scales | RGB | S |

Nature Photonics says panels are saved "at a maximum width of 180 mm" (S); the 183 mm preset is
3 mm wider, so use `pf.figure("full180")` for a full-width Nature Photonics figure if in doubt. No
LSA-specific figure rules were found; the Nature Communications preset is a stand-in.

## AAAS

| Item | Science | Science Advances | Basis |
|---|---|---|---|
| Widths | 57 / 121 / 184 mm (1, 2, 3 columns) | 90 mm and 184 mm, or anything between | S |
| Maximum height | not found; `pubfig` uses 215 mm | 199 mm recommended (page is 227.5 mm) | C / S |
| Text | Helvetica or Arial, 6–9 pt | 8 pt, minimum 6 pt, sentence case | S |
| Panel labels | bold capitals A, B, C at 9 pt | bold capitals at 9 pt | S |
| Line weight | 0.5 pt minimum | not found; `pubfig` uses 0.5 pt | S / C |
| Formats | vector PDF, EPS or AI; TIFF for raster | vector PDF or AI; TIFF, PNG, JPEG | S |
| Resolution | 300 dpi at print size | 300 dpi; 1200 dpi for line art | S |

**Unresolved for Science.** The initial-manuscript page gives 5.7 / 12.1 / 18.4 cm, while the
2025 figure-preparation PDF gives one column as 9 cm and two as 18.3 cm, and panel letters as
10 pt rather than 9 pt. `pubfig` follows the web page. Before building final Science figures,
open the current figure guide and, if it says 9 cm, use the `sciadv` preset.

## Slides

`pf.use("slides")` targets a 16:9 slide (13.33 × 7.5 in): 16 pt text, 1.8 pt lines, half-slide
(150 mm) and full-slide (310 mm) widths. It is a readability preset, not a journal rule.

## Sources

- Optica style guide: https://opg.optica.org/content/author/portal/item/style-optica-styleguide/
- Optica templates: https://opg.optica.org/content/author/portal/item/templates-default
- Nature final submission: https://www.nature.com/nature/for-authors/final-submission
- Nature figure guide: https://research-figure-guide.nature.com/
- Nature Photonics formatting: https://www.nature.com/nphoton/submission-guidelines/aip-and-formatting
- Nature Communications: https://www.nature.com/ncomms/submit/how-to-submit
- Science initial manuscript: https://www.science.org/content/page/instructions-preparing-initial-manuscript
- Science revised manuscript: https://www.science.org/content/page/instructions-preparing-revised-manuscript
- Science Advances: https://www.science.org/content/page/science-advances-information-authors
