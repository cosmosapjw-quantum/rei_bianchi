#!/usr/bin/env python3
"""Byte-locked original REI F08 first-step source intake, no simulation."""
import csv
import gzip
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARCHIVE = Path("/home/cosmosapjw/archives/BASS_REI_F08_S0_ORIGINAL_HAT_SUPPORT_20261101.zip")
ARCHIVE_SHA = "530370df21fd40e57165bd0882c17c25f684d571788c5c2db70f2c3105a48cfb"
P = "research/bass_rei_f08_s0_source_photon_thomson_20261101/source_inputs/"
Q = "research/bass_rei_f08_s0_remap_support_20261101/source_inputs/"
SHAS = {
    P+"science_scenario_v1.json": "c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1",
    P+"REI_ORIGINAL_atomic_provider.rs": "b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3",
    P+"S0_BI.csv.gz": "3096dc923520ec98da8c2e1dd3f03605cbf0809e944eeb5e4ceb6f58eff58893",
    P+"S0_FLRW.csv.gz": "cab6e37e0f375e06dc03218067fa74fe3f14455e2dcf41a03051965008acb521",
    P+"S0_BI-electron_density.csv.gz": "663911291bea564d314e1d46df9750c03a39fd5d9404eca6a7485776d894f723",
    P+"S0_FLRW-electron_density.csv.gz": "0b81cae87d6f90888d1d3def1995cd8d029625d1cc1dd11bffab94e8d30e7efa",
    Q+"S0_BI-header.jsonl": "a2a8bdd963febd1667d61e49ae027c02a2260208bbd9061c25117f1fdbe59082",
    Q+"S0_FLRW-header.jsonl": "7746d4f6e19ce59cdc3f0c8da300f6b5f12aa3b1c7e06d85cfc27ed89cff33db",
}

def sha(x):
    return hashlib.sha256(x).hexdigest()

def main():
    if sha(ARCHIVE.read_bytes()) != ARCHIVE_SHA:
        raise ValueError("FAIL_SOURCE_ARCHIVE_SHA")
    with zipfile.ZipFile(ARCHIVE) as z:
        if z.testzip() is not None: raise ValueError("FAIL_SOURCE_ARCHIVE_CRC")
        blobs = {name: z.read(name) for name in SHAS}
    for name, expected in SHAS.items():
        if sha(blobs[name]) != expected:
            raise ValueError("FAIL_SOURCE_MEMBER_SHA: "+name)
    provider_path=ROOT/"src"/"original_atomic_provider.rs"
    provider_path.write_bytes(blobs[P+"REI_ORIGINAL_atomic_provider.rs"])
    scenario=json.loads(blobs[P+"science_scenario_v1.json"])
    rows=[]
    report={"archive_sha256":ARCHIVE_SHA,"original_rust_atomic_sha256":SHAS[P+"REI_ORIGINAL_atomic_provider.rs"],
            "source_member_sha256":SHAS,"original_pairing":"F08_S0_original_16001_HHe_electron_samples",
            "first_step":625000000.0,"source_birth_ev":13.7,"source_birth_per_H":0.05,
            "photon_source_per_H_per_s":5e-15,"original_first_step_rows":[],"scope":"FROZEN_MATTER_FIRST_STEP_ONLY"}
    for label,geom in [("S0_BI","BIANCHI_I"),("S0_FLRW","FLRW")]:
        head=json.loads(blobs[Q+label+"-header.jsonl"])
        orig=next(csv.DictReader(io.StringIO(gzip.decompress(blobs[P+label+".csv.gz"]).decode())))
        electrons=list(csv.DictReader(io.StringIO(gzip.decompress(blobs[P+label+"-electron_density.csv.gz"]).decode())))
        if len(electrons)!=16001 or float(orig["time_s"])!=625000000.0:
            raise ValueError("FAIL_ORIGINAL_FIRST_STEP_CLOCK")
        row=electrons[1]
        if float(row["normal_time_s"])!=625000000.0:
            raise ValueError("FAIL_NH_CLOCK")
        nH=float(row["nH_proper_cm3"]); x=float(orig["x_HII"])
        nHI=nH*(1.0-x)
        if not(0<nHI<nH and 0<x<1): raise ValueError("FAIL_ORIGINAL_HI")
        energies=head["energy_nodes"]
        if len(energies)!=17 or not(abs(energies[11]-13.675)<1e-11 and abs(energies[12]-13.7)<1e-11):
            raise ValueError("FAIL_ORIGINAL_ENERGY_GRID")
        h=scenario["background"]["pairs"][geom]["H_per_s"]
        q=head["qhat"]
        if len(q)!=128 or len(h)!=3:raise ValueError("FAIL_ORIGINAL_Q_H")
        for i,v in enumerate(q):
            if len(v)!=3 or abs(sum(c*c for c in v)-1)>1e-12:
                raise ValueError("FAIL_ORIGINAL_Q_NORM")
            rows.append([label,i,*[format(float(t),".17g") for t in v],
                         *[format(float(t),".17g") for t in h],
                         format(nHI,".17g"),
                         format(float(energies[11]),".17g"),
                         format(float(energies[12]),".17g"),
                         format(float(orig["gamma_HI_per_s"]),".17g")])
        report["original_first_step_rows"].append(
            {"branch":label,"nH_proper_cm3":nH,"x_HII":x,"nHI_proper_cm3":nHI,
             "owner_full_coupled_gamma_HI_per_s":float(orig["gamma_HI_per_s"]),
             "original_ray_count":len(q),"original_energy_nodes":len(energies),
             "background_H_per_s":h})
    out=ROOT/"source_inputs"/"ORIGINAL_REI_F08_S0_FIRSTSTEP_256_RAYS.csv"
    with out.open("w",newline="") as f:
        wr=csv.writer(f,lineterminator="\n")
        wr.writerow(["branch","direction_id","qx","qy","qz","hx","hy","hz","nHI_cm3","e_lower_ev","e_upper_ev","owner_gamma_hi_per_s"])
        wr.writerows(rows)
    report["input_256_ray_csv_sha256"]=sha(out.read_bytes())
    (ROOT/"source_inputs"/"SOURCE_LOCK.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"native_input_rows":len(rows),"input_sha":sha(out.read_bytes()),
                     "original_atomic_sha":sha(provider_path.read_bytes()),
                     "branch_nhi":[(v["branch"],v["nHI_proper_cm3"]) for v in report["original_first_step_rows"]]},indent=2))

if __name__=="__main__":
    main()
