"""Reproduce PHYS52 certified matching and noncertifying angular bench."""
import json,argparse
from pathlib import Path
from wu088_hh.phys52_outgoing_glue import (
    finite_band_robin_certificate,PhysicalScreenBlocks,assembly_benchmark
)
root=Path(__file__).resolve().parents[1]
arg=argparse.ArgumentParser()
arg.add_argument("--source",default=str(root/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"))
arg.add_argument("--out",default=str(root/"research/hh_phys52_20261015/results/PHYS52_MATCHED.json"))
arg.add_argument("--nodes",type=int,default=128)
arg.add_argument("--compare-nodes",type=int,default=256)
ns=arg.parse_args()
out=finite_band_robin_certificate(ns.source)
K=PhysicalScreenBlocks(ns.source,ns.nodes)
ref=PhysicalScreenBlocks(ns.source,ns.compare_nodes)
import numpy as np
errs={}
for m in [0,1,21,28]:
 a=K.matrix(m,27.0);b=ref.matrix(m,27.0)
 errs[str(m)]=float(np.max(np.abs(a-b))/np.max(np.abs(b)))
out["numerical_angular_diagnostics_NONCERT"]={
 "primary_nodes":ns.nodes,"reference_nodes":ns.compare_nodes,
 "radial_samples":[K.angular_certificate(r) for r in [27.0,30.0,43.0]],
 "quad_relative_difference":errs,
 "benchmark":assembly_benchmark(K,27.0,7),
}
target=Path(ns.out)
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({k:out[k] for k in ["schema","n_channels","current_lower_per_Bohr","matched_Robin_inverse_norm_upper_Bohr","entries_dense","entries_nonzero_signed_m_blocks","entries_unique_nonnegative_m_blocks"]},indent=2))
print("BENCHMARK",out["numerical_angular_diagnostics_NONCERT"]["benchmark"])
