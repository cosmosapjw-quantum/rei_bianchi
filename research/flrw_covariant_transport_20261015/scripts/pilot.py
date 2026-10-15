#!/usr/bin/env python3
"""Finite prescribed pilot executor. Each run is explicit, fresh, and non-resuming."""
import argparse,csv,datetime,hashlib,json,os,re,resource,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
TASK=ROOT/'research/flrw_covariant_transport_20261015'
RAW=TASK/'raw'
BINARY=ROOT/'rust/rei_microphysics/target/release/examples/axbi_reionization'
CASES=['q128','q256','q512','q512_time','q512_angle']
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,data): Path(path).write_text(json.dumps(data,indent=2)+'\n')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def expected_source():
 driver=ROOT/'rust/rei_microphysics/src/axbi_driver.rs'
 section=driver.read_text().split('pub fn compiled_identity() -> String {',1)[1].split('fn ledger_values',1)[0]
 paths=[(driver.parent/s).resolve() for s in re.findall(r'include_str!\(\s*"([^"]+)"',section)]
 return '\nAXBI_SOURCE_BOUNDARY\n'.join(p.read_text() for p in paths),{str(p.relative_to(ROOT)):sha(p) for p in paths}
def proc_usage(pid):
 try:
  text=Path(f'/proc/{pid}/status').read_text(); out={}
  for key in ['VmRSS','VmHWM','Threads']:
   m=re.search(r'^'+key+r':\s+(\d+)',text,re.M)
   if m:out[key]=int(m.group(1))*(1024 if key!='Threads' else 1)
  return out
 except (FileNotFoundError,ProcessLookupError):return {}
def execute(cmd,log,limit,environment=None,limit_memory=False):
 t=time.monotonic(); peak=0;threads=0;timed_out=False
 def bound():
  if limit_memory:resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
 with open(log,'w') as f:
  child=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,env=environment,preexec_fn=bound if limit_memory else None)
  while child.poll() is None:
   usage=proc_usage(child.pid);peak=max(peak,usage.get('VmHWM',usage.get('VmRSS',0)));threads=max(threads,usage.get('Threads',0))
   if time.monotonic()-t>=limit:
    timed_out=True;child.terminate()
    try:child.wait(timeout=2)
    except subprocess.TimeoutExpired:child.kill();child.wait()
    break
   time.sleep(.1)
 return {'command':cmd,'exit_code':child.returncode,'wall_s':time.monotonic()-t,'timed_out':timed_out,'hard_wall_limit_s':limit,'peak_rss_sampled_bytes':peak,'maximum_threads_observed':threads}
def build(attempt):
 receipt=RAW/f'build_attempt{attempt}.json';log=RAW/f'build_attempt{attempt}.log'
 if receipt.exists() or log.exists():raise RuntimeError('fresh build attempt path required')
 if attempt not in [1,2]:raise RuntimeError('build limit2')
 tc=Path('/workspace/scratch/56fd3625e428/toolchain');env=os.environ.copy();env.update(RUSTUP_HOME=str(tc/'rustup'),CARGO_HOME=str(tc/'cargo'),PATH=str(tc/'cargo/bin')+':'+env['PATH'],CARGO_BUILD_JOBS='4')
 data=execute(['cargo','build','--release','--locked','--manifest-path','rust/rei_microphysics/Cargo.toml','--example','axbi_reionization'],log,180,env)
 data['observed_utc']=now();data['source_inputs_sha256']=expected_source()[1]
 if BINARY.exists():data['binary_sha256']=sha(BINARY)
 save(receipt,data);print(json.dumps(data));return data['exit_code']==0 and not data['timed_out']
