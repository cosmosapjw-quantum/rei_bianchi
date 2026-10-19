#!/usr/bin/env python3
"""Fast exact binary64 replay of exported BR05 panel identities."""
import argparse
import csv
from datetime import datetime,timezone
import json
from pathlib import Path
from verify_panel_math import boundaries,sha

def check(monitor,outdir):
    names=["MONITOR_RULES.csv","MONITOR_PANELS.csv"]
    hashes={n:sha(monitor/n) for n in names}
    with (monitor/names[0]).open(newline="") as f:
        rules=list(csv.DictReader(f))
    with (monitor/names[1]).open(newline="") as f:
        panels=list(csv.DictReader(f))
    index={(int(v["step"]),int(v["rule_id"]),int(v["panel_id"])):v for v in panels}
    assert len(index)==len(panels)
    checked=set()
    for row in rules:
        key=(int(row["step"]),int(row["rule_id"]))
        reference=boundaries(float(row["tau"]),int(row["refinement"]))
        assert len(reference)==int(row["panels"])
        assert int(row["nodes"])==2*len(reference)
        for p,(left,right,width) in enumerate(reference):
            pk=(*key,p)
            observed=index[pk]
            assert float(observed["left_x"]).hex()==left.hex(),pk
            assert float(observed["right_x"]).hex()==right.hex(),pk
            assert float(observed["width_from_actual_weights"]).hex()==width.hex(),pk
            checked.add(pk)
    assert checked==set(index)
    assert all(sha(monitor/n)==h for n,h in hashes.items())
    outdir.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"BR05_NATIVE_PANEL_EXACT_REPLAY_V1","status":"PASS",
      "created_utc":datetime.now(timezone.utc).isoformat(),
      "script_sha256":sha(Path(__file__)),
      "helper_sha256":sha(Path(__file__).with_name("verify_panel_math.py")),
      "input_directory":str(monitor.resolve()),"input_sha256":hashes,
      "step_rules":len(rules),"panels":len(panels),"compared_binary64_boundary_fields":3*len(panels),
      "scope":"Exact replay of the published width recurrence and node-pair cardinality in every exported rule. The separate Decimal audit joins those panel IDs to actual native cohort rows."}
    (outdir/"NATIVE_PANEL_REPLAY_VERIFICATION.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({k:receipt[k] for k in ["status","step_rules","panels","compared_binary64_boundary_fields"]}))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--monitor-dir",type=Path,required=True)
    ap.add_argument("--out-dir",type=Path,required=True)
    args=ap.parse_args()
    check(args.monitor_dir,args.out_dir)

