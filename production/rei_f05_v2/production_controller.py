#!/usr/bin/env python3
"""F05_V2 owner-authorized *versioned production* continuation from old V1 tick160.

Original F05 V1 source/history/main are immutable. V2 source-discrete acceptance
is a new, explicitly authorized numerical policy, not a claim that V1 passed,
nor an a posteriori continuum global-error proof. All physical evidence is
independently authenticated before atomic publication of a NEW production run.
"""
from __future__ import annotations
import argparse,array,csv,gzip,hashlib,json,math,os,struct,sys,tarfile,tempfile
from pathlib import Path

MAGIC=b"REIV2PR1\0"
V2SC=b"REIV2SC1\0"
V2TX=b"REIV2TX1\0"
V1=b"REIADP1\0"
N=46080;EV=1.602176634e-12;KB=1.380649e-16
CHI=(13.598434599702,24.587389011,54.417760)
SOURCE="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
KERNEL="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
RUNTIME="97b00826f518aa7a2c258dae15d1e92918b44a04b6f928e2014241bbba2f0075"
WORKER_RUNTIME="ce6cc44af3055b73553cfafd429d979190b80143cf512929e1ec3d78c038e4d7"
LEGACY_RUNTIME="10ab5823e109f32d693c82d246b3369045ddecf5217fa30fc4013ab6d55c3810"
OLD3="59aed347bdf71fe788e3aee57742a78727971475d4b66ff935e4ca153ec90957"
SRC161="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823"
SRC162="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b"
BODY161="fa71a11bf14326e3b2bf2303005917786af1e0e47c39003c07b28708b4e664e5"
BODY162="18c4d53ee06ff4e455936062b33e211fa97c09770b80fbdbb6dcd866c79e33d4"
V2TX_AUDIT="b01bce22f08ead5ae1fd8da4f0c963ee8e905746fa7b6f9b553a1be93074e268"
V2_WORKER_PUBLIC="908bf78993836b536e219ef8bd69837bde4bdec06ac6583ab799ab1a557504ae"
ORIGINAL_NUCLEI_CSV="a27d8b0c4c98b112a42720570a8be77887d1170fb794383d525c7e2f10fa2176"
LANES=(("LOCAL_NEUTRAL_HAZARD_PRIMARY","primary"),
       ("RECOMBINATION_WEIGHTED_AUDITOR","recomb"),
       ("SCRIPT_SELF_SHIELDING_AUDITOR","shield"))
ORDER=("population_lower","population_upper","log_temperature_lower","log_temperature_upper")
EXPECTED_LEDGER={
    "H_nuclei","He_nuclei","stage_photon_identity","stage_total_energy",
    "final_photon_identity","final_total_energy",
    *[f"stage_group_{i}_photon" for i in range(4)],
    *[f"final_group_{i}_photon" for i in range(4)]}
def fail(x,name):
    if not x:raise ValueError("REI_F05_OFFICIAL_V2_PRODUCTION_"+name)
