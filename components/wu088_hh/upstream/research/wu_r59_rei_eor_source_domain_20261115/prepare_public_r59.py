#!/usr/bin/env python3
"""Create small public genuine R59 source-cell witnesses, no invented sky data."""
from pathlib import Path
import csv,gzip,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"results"
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def run():
    result=json.loads((OUT/"R59_RESULTS.json").read_text())
    full=OUT/result["files"]["46080_real_source_cells"]
    assert sha(full)==result["files"]["sha256"]
    with gzip.open(full,"rt",newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==46080 and all(int(row["node"])==i for i,row in enumerate(rows))
    order=np.argsort([float(row["local_Thomson_tau_proxy_0_160"]) for row in rows],kind="stable")
    pick=np.unique(order[np.linspace(0,len(rows)-1,24,dtype=int)])
    names=["node","comoving_W","x_HII_tick0","x_HII_tick160","n_e_tick0_cm3",
           "n_e_tick160_cm3","original_T_tick160_K",
           "electron_column_cm_minus3_s_0_160","local_Thomson_tau_proxy_0_160"]
    witness=OUT/"R59_REAL_ORIGINAL_F05_THOMSON_WITNESS_24.csv"
    with witness.open("w",newline="") as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(names)
        for i in pick:w.writerow([rows[i][k] for k in names])
    public={
        "schema":"WU_R59_SOURCE_FREE_REI_EOR_SCENARIO_AND_REAL_THOMSON_V1",
        "project":"cosmosapjw-quantum/WU088_HH",
        "parent_WU_PR":198,
        "source_F05_HHe_184320_SHA256":result["source_SHA256"]["REI_F05_184320_27col"],
        "source_F05_photon_17_SHA256":result["source_SHA256"]["REI_F05_17_photon_knots"],
        "source_F08_true_640_SHA256":result["source_SHA256"]["BASS_F08_640_native_consecutive"],
        "F05_original_source":result["original_F05_source"],
        "F08_BASS_source":result["BASS_F08_source"],
        "physical_local_electron_Thomson":result["source_matched_Thomson_proxy"],
        "consumer_decision":result["physical_decision"],
        "original_46080_csv_SHA256":result["files"]["sha256"],
        "24_original_source_witness_sha256":sha(witness),
        "actual_46k_rows_not_published_on_GitHub":True,
        "owner_science_is_NOT_a_full_EoR_or_sky_tau":True,
        "science_DAG":result["DAG"],
        "independent_same_author_audit":json.loads((OUT/"R59_INDEPENDENT_AUDIT.json").read_text()),
        "source_owners":json.loads((OUT/"SOURCE_ABSORBER_OWNER_MATRIX.json").read_text())
    }
    p=OUT/"R59_SOURCE_FREE_SCIENCE.json"
    p.write_text(json.dumps(public,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"full_original_cells":len(rows),"original_full_sha256":sha(full),
        "witness_rows":len(pick),"witness_sha256":sha(witness),"public_sha256":sha(p)},sort_keys=True),flush=True)
if __name__=="__main__":run()
