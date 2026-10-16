#!/usr/bin/env python3
"""Independent BASS source-table/Rust producer point comparison on NCP."""
import json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).with_name("source_reference")))
from source_table import BackgroundTable, AREF

root=Path(sys.argv[1])
prefix=sys.argv[2] if len(sys.argv)>2 else "validated"
source=root/"research/bass_dynamic_20261016/source_grids/matched_n121_241_481_retry"
out={"schema":"bass.rei.python_rust_clock_comparison.v1","reference_source_table_sha256":"6b8580bf7e065d03b15a3c5b2d9a810d04ae883b538795ea5b575e428310783e","runs":[]}
for grid in (121,241,481):
    d=source/f"n{grid:04d}"
    table=BackgroundTable(d/"PRODUCER_RECEIPT.json",d/"PROPOSED_REI_BACKGROUND.csv")
    for tag,case in (("cold","COLD_FLRW"),("signed","SIGNED_MINUS")):
        for span in ("long","short"):
            native=json.loads((root/f"{prefix}_{tag}_{span}_g{grid}"/"result.json").read_text())
            ref=table.point_at_x(case,math.log(native["a"]/AREF))
            residual={"time_s":native["time_s"]-ref.time_s,"b":native["b"]-ref.b,"h_per_s":native["h_per_s"]-ref.h_per_s,"s_per_s":native["s_per_s"]-ref.s_per_s}
            normalized={"time_s":abs(residual["time_s"])/max(abs(ref.time_s),1.0),"b":abs(residual["b"])/max(abs(ref.b),1e-30),"h_per_s":abs(residual["h_per_s"])/max(abs(ref.h_per_s),1e-30),"s_per_s":abs(residual["s_per_s"])/max(abs(ref.s_per_s),1e-30)}
            out["runs"].append({"case":case,"span":span,"grid":grid,"residual":residual,"normalized":normalized})
out["max_time_relative"]=max(x["normalized"]["time_s"] for x in out["runs"])
out["max_h_relative"]=max(x["normalized"]["h_per_s"] for x in out["runs"])
print(json.dumps(out,indent=2,sort_keys=True))
