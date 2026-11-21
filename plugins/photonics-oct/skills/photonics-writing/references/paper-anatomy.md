# Anatomy of a device or system paper

How papers on integrated-photonic devices and OCT systems are usually built, and what each
part has to do. Use it to plan a draft and to find what a draft is missing. It describes
common practice, so depart from it when the result calls for a different order.

## The one-paragraph test

Before drafting, write four sentences. If one cannot be written, the paper is not ready to
draft, and the missing sentence says what to work out with the user.

1. **Need** — what the application cannot do today, with a number (imaging speed, range, size,
   cost, drive voltage).
2. **Why existing approaches fall short** — the specific physical or engineering limit, cited.
3. **What we did** — the device or system and the idea that makes it work, in one sentence.
4. **What it achieves** — the two or three headline numbers with their conditions, and what
   they enable.

These four sentences are the abstract's skeleton and the introduction's last paragraph.

## Abstract

Optica family, about 100 words: need in one sentence, approach in one, results with numbers in
two, consequence in one. Nature and Science family, 125–200 words, no references: one or two
sentences of context a physicist outside the subfield can follow, the gap, "Here we ...", the
main results with numbers, and the wider implication.

Put the headline numbers in the abstract with units and the key condition ("a 3-dB
electro-optic bandwidth above 67 GHz at 1310 nm"), and make them match the text exactly.

## Introduction

Three to five paragraphs, narrowing:

1. The application and why it matters, kept to the reader's field. For OCT: what clinical or
   industrial capability depends on the parameter being improved.
2. The current solutions and the limit they hit. Group prior work by approach, not by paper.
3. Why this platform or idea can get past that limit (for TFLN: strong Pockels effect, low
   loss, wafer-scale fabrication), and what stood in the way until now.
4. "Here we demonstrate ..." — the device or system, the key numbers, and the validation
   (imaging of what, compared against what).

Do not review the whole field; cite reviews for that. Do not end with a section-by-section
outline in a letter or a Nature-family paper.

## Results (or the numbered sections of an Optica article)

A typical order for a chip-based OCT paper, one figure per step:

| Figure | Content | Purpose |
|---|---|---|
| 1 | Concept: system schematic, chip layout or micrograph, how the chip replaces the bulk parts | The reader sees the idea and the scale |
| 2 | Device design and simulation: cross-section, mode, dispersion or phase matching, design curves | Why these dimensions |
| 3 | Device characterization: loss, spectra, Q, EO response, Vπ, tuning | The device works as designed |
| 4 | System characterization: sweep or spectrum, linearity, PSF, axial resolution, sensitivity, roll-off | The OCT figures of merit |
| 5 | Imaging: phantom or standard target, then tissue or the real sample, with a reference system if there is one | It does the job |
| Table | Comparison with prior chip-based and benchtop systems, same metric definitions | Where this stands |

Each subsection: one sentence on what is being tested and why, the measurement in enough detail
to interpret the result, the result with numbers, and what it means for the next step. Lead
with the finding, not with "Figure 3 shows".

For a device-only paper, drop rows 4–5 and add a system-level demonstration that shows the
device doing something (data transmission, a sweep, a spectrum).

## Discussion and conclusion

- What limits the present performance and whether the limit is fundamental or engineering.
  Reviewers will raise it otherwise.
- The path to the next factor of improvement, tied to something specific (lower coupling loss
  with a mode converter, longer electrode, heterogeneous laser integration).
- The comparison table's message in one or two sentences.
- For OCT: what would be needed for in vivo or clinical use that this work has not shown
  (power on the sample, safety limits, speed, packaging).

The conclusion of an Optica article restates the result and its implication in a short
paragraph. Do not introduce new data there.

## Methods

Enough for a group with a similar cleanroom and lab to reproduce the work; the reporting
checklist lists the items. Fabrication, device characterization, system setup, signal
processing (k-linearization, dispersion compensation, windowing, averaging), imaging protocol
and sample handling each get a paragraph.

## Supplement

Derivations, extra device statistics, the full link budget, additional images, and
characterization that supports but does not carry the argument. Every supplementary item is
cited from the main text.

## Figure captions

- Optica: "Fig. 1. Title sentence. (a) What panel a shows. (b) ..." The title is a statement of
  content. Panels are referred to as (a), (b).
- Nature family: "Fig. 1 | Title." then "**a**, description. **b**, description." Define every
  symbol, scale bar, colour scale and error bar in the legend; say what n is.
- Science family: a short bold title sentence, then "(**A**) description. (**B**) ..."

A caption states what is plotted and under what conditions (wavelength, power, polarization,
averaging, dynamic range of an OCT image, scale-bar length). Interpretation belongs in the
text. Inset, abbreviation and colour meanings are spelled out even if the text repeats them.

## Cover letter

Three short paragraphs: what was done and the headline result; why it matters to this journal's
readers and what is new relative to the two or three closest papers, cited; any related
submissions, suggested or excluded reviewers, and confirmation that the work is not under
consideration elsewhere. Optica asks for about 250 words.
