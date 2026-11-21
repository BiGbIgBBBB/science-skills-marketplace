---
name: photonics-figure
description: >-
  Make publication and talk figures for integrated-photonics and OCT work with Python/matplotlib,
  sized and styled for Optica, Optics Letters, Optics Express, Nature, Nature Photonics, Nature
  Communications, Science and Science Advances. Use first for any plotting request from this
  user: 作图, 画图, 论文配图, 改图, transmission or resonance spectra, Q-factor fits, EO S21
  response, OCT A-scans, PSF and sensitivity roll-off, B-scans, noise spectra, mode profiles,
  multi-panel figures, or slide figures. Bundles a tested helper library (journal column widths,
  fonts, panel labels, export audit) and photonics plot recipes.
---

# Photonics figures

Figures for a researcher building OCT systems on thin-film lithium niobate photonic circuits.
The decisions below are already made; do not ask about them again.

| Decision | Default |
|---|---|
| Tool | Python + matplotlib. Not MATLAB, not R, not seaborn styling. |
| Language in figures | English, always, even when the conversation is in Chinese. |
| Journal | Whatever the user names; `optica` if they name none. Say which one you used. |
| Output | Vector PDF for the manuscript plus a 600 dpi PNG to look at. |
| Colour | The Okabe-Ito palette in `pubfig.PALETTE`; greyscale for OCT images on a dB scale. |

## Workflow

1. **Say what the figure has to show** in one sentence before writing code. That sentence
   decides which panel gets the most area and what gets annotated.
2. **Set the journal and build at final size.** Copy `scripts/pubfig.py` and
   `scripts/photonics_plots.py` next to the plotting script (or put the `scripts/` directory on
   `sys.path`). The figure is created at the width the journal prints, so font sizes in the code
   are the font sizes on the page.

   ```python
   import pubfig as pf, photonics_plots as pp
   pf.use("optica")                       # optica | oe | nature | ncomms | science | sciadv | slides
   fig, axs = pf.figure("full", aspect=0.45, ncols=3)
   fit = pp.plot_resonance(axs[0], wl_nm, t_linear)
   pp.plot_eo_response(axs[1], f_ghz, s21_db)
   pp.plot_bscan(axs[2], bscan_linear, width_mm=2.5, depth_mm=1.5, dynamic_range_db=40)
   pf.label_panels(axs)                   # (a) for Optica, bold a for Nature, bold A for Science
   pf.save(fig, "fig3_characterization")  # .pdf + .png at exact size, prints audit findings
   ```

3. **Use a recipe when one fits.** `references/recipes.md` lists them with the conventions each
   plot type follows (which dB, what to state in the caption). The `plot_*` functions return the
   numbers they annotate (Q, linewidth, 3-dB bandwidth, roll-off depth, axial resolution); reuse
   those numbers in the caption and text instead of reading them off the plot.
4. **Save with `pf.save`**, never `bbox_inches="tight"`: tight cropping changes the physical
   width and the fonts no longer match the journal. `pf.save` warns about a wrong width, text
   under the journal minimum, hairlines and clipped labels. Fix what it reports.
5. **Look at the PNG** before handing it over. Check for overlapping labels, legends on top of
   data, and anything unreadable at print size. Regenerate until it is clean.
6. **Hand over** the script, the PDF and the PNG, and state the journal preset and any number
   that came from a fit.

To retarget a figure, change the `pf.use(...)` line and rerun. To use the style without the
library, `python scripts/pubfig.py mplstyle optica > optica.mplstyle`.

## Rules that hold for every figure

- One figure width per journal column: `pf.figure("single" | "full" | ...)`. `python
  scripts/pubfig.py specs` prints the table; `references/journal-specs.md` gives the sources
  and the open questions. Check the journal's live author page before a final submission.
- Axis labels are `Quantity (unit)` in sentence case: `Wavelength (nm)`, `Transmission (dB)`,
  `Depth in air (mm)`. Use a real minus sign and µ, not a hyphen and "u".
- Never encode a series by colour alone when a figure has more than two: add line style,
  markers or direct labels. Optica asks for this explicitly.
- Images (B-scans, mode profiles, micrographs) get a scale bar rather than tick labels, square
  physical pixels, and a stated dynamic range or colour scale.
- Do not smooth, crop, window or drop data to make a plot look cleaner without saying so in the
  caption. Show measured points and the fit as separate artists.
- Synthetic or placeholder data must be labelled as such in the file name and the reply.

## When to reach for another skill

- `nature-skills:nature-figure` for the argument of a multi-panel figure (panel roles, evidence
  chain) and its QA scripts (panel alignment, text collision, PDF font audit). The backend is
  Python; do not ask the Python-or-R question.
- `sci-computing:matplotlib` for API details and unusual plot types.
- `sci-computing:scientific-visualization` for palette and export audits on finished files.
- `photonics-writing` for the caption and the Results paragraph that cites the figure.
- `sci-computing:uncertainty-and-units` when fitted values need an uncertainty budget.
