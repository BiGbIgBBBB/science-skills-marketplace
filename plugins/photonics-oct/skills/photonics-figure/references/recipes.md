# Plot recipes for PIC and OCT figures

All functions live in `scripts/photonics_plots.py` (imported as `pp`) and draw on an axes made
with `pubfig` (imported as `pf`). `python scripts/photonics_plots.py demo optica out/` renders
every recipe with synthetic data; run it after editing the library.

## Which dB

Getting this wrong is the most common error in the field, so the caption should say which one.

| Quantity | Conversion | Notes |
|---|---|---|
| Optical power, insertion loss, extinction | `pp.db(x)` = 10 log10 | |
| OCT A-scan and B-scan intensity | 10 log10 of intensity = 20 log10 of the FFT magnitude | Sensitivity and roll-off are quoted on this scale, so the "6-dB roll-off" is where the fringe amplitude has halved. |
| EO response measured on a VNA or LCA | `pp.db(x, power=False)` = 20 log10 \|S21\| | This is the electrical 3-dB bandwidth, where the modulation amplitude has dropped to 71%. Write "3-dB electro-optic bandwidth" and state the reference frequency. |
| RIN, phase noise | dBc/Hz | State the resolution bandwidth and whether the shot-noise limit is drawn. |

## Recipes

### Broadband transmission: `pp.plot_transmission(ax, wl_nm, t_db, frequency_axis=True)`
Wavelength in nm on the bottom axis and optical frequency in THz on top. Use a thin line
(0.5 pt) for dense resonance combs. Caption: on-chip or fibre-to-fibre, polarization (TE/TM),
laser step or OSA resolution, and how the spectrum was normalized.

### Single resonance and Q: `pp.plot_resonance(ax, wl_nm, t_linear)`
Fits a Lorentzian dip and returns `wl0_nm`, `fwhm_pm`, `linewidth_ghz`, `extinction_db`,
`q_loaded` with its fit uncertainty, and two intrinsic-Q candidates. A single transmission scan
cannot tell under- from over-coupling, so report `q_intrinsic_undercoupled` or
`q_intrinsic_overcoupled` only with the evidence for the regime (gap sweep, phase response).
Data are grey points and the fit is a line, so the reader sees both. For split or Fano
resonances this model is wrong; fit the right one and say so.

Loss from intrinsic Q: α = 2π n_g / (Q_i λ0), and α[dB/cm] = 4.343 × α[cm⁻¹].

### Electro-optic response: `pp.plot_eo_response(ax, f_ghz, s21_db, log_x=False)`
Normalizes to the low-frequency value, draws the −3 dB line and returns
`bandwidth_3db_ghz` (nan when the response never crosses −3 dB; then write "> f_max" in the
text). Caption: reference frequency, whether the photodetector and probe response were
de-embedded, electrode length, termination.

### OCT point-spread function: `pp.plot_psf(ax, depth_um, ascan_linear)`
Linear scale, FWHM marked, returns `axial_resolution_um`. State whether depth is in air or in
tissue (divide by the group index, about 1.38 for soft tissue) and which spectral window was
applied, since the window sets both the width and the sidelobes.

Theory for a Gaussian spectrum: δz = (2 ln 2 / π) λ0² / Δλ, with Δλ the FWHM bandwidth.

### Sensitivity roll-off: `pp.plot_rolloff(ax, depth_mm, ascans_db, floor_db=-60)`
PSFs from a mirror at several path differences on one dB axis, coloured by depth, with the peak
envelope and the 6-dB roll-off depth. Normalize so the shallowest peak is 0 dB, or plot
absolute sensitivity if the attenuation is calibrated. Caption: sample-arm power, attenuation
used, A-scan rate, number of averages. Returns `rolloff_6db_mm`.

Sampling-limited range: z_max = λ0² / (4 δλ), with δλ the spectral sampling interval.

### B-scan: `pp.plot_bscan(ax, intensity, width_mm, depth_mm, dynamic_range_db=40)`
Greyscale on a dB scale with a fixed dynamic range, square physical pixels, a scale bar and a
dB colour bar. The top of the display window is the 99.9th percentile unless `ceiling_db` is
given. Use the same `dynamic_range_db` and `ceiling_db` for every image being compared, and
give the dynamic range in the caption. Scale bars in tissue should say whether they assume a
refractive index.

### Noise spectra: `pp.plot_noise(ax, f_hz, psd_db, ylabel="RIN (dBc/Hz)")`
Log frequency axis with decade ticks. Overlay the shot-noise or instrument floor as a dashed
grey line with `pf.annotate_level`.

### Mode profile: `pp.plot_mode(ax, x_um, y_um, intensity, outlines=[...])`
Normalized |E|² in the `magma` map with the waveguide cross-section drawn in white and a µm
scale bar. Caption: wavelength, polarization, film thickness, etch depth, sidewall angle,
cladding, and the solver.

## Helpers in `pubfig`

| Call | Use |
|---|---|
| `pf.frequency_axis(ax)` | THz axis on top of a wavelength axis. |
| `pf.detuning_axis(ax, center_nm)` | GHz detuning on top of a narrow wavelength scan. |
| `pf.scalebar(ax, length, "0.5 mm")` | Scale bar in data units; hides the ticks. |
| `pf.colorbar(im, ax, "Intensity (dB)")` | Colour bar matched to the axes height. |
| `pf.annotate_level(ax, -3, "−3 dB")` | Dashed reference level with a label. |
| `pf.label_panels(axs)` | Panel labels in the journal's style. |
| `pf.audit(fig)` | The checks `pf.save` runs, as a list of strings. |
| `pf.PALETTE`, `pf.CMAPS` | Named colours and the colormap for each role. |

## Plot types without a recipe yet

Follow the same conventions and add a function to `photonics_plots.py` when one recurs.

- **Sweep linearity / instantaneous frequency**: time on x, optical frequency or wavelength on
  y, residual from a linear fit in a second panel with its RMS value.
- **Spectrogram or depth-resolved spectrum**: `viridis`, colour bar in dB, both axes labelled
  with units.
- **Vπ measurement**: optical output against drive voltage with a sin² fit; report Vπ and
  Vπ·L in V·cm, and the drive frequency.
- **En-face or volume OCT**: same dB window as the B-scans in the figure; mark where the B-scan
  was taken.
- **Dispersion**: integrated dispersion D_int/2π in GHz against mode number, or GVD in
  fs²/mm against wavelength, with the zero line drawn.
- **Benchmark comparison**: a scatter of the two figures of merit that matter (for example
  Vπ·L against bandwidth), log axes when the range needs it, this work marked with a filled
  star, every other point labelled with its reference number.
