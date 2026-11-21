# Journal requirements for photonics and OCT papers

Compiled 2026-11-21. Limits change; this is for planning a draft, not for certifying one.

**How far to trust each line.** The publishers' sites could not be opened from the session that
compiled this.

- **T** — read from the publisher's own LaTeX template or class file.
- **S** — text returned by a web search restricted to the publisher's domain; confirm on the
  live page before submission.
- **C** — long-standing house convention seen in published papers, not checked against a page.
- **?** — not found; check the author page.

Figure sizes and typography are in the `photonics-figure` skill
(`references/journal-specs.md`).

## Choosing between them

| Journal | Length | Fits |
|---|---|---|
| Optics Letters | 4 pages | One result, one or two key figures, fast turnaround |
| Optica | Letter 4 pages; Article 6–8 pages | High-impact result with a complete story |
| Optics Express, Biomedical Optics Express | No page limit found; page charges above 15 pages | Full engineering detail; BOE for imaging and biomedical validation |
| Photonics Research | ? | Device and platform papers |
| Nature Photonics | 3,000 words, 6 display items | A capability change, argued for a broad photonics readership |
| Nature Communications | about 5,000 words, 10 display items | Complete study with broad interest |
| Light: Science & Applications | 6,000 words | Device or system paper with application reach |
| Science | about 3,000 words, 3–5 display items | Result of interest outside optics |
| Science Advances | up to 15,000 words, 10 display items | Full study, Science-family format |

## Optica Publishing Group

**Templates.** Two official LaTeX templates, both on Overleaf and as a ZIP from the templates
page (T):

- Two-column "length-check" template, `\documentclass[9pt,twocolumn,twoside]{opticajnl}` with
  `\journal{opticajournal}`: Optics Letters, Optica, Photonics Research, AO, JOSA A/B. Use it for
  anything with a page limit. `\setboolean{shortarticle}{true}` selects the letter layout,
  `false` the research-article layout.
- Single-column universal template, `\documentclass{optica-article}`: Optics Express, Biomedical
  Optics Express and the other Express-layout journals. To estimate two-column pages, multiply
  the page count by 0.6 (T).
- BibTeX style `opticajnl.bst` (T).

**Length.**

- Optics Letters, and Letters in Optica: four printed pages; over-length papers are returned (S).
- Optica: research articles 6–8 pages, letters 4 pages, memoranda 2 pages, mini-reviews 8–12
  pages (S). A cover letter of about 250 words is required (S).
- Optics Express and BOE: no limit found; a per-page charge applies above 15 published pages (S).
- Abstract: about 100 words (T, S).

**Structure.** Numbered sections for articles (Introduction, then sections named for the
content, then Conclusion); Optics Letters papers run without section headings (C). Back matter is unnumbered
and in this order (T):

1. Funding — generated from what is entered in the Prism submission system.
2. Acknowledgment.
3. Disclosures — conflict-of-interest codes, or "The authors declare no conflicts of interest."
4. Data availability — required for all submissions.
5. Supplemental document — "See Supplement 1 for supporting content." Photonics Research does
   not accept a supplemental PDF.

**References.** Numbered in order of first citation, `[1]` in square brackets; the first
reference cited must be [1]; up to three authors then "et al."; no footnotes (T). Optics
Letters and Optica short articles use an abbreviated style without article titles, produced by
the template; the template also appends a full reference list with titles for the reviewers,
which does not count against the page limit (T). An older Optica page describes this the other
way round, so follow whatever the current template produces.

**Figures and captions.** Captions start "Fig. 1." and are 8 pt (S, T). Subfigures are cited as
Fig. 1(a) (C). One file per figure, PDF or EPS (T, S). Do not rely on colour alone to separate
curves (S).

**CLEO summaries.** Two pages plus a 35-word abstract for the programme, submitted as PDF with
embedded fonts; the conference page links the template (S). Check the current year's page for
the exact template.

## Nature Portfolio

