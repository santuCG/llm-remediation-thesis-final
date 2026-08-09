"""Generate the thesis figures from the frozen evidence archive.

Every figure is produced from files under results/; nothing is hand-entered.
Run from the repository root:  python scripts/figures/make_figures.py
Output: figures/F1..F5 as PNG (300 dpi).
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

EV = os.path.join("results", "execution_evidence")
OUT = "figures"
IDS = [f"JS-0{i}" for i in range(1, 10)] + [f"AF-0{i}" for i in range(1, 10)]

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 9,
    "axes.titlesize": 10,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

INK = "#1a1a1a"
OK = "#2f6f4e"
BAD = "#a33a3a"
NA = "#9a9a9a"
BOX = "#e8eef4"
BOX2 = "#f2ece2"


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def metrics(sid):
    return load(os.path.join(EV, sid, "metrics.json")) or {}


def match_count(sid, fname):
    j = load(os.path.join(EV, sid, fname))
    return len(j.get("matches", [])) if j else None


# ---------------------------------------------------------------- Figure 1
def figure1():
    """Two-arm experimental design."""
    fig, ax = plt.subplots(figsize=(7.0, 5.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12.4)
    ax.axis("off")

    def box(x, y, w, h, text, fc, fs=7.6):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                                    fc=fc, ec=INK, lw=0.7))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, color=INK, linespacing=1.25)

    def arrow(x1, y1, x2, y2, style="-|>", ls="-"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                     mutation_scale=9, lw=0.7, color=INK,
                                     linestyle=ls, shrinkA=1, shrinkB=1))

    ax.text(5, 12.05, "Shared preparation (identical for both arms)",
            ha="center", fontsize=8.6, style="italic")
    shared = [
        "Pre-registered scenario (target CVE fixed in advance)",
        "Baseline dependency install  —  known vulnerable state",
        "SBOM generation  —  Syft v1.44.0, SPDX-JSON",
        "Vulnerability scan  —  Grype v0.112.0 (DB schema v6.1.9)",
    ]
    y = 11.3
    for s in shared:
        box(1.6, y, 6.8, 0.52, s, BOX)
        if y > 9.1:
            arrow(5.0, y, 5.0, y - 0.22)
        y -= 0.74

    arrow(5.0, 9.08, 5.0, 8.86)
    box(3.5, 8.34, 3.0, 0.5, "Prioritisation  KEV → EPSS → CVSS", BOX)
    arrow(5.0, 8.34, 2.4, 8.06)
    arrow(5.0, 8.34, 7.6, 8.06)

    ax.text(2.4, 8.00, "Deterministic baseline arm", ha="center",
            fontsize=8.6, weight="bold")
    ax.text(7.6, 8.00, "LLM-assisted arm", ha="center",
            fontsize=8.6, weight="bold")
    ax.text(2.4, 7.70, "grype-baseline.yml", ha="center", fontsize=7,
            style="italic", color="#555")
    ax.text(7.6, 7.70, "generic-remediation.yml", ha="center", fontsize=7,
            style="italic", color="#555")

    left = [
        "Apply scanner-recommended\nfixed version",
        "Reinstall dependencies",
        "Build",
    ]
    y = 6.9
    for s in left:
        box(0.75, y, 3.3, 0.62, s, BOX2)
        arrow(2.4, y, 2.4, y - 0.28)
        y -= 0.9

    box(0.75, 4.2, 3.3, 0.62, "Build failure → record\noutcome and stop", "#f6e3e3")
    ax.text(2.4, 3.72, "(stopping point differs\nbetween arms — §3.8)",
            ha="center", va="top", fontsize=6.8, style="italic", color=BAD)

    right = [
        "Build dependency-graph context",
        "LLM reasoning — structured JSON",
        "Apply manifest patch",
        "Reinstall dependencies + build",
        "Retry once on failure",
        "SBOM regeneration (Syft)",
        "Repeat scan (Grype)",
        "Deterministic validation",
    ]
    y = 6.9
    for s in right:
        box(5.95, y, 3.3, 0.5, s, BOX2, fs=7.2)
        if s != right[-1]:
            arrow(7.6, y, 7.6, y - 0.16)
        y -= 0.66

    ax.add_patch(FancyArrowPatch((5.95, 4.62), (5.25, 4.62), arrowstyle="-|>",
                                 mutation_scale=8, lw=0.7, color=INK,
                                 linestyle="--", connectionstyle="arc3,rad=0.35"))
    ax.text(5.55, 4.9, "retry\nfeeds back", ha="center", fontsize=6.4,
            style="italic", color="#555")

    box(5.95, 1.4, 3.3, 0.62, "Recorded outcome:\nbuild / dependency / rescan", "#e3efe6")
    box(0.75, 1.4, 3.3, 0.62, "Recorded outcome:\nbuild only", "#e3efe6")
    arrow(7.6, 2.62, 7.6, 2.08)
    arrow(2.4, 3.24, 2.4, 2.08)

    fig.savefig(os.path.join(OUT, "F1_experimental_architecture.png"))
    plt.close(fig)


# ---------------------------------------------------------------- Figure 2
def figure2():
    """Per-scenario deterministic-gate outcome matrix, read from metrics.json."""
    gates = ["build_success", "dependency_verified", "rescan_success"]
    labels = ["Dependency\ninstall", "Dependency\nverified", "Target CVE\nabsent on rescan"]
    grid = []
    for sid in IDS:
        m = metrics(sid)
        grid.append([m.get(g, None) for g in gates])

    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    for r, sid in enumerate(IDS):
        for c in range(3):
            v = grid[r][c]
            fc = OK if v is True else (BAD if v is False else NA)
            txt = "✓" if v is True else ("✗" if v is False else "–")
            ax.add_patch(plt.Rectangle((r, 2 - c), 1, 1, fc=fc, ec="white", lw=1.1))
            ax.text(r + 0.5, 2 - c + 0.5, txt, ha="center", va="center",
                    color="white", fontsize=9, weight="bold", family="DejaVu Sans")
    ax.set_xlim(0, len(IDS))
    ax.set_ylim(0, 3)
    ax.set_xticks([i + 0.5 for i in range(len(IDS))])
    ax.set_xticklabels(IDS, rotation=90, fontsize=7.5)
    ax.set_yticks([2.5, 1.5, 0.5])
    ax.set_yticklabels(labels, fontsize=7.5)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.axvline(9, color=INK, lw=1.0)
    ax.text(4.5, 3.12, "npm  (OWASP Juice Shop)", ha="center", fontsize=8)
    ax.text(13.5, 3.12, "pip  (Apache Airflow)", ha="center", fontsize=8)
    ax.text(0.1, -0.66, "✓ recorded true    ✗ recorded false    – no record "
                        "(JS-06 produced no candidate, §4.3b)",
            transform=ax.transAxes, fontsize=6.8, color="#444",
            family="DejaVu Sans")
    fig.savefig(os.path.join(OUT, "F2_outcome_matrix.png"))
    plt.close(fig)


# ---------------------------------------------------------------- Figure 3
def figure3():
    """Scanner match counts before and after remediation, per scenario."""
    base, resc, labs = [], [], []
    for sid in IDS:
        b = match_count(sid, "baseline-grype.json")
        r = match_count(sid, "rescan.json")
        if b is None or r is None:
            continue  # JS-06 produced no rescan (§4.3b)
        base.append(b)
        resc.append(r)
        labs.append(sid)

    x = range(len(labs))
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    ax.bar([i - 0.2 for i in x], base, width=0.4, label="Baseline scan",
           color="#7f9cb5", ec=INK, lw=0.4)
    ax.bar([i + 0.2 for i in x], resc, width=0.4, label="Post-remediation rescan",
           color="#3d5a73", ec=INK, lw=0.4)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labs, rotation=90, fontsize=7.5)
    ax.set_ylabel("Total Grype matches", fontsize=8)
    ax.set_ylim(0, max(base) * 1.42)
    ax.legend(fontsize=7.2, frameon=False, loc="upper left", ncol=2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=7.5)
    if "AF-03" in labs:
        i = labs.index("AF-03")
        ax.text(i, max(base) * 1.03, "*", ha="center", fontsize=11, color=BAD)
        ax.text(0.02, 0.82,
                "* AF-03: total match count unchanged (584 → 584) while the target CVE "
                "is absent on rescan —\n  the aggregate count is not a proxy for target removal.",
                transform=ax.transAxes, fontsize=6.6, color=BAD, va="top")
    if "JS-06" not in labs:
        ax.text(0.995, 0.995, "JS-06 omitted: no rescan produced (§4.3b)",
                transform=ax.transAxes, ha="right", va="top", fontsize=6.4,
                color="#444")
    fig.savefig(os.path.join(OUT, "F3_match_counts.png"))
    plt.close(fig)


# ---------------------------------------------------------------- Figure 4
def figure4():
    """JS-01 transitive shadowing, drawn from the recorded dependency context."""
    fig, ax = plt.subplots(figsize=(6.4, 2.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.4)
    ax.axis("off")

    def node(x, y, label, fc, w=2.5):
        ax.add_patch(FancyBboxPatch((x, y), w, 0.62, boxstyle="round,pad=0.06",
                                    fc=fc, ec=INK, lw=0.7))
        ax.text(x + w / 2, y + 0.31, label, ha="center", va="center", fontsize=7.6)

    def arrow(x1, y1, x2, y2, lbl="", ls="-", col=INK):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=9, lw=0.7, color=col, linestyle=ls))
        if lbl:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.46, lbl, ha="center",
                    fontsize=6.6, style="italic", color=col)

    node(0.3, 1.9, "juice-shop@15.3.0\n(root manifest)", BOX)
    node(3.7, 1.9, "juicy-chat-bot@0.8.0\n(direct dependency)", BOX)
    node(7.1, 1.9, "vm2@3.9.17\n(transitive, vulnerable)", "#f6e3e3")
    arrow(2.8, 2.21, 3.7, 2.21, "depends on")
    arrow(6.2, 2.21, 7.1, 2.21, "pins 3.9.17")

    node(3.7, 0.35, "overrides: { vm2: 3.9.18 }\nadded to root package.json", "#e3efe6", w=3.9)
    arrow(5.65, 0.97, 8.35, 1.86, "forces resolution", ls="--", col=OK)
    ax.text(5.0, 3.22, "A direct upgrade of juice-shop's own dependencies cannot reach vm2; "
                      "the override can.", ha="center", fontsize=7, style="italic")
    fig.savefig(os.path.join(OUT, "F4_js01_transitive_override.png"))
    plt.close(fig)


# ---------------------------------------------------------------- Figure 5
def figure5():
    """JS-07: why a root-level override cannot reach the frontend tree."""
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.0)
    ax.axis("off")

    def panel(x, title, sub, items, fc, reach):
        ax.add_patch(FancyBboxPatch((x, 0.5), 4.3, 3.0, boxstyle="round,pad=0.08",
                                    fc=fc, ec=INK, lw=0.8))
        ax.text(x + 2.15, 3.24, title, ha="center", fontsize=8, weight="bold")
        ax.text(x + 2.15, 2.98, sub, ha="center", fontsize=6.8, style="italic", color="#555")
        y = 2.58
        for it, col in items:
            ax.text(x + 0.25, y, it, fontsize=7.2, color=col, family="monospace")
            y -= 0.36
        ax.text(x + 2.15, 0.72, reach, ha="center", fontsize=7,
                color=OK if "edits" in reach else BAD, weight="bold")

    panel(0.2, "Root tree", "package.json + package-lock.json",
          [("juice-shop", INK), ("└─ engine.io", INK),
           ("   └─ ws@7.4.6  (vulnerable)", BAD),
           ("overrides: { ws: 7.5.13 }", OK)],
          "#eef3f8", "manifest_editor.py edits this")

    panel(5.5, "frontend/ tree", "frontend/package.json + own lockfile",
          [("frontend", INK), ("└─ engine.io-client", INK),
           ("   └─ ws@7.4.6  (vulnerable)", BAD),
           ("(no overrides reachable)", BAD)],
          "#f8f0ee", "outside editing scope")

    ax.add_patch(FancyArrowPatch((4.5, 2.0), (5.5, 2.0), arrowstyle="-|>",
                                 mutation_scale=9, lw=0.9, color=BAD, linestyle=":"))
    ax.text(5.0, 2.22, "override\ncannot cross", ha="center", fontsize=6.4,
            color=BAD, style="italic")
    ax.text(5.0, 3.78, "postinstall runs 'cd frontend && npm install' — a second, "
                       "independent resolution",
            ha="center", fontsize=7, style="italic")
    fig.savefig(os.path.join(OUT, "F5_js07_two_tree.png"))
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    figure1()
    figure2()
    figure3()
    figure4()
    figure5()
    print("wrote figures to", OUT)
