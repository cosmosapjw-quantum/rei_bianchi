#!/usr/bin/env python3
"""Publish source-free project-owner decision on genuine F05 next-map input."""
import argparse,hashlib,json,math
from pathlib import Path

ORIGINAL="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
ORIGINAL_KERNEL="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
PARENT="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823"
NEXT="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b"
RUST_JSON_SHA="8a10a20221588eaef386b17c7cb4038cfb99666ebdadd3976c1f04fa2510f8a2"
GATE=2e-4
WIDTH=2e-3
LANES=("primary","recomb","shield")

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()
def chk(p,msg):
    if not p:raise AssertionError("REI_OWNER_NATIVE_TICK161_"+msg)
def main(private,public,prior366):
    private=Path(private);public=Path(public)
    public.mkdir(parents=True,exist_ok=True)
    receipts={}
    for lane in LANES:
        d=private/(lane+"_tick161_parent_to_tick162")
        s=d/"REI_TICK162_V2_RESEARCH_NONPRODUCTION.npz"
        r=d/"SCIENTIFIC_CONSUMER_RECEIPT.json"
        chk(sha(s)==NEXT and r.is_file(),"SHA_"+lane)
        j=json.loads(r.read_text())
        chk(j["source_candidate_state_tick162_sha256"]==NEXT and
            j["source_parent_tick161_sha256"]==PARENT,"PARENT_CHAIN_"+lane)
        chk(j["source_parent_original_V1_failure_logT"]>GATE,"ORIGINAL_V1_FAIL_"+lane)
        chk(j["source_parent_original_V2_gate_logT"]<GATE,"ORIGINAL_T161_V2_PASS_"+lane)
        chk(j["original_source_tar_sha256"]==ORIGINAL and
            j["original_source_kernel_sha256"]==ORIGINAL_KERNEL,"ORIGINAL_REI_SOURCE_"+lane)
        chk(j["original_14_ledgers_include_zero"] is True and
            len(j["original_14_ledgers"])==14,"ORIGINAL_14_LEDGER_"+lane)
        chk(j["original_table_event_count"]==0,"TABLE_EVENT_"+lane)
        chk(max(j["original_V2_common_parent_local_defect_four_coordinates"].values())<GATE and
            max(j["original_width_four_coordinates"].values())<WIDTH,"UNCHANGED_SOURCE_GATE_"+lane)
        chk(len(j["actual_original_26event_full_half_maps"])==3 and
            all(z["native_certified"] for z in j["actual_original_26event_full_half_maps"]),"ACTUAL_ORIGINAL_MAPS_"+lane)
        chk(j["original_one_tick_physics_generated"] is True and
            j["status"]=="SOURCE_NATIVE_TICK161_ACTUALLY_CONSUMED_IN_NEXT_MAP","ACTUAL_CONSUMPTION_"+lane)
        chk(j["official_tick161_accepted"] is False and
            j["official_tick162_accepted"] is False and j["production"]=="HOLD",
            "CANONICAL_FALSE_PROMOTION_"+lane)
        receipts[lane]=j
    baseline=receipts["primary"]
    for lane in LANES[1:]:
        j=receipts[lane]
        for key in ("original_V2_common_parent_local_defect_four_coordinates",
                    "original_width_four_coordinates","source_conditional_delta_midpoint",
                    "source_conditional_delta_outer_intervals"):
            chk(j[key]==baseline[key],"THREE_LANE_IDENTICAL_PHYS_"+key)
    prior=json.loads(Path(prior366).read_text())
    chk(prior["candidate_pinned_npz_sha256"]==PARENT and
        prior["project_owner_original_F05_accepted"]=="160/131072" and
        prior["v2_canonical_accepted"] is False,"PR366_SOURCE_CANDIDATE")
    previous=prior["global_physics"]
    current=baseline["source_conditional_delta_midpoint"]
    sequential={
        "original_source_v2_t160_to161_midpoint": {
            "Ne":previous["delta_Ne_160_161_v2_mid"],
            "B":previous["delta_B_160_161_v2_mid_erg"],
            "U":previous["delta_U_160_161_v2_mid_erg"]
        },
        "original_source_v2_t161_to162_midpoint":current,
        "next_minus_previous_midpoint": {k:current[k]-v for k,v in
            (("Ne",previous["delta_Ne_160_161_v2_mid"]),
             ("B",previous["delta_B_160_161_v2_mid_erg"]),
             ("U",previous["delta_U_160_161_v2_mid_erg"]))},
        "intervals_are_unaccepted_research_states":True
    }
    rust=json.loads((private/"REI_F05_V2_T161_T162_RUST_EOS_SCIENCE.json").read_text())
    independent=json.loads((public/"RUST_INDEPENDENT_AUDIT.json").read_text())
    chk(sha(private/"REI_F05_V2_T161_T162_RUST_EOS_SCIENCE.json")==RUST_JSON_SHA,"RUST_SOURCE_LOCK")
    chk(rust["source_rows"]==46080 and rust["electron_interval_misses"]==0 and
        rust["thermal_interval_misses"]==0,"RUST_NODES_OR_CONE")
    chk(rust["rust_eos_max_rel_discrepancy"]<1e-14 and
        independent["rust_eos_source_full_46080_max_rel"]<1e-14,"RUST_EOS")
    chk(independent["source_rows"]==46080 and independent["source_next_tick162_SHA256"]==NEXT,
        "INDEPENDENT_AUDIT_SCOPE")
    witness_sha=sha(public/"REAL_24CELL_T161_T162_RUST_WITNESS.csv")
    assert witness_sha==independent["witness_csv_sha256"]
    artifact={
      "schema":"REI_F05_OWNER_VERSIONED_TICK161_GENUINE_CAUSAL_SOURCE_CONSUMPTION_V1",
      "project_owner_repo":"cosmosapjw-quantum/rei_bianchi",
      "source_original_F05_tar_SHA256":ORIGINAL,
      "source_original_26event_kernel_SHA256":ORIGINAL_KERNEL,
      "source_original_tick160_accepted":"160/131072",
      "source_v2_tick161_parent_SHA256":PARENT,
      "source_v2_tick162_research_SHA256":NEXT,
      "source_exact_three_lane_tick161_parent_bytes":True,
      "source_exact_three_lane_tick162_next_bytes":True,
      "source_original_physics_independent_realizations":1,
      "actual_original_source_cells":46080,
      "new_source_native_full_half_maps":9,
      "original_14_ledger_includes_zero":"3_OF_3_LANES_PASS",
      "source_original_table_events":0,
      "fixed_original_local_error_threshold":GATE,
      "fixed_original_width_threshold":WIDTH,
      "source_old_V1_tick160_to161_logT_fail":baseline["source_parent_original_V1_failure_logT"],
      "source_versioned_V2_tick160_to161_logT_upper":baseline["source_parent_original_V2_gate_logT"],
      "source_versioned_V2_tick161_to162_errors":
            baseline["original_V2_common_parent_local_defect_four_coordinates"],
      "source_versioned_V2_tick161_to162_widths":
            baseline["original_width_four_coordinates"],
      "source_native_161_to162_physical_delta_outer_intervals":
            baseline["source_conditional_delta_outer_intervals"],
      "source_native_161_to162_midpoint_changes":
            current,
      "source_conditioned_one_step_sequential_trend":sequential,
      "original_source_frozen_clock":{
        "t0":baseline["original_source_clock_hex"]["t0"],
        "tm":baseline["original_source_clock_hex"]["mid"],
        "t1":baseline["original_source_clock_hex"]["t1"],
        "duration":baseline["original_source_clock_hex"]["duration"]},
      "original_source_electron_thermal_Rust_real_46080": {
        "source_original_HHe_rust_schema":rust["schema"],
        "rust_46k_cell_EOS_maxrel":rust["rust_eos_max_rel_discrepancy"],
        "rust_46k_cell_thermal_interval_misses":0,
        "rust_46k_cell_electron_interval_misses":0,
        "rust_delta_ne_mid":rust["delta_ne_mid"],
        "rust_delta_B_mid_erg":rust["delta_B_mid_erg"],
        "rust_delta_U_mid_erg":rust["delta_U_mid_erg"],
        "rust_46k_electron_sign_classes":{
            "decrease":rust["definitely_decreasing_electron_cells"],
            "increase":rust["definitely_increasing_electron_cells"],
            "uncertain":rust["sign_ambiguous_cells"]}
       },
       "source_original_26event_full_worker_rust_port":False,
       "rust_source_actual_46k_output_private_SHA256":independent["rust_output_full_46080_sha256"],
       "rust_source_actual_46k_input_private_SHA256":independent["rust_input_original_source_sha256"],
       "independent_original_source_full_46k_audit_sha256":sha(public/"RUST_INDEPENDENT_AUDIT.json"),
       "source_free_witness24_sha256":witness_sha,
       "source_science_scope":"ACTUAL_T161_PARENT_CONSUMED_ONE_NATIVE_ORIGINAL_F05_SHADOW_STEP_TO_T162",
       "owner_scoped_decision":"PROMOTE_FOR_RESEARCH_NEXT_PARENT_CONSUMPTION_ONLY",
       "official_tick161_accepted":False,"official_tick162_accepted":False,
       "original_production_worker_mutated":False,
       "error_claim":"SOURCE_DISCRETE_MAP_GATE_ONLY_NOT_CERTIFIED_CONTINUUM_ODE_ERROR",
       "owner_publication":"DRAFT_RESEARCH_ONLY",
       "central_DAG":"28/88","working_DAG":"33/88","physical_fast_DAG":"4/7",
       "canonical_delta":0,"production":"HOLD","native_subagent":"NOT_RUN"
    }
    out=public/"SCIENCE_RESULT.json"
    out.write_text(json.dumps(artifact,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"source_owner_status":artifact["owner_scoped_decision"],
        "real_source_maps":artifact["new_source_native_full_half_maps"],
        "source_data":artifact["source_native_161_to162_midpoint_changes"],
        "rust_eos_discrepancy":rust["rust_eos_max_rel_discrepancy"],
        "science_result_sha256":sha(out)},sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for x in ("private","public","prior366"):
        p.add_argument("--"+x,required=True,type=Path)
    a=p.parse_args();main(a.private,a.public,a.prior366)
