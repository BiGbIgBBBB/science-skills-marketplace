# House style

Two rules from the PI's review of a manuscript draft (November 2026). They apply to every
piece of manuscript text written or edited for this user: papers, abstracts, captions,
Supplements, cover letters, responses to reviewers, conference summaries and proposals. They
override any other skill's guidance, including `academic-humanizer`, which allows semicolons
in moderation.

The PI's words:

> Get rid of all semicolons and where needed rewrite to remove. Some are unnecessary, but
> overall they scream AI generated.
>
> Change results to past tense when describing any experimental work.

`scripts/check_style.py` checks both. Run it on every draft before handing it over.

## Rule 1: no semicolons

Not one, anywhere in the prose. That includes captions, tables written as sentences,
the cover letter and the response to reviewers. Semicolons inside math (`$f(x;\theta)$`), code,
URLs and the reference list are not prose and are left alone. The checker skips them.

Removing the semicolon is not enough. Rewrite the sentence so it reads as if it never had one.
Pick the repair by what the semicolon was doing:

| The semicolon joined | Repair | Before | After |
|---|---|---|---|
| Two complete thoughts | Two sentences | The ring was undercoupled; its intrinsic Q was $2.1\times10^6$. | The ring was undercoupled. Its intrinsic Q was $2.1\times10^6$. |
| A claim and its reason | "because", "since" | The loss was low; the sidewalls were smooth. | The loss was low because the sidewalls were smooth. |
| A contrast | "but", "whereas", "while" | The 5-mm device reached 67 GHz; the 20-mm device reached 4.5 GHz. | The 5-mm device reached 67 GHz, whereas the 20-mm device reached 4.5 GHz. |
| A consequence | "so", "which", or a new sentence with "This" + noun | The sweep was linear to 0.1%; no k-clock was needed. | The sweep was linear to 0.1%, so no k-clock was needed. |
| A second point that adds little | Delete it, or fold it into a phrase | The chip was packaged; packaging is described in Supplement 1. | The chip was packaged (Supplement 1). |
| Items of a list that contain commas | Split into sentences, or number them with (i), (ii) and commas | We report (i) a laser, tunable over 100 nm; (ii) a modulator... | We report a laser tunable over 100 nm and a modulator with... |
| Panel descriptions in a caption | Periods | (a) Layout; (b) micrograph; (c) spectrum. | (a) Layout. (b) Micrograph. (c) Transmission spectrum. |
| A "however" or "therefore" clause | Period before it | The bandwidth was 40 GHz; however, Vπ rose to 4 V. | The bandwidth was 40 GHz. However, Vπ rose to 4 V. |

Do not swap a semicolon for an em dash or a colon by reflex. Both read as the same tell. Use a
colon only to introduce a list or a defined term, and keep em dashes out of the prose.

## Rule 2: experimental results in the past tense

Anything that happened in the lab, in the cleanroom or in a simulation run is reported in the
past tense. That covers what was made, what was measured, what was observed, what values came
out, how they compared, and what the simulations returned.

| Use the past tense for | Example |
|---|---|
| Fabrication and setup | The waveguides were patterned by electron-beam lithography. |
| Measurement procedure | We swept the laser from 1500 to 1600 nm and recorded the transmission. |
| Measured values | The propagation loss was 0.21 ± 0.03 dB/cm. |
| Observations | The B-scans showed the epidermis–dermis boundary. |
| Comparisons made in this work | The chip-based system matched the benchtop reference within 1 dB. |
| Simulation results | The simulated mode had an effective index of 1.89. |
| Results in the abstract and the conclusion | The modulator achieved a 3-dB electro-optic bandwidth beyond 67 GHz. |

The present tense stays where it is correct, and the checker does not flag these:

| Keep the present tense for | Example |
|---|---|
| What the paper, a figure or a table contains | Figure 3(a) shows the transmission spectrum. This Letter reports a chip-scale swept source. |
| Established physics and prior knowledge | Lithium niobate has a large Pockels coefficient. |
| Design facts that remain true of the device | The ring has a radius of 100 µm. |
| Interpretation and implication drawn from the results | These results indicate that sidewall scattering dominates the loss. |
| Statements about other groups' published work | Prior thin-film modulators reach 100 GHz [12]. |

When one sentence mixes the two, let the figure pointer be present and the result past, or
split it: "Figure 3(b) shows the EO response. The 3-dB bandwidth was 67 GHz."

Openers that break the rule and their repairs:

| Avoid | Write |
|---|---|
| Here we demonstrate a... | Here we report a ..., which achieved ... / We demonstrated a ... |
| We show that the loss is... | We found that the loss was... / The measured loss was... |
| The device exhibits / achieves / shows ... | The device exhibited / achieved / showed ... |
| The measured Vπ is 2.1 V. | The measured Vπ was 2.1 V. |
| The Q is extracted from a Lorentzian fit. | We extracted the Q from a Lorentzian fit. |
| The ring has a loaded Q of ... | The ring had a loaded Q of ... / The loaded Q was ... |
| Results show that ... | The measurements showed that ... |

Methods are experimental work, so the Methods are in the past tense too, apart from design
facts and definitions ("$Q_\mathrm{L} = \lambda_0/\Delta\lambda$").

## Running the checker

```bash
python3 scripts/check_style.py main.tex sections/*.tex
```

```bash
python3 scripts/check_style.py --json draft.md
```

For text written in the chat rather than a file, pipe it in and pass `-` as the file name.

- **ERROR semicolon**: every one must go. The exit status is 1 while any remain.
- **check tense**: a candidate, not a verdict. Rewrite it unless it falls under "keep the
  present tense" above. Expect a few correct present-tense sentences in every paper.

The checker is a heuristic. It does not see a present-tense result that uses a verb or a
subject outside its lists, so read the Results and the abstract once more for tense after it
passes.
