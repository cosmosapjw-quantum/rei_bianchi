"""Generate conditional angular b bounds figure, no physical source/data fitting."""
from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0,str(Path(__file__).resolve().parent / "src"))
import angular_moments as a

Lvals=np.geomspace(1/700,1/100,27)
results=[a.outer_interval(str(L),43,80) for L in Lvals]
fig,ax=plt.subplots(figsize=(9.6,5.0))
ax.fill_between(Lvals,[float(x["b_outer_lower"]) for x in results],
                [float(x["b_outer_upper"]) for x in results],alpha=.13,
                label="Outer interval (not sharp)")
for key,label,ls in [
    ("b_outer_lower","Outer lower","-"),
    ("b_outer_upper","Outer upper","-"),
    ("b_feasible_lower_envelope","Feasible f_minus","--"),
    ("b_feasible_upper_envelope","Feasible f_plus",":"),
]:
    ax.plot(Lvals,[float(x[key]) for x in results],linestyle=ls,linewidth=1.8,label=label)
ax.set_xscale("log")
ax.set_xlabel("Assumed L [nb / (sr degree)]")
ax.set_ylabel("Normalized b = <cos^2(theta)>")
ax.set_title("Conditional angular-moment bounds, gamma + He4 -> d + d, 330 MeV")
ax.set_ylim(.04,.66)
ax.grid(alpha=.25)
ax.legend(loc="center left",bbox_to_anchor=(1.01,.5),frameon=False,fontsize=9)
fig.tight_layout()
out=Path(__file__).parent/"results"/"angular_moment_enclosure.png"
fig.savefig(out,dpi=190)
print(out)
