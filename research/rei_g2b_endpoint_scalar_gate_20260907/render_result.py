"""Report an existing exact RESULT.json; never read or regenerate physical inputs."""
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
result = json.loads((HERE / "RESULT.json").read_text())
exact = {k: Fraction(int(v["numerator"]), int(v["denominator"]))
         for k, v in result["exact"].items()}
enclosures = {}
for name, value in exact.items():
    with localcontext() as context:
        context.prec = 20
        context.rounding = ROUND_FLOOR
        lower = Decimal(value.numerator) / Decimal(value.denominator)
        context.rounding = ROUND_CEILING
        upper = Decimal(value.numerator) / Decimal(value.denominator)
    assert Fraction(lower) <= value <= Fraction(upper)
    enclosures[name] = {"lower_decimal": str(lower), "upper_decimal": str(upper)}
quoted = None
if "conditional_L_G2b_upper" in exact:
    assert exact["conditional_L_G2b_upper"] < Fraction("1.914e52")
    quoted = "1.914e52"
(HERE / "DECIMAL_BOUNDS.json").write_text(json.dumps({
    "method": "Decimal precision 20 with FLOOR/CEILING, each side checked against exact Fraction; display/report bounds only",
    "values": enclosures,
    "quoted_L_upper_exact_decimal": quoted,
    "quoted_L_comparison": "strictly greater than exact conditional bound expression" if quoted else "NOT_APPLICABLE",
}, indent=2) + "\n")

names = ["HI contribution", "HeI contribution", "Total D lower"]
keys = ["H_contribution_lo", "He_contribution_lo", "D_lo"]
values = [float(exact[k] * 10**6) for k in keys]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
fig, ax = plt.subplots(figsize=(8.6, 4.7))
bars = ax.bar(names, values, color=["#2878a5", "#62a6c6", "#264653"], width=0.58)
ax.bar_label(bars, labels=[f"{v:.6f}" for v in values], padding=5)
ax.axhline(0, color="#333333", linewidth=0.8)
ax.set_ylim(min(0, min(values) * 1.15), max(values) * 1.22)
ax.set_ylabel(r"Upper-face contribution ($10^{-6}$ cMpc$^{-1}$)")
ax.set_title("G2b saved endpoint: denominator lower bound", loc="left", weight="bold", pad=27)
ax.text(0, 1.035, "Primary lane · 46,080 nodes · charged-fraction upper face",
        transform=ax.transAxes, fontsize=10, color="#555555")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.15)
ax.set_axisbelow(True)
fig.text(0.08, 0.025, "Display only. Exact fractions: RESULT.json. Saved endpoint inclusion remains an inherited assumption.",
         fontsize=8, color="#555555")
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(HERE / "neutral_contributions.png", dpi=150)
plt.close(fig)
print("Rendered neutral_contributions.png from exact RESULT.json; no scalar/producer rerun.")