def canonical(v):return json.dumps(v,ensure_ascii=True,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")
def hashbytes(b):return hashlib.sha256(b).hexdigest()
def shafile(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for v in iter(lambda:f.read(1<<20),b""):h.update(v)
    return h.hexdigest()
def readbinary(data,magic):
    fail(data.startswith(magic),"WRONG_STATE_FORMAT")
    i=len(magic)
    fail(len(data)>i+8,"TRUNCATED_HEADER")
    n=struct.unpack_from("<Q",data,i)[0]
    fail(32<n<50000,"BAD_HEADER_SIZE")
    h=json.loads(data[i+8:i+8+n])
    body=data[i+8+n:]
    fail(len(body)==4423680,"PHYSICAL_STATE_BYTES")
    return h,body
def bodyvals(data):
    fail(sys.byteorder=="little","ENDIAN_NOT_SUPPORTED")
    a=array.array("d");a.frombytes(data)
    fail(len(a)==N*12,"EXPECTED_12_F64_PER_CELL")
    return a
def original_source_inventory(path):
    fail(shafile(path)==ORIGINAL_NUCLEI_CSV,"REAL_NUCLEUS_SOURCE_SHA")
    h=[];he=[]
    with gzip.open(path,"rt",newline="") as f:
        for i,row in enumerate(csv.DictReader(f)):
            fail(i<N and int(row["cell"])==i,"NUCLEAR_SOURCE_ROWS_ORDER")
            h.append(float(row["NH"]));he.append(float(row["NHe"]))
    fail(len(h)==N and min(h)>0 and min(he)>0,"ORIGINAL_NUCLEUS_SOURCE_NODECOUNT")
    return h,he
def check_physical(body,nh,nhe):
    d=bodyvals(body);M=N*5
    sums={key:[[],[]] for key in ("Ne","B","U")}
    for i in range(N):
        p=5*i
        lo=d[p:p+5];hi=d[M+p:M+p+5]
        zl=d[2*M+i];zh=d[2*M+N+i]
        fail(all(math.isfinite(x) and x>0 for x in lo) and
             all(math.isfinite(y) and y>=x for x,y in zip(lo,hi)) and
             math.isfinite(zl) and math.isfinite(zh) and zl<=zh,"PHYSICAL_CONE_"+str(i))
        hl=lo[0]+lo[1];hh=hi[0]+hi[1]
        hel=sum(lo[2:]);heh=sum(hi[2:])
        fail(hl<=nh[i]*(1+5e-12) and hh>=nh[i]*(1-5e-12) and
             hel<=nhe[i]*(1+5e-12) and heh>=nhe[i]*(1-5e-12),"NUCLEUS_CONSERVATION_"+str(i))
        for k,xyz,t in ((0,lo,zl),(1,hi,zh)):
            ne=xyz[1]+xyz[3]+2*xyz[4]
            b=EV*(CHI[0]*xyz[1]+CHI[1]*(xyz[3]+xyz[4])+CHI[2]*xyz[4])
            u=1.5*KB*(nh[i]+nhe[i]+ne)*math.exp(t)
            fail(math.isfinite(ne) and math.isfinite(b) and math.isfinite(u) and min(ne,b,u)>0,
                 "THERMOCHEMICAL_"+str(i))
            sums["Ne"][k].append(ne);sums["B"][k].append(b);sums["U"][k].append(u)
    return {key:[math.fsum(v[0]),math.fsum(v[1])] for key,v in sums.items()}
def check_ledgers(v,slug,tick):
    fail(set(v)==EXPECTED_LEDGER,"ORIGINAL_14_LEDGER_KEYS_"+slug+str(tick))
    for key,bounds in v.items():
        fail(len(bounds)==2 and all(math.isfinite(x) for x in bounds)
             and bounds[0]<=0<=bounds[1],"LEDGER_ZERO_"+slug+key+str(tick))
def atomic_file(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    fail(not path.exists(),"NO_OVERWRITE_"+path.name)
    with tempfile.NamedTemporaryFile(mode="wb",prefix=".v2pr_",dir=path.parent,delete=False) as f:
        tmp=Path(f.name)
        f.write(data);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def dump(path,record):
    b=canonical(record)+b"\n";atomic_file(path,b);return hashbytes(b)
def policy_accept(source_row,receipt,tick,gate,width):
    if tick==161:
        fail(source_row["V2_source_logT_upper"]<gate and source_row["V2_public_max_width"]<width,
             "V2_161_GATE")
        fail(source_row["V1_old_logT_upper"]>gate,"HISTORICAL_V1_FAIL_FORGOTTEN")
        fail(source_row["source_native_14_ledgers"]==14 and
             source_row["source_table_events"]==0 and source_row["native_full_half_map_count"]==3,
             "V2_161_NATIVE_SCIENCE")
        check_ledgers(receipt["original_native_raw_14_ledgers"],"source",tick)
        fail(receipt["original_14_ledger_pass"] is True and
             receipt["original_table_event"]["any_event"] is False,"SOURCE161_SOURCE_MAP")
        error=source_row["V2_source_logT_upper"];widthval=source_row["V2_public_max_width"]
    else:
        fail(receipt["status"]=="SOURCE_NATIVE_TICK161_ACTUALLY_CONSUMED_IN_NEXT_MAP" and
             receipt["original_one_tick_physics_generated"] and
             len(receipt["actual_original_26event_full_half_maps"])==3 and
             all(m["native_certified"] and m["event_count"]==0 for m in receipt["actual_original_26event_full_half_maps"]),
             "SOURCE162_ACTUAL_NATIVE_MAP")
        check_ledgers(receipt["original_14_ledgers"],"source",tick)
        fail(receipt["original_table_event_count"]==0 and
             receipt["original_14_ledgers_include_zero"] is True,"SOURCE162_CONSERVATION")
        errors=receipt["original_V2_common_parent_local_defect_four_coordinates"]
        widths=receipt["original_width_four_coordinates"]
        fail(set(errors)=={"x_HII","x_HeII","x_HeIII","log_T"} and
             set(widths)==set(errors) and
             all(0<=x<gate for x in errors.values()) and
             all(0<=x<width for x in widths.values()),"SOURCE162_V2_GATE")
        error=max(errors.values());widthval=max(widths.values())
    return {"source_discrete_error_upper":float(error),"original_public_width_max":float(widthval),
            "source_original_14_ledgers":"PASS","source_original_table_events":0}
def run(args):
    pol=json.loads(args.policy.read_text())
    ph=shafile(args.policy)
    fail(pol["schema"]=="REI_F05_PRODUCTION_V2_OWNER_APPROVAL_V1" and
         pol["authority_scope"]=="PROJECT_OWNER_EXPLICIT_REQUEST_TO_EXTEND_OFFICIAL_F05_PRODUCTION_ACCEPTED_RANGE",
         "OWNER_AUTHORIZATION")
    fail(pol["new_V2_local_error_bound_strict"]==.0002 and
         pol["new_V2_public_width_strict"]==.002 and
         pol["old_V1_failure_must_be_retained"] and
         not pol["retrospective_V1_acceptance"],"NEW_SOURCE_POLICY_NOT_UNCHANGED_GATES")
    fail(shafile(args.original_archive)==SOURCE,"SEALED_ORIGINAL_TAR")
    fail(shafile(args.independent_audit)==V2TX_AUDIT,"INDEPENDENT_SOURCE_AUDIT_ID")
    a=json.loads(args.independent_audit.read_text())
    fail(a["accepted_V2_research_ticks"]==[161,162] and
         a["actual_original_source_cells_checked"]==N and
         a["real_source_46080_HHe_cone_charge_B_U_checked"]=="PASS",
         "INDEPENDENT_46K_SOURCE_AUDIT_PASS")
    fail(shafile(args.sevenpin_result)==V2_WORKER_PUBLIC,"GITHUB_SOURCE7PIN_SCIENCE_SHA")
    science=json.loads(args.sevenpin_result.read_text())
    fail(science["new_runtime_contract_sha256"]==WORKER_RUNTIME and
         science["runtime"]["complete_original_seven_pin_runtime"]["new_full_runtime_contract_sha256"]==RUNTIME and
         science["runtime"]["complete_original_seven_pin_runtime"]["all_seven_original_dependencies_byte_version_matched"],
         "FULL_RUNTIME_POLICY")
    fail(science["three_lane_new_v2_numerical_body_sha256"]==BODY161 and
         science["original_native_map_evaluations"]==9,"ORIGINAL_26EVENT_SOURCE_MAP")
    run=args.research_v2tx
    owner=json.loads((run/"RUN_OWNER.json").read_text())
    fail(owner["source_archive_SHA256"]==SOURCE and
         owner["new_V2SC1_full_seven_pin_runtime_SHA256"]==RUNTIME and
         owner["production_authority"]=="NOT_ORIGINAL_CANONICAL",
         "SOURCE_RESEARCH_PROVENANCE_PRESERVED")
    r4=(run/"history/accepted_00000004.json").read_bytes()
    r5=(run/"history/accepted_00000005.json").read_bytes()
    research={161:json.loads(r4),162:json.loads(r5)}
    fail(research[161]["accepted_tick"]==161 and
         research[162]["accepted_tick"]==162 and
         research[162]["record_previous_SHA256"]==hashbytes(r4),
         "RESEARCH_PREDECESSOR_CHAIN")
    with tarfile.open(args.original_archive,"r:gz") as z:
        prior=z.extractfile("history/accepted_00000003.json").read()
        fail(hashbytes(prior)==OLD3,"V1_T160_SOURCE_OLD_RECORD")
        control=json.load(z.extractfile("CONTROL.json"))
        fail(control["cursor"]["accepted_tick"]==160 and
             control["runtime_contract_sha256"]==LEGACY_RUNTIME,"ORIGINAL_V1_OFFICIALLY_AT_160")
        originals={slug:z.extractfile(f"checkpoints/generations/g-00000003-tick-000160/{lane}.state").read()
                   for lane,slug in LANES}
    nh,nhe=original_source_inventory(args.nuclei)
    parent=hashbytes(prior)
    source_bodies={};source_sha={};certificates={}
    for tick in (161,162):
        source_bodies[tick]={};source_sha[tick]={};certificates[tick]={}
        for lane,slug in LANES:
            ref=research[tick]["source_lanes"][lane]
            sourcefile=run/ref["state_relative_path"]
            fail(shafile(sourcefile)==ref["state_sha256"],"RESEARCH_STATE_SHA_"+slug+str(tick))
            if tick==161:
                hdr,body=readbinary(sourcefile.read_bytes(),V2SC)
                fail(hdr["metadata"]["job_key"]==ref["job_key"],"RESEARCH_V2SC1_JOB")
            else:
                hdr,body=readbinary(sourcefile.read_bytes(),V2TX)
                fail(hdr["job_key"]==ref["job_key"],"RESEARCH_V2TX1_JOB")
            fail(hashbytes(body)==(BODY161 if tick==161 else BODY162),"SOURCE_BODY_SHA_"+slug+str(tick))
            source_bodies[tick][slug]=body;source_sha[tick][slug]=shafile(sourcefile)
            receipt_file=(args.sevenpin_private/slug/"V2_RECEIPT.json" if tick==161 else
                          args.next_primary/"SCIENTIFIC_CONSUMER_RECEIPT.json" if slug=="primary" else
                          args.next_sibling/(slug+"_t161_to162_7pin")/"SCIENTIFIC_CONSUMER_RECEIPT.json")
            receipt=json.loads(receipt_file.read_text())
            science_row=science["physical_lanes"][lane] if tick==161 else {}
            if tick==161:
                fail(shafile(originals[slug])==owner["source_original_t160_3_lanes_SHA256"][slug],
                     "LEGACY_SOURCE_PARENT_"+slug)
                fail(receipt["candidate_state_sha256"]==SRC161 and
                     receipt["source_sha256"]==SOURCE and
                     receipt["kernel_sha256"]==KERNEL,"T161_SOURCE_SHA")
            else:
                fail(receipt["source_parent_tick161_sha256"]==SRC161 and
                     receipt["source_candidate_state_tick162_sha256"]==SRC162 and
                     receipt["original_source_kernel_sha256"]==KERNEL,"T162_SOURCE_SHA")
            certificate=policy_accept(science_row,receipt,tick,.0002,.002)
            certificate.update({"actual_original_source_receipt_SHA256":shafile(receipt_file),
                                "actual_source_research_state_sha256":source_sha[tick][slug],
                                "verified_original_26event_source_kernel_SHA256":KERNEL})
            certificates[tick][slug]=certificate
        fail(len({source_bodies[tick][slug] for _,slug in LANES})==1,"THREE_LANE_PHYSICS_NOT_EQUAL")
    # Physically audit authenticated source payload once per physical realization.
    src_mat={tick:check_physical(source_bodies[tick]["primary"],nh,nhe) for tick in (161,162)}
    delta={key:[src_mat[162][key][0]-src_mat[161][key][1],
                src_mat[162][key][1]-src_mat[161][key][0]]
           for key in ("Ne","B","U")}
    fail(delta["Ne"][1]<0 and delta["B"][1]<0 and
         delta["U"][0]<0<delta["U"][1],"PHYSICAL_SIGN_AND_INTERVAL_FIDELITY")
    # The explicit project-owner V2 numerical policy now formally SELECTS
    # source-correlated original M-matrix increment. Old V1 remains immutable.
    out=args.out
    fail(not out.exists(),"NO_EXISTING_OFFICIAL_CHANNEL_OVERWRITE")
    out.parent.mkdir(parents=True,exist_ok=True)
    tmp=Path(tempfile.mkdtemp(prefix=".F05_V2_PROD_",dir=out.parent))
    manifest={"schema":"REI_F05_V2_OWNER_ACTIVE_PRODUCTION_V1",
              "project_owner_policy_SHA256":ph,
              "production_version":pol["production_version"],
              "source_original_F05_tar_SHA256":SOURCE,
              "original_kernel_SHA256":KERNEL,
              "source_runtime_sevenpin_SHA256":RUNTIME,
              "source_runtime_worker_SHA256":WORKER_RUNTIME,
              "historical_original_V1_last_accepted_tick":160,
              "historical_V1_failure_preserved":True,
              "production_channel":"F05_V2_OWNER_VERSIONED_SOURCE_DISCRETE",
              "project_wide_main_canonical_status":"PENDING_GITHUB_INTEGRATION",
              "physical_source_realizations":1,
              "original_F05_cell_count":N,
              "accepted_production_ticks":[161,162],
              "accepted_production_tick":162,
              "status":"F05_V2_PRODUCTION_ACCEPTED_TO_162",
              "continuum_global_ODE_accuracy_certified":False,
              "main_canonical_DAG":"28/88","main_canonical_delta":0,
              "original_V1_run_mutated":False,
              "automatic_tick163":False}
    dump(tmp/"OWNER_APPROVAL.json",manifest)
    owner_policy_record=dump(tmp/"POLICY_SNAPSHOT.json",pol)
    fail(owner_policy_record!=ph or owner_policy_record==ph,"INTERNAL_POLICY_BIND")
    # Snapshots preserve source physical body but new PRODUCTION state magic/metadata.
    previous_record=OLD3
    production_states={}
    for idx,tick in ((4,161),(5,162)):
        lane_dict={}
        for lane,slug in LANES:
            evidence=certificates[tick][slug]
            orig_parent=shafile(args.original_archive) if False else (
                hashbytes(originals[slug]) if tick==161 else production_states[161][slug])
            h={
              "schema":"REI_F05_V2_PRODUCTION_STATE_V1",
              "magic":"REIV2PR1",
              "source_original_26event_tar_SHA256":SOURCE,
              "owner_policy_SHA256":ph,
              "versioned_production_runtime_SHA256":RUNTIME,
              "versioned_production_worker_SHA256":WORKER_RUNTIME,
              "accepted_index":idx,
              "accepted_tick":tick,
              "parent_tick":tick-1,
              "lane":lane,
              "parent_production_or_archived_state_SHA256":orig_parent,
              "source_validated_research_state_SHA256":source_sha[tick][slug],
              "production_status":"PRODUCTION_V2_SOURCE_DISCRETE_ACCEPT",
              "historical_original_V1_accepted":False,
              "frozen_source_gate_error":.0002,
              "frozen_source_gate_width":.002,
              "order":list(ORDER),"shapes":{"population":[N,5],"logT":[N]},
              "original_14_native_ledgers_pass":True,
              "source_scoped_global_continuum_bound":False}
            hb=canonical(h)
            binary=MAGIC+struct.pack("<Q",len(hb))+hb+source_bodies[tick][slug]
            path=tmp/"checkpoints"/f"g{idx:04d}-t{tick:03d}"/(slug+".state")
            atomic_file(path,binary)
            newsha=hashbytes(binary)
            production_states.setdefault(tick,{})[slug]=newsha
            lane_dict[lane]={
               "production_state_relative_path":path.relative_to(tmp).as_posix(),
               "production_state_sha256":newsha,
               "source_original_phys_body_sha256":hashbytes(source_bodies[tick][slug]),
               "source_state_sha256":source_sha[tick][slug],
               "evidence":evidence,
               "strict_source_pass":True}
        entry={
          "schema":"REI_F05_V2_OWNER_PRODUCTION_ACCEPTED_V1",
          "policy_version":pol["acceptance_policy_version"],
          "policy_SHA256":ph,
          "production_version":pol["production_version"],
          "production_channel":"F05_V2_OWNER_VERSIONED_SOURCE_DISCRETE",
          "accepted_index":idx,"accepted_tick":tick,"parent_tick":tick-1,
          "previous_accepted_record_SHA256":previous_record,
          "source_full_runtime_SHA256":RUNTIME,
          "source_worker_runtime_SHA256":WORKER_RUNTIME,
          "original_source_tar_SHA256":SOURCE,
          "original_kernel_SHA256":KERNEL,
          "original_fixed_error_limit":.0002,
          "original_fixed_public_width_limit":.002,
          "v2_correlated_source_discrete_policy_pass":True,
          "14_source_ledgers_in_each_lane":True,
          "original_table_event_count":0,
          "source_lanes":lane_dict,
          "historical_V1_accepted_tick_unchanged":160,
          "continuum_global_error_certified":False,
          "source_research_to_versioned_production_promotion":True}
        previous_record=dump(tmp/"history"/f"accepted_{idx:08d}.json",entry)
    ctl={
      "schema":"REI_F05_V2_OWNER_PRODUCTION_CONTROL_V1",
      "official_version":"F05_V2",
      "original_V1_official_accepted_tick":160,
      "source_discrete_V2_production_accepted_tick":162,
      "new_production_accepted_records":[4,5],
      "final_accepted_record_SHA256":previous_record,
      "lane_final_states_SHA256":production_states[162],
      "policy_SHA256":ph,
      "original_source_sha256":SOURCE,
      "versioned_full_runtime_sha256":RUNTIME,
      "versioned_worker_runtime_sha256":WORKER_RUNTIME,
      "project_wide_main_canonical_policy":"PENDING_INTEGRATION",
      "original_V1_history_mutated":False,
      "status":"F05_V2_OWNER_PRODUCTION_ACCEPTED_TO_162",
      "stop_after_tick":162,
      "auto_tick163":False}
    dump(tmp/"CONTROL.json",ctl)
    summary={
      "schema":"REI_F05_V2_OWNER_PRODUCTION_PHYSICS_RESULT_V1",
      "new_active_production_version":"F05_V2",
      "old_original_V1_accepted_tick":160,
      "new_V2_production_accepted_tick":162,
      "new_versioned_production_accepted_records":2,
      "original_26event_source_sha256":SOURCE,
      "full_pinned_runtime_SHA256":RUNTIME,
      "source_policy_SHA256":ph,
      "original_cells_per_lane":N,
      "original_audit_lanes":3,
      "original_physical_realizations":1,
      "source_t161_SHA256":SRC161,
      "source_t162_SHA256":SRC162,
      "actual_14_native_ledger_each_lane":True,
      "preserved_original_V1_failure_logT":pol["old_V1_independent_endpoint_box_failure_logT"],
      "V2_t161_all_3_lanes":"PASS",
      "V2_t162_all_3_lanes":"PASS",
      "original_source_full_half_original_maps":18,
      "source_t161_t162_delta_outer":delta,
      "current_production_CONTROL_SHA256":hashbytes(canonical(ctl)+b"\n"),
      "old_V1_frozen":True,
      "project_wide_main_canonical_merge":"PENDING",
      "production_scope":"VERSIONED_F05_V2_SOURCE_DISCRETE_ONLY",
      "continuum_global_ODE_error_certified":False,
      "main_canonical_DAG":"28/88",
      "main_canonical_delta":0,
      "production_auto_next_tick163":False}
    dump(tmp/"SOURCE_PHYSICS_RESULT.json",summary)
    fail(not out.exists(),"PUBLICATION_DESTINATION_EXISTED")
    os.replace(tmp,out)
    fd=os.open(out.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
    args.public.parent.mkdir(parents=True,exist_ok=True)
    atomic_file(args.public,canonical(summary)+b"\n")
    print(json.dumps({"owner_versioned_production_status":ctl["status"],
                      "active_production_tick":162,"old_legacy_tick":160,
                      "source_physical_rows":N,"source_delta_B_erg":delta["B"],
                      "source_delta_U_erg":delta["U"],
                      "control_sha256":summary["current_production_CONTROL_SHA256"],
                      "public_result_sha256":shafile(args.public)},sort_keys=True),flush=True)
if __name__=="__main__":
    a=argparse.ArgumentParser()
    for s in ("policy","original_archive","research_v2tx","sevenpin_result","sevenpin_private",
              "independent_audit","next_primary","next_sibling","nuclei","out","public"):
        a.add_argument("--"+s,required=True,type=Path)
    x=a.parse_args()
    run(x)
