"""
Figures 1-4 of the paper.

    Figure 1: functional block diagrams of the three deorbit systems
    Figure 2: aggregate risk metrics by system (visualizes Table 6)
    Figure 3: risk matrix (Severity vs Occurrence, bubble size = Detection)
    Figure 4: Pareto chart of the ten highest-RPN failure modes
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

from data import FAILURE_MODES, SYSTEMS, DRAG_SAIL, EDT, COLD_GAS, modes_for
from metrics import table6, pareto, ZONE_S_MIN, ZONE_O_MIN

OUT = Path("figures")
COLORS = {DRAG_SAIL: "#4e79a7", EDT: "#f28e2b", COLD_GAS: "#59a14f"}
SHORT = {DRAG_SAIL: "Drag Sail", EDT: "EDT", COLD_GAS: "Propulsion"}


# --------------------------------------------------------------------------
# Figure 1
# --------------------------------------------------------------------------
def _box(ax, x, y, w, h, text, fc, ec="#333333", color="black",
         size=9, bold=False, align="center"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.2))
    ha_x = x + w / 2 if align == "center" else x + 0.35
    ax.text(ha_x, y + h / 2, text, ha=align, va="center", fontsize=size,
            color=color, fontweight="bold" if bold else "normal",
            linespacing=1.5)


def _arrow(ax, x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.3))


def figure1():
    cols = [
        (COLD_GAS, "Cold-Gas Propulsion", "Firing\nCommand",
         "Core Function:\nControlled Gas\nExpulsion",
         ["Control Electronics", "Propellant Storage",
          "Pressure Regulation", "Thruster Assembly"],
         "Output:\nThrust Impulse (\u0394V)"),
        (EDT, "Electrodynamic Tether", "Power &\nControl Command",
         "Core Function:\nCurrent Generation\n& Interaction",
         ["Power & Control Unit", "Deployment System",
          "Tether Assembly", "Plasma Contactor"],
         "Output:\nLorentz\nDeceleration Force"),
        (DRAG_SAIL, "Drag Sail System", "Deployment\nCommand",
         "Core Function:\nDeployment & Area\nExpansion",
         ["Control & Sensing", "Deployment Mechanism",
          "Structural Assembly", "Sail Membrane"],
         "Output:\nIncreased\nAtmospheric Drag"),
    ]
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xlim(0, 15.6)
    ax.set_ylim(0, 12)
    ax.axis("off")

    _box(ax, 5.6, 10.6, 4.4, 1.1, "CubeSat Bus\n(4.0 kg dry mass)", "#2f3e50",
         color="white", size=11, bold=True)

    width, xs = 4.6, [0.4, 5.5, 10.6]
    for (system, title, cmd, core, subs, out), x in zip(cols, xs):
        cx = x + width / 2
        _arrow(ax, 7.8, 10.6, cx, 9.5)
        ax.text((7.8 + cx) / 2 + (0.2 if cx > 7.8 else -0.2 if cx < 7.8 else 0.6),
                10.0, cmd, fontsize=8, style="italic", ha="center", va="center",
                bbox=dict(fc="white", ec="none", pad=1.5), zorder=5)
        _box(ax, x, 8.6, width, 0.9, title, COLORS[system], color="white",
             size=10, bold=True)
        _arrow(ax, cx, 8.6, cx, 8.25)
        _box(ax, x, 7.0, width, 1.25, core, "#d6e6f3", size=9)
        _arrow(ax, cx, 7.0, cx, 6.65)
        _box(ax, x, 3.1, width, 3.55,
             "Subsystems:\n\n" + "\n".join(f"\u2022 {s}" for s in subs),
             "#f7f7f7", size=9, align="left")
        _arrow(ax, cx, 3.1, cx, 2.75)
        _box(ax, x, 1.3, width, 1.45, out, "#dcebd5", size=9)

    fig.text(0.5, 0.03,
             "Figure 1: Functional block diagrams of the analyzed CubeSat deorbit systems. "
             "Each system receives an input command from the CubeSat bus\nand produces a distinct "
             "output for orbital decay. Subsystems correspond to the functional decomposition in Table 1.",
             ha="center", fontsize=8)
    return fig


# --------------------------------------------------------------------------
# Figure 2
# --------------------------------------------------------------------------
def figure2():
    t6 = table6()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5),
                                   gridspec_kw={"width_ratios": [1.5, 1]})

    metrics = ["Average Severity (S)", "Average Occurrence (O)", "Average Detection (D)"]
    groups = ["Severity (S)", "Occurrence (O)", "Detection (D)"]
    x = np.arange(len(groups))
    w = 0.26
    for i, s in enumerate(SYSTEMS):
        vals = [t6[s][m] for m in metrics]
        bars = ax1.bar(x + (i - 1) * w, vals, w, color=COLORS[s], edgecolor="#333",
                       lw=0.6, label=s)
        for b, v in zip(bars, vals):
            ax1.text(b.get_x() + b.get_width() / 2, v - 0.35, f"{v:.2f}",
                     ha="center", va="top", fontsize=7)
    ax1.set_xticks(x, groups)
    ax1.set_ylim(0, 10)
    ax1.set_ylabel("Average score (1-10 scale)")
    ax1.set_title("Average S / O / D by System", fontsize=10)
    ax1.legend(frameon=True, fontsize=8, loc="upper center",
               bbox_to_anchor=(0.5, -0.1), ncol=1)
    ax1.grid(axis="y", ls=":", alpha=0.6)
    ax1.set_axisbelow(True)

    avg = [t6[s]["Average RPN"] for s in SYSTEMS]
    bars = ax2.bar([SHORT[s] for s in SYSTEMS], avg,
                   color=[COLORS[s] for s in SYSTEMS], edgecolor="#333", lw=0.6)
    for b, v in zip(bars, avg):
        ax2.text(b.get_x() + b.get_width() / 2, v - 6, f"{v:.1f}",
                 ha="center", va="top", fontsize=9)
    ax2.set_ylim(0, 260)
    ax2.set_ylabel("Average RPN")
    ax2.set_title("Average RPN by System", fontsize=10)
    ax2.grid(axis="y", ls=":", alpha=0.6)
    ax2.set_axisbelow(True)
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------
# Figure 3
# --------------------------------------------------------------------------
def figure3():
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.add_patch(Rectangle((ZONE_S_MIN - 0.5, ZONE_O_MIN), 10.5 - (ZONE_S_MIN - 0.5),
                           5.5 - ZONE_O_MIN, fc="#f4c7c3", alpha=0.35, ec="none", zorder=0))

    for s in SYSTEMS:
        ms = modes_for(s)
        ax.scatter([m.S for m in ms], [m.O for m in ms],
                   s=[m.D ** 2 * 9 for m in ms], c=COLORS[s],
                   alpha=0.85, edgecolors="#333", linewidths=0.6,
                   label=s, zorder=3)
    ax.set_xlim(0.5, 10.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 11))
    ax.set_yticks(range(1, 6))
    ax.set_xlabel("Severity (S) -- deorbit-timeline impact")
    ax.set_ylabel("Occurrence (O) -- failure fraction of missions")
    ax.set_title("Risk Matrix: Severity vs. Occurrence by System\n"
                 "(bubble size = Detection; upper-right region = highest combined risk)",
                 fontsize=10)
    ax.grid(ls=":", alpha=0.5)

    leg1 = ax.legend(title="System (color)", loc="upper left", fontsize=8, framealpha=0.95)
    ax.add_artist(leg1)
    handles = [ax.scatter([], [], s=d ** 2 * 9, c="#bbbbbb", edgecolors="#333", lw=0.6)
               for d in (3, 6, 9)]
    ax.legend(handles, ["D=3", "D=6", "D=9"], title="Bubble size = Detection (D)",
              loc="lower left", fontsize=8, labelspacing=1.4, borderpad=1.0,
              framealpha=0.95)
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------
# Figure 4
# --------------------------------------------------------------------------
def figure4(top_n: int = 10):
    ranked, cum = pareto()
    top = ranked[:top_n]

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.bar(range(top_n), [m.rpn for m in top],
           color=[COLORS[m.system] for m in top], edgecolor="#333", lw=0.5)
    ax.set_xticks(range(top_n), [m.label for m in top], rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("Risk Priority Number (RPN)")
    ax.set_ylim(0, 350)
    ax.grid(axis="y", ls=":", alpha=0.6)
    ax.set_axisbelow(True)

    ax2 = ax.twinx()
    ax2.plot(range(top_n), cum[:top_n], "o-", color="#c0392b", lw=2, ms=5,
             label="Cumulative %")
    ax2.axhline(80, color="gray", ls="--", lw=1)
    ax2.text(top_n - 0.6, 81.5, "80% threshold", ha="right", fontsize=8, color="gray")
    ax2.set_ylim(0, 120)
    ax2.set_ylabel("Cumulative % of Total RPN")

    handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[s]) for s in SYSTEMS]
    handles.append(ax2.lines[0])
    ax.legend(handles, SYSTEMS + ["Cumulative %"], loc="upper right",
              fontsize=8, bbox_to_anchor=(0.99, 0.99))
    ax.set_title("Pareto Chart: Ten Highest-RPN Failure Modes", fontsize=10)
    fig.tight_layout()
    return fig


def save_all(dpi: int = 300):
    OUT.mkdir(exist_ok=True)
    for name, fn in [("figure1_block_diagram", figure1),
                     ("figure2_aggregate_metrics", figure2),
                     ("figure3_risk_matrix", figure3),
                     ("figure4_pareto", figure4)]:
        fig = fn()
        fig.savefig(OUT / f"{name}.png", dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        print(f"saved {OUT / name}.png")


if __name__ == "__main__":
    save_all()
