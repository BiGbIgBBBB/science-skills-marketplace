# Science Skills Marketplace

A personal [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) with curated skills for photonics / OCT / quantum research and scientific writing, taken from:

- [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) (MIT)
- [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) (Apache-2.0)
- [AIScientists-Dev/academic-humanizer](https://github.com/AIScientists-Dev/academic-humanizer) (MIT), synced into `sci-research-writing`
- [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) (CC-BY-NC-4.0, **non-commercial only**), referenced as an external plugin `academic-research-skills` (not copied; it needs its own `shared/`, `scripts/` and hooks)

A GitHub Action (`.github/workflows/sync.yml`) pulls the selected skills from both upstreams **every day** and bumps the plugin version whenever anything changed, so Claude Code picks up the update.

## Plugins

| Plugin | Source | Contents |
|---|---|---|
| `sci-computing` | K-Dense | matplotlib, scientific-visualization, seaborn, sympy, matlab, uncertainty-and-units, optimize-for-gpu, qutip, qiskit, pennylane, statistics, scikit-learn, pytorch-lightning, pymoo, pymc, dask, polars, zarr, experimental-design, lab-hardware-cad, markitdown, liteparse … |
| `sci-research-writing` | K-Dense + academic-humanizer | scientific-writing, literature-review, citation-management, paper-lookup, pyzotero, peer-review, research-grants, venue-templates, LaTeX/PPTX posters, slides, schematics, hypothesis generation, critical thinking, **academic-humanizer** … |
| `nature-skills` | nature-skills | nature-writing, polishing, figure, statistics, data, citation, ref-verifier, reviewer, response, paper-xray/card/reader/trans, paper2ppt, paper2word, proposal-writer, paper-to-patent, experiment-log (+ `nature-shared`, required by the others) |

The exact list is in [`sources.json`](sources.json); the pinned upstream commits are in [`sources.lock.json`](sources.lock.json).

## Install

In Claude Code:

```
/plugin marketplace add BiGbIgBBBB/science-skills-marketplace
/plugin install sci-computing@jfang-science-skills
/plugin install sci-research-writing@jfang-science-skills
/plugin install nature-skills@jfang-science-skills
/plugin install academic-research-skills@jfang-science-skills
```

### Turn on auto-update

Auto-update is off by default for third-party marketplaces. Run `/plugin`, go to **Marketplaces**, select `jfang-science-skills`, and choose **Enable auto-update**. Claude Code then refreshes the marketplace at startup and installs new plugin versions. To update by hand, run `/plugin marketplace update jfang-science-skills`.

If the repo is private, Claude Code needs Git access to it (for background auto-update, set `GITHUB_TOKEN` in your environment).

## Add or remove skills

Edit the `skills` arrays in `sources.json` and push. The workflow runs on that push, as well as daily or by hand from the Actions tab. To run it locally:

```
python3 scripts/sync.py
```

If a skill is renamed or removed upstream, the sync prints a warning and leaves it out.

## Licenses

Each plugin directory includes the upstream license as `UPSTREAM_LICENSE`. The skills belong to their original authors.
