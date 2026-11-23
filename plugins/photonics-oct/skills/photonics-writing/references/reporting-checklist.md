# Reporting checklist

What a reviewer of an integrated-photonics or OCT paper expects to find. Use it two ways: to
list what to ask the user for before drafting Methods, and to audit a finished draft. Mark
each item as present, missing, or not applicable. Never fill a missing item with a typical
value.

## Chip and fabrication

- Platform: material, crystal cut (x-cut, z-cut), film thickness, buried-oxide thickness,
  substrate, wafer supplier.
- Waveguide geometry: top width, etch depth, slab thickness, sidewall angle, cladding material
  and thickness.
- Process: lithography (e-beam or stepper, resist), etch chemistry, cleaning, annealing,
  cladding deposition, metallization (metal, thickness, lift-off or plating), facet preparation.
- Electrodes: gap, signal width, length, thickness, type (lumped, travelling-wave, segmented),
  termination.
- Where it was made (in-house cleanroom, foundry run).
- How many chips and devices were made and measured, and how the reported one was chosen.

## Passive characterization

- Wavelength range and polarization.
- Insertion loss, with the definition (fibre-to-fibre or on-chip) and the coupling loss per
  facet, including how it was separated out (cut-back, loop-back, reference waveguide).
- Propagation loss and method. For a Q-based value: resonator type and radius, loaded Q,
  coupling regime and the evidence for it, group index used.
- Spectra: source and detector (tunable laser step, OSA resolution), normalization.
- Optical power in the waveguide for any power-dependent or photorefractive effect.

## Electro-optic characterization

- Vπ and Vπ·L: DC or at what frequency, waveform, how extracted.
- EO bandwidth: instrument, frequency range, calibration and de-embedding (probes, cables,
  photodetector), reference frequency, electrical or optical dB.
- RF properties when relevant: characteristic impedance, microwave index, RF loss, S11.
- Extinction ratio (static, dynamic), bias point and bias-drift behaviour over time.
- Tuning efficiency (pm/V or GHz/V) and tuning speed for tunable devices.

## Light source and sweep (swept-source systems)

- Centre wavelength, sweep range (full and FWHM), sweep rate, duty cycle, sweep direction.
- Output power, on chip and in fibre.
- Instantaneous linewidth or coherence length and how it was measured.
- Sweep linearity and how k-clock or resampling was done.
- Noise: RIN over the detection band, and whether balanced detection is used.

## OCT system performance

- Configuration: SS or SD, interferometer type, reference-arm design, what is on chip and what
  is off chip.
- Power on the sample.
- Axial resolution: measured FWHM, in air and in tissue, spectral window, theoretical value.
- Lateral resolution: objective, beam diameter, and whether measured or calculated.
- Sensitivity: value, how measured (mirror plus calibrated attenuation), sample power and
  A-scan rate at which it was measured, and the shot-noise limit for comparison.
- Roll-off: 6-dB depth, and the imaging range set by sampling.
- A-scan rate, B-scan and volume size, and acquisition time.
- Detection: detector bandwidth, digitizer rate and bit depth.
- Processing: background subtraction, k-linearization, dispersion compensation, windowing,
  averaging or registration, and whether images are single-frame.

## Imaging

- Sample: what it is, preparation, for tissue the source and the ethics approval or consent
  statement.
- For in vivo imaging: power on the sample and the exposure standard it is compared against
  (ANSI Z136.1 or IEC 60825-1), with the limit that applies.
- Scan protocol and field of view. Scale bars in every image, with the refractive index
  assumed for depth.
- Display: dB scale, dynamic range, same window for images being compared.
- Reference comparison: the system compared against and its settings.

## Statistics and uncertainty

- For any value given as mean ± spread: N, what varied (devices, chips, repeated scans), and
  whether the spread is a standard deviation or a standard error.
- For fitted values: the model, the fit range and the uncertainty.
- For "typical" or "best" devices: say which it is.

## Comparison table

- The same metric definitions down every column, with conversions noted.
- Prior work chosen by relevance, including the results that outperform this one on some axis.
- Wavelength band stated for each entry, since performance is not comparable across bands.

## Before submission

- Data availability statement that says where the data are, not "available on request" where
  the journal disallows it.
- Code availability for processing that affects the images.
- Funding, author contributions, competing interests (including patents filed on the work).
- Any figure reused or adapted from earlier work has permission and a credit line.
- Supplementary items all cited from the main text.
