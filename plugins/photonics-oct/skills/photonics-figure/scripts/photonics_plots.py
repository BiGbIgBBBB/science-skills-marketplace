#!/usr/bin/env python3
"""Plot recipes and the small analyses that go with them, for PIC and OCT figures.

Each plot_* function draws on an axes you pass in and returns the numbers it
annotated, so the same values can go into the caption and the text.

    import pubfig as pf, photonics_plots as pp
    pf.use("optica")
    fig, ax = pf.figure("single", aspect=0.72)
    fit = pp.plot_resonance(ax, wl_nm, transmission_linear)
    print(fit["q_loaded"], fit["fwhm_pm"])

Demo with synthetic data (also the regression test for this file):

    python photonics_plots.py demo optica out_dir
"""
from __future__ import annotations

import sys

import matplotlib as mpl
import numpy as np
from scipy.optimize import curve_fit

import pubfig as pf


# ---- small analyses -------------------------------------------------------

def db(x, power=True):
    """Linear to dB. power=True: 10 log10 (optical power, OCT intensity);
    power=False: 20 log10 (field amplitude, voltage, S21 magnitude)."""
    x = np.asarray(x, dtype=float)
    with np.errstate(divide="ignore"):
        return (10.0 if power else 20.0) * np.log10(x)


def crossing_width(x, y, level):
    """Full width of the single peak in y(x) at absolute `level`, by linear
    interpolation between samples. Returns (width, x_left, x_right)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    i = int(np.nanargmax(y))
    if y[i] <= level:
        raise ValueError("peak does not reach the requested level")
    left = np.where(y[:i] < level)[0]
    right = np.where(y[i:] < level)[0]
    if len(left) == 0 or len(right) == 0:
        raise ValueError("peak does not fall below the level inside the window; widen the window")
    a, b = left[-1], i + right[0]
    xl = np.interp(level, [y[a], y[a + 1]], [x[a], x[a + 1]])
    xr = np.interp(level, [y[b], y[b - 1]], [x[b], x[b - 1]])
    return xr - xl, xl, xr


def fwhm(x, y_linear):
    """FWHM of a peak given on a linear scale (not dB)."""
    y = np.asarray(y_linear, float)
    return crossing_width(x, y, np.nanmax(y) / 2)[0]


def lorentzian_dip(wl, wl0, width, depth, base):
    """Transmission dip: base * (1 - depth * L), L a unit-height Lorentzian of FWHM `width`."""
    return base * (1 - depth / (1 + (2 * (wl - wl0) / width) ** 2))


def fit_resonance(wl_nm, t_linear):
    """Fit one resonance dip (linear transmission vs wavelength in nm).

    Returns centre, linewidth, extinction and Q. The intrinsic Q depends on the
    coupling regime, which a single transmission scan cannot tell apart, so both
    candidates are returned; report the one your gap sweep or phase response supports.
    """
    wl, t = np.asarray(wl_nm, float), np.asarray(t_linear, float)
    base0 = np.percentile(t, 90)
    i0 = int(np.argmin(t))
    depth0 = np.clip(1 - t[i0] / base0, 0.01, 1)
    below = np.where(t < base0 * (1 - depth0 / 2))[0]
    width0 = max(wl[below[-1]] - wl[below[0]], 2 * np.mean(np.diff(wl))) if len(below) else (wl[-1] - wl[0]) / 10
    popt, pcov = curve_fit(lorentzian_dip, wl, t, p0=[wl[i0], width0, depth0, base0],
                           bounds=([wl[0], 0, 0, 0], [wl[-1], wl[-1] - wl[0], 1, np.inf]))
    wl0, width, depth, base = popt
    err = np.sqrt(np.diag(pcov))
    q_loaded = wl0 / width
    t0 = max(1 - depth, 0.0)  # normalised on-resonance transmission
    return {
        "wl0_nm": wl0, "fwhm_pm": width * 1e3, "fwhm_pm_err": err[1] * 1e3,
        "linewidth_ghz": pf.C_NM_THZ / wl0 ** 2 * width * 1e3,
        "extinction_db": -db(t0) if t0 > 0 else np.inf,
        "q_loaded": q_loaded, "q_loaded_err": q_loaded * err[1] / width,
        "q_intrinsic_undercoupled": 2 * q_loaded / (1 + np.sqrt(t0)),
        "q_intrinsic_overcoupled": 2 * q_loaded / (1 - np.sqrt(t0)) if t0 < 1 else np.inf,
        "popt": popt,
    }


def bandwidth_3db(f, response_db, drop_db=3.0):
    """First frequency where the response falls `drop_db` below its low-frequency
    value (mean of the lowest 3 points). Returns nan if it never does."""
    f, r = np.asarray(f, float), np.asarray(response_db, float)
    ref = np.mean(r[:3])
    below = np.where(r < ref - drop_db)[0]
    if len(below) == 0 or below[0] == 0:
        return np.nan
    i = below[0]
    return float(np.interp(ref - drop_db, [r[i], r[i - 1]], [f[i], f[i - 1]]))


def rolloff_depth(depths, peaks_db, drop_db=6.0):
    """Depth at which the A-scan peak has dropped `drop_db` from its shallowest value."""
    d, p = np.asarray(depths, float), np.asarray(peaks_db, float)
    order = np.argsort(d)
    d, p = d[order], p[order]
    below = np.where(p < p[0] - drop_db)[0]
    if len(below) == 0:
        return np.nan
    i = below[0]
    return float(np.interp(p[0] - drop_db, [p[i], p[i - 1]], [d[i], d[i - 1]]))


# ---- recipes --------------------------------------------------------------

def plot_transmission(ax, wl_nm, t_db, label=None, frequency_axis=True, **kwargs):
    """Broadband transmission / insertion-loss spectrum, dB against wavelength."""
    ax.plot(wl_nm, t_db, label=label, **kwargs)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Transmission (dB)")
    ax.set_xlim(np.min(wl_nm), np.max(wl_nm))
    if frequency_axis and not getattr(ax, "_pubfig_freq_axis", False):
        pf.frequency_axis(ax)
        ax._pubfig_freq_axis = True


def plot_resonance(ax, wl_nm, t_linear, detuning_axis=True, annotate=True):
    """Single resonance with Lorentzian fit; x axis is detuning from the centre in pm."""
    fit = fit_resonance(wl_nm, t_linear)
    wl0, base = fit["wl0_nm"], fit["popt"][3]
    x = (np.asarray(wl_nm) - wl0) * 1e3
    ax.plot(x, np.asarray(t_linear) / base, ".", color=pf.PALETTE["grey"], ms=mpl.rcParams["lines.markersize"],
            label="Data")
    xf = np.linspace(x.min(), x.max(), 600)
    ax.plot(xf, lorentzian_dip(wl0 + xf * 1e-3, *fit["popt"]) / base, color=pf.PALETTE["vermilion"], label="Fit")
    ax.set_xlabel("Wavelength detuning (pm)")
    ax.set_ylabel("Normalized transmission")
    ax.set_xlim(x.min(), x.max())
    ax.set_ylim(0, 1.08)
    if annotate:
        q = fit["q_loaded"]
        exp = int(np.floor(np.log10(q)))
        ax.text(0.05, 0.06, rf"$Q_L = {q / 10 ** exp:.2f}\times10^{{{exp}}}$", transform=ax.transAxes,
                va="bottom", ha="left", fontsize=mpl.rcParams["legend.fontsize"])
    if detuning_axis:
        ghz_per_pm = pf.C_NM_THZ / wl0 ** 2  # |df/dlambda| in GHz per pm
        sec = ax.secondary_xaxis("top", functions=(lambda p: -p * ghz_per_pm, lambda g: -g / ghz_per_pm))
        sec.set_xlabel("Frequency detuning (GHz)")
        ax.tick_params(axis="x", which="both", top=False)
    return fit


def plot_eo_response(ax, f_ghz, s21_db, label=None, log_x=False, annotate=True, **kwargs):
    """Electro-optic S21 normalised to its low-frequency value, with the 3-dB bandwidth."""
    f, r = np.asarray(f_ghz, float), np.asarray(s21_db, float)
    r = r - np.mean(r[:3])
    ax.plot(f, r, label=label, **kwargs)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("EO response (dB)")
    if log_x:
        ax.set_xscale("log")
    ax.set_xlim(f.min(), f.max())
    bw = bandwidth_3db(f, r)
    if annotate:
        pf.annotate_level(ax, -3, "−3 dB")
        if np.isfinite(bw):
            ax.plot([bw], [-3], "o", color=pf.PALETTE["vermilion"], ms=mpl.rcParams["lines.markersize"] + 1, zorder=5)
    return {"bandwidth_3db_ghz": bw}


def plot_rolloff(ax, depth_mm, ascans_db, floor_db=None, annotate=True):
    """Sensitivity roll-off: PSFs measured at several mirror positions on one axes.

    ascans_db: iterable of A-scans in dB (10 log10 of intensity) on the common depth
    axis, normalised so the shallowest peak is 0 dB. Returns peak depths, peak levels
    and the 6-dB roll-off depth.
    """
    z = np.asarray(depth_mm, float)
    scans = [np.asarray(a, float) for a in ascans_db]
    cmap = mpl.colormaps["viridis"]
    peaks_z, peaks = [], []
    for k, a in enumerate(scans):
        ax.plot(z, a, color=cmap(0.1 + 0.75 * k / max(len(scans) - 1, 1)), lw=mpl.rcParams["lines.linewidth"] * 0.8)
        i = int(np.argmax(a))
        peaks_z.append(z[i])
        peaks.append(a[i])
    order = np.argsort(peaks_z)
    peaks_z, peaks = np.array(peaks_z)[order], np.array(peaks)[order]
    ax.plot(peaks_z, peaks, "--", color=pf.PALETTE["black"], lw=mpl.rcParams["axes.linewidth"], marker="o",
            ms=mpl.rcParams["lines.markersize"] * 0.8, mfc="white", label="Peak envelope")
    ax.set_xlabel("Depth in air (mm)")
    ax.set_ylabel("Signal (dB)")
    ax.set_xlim(z.min(), z.max())
    if floor_db is not None:
        ax.set_ylim(floor_db, 5)
    z6 = rolloff_depth(peaks_z, peaks)
    if annotate and np.isfinite(z6):
        ax.axvline(z6, color=pf.PALETTE["grey"], ls=":", lw=mpl.rcParams["axes.linewidth"])
        ax.text(z6, 0.97, f" \u22126 dB\n {z6:.1f} mm", transform=ax.get_xaxis_transform(), va="top", ha="left",
                color=pf.PALETTE["grey"], fontsize=mpl.rcParams["xtick.labelsize"])
    return {"peak_depth_mm": peaks_z, "peak_db": peaks, "rolloff_6db_mm": z6}


def plot_psf(ax, depth_um, ascan_linear, annotate=True):
    """One axial point-spread function on a linear scale with its FWHM (axial resolution)."""
    z, a = np.asarray(depth_um, float), np.asarray(ascan_linear, float)
    a = a / a.max()
    width, zl, zr = crossing_width(z, a, 0.5)
    ax.plot(z - z[np.argmax(a)], a, color=pf.PALETTE["blue"])
    ax.set_xlabel("Depth (µm)")
    ax.set_ylabel("Normalized intensity")
    ax.set_ylim(0, 1.1)
    if annotate:
        z0 = z[np.argmax(a)]
        ax.annotate("", xy=(zl - z0, 0.5), xytext=(zr - z0, 0.5),
                    arrowprops=dict(arrowstyle="<->", lw=mpl.rcParams["axes.linewidth"], color=pf.PALETTE["black"],
                                    shrinkA=0, shrinkB=0))
        ax.text(zr - z0, 0.5, f"  {width:.1f} µm", va="center", ha="left", fontsize=mpl.rcParams["legend.fontsize"])
    return {"axial_resolution_um": width}


def plot_bscan(ax, intensity, width_mm, depth_mm, dynamic_range_db=40.0, ceiling_db=None,
               scalebar_mm=0.5, colorbar=True, in_db=False):
    """OCT B-scan in greyscale on a dB scale with a fixed dynamic range and scale bars.

    intensity: 2-D array [depth, lateral], linear intensity (or dB if in_db=True).
    The display window is [ceiling - dynamic_range, ceiling]; ceiling defaults to the
    99.9th percentile so one specular pixel does not set the scale. State the dynamic
    range in the caption. Pixels are square in physical units (aspect="equal").
    """
    img = np.asarray(intensity, float)
    img_db = img if in_db else db(np.maximum(img, np.finfo(float).tiny))
    top = np.percentile(img_db, 99.9) if ceiling_db is None else ceiling_db
    im = ax.imshow(img_db - top, cmap=pf.CMAPS["oct"], vmin=-dynamic_range_db, vmax=0,
                   extent=(0, width_mm, depth_mm, 0), aspect="equal", interpolation="nearest", rasterized=True)
    if scalebar_mm:
        pf.scalebar(ax, scalebar_mm, f"{scalebar_mm:g} mm")
    cb = pf.colorbar(im, ax, "Intensity (dB)") if colorbar else None
    return {"image": im, "colorbar": cb, "ceiling_db": top}


def plot_noise(ax, f_hz, psd_db, ylabel="RIN (dBc/Hz)", label=None, **kwargs):
    """Noise spectrum (RIN, phase noise, frequency noise) on a log frequency axis."""
    ax.semilogx(f_hz, psd_db, label=label, **kwargs)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel(ylabel)
    ax.set_xlim(np.min(f_hz), np.max(f_hz))
    ax.xaxis.set_major_locator(mpl.ticker.LogLocator(base=10, numticks=12))
    ax.xaxis.set_minor_locator(mpl.ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=100))
    ax.xaxis.set_minor_formatter(mpl.ticker.NullFormatter())


def plot_mode(ax, x_um, y_um, intensity, outlines=(), scalebar_um=1.0, colorbar=False):
    """Simulated or measured mode profile |E|^2 with the waveguide cross-section drawn on top.

    outlines: iterable of (N, 2) arrays of polygon vertices in micrometres
    (ridge, slab, cladding boundaries).
    """
    z = np.asarray(intensity, float)
    im = ax.imshow(z / z.max(), cmap=pf.CMAPS["field"], vmin=0, vmax=1, origin="lower",
                   extent=(np.min(x_um), np.max(x_um), np.min(y_um), np.max(y_um)), aspect="equal",
                   interpolation="bilinear", rasterized=True)
    for poly in outlines:
        p = np.asarray(poly, float)
        ax.plot(np.r_[p[:, 0], p[0, 0]], np.r_[p[:, 1], p[0, 1]], color="white", lw=mpl.rcParams["axes.linewidth"])
    if scalebar_um:
        pf.scalebar(ax, scalebar_um, f"{scalebar_um:g} µm")
    cb = pf.colorbar(im, ax, r"$|E|^2$ (norm.)") if colorbar else None
    return {"image": im, "colorbar": cb}


# ---- demo -----------------------------------------------------------------

def _synthetic(rng):
    d = {}
    # ring-resonator transmission across the C band
    wl = np.linspace(1530, 1570, 8001)
    fsr, width = 1.6, 0.012
    t = np.ones_like(wl)
    for wl0 in np.arange(1530.4, 1570, fsr):
        t *= lorentzian_dip(wl, wl0, width, 0.9, 1.0)
    envelope = -4.5 - 1.2 * ((wl - 1550) / 20) ** 2
    d["wl"], d["t_db"] = wl, db(t) + envelope + rng.normal(0, 0.05, wl.size)
    # one resonance, Q_L = 1.2e6
    wl1 = 1550.12 + np.linspace(-6e-3, 6e-3, 241)
    d["wl_res"] = wl1
    d["t_res"] = lorentzian_dip(wl1, 1550.12, 1550.12 / 1.2e6, 0.82, 0.31) * (1 + rng.normal(0, 0.012, wl1.size))
    # travelling-wave modulator EO response
    f = np.linspace(0.1, 67, 400)
    d["f"] = f
    d["s21"] = {L: -0.9 * np.sqrt(f) * L / 10 - 0.012 * f * L / 10 + rng.normal(0, 0.08, f.size) for L in (5, 10, 20)}
    # roll-off: gaussian PSFs under a sinc^2 * gaussian envelope
    z = np.linspace(0, 12, 4000)
    scans = []
    for z0 in np.arange(1, 11.1, 1.0):
        peak = -6 * (z0 / 7.5) ** 2
        psf = 10 ** (peak / 10) * np.exp(-4 * np.log(2) * ((z - z0) / 0.015) ** 2)
        scans.append(db(psf + 10 ** (-5.2) * (1 + 0.5 * rng.random(z.size))))
    d["z"], d["scans"] = z, scans
    # layered speckle phantom
    nz, nx = 300, 500
    depth = np.linspace(0, 1.5, nz)[:, None]
    surf = 0.25 + 0.05 * np.sin(np.linspace(0, 3 * np.pi, nx))[None, :]
    rel = depth - surf
    refl = np.where(rel < 0, 1e-4, np.exp(-2.2 * rel) * (0.15 + 0.85 * (np.sin(18 * rel) > 0.2)))
    refl = refl + 3.0 * np.exp(-((rel) / 0.006) ** 2)
    d["bscan"] = refl * rng.exponential(1.0, (nz, nx)) + 1e-4 * rng.exponential(1.0, (nz, nx))
    # TFLN ridge mode
    x, y = np.linspace(-2, 2, 321), np.linspace(-0.6, 1.2, 181)
    xx, yy = np.meshgrid(x, y)
    d["x"], d["y"] = x, y
    d["mode"] = np.exp(-(xx / 0.55) ** 2 - ((yy - 0.3) / 0.28) ** 2)
    d["outlines"] = [np.array([[-2, 0], [2, 0], [2, 0.3], [0.85, 0.3], [0.6, 0.6], [-0.6, 0.6], [-0.85, 0.3], [-2, 0.3]])]
    return d


def demo(journal="optica", out_dir="."):
    import os
    import matplotlib.pyplot as plt

    os.makedirs(out_dir, exist_ok=True)
    pf.use(journal)
    d = _synthetic(np.random.default_rng(7))
    fig, axs = pf.figure("full", aspect=0.45 if journal == "slides" else 0.62, nrows=2, ncols=3)
    (a, b, c), (e, f, g) = axs
    plot_transmission(a, d["wl"], d["t_db"], lw=max(0.5, pf.spec()["line_min"]))
    fit = plot_resonance(b, d["wl_res"], d["t_res"])
    b.legend(loc="lower right")
    for L, r in d["s21"].items():
        bw = plot_eo_response(c, d["f"], r, label=f"{L} mm", annotate=(L == 5))
        print(f"  {L} mm modulator: 3-dB bandwidth {bw['bandwidth_3db_ghz']:.1f} GHz")
    c.set_ylim(-12, 1)
    c.legend(title="Electrode length", loc="lower right")
    ro = plot_rolloff(e, d["z"], d["scans"], floor_db=-60)
    plot_bscan(f, d["bscan"], width_mm=2.5, depth_mm=1.5, dynamic_range_db=40)
    plot_mode(g, d["x"], d["y"], d["mode"], outlines=d["outlines"], colorbar=True)
    pf.label_panels(axs)
    paths = pf.save(fig, os.path.join(out_dir, f"demo_{journal}"))
    plt.close(fig)
    print(f"  resonance: Q_L = {fit['q_loaded']:.3g}, FWHM = {fit['fwhm_pm']:.2f} pm, "
          f"extinction = {fit['extinction_db']:.1f} dB; 6-dB roll-off at {ro['rolloff_6db_mm']:.2f} mm")
    print("  wrote", ", ".join(paths))
    return paths


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "demo":
        demo(*(sys.argv[2:4]))
    else:
        print(__doc__)
        sys.exit(2)
