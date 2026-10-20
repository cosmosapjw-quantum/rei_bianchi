from pathlib import Path
from decimal import Decimal, localcontext
from unittest.mock import patch
import hashlib, json, math, sys, time
ROOT=Path("/workspace/scratch/3fac997d7514/rei_repo")
TASK=ROOT/"research/rei_age_exposure_envelope_20261018"
UNIT=TASK/"native_age32_analysis_20261020"
REVIEW=Path(__file__).resolve().parent
sys.path.insert(0,str(UNIT))
import analysis as a
start=time.monotonic()
source_hash=hashlib.sha256((UNIT/"analysis.py").read_bytes()).hexdigest()
data=Path("/workspace/scratch/3fac997d7514/intake_backup/age32/run_corrected/results/age32/attempt001/data")
good=a.photon_history(data)
assert good["status"]=="AVAILABLE"
assert len(good["crosschecks"])==33 and all(x["status"]=="VERIFIED" for x in good["crosschecks"])
orig_read=a.read
orig_endpoint=orig_read(data/"endpoint.json")
mismatches=[]
for kind in ["N","photo"]:
    modified=json.loads(json.dumps(orig_endpoint))
    if kind=="N": modified["N"]*=2
    else: modified["ledgers"][4]*=2
    with patch.object(a,"read",side_effect=lambda p: modified if Path(p)==data/"endpoint.json" else orig_read(p)):
        changed=a.photon_history(data)
    assert changed["status"]=="INVALID"
    mismatches.append({"kind":kind,"status":changed["status"],"reason":changed["reason"]})
with localcontext() as ctx:
    ctx.prec=150
    expected=Decimal.from_float(1e300)*Decimal(-1000).exp()
    got=a.source_step(1e300,0,1,1000)["n1"]
    relative=float(abs(Decimal.from_float(got)-expected)/expected)
    assert got>0 and relative<2e-13
    x=Decimal(1491);midpoint_expected=float(x/((x/2).exp()-(-x/2).exp()))
    midpoint_got=a.midpoint_ratio(1491)
    ulp_error=abs(midpoint_got-midpoint_expected)/math.ulp(midpoint_expected)
    assert midpoint_got>0 and ulp_error<=1
    brackets=[]
    for eps in [1e-16,.005,.01,.1,.9]:
        limits=a.exposure_limits(eps)
        signs=[]
        for value in limits["continuum_bracket"]:
            x=Decimal.from_float(value)
            defect=1-x/((x/2).exp()-(-x/2).exp())
            signs.append(defect-Decimal.from_float(eps))
        assert signs[0]<=0<=signs[1]
        brackets.append({"epsilon":eps,"bracket":limits["continuum_bracket"],"independent_signs_decimal150":[str(v) for v in signs]})
final=orig_read(UNIT/"results/attempt004/ANALYSIS.json")
assert len(final["photon_histories"]["32"]["crosschecks"])==33
assert final["photon_histories"]["32"]["exact_zero_telescope_residual"]
assert final["photon_histories"]["64"]["status"]=="INCOMPLETE"
assert final["PRODUCTION_SCIENTIFIC_ADMISSION"]=="NOT_ISSUED"
for field in ["jumps","continuous","endpoint","telescope"]:
    assert final["photon_histories"]["32"][field]==good[field]
assert source_hash==hashlib.sha256((UNIT/"analysis.py").read_bytes()).hexdigest()
out={"schema":"rei.v9.c9_targeted_recheck.v1","status":"PASS_SCOPED","source_sha256":source_hash,
     "C9-01":{"actual_crosschecks":33,"all_verified":True,"endpoint_mismatch_rejections":mismatches},
     "C9-02":{"weighted_survival":got,"independent_expected_decimal150":str(expected),"relative_error":relative,
              "midpoint_ratio_x1491":midpoint_got,"expected_binary64":midpoint_expected,"ulp_error":ulp_error},
     "C9-03":{"independent_precision":150,"brackets":brackets},
     "authoritative_output":"results/attempt004/ANALYSIS.json",
     "analysis_sha256":hashlib.sha256((UNIT/"results/attempt004/ANALYSIS.json").read_bytes()).hexdigest(),
     "wall_seconds":time.monotonic()-start,"native_runs":0,"v8_campaign_runs":0}
(REVIEW/"C9_TARGETED_RECHECK.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))

