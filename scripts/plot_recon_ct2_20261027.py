"""Plot inherited and unchanged ordinal CT2 values from the recorded ledgers."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
prior = json.loads((root / "research/ABH20_ATLAS_20261026/C09_RESULT.json").read_text(encoding="utf8"))
points = [prior["AB_R"]["CT2_after"]]
for i in range(1, 5):
    entry = json.loads((root / f"research/ABH_RECON_20261027/RC0{i}_RESULT.json").read_text(encoding="utf8"))
    before, after = entry["I"]["CT2_identity_before_after"]
    assert before == points[-1], "CT2 trajectory is not continuous"
    points.append(after)
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), layout="constrained")
labels = ["C09 previo", "RC01", "RC02", "RC03", "RC04"]
for ax, limits, label in zip(axes, [(0, 100), (25, 33)], ["Escala completa", "Vista ampliada"]):
    ax.plot(labels, points, marker="o", color="#32696a", linewidth=2)
    for i, point in enumerate(points):
        ax.annotate(str(point), (i, point), xytext=(0, 8), textcoords="offset points", ha="center")
    ax.set_ylim(*limits)
    ax.set_title(label)
    ax.set_ylabel("CT2 ordinal de identidad")
    ax.grid(axis="y", alpha=.25)
fig.suptitle("CT2 heredada: sin cambios en esta continuación")
fig.text(.5, -.04, "Juicio ordinal, no probabilidad. No se ha recalibrado por estas pruebas.", ha="center", fontsize=9)
fig.savefig(root / "research/ABH_RECON_20261027/CT2_IDENTIDAD.png", dpi=150, bbox_inches="tight")
