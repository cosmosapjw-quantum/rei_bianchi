#!/usr/bin/env python3
"""Two actual original F05 V2 accepted-research transactions: 160->161->162.

Requires source-authentic 7-pin 3-lane V2SC1 receipts and real subsequent original
full/half1/half2 physical maps. Writes a completely distinct REIV2TX1 on-disk
accepted-research history; NEVER the original REIADP1 V1 production history.
One bounded atomic source-scoped history advancement, stop at 162.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,shutil,struct,sys,tarfile,tempfile
from pathlib import Path
import numpy as np

SOURCE_TAR="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
SOURCE_KERNEL="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
V1_HIST_SHA="10ab5823e109f32d693c82d246b3369045ddecf5217fa30fc4013ab6d55c3810"
V2_FULL_RUNTIME="97b00826f518aa7a2c258dae15d1e92918b44a04b6f928e2014241bbba2f0075"
V2_JOB_RUNTIME="ce6cc44af3055b73553cfafd429d979190b80143cf512929e1ec3d78c038e4d7"
STATE161="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823"
STATE162="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b"
BODY161="fa71a11bf14326e3b2bf2303005917786af1e0e47c39003c07b28708b4e664e5"
GATE=2e-4;WIDTH=2e-3
LANES=(("LOCAL_NEUTRAL_HAZARD_PRIMARY","primary"),
       ("RECOMBINATION_WEIGHTED_AUDITOR","recomb"),
       ("SCRIPT_SELF_SHIELDING_AUDITOR","shield"))
N=46080
FIELDS=("population_lower","population_upper","log_temperature_lower","log_temperature_upper")
MAGIC_TX=b"REIV2TX1\0"
MAGIC_SC=b"REIV2SC1\0"

def sha(b):return hashlib.sha256(b).hexdigest()
def digest(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for x in iter(lambda:f.read(1<<20),b""):h.update(x)
 return h.hexdigest()
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")
def enforce(ok,msg):
 if not ok:raise ValueError("REI_F05_V2_TX_HISTORY_"+msg)
def atomic(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 enforce(not path.exists(),"DO_NOT_OVERWRITE_"+path.name)
 with tempfile.NamedTemporaryFile(dir=path.parent,prefix=".tmp_tx_",delete=False) as f:
  temp=Path(f.name)
  try:
   f.write(data);f.flush();os.fsync(f.fileno())
  finally:pass
 os.replace(temp,path)
 fd=os.open(path.parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def record(path,obj):
 b=canonical(obj)+b"\n";atomic(path,b);return sha(b)
def parse_state(path,magic):
 data=Path(path).read_bytes()
 enforce(data.startswith(magic),"STATE_FORMAT")
 offset=len(magic)
 (n,)=struct.unpack_from("<Q",data,offset)
 enforce(32<n<1_000_000,"STATE_HEADER_SIZE")
 header=json.loads(data[offset+8:offset+8+n])
 body=data[offset+8+n:]
 enforce(len(body)==4423680,"PHYSICAL_BODY_SHAPE")
 return header,body
def npz_body(path):
 enforce(digest(path) in (STATE161,STATE162),"UNAUTHORIZED_SOURCE_NPZ")
 with np.load(path,allow_pickle=False) as z:
  enforce(set(z.files)>=set(FIELDS),"NPZ_SOURCE_SCHEMA")
  arr=[]
  for name in FIELDS:
   a=np.asarray(z[name],dtype="<f8")
   enforce(a.shape==((N,5) if "population" in name else (N,)),"SOURCE_ARRAY_SHAPE")
   enforce(np.isfinite(a).all(),"SOURCE_FINITE")
   arr.append(np.ascontiguousarray(a).tobytes())
  for i in (0,2):
   low=np.asarray(z[FIELDS[i]])
   high=np.asarray(z[FIELDS[i+1]])
   enforce(np.all(low<=high),"SOURCE_INTERVAL_ORDER")
 return b"".join(arr)

def main(args):
 out=args.out.resolve()
 enforce(not out.exists(),"OUTPUT_MUST_BE_NEW")
 j=json.loads(args.sevenpin_result.read_text())
 enforce(j["schema"]=="REI_F05_NEW_SOURCE_ONLY_VERSIONED_V2_RESEARCH_WORKER_V1",
         "SEVENPIN_RESULT_SCHEMA")
 enforce(j["new_runtime_contract_sha256"]==V2_JOB_RUNTIME,
         "SEVENPIN_JOB_RUNTIME")
 runtime=j["runtime"]["complete_original_seven_pin_runtime"]
 enforce(runtime["new_full_runtime_contract_sha256"]==V2_FULL_RUNTIME and
         runtime["original_v1_sha256"]==V1_HIST_SHA,
         "FULL_AND_HISTORICAL_RUNTIME_BOUND")
 enforce(runtime["all_seven_original_dependencies_byte_version_matched"] and
         runtime["original_runtime_changed_fields"]==
          ["git_head","numeric_fingerprint.numpy_runtime_sha256"],
         "SEVEN_PIN_RUNTIME_DIFF_SCOPE")
 enforce(j["three_lane_new_v2_numerical_body_sha256"]==BODY161 and
         j["original_native_map_evaluations"]==9,"ORIGINAL_SOURCE_9MAP")
 enforce(j["original_accepted_tick"]=="160/131072" and
         j["official_accepted_161"] is False,"V1_NOT_OFFICIALLY_ACCEPTED")
 enforce(digest(args.archive)==SOURCE_TAR,"ORIGINAL_ARCHIVE_SHA")
 with tarfile.open(args.archive,"r:gz") as z:
  source_owner=json.load(z.extractfile("RUN_OWNER.json"))
  orig_control=json.load(z.extractfile("CONTROL.json"))
  orig_accept=z.extractfile("history/accepted_00000003.json").read()
  orig_history=json.loads(orig_accept)
  original_state_files={}
  for lane,slug in LANES:
   name=f"checkpoints/generations/g-00000003-tick-000160/{lane}.state"
   original_state_files[slug]=sha(z.extractfile(name).read())
 enforce(orig_control["cursor"]["accepted_tick"]==160 and
         orig_control["cursor"]["accepted_index"]==3,
         "ORIGINAL_FROZEN_T160_ACCEPTED")
 enforce(orig_control["runtime_contract_sha256"]==V1_HIST_SHA and
         source_owner["runtime_contract_sha256"]==V1_HIST_SHA,
         "ORIGINAL_RUNTIME_LOCK")
 enforce(j["number_of_original_physical_realizations"]==1,"NOT_THREE_UNIVERSES")
 # Verify exact real source evidence for the entire two-step chain before mutation.
 all_lanes={}
 body161s=set();body162s=set();source_clocks={}
 for lane,slug in LANES:
  v=j["physical_lanes"][lane]
  p161=args.sevenpin_private/slug
  source161=p161/"SHADOW_V2_NONAUTHORITATIVE_TICK161.npz"
  state161=p161/"VERSIONED_RESEARCH_V2_SOURCE_TICK161.state"
  rec161=json.loads((p161/"V2_RECEIPT.json").read_text())
  enforce(digest(source161)==STATE161 and digest(source161)==v["source_shadows_sha256"],
          "SOURCE161_"+slug)
  enforce(digest(state161)==v["versioned_state_sha256"],"V2SC1_"+slug)
  h,body=parse_state(state161,MAGIC_SC)
  enforce(sha(body)==BODY161 and body==npz_body(source161),
          "V2SC1_BODYSOURCE_"+slug)
  enforce(h["metadata"]["job_key"]==v["job_key"] and
          h["metadata"]["job"]["accepted_parent_state_sha256"]==
             j["original_source_history"][lane]["160"]["full_state_sha256"],
          "ORIGINAL_PREDECESSOR_"+slug)
  enforce(j["original_source_history"][lane]["160"]["full_state_sha256"]==
          original_state_files[slug],"ARCHIVED_ORIGINAL_F05_160_"+slug)
  enforce(v["V1_old_logT_upper"]>GATE and v["V2_source_logT_upper"]<GATE and
          v["V2_public_max_width"]<WIDTH,
          "OLD_V1_FAIL_AND_V2_PASS_"+slug)
  enforce(v["source_native_14_ledgers"]==14 and v["source_table_events"]==0,
          "ORIGINAL161_LEDGER_"+slug)
  enforce(rec161["original_14_ledger_pass"] and
          len(rec161["original_native_raw_14_ledgers"])==14 and
          not rec161["original_table_event"]["any_event"],
          "NATIVE_RECEIPT161_"+slug)
  d=(args.continuation_primary_root/"consumer_161_to_162" if slug=="primary" else
     args.continuation_other_root/(slug+"_t161_to162_7pin"))
  npath=d/"REI_TICK162_V2_RESEARCH_NONPRODUCTION.npz"
  receipt_path=d/"SCIENTIFIC_CONSUMER_RECEIPT.json"
  nxt=json.loads(receipt_path.read_text())
  enforce(digest(npath)==STATE162 and
          nxt["source_candidate_state_tick162_sha256"]==STATE162 and
          nxt["source_parent_tick161_sha256"]==STATE161,"NEXT162_PHYSICAL_"+slug)
  enforce(nxt["source_original_source_tar_sha256"]==SOURCE_TAR if
          "source_original_source_tar_sha256" in nxt else
          nxt["original_source_tar_sha256"]==SOURCE_TAR,
          "NEXT162_ORIGINAL_SOURCE_"+slug)
  enforce(nxt["original_source_kernel_sha256"]==SOURCE_KERNEL and
          nxt["original_14_ledgers_include_zero"] is True and
          len(nxt["original_14_ledgers"])==14 and
          all(a<=0<=b for a,b in nxt["original_14_ledgers"].values()) and
          nxt["original_table_event_count"]==0,"NEXT162_LEDGER_"+slug)
  enforce(max(nxt["original_V2_common_parent_local_defect_four_coordinates"].values())<GATE and
          max(nxt["original_width_four_coordinates"].values())<WIDTH and
          nxt["status"]=="SOURCE_NATIVE_TICK161_ACTUALLY_CONSUMED_IN_NEXT_MAP",
          "NEXT162_SOURCE_PHYSICAL_GATE_"+slug)
  enforce(nxt["official_tick161_accepted"] is False and
          nxt["official_tick162_accepted"] is False,"NO_FAKED_OFFICIAL_"+slug)
  source_clocks[slug]=nxt["original_source_clock_hex"]
  enforce(nxt["original_source_clock_hex"]["t0"]==rec161["clock_hex"]["t1"],
          "CLOCK_CONTIGUITY_"+slug)
  a162=npz_body(npath)
  body161s.add(sha(body));body162s.add(sha(a162))
  all_lanes[slug]={
   "lane":lane,"t160_original_state_sha256":original_state_files[slug],
   "t161_source_npz_SHA256":STATE161,"t161_state_SHA256":digest(state161),
   "t161_state_body_SHA256":sha(body),"t161_original_receipt_SHA256":digest(p161/"V2_RECEIPT.json"),
   "t161_job_key":v["job_key"],"t161_local_error_logT":v["V2_source_logT_upper"],
   "t161_public_max_width":v["V2_public_max_width"],
   "t162_source_npz_SHA256":STATE162,"t162_source_state_body_SHA256":sha(a162),
   "t162_original_receipt_SHA256":digest(receipt_path),
   "t162_local_error_max":max(nxt["original_V2_common_parent_local_defect_four_coordinates"].values()),
   "t162_public_width_max":max(nxt["original_width_four_coordinates"].values()),
   "t162_original_14_ledgers":14,"t162_original_table_events":0,
   "t162_material_midpoint_delta":nxt["source_conditional_delta_midpoint"],
   "_source_t161_file":state161,"_source_t162_npz":npath,
  }
 enforce(body161s=={BODY161} and len(body162s)==1 and len({canonical(clock) for clock in source_clocks.values()})==1,
         "THREE_LANE_ONE_PHYSICAL_REALIZATION")
 enforce(len({v["t161_job_key"] for v in all_lanes.values()})==3,
         "LANE_JOB_KEYS_DISTINCT")
 # Atomically initialize a NEW V2TX1 run directory, never an original V1 run.
 out.mkdir(parents=True)
 try:
  for slug,v in all_lanes.items():
   x=out/"checkpoints/g0004-tick161"/slug
   x.mkdir(parents=True,exist_ok=False)
   data=v["_source_t161_file"].read_bytes()
   atomic(x/"SOURCE_V2SC1_TICK161.state",data)
   enforce(digest(x/"SOURCE_V2SC1_TICK161.state")==v["t161_state_SHA256"],
           "CHECKPOINT161_COPY_"+slug)
   v["t161_checkpoint_relative"]=(x/"SOURCE_V2SC1_TICK161.state").relative_to(out).as_posix()
   r=out/"checkpoints/g0005-tick162"/slug
   r.mkdir(parents=True,exist_ok=False)
   parentstate=v["t161_state_SHA256"]
   job={"schema":"REI_V2TX1_JOB_V1","lane":v["lane"],
        "interval_ticks":[161,162],"accepted_index":5,
        "parent_v2sc1_state_sha256":parentstate,
        "parent_v2_source_npz_sha256":STATE161,
        "new_source_npz_sha256":STATE162,
        "source_native_26event_receipt_sha256":v["t162_original_receipt_SHA256"],
        "source_original_tar_sha256":SOURCE_TAR,"source_kernel_sha256":SOURCE_KERNEL,
        "versioned_worker_runtime_SHA256":V2_JOB_RUNTIME,
        "versioned_full_seven_pin_runtime_SHA256":V2_FULL_RUNTIME,
        "source_discrete_research_only":True,
        "official_V1_tick161_accepted":False}
   job_key=sha(canonical(job))
   h={"schema":"REI_V2TX1_STATE_V1","format":"REI_V2TX1_EXPERIMENTAL_ACCEPTED_NOT_REIADP1",
      "array_order":list(FIELDS),"dtype":"<f8","population_shape":[N,5],
      "log_temperature_shape":[N],
      "versioned_parent_state_SHA256":parentstate,
      "interval_ticks":[161,162],
      "job":job,"job_key":job_key,"source_original_not_official":True}
   hbyte=canonical(h)
   body=npz_body(v["_source_t162_npz"])
   new_state=MAGIC_TX+struct.pack("<Q",len(hbyte))+hbyte+body
   atomic(r/"SOURCE_V2TX1_TICK162.state",new_state)
   v["t162_checkpoint_relative"]=(r/"SOURCE_V2TX1_TICK162.state").relative_to(out).as_posix()
   v["t162_V2TX1_full_SHA256"]=sha(new_state)
   v["t162_V2TX1_job_SHA256"]=job_key
  # Persist immutable original bootstrap and two consecutive accepted V2 receipts.
  root_owner={
    "schema":"REI_F05_V2TX1_DISTINCT_SOURCE_PRODUCTION_CANDIDATE_HISTORY_V1",
    "source_archive_SHA256":SOURCE_TAR,"source_kernel_SHA256":SOURCE_KERNEL,
    "original_V1_runtime_SHA256":V1_HIST_SHA,
    "source_original_run_owner_SHA256":source_owner["runtime_contract_sha256"],
    "source_original_accepted_history3_SHA256":sha(orig_accept),
    "source_original_t160_3_lanes_SHA256":original_state_files,
    "new_V2SC1_full_seven_pin_runtime_SHA256":V2_FULL_RUNTIME,
    "new_V2SC1_worker_runtime_SHA256":V2_JOB_RUNTIME,
    "V1_production_original_readonly":True,
    "canonical_REI_DAG":"28/88",
    "branch_type":"SEPARATE_VERSIONED_V2_SOURCE_DISCRETE_ACCEPTED_RESEARCH_HISTORY",
    "production_authority":"NOT_ORIGINAL_CANONICAL",
    "single_source_realization":True}
  record(out/"RUN_OWNER.json",root_owner)
  prior=sha(orig_accept)
  for index,(left,right) in enumerate(((160,161),(161,162)),start=4):
   gen=out/f"checkpoints/g{index:04d}-tick{right:03d}"
   lanes={}
   for slug,v in all_lanes.items():
    key=f"t{right}_checkpoint_relative"
    sha_key="t161_state_SHA256" if right==161 else "t162_V2TX1_full_SHA256"
    state_path=out/v[key]
    enforce(digest(state_path)==v[sha_key],"MUTABLE_CHECKPOINT_"+slug)
    lanes[v["lane"]]={
      "state_relative_path":v[key],"state_sha256":v[sha_key],
      "source_npz_sha256":STATE161 if right==161 else STATE162,
      "original_source_receipt_sha256":
          v["t161_original_receipt_SHA256"] if right==161 else v["t162_original_receipt_SHA256"],
      "original_source_discrete_logT_local_error":
          v["t161_local_error_logT"] if right==161 else v["t162_local_error_max"],
      "original_public_width_max":
          v["t161_public_max_width"] if right==161 else v["t162_public_width_max"],
      "original_source_14_ledgers_include_zero":True,
      "original_table_events":0,
      "job_key":v["t161_job_key"] if right==161 else v["t162_V2TX1_job_SHA256"]}
   rec={
    "schema":"REI_V2TX1_ACCEPTED_RESEARCH_TRANSACTION_V1",
    "accepted_index":index,"parent_tick":left,"accepted_tick":right,
    "record_previous_SHA256":prior,
    "source_original_tar_SHA256":SOURCE_TAR,"source_kernel_SHA256":SOURCE_KERNEL,
    "source_full_seven_pin_runtime_SHA256":V2_FULL_RUNTIME,
    "source_worker_runtime_SHA256":V2_JOB_RUNTIME,
    "source_lanes":lanes,
    "original_fixed_local_gate":GATE,"original_fixed_width_gate":WIDTH,
    "original_source_26event_map_pass":"ALL_3_LANES",
    "V1_historical_end_box_failure_unchanged":True,
    "source_discrete_accept":True,
    "acceptance_namespace":"V2_EXPERIMENTAL_RESEARCH_NOT_V1_PRODUCTION",
    "canonical_accepted":False,"production":"HOLD",
    "original_canonical_F05_tick":160,"canonical_DAG":"28/88"}
   p=out/"history"/f"accepted_{index:08d}.json"
   prior=record(p,rec)
   record(gen/"GENERATION_RECEIPT.json",{
    "schema":"REI_V2TX1_CHECKPOINT_V1","index":index,
    "tick":right,"transaction_sha256":prior,
    "three_source_lanes":lanes,
    "original_production_modified":False})
  state_digest={v["lane"]:v["t162_V2TX1_full_SHA256"] for v in all_lanes.values()}
  final={
   "schema":"REI_V2TX1_TX_CONTROL_V1","accepted_count":5,
   "legacy_original_accepted_count":3,"legacy_original_accepted_tick":160,
   "new_versioned_branch_accepted_ticks":[161,162],
   "versioned_branch_accepted_tick":162,"versioned_branch_accepted_index":5,
   "history_last_record_sha256":prior,
   "checkpoint_state_sha256":state_digest,
   "original_source_tar_sha256":SOURCE_TAR,
   "versioned_full_runtime_sha256":V2_FULL_RUNTIME,
   "no_pending_automatic_next_step":True,
   "status":"STOP_AT_TICK162_VERSIONED_RESEARCH_TWO_ACCEPTED_TRANSACTIONS",
   "canonical_F05_tick_unchanged":160,
   "official_original_production_advance":False,
   "DAG_central":"28/88","DAG_working":"33/88","DAG_fast":"4/7",
   "canonical_delta":0,"production":"HOLD"}
  record(out/"CONTROL.json",final)
  s={
   "schema":"REI_F05_V2TX1_OWNER_REAL_TRANSACTIONAL_HISTORY_SCIENCE_V1",
   "original_legacy_V1_terminal_tick":160,
   "research_V2_transaction_accepted_ticks":[161,162],
   "research_V2_accepted_records":2,
   "real_native_source_original_maps_consumed_for_this_history":9+9,
   "real_native_source_node_count":N,
   "single_IGM_realization":True,
   "source_original_26event_source_SHA256":SOURCE_TAR,
   "new_V2SC1_full_runtime_SHA256":V2_FULL_RUNTIME,
   "new_V2SC1_runtime_bound_SHA256":V2_JOB_RUNTIME,
   "source_actual_t161_npz_SHA256":STATE161,
   "source_actual_t162_npz_SHA256":STATE162,
   "source_t161_full_physical_SHA256":BODY161,
   "source_t162_full_physical_SHA256":next(iter(body162s)),
   "source_t162_V2TX1_states_sha256":state_digest,
   "source_original_t160_state_sha256":original_state_files,
   "source_three_lanes_sha256_distinct":True,
   "all_14_original_ledgers_per_state":True,
   "source_original_table_events":0,
   "original_local_error_limit_unchanged":GATE,
   "original_width_limit_unchanged":WIDTH,
   "source_original_V1_failure_is_preserved":True,
   "transaction_first_SHA256":digest(out/"history/accepted_00000004.json"),
   "transaction_final_SHA256":prior,
   "full_private_transaction_control_SHA256":digest(out/"CONTROL.json"),
   "research_accepted_history":"V2TX1_TWO_REAL_SOURCE_CONDITIONAL_ACCEPTS",
   "distinct_original_canonical_acceptance":"HOLD_AT_T160",
   "no_automatic_t163":True,
   "source_owner_admission":"PROMOTE_EXPLICIT_VERSIONED_V2_TRANSACTIONAL_RESEARCH_HISTORY_ONLY",
   "canonical_DAG":"28/88","working_DAG":"33/88","fast_DAG":"4/7",
   "canonical_delta":0,"production":"HOLD"}
  (out/"SOURCE_SCIENCE_RESULT.json").write_text(json.dumps(s,indent=2,sort_keys=True)+"\n")
  print(json.dumps({"status":s["research_accepted_history"],"new_ticks":[161,162],
   "source_46080_cells":N,"lanes":3,
   "body_next_sha":s["source_t162_full_physical_SHA256"],
   "control_sha256":s["full_private_transaction_control_SHA256"],
   "last_transaction":prior,"DAG":"28/88","official":"HOLD"},sort_keys=True),flush=True)
 except Exception:
  # Preserve failure evidence for diagnosis and do not claim any accepted state.
  raise

if __name__=="__main__":
 p=argparse.ArgumentParser()
 for n in ("archive","sevenpin_result","sevenpin_private",
           "continuation_primary_root","continuation_other_root","out"):
  p.add_argument("--"+n,required=True,type=Path)
 main(p.parse_args())
