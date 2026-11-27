"""Render only the ten independently reviewed original printed source cells."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

leaf=Path(__file__).resolve().parents[1]
started_cpu=time.process_time();started_wall=time.monotonic()
path=leaf/"results/NATIVE_ROW_COMPUTED.json"
data=json.loads(path.read_text())
x=[];y=[]
for row in data["cells"]:
    f=row["nominal_m3_s_exact"]
    x.append(row["temperature_K"]);y.append(float(Fraction(int(f["numerator"]),int(f["denominator"]))))
assert len(x)==10 and min(y)>0
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,
                     "axes.spines.top":False,"axes.spines.right":False})
fig,ax=plt.subplots(figsize=(8.4,4.9),layout="constrained")
ax.scatter(x,y,s=44,color="#245c8a",edgecolor="#12364e",linewidth=.7,zorder=3)
ax.set_xscale("log");ax.set_yscale("log")
ax.set_xlabel("Temperature T [K]")
ax.set_ylabel(r"Printed raw SQM rate $k_{02,01}$ [$\mathrm{m^3\,s^{-1}}$]")
ax.set_title(r"H$^+$ + HD(0,2) $\rightarrow$ D$^+$ + H$_2$(0,1)",loc="left",pad=14)
ax.set_xticks([15,55,105,505,1505,3005])
ax.xaxis.set_major_formatter(ScalarFormatter())
ax.set_xlim(12,3900);ax.set_ylim(1e-20,6e-16)
ax.grid(which="major",color="#dfe4e8",linewidth=.7,zorder=0)
fig.supxlabel("GL2022 supplementary Table 2 | 10 source points | uncertainty unspecified\nRaw state-to-state values; thermal spin/population factors are not applied.",
               fontsize=9)
for suffix in ["png","svg"]:
    fig.savefig(leaf/"figures"/("NATIVE_J2_R1_SOURCE."+suffix),dpi=180)
plt.close(fig)
result={"schema":"wu.r18.figure_execution.v1","source_data_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
        "input_cells":10,"plotted_points":10,"connecting_lines":0,"invented_errorbars":0,
        "units":"m^3/s","x_axis":"log Kelvin","y_axis":"log nominal raw SQM rate",
        "matplotlib":matplotlib.__version__,"cpu_seconds":time.process_time()-started_cpu,
        "wall_seconds":time.monotonic()-started_wall,"exit_code":0}
(leaf/"results/FIGURE_EXECUTION.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))

