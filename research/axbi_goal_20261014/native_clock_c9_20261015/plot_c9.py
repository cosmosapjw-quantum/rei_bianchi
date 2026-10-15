"""Actual release Rust source-clock benchmark visualization, no invented speedup."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
E=ROOT/"evidence"
def main():
    objects=[json.loads(line) for line in (E/"NATIVE_BENCHMARK_FINAL.jsonl").read_text().splitlines()]
    rec=[r for r in objects if "mode" in r]
    names=["Original two Simpson4096","Local GL4 serial","Local GL4 2 threads","Local GL4 4 threads"]
    t=[r["median_s"]*1000 for r in rec]
    fig,ax=plt.subplots(figsize=(8.5,4.8))
    ax.barh(names,t)
    ax.set_xscale("log")
    ax.set(xlabel="Median wall time (ms), same 90 AX03 intervals",
           title="Native original cumulative-subtraction vs source-correct physical increments")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(E/"C9_NATIVE_CLOCK_BENCHMARK.png",dpi=175)
    plt.close(fig)
    print(str(E/"C9_NATIVE_CLOCK_BENCHMARK.png"))
if __name__=="__main__":main()
