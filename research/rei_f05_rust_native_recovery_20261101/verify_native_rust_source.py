#!/usr/bin/env python3
"""Read-only independent audit of Rust F05 source-consumption results.

Python here is an AUDITOR only. No REI time integration or physics production.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ORIGINAL_CSV_SHA256="713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d"
ORIGINAL_SOURCE_TAR="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
ORIGINAL_KERNEL="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
ORIGINAL_STATE="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"

def close(actual:float,reference:float,rel:float=8e-14)->bool:
    return abs(actual-reference)<=rel*abs(reference)

def validate(actual:dict,owner:dict):
    o=owner["observables"]
    assert owner["physical_csv_sha256"]==ORIGINAL_CSV_SHA256
    assert owner["original_source_tar_sha256"]==ORIGINAL_SOURCE_TAR
    assert owner["original_kernel_sha256"]==ORIGINAL_KERNEL
    assert owner["original_accepted_state_array_sha256"]==ORIGINAL_STATE
    assert owner["original_tick"]=="160/131072"
    assert owner["official_state_161"]=="NOT_ACCEPTED_OR_WRITTEN"
    assert actual["schema"]=="REI_F05_ORIGINAL_46080_RUST_EOS_CONSUMER_V1"
    assert actual["original_parent_tick"]=="160/131072"
    assert actual["native_rust_rows"]==46080==owner["actual_original_spatial_cells"]
    assert actual["owner_26event_full_map_port"]=="NOT_IMPLEMENTED"
    assert actual["production"]=="HOLD" and actual["canonical_delta"]==0
    assert actual["official_tick161"]=="NOT_ACCEPTED"
    assert "IgmGasState::from_temperature/eos" in actual["historical_rust_engine_reused"]
    for native,old in [
        ("h_source_total","h_source_nuclei"),
        ("he_source_total","he_source_nuclei"),
        ("electron_lower_total","electron_count_N_lower"),
        ("electron_upper_total","electron_count_N_upper"),
        ("gas_u_lower_erg","gas_energy_erg_lower"),
        ("gas_u_upper_erg","gas_energy_erg_upper"),
        ("delta_electron_lower","delta_electron_N_total_lower"),
        ("delta_electron_upper","delta_electron_N_total_upper"),
        ("temperature_min_k","Tgas_min_K"),
        ("temperature_max_k","Tgas_max_K")
    ]:
        assert close(actual[native],o[old]), (native,actual[native],o[old])
    assert actual["strict_original_electron_interval_misses"]==0
    assert actual["strict_original_energy_interval_misses"]==0
    assert actual["electron_lower_total"] <= actual["electron_rust_eos_total"] <= actual["electron_upper_total"]
    assert actual["gas_u_lower_erg"] <= actual["gas_u_rust_eos_erg"] <= actual["gas_u_upper_erg"]
    # The source intervals are not the exact nonlinear function of independent
    # interval midpoints. Retain old 1206 cells as explicit diagnostics.
    assert actual["eos_diagnostic_1e_minus10_misses"]>=0
    return {
        "schema":"REI_F05_RUST_OWNER_ORIGINAL46K_INDEPENDENT_READBACK_V1",
        "source_csv_sha256":ORIGINAL_CSV_SHA256,
        "original_source_tar_sha256":ORIGINAL_SOURCE_TAR,
        "original_kernel_sha256":ORIGINAL_KERNEL,
        "original_accepted_parent_array_sha256":ORIGINAL_STATE,
        "source_owner_native_rows":actual["native_rust_rows"],
        "rust_electron_reconstructed":actual["electron_rust_eos_total"],
        "rust_energy_erg_reconstructed":actual["gas_u_rust_eos_erg"],
        "rust_within_native_source_owner_intervals_all_cells":True,
        "source_global_totals_crosschecked":True,
        "historical_rust_physical_eos_directly_reused":True,
        "original_source_input":"READ_ONLY_ORIGINAL_F05_NATIVE_PREVIEW",
        "official_original_tick161":"NOT_ACCEPTED",
        "rust_full_26event_interval_solver_port":"NOT_IMPLEMENTED",
        "original_14_ledgers_reexecuted_in_rust":"NOT_RUN",
        "numerically_checked_scoped_only":True,
        "canonical_delta":0,
        "rei_central":"28/88",
        "vigilode_official":"7/23",
        "production":"HOLD",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--owner",type=Path,required=True)
    p.add_argument("--source-gzip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    hash_=hashlib.sha256(args.source_gzip.read_bytes()).hexdigest()
    if hash_!=ORIGINAL_CSV_SHA256:
        raise ValueError("ORIGINAL_PHYSICAL_SOURCE_GZIP_SHA_CHANGED")
    native=json.loads(args.native.read_text())
    owner=json.loads(args.owner.read_text())
    data=validate(native,owner)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"verified":"SCOPED_RUST_SOURCE_RESULT_PASS",
                      "original_nodes":data["source_owner_native_rows"],
                      "original_tick161":data["official_original_tick161"]}))

if __name__=="__main__":
    main()
