#!/usr/bin/env python3
"""pubfig - journal-sized matplotlib figures for photonics / OCT papers.

Copy this file next to the plotting script (or add its directory to sys.path):

    import pubfig as pf
    pf.use("optica")                              # or "oe", "nature", "ncomms", "science", "sciadv", "slides"
    fig, axs = pf.figure("single", aspect=0.7, ncols=2)
    ...
    pf.label_panels(axs)
    pf.save(fig, "fig2_transmission")             # fig2_transmission.pdf + .png, exact physical size

Command line:

    python pubfig.py specs                        # print the journal table
    python pubfig.py mplstyle optica > optica.mplstyle

The journal numbers live in JOURNALS below and are documented, with sources, in
../references/journal-specs.md. Journals revise their guidelines; re-check the
official author page before a final submission.
"""
from __future__ import annotations

import string
import sys
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.transforms import ScaledTranslation

MM = 1 / 25.4  # inches per millimetre
C_NM_THZ = 299_792.458  # c in nm*THz: f[THz] = C_NM_THZ / lambda[nm]

# Okabe-Ito colour-blind-safe palette, ordered so the first two (blue, vermilion)
# also separate in greyscale. Use these names in plotting code.
PALETTE = {
    "blue": "#0072B2",
    "vermilion": "#D55E00",
    "green": "#009E73",
    "orange": "#E69F00",
    "sky": "#56B4E9",
    "purple": "#CC79A7",
    "black": "#000000",
    "grey": "#7F7F7F",
}
CYCLE = [PALETTE[k] for k in ("blue", "vermilion", "green", "orange", "sky", "purple", "black")]

# Colormaps by role. All perceptually uniform or the field convention.
CMAPS = {
    "oct": "gray",          # OCT B-scans / en-face: greyscale on a dB scale
    "sequential": "viridis",  # spectrograms, intensity maps
    "field": "magma",       # optical mode |E|^2
    "diverging": "RdBu_r",  # signed quantities (Re E, phase error, dispersion sign)
    "phase": "twilight",    # cyclic phase
}

# Widths and heights in mm. "label" is the panel-label style: (format, weight, size in pt).
# "any_width": the journal accepts any width up to the largest one listed.
# Provenance and open questions for every number: ../references/journal-specs.md
JOURNALS = {
    "optica": {
        "name": "Optica / Optics Letters / Photonics Research (two-column opticajnl template)",
        "widths": {"single": 88.0, "full": 184.0},
        "max_height": 230.0,
        "font": 8.0, "font_min": 6.0, "line_min": 0.25,
        "label": ("({})", "normal", 8.0),
    },
    "oe": {
        "name": "Optics Express / Biomedical Optics Express (single-column optica-article template)",
        "widths": {"small": 84.0, "single": 108.0, "full": 133.0}, "any_width": True,
        "max_height": 200.0,
        "font": 8.0, "font_min": 6.0, "line_min": 0.25,
        "label": ("({})", "normal", 8.0),
    },
    "nature": {
        "name": "Nature / Nature Photonics",
        "widths": {"single": 89.0, "onehalf": 120.0, "full180": 180.0, "full": 183.0},
        "max_height": 170.0,
        "font": 7.0, "font_min": 5.0, "line_min": 0.25,
        "label": ("{}", "bold", 8.0),
    },
    "ncomms": {
        "name": "Nature Communications / Light: Science & Applications",
        "widths": {"single": 88.0, "full": 180.0},
        "max_height": 225.0,
        "font": 7.0, "font_min": 5.0, "line_min": 0.25,
        "label": ("{}", "bold", 8.0),
    },
    "science": {
        "name": "Science",
        "widths": {"single": 57.0, "double": 121.0, "full": 184.0},
        "max_height": 215.0,
        "font": 7.0, "font_min": 6.0, "line_min": 0.5,
        "label": ("{}", "bold", 9.0), "label_upper": True,
    },
    "sciadv": {
        "name": "Science Advances",
        "widths": {"single": 90.0, "full": 184.0}, "any_width": True,
        "max_height": 199.0,
        "font": 8.0, "font_min": 6.0, "line_min": 0.5,
        "label": ("{}", "bold", 9.0), "label_upper": True,
    },
    "slides": {
        "name": "Talk slides (16:9, 13.33 x 7.5 in)",
        "widths": {"half": 150.0, "full": 310.0}, "any_width": True,
        "max_height": 150.0,
        "font": 16.0, "font_min": 12.0, "line_min": 0.75,
        "label": ("({})", "normal", 18.0),
    },
}

