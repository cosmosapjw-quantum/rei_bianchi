#!/usr/bin/env python3
"""D8: adjacent saved-sample brackets, without ODE calls or root interpolation."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import numpy as np

ARCHIVE="7f3856bceea80f25e1f32d69f61cb40841a8461f66e1257bbd7eb79e01184498"

def atomic_write(path,content):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix="."+path.name,dir=path.parent)
    try:
        with os.fdopen(fd,"w") as f:
            f.write(content);f.flush();os.fsync(f.fileno())
        os.replace(name,path)
        directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if os.path.exists(name):os.unlink(name)

def brackets(catalog_path,histories_path):
    catalog=json.loads(catalog_path.read_text())
    digest=hashlib.sha256(histories_path.read_bytes()).hexdigest()
    if digest!=catalog["histories_sha256"] or catalog["source_archive_sha256"]!=ARCHIVE:
        raise ValueError("source identity mismatch")
    rows=catalog["cases"]
    with np.load(histories_path,allow_pickle=False) as a:
        if list(a["case_id"])!=[r["case_id"] for r in rows]:raise ValueError("case index mismatch")
        z=a["z_mean"].copy();S=(np.sqrt(6)*a["s"]/a["H"]).copy()
    if not np.all(np.diff(z)<0):raise ValueError("mean redshift must decrease")
    join=np.flatnonzero(abs(z-4)<1e-12)
    if len(join)!=1:raise ValueError("one exact z4 join expected")
    j4=int(join[0]);selected=[i for i,r in enumerate(rows) if r["joint_grid"] and r["Sigma_i"]==.003]
    if len(selected)!=25:raise ValueError("expected physical 25-point plane")
    found=[]
    for i in selected:
        if not (S[i,j4]>0 and S[i,-1]<0):continue
        indices=np.flatnonzero((S[i,j4:-1]>0)&(S[i,j4+1:]<0))+j4
        if len(indices)!=1:raise ValueError("expected one positive-to-negative saved transition per selected case")
        j=int(indices[0]);r=rows[i]
        found.append({"case_id":r["case_id"],"source_raw_sha256":r["source_raw_sha256"],
            "Sigma_i":r["Sigma_i"],"P_m_i":r["P_m_i"],"P_r_i":r["P_r_i"],
            "earlier_sample_index":j,"later_sample_index":j+1,
            "z_lower":float(z[j+1]),"z_upper":float(z[j]),
            "S_at_z_upper":float(S[i,j]),"S_at_z_lower":float(S[i,j+1]),
            "S_at_z4":float(S[i,j4]),"S_at_z2":float(S[i,-1])})
    found.sort(key=lambda r:(r["P_m_i"],r["P_r_i"]))
    if len(found)!=4:raise ValueError("current D8 contract expects exactly four cases")
    return {"schema":"HE30_D8_SAVED_SAMPLE_BRACKETS_V1","source_archive_sha256":ARCHIVE,
        "histories_sha256":digest,"bass_he_compact_results_commit":"65cc2af0caeaa4d5ce6aff37d72cf352cf24aaa7",
        "rei_published_source_results_commit":"3a525e3e16f1ba9393818a800327cc58597fd7b5",
        "upstream_next_node_observed_at":"744438f4512c7df1646aad0136ddc435b27200b0",
        "science_runs":0,"root_solver_calls":0,"interpolation":"NONE",
        "scope":"Open mean-redshift intervals between adjacent stored samples with opposite signed shear; continuity implies at least one crossing, not its precise time or uniqueness between samples.",
        "initial_shear":.003,"plane_cases":25,"late_reversals":4,"cases":found}

def main():
    default=Path(__file__).resolve().parents[1]/"results"
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--catalog",type=Path,default=default/"CATALOG.json")
    p.add_argument("--histories",type=Path,default=default/"histories.npz")
    p.add_argument("--out",type=Path,default=default)
    args=p.parse_args();report=brackets(args.catalog,args.histories)
    atomic_write(args.out/"LATE_REVERSAL_BRACKETS.json",json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    s=io.StringIO(newline="");w=csv.DictWriter(s,fieldnames=list(report["cases"][0]));w.writeheader();w.writerows(report["cases"])
    atomic_write(args.out/"late_reversal_brackets.csv",s.getvalue())
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
