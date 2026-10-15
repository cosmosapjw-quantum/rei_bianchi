#!/usr/bin/env python3
"""Immutable public supplier-code intake into a *separate* REI C11 worktree.

Source SHA is the exact public Git commit, captured payloads are verified Git blobs.
Original repos and source/production libraries are read-only.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parent
PINS={
    "bass_cr":"ff23e118a72d268bb44f24a35a0eb053a80bb2c8",
    "bass":"f3f741d8731380f734c7c4e6679e87d6a5d3bff3",
    "rec_bianchi":"8071d2e26d1befe2efe4599c5abd416d90e5e031",
    "WU088_HH":"4b36f178d5effa2ccf960d5285372f2f51d21327",
    "BASS_HE":"b0af50b052862320896085fac70250f51c077944",
}
ITEMS=[
 ("bass_cr","research/cr_c9_curvature_20261015/src/fast_compression.py","cr/fast_compression.py","e983ca5ee4ab3922bd298fce264a2950f861fe79"),
 ("bass_cr","research/cr_c5_budgeted_cohorts_20261015/src/compressed_cohorts.py","cr/compressed_cohorts.py","f368cebb4f9de3953f0b4592f9504e54ca53bca9"),
 ("bass_cr","research/cr_c9_curvature_20261015/src/curvature_bounds.py","cr/curvature_bounds.py","85d6067f2bde8316b83af72b03301709ea3c0f4f"),
 ("bass_cr","research/cr_c5_budgeted_cohorts_20261015/src/threshold_rt.py","cr/threshold_rt.py","02820ebe4f3492d0f1455035eb11f4beb37eac26"),
 ("bass_cr","research/cr_c9_curvature_20261015/src/directed_curvature.py","cr/directed_curvature.py","49c96ee8e3b1013f1cd0ddcc53e154afcaad8d65"),
 ("bass_cr","research/cr_c8_adaptive_q_20261015/src/adaptive_q.py","cr/adaptive_q.py","c9193ff714172a9cdd2bfa187c12a3f081f1ed51"),
 ("bass_cr","research/cr_c7a_shapefree_20261015/src/moment_envelopes.py","cr/moment_envelopes.py","5c73f7c995984a6c4af66e47bcc3343dbc1907a5"),
 ("bass","research/rei_axbi_shortstep_20261015/shortstep.py","bass/rei_axbi_shortstep_20261015/shortstep.py","9997b4fb9638770c2758781bb235ed000bd9e546"),
 ("bass","research/rei_axbi_background_supplier_20261015/axbi_provider.py","bass/rei_axbi_background_supplier_20261015/axbi_provider.py","cf08893bfdbaf8f4ce822df559ebc6b0f44f11dd"),
 ("bass","research/rei_axbi_background_supplier_20261015/source/REI_BACKGROUND_FAMILY_LOCK.json","bass/rei_axbi_background_supplier_20261015/source/REI_BACKGROUND_FAMILY_LOCK.json",None),
 ("rec_bianchi","src/full_bianchi_hyrec/trajectory/rei_initial_boundary.py","rec/rei_initial_boundary.py","20dd78f542962c92648bdc9763f9641bd2191214"),
 ("rec_bianchi","research/rec_r3c_rei_bridge_20261015/REI_DONOR_CANDIDATE_OPTIN_ONLY.json","rec/REI_DONOR_CANDIDATE_OPTIN_ONLY.json","1e3fdd5019f2a9a7d5ccd6a23e2f3a03faf74bd4"),
 ("WU088_HH","src/wu088_hh/phys44_rei_guard.py","wu/phys44_rei_guard.py","0d76ed75793e081ebb6b72989686d194e18f18e0"),
 ("WU088_HH","research/hh_phys44_20261015/results/REI_CONSUMER_PREFLIGHT.json","wu/REI_CONSUMER_PREFLIGHT.json","1a1223ce542672509fca382ad9465469e286c431"),
 ("BASS_HE","research/p01_remaining_cells_20261015/results/RESULT_STATUS.json","he/RESULT_STATUS.json","86001f8e87665112e6fc57e634d132a774b8068e"),
 ("BASS_HE","research/p01_remaining_cells_20261015/results/warm_P01_cumulative_tau.csv","he/warm_P01_cumulative_tau.csv",None),
]
def main():
    records=[]
    for repo,remote,local,expected in ITEMS:
        url=f"https://raw.githubusercontent.com/cosmosapjw-quantum/{repo}/{PINS[repo]}/{remote}"
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"REI-source-identity-test"}),timeout=25) as resp:
            raw=resp.read()
        gitsha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        if expected is not None and gitsha!=expected:
            raise RuntimeError(f"provider Git blob mismatch {repo}/{remote}: {gitsha} != {expected}")
        out=ROOT/"suppliers"/local
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_bytes(raw)
        records.append({"provider":repo,"commit":PINS[repo],"repo_path":remote,"local_path":str(out.relative_to(ROOT)),
                        "git_blob_sha1":gitsha,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"url":url})
        print("GIT_BLOB_MATCH",repo,local,gitsha,len(raw),flush=True)
    (ROOT/"SUPPLIER_SOURCE_MANIFEST.json").write_text(json.dumps(
        {"schema":"rei.crossrepo.source_intake.v1","sources":records,"source_use":"read-only snapshots in isolated REI bridge, not native production injection"},indent=2)+"\n")
if __name__=="__main__":main()