_current = "optica"


def _rc(spec):
    f = spec["font"]
    slides = f >= 12
    lw = 1.8 if slides else 1.0
    return {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "Nimbus Sans", "DejaVu Sans"],
        "font.size": f,
        "axes.labelsize": f, "axes.titlesize": f,
        "xtick.labelsize": f - (2 if slides else 1), "ytick.labelsize": f - (2 if slides else 1),
        "legend.fontsize": f - (2 if slides else 1),
        "mathtext.default": "regular", "mathtext.fontset": "dejavusans",
        "axes.linewidth": 1.2 if slides else 0.6,
        "axes.prop_cycle": mpl.cycler(color=CYCLE),
        "axes.axisbelow": True,
        "axes.formatter.useoffset": False,  # no "+1.55e3" offsets on narrow wavelength scans
        "lines.linewidth": lw, "lines.markersize": 6 if slides else 3,
        "xtick.direction": "in", "ytick.direction": "in",
        "xtick.top": True, "ytick.right": True,
        "xtick.major.width": 1.2 if slides else 0.6, "ytick.major.width": 1.2 if slides else 0.6,
        "xtick.minor.width": 0.9 if slides else 0.5, "ytick.minor.width": 0.9 if slides else 0.5,
        "xtick.major.size": 5 if slides else 3, "ytick.major.size": 5 if slides else 3,
        "xtick.minor.size": 3 if slides else 1.5, "ytick.minor.size": 3 if slides else 1.5,
        "legend.frameon": False, "legend.handlelength": 1.6,
        "image.cmap": CMAPS["sequential"], "image.interpolation": "nearest",
        "figure.dpi": 150, "savefig.dpi": 600,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "figure.constrained_layout.use": True,
    }


def use(journal="optica"):
    """Apply the style for a journal and remember it for figure()/label_panels()/save()."""
    global _current
    if journal not in JOURNALS:
        raise ValueError(f"unknown journal {journal!r}; choose from {sorted(JOURNALS)}")
    _current = journal
    mpl.rcParams.update(_rc(JOURNALS[journal]))
    return JOURNALS[journal]


def spec(journal=None):
    return JOURNALS[journal or _current]


def figure(width="single", aspect=0.75, height_mm=None, nrows=1, ncols=1, journal=None, **kwargs):
    """Create a figure at the exact physical size the journal prints.

    width      a key of the journal's widths ("single", "full", ...) or a number in mm
    aspect     height / width of the whole figure (ignored when height_mm is given)
    Returns (fig, axes) exactly like plt.subplots.
    """
    s = spec(journal)
    w_mm = s["widths"][width] if isinstance(width, str) else float(width)
    h_mm = height_mm if height_mm is not None else w_mm * aspect
    if h_mm > s["max_height"]:
        warnings.warn(f"figure height {h_mm:.0f} mm exceeds the {s['max_height']:.0f} mm page limit for {s['name']}")
    return plt.subplots(nrows, ncols, figsize=(w_mm * MM, h_mm * MM), **kwargs)


