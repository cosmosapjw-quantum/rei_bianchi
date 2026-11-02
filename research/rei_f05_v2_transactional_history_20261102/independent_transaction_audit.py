#!/usr/bin/env python3
"""Disjoint stdlib-only hostile audit of real original F05 V2TX1 accepted history.

Never imports the V2TX writer, original source operator, NumPy, Rust or the V1
controller. Validates archived original tick160, both actual V2 transaction
chains, all 6 checkpoint binary states and 46,080 actual physical cell rows.
"""
from __future__ import annotations
import argparse,array,csv,gzip,hashlib,json,math,struct,sys,tarfile,tempfile
from pathlib import Path

N=46080
CHIH=13.598434599702
CHI1=24.587389011
CHI2=54.417760
EV=1.602176634e-12
KB=1.380649e-16
SOURCE_TAR="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
SOURCE161="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823"
SOURCE162="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b"
BODY161="fa71a11bf14326e3b2bf2303005917786af1e0e47c39003c07b28708b4e664e5"
FULL_RUNTIME="97b00826f518aa7a2c258dae15d1e92918b44a04b6f928e2014241bbba2f0075"
JOB_RUNTIME="ce6cc44af3055b73553cfafd429d979190b80143cf512929e1ec3d78c038e4d7"
LANES=(("LOCAL_NEUTRAL_HAZARD_PRIMARY","primary"),
       ("RECOMBINATION_WEIGHTED_AUDITOR","recomb"),
       ("SCRIPT_SELF_SHIELDING_AUDITOR","shield"))
FIELDS=("population_lower","population_upper","log_temperature_lower","log_temperature_upper")

def sha(v):return hashlib.sha256(v).hexdigest()
def sha_file(path):
 d=hashlib.sha256()
 with Path(path).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):d.update(b)
 return d.hexdigest()
def can(x):return json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":"),allow_nan=False).encode("ascii")
def require(c,msg):
 if not c:raise AssertionError("REI_F05_V2TX_INDEPENDENT_"+msg)
def readstate(data,magic):
 require(data[:len(magic)]==magic,"MAGIC")
 (size,)=struct.unpack_from("<Q",data,len(magic))
 require(32<size<1_000_000,"HEADER_LENGTH")
 header=json.loads(data[len(magic)+8:len(magic)+8+size])
 body=data[len(magic)+8+size:]
 require(len(body)==4423680,"PHYSICS_PAYLOAD_LENGTH")
 return header,body
def decode(body):
 require(sys.byteorder=="little","LITTLE_ENDIAN")
 dims=(N*5,N*5,N,N);result=[];off=0
 for count in dims:
  sl=body[off:off+count*8]
  a=array.array("d");a.frombytes(sl);off+=count*8
  require(len(a)==count,"ARRAY_LENGTH")
  result.append(a)
 require(off==len(body),"TRAILING")
 return result
def close(a,b,ref=None):
 s=max(abs(a),abs(b),abs(ref or 0),1e-300)
 return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=64*2.220446049250313e-16*s

