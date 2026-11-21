# Science Skills Marketplace

A personal [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
for integrated-photonics (thin-film lithium niobate) and OCT research. It has one hand-written
plugin that holds my own defaults for figures and papers, and three plugins with a curated
subset of skills from:

- [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) (MIT)
- [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) (Apache-2.0)

A GitHub Action (`.github/workflows/sync.yml`) pulls the selected upstream skills every day and
bumps a plugin's version whenever its content changed, so Claude Code picks up the update.

## Plugins

34 skills in four plugins.

### `photonics-oct` (written here, not synced)

| Skill | What it does |
|---|---|
| `photonics-figure` | Entry point for any plot. Python/matplotlib at the exact column width of Optica, Optics Express, Nature, Nature Communications, Science or Science Advances, with the right fonts and panel labels, an export audit, and tested recipes for transmission spectra, resonance/Q fits, EO response, OCT PSF and roll-off, B-scans, noise spectra and mode profiles. |
| `photonics-writing` | Entry point for any paper task. LaTeX defaults, journal limits and structure, photonics and OCT terminology (including Chinese-to-English pitfalls), a reporting checklist, a `siunitx` preamble, and a routing table to the general writing skills below. |

The two libraries can be used directly:

```python
import pubfig as pf, photonics_plots as pp   # plugins/photonics-oct/skills/photonics-figure/scripts
pf.use("optica")
fig, ax = pf.figure("single", aspect=0.72)
fit = pp.plot_resonance(ax, wavelength_nm, transmission_linear)
pf.save(fig, "fig2_resonance")               # PDF + PNG at exact size, with an audit
```

### Synced from upstream

| Plugin | Skills |
|---|---|
| `sci-computing` (K-Dense) | matplotlib, scientific-visualization, sympy, uncertainty-and-units, statistical-analysis, qutip, qiskit, pennylane, scikit-learn, pytorch-lightning, pymoo, optimize-for-gpu, lab-hardware-cad |
| `sci-research-writing` (K-Dense) | literature-review, paper-lookup, citation-management, pyzotero, research-grants, venue-templates, latex-posters, scientific-slides, scientific-brainstorming |
| `nature-skills` | nature-writing, nature-polishing, nature-figure, nature-data, nature-ref-verifier, nature-reviewer, nature-response, nature-paper-xray, nature-reader (+ `nature-shared`, required by the others) |

The exact list is in [`sources.json`](sources.json); the pinned upstream commits and content
hashes are in [`sources.lock.json`](sources.lock.json).

## Install

In Claude Code:

```
/plugin marketplace add BiGbIgBBBB/science-skills-marketplace
/plugin install photonics-oct@jfang-science-skills
/plugin install sci-computing@jfang-science-skills
/plugin install sci-research-writing@jfang-science-skills
/plugin install nature-skills@jfang-science-skills
```

### Turn on auto-update

Auto-update is off by default for third-party marketplaces. Run `/plugin`, go to
**Marketplaces**, select `jfang-science-skills`, and choose **Enable auto-update**. Claude Code
then refreshes the marketplace at startup and installs new plugin versions. To update by hand,
run `/plugin marketplace update jfang-science-skills`.

If the repo is private, Claude Code needs Git access to it (for background auto-update, set
`GITHUB_TOKEN` in your environment).

## Change what is included

**Upstream skills.** Edit the `skills` arrays in `sources.json` and push to `main`. The
workflow runs on that push, daily, or by hand from the Actions tab. Files under
`plugins/sci-computing`, `plugins/sci-research-writing` and `plugins/nature-skills` are
overwritten on every sync, so do not edit them by hand. A per-skill `exclude` list drops bulky
upstream files (it currently removes 30 MB of example images from `nature-figure`). If a skill
is renamed or removed upstream, the sync prints a warning and leaves it out.

Skills that were removed in the November 2026 clean-up and can be added back by name:

- K-Dense: seaborn, matlab, statsmodels, statistical-power, pymc, exploratory-data-analysis,
  experimental-design, dask, polars, zarr-python, get-available-resources, markitdown, liteparse,
  scientific-writing, peer-review, scholar-evaluation, research-lookup, hypothesis-generation,
  scientific-critical-thinking, scientific-schematics, markdown-mermaid-writing, pptx-posters
- nature-skills: nature-statistics, nature-citation, nature-academic-search,
  nature-literature-pipeline, nature-paper-card, nature-paper-trans, nature-paper2ppt,
  nature-image2ppt, nature-paper2word, nature-proposal-writer, nature-paper-to-patent,
  nature-experiment-log

**My own skills.** Edit the files under `plugins/photonics-oct/skills/` and push to `main`; the
workflow bumps the plugin version. After changing the plotting library, run its regression demo:

```
python3 plugins/photonics-oct/skills/photonics-figure/scripts/photonics_plots.py demo optica /tmp/demo
```

To run the sync locally:

```
python3 scripts/sync.py            # fetch upstreams and rebuild
python3 scripts/sync.py --offline  # refresh the local plugin's version and the manifests only
```

## Licenses

Each synced plugin directory includes the upstream license as `UPSTREAM_LICENSE`; those skills
belong to their original authors. `photonics-oct` is MIT.
