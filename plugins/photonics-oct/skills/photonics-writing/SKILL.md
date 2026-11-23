---
name: photonics-writing
description: >-
  Write, restructure, polish and prepare for submission papers on integrated photonics
  (thin-film lithium niobate, modulators, resonators, swept sources) and optical coherence
  tomography, in LaTeX, for Optica, Optics Letters, Optics Express, Biomedical Optics Express,
  Nature Photonics, Nature Communications, Light: Science & Applications, Science and Science
  Advances. Use first for any writing request from this user: 写论文, 论文润色, 中译英, 起草摘要,
  引言, figure captions, methods, cover letter, response to reviewers, conference summaries
  (CLEO), or checking a draft against a journal's limits. Enforces the PI's house style (no
  semicolons, experimental results in the past tense) with a checker script, holds the journal
  requirements, photonics and OCT terminology, reporting checklists and a LaTeX preamble, and
  routes each task to the right general writing skill.
---

# Photonics writing

For a researcher building OCT systems on thin-film lithium niobate photonic integrated circuits.
The decisions below are already made. Do not ask about them again.

| Decision | Default |
|---|---|
| Manuscript language | English. Reply to the user in the language they wrote in. |
| Format | LaTeX for Overleaf: `.tex` source, BibTeX `.bib`, `siunitx` for every number with a unit. |
| Journal | Whatever the user names. If they name none, ask once, because it sets length, structure and voice. |
| Spelling | American English, which Optica, Science and most Nature Portfolio photonics papers use. |

## House style (from the PI, overrides every other skill)

Every piece of manuscript text written or edited for this user follows two rules. They come from
the PI's review of a draft and take precedence over the guidance of any other skill, including
`academic-humanizer` and the Nature skills, which allow semicolons.

1. **No semicolons in the prose.** Rewrite the sentence rather than swapping in a comma, colon
   or dash. Captions, cover letters and responses to reviewers included.
2. **Experimental results in the past tense.** Fabrication, measurements, observations,
   measured values, comparisons and simulation results are all past: "The propagation loss was
   0.21 dB/cm", "We extracted the Q from a Lorentzian fit", "The modulator achieved a 3-dB
   bandwidth beyond 67 GHz". The present stays for what a figure or the paper contains
   ("Figure 3 shows"), established physics, design facts and interpretation.

`references/house-style.md` has the repair patterns and the tense table. Before any draft goes
back to the user, run the checker and fix what it reports:

```bash
python3 scripts/check_style.py main.tex
```

Semicolons are errors and every one must go. Tense findings are candidates to read, since some
present-tense sentences are correct. For text drafted in the chat, pipe it to
`python3 scripts/check_style.py -`. When another skill produced or polished the text, run the
checker on its output too, because those skills do not know these rules.

## Ground rules

- **Never invent** a number, a measurement condition, a citation, a DOI or a comparison with
  prior work. When something is missing, write `\todo{what is needed}` in the draft and list
  the open items at the end of the reply.
- **Every performance claim carries its conditions**: wavelength, polarization, frequency,
  optical power, how it was measured, and how many devices. `references/reporting-checklist.md`
  has the list reviewers in this field expect.
- **Comparisons use the same metric definition** as the work compared against (fibre-to-fibre
  or on-chip loss, DC or RF Vπ, electrical or optical 3-dB bandwidth, resolution in air or in
  tissue). Say which.
- **"First", "record" and "state of the art"** need a citation trail or a comparison table that
  supports them. Otherwise state the number and let it stand.
- Keep the user's technical content. Polishing changes wording, not claims.

## Route by task

Read the reference file named here first, then hand the drafting to the general skill if it
is installed. The reference files hold what those skills do not know about this field. Every
route ends with the house-style check.