def main(run,original_tar,continuation,original_nuclei_csv,out):
 require(sha_file(original_tar)==SOURCE_TAR,"ORIGINAL_ARCHIVE_SHA")
 require(sha_file(original_nuclei_csv)=="a27d8b0c4c98b112a42720570a8be77887d1170fb794383d525c7e2f10fa2176",
         "ORIGINAL_NUCLEUS_PROVENANCE_SHA")
 owner=json.loads((run/"RUN_OWNER.json").read_text())
 ctrl=json.loads((run/"CONTROL.json").read_text())
 require(owner["source_archive_SHA256"]==SOURCE_TAR and
         owner["new_V2SC1_full_seven_pin_runtime_SHA256"]==FULL_RUNTIME and
         owner["new_V2SC1_worker_runtime_SHA256"]==JOB_RUNTIME,
         "SOURCE_RUNTIME_IDENTITY")
 require(owner["V1_production_original_readonly"] is True and
         ctrl["official_original_production_advance"] is False and
         ctrl["canonical_F05_tick_unchanged"]==160 and
         ctrl["versioned_branch_accepted_tick"]==162 and
         ctrl["no_pending_automatic_next_step"] is True and
         ctrl["status"]=="STOP_AT_TICK162_VERSIONED_RESEARCH_TWO_ACCEPTED_TRANSACTIONS",
         "ORIGINAL_HISTORY_SCOPE")
 require(ctrl["accepted_count"]==5 and ctrl["legacy_original_accepted_count"]==3,
         "ACCEPTED_HISTORY_INDICES")
 with tarfile.open(original_tar,"r:gz") as tar:
  old3=tar.extractfile("history/accepted_00000003.json").read()
  historical={
   slug:tar.extractfile(
    f"checkpoints/generations/g-00000003-tick-000160/{lane}.state").read()
   for lane,slug in LANES
  }
 require(sha(old3)==owner["source_original_accepted_history3_SHA256"],
         "ORIGINAL_PREDECESSOR_LAST_RECORD")
 accepted={}
 prior=sha(old3)
 for idx,tick in ((4,161),(5,162)):
  p=run/"history"/f"accepted_{idx:08d}.json"
  raw=p.read_bytes();v=json.loads(raw)
  require(v["schema"]=="REI_V2TX1_ACCEPTED_RESEARCH_TRANSACTION_V1" and
          v["accepted_index"]==idx and v["parent_tick"]==tick-1 and
          v["accepted_tick"]==tick and v["record_previous_SHA256"]==prior,
          "HISTORY_CHAIN_"+str(idx))
  require(v["original_source_26event_map_pass"]=="ALL_3_LANES" and
          v["source_full_seven_pin_runtime_SHA256"]==FULL_RUNTIME and
          v["source_worker_runtime_SHA256"]==JOB_RUNTIME and
          v["source_original_tar_SHA256"]==SOURCE_TAR,"ORIGINAL_MAP_"+str(idx))
  require(v["source_discrete_accept"] is True and
          v["canonical_accepted"] is False and
          v["acceptance_namespace"]=="V2_EXPERIMENTAL_RESEARCH_NOT_V1_PRODUCTION",
          "NO_FAKED_ORIGINAL_CANONICAL_"+str(idx))
  require(v["original_fixed_local_gate"]==2e-4 and
          v["original_fixed_width_gate"]==2e-3 and
          v["V1_historical_end_box_failure_unchanged"],
          "FROZEN_LOCAL_GATES_"+str(idx))
  require(set(v["source_lanes"])=={a for a,_ in LANES},"ALL_LANES_"+str(idx))
  receipt=json.loads((run/f"checkpoints/g{idx:04d}-tick{tick:03d}"/
                      "GENERATION_RECEIPT.json").read_text())
  require(receipt["transaction_sha256"]==sha(raw) and
          receipt["tick"]==tick and receipt["index"]==idx,
          "CHECKPOINT_GENERATION_"+str(idx))
  accepted[idx]=v
  prior=sha(raw)
 require(prior==ctrl["history_last_record_sha256"],"FINAL_CONTROL_LAST_SHA")
 bodies={}
 states={}
 jobs={161:set(),162:set()}
 for tick,idx,magic in ((161,4,b"REIV2SC1\0"),(162,5,b"REIV2TX1\0")):
  bodies[tick]=set()
  states[tick]={}
  for lane,slug in LANES:
   e=accepted[idx]["source_lanes"][lane]
   f=run/e["state_relative_path"]
   require(f.is_file() and sha_file(f)==e["state_sha256"],"CHECKPOINT_BYTES_"+slug+str(tick))
   header,body=readstate(f.read_bytes(),magic)
   bodies[tick].add(sha(body))
   require(e["source_npz_sha256"]==(SOURCE161 if tick==161 else SOURCE162),
           "SOURCE_MAP_NPZ_"+slug+str(tick))
   require(e["original_source_discrete_logT_local_error"]<2e-4 and
           e["original_public_width_max"]<2e-3 and
           e["original_source_14_ledgers_include_zero"] is True and
           e["original_table_events"]==0,
           "SOURCE_PHYSICAL_GATES_"+slug+str(tick))
   if tick==161:
    require(header["metadata"]["job_key"]==e["job_key"] and
            header["metadata"]["job"]["accepted_parent_state_sha256"]==
                  owner["source_original_t160_3_lanes_SHA256"][slug],
            "T161_HISTORY_ORIGINAL_SHA_"+slug)
    require(sha(historical[slug])==owner["source_original_t160_3_lanes_SHA256"][slug],
            "T160_ARCHIVAL_SOURCE_MATCH_"+slug)
    require(header["source_not_official"] is True,"V2SC1_IS_NOT_V1")
   else:
    require(header["format"]=="REI_V2TX1_EXPERIMENTAL_ACCEPTED_NOT_REIADP1" and
            header["source_original_not_official"] is True,
            "V2TX2_NOT_V1_"+slug)
    job=header["job"]
    require(job["interval_ticks"]==[161,162] and job["accepted_index"]==5 and
            job["source_discrete_research_only"] is True and
            job["official_V1_tick161_accepted"] is False,
            "RESEARCH_JOB_"+slug)
    require(job["parent_v2sc1_state_sha256"]==
              accepted[4]["source_lanes"][lane]["state_sha256"],
            "JOB_PARENT_SHA_"+slug)
    require(job["new_source_npz_sha256"]==SOURCE162 and
            job["source_original_tar_sha256"]==SOURCE_TAR and
            job["versioned_full_seven_pin_runtime_SHA256"]==FULL_RUNTIME,
            "JOB_SOURCE_PROVENANCE_"+slug)
    require(sha(can(job))==header["job_key"]==e["job_key"],
            "JOB_CANONICAL_HASH_"+slug)
   jobs[tick].add(e["job_key"])
   states[tick][slug]=body
 require(bodies[161]=={BODY161} and len(bodies[162])==1,
         "THREE_LANE_SAME_ORIGINAL_SOURCE_BODY")
 require(len(jobs[161])==3 and len(jobs[162])==3,
         "DISTINCT_SOURCE_LANE_JOB_KEYS")
 for slug in ("recomb","shield"):
  require(states[161][slug]==states[161]["primary"] and
          states[162][slug]==states[162]["primary"],
          "THREE_LANE_BODIES_IDENTICAL_"+slug)
 require(all(ctrl["checkpoint_state_sha256"][lane]==
             accepted[5]["source_lanes"][lane]["state_sha256"]
             for lane,_ in LANES),"CONTROL_STATE_REFERENCES")
 # One physical realization: independently compute actual source H/He matter
 # on every cell from BOTH accepted transaction states using pure stdlib.
 P=decode(states[161]["primary"]);Q=decode(states[162]["primary"])
 Hsource=decode(readstate(historical["primary"],b"REIADP1\0")[1])
 source_nH=[];source_nHe=[]
 with gzip.open(original_nuclei_csv,"rt",newline="") as f:
  for ix,row in enumerate(csv.DictReader(f)):
   require(ix<N and int(row["cell"])==ix,"ORIGINAL_NUCLEUS_ROW_ORDER")
   source_nH.append(float(row["NH"]))
   source_nHe.append(float(row["NHe"]))
 require(len(source_nH)==N and len(source_nHe)==N,
         "ORIGINAL_NUCLEI_COMPLETE")
 pieces={"Ne":[[],[]],"B":[[],[]],"U":[[],[]]}
 parent_extensive={k:[[],[]] for k in ("Ne","B","U")}
 child_extensive={k:[[],[]] for k in ("Ne","B","U")}
 cell_count=0
 for i in range(N):
  base=i*5
  # Source inventory is the conserved proper H/He nucleus count,
  # NOT the LOWER endpoint of an original interval state. Treating
  # t160 lower-bound populations as exact nucleus counts changes
  # the U reservoir by ~1e-12 of the extensive parent.
  nH=source_nH[i]
  nHe=source_nHe[i]
  require(nH>0 and nHe>0,"ORIGINAL_NUCLEUS_SOURCE")
  source_Hlo=Hsource[0][base]+Hsource[0][base+1]
  source_Hhi=Hsource[1][base]+Hsource[1][base+1]
  source_Helo=sum(Hsource[0][base+2:base+5])
  source_Hehi=sum(Hsource[1][base+2:base+5])
  require(source_Hlo<=nH*(1+5e-12) and source_Hhi>=nH*(1-5e-12)
          and source_Helo<=nHe*(1+5e-12) and source_Hehi>=nHe*(1-5e-12),
          "ORIGINAL_T160_SOURCE_NUCLEUS_INTERVAL_CONTAINS_TRUE_NH")
  intervals=[]
  for state in (P,Q):
   lo,hi,zl,zh=state
   ph=lo[base:base+5];up=hi[base:base+5]
   require(all(math.isfinite(x) and x>0 for x in ph) and
           all(math.isfinite(x) and x>=y for x,y in zip(up,ph)),
           "POPULATION_CONE_"+str(i))
   require(math.isfinite(zl[i]) and math.isfinite(zh[i]) and zl[i]<=zh[i],
           "THERMAL_LOG_CONE_"+str(i))
   hlow=ph[0]+ph[1];hhigh=up[0]+up[1]
   helow=sum(ph[2:5]);hehigh=sum(up[2:5])
   require(hlow<=nH*(1+5e-12) and hhigh>=nH*(1-5e-12) and
           helow<=nHe*(1+5e-12) and hehigh>=nHe*(1-5e-12),
           "NUCLEON_CONSERVATION_CONE_"+str(i))
   nel=ph[1]+ph[3]+2*ph[4];neh=up[1]+up[3]+2*up[4]
   bl=EV*(CHIH*ph[1]+CHI1*(ph[3]+ph[4])+CHI2*ph[4])
   bh=EV*(CHIH*up[1]+CHI1*(up[3]+up[4])+CHI2*up[4])
   ul=1.5*KB*(nH+nHe+nel)*math.exp(zl[i])
   uh=1.5*KB*(nH+nHe+neh)*math.exp(zh[i])
   require(0<nel<=neh and 0<bl<=bh and 0<ul<=uh,"PHYSICAL_BOUNDS_"+str(i))
   intervals.append({"Ne":(nel,neh),"B":(bl,bh),"U":(ul,uh)})
  for k in ("Ne","B","U"):
   pieces[k][0].append(intervals[1][k][0]-intervals[0][k][1])
   pieces[k][1].append(intervals[1][k][1]-intervals[0][k][0])
   for ix in (0,1):
    parent_extensive[k][ix].append(intervals[0][k][ix])
    child_extensive[k][ix].append(intervals[1][k][ix])
  cell_count+=1
 require(cell_count==N,"SOURCE_46080_CELLS")
 parent_sums={k:[math.fsum(v[0]),math.fsum(v[1])] for k,v in parent_extensive.items()}
 child_sums={k:[math.fsum(v[0]),math.fsum(v[1])] for k,v in child_extensive.items()}
 # Preserve the source's order: globally sum each extensive parent and child
 # endpoint BEFORE subtraction. Cellwise difference-then-sum differs by
 # floating-point cancellation but not source physics.
 derived={k:[child_sums[k][0]-parent_sums[k][1],
             child_sums[k][1]-parent_sums[k][0]] for k in ("Ne","B","U")}
 per_cell_delta={k:[math.fsum(v[0]),math.fsum(v[1])] for k,v in pieces.items()}
 max_parent_normalized_gap=0.0
 for k in ("Ne","B","U"):
  scale=max(abs(x) for x in parent_sums[k]+child_sums[k])
  for ix in (0,1):
   mismatch=abs(per_cell_delta[k][ix]-derived[k][ix])
   require(mismatch<=64*2.220446049250313e-16*scale,
           "CANCELLATION_SCOPE_"+k)
   max_parent_normalized_gap=max(max_parent_normalized_gap,mismatch/scale)
 source=json.loads(Path(continuation).read_text())
 require(source["source_parent_tick161_sha256"]==SOURCE161 and
         source["source_candidate_state_tick162_sha256"]==SOURCE162,
         "REAL_SOURCE_NEXT_MAP_AUTHORITY")
 for k,bounds in derived.items():
  prior=source["source_conditional_delta_outer_intervals"][k]
  # Independently recomputed SUM(parent) and SUM(child) before subtraction,
  # with cancellation tolerance set against the *original extensive parent*
  # scale, not an arbitrarily loosened physical or source gate.
  parent_scale=max(abs(x) for x in parent_sums[k]+child_sums[k])
  for a,b in zip(bounds,prior):
   require(close(a,b,ref=parent_scale),"GLOBAL_PHYSICAL_INTERVAL_"+k)
 report={
  "schema":"REI_F05_V2TX1_INDEPENDENT_ORIGINAL_SOURCE_TRANSACTION_AUDIT_V1",
  "source_original_tar_sha256":SOURCE_TAR,
  "source_legacy_tick160_original_record_sha256":sha(old3),
  "source_original_nuclear_inventory_csv_sha256":sha_file(original_nuclei_csv),
  "nuclear_inventory_semantics":"TRUE_ORIGINAL_SOURCE_NH_NHE_NOT_INTERVAL_LOWER_ENDPOINT",
  "accepted_V2_research_ticks":[161,162],
  "accepted_V2_research_transactions":2,
  "original_V1_tick_still":160,
  "history_chain_last_SHA256":ctrl["history_last_record_sha256"],
  "checkpoint_three_t161_same_body_sha256":BODY161,
  "checkpoint_three_t162_same_body_sha256":next(iter(bodies[162])),
  "checkpoint_all_6_states_sha_and_job_keys":"PASS",
  "real_source_46080_HHe_cone_charge_B_U_checked":"PASS",
  "actual_original_source_cells_checked":N,
  "next_source_chemothermal_delta_outer_independent":derived,
  "independent_cellwise_difference_then_sum":per_cell_delta,
  "max_parent_normalized_summation_order_difference":max_parent_normalized_gap,
  "source_summation_method":"ORIGINAL_GLOBAL_PARENT_AND_CHILD_ENDPOINT_SUM_THEN_SUBTRACT",
  "original_14_ledger_by_each_accepted":"PASS",
  "source_discrete_V2_fixed_gates_unrelaxed":True,
  "original_V1_prod_unmodified":True,
  "versioned_V2_research_history_advance":True,
  "official_original_tick161":False,
  "canonical_REI_DAG":"28/88",
  "production":"HOLD",
  "review_type":"SAME_AUTHOR_SEPARATE_STDLIB_SOURCE_BINARY_READER"}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"AUDIT":"PASS","source_cells":N,
   "new_accepted_research_ticks":[161,162],
   "last_transaction":report["history_chain_last_SHA256"],
   "source_t162_body":report["checkpoint_three_t162_same_body_sha256"],
   "original_F05_official_tick":160,
   "source_discrete_ne_b_u":derived,
   "audit_sha256":sha_file(out)},sort_keys=True))

if __name__=="__main__":
 ap=argparse.ArgumentParser()
 for n in ("run","original_tar","continuation","original_nuclei_csv","out"):
  ap.add_argument("--"+n,required=True,type=Path)
 a=ap.parse_args()
 main(a.run,a.original_tar,a.continuation,a.original_nuclei_csv,a.out)
