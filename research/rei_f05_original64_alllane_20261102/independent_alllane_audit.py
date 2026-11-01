#!/usr/bin/env python3
"""Independent stdlib source/bytes/physical audit for original REI F05 [0,64] all lanes.
Does NOT import original_worker, replay_all_lane_original64 or state_io."""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, math, struct, sys, tarfile
from array import array
from pathlib import Path

LANES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR","SCRIPT_SELF_SHIELDING_AUDITOR")
SRC_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
FIRST_SHAS={
"LOCAL_NEUTRAL_HAZARD_PRIMARY":"aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425",
"RECOMBINATION_WEIGHTED_AUDITOR":"b9b1c383a3b697770528481f9cfa35989c61e17609c0100ef27b8c8cda337d9d",
"SCRIPT_SELF_SHIELDING_AUDITOR":"31a763fdca76eb4d0b3fb03276342733dd1618bc2c7df22c3b00ba80691604fa"
}
KB=1.380649e-16
EV=1.602176634e-12
CHI_H=13.598434599702
CHI_HeI=24.587389011
CHI_HeII=54.417760
SIZE=46080

def digest(p):
    d=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):d.update(b)
    return d.hexdigest()

def read_original_state(path):
    data=Path(path).read_bytes()
    if data[:8]!=b"REIADP1\0":raise AssertionError("bad magic")
    (n,)=struct.unpack_from("<Q",data,8)
    if not(30<n<10000):raise AssertionError("state header bounds")
    h=json.loads(data[16:16+n].decode("ascii"))
    if h["schema"]!=1 or h["byte_order"]!="little" or h["dtype"]!="float64":
        raise AssertionError("state header semantic contract")
    if h["population_shape"]!=[SIZE,5] or h["log_temperature_shape"]!=[SIZE]:
        raise AssertionError("state physics shape")
    if h["array_order"]!=["population_lower","population_upper","log_temperature_lower","log_temperature_upper"]:
        raise AssertionError("state layout mismatch")
    body=data[16+n:]
    if len(body)!=8*(SIZE*5*2+SIZE*2):raise AssertionError("truncated physical body")
    assert sys.byteorder=="little"
    y=array("d");y.frombytes(body)
    if len(y)!=SIZE*12:raise AssertionError("state floats")
    N=SIZE*5
    for i in range(SIZE):
        for k in range(5):
            a=y[i*5+k];b=y[N+i*5+k]
            if not(0<a<=b and math.isfinite(a) and math.isfinite(b)):
                raise AssertionError(f"invalid_pop_{i}_{k}")
        a=y[2*N+i];b=y[2*N+SIZE+i]
        if not(math.isfinite(a) and math.isfinite(b) and a<=b):
            raise AssertionError(f"invalid_T_{i}")
    return h["metadata"],hashlib.sha256(body).hexdigest(),y

def near(a,b,eps=4e-14):
    return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=eps*max(abs(a),abs(b),1e-290)

