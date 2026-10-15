#!/usr/bin/env python3
"""Original Rust Grackle owner oracle vs C11 PCHIP interpolation holdouts."""
from __future__ import annotations
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from rate_table import CaseARates

def main():
    cargo=os.environ.get("CARGO","cargo")
    target=Path(os.environ.get("CARGO_TARGET_DIR","/tmp/rei_source07_c11_cargo_target"))
    source=ROOT/"rust/rei_microphysics/examples/source07_c11_rates.rs"
    rust_owner=ROOT/"rust/rei_microphysics/src/igm_rates.rs"
    build=subprocess.run([cargo,"build","--offline","--release","--example",
                           "source07_c11_rates"],cwd=ROOT/"rust/rei_microphysics",
                         env={**os.environ,"CARGO_TARGET_DIR":str(target),
                              "CARGO_BUILD_JOBS":"2"},
                         text=True,capture_output=True)
    if build.returncode!=0:
        raise RuntimeError(build.stderr[-2000:])
    exe=target/"release/examples/source07_c11_rates"
    grid=CaseARates()
    points=np.geomspace(10000.07,23999.91,121)
    rows=subprocess.run([str(exe),"--points",*map(lambda x:format(x,".17g"),points)],
                         cwd=ROOT,text=True,capture_output=True,check=True)
    reference=np.genfromtxt(io.StringIO(rows.stdout),delimiter=",",skip_header=1)
    interpolation=np.array([grid(float(t)) for t in points])
    dif=np.abs(reference[:,1:]-interpolation)/reference[:,1:]
    maxima=dif.max(axis=0)
    index=np.unravel_index(np.argmax(dif),dif.shape)
    result={
        "schema":"rei.source07.c11.original_rust_igm_rate_heldout.v1",
        "node_count":len(grid.temperatures),"holdout_count":len(points),
        "highest_relative_difference":float(dif.max()),
        "max_rel_per_channel":maxima.tolist(),
        "worst_T_K":float(points[index[0]]),
        "worst_column":int(index[1]),
        "table_sha256":grid.sha256,
        "rust_owner_sha256":hashlib.sha256(rust_owner.read_bytes()).hexdigest(),
        "rust_example_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "rate_owner":"Grackle 3.4.1 af793... as implemented by rei_microphysics::igm_rates",
        "test":"121 independent exact Rust owner temperatures in interpolation interior; no extrapolation",
        "acceptance_max_rel":2e-7,
        "PASS":bool(dif.max()<2e-7)
    }
    (HERE/"RATE_VALIDATION.json").write_text(json.dumps(result,indent=2)+"\n")
    if not result["PASS"]:
        raise AssertionError("owner interpolation too inaccurate")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