**Templates.** Nature journals accept LaTeX in any standard class (`article`, `revtex`) as a
single `.tex` file with figures supplied separately (S). The Springer Nature template
(`sn-jnl.cls`, reference style option `sn-nature`) is the usual choice (T). Nature
Communications wants numeric citations and the reference list pasted into the `.tex` from the
`.bbl` (S). There is no required format at first submission for Nature Communications (S).

| | Nature Photonics | Nature Communications | Light: Sci. & Appl. | Nature |
|---|---|---|---|---|
| Main text | up to 3,000 words, excluding abstract, Methods, references, legends (S) | ideally within 5,000 words (S) | 6,000 words (S) | about 2,500 words for a typical six-page Article (S) |
| Abstract | up to 200 words, no references (S) | up to 200 words, no references (S) | up to 250 words, no abbreviations or references (S) | summary paragraph of about 200 words (S) |
| Display items | up to 6 (S) | up to 10 (S) | 8 in the 2019 guide; current value ? | ? |
| References | about 50 (S) | about 70 as a guide (S) | up to 50 (S) | up to 50 in the main text (S) |
| Methods | online Methods; limit ? | typically under 3,000 words (S) | ? | typically under 3,000 words (S) |
| Extended Data | up to 10 figures (S) | — | — | up to 10 items (S) |

**Structure.** Nature Photonics: introduction without a heading, Results, Discussion, Methods
(S). Nature Photonics no longer has a Letter format (S). Data availability and Code availability
statements close the Methods, followed by Acknowledgements, Author contributions and Competing
interests (S for Nature; C for the others). Figure legends
up to about 350 words for Nature Communications (S).

**References.** Numbered in order of appearance (S), cited as superscripts (C). Titles are included (S). Nature lists
all authors up to five, otherwise the first author and "et al." (S).

## AAAS

**Template.** `science_template.tex` v1.1 with `scicite.sty` and `sciencemag.bst`, from the
Science LaTeX page or Overleaf; it covers Science and Science Advances (T). The template says
not to load additional packages and not to use `figure*` (T). Science prefers a `.docx` file but
accepts LaTeX (S).

| | Science (Research Article) | Science Advances |
|---|---|---|
| Main text | about 3,000 words; an extended online format allows about 6,000 (S, from summaries: confirm) | up to 15,000 words (S; what the count includes is ?) |
| Abstract | 125 words or fewer (S) | 150 words or fewer, one paragraph (S) |
| Display items | 3–5 (S: confirm) | up to 10 (S) |
| References | about 50 (S: confirm) | up to 80 (S) |
| Title | up to 125 characters; short title 40 (S) | up to 135 characters; short title 50 (S) |

**Structure.** Science: main text without a Methods section; Materials and Methods go in the
supplement and are cited as a numbered note (T). Science Advances: Introduction, Results,
Discussion, Materials and Methods in the main text (S). Both end with "References and Notes"
and an Acknowledgments section with required subheadings: Funding, Author contributions,
Competing interests, Data, code and materials availability; then the list of supplementary
materials (T). "Available on request" is not accepted for data (T).

**References and captions.** Numeric citations in italic parentheses, titles included (T).
Captions start with a short bold title sentence; panels are referred to as (**A**), (**B**) (T).

## Sources

- Optica style guide: https://opg.optica.org/content/author/portal/item/style-optica-styleguide/
- Optica templates: https://opg.optica.org/content/author/portal/item/templates-default
- Optica article types: https://opg.optica.org/submit/review/optica.cfm
- Optica publication charges: https://opg.optica.org/content/author/portal/item/review-pub-charge/
- Nature Photonics content types: https://www.nature.com/nphoton/content
- Nature Communications: https://www.nature.com/ncomms/submit/article
- LSA guide for authors: https://www.nature.com/documents/Guide_for_Authors_lsa_gta.pdf
- Nature formatting guide: https://www.nature.com/nature/for-authors/formatting-guide
- Springer Nature LaTeX: https://www.springernature.com/gp/authors/campaigns/latex-author-support
- Science LaTeX: https://www.science.org/content/page/preparing-manuscripts-using-latex
- Science authors: https://www.science.org/content/page/science-information-authors
- Science Advances authors: https://www.science.org/content/page/science-advances-information-authors
