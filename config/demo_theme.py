"""Preview an .mplstyle file: fonts, colors, grid, spines, and the full
line-color cycle, all in one plot.

    python config/demo_theme.py                    # defaults to sirius.mplstyle
    python config/demo_theme.py config/plot_style.mplstyle
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

style_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "sirius.mplstyle"
plt.style.use(style_file)

# Fake residual convergence curves -- one per equation, decaying with noise,
# same shape of plot this toolkit actually produces. 7 lines so the 6-color
# prop_cycle visibly wraps back around to the first color.
rng = np.random.default_rng(0)
iterations = np.arange(1, 400)
equations = [
    "continuity",
    "x-momentum",
    "y-momentum",
    "z-momentum",
    "energy",
    "turb-k",
    "turb-omega",
]

fig, ax = plt.subplots(figsize=(10, 6))

for i, name in enumerate(equations):
    decay_rate = 0.012 + 0.003 * i
    noise = rng.normal(0, 0.05, size=iterations.size)
    residual = 1.0 * np.exp(-decay_rate * iterations) + 0.01
    residual *= 1 + noise * np.exp(-0.004 * iterations)
    ax.plot(iterations, residual, label=name)

ax.set_yscale("log")
ax.set_xlabel("Solver Iteration")
ax.set_ylabel("Residual")
ax.set_title(f"Theme preview -- {style_file.name}", loc="left", pad=15, fontweight="bold")
ax.legend(loc="upper right", framealpha=0.9)

plt.show()