| Task | Read | Then use |
|---|---|---|
| Plan a paper, decide the figure sequence | `references/paper-anatomy.md` | `nature-skills:nature-writing` |
| Draft or restructure a section | `references/paper-anatomy.md`, `references/terminology.md`, `references/house-style.md` | `nature-skills:nature-writing` |
| Polish, tighten, or translate Chinese to English | `references/terminology.md`, `references/house-style.md` | `nature-skills:nature-polishing` |
| Clean up an AI-assisted draft (stock phrases, over-claiming, clause-stacked sentences) | `references/house-style.md` | `academic-humanizer:academic-humanizer`, with one of the user's published papers as the voice sample when available |
| Apply the PI's feedback to an existing draft | `references/house-style.md` | `scripts/check_style.py`, then rewrite each finding by hand |
| Grant or fellowship proposal (NSF, NIH, DOE) | `references/reporting-checklist.md` for the technical claims | `sci-research-writing:research-grants`, then `academic-humanizer:academic-humanizer` in proposal mode |
| Check length, structure, back matter, template | `references/journal-guide.md` | `sci-research-writing:venue-templates` for LaTeX scaffolds |
| Methods, or "is anything missing" | `references/reporting-checklist.md` | — |
| Figure captions | `references/paper-anatomy.md` (caption section) | `photonics-figure` for the figure itself |
| Find, add or check references | — | `sci-research-writing:paper-lookup`, `sci-research-writing:citation-management` (BibTeX), `nature-skills:nature-ref-verifier` |
| Related-work survey | — | `sci-research-writing:literature-review` |
| Self-review before submission | `references/reporting-checklist.md` | `nature-skills:nature-reviewer` |
| Response to reviewers | `references/house-style.md` | `nature-skills:nature-response` |
| Data and code availability statement | `references/journal-guide.md` | `nature-skills:nature-data` |
| Understand someone else's paper | — | `nature-skills:nature-paper-xray`, `nature-skills:nature-reader` |

The Nature skills are written for Nature-family journals. For Optica-family and AAAS targets,
keep their argument discipline and apply the limits and structure from
`references/journal-guide.md` instead of their journal fragments.

`academic-humanizer` draws its examples from machine learning. Its rules carry over with three
adjustments for this user. The evidence a claim points to is usually a measurement with its
conditions (wavelength, power, frequency, device count) rather than a benchmark table.
"Demonstrated" is the normal verb for a working device or system in optics, so keep it where a
working device backs it and reserve the downgrade for claims about generality. Its Layer 3
allows semicolons in moderation, which the house style does not.

## LaTeX conventions

Start a manuscript from the journal's official template (`references/journal-guide.md` names
each one) and add `assets/photonics-preamble.tex`, which sets up `siunitx` and the macros for
recurring symbols. Then:

- Numbers with units: `\qty{1550}{\nm}`, `\qty{2.3}{\V\cm}`, `\qtyrange{1260}{1360}{\nm}`,
  `\qty{0.2}{\dB\per\cm}`. Never type a unit by hand.
- One label scheme with the prefixes `fig:`, `tab:`, `eq:` and `sec:`. Refer with
  `Fig.~\ref{fig:setup}(a)` for Optica, `Fig.~\ref{fig:setup}a` for Nature and
  `Fig.~\ref{fig:setup}A` for Science.
- Figures as vector PDF at the final column width, so `\includegraphics` needs no scaling.
- One `.bib` file with DOIs. Citation keys `firstauthorYEARkeyword`.
- Science's template forbids extra packages. For a Science submission, expand the macros and
  write units by hand in the same form.

## Before handing over a draft

1. `python3 scripts/check_style.py` on every changed file: zero semicolons, and each tense
   finding either rewritten in the past tense or a correct present (figure pointer, design fact,
   physics, interpretation).
2. Word, page, figure and reference counts against the target in `references/journal-guide.md`.
3. Every abbreviation defined once at first use in the abstract and again in the main text.
4. Every number has a unit, a condition and consistent significant figures between abstract,
   text, figure and table.
5. Each figure is cited in order, and every panel is mentioned in the text.
6. `\todo{}` items listed for the user.
