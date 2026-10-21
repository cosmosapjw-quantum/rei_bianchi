"""Bounded changed-risk verification; never execute a full native time case."""
from pathlib import Path
import argparse,json,os,subprocess,sys,time,hashlib
HERE=Path(__file__).resolve().parent;TASK=HERE.parent

def execute(cmd,out,label,cap,env=None,*,build=False):
 out.mkdir(parents=True,exist_ok=True);receipt=out/('BUILD_COMMANDS.json' if build else 'COMMANDS.json')
 records=json.loads(receipt.read_text()) if receipt.exists() else []
 if build and not records:
  for legacy in ['BUILD_RECEIPT.json','BENCH_BUILD_RECEIPT.json']:
   if (out/legacy).exists():records.append(json.loads((out/legacy).read_text()))
 budget=120 if build else 240;spent=sum(r['wall_seconds'] for r in records);limit=min(cap,budget-spent)
 if limit<=0:raise RuntimeError('BUILD_CAP_EXHAUSTED' if build else 'LIGHT_CAP_EXHAUSTED')
 start=time.monotonic();timed=False
 try:r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=limit)
 except subprocess.TimeoutExpired as e:
  timed=True
  decode=lambda v:v.decode(errors='replace') if isinstance(v,bytes) else v or ''
  r=subprocess.CompletedProcess(cmd,124,decode(e.stdout),decode(e.stderr))
 wall=time.monotonic()-start;prefix=out/f'{len(records)+1:02d}_{label}'
 stdout=prefix.with_suffix('.stdout.log');stderr=prefix.with_suffix('.stderr.log');stdout.write_text(r.stdout);stderr.write_text(r.stderr)
 row=dict(command=cmd,exit_code=r.returncode,timed_out=timed,cap_seconds=limit,wall_seconds=wall,label=label,aggregate_seconds=spent+wall,budget_seconds=budget,stdout=str(stdout),stderr=str(stderr))
 records.append(row);receipt.write_text(json.dumps(records,indent=2)+'\n')
 if r.returncode:raise RuntimeError(str(row)+'\n'+r.stderr)
 return r

def run(cmd,out,label,cap,env=None):return execute(cmd,out,label,cap,env)

def controls_source():
 lines=['use rei_microphysics::axbi_covariant_transport::*;','fn main(){','let serial=rei_synthetic_parallel_control(1).unwrap();for w in [2,4]{assert_eq!(serial,rei_synthetic_parallel_control(w).unwrap());}', 'let eta=f64::from_bits(1);assert!(!rei_repair_candidate_test(1.,2.,1.,1.5));assert!(!rei_repair_candidate_test(1.,2.,eta,10.*eta));assert!(!rei_repair_candidate_test(f64::NAN,2.,eta,eta));']
 paths=[TASK/'evidence/native_count_energy_20261019/N2/FULL_DIAGNOSTIC_BITS.json',TASK/'evidence/native_count_energy_20261019/N3/FULL_DIAGNOSTIC_BITS.json',TASK/'evidence/native_pair_search_20261019/FULL_DIAGNOSTIC_BITS.json']
 for label,path in zip(['N2','N3','N4'],paths):
  rows=json.loads(path.read_text())['diagnostic_bits'];row=rows[-1]
  args=','.join('f64::from_bits(0x'+row[k]['u64_bits']+')' for k in ['lo','hi','n','u','r'])
  lines.extend(['std::env::remove_var("REI_SUBNORMAL_REPAIR");',f'assert!(rei_cell_replay({args}).is_err(),"{label} original gate should fail");','std::env::set_var("REI_SUBNORMAL_REPAIR","subnormal-barycenter");',f'let got=rei_cell_replay({args}).unwrap();assert_eq!(got.len(),1);println!("{label} repaired {{:?}}",got);'])
 lines.extend(['std::env::remove_var("REI_SUBNORMAL_REPAIR");let a=rei_cell_replay(15.,25.,1.,20.,1.).unwrap();','std::env::set_var("REI_SUBNORMAL_REPAIR","subnormal-barycenter");assert_eq!(a,rei_cell_replay(15.,25.,1.,20.,1.).unwrap());','println!("NORMAL_UNCHANGED;PARALLEL_1_2_4_IDENTICAL;CAPTURED_N2_N3_N4_PASS");}'])
 return '\n'.join(lines)

def tiny(binary,out,receipts):
 outputs=[]
 for label,threads,full,observer in [('serial_off',1,False,False),('parallel_off',2,False,False),('parallel_observer',2,False,True),('full_observer',2,True,True)]:
  dest=out/label
  if dest.exists():raise ValueError('TINY_DEST_EXISTS')
  env=dict(os.environ,REI_SUBNORMAL_REPAIR='subnormal-barycenter',REI_TRANSPORT_THREADS=str(threads));env.pop('REI_FULL_TRACE',None);env.pop('REI_BE_TRACE',None)
  if full:env['REI_FULL_TRACE']='1'
  if observer:env['REI_BE_TRACE']=str(dest/'be_trace.jsonl')
  dest.mkdir(parents=True)
  run([str(binary),'native_refine','0',str(dest),'2','8','8','8','2,8','1'],receipts,label,30,env)
  outputs.append({n:(dest/n).read_bytes() for n in ['endpoint.json','observations.json','native_return.json']})
 assert all(v==outputs[0] for v in outputs),'TINY_PHYSICAL_OUTPUT_MISMATCH'
 from analyze import analyze_trace
 result=analyze_trace(out/'parallel_observer/be_trace.jsonl',True);assert result['status']=='COMPLETE' and result['records']
 (out/'TINY_RESULT.json').write_text(json.dumps(dict(status='PASS',physical_output_bytes_equal=True,trace_rows=len(result['records']),PRODUCTION_SCIENTIFIC_ADMISSION='NOT_ISSUED'),indent=2)+'\n')

def main():
 p=argparse.ArgumentParser();p.add_argument('--prepared',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--rust-prefix',type=Path,required=True);p.add_argument('--build',action='store_true');p.add_argument('--tiny-only',action='store_true')
 a=p.parse_args();env=dict(os.environ,PATH=str(a.rust_prefix/'bin')+os.pathsep+os.environ['PATH'],CARGO_BUILD_JOBS='2');crate=a.prepared/'rust/rei_microphysics'
 if a.build:
  controls=crate/'examples/v10_controls.rs';controls.write_text(controls_source())
  cmd=[str(a.rust_prefix/'bin/cargo'),'build','--offline','--release','--manifest-path',str(crate/'Cargo.toml'),'--example','positive_native','--example','v10_controls','-j','2']
  execute(cmd,a.out,'changed_core_build',120,env,build=True)
 if not a.tiny_only:
  run([str(crate/'target/release/examples/v10_controls')],a.out,'captured_core_controls',30,env)
  run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_changed.py','-v'],a.out,'python_changed_risks',30,env)
 number=1
 while (a.out/f'tiny_attempt{number:03d}').exists():number+=1
 tiny(crate/'target/release/examples/positive_native',a.out/f'tiny_attempt{number:03d}',a.out)
 print('V10_FOCUSED_CONTROLS_PASS')
if __name__=='__main__':main()
