import sys
sys.dont_write_bytecode=True
import hashlib, importlib.util, json, math
from pathlib import Path
root=Path("/home/cosmosapjw/Dropbox/bianchi/rei_bianchi")
probe=Path(__file__).resolve().parent
scope=json.loads((root/".cuh/fastest-track/REI-F05/review-scope.json").read_text())
def hashes():
    return {f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in scope}
before=hashes();assert before==scope
sourcefiles=["rust/rei_microphysics/src/adaptive_history.rs","rust/rei_microphysics/examples/first_interval.rs","rust/rei_microphysics/src/lib.rs"]
sid=hashlib.sha256(b"".join((root/f).read_bytes() for f in sourcefiles)).hexdigest()
pilot=root/".cuh/fastest-track/REI-F05/pilot"/sid
out=probe/"ledger_report_mutant";out.mkdir()
for level in range(3):
    summary=json.loads((pilot/f"level_{level}_summary.json").read_text())
    rows=[json.loads(line) for line in (pilot/f"level_{level}_transactions.jsonl").read_text().splitlines()]
    if level==0:
        p0=summary["initial_state"][4]
        rdim=[row["old_state"][4]-row["state"][4]-math.fsum(row["events"]["photo"][a][0] for a in range(3)) for row in rows]
        print(json.dumps({"source_id":sid,"observed_summary_photon0":summary["all_seven_ledgers"]["photon_group0_absorption"],"dimensional_residual_sum_over_initial_photon0":math.fsum(rdim)/p0}),flush=True)
    summary["all_seven_ledgers"]={k:0.0 for k in summary["all_seven_ledgers"]}
    for row in rows:row["ledgers"]={k:42.0 for k in row["ledgers"]}
    (out/f"level_{level}_summary.json").write_text(json.dumps(summary)+"\n")
    (out/f"level_{level}_transactions.jsonl").write_text("".join(json.dumps(row)+"\n" for row in rows))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
v=module("frozen_review_validator",root/".cuh/fastest-track/REI-F05/verify_candidate.py")
f=module("frozen_review_fast",root/".cuh/fastest-track/REI-F05/verify_whole_fast.py")
for name,expected in v.manifest["source_identity"].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected
stats=f.install_cache(v)
result=v.validate_run(out,True)
after=hashes();assert after==before
receipt={"probe":"ledger_reports_only_changed","result":result,"stats":stats,"source_id":sid,"frozen_hashes_before":before,"frozen_hashes_after":after,"mutations":{"summary_all_seven_ledgers":0.0,"row_ledgers":42.0,"state_box_event_changes":False}}
(probe/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps({"probe":"ledger_reports_only_changed","checker_status":result["status"],"uniformly_certified_trials":result["uniformly_certified_trials"],"frozen_hashes_unchanged":after==before,"stats":stats}),flush=True)