def run(case,attempt):
 out=RAW/f'{case}_attempt{attempt}';receipt=RAW/f'{case}_attempt{attempt}_receipt.json';log=RAW/f'{case}_attempt{attempt}.log'
 if out.exists() or receipt.exists() or log.exists():raise RuntimeError('fresh case attempt path required; no overwrite or implicit resume')
 if case!='q128':
  candidates=list(RAW.glob('q128_attempt*_receipt.json'))
  if not any(json.loads(f.read_text()).get('status')=='COMPLETE_REPRESENTED_INTERVAL' for f in candidates):raise RuntimeError('q128 completion prerequisite missing')
 cfg=TASK/'configs'/f'pilot_z20_19p8_{case}.cfg'
 before,inputs=expected_source();identity=hashlib.sha256(before.encode()).hexdigest()
 data={'case':case,'attempt':attempt,'start_utc':now(),'config':str(cfg.relative_to(ROOT)),'config_sha256':sha(cfg),'binary_sha256':sha(BINARY),'source_inputs_sha256':inputs,'expected_compiled_identity_sha256':identity,'scientific_admission':'NOT_ISSUED','allocation':{'max_wall_s':600,'max_accepted':20000,'max_attempts':65000,'max_rhs':5000000,'output_mib':256,'address_space_bytes':8*1024**3,'max_concurrent_cases':2}}
 save(receipt,{**data,'status':'RUNNING'})
 cmd=[str(BINARY),'--config',str(cfg),'--output',str(out),'--case',f'FLRW_COVARIANT_{case.upper()}_A{attempt}']
 data.update(execute(cmd,log,600,limit_memory=True));data['end_utc']=now();data['output_bytes']=sum(f.stat().st_size for f in out.rglob('*') if f.is_file()) if out.exists() else 0
 data['status']='FAILED_OR_INCOMPLETE';data['log_tail']=log.read_text()[-3000:]
 if (out/'RETURN.txt').exists():
  fields=dict(line.split('=',1) for line in (out/'RETURN.txt').read_text().splitlines() if '=' in line);data['native_return']=fields
  if data['exit_code']==0 and fields.get('status')=='COMPLETE_REPRESENTED_INTERVAL':data['status']='COMPLETE_REPRESENTED_INTERVAL'
  for k in ['accepted','attempts','rejections','rhs_evaluations']:data[k]=int(fields[k])
  data['final_zbar']=1/float(fields['a'])-1
 if (out/'history.csv').exists():
  with (out/'history.csv').open() as f:rows=list(csv.DictReader(f))
  if rows:
   final=rows[-1];data['history_rows']=len(rows);data['endpoint_metrics']={k:float(final[k]) for k in ['a','zbar','time_s','x_HII','x_HeII','x_HeIII','temperature_K','photon_n_per_H','photon_u_eV_per_H','Gamma_HI_per_s','Gamma_HeI_per_s','Gamma_HeII_per_s']}
 if (out/'ledgers.csv').exists():
  with (out/'ledgers.csv').open() as f:rows=list(csv.DictReader(f))
  last={row['ledger_name']:row for row in rows};data['final_ledgers']={k:float(v['residual']) for k,v in last.items()};data['ledger_failure_rows']=sum(row['status']=='FAIL' for row in rows)
  data['max_abs_number_residual']=max((abs(float(row['residual'])) for row in rows if row['ledger_name']=='photon_count'),default=0)
  data['max_abs_energy_residual_ev_per_h']=max((abs(float(row['residual'])) for row in rows if row['ledger_name']=='augmented_energy_eV_per_H'),default=0)
  data['endpoint_metrics'].update({f'photo_events_{j}_per_H':data['final_ledgers'].get(f'photo_events_{j}_per_H',0) for j in range(3)})
 if (out/'checkpoint.txt').exists():
  lines=(out/'checkpoint.txt').read_text().splitlines();data['checkpoint_version']=lines[0];data['checkpoint_final_a']=float(lines[1].split()[0]);data['checkpoint_counts']=list(map(int,lines[2].split()));data['checkpoint_arrays_lengths']=[len(lines[i].split()) for i in [4,5,6,7]] if lines[0]=='AXBI_CHECKPOINT_V3' else []
 if (out/'source_identity.txt').exists():
  actual=(out/'source_identity.txt').read_text();data['compiled_identity_sha256']=sha(out/'source_identity.txt');data['compiled_source_readback_equal']=actual==before
 data['config_readback_equal']=(out/'config.cfg').exists() and (out/'config.cfg').read_bytes()==cfg.read_bytes()
 data['source_unchanged_during_run']=expected_source()[0]==before
 if not data.get('compiled_source_readback_equal') or not data.get('source_unchanged_during_run') or not data['config_readback_equal']:data['status']='SOURCE_OR_CONFIG_BINDING_FAILURE'
 save(receipt,data);print(json.dumps(data));return data['status']=='COMPLETE_REPRESENTED_INTERVAL'
def compare():
 selected={}
 for case in CASES:
  rs=sorted(RAW.glob(f'{case}_attempt*_receipt.json'))
  passed=[json.loads(f.read_text()) for f in rs if json.loads(f.read_text()).get('status')=='COMPLETE_REPRESENTED_INTERVAL']
  if not passed:raise RuntimeError(f'{case}: no completed source-bound pilot')
  selected[case]=passed[-1]
 metrics=['x_HII','x_HeII','x_HeIII','temperature_K','photon_n_per_H','photon_u_eV_per_H']+[f'photo_events_{j}_per_H' for j in range(3)]
 def delta(a,b):
  out={}
  for k in metrics:
   x=selected[a]['endpoint_metrics'][k];y=selected[b]['endpoint_metrics'][k];floor=1 if k=='temperature_K' else 1e-5 if k.startswith('x_') else 1e-8
   out[k]=abs(x-y)/max(abs(y),floor)
  return out
 pairs={f'{a}__{b}':delta(a,b) for a,b in [('q128','q256'),('q256','q512'),('q512','q512_time'),('q512','q512_angle')]}
 first=pairs['q128__q256'];fine=pairs['q256__q512'];monotone={k:fine[k]<=1.1*first[k] or max(fine[k],first[k])<=1e-8 for k in metrics}
 data={'schema':'rei.covariant.pilot_screen.v1','frozen_contract':'NATIVE_CONTRACT.md','relative_limit':1e-3,'pairwise_relative_differences':pairs,'grid_refinement_contract_per_metric':monotone,'all_pairwise_below_limit':all(v<=1e-3 for row in pairs.values() for v in row.values()),'all_grid_refinement_checks':all(monotone.values()),'scientific_admission':'PENDING_INDEPENDENT_REVIEW','receipts':{k:str(RAW.relative_to(ROOT)/f"{k}_attempt{v['attempt']}_receipt.json") for k,v in selected.items()}}
 data['screen_status']='PASS_EMPIRICAL_SCREEN_ONLY' if data['all_pairwise_below_limit'] and data['all_grid_refinement_checks'] else 'HOLD_EMPIRICAL_SCREEN'
 save(TASK/'PILOT_COMPARISON.json',data);print(json.dumps(data));return data['screen_status'].startswith('PASS')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['build','run','compare']);parser.add_argument('--case',choices=CASES);parser.add_argument('--attempt',type=int,default=1);args=parser.parse_args()
 try: ok=build(args.attempt) if args.action=='build' else run(args.case,args.attempt) if args.action=='run' else compare()
 except Exception as e:print(f'{type(e).__name__}: {e}',file=sys.stderr);sys.exit(2)
 sys.exit(0 if ok else 1)