def label_panels(axes, labels=None, journal=None, dx_pt=None, dy_pt=3.0):
    """Put panel labels at the top-left corner of each axes, in the journal's style.

    Optica family: (a) (b) regular; Nature family: a b bold; Science family: A B bold.
    The label sits just above the top-left corner of the plot area, pushed left by
    dx_pt points so it clears the y tick labels. Draw the y labels first.
    """
    s = spec(journal)
    fmt, weight, size = s["label"]
    axs = [a for a in np.atleast_1d(axes).ravel() if a is not None]
    letters = string.ascii_uppercase if s.get("label_upper") else string.ascii_lowercase
    labels = labels or letters[: len(axs)]
    for ax, lab in zip(axs, labels):
        fig = ax.figure
        if dx_pt is None:
            fig.canvas.draw()
            bbox = ax.get_tightbbox(fig.canvas.get_renderer())
            left = (ax.get_window_extent().x0 - bbox.x0) * 72 / fig.dpi
        else:
            left = dx_pt
        offset = ScaledTranslation(-left / 72, dy_pt / 72, fig.dpi_scale_trans)
        ax.text(0, 1, fmt.format(lab), transform=ax.transAxes + offset, fontsize=size,
                fontweight=weight, va="bottom", ha="left")


def audit(fig, journal=None):
    """Return a list of problems that would get the figure bounced: wrong width,
    text below the journal minimum, hairlines, or content clipped at the figure edge."""
    s = spec(journal)
    problems = []
    w_mm, h_mm = (v / MM for v in fig.get_size_inches())
    if s.get("any_width"):
        if w_mm > max(s["widths"].values()) + 0.6:
            problems.append(f"width {w_mm:.1f} mm exceeds the {max(s['widths'].values()):g} mm text width of {s['name']}")
    elif not any(abs(w_mm - w) < 0.6 for w in s["widths"].values()):
        allowed = ", ".join(f"{k} {v:g}" for k, v in s["widths"].items())
        problems.append(f"width {w_mm:.1f} mm is not a {s['name']} column width ({allowed} mm)")
    if h_mm > s["max_height"] + 0.5:
        problems.append(f"height {h_mm:.1f} mm exceeds {s['max_height']:g} mm")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    small = set()
    for t in fig.findobj(mpl.text.Text):
        if t.get_visible() and t.get_text().strip() and t.get_fontsize() < s["font_min"] - 1e-6:
            small.add(f"{t.get_text()[:20]!r} at {t.get_fontsize():.1f} pt")
    for i, ax in enumerate(fig.axes):
        box = ax.get_tightbbox(renderer)  # drawn extent only; ignores tick labels outside the limits
        if box is not None and (box.x0 < fig.bbox.x0 - 1 or box.x1 > fig.bbox.x1 + 1
                                or box.y0 < fig.bbox.y0 - 1 or box.y1 > fig.bbox.y1 + 1):
            problems.append(f"axes {i} (labels or ticks) is clipped by the figure edge")
    if small:
        problems.append(f"text below {s['font_min']:g} pt: " + "; ".join(sorted(small)[:6]))
    thin = [ln for ln in fig.findobj(mpl.lines.Line2D)
            if ln.get_visible() and ln.get_linestyle() not in ("None", "", " ") and 0 < ln.get_linewidth() < s["line_min"] - 1e-9]
    if thin:
        problems.append(f"{len(thin)} line(s) thinner than {s['line_min']:g} pt")
    return problems


def save(fig, stem, formats=("pdf", "png"), dpi=600, journal=None, strict=False):
    """Save at the exact physical size (never bbox_inches='tight', which changes it).

    PDF keeps text editable and lines vector; images inside are rasterised at `dpi`.
    Prints audit() findings; with strict=True they raise instead.
    """
    problems = audit(fig, journal)
    for p in problems:
        print(f"[pubfig] {stem}: {p}", file=sys.stderr)
    if problems and strict:
        raise ValueError(f"{stem}: {len(problems)} figure problem(s); see messages above")
    paths = []
    for ext in formats:
        path = f"{stem}.{ext}"
        fig.savefig(path, dpi=dpi)
        paths.append(path)
    return paths


# ---- axes helpers ---------------------------------------------------------

def frequency_axis(ax, label="Frequency (THz)", decimals=None):
    """Add a top axis in THz to an axes whose x axis is wavelength in nm."""
    def conv(x):
        x = np.asarray(x, dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(x > 0, C_NM_THZ / x, np.nan)
    ax.tick_params(axis="x", which="both", top=False)
    sec = ax.secondary_xaxis("top", functions=(conv, conv))
    sec.set_xlabel(label)
    if decimals is not None:
        sec.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter(f"%.{decimals}f"))
    return sec


