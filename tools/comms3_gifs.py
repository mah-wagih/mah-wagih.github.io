"""
Generate the extra teaching GIFs used on comms3.html.

    pip install numpy matplotlib pillow
    python tools/comms3_gifs.py              # all GIFs -> images/comms3/
    python tools/comms3_gifs.py two_ray      # just one

Style matches the ENG3014_* course GIFs: Carlito/Lato font, bold left titles,
light grid, boxed annotations, 60 ms per frame.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Circle, Ellipse, Rectangle

OUT = os.path.join(os.path.dirname(__file__), "..", "images", "comms3")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": ["Carlito", "DejaVu Sans"],
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#e6e6e6",
    "grid.linewidth": 0.8,
    "axes.edgecolor": "#222222",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "mathtext.fontset": "custom",
    "mathtext.rm": "Carlito",
    "mathtext.it": "Carlito:italic",
    "mathtext.bf": "Carlito:bold",
})

RED, BLUE, ORANGE, GREEN, GREY = "#d62728", "#1f77b4", "#ff7f0e", "#2ca02c", "#9a9a9a"
BOX = dict(boxstyle="square,pad=0.35", fc="white", ec="#9a9a9a", lw=0.8)
FRAME_MS = 60


def save(fig, update, n, name):
    anim = FuncAnimation(fig, update, frames=n, blit=False)
    path = os.path.join(OUT, name)
    anim.save(path, writer=PillowWriter(fps=1000 / FRAME_MS))
    plt.close(fig)
    print(f"{name}: {os.path.getsize(path) / 1e6:.2f} MB, {n} frames")


def ease(x):
    return 0.5 - 0.5 * np.cos(np.pi * np.clip(x, 0, 1))


# ---------------------------------------------------------------------------
# 1. Sine wave: time domain -> frequency domain
# ---------------------------------------------------------------------------
def sine_time_freq():
    t = np.linspace(0, 0.2, 2000)
    n_draw, n_f, n_a, n_hold = 40, 50, 36, 14
    N = n_draw + n_f + n_a + n_hold

    def params(i):
        f, A, frac = 10.0, 1.0, 1.0
        if i < n_draw:
            frac = (i + 1) / n_draw
        elif i < n_draw + n_f:
            u = (i - n_draw) / (n_f - 1)
            f = 10 + 30 * np.sin(np.pi * ease(u))  # 10 -> 40 -> 10 Hz
        elif i < n_draw + n_f + n_a:
            u = (i - n_draw - n_f) / (n_a - 1)
            A = 1 - 0.6 * np.sin(np.pi * ease(u))  # 1 -> 0.4 -> 1 V
        return f, A, frac

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.16), dpi=100,
                                   gridspec_kw=dict(width_ratios=[1.6, 1]))
    fig.subplots_adjust(left=0.06, right=0.98, bottom=0.13, top=0.9, wspace=0.18)
    ax1.set(xlim=(0, 200), ylim=(-1.4, 1.4), xlabel="t (ms)", ylabel="x(t) (V)")
    ax1.set_title(r"Time domain: $x(t) = A\cos(2\pi f t)$")
    ax2.set(xlim=(0, 50), ylim=(0, 1.25), xlabel="f (Hz)", ylabel="Amplitude (V)")
    ax2.set_title("Frequency domain: one line")
    (line,) = ax1.plot([], [], color="black", lw=1.8)
    (dot,) = ax1.plot([], [], "o", color=RED, ms=6)
    stem = ax2.plot([], [], color=RED, lw=2.5)[0]
    head = ax2.plot([], [], "^", color=RED, ms=8)[0]
    lab = ax2.text(0, 0, "", color=RED, ha="center", va="bottom", fontsize=10)
    info = ax1.text(0.012, 0.97, "", transform=ax1.transAxes, va="top", bbox=BOX)
    note = ax2.text(0.98, 0.97, "Height = amplitude A\nPosition = frequency f",
                    transform=ax2.transAxes, ha="right", va="top", bbox=BOX)

    def update(i):
        f, A, frac = params(i)
        k = max(2, int(len(t) * frac))
        y = A * np.cos(2 * np.pi * f * t)
        line.set_data(t[:k] * 1e3, y[:k])
        dot.set_data([t[k - 1] * 1e3], [y[k - 1]])
        h = A * frac
        stem.set_data([f, f], [0, h])
        head.set_data([f], [h])
        lab.set_position((f, h + 0.05))
        lab.set_text(f"{A:.2f} V")
        info.set_text(f"f = {f:.0f} Hz  (period T = {1000 / f:.0f} ms)    A = {A:.2f} V")
        return line, dot, stem, head, lab, info

    save(fig, update, N, "ENG3014_sine_time_freq.gif")


# ---------------------------------------------------------------------------
# 2. Square wave: time domain -> frequency domain (comb of odd harmonics)
# ---------------------------------------------------------------------------
def square_time_freq():
    t = np.linspace(0, 0.2, 4000)
    harm = np.arange(1, 40, 2)
    n_draw, n_f, n_hold = 45, 70, 15
    N = n_draw + n_f + n_hold

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.16), dpi=100,
                                   gridspec_kw=dict(width_ratios=[1.6, 1]))
    fig.subplots_adjust(left=0.06, right=0.98, bottom=0.13, top=0.9, wspace=0.18)
    ax1.set(xlim=(0, 200), ylim=(-1.6, 1.6), xlabel="t (ms)", ylabel="x(t) (V)")
    ax1.set_title("Time domain: square wave")
    ax2.set(xlim=(0, 250), ylim=(0, 1.5), xlabel="f (Hz)", ylabel="Amplitude (V)")
    ax2.set_title("Frequency domain: odd harmonics")
    (line,) = ax1.plot([], [], color="black", lw=1.8)
    (dot,) = ax1.plot([], [], "o", color=RED, ms=6)
    stems = [ax2.plot([], [], color=RED, lw=2.2)[0] for _ in harm]
    heads = ax2.plot([], [], "^", color=RED, ms=6)[0]
    info = ax1.text(0.012, 0.97, "", transform=ax1.transAxes, va="top", bbox=BOX)
    note = ax2.text(0.98, 0.97, "", transform=ax2.transAxes, ha="right", va="top", bbox=BOX)

    def update(i):
        f0, frac = 10.0, 1.0
        if i < n_draw:
            frac = (i + 1) / n_draw
        elif i < n_draw + n_f:
            u = (i - n_draw) / (n_f - 1)
            f0 = 10 + 15 * np.sin(np.pi * ease(u))  # 10 -> 25 -> 10 Hz
        k = max(2, int(len(t) * frac))
        y = np.sign(np.sin(2 * np.pi * f0 * t + 1e-9))
        line.set_data(t[:k] * 1e3, y[:k])
        dot.set_data([t[k - 1] * 1e3], [y[k - 1]])
        hx, hy = [], []
        for j, (n, s) in enumerate(zip(harm, stems)):
            # harmonics fade in one after another while the wave is drawn
            g = np.clip(frac * len(harm) * 0.5 - j * 0.5 + 0.5, 0, 1) if i < n_draw else 1.0
            a = 4 / (np.pi * n) * g
            s.set_data([n * f0, n * f0], [0, a])
            if a > 0.01:
                hx.append(n * f0)
                hy.append(a)
        heads.set_data(hx, hy)
        info.set_text(f"f0 = {f0:.0f} Hz  (period {1000 / f0:.0f} ms)")
        note.set_text(f"Lines at f0, 3f0, 5f0 ... = {f0:.0f}, {3 * f0:.0f}, {5 * f0:.0f} Hz ...\n"
                      "Height 4/(πn): 1.27, 0.42, 0.25 V ...")
        return [line, dot, heads, info, note, *stems]

    save(fig, update, N, "ENG3014_square_time_freq.gif")


# ---------------------------------------------------------------------------
# 3. Spreading sphere -> free-space path loss
# ---------------------------------------------------------------------------
def fspl_sphere():
    f = 2.4e9
    lam = 3e8 / f
    Pt_dbm = 20.0  # 100 mW
    d_all = np.logspace(0, 2, 400)
    pr_all = Pt_dbm - 20 * np.log10(4 * np.pi * d_all / lam)
    n_grow, n_hold = 100, 18
    N = n_grow + n_hold

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.4), dpi=100,
                                   gridspec_kw=dict(width_ratios=[1, 1.25]))
    fig.subplots_adjust(left=0.03, right=0.98, bottom=0.12, top=0.9, wspace=0.18)
    ax1.set_title("Power spreads over a growing sphere")
    ax1.set(xlim=(-1.15, 1.15), ylim=(-1.0, 1.15), aspect="equal")
    ax1.axis("off")
    ax1.plot(0, 0, marker="*", color="black", ms=13, zorder=5)
    ax1.text(0, -0.1, "Tx", ha="center", va="top", fontsize=10)
    sphere = Circle((0, 0), 0.1, fc=RED, ec=RED, lw=1.5, alpha=0.5)
    equator = Ellipse((0, 0), 0.2, 0.06, fill=False, ec=RED, lw=1, ls="--")
    ax1.add_patch(sphere)
    ax1.add_patch(equator)
    rx = Rectangle((0, 0), 0.07, 0.16, fc=BLUE, ec="black", lw=0.8, zorder=6)
    ax1.add_patch(rx)
    rx_lab = ax1.text(0, 0, "Rx area\n(fixed)", fontsize=9, color=BLUE, va="center")
    (rad,) = ax1.plot([], [], color="black", lw=1)
    rad_lab = ax1.text(0, 0, "d", fontsize=11, ha="center", va="bottom")
    info1 = ax1.text(-1.12, -0.97, "", fontsize=9.5, va="bottom", bbox=BOX)

    ax2.set_title("Received power vs distance (2.4 GHz, isotropic antennas)")
    ax2.set_xscale("log")
    ax2.set(xlim=(1, 100), ylim=(-65, -15), xlabel="distance d (m)", ylabel="P$_r$ (dBm)")
    ax2.grid(True, which="both")
    (trace,) = ax2.plot([], [], color=RED, lw=2)
    (dot,) = ax2.plot([], [], "o", color="black", ms=6, zorder=5)
    info2 = ax2.text(0.98, 0.97, "", transform=ax2.transAxes, ha="right", va="top", bbox=BOX)
    marks = []
    for d1 in (2, 4, 8):
        p0 = Pt_dbm - 20 * np.log10(4 * np.pi * (d1 / 2) / lam)
        p1 = Pt_dbm - 20 * np.log10(4 * np.pi * d1 / lam)
        a = ax2.annotate("", xy=(d1, p1), xytext=(d1, p0),
                         arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.2))
        tx = ax2.text(d1 * 1.06, (p0 + p1) / 2, "−6 dB", color=BLUE, fontsize=9, va="center")
        marks.append((d1, a, tx))
    dec = ax2.text(20, -30, "−20 dB per decade\n(×10 distance = 1/100 power)",
                   color=BLUE, fontsize=9.5)

    def update(i):
        u = min(1.0, (i + 1) / n_grow)
        d = 10 ** (2 * ease(u))
        r = 0.12 + 0.83 * np.log10(d) / 2
        sphere.set_radius(r)
        sphere.set_alpha(float(np.clip(0.65 / d ** 0.5, 0.06, 0.65)))
        equator.width, equator.height = 2 * r, 0.3 * r
        rx.set_xy((r * np.cos(0.5) - 0.02, r * np.sin(0.5) - 0.08))
        rx_lab.set_position((r * np.cos(0.5) + 0.07, r * np.sin(0.5)))
        rad.set_data([0, r * np.cos(0.5)], [0, r * np.sin(0.5)])
        rad_lab.set_position((0.5 * r * np.cos(0.5) - 0.04, 0.5 * r * np.sin(0.5) + 0.02))
        area = 4 * np.pi * d ** 2
        S = 0.1 / area * 1e3  # mW/m^2
        info1.set_text(f"d = {d:5.1f} m\nsphere area 4πd² = {area:,.0f} m²\n"
                       f"power density S = P$_t$/4πd² = {S:.3g} mW/m²")
        k = d_all <= d
        trace.set_data(d_all[k], pr_all[k])
        pr = Pt_dbm - 20 * np.log10(4 * np.pi * d / lam)
        dot.set_data([d], [pr])
        info2.set_text(f"P$_t$ = 20 dBm (100 mW)\nFSPL = 20 log$_{{10}}$(4πd/λ) = {-pr + Pt_dbm:.1f} dB\n"
                       f"P$_r$ = {pr:.1f} dBm")
        for d1, a, tx in marks:
            a.set_visible(d >= d1)
            tx.set_visible(d >= d1)
        dec.set_visible(d >= 30)
        return [sphere, equator, rx, rx_lab, rad, rad_lab, info1, trace, dot, info2, dec]

    save(fig, update, N, "ENG3014_FSPL_sphere.gif")


# ---------------------------------------------------------------------------
# 4. Two-ray ground reflection model
# ---------------------------------------------------------------------------
HT, HR, F2R = 10.0, 1.5, 900e6
LAM2R = 3e8 / F2R


def two_ray_power(d, pt_dbm=30.0):
    d1 = np.sqrt(d ** 2 + (HT - HR) ** 2)
    d2 = np.sqrt(d ** 2 + (HT + HR) ** 2)
    k = 2 * np.pi / LAM2R
    e = np.exp(-1j * k * d1) / d1 - np.exp(-1j * k * d2) / d2  # ground: Gamma = -1
    return pt_dbm + 20 * np.log10(LAM2R / (4 * np.pi) * np.abs(e)), d2 - d1


def two_ray():
    d_all = np.logspace(1, np.log10(5000), 3000)
    p_all, _ = two_ray_power(d_all)
    p_fs = 30 - 20 * np.log10(4 * np.pi * d_all / LAM2R)
    p_d4 = 30 + 20 * np.log10(HT * HR / d_all ** 2)
    dc = 4 * HT * HR / LAM2R
    n_grow, n_hold = 120, 20
    N = n_grow + n_hold

    fig = plt.figure(figsize=(9, 7), dpi=100)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1.45], hspace=0.35,
                          left=0.08, right=0.97, top=0.94, bottom=0.08)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    # schematic (log-distance, not to scale)
    hts, hrs = 1.0, 0.35
    xpos = lambda d: 0.4 + 9.4 * np.log10(d / 10) / np.log10(500)
    ax1.set_title("Two-ray model: direct path + ground reflection  (geometry not to scale)")
    ax1.set(xlim=(-0.3, 10.3), ylim=(-0.35, 1.3))
    ax1.axis("off")
    ax1.fill_between([-0.3, 10.3], -0.35, 0, color="#ead9c3")
    ax1.plot([-0.3, 10.3], [0, 0], color="#8c6d46", lw=1.5)
    ax1.plot([0, 0], [0, hts], color="black", lw=2.5)
    ax1.plot(0, hts, marker="v", color="black", ms=10)
    ax1.text(-0.1, hts / 2, f"h$_t$ = {HT:.0f} m", ha="right", va="center", fontsize=9.5, rotation=90)
    (mast,) = ax1.plot([], [], color="black", lw=2.5)
    (rxm,) = ax1.plot([], [], marker="v", color="black", ms=9)
    (direct,) = ax1.plot([], [], color=BLUE, lw=2, label="direct")
    (refl,) = ax1.plot([], [], color=ORANGE, lw=2, label="ground-reflected (Γ = −1)")
    ax1.legend(loc="upper right", frameon=True, fontsize=9.5)
    rx_lab = ax1.text(0, 0, "", fontsize=9.5, ha="center", va="bottom")

    ax2.set_title("Received power, f = 900 MHz, P$_t$ = 30 dBm, isotropic antennas")
    ax2.set_xscale("log")
    ax2.set(xlim=(10, 5000), ylim=(-110, -10), xlabel="distance d (m)", ylabel="P$_r$ (dBm)")
    ax2.grid(True, which="both")
    ax2.plot(d_all, p_fs, "--", color=GREY, lw=1.3, label="free space: −20 dB/decade")
    ax2.plot(d_all, p_d4, ":", color=BLUE, lw=1.6, label="beyond d$_c$: −40 dB/decade")
    ax2.axvline(dc, color=GREEN, ls=":", lw=1.3)
    ax2.text(dc * 1.05, -14, f"crossover d$_c$ = 4h$_t$h$_r$/λ ≈ {dc:.0f} m",
             color=GREEN, fontsize=9.5, va="top")
    (trace,) = ax2.plot([], [], color=RED, lw=1.8, label="two-ray (direct + reflected)")
    (dot,) = ax2.plot([], [], "o", color="black", ms=6, zorder=5)
    ax2.legend(loc="lower left", fontsize=9.5)
    info = ax2.text(0.98, 0.97, "", transform=ax2.transAxes, ha="right", va="top", bbox=BOX)

    def update(i):
        u = min(1.0, (i + 1) / n_grow)
        d = 10 * 500 ** u
        x = xpos(d)
        mast.set_data([x, x], [0, hrs])
        rxm.set_data([x], [hrs])
        rx_lab.set_position((x, hrs + 0.08))
        rx_lab.set_text(f"Rx, d = {d:.0f} m")
        direct.set_data([0, x], [hts, hrs])
        xr = x * hts / (hts + hrs)  # reflection point (image method)
        refl.set_data([0, xr, x], [hts, 0, hrs])
        k = d_all <= d
        trace.set_data(d_all[k], p_all[k])
        p, dd = two_ray_power(np.array([d]))
        dot.set_data([d], p)
        dphi = (2 * np.pi * dd[0] / LAM2R + np.pi) % (2 * np.pi)
        state = "constructive" if np.cos(dphi) > 0.5 else ("destructive" if np.cos(dphi) < -0.5 else "partial")
        info.set_text(f"path difference Δd = {dd[0] * 100:.1f} cm = {dd[0] / LAM2R:.2f} λ\n"
                      f"phase difference = {np.degrees(dphi):.0f}°  →  {state}\n"
                      f"P$_r$ = {p[0]:.1f} dBm")
        return [mast, rxm, rx_lab, direct, refl, trace, dot, info]

    save(fig, update, N, "ENG3014_two_ray.gif")


# ---------------------------------------------------------------------------
# FM: message in the phase of the carrier
# ---------------------------------------------------------------------------
def bessel_j(n, x):
    """J_n(x) by numerical integration (avoids a scipy dependency)."""
    th = np.linspace(0, np.pi, 2001)
    return np.trapezoid(np.cos(n * th - x * np.sin(th)), th) / np.pi


def fm():
    fc, fm_, A = 100.0, 10.0, 1.0
    t = np.linspace(0, 0.2, 4000)
    n_draw, n_sweep, n_hold = 40, 90, 15
    N = n_draw + n_sweep + n_hold

    def dev(i):
        if i < n_draw:
            return 30.0
        u = min(1.0, (i - n_draw) / (n_sweep - 1))
        return 30 + 30 * np.sin(2 * np.pi * u) * (1 if u < 0.5 else 0.66)  # 30 -> 60 -> 10 -> 30 Hz

    fig = plt.figure(figsize=(10, 6.2), dpi=90)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.5, 1], hspace=0.45, wspace=0.2,
                          left=0.07, right=0.98, top=0.93, bottom=0.09)
    ax1 = fig.add_subplot(gs[0, 0]); ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[0, 1]); ax4 = fig.add_subplot(gs[1, 1])

    ax1.set_title("Message v(t): 10 Hz sine")
    ax1.set(xlim=(0, 200), ylim=(-1.4, 1.4), ylabel="V")
    ax2.set_title("FM signal: the message is in the phase")
    ax2.set(xlim=(0, 200), ylim=(-1.5, 1.5), xlabel="t (ms)", ylabel="V")
    ax3.set_title("Instantaneous frequency f$_i$(t)")
    ax3.set(xlim=(0, 200), ylim=(20, 180), xlabel="t (ms)", ylabel="Hz")
    ax3.axhline(fc, color=GREY, ls="--", lw=1)
    ax3.text(198, fc + 4, "f$_c$ = 100 Hz", color=GREY, ha="right", fontsize=9)
    ax4.set_title("Spectrum: many sidebands, f$_c$ ± n f$_m$")
    ax4.set(xlim=(0, 200), ylim=(0, 1.1), xlabel="f (Hz)", ylabel="Amplitude (V)")

    (l_msg,) = ax1.plot([], [], color="black", lw=1.8)
    (l_fm,) = ax2.plot([], [], color=RED, lw=1.1)
    (l_fi,) = ax3.plot([], [], color=BLUE, lw=1.8)
    nn = np.arange(-12, 13)
    stems = [ax4.plot([], [], color=RED, lw=2)[0] for _ in nn]
    band = ax4.axvspan(0, 0, color=GREEN, alpha=0.15)
    info2 = ax2.text(0.01, 0.97, "", transform=ax2.transAxes, va="top", fontsize=9.5, bbox=BOX)
    info4 = ax4.text(0.98, 0.97, "", transform=ax4.transAxes, ha="right", va="top", fontsize=9, bbox=BOX)

    def update(i):
        df = dev(i)
        beta = df / fm_
        frac = min(1.0, (i + 1) / n_draw)
        k = max(2, int(len(t) * frac))
        msg = np.sin(2 * np.pi * fm_ * t)
        sig = A * np.cos(2 * np.pi * fc * t - beta * np.cos(2 * np.pi * fm_ * t))  # phase = integral of f_i
        fi = fc + df * msg
        l_msg.set_data(t[:k] * 1e3, msg[:k])
        l_fm.set_data(t[:k] * 1e3, sig[:k])
        l_fi.set_data(t[:k] * 1e3, fi[:k])
        for n, st in zip(nn, stems):
            st.set_data([fc + n * fm_] * 2, [0, abs(bessel_j(n, beta))])
        bw = 2 * (df + fm_)
        band.set_x(fc - bw / 2); band.set_width(bw)
        info2.set_text(f"Δf = {df:.0f} Hz    β = Δf / f$_m$ = {beta:.1f}")
        info4.set_text(f"Carson: B ≈ 2(Δf + f$_m$) = {bw:.0f} Hz")
        return [l_msg, l_fm, l_fi, band, info2, info4, *stems]

    save(fig, update, N, "ENG3014_FM.gif")


# ---------------------------------------------------------------------------
# FSK: bits switch the carrier between two frequencies
# ---------------------------------------------------------------------------
def fsk():
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    Tb, f1, f0 = 0.1, 60.0, 30.0
    T = Tb * len(bits)
    t = np.linspace(0, T, 6000)
    b = np.array(bits)[np.minimum((t / Tb).astype(int), len(bits) - 1)]
    f = np.where(b == 1, f1, f0)
    phase = 2 * np.pi * np.cumsum(f) * (t[1] - t[0])  # continuous phase
    sig = np.cos(phase)
    per_bit, n_hold = 14, 18
    N = per_bit * len(bits) + n_hold

    fig = plt.figure(figsize=(10, 6.2), dpi=90)
    gs = fig.add_gridspec(3, 2, width_ratios=[1.75, 1], height_ratios=[0.8, 1.2, 0.9],
                          hspace=0.6, wspace=0.18, left=0.07, right=0.98, top=0.93, bottom=0.09)
    ax1 = fig.add_subplot(gs[0, 0]); ax2 = fig.add_subplot(gs[1, 0]); ax3 = fig.add_subplot(gs[2, 0])
    ax4 = fig.add_subplot(gs[:, 1])

    ax1.set_title("Data: 1 0 1 1 0 0 1 0  (10 bit/s)")
    ax1.set(xlim=(0, 800), ylim=(-0.3, 1.5), ylabel="bit")
    ax1.set_yticks([0, 1])
    ax2.set_title("FSK signal")
    ax2.set(xlim=(0, 800), ylim=(-1.4, 1.4), ylabel="V")
    ax3.set_title("Frequency")
    ax3.set(xlim=(0, 800), ylim=(15, 75), xlabel="t (ms)", ylabel="Hz")
    ax3.set_yticks([f0, f1])
    for k_ in range(len(bits) + 1):
        for ax in (ax1, ax2, ax3):
            ax.axvline(k_ * Tb * 1e3, color="#dddddd", lw=0.8, zorder=0)
    ax4.set_title("Spectrum: the line jumps")
    ax4.set(xlim=(0, 90), ylim=(0, 1.25), xlabel="f (Hz)", ylabel="Amplitude (V)")
    s1 = ax4.plot([f1, f1], [0, 1], color=RED, lw=3)[0]
    s0 = ax4.plot([f0, f0], [0, 1], color=BLUE, lw=3)[0]
    ax4.text(f1, 1.04, "f$_1$ = 60 Hz\n'1'", color=RED, ha="center", fontsize=10)
    ax4.text(f0, 1.04, "f$_0$ = 30 Hz\n'0'", color=BLUE, ha="center", fontsize=10)

    (l_bits,) = ax1.plot([], [], color="black", lw=2, drawstyle="steps-post")
    seg1 = ax2.plot([], [], color=RED, lw=1.4)[0]
    seg0 = ax2.plot([], [], color=BLUE, lw=1.4)[0]
    (l_f,) = ax3.plot([], [], color="black", lw=2)
    labels = [ax1.text((k_ + 0.5) * Tb * 1e3, 1.2, str(v), ha="center", fontsize=12, fontweight="bold",
                       color=RED if v else BLUE) for k_, v in enumerate(bits)]

    def update(i):
        frac = min(1.0, (i + 1) / (per_bit * len(bits)))
        k = max(2, int(len(t) * frac))
        tm = t[:k] * 1e3
        l_bits.set_data(tm, b[:k])
        seg1.set_data(tm, np.where(b[:k] == 1, sig[:k], np.nan))
        seg0.set_data(tm, np.where(b[:k] == 0, sig[:k], np.nan))
        l_f.set_data(tm, f[:k])
        cur = b[k - 1]
        for j, lab in enumerate(labels):
            lab.set_visible(j * Tb <= t[k - 1])
        done = frac >= 1.0
        s1.set_alpha(1.0 if (cur == 1 or done) else 0.15)
        s0.set_alpha(1.0 if (cur == 0 or done) else 0.15)
        return [l_bits, seg1, seg0, l_f, s1, s0, *labels]

    save(fig, update, N, "ENG3014_FSK.gif")


# ---------------------------------------------------------------------------
# 5. Doppler shift seen by a moving receiver (fixed CW transmitter, one axis)
# ---------------------------------------------------------------------------
def doppler():
    lam, c = 2.0, 1.0                  # wavelength and wave speed (normalised units)
    fc = c / lam                       # carrier frequency
    v = 0.25 * c                       # receiver speed, exaggerated so the shift is visible
    dt = (1 / fc) / 12                 # 12 frames per carrier cycle: slow enough to follow
    x_tx = -7.0
    # (frames, velocity, label): still, away, still, towards, still -> ends where it started
    plan = [(24, 0.0, "still"), (60, +v, "away"), (18, 0.0, "still"), (60, -v, "towards"), (18, 0.0, "still")]
    xs, ts, vs, labs = [], [], [], []
    x, t = -1.25, 0.0
    for nf, vel, lab in plan:
        for _ in range(nf):
            xs.append(x); ts.append(t); vs.append(vel); labs.append(lab)
            x += vel * dt; t += dt
    xs, ts, vs = map(np.array, (xs, ts, vs))
    N = len(xs)
    f_rx = fc * (1 - vs / c)                             # moving with the wave -> lower, against it -> higher
    xx = np.linspace(-8, 8, 1200)

    fig = plt.figure(figsize=(10, 6.0), dpi=90)
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[1.6, 1], hspace=0.5, wspace=0.18,
                          left=0.06, right=0.98, top=0.92, bottom=0.1)
    ax1 = fig.add_subplot(gs[0, :]); ax2 = fig.add_subplot(gs[1, 0]); ax3 = fig.add_subplot(gs[1, 1])

    ax1.set_title("Fixed transmitter, moving receiver  (speed exaggerated: v = 0.25c)")
    ax1.set(xlim=(-8, 8), ylim=(-1.8, 1.9), xlabel="position")
    ax1.set_yticks([]); ax1.spines["left"].set_visible(False)
    ax1.plot([x_tx], [0], marker="s", color="black", ms=11, zorder=5)
    ax1.text(x_tx, 1.25, "Tx", ha="center", fontsize=11, fontweight="bold")
    ax1.annotate("", xy=(-4.3, 1.45), xytext=(-5.8, 1.45), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.4))
    ax1.text(-5.05, 1.6, "wave travels this way", color=GREY, ha="center", fontsize=9)
    (wave,) = ax1.plot([], [], color=GREY, lw=1.4)
    (rx,) = ax1.plot([], [], "o", color=RED, ms=11, zorder=6)
    rx_lab = ax1.text(0, 0, "Rx", ha="center", fontsize=11, fontweight="bold", color=RED)
    arrow = ax1.annotate("", xy=(0, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=RED, lw=2))
    state = ax1.text(0.99, 0.97, "", transform=ax1.transAxes, ha="right", va="top", fontsize=10.5, bbox=BOX)

    ax2.set_title("Signal at the receiver")
    window = 4 / fc
    ax2.set(xlim=(-window, 0), ylim=(-1.4, 1.4), xlabel="time (last 4 carrier cycles)")
    ax2.set_xticks([]); ax2.set_yticks([])
    (trace,) = ax2.plot([], [], color=RED, lw=1.8)

    ax3.set_title("Received frequency")
    ax3.set(xlim=(0.5, 1.5), ylim=(0, 1.3), xlabel="frequency (× f$_c$)")
    ax3.set_yticks([])
    ax3.plot([1, 1], [0, 1], "--", color=GREY, lw=1.5)
    ax3.text(1, 1.05, "f$_c$", color=GREY, ha="center", fontsize=10)
    (line,) = ax3.plot([], [], color=RED, lw=3)
    flab = ax3.text(0, 1.05, "", color=RED, ha="center", fontsize=10, fontweight="bold")

    text = {"still": "Rx still: f = f$_c$",
            "away": "Rx moving away: crests arrive less often → f = (1 − v/c) f$_c$ = 0.75 f$_c$",
            "towards": "Rx moving towards Tx: crests arrive more often → f = (1 + v/c) f$_c$ = 1.25 f$_c$"}

    def update(i):
        t, x, vel = ts[i], xs[i], vs[i]
        w = np.cos(2 * np.pi * (fc * t - (xx - x_tx) / lam))
        w[xx < x_tx] = np.nan
        wave.set_data(xx, w)
        y = np.cos(2 * np.pi * (fc * t - (x - x_tx) / lam))
        rx.set_data([x], [y])
        rx_lab.set_position((x, -1.65))
        if vel == 0:
            arrow.set_visible(False)
        else:
            arrow.set_visible(True)
            d = 1.4 if vel > 0 else -1.4
            arrow.set_position((x + 0.35 * np.sign(d), -1.15)); arrow.xy = (x + d, -1.15)
        state.set_text(text[labs[i]])
        tf = np.linspace(max(0.0, t - window), t, 300)      # fine time grid -> smooth trace
        xf = np.interp(tf, ts, xs)
        trace.set_data(tf - t, np.cos(2 * np.pi * (fc * tf - (xf - x_tx) / lam)))
        fr = f_rx[i] / fc
        line.set_data([fr, fr], [0, 1])
        flab.set_position((fr, 1.15 if abs(fr - 1) < 0.01 else 1.05))
        flab.set_text("" if abs(fr - 1) < 0.01 else f"{fr:.2f} f$_c$")
        return [wave, rx, rx_lab, arrow, state, trace, line, flab]

    save(fig, update, N, "ENG3014_doppler.gif")


if __name__ == "__main__":
    import sys
    only = sys.argv[1:]
    for fn in (sine_time_freq, square_time_freq, fm, fsk, fspl_sphere, two_ray, doppler):
        if not only or fn.__name__ in only:
            fn()
