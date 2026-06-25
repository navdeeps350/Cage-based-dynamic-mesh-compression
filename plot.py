import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.optimize import curve_fit

action = "jumping"

matplotlib.rcParams.update({
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

def hyperbola_1(x, A, h, k, n):
    return k + A / (x - h) ** n



# ── Load data ──────────────────────────────────────────────────────────────────

df_ours  = pd.read_csv(f"sted_results_refined/sted_results_mvc_mvc_{action}_5000.csv")
df_base = pd.read_csv(f"sted_results_baseline/sted_results_mvc_mvc_{action}_p2.csv")


def fit_hyperbola(df):
    x = df['bpvf'].values
    y = df['STED Value'].values
    k0 = y[-1]
    h0 = x.min() - 0.1
    A0 = (y[0] - k0) * (x[0] - h0)
    bounds = ([0, -np.inf, 0, 0], [np.inf, x.min() - 1e-6, np.inf, np.inf])
    popt, _ = curve_fit(hyperbola_1, x, y, p0=[A0, h0, k0, 1.0],
                        bounds=bounds, maxfev=100000)
    xs = np.linspace(x.min(), x.max(), 500)
    ys = hyperbola_1(xs, *popt)
    return xs, ys


xs_ours,  ys_ours  = fit_hyperbola(df_ours)
xs_base,  ys_base  = fit_hyperbola(df_base)

# ── Figure ─────────────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(5, 5))  # square figure

ax.plot(xs_ours, ys_ours, color='tab:blue')
ax.plot(xs_base, ys_base, color='tab:orange')

ax.scatter(df_ours['bpvf'], df_ours['STED Value'], s=15, label="ours", color='tab:blue')
ax.scatter(df_base['bpvf'], df_base['STED Value'], s=15, label="baseline", color='tab:orange')

ax.set_xlim(0, 2.5)
ax.set_ylim(0, 0.1)

# make the *plot area* square (so grid cells can be square)
ax.set_box_aspect(1)

ax.xaxis.set_major_locator(mticker.MultipleLocator(0.5))
ax.yaxis.set_major_locator(mticker.MultipleLocator(0.02))

ax.grid(True)
ax.legend()

plt.show()