def audit(archive,primary_state,private,original_source_input,public_json,out):
    if digest(archive)!=SRC_SHA:raise AssertionError("TAR_SOURCE_SHA")
    with tarfile.open(archive,"r:gz") as z:
        a=json.load(z.extractfile("receipts/attempt_00000001_000000_000064.json"))
    assert a["action"]=="ACCEPT"
    receipt={p["lane"]:p["envelope"] for p in a["processes"]}
    if set(receipt)!=set(LANES):raise AssertionError("source receipts")
    j=json.loads(Path(public_json).read_text())
    assert j["historical_all_lane_byte_identity"] is True
    assert j["source_map_rows_per_lane"]==SIZE and j["actually_new_native_lanes_recomputed"]==2
    rows_by_lane={v["lane"]:v for v in j["lanes"]}
    assert set(rows_by_lane)==set(LANES)
    with Path(original_source_input).open(newline="") as f:
        baseline=list(csv.DictReader(f))
    assert len(baseline)==SIZE
    ref_body=None;ref_rows=None;status=[]
    for lane in LANES:
        source_state=Path(primary_state) if lane==LANES[0] else private/(lane+".state")
        state_sha=digest(source_state)
        expected=FIRST_SHAS[lane]
        if state_sha!=expected or state_sha!=receipt[lane]["candidate_state"]["sha256"]:
            raise AssertionError("historical state SHA "+lane)
        meta,body_sha,values=read_original_state(source_state)
        if ref_body is None:ref_body=body_sha
        if ref_body!=body_sha:raise AssertionError("body differs across original shape lanes")
        old=receipt[lane]
        for key in ("accepted_index","input_lock_sha256","job_key","lane","parent_state_sha256",
                    "predecessor_kernel_sha256","runtime_contract_sha256","stage_id"):
            if meta[key]!=old[key]:raise AssertionError("archival original metadata key "+key)
        if meta["endpoint_tick"]!=64:raise AssertionError("state tick not 64")
        v=rows_by_lane[lane]
        assert v["byte_identical"] and v["replayed_state_sha256"]==expected
        if lane==LANES[0]:
            assert v["classification"]=="REUSED_VERIFIED_ORIGINAL64_RUST_OWNER_PR363"
            status.append({"lane":lane,"reused_prior_source":True,"sha256":state_sha,"body_sha256":body_sha})
            continue
        assert len(v["ledger_keys"])==14 and v["ledgers_all_include_zero"] and v["table_events"]==0
        assert all(x<2e-4 for x in v["replay_validated_local_bounds"].values())
        assert all(x<2e-3 for x in v["replay_widths"].values())
        assert v["max_abs_local_difference"]==0 and v["max_abs_width_difference"]==0
        if v["source_map_certification"]!=[True,True,True]:raise AssertionError("missing original half")
        csvfile=private/(lane+"_PHYSICAL_46080.csv.gz")
        if digest(csvfile)!=v["private_physical_csv_gz_sha256"]:raise AssertionError("generated csv sha mismatch")
        with gzip.open(csvfile,"rt",newline="") as f:
            rows=list(csv.DictReader(f))
        if len(rows)!=SIZE:raise AssertionError("wrong native physics row count")
        rawcsv=gzip.decompress(csvfile.read_bytes())
        csv_sha=hashlib.sha256(rawcsv).hexdigest()
        if ref_rows is None:ref_rows=csv_sha
        if csv_sha!=ref_rows:raise AssertionError("shape-lane physical rows are different")
        n=SIZE*5
        total={k:[] for k in ("Ne0","Ne64_lo","Ne64_hi","B0_erg","B64_lo_erg",
                             "B64_hi_erg","U0_erg","U64_lo_erg","U64_hi_erg")}
        max_rel=0.0
        for i,(base,r) in enumerate(zip(baseline,rows,strict=True)):
            if int(r["node"])!=i or int(base["node"])!=i:raise AssertionError("source rows reordered")
            lower=values; upper_offset=n
            hlo=values[i*5+1];hhi=values[n+i*5+1]
            hel=values[i*5+3];heh=values[n+i*5+3]
            he3l=values[i*5+4];he3h=values[n+i*5+4]
            tl=math.exp(values[2*n+i])
            th=math.exp(values[2*n+SIZE+i])
            nh=float(base["N_H"]);nhe=float(base["N_He"])
            ne0=float(base["N_HII_0"])+float(base["N_HeII_0"])+2*float(base["N_HeIII_0"])
            B0=EV*(CHI_H*float(base["N_HII_0"])+CHI_HeI*float(base["N_HeII_0"])+
                   (CHI_HeI+CHI_HeII)*float(base["N_HeIII_0"]))
            U0=1.5*KB*(nh+nhe+ne0)*float(base["T0_K"])
            nel=hlo+hel+2*he3l; neu=hhi+heh+2*he3h
            B_l=EV*(CHI_H*hlo+CHI_HeI*hel+(CHI_HeI+CHI_HeII)*he3l)
            B_h=EV*(CHI_H*hhi+CHI_HeI*heh+(CHI_HeI+CHI_HeII)*he3h)
            U_l=1.5*KB*(nh+nhe+nel)*tl
            U_h=1.5*KB*(nh+nhe+neu)*th
            calc={"Ne0":ne0,"Ne64_lo":nel,"Ne64_hi":neu,"B0_erg":B0,"B64_lo_erg":B_l,
                  "B64_hi_erg":B_h,"U0_erg":U0,"U64_lo_erg":U_l,"U64_hi_erg":U_h}
            for key,val in calc.items():
                observed=float(r[key])
                if not near(val,observed):
                    raise AssertionError(f"independent original physics {lane} {i} {key}: {val} {observed}")
                err=abs(val-observed)/max(abs(val),abs(observed),1e-290)
                max_rel=max(max_rel,err)
                total[key].append(val)
        sums={k:math.fsum(vals) for k,vals in total.items()}
        delta={
          "Ne":[sums["Ne64_lo"]-sums["Ne0"],sums["Ne64_hi"]-sums["Ne0"]],
          "B":[sums["B64_lo_erg"]-sums["B0_erg"],sums["B64_hi_erg"]-sums["B0_erg"]],
          "U":[sums["U64_lo_erg"]-sums["U0_erg"],sums["U64_hi_erg"]-sums["U0_erg"]]}
        for k,name in (("Ne","physical_interval_delta_Ne"),("B","physical_interval_delta_B_erg"),
                       ("U","physical_interval_delta_U_erg")):
            for got,expected in zip(delta[k],v[name]):
                # The difference of two extensive, close parent-state totals is
                # cancellation sensitive: compare with 64 ulps of positive parent sums.
                scale=max(abs(got),abs(expected),
                   abs(sums["Ne0"] if k=="Ne" else sums["B0_erg"] if k=="B" else sums["U0_erg"]))
                if abs(got-expected)>64*2.220446049250313e-16*scale:
                    raise AssertionError("original source extensive delta "+lane+" "+k)
        status.append({"lane":lane,"source_rows":len(rows),"sha256":state_sha,
                       "body_sha256":body_sha,"physical_decoded_sha256":csv_sha,
                       "max_cell_relative_error":max_rel,
                       "independent_extensive_changes":delta,
                       "source_acceptance_record":"CANDIDATE_UNSEALED_LOCAL_EXECUTION"})
    report={
      "schema":"REI_F05_ORIGINAL64_ALLLANE_INDEPENDENT_READBACK_V1",
      "original_source_archive_sha256":SRC_SHA,
      "original_3_lane_state_sha256":FIRST_SHAS,
      "original_physical_state_byte_body_equal":True,"common_physical_body_sha256":ref_body,
      "original_physical_source_csv_all_lane_byte_equal":True,
      "total_new_native_physical_rows_checked":SIZE*2,
      "physically_independent_realizations":1,
      "validation_mode":"SAME_AUTHOR_DISJOINT_STDLIB_STATE_DECODER_AND_PHYSICAL_FORMULAS",
      "exact_runtime_contract_recreated":False,
      "original_old_V1_fail_unchanged":True,
      "new_source_owner_tick161_accepted":False,
      "central_DAG":"28/88","production":"HOLD","lanes":status}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"independent_audit":"PASS","new_cells":SIZE*2,
     "state_body_sha256":ref_body,"all_lanes_SHA256_match":True,
     "csv_identical":True,"report_sha256":digest(out)},sort_keys=True))
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive",type=Path,required=True)
    ap.add_argument("--primary-state",type=Path,required=True)
    ap.add_argument("--previous-source",type=Path,required=True)
    ap.add_argument("--private",type=Path,required=True)
    ap.add_argument("--science",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    audit(a.archive,a.primary_state,a.private,a.previous_source,a.science,a.out)
