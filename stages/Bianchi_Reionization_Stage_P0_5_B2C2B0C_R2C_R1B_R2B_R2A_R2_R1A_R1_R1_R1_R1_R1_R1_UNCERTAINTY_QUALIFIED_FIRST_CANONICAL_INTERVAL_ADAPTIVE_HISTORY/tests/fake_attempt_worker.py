#!/usr/bin/env python3
import argparse,array,hashlib,json,os,struct,subprocess,sys,time
from pathlib import Path

LANES=('LOCAL_NEUTRAL_HAZARD_PRIMARY','RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR')
WIDTH_KEYS=('x_HII','x_HeII','x_HeIII','log_T')
LEDGER_KEYS=('H_nuclei','He_nuclei','stage_photon_identity','stage_total_energy','stage_group_0_photon','stage_group_1_photon','stage_group_2_photon','stage_group_3_photon','final_photon_identity','final_total_energy','final_group_0_photon','final_group_1_photon','final_group_2_photon','final_group_3_photon')
NODE_COUNT=46080
def canonical(value):return json.dumps(value,allow_nan=False,ensure_ascii=True,separators=(',',':'),sort_keys=True).encode('ascii')
def write_state(path,job):
 metadata={'accepted_index':job['accepted_index'],'endpoint_tick':job['interval']['right_tick'],'input_lock_sha256':job['input_lock_sha256'],'job_key':job['job_key'],'lane':job['lane'],'parent_state_sha256':job['parent']['sha256'],'predecessor_kernel_sha256':job['predecessor_kernel_sha256'],'runtime_contract_sha256':job['runtime_contract_sha256'],'stage_id':job['stage_id']}
 header={'array_order':['population_lower','population_upper','log_temperature_lower','log_temperature_upper'],'byte_order':'little','dtype':'float64','log_temperature_shape':[NODE_COUNT],'metadata':metadata,'population_shape':[NODE_COUNT,5],'schema':1};encoded=canonical(header)
 values=array.array('d',[1.0])*(2*NODE_COUNT*5)+array.array('d',[9.0])*(2*NODE_COUNT)
 if values.itemsize!=8:raise RuntimeError('unexpected double size')
 if os.sys.byteorder!='little':values.byteswap()
 payload=b'REIADP1\0'+struct.pack('<Q',len(encoded))+encoded+values.tobytes();Path(path).write_bytes(payload);return payload
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--job');parser.add_argument('--result');parser.add_argument('--state');args=parser.parse_args();job=json.loads(Path(args.job).read_text());mode=os.getenv('FAKE_WORKER_MODE','PASS');lane=job['lane'];interval=job['interval']
 if mode=='CRASH' and lane=='RECOMBINATION_WEIGHTED_AUDITOR':return 7
 if mode=='TIMEOUT' and lane=='RECOMBINATION_WEIGHTED_AUDITOR':
  print('partial timeout output',flush=True);time.sleep(2);return 0
 if mode=='DESCENDANT_TIMEOUT' and lane=='RECOMBINATION_WEIGHTED_AUDITOR':
  release=Path(str(args.result)+'.release');pid_path=Path(str(args.result)+'.descendant-pid')
  program=('import os,sys,time; from pathlib import Path; '
   'release=Path(sys.argv[1]); pid_path=Path(sys.argv[2]); pid_path.write_text(str(os.getpid())); '
   'deadline=time.monotonic()+3; exec("while not release.exists() and time.monotonic()<deadline:\\n time.sleep(0.01)")')
  subprocess.Popen([sys.executable,'-c',program,str(release),str(pid_path)])
  print('ordinary descendant started',flush=True);time.sleep(2);return 0
 event=mode=='EVENT' and lane=='SCRIPT_SELF_SHIELDING_AUDITOR' and interval['left_tick']==0
 reject=mode=='REJECT_BASE_ZERO' and lane=='RECOMBINATION_WEIGHTED_AUDITOR' and interval['left_tick']==0 and interval['right_tick']==64
 accepted=not(event or reject);classification='TABLE_EVENT_REQUIRES_RESTART' if event else 'PUBLIC_WIDTH_GATE_FAILURE' if reject else 'PASS';candidate=None
 widths={key:1e-6 for key in WIDTH_KEYS};local={key:1e-7 for key in WIDTH_KEYS};ledgers={key:[-1e-12,1e-12] for key in LEDGER_KEYS};diagnostics={'map_enclosed':True,'maximum_validated_local_error':1e-7,'validated_local_error_bounds':local}
 if reject:widths['log_T']=.002
 if event:widths={};ledgers={};diagnostics={'failed_phase':'full_step'}
 if accepted:
  state=b'FAKE' if mode=='MALFORMED_STATE' and lane=='RECOMBINATION_WEIGHTED_AUDITOR' else write_state(args.state,job)
  if state==b'FAKE':Path(args.state).write_bytes(state)
  candidate={'format':'REIADP1-deterministic-float64','node_count':NODE_COUNT,'path':str(Path(args.state).resolve()),'sha256':hashlib.sha256(state).hexdigest(),'size_bytes':len(state)}
 events=[{'any_event':True,'knot_indices':[],'minimum_distance':0.0,'node_indices':[]}] if event else [];duration=1.0
 row={'accepted_index':job['accepted_index'],'candidate_state':candidate,'classification':classification,'diagnostics':diagnostics,'duration_seconds_hex':duration.hex(),'input_lock_sha256':job['input_lock_sha256'],'interval':interval,'job_key':job['job_key'],'lane':lane,'parent_state_sha256':job['parent']['sha256'],'predecessor_kernel_sha256':job['predecessor_kernel_sha256'],'public_widths':widths,'runtime_contract_sha256':job['runtime_contract_sha256'],'scientific_accept':accepted,'set_ledgers':ledgers,'stage_id':job['stage_id'],'table_event':{'any_event':event,'events':events,'minimum_distance':0.0 if event else .25,'node_count':0},'telemetry':{'fake':True},'time':{'t0_hex':(duration*interval['left_tick']/131072).hex(),'t1_hex':(duration*interval['right_tick']/131072).hex()},'transport_status':'OK','worker_envelope_schema':1}
 if mode=='MALFORMED_ENVELOPE' and lane=='SCRIPT_SELF_SHIELDING_AUDITOR':row['classification']='PUBLIC_WIDTH_GATE_FAILURE'
 Path(args.result).write_bytes(canonical(row)+b'\n');return 0
if __name__=='__main__':raise SystemExit(main())