def detuning_axis(ax, center_nm, label="Detuning (GHz)"):
    """Add a top axis of optical-frequency detuning in GHz around center_nm, for an
    x axis in nm. Use it on narrow resonance scans where THz ticks are useless."""
    f0 = C_NM_THZ / center_nm
    fwd = lambda x: (C_NM_THZ / np.where(np.asarray(x, float) > 0, x, np.nan) - f0) * 1e3
    inv = lambda d: C_NM_THZ / (np.asarray(d, float) / 1e3 + f0)
    ax.tick_params(axis="x", which="both", top=False)
    sec = ax.secondary_xaxis("top", functions=(fwd, inv))
    sec.set_xlabel(label)
    return sec


def scalebar(ax, length, label, loc="lower right", color="white", pad=0.05, lw=None):
    """Draw a scale bar of `length` data units on an image axes and hide the ticks."""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    frac = abs(length / (x1 - x0))
    right = "right" in loc
    lower = "lower" in loc
    xa = (1 - pad - frac) if right else pad
    ya = pad if lower else 1 - pad
    lw = lw if lw is not None else mpl.rcParams["lines.linewidth"] * 1.5
    ax.plot([xa, xa + frac], [ya, ya], transform=ax.transAxes, color=color, lw=lw,
            solid_capstyle="butt", clip_on=False)
    ax.text(xa + frac / 2, ya + (0.025 if lower else -0.025), label, transform=ax.transAxes,
            color=color, ha="center", va="bottom" if lower else "top",
            fontsize=mpl.rcParams["xtick.labelsize"])
    ax.set_xticks([])
    ax.set_yticks([])


def colorbar(im, ax, label, **kwargs):
    """Colorbar matched to the axes height, with the journal's thin outline."""
    cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.03, **kwargs)
    cb.set_label(label)
    cb.outline.set_linewidth(mpl.rcParams["axes.linewidth"])
    cb.ax.tick_params(which="both", direction="out", right=True)
    return cb


def annotate_level(ax, y, text, x=0.98, **kwargs):
    """Dashed horizontal reference line (for example -3 dB) with a right-aligned label."""
    ax.axhline(y, color=PALETTE["grey"], lw=mpl.rcParams["axes.linewidth"], ls="--", zorder=1)
    ax.text(x, y, text, transform=ax.get_yaxis_transform(), ha="right", va="bottom",
            color=PALETTE["grey"], fontsize=mpl.rcParams["xtick.labelsize"], **kwargs)


def mplstyle(journal):
    """Return the journal style as .mplstyle text, for use without importing pubfig."""
    rc = _rc(JOURNALS[journal])
    lines = [f"# {JOURNALS[journal]['name']} - generated by pubfig.py; do not edit by hand"]
    for k, v in rc.items():
        if k == "axes.prop_cycle":
            v = "cycler('color', [" + ", ".join(repr(c.lstrip("#")) for c in CYCLE) + "])"
        elif isinstance(v, (list, tuple)):
            v = ", ".join(str(x) for x in v)
        lines.append(f"{k}: {v}")
    return "\n".join(lines) + "\n"


def _main(argv):
    if len(argv) >= 1 and argv[0] == "specs":
        for key, s in JOURNALS.items():
            widths = ", ".join(f"{k} {v:g}" for k, v in s["widths"].items())
            fmt, weight, size = s["label"]
            example = fmt.format("A" if s.get("label_upper") else "a")
            print(f"{key:8s} {s['name']}\n         widths (mm): {widths}; max height {s['max_height']:g} mm; "
                  f"text {s['font']:g} pt (min {s['font_min']:g}); panel label {example} {weight} {size:g} pt")
        return 0
    if len(argv) == 2 and argv[0] == "mplstyle" and argv[1] in JOURNALS:
        sys.stdout.write(mplstyle(argv[1]))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
