# Terminology, symbols and units

Pick one form per term and hold it for the whole manuscript. The forms below are the ones most
used in Optica-family and Nature Photonics papers. When the user's draft consistently uses
another, keep theirs.

## Terms

| Write | Not | Note |
|---|---|---|
| thin-film lithium niobate (TFLN) | LNOI and TFLN mixed | "lithium niobate on insulator (LNOI)" is fine if used alone throughout. Hyphenate "thin-film" before a noun. |
| photonic integrated circuit (PIC) | photonics integrated circuit | |
| electro-optic (EO) | electrooptic, electro-optical | |
| half-wave voltage $V_\pi$, voltage–length product $V_\pi L$ | "Vpi" | Give $V_\pi L$ in V·cm and say DC or the RF frequency. |
| optical coherence tomography (OCT) | | Define in the abstract and again in the text. |
| swept-source OCT (SS-OCT), spectral-domain OCT (SD-OCT) | Fourier-domain when the type is known | "Fourier-domain OCT" covers both. |
| A-scan, B-scan, en face | A-line and A-scan mixed | "A-scan rate" in kHz, "en face image". |
| axial resolution, lateral resolution | depth resolution | Say "in air" or "in tissue (n = 1.38)". |
| sensitivity | SNR, when the minimum detectable reflectivity is meant | Sensitivity is the sample reflectivity giving SNR = 1, in dB. |
| sensitivity roll-off, 6-dB roll-off depth | fall-off | |
| imaging range, imaging depth | | Sampling sets the range and the sample sets the depth. Do not swap them. |
| insertion loss (fibre-to-fibre), on-chip loss, coupling loss per facet | "loss" unqualified | |
| propagation loss | waveguide loss | In dB/cm, with the method (cut-back, resonator Q). |
| loaded Q ($Q_\mathrm{L}$), intrinsic Q ($Q_\mathrm{i}$) | "Q factor" unqualified | |
| 3-dB electro-optic bandwidth | 3-dB bandwidth unqualified | See dB conventions below. |
| extinction ratio | contrast | In dB. Say DC or dynamic. |
| free spectral range (FSR) | | In GHz or nm. Say which. |
| TE, TM (fundamental: TE$_0$) | quasi-TE on every use | Define once as quasi-TE if needed. |
| x-cut, z-cut | X-cut | |
| wavelength-swept laser, swept source | sweeping laser | "sweep rate" in kHz, "sweep range" in nm. |

Compound modifiers take a hyphen before the noun and none after it: "a 3-dB bandwidth of
40 GHz" and "the bandwidth is 3 dB down", "a low-loss waveguide", "the waveguide is low loss".

## dB conventions

- Optical power ratios: 10 log10. OCT image intensity: 10 log10 of intensity, which equals
  20 log10 of the interference amplitude.
- A 6-dB drop in OCT signal means the fringe amplitude has halved.
- EO S21 from a vector network analyser or lightwave component analyser is electrical:
  20 log10. Its 3-dB point is where the modulation amplitude falls to 71%. If a paper being
  compared against quotes an optical 3-dB (electrical 6-dB) bandwidth, convert before comparing
  and say so.
- dB is a ratio and dBm is power referred to 1 mW. Losses are in dB, powers in dBm.
- Write "−3 dB" with a minus sign for a level and "3-dB bandwidth" for the modifier.

## Symbols

| Quantity | Symbol | Unit |
|---|---|---|
| centre wavelength | $\lambda_0$ | nm |
| FWHM optical bandwidth | $\Delta\lambda$ | nm |
| spectral sampling interval | $\delta\lambda$ | pm |
| axial resolution | $\delta z$ | µm |
| imaging range | $z_\mathrm{max}$ | mm |
| group index, effective index | $n_\mathrm{g}$, $n_\mathrm{eff}$ | |
| propagation loss | $\alpha$ | dB/cm |
| half-wave voltage | $V_\pi$ | V |
| EO coefficient | $r_{33}$ | pm/V |
| A-scan rate | $f_\mathrm{A}$ | kHz |

Variables are italic. Descriptive subscripts are upright (`n_\mathrm{eff}`, `Q_\mathrm{L}`,
`z_\mathrm{max}`), and subscripts that are themselves variables stay italic (`V_\pi`, `r_{33}`).
Units are upright with a thin space, which `siunitx` handles.

## Relations worth getting right

State which one was used when a number in the paper is "theoretical".

- Axial resolution for a Gaussian spectrum, in air:
  $\delta z = \dfrac{2\ln 2}{\pi}\,\dfrac{\lambda_0^2}{\Delta\lambda}$. Divide by $n$ for tissue.
- Sampling-limited imaging range:
  $z_\mathrm{max} = \dfrac{\lambda_0^2}{4\,n\,\delta\lambda}$.
- Loaded Q from a resonance: $Q_\mathrm{L} = \lambda_0/\Delta\lambda_\mathrm{FWHM}$.
- Intrinsic Q from loaded Q and the normalized on-resonance transmission $T_0$:
  $Q_\mathrm{i} = 2Q_\mathrm{L}/(1 \pm \sqrt{T_0})$, plus for under-coupling and minus for
  over-coupling.
- Loss from intrinsic Q: $\alpha = 2\pi n_\mathrm{g}/(Q_\mathrm{i}\lambda_0)$ in inverse length.
  multiply by 4.343 for dB per the same length.
- Wavelength to frequency span: $\Delta\nu = c\,\Delta\lambda/\lambda_0^2$.

## Numbers

- Significant figures follow the measurement: a Q of $1.2\times10^6$, not 1,213,442.
- Give uncertainty where it exists: `\qty{0.21 \pm 0.03}{\dB\per\cm}`, and say what the ± is
  (standard deviation over N devices, fit uncertainty).
- "≈" for a rounded measured value, "~" only for order of magnitude.
- Ranges with an en dash and one unit: 1260–1360 nm.
- Spell out numbers below ten when they are counts without units ("three devices"), and use
  numerals with units ("3 mm").

## Chinese to English

Common renderings that come out wrong in direct translation:

| Chinese | Use | Avoid |
|---|---|---|
| 铌酸锂薄膜 | thin-film lithium niobate | lithium niobate thin film (as the platform name) |
| 半波电压 | half-wave voltage | half wave voltage, π voltage |
| 插入损耗 / 传输损耗 | insertion loss / propagation loss | transmission loss |
| 扫频光源 | swept source, wavelength-swept laser | sweep frequency light source |
| 灵敏度滚降 | sensitivity roll-off | sensitivity decline |
| 成像深度 / 成像量程 | imaging depth / imaging range | |
| 轴向分辨率 / 横向分辨率 | axial resolution / lateral resolution | longitudinal, horizontal |
| 片上 | on-chip (modifier), on chip (after the noun) | on the chip |
| 调制带宽 | modulation bandwidth, EO bandwidth | modulating bandwidth |
| 消光比 | extinction ratio | |
| 相干长度 | coherence length | coherent length |
| 实现了 | "we demonstrated", "the device achieved", or just state the result in the past tense | "we realize", "is realized", "we demonstrate" |
| 具有重要意义 | say what it enables, with a number | "is of great significance" |
