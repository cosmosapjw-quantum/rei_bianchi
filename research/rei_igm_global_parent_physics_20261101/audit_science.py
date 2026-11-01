#!/usr/bin/env python3
"""Independent stdlib readback audit of original 46080-cell REI science output."""
import csv,gzip,hashlib,json,math,sys,decimal
from pathlib import Path

decimal.getcontext().prec=45
N=46080
MODES=("HI_to_HII","HeI_to_HeII")
def pct(a,q):
    a=sorted(a)
    z=(len(a)-1)*q/100
    i=int(z);j=min(i+1,len(a));frac=z-i
    return a[i]*(1-frac)+a[j]*frac

def main(folder):
    p=Path(folder).resolve()
    report=json.loads((p/"RESULT.json").read_text())
    assert report["canonical_delta"]==0 and report["unchanged_strict_gate"]==2e-4
    assert report["true_all_X_non_linear_interval_remainder"]=="NOT_CONSTRUCTED"
    assert report["parent_source_sha256"]=="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
    compressed=p/report["science_csv"]
    digest=hashlib.sha256(compressed.read_bytes()).hexdigest()
    assert digest==report["science_csv_sha256"]
    samples={k:[] for mode in MODES for k in (mode+"_dxe_total_coupled_MPRK",mode+"_dxe_global_photon",
        mode+"_dxe_finite_original_source",mode+"_global_fraction_abs_with_floor")}
    stats={mode:{"negative_total":0,"positive_total":0,"zero_total":0,"global_negative":0,
       "max_pointwise_relative_vs_finite":0.0,"max_abs_fd_difference":0.0,"max_fd_signal":0.0,"max_decomposition_absolute":0.0,
       "max_global_over_total_floor":0.0} for mode in MODES}
    witness_idx=set(round(k*(N-1)/23) for k in range(24))
    witnesses=[]
    with gzip.open(compressed,"rt",encoding="utf8",newline="") as f:
        read=csv.DictReader(f)
        keys=read.fieldnames
        assert len(keys)==1+report["scientific_output_columns"]
        for j,row in enumerate(read):
            assert int(row["node"])==j
            assert all(math.isfinite(float(v)) for k,v in row.items() if k!="node")
            if j in witness_idx: witnesses.append([row[k] for k in keys])
            for mode in MODES:
                def get(k):return float(row[mode+"_"+k])
                total=get("dxe_total_coupled_MPRK")
                finite=get("dxe_finite_original_source")
                glob=get("dxe_global_photon")
                other=get("dxe_other_local_electron_OTS")
                ratio=get("global_fraction_abs_with_floor")
                stat=stats[mode]
                stat["positive_total"]+=(total>0)
                stat["negative_total"]+=(total<0)
                stat["zero_total"]+=(total==0)
                stat["global_negative"]+=(glob<0)
                stat["max_pointwise_relative_vs_finite"]=max(stat["max_pointwise_relative_vs_finite"],
                   abs(total-finite)/max(abs(total),abs(finite),1e-100))
                stat["max_abs_fd_difference"]=max(stat["max_abs_fd_difference"],abs(total-finite))
                stat["max_fd_signal"]=max(stat["max_fd_signal"],abs(total),abs(finite))
                stat["max_decomposition_absolute"]=max(stat["max_decomposition_absolute"],
                   abs(total-(glob+other)))
                stat["max_global_over_total_floor"]=max(stat["max_global_over_total_floor"],ratio)
                for key in (mode+"_dxe_total_coupled_MPRK",mode+"_dxe_global_photon",
                            mode+"_dxe_finite_original_source",mode+"_global_fraction_abs_with_floor"):
                    samples[key].append(float(row[key]))
                if j in witness_idx:
                    tD=decimal.Decimal(row[mode+"_dxe_total_coupled_MPRK"])
                    gD=decimal.Decimal(row[mode+"_dxe_global_photon"])
                    oD=decimal.Decimal(row[mode+"_dxe_other_local_electron_OTS"])
                    assert abs(tD-gD-oD) <= decimal.Decimal("1e-18")
    assert j+1==N
    assert len(witnesses)==24
    for mode in MODES:
        stat=stats[mode]
        # Never divide by near-zero nodewise responses: use the mode-level
        # physical signal norm, and retain pointwise ratios only diagnostically.
        stat["mode_normalized_fd_error"]=stat["max_abs_fd_difference"]/max(stat["max_fd_signal"],1e-100)
        assert stat["mode_normalized_fd_error"]<3e-4
        assert stat["max_decomposition_absolute"]<1e-18
        assert stat["positive_total"]+stat["negative_total"]+stat["zero_total"]==N
        assert report["modes"][mode]["number_nonzero_amplitude_nodes"]==N
        stat["median_total"]=pct(samples[mode+"_dxe_total_coupled_MPRK"],50)
        stat["median_global"]=pct(samples[mode+"_dxe_global_photon"],50)
        stat["median_global_fraction_floor"]=pct(samples[mode+"_global_fraction_abs_with_floor"],50)
        stat["p95_global_fraction_floor"]=pct(samples[mode+"_global_fraction_abs_with_floor"],95)
    with (p/"INDEPENDENT_WITNESS_24.csv").open("w",encoding="utf8",newline="") as file:
        w=csv.writer(file);w.writerow(keys);w.writerows(witnesses)
    output={"schema":"REI_ORIGINAL26_PHYSICAL_PARENT_JVP_INDEPENDENT_AUDIT",
      "input_original_csv_sha256":digest,"rows_verified":N,"scientific_columns":len(keys)-1,
      "original_source":"ORIGINAL_HHE_MPRK22_26EVENT_FROZEN_TICK160",
      "source_FD_comparison":"PASS_SCOPED_DIRECTIONAL",
      "electron_JVP_decomposition":"PASS",
      "exact_photon_global_pr345_derivative":"VERIFIED_IN_MAIN_ORIGINAL_CALC",
      "modes":stats,"witness_nodes":sorted(witness_idx),
      "source_science_gate":"NOT_ALL_X","central_DAG":"28/88_REPORTED","canonical_delta":0}
    (p/"INDEPENDENT_AUDIT.json").write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("INDEPENDENT_ORIGINAL_JVP_AUDIT",json.dumps(output,sort_keys=True))
if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("python audit_science.py DIR")
    main(sys.argv[1])
