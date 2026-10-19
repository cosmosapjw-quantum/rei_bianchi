#!/usr/bin/env python3
"""Restore and execute bounded native SSPRK diagnostics offline, with receipts."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,time,sys,platform,datetime
ROOT=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input-root',required=True,type=Path);p.add_argument('--output-root',required=True,type=Path);p.add_argument('--cargo',default='cargo');p.add_argument('--jobs',type=int,choices=[1,2],default=2);p.add_argument('--prepare-only',action='store_true');p.add_argument('--mode',choices=['all','transport','fixed','birth'],default='all');a=p.parse_args();out=a.output_root.resolve();inputroot=a.input_root.resolve()
 if out.exists():raise SystemExit('Refusing existing run root: '+str(out))
 restore_cmd=[sys.executable,str(ROOT/'restore_ssprk2_native.py'),'--input-root',str(inputroot),'--output-root',str(out)];t0=time.monotonic();restore=subprocess.run(restore_cmd,capture_output=True,text=True);out.mkdir(parents=True,exist_ok=True);evidence=out/'evidence';evidence.mkdir(exist_ok=True)
 (evidence/'restore.command.json').write_text(json.dumps({'argv':restore_cmd},indent=2)+'\n');(evidence/'restore.stdout').write_text(restore.stdout);(evidence/'restore.stderr').write_text(restore.stderr);(evidence/'restore.exit').write_text(str(restore.returncode)+'\n');(evidence/'restore.timing.json').write_text(json.dumps({'elapsed_s':time.monotonic()-t0,'exit':restore.returncode},indent=2)+'\n')
 (out/'README_RUN.md').write_text('# Native SSPRK execution evidence\n\nCommands, stdout/stderr, exits, timings and source hashes are recorded. A successful exit is not scientific admission. Prepare-only performs no native compilation, tests or scientific run. Failed stages stop immediately; see RUN_RECEIPT.json and evidence.\n')
 if restore.returncode:
  (out/'RUN_RECEIPT.json').write_text(json.dumps({'schema':'rei.v15.sspp_runner.2','execution_status':'FAILED','failed_stage':'restore','exit':restore.returncode,'scientific_admission':'NOT_INFERRED_FROM_EXIT'},indent=2)+'\n');raise SystemExit(restore.returncode)
 native=out/'native_owner';crate=native/'rust/rei_microphysics';spec=json.loads((ROOT/'SOURCE_DELTA_SSPRK2.json').read_text());env=os.environ.copy();env.update(CARGO_BUILD_JOBS=str(a.jobs),OMP_NUM_THREADS=str(a.jobs),RAYON_NUM_THREADS=str(a.jobs),CARGO_HOME=str(out/'cargo_home'))
 cargo=a.cargo;cargo_path=Path(cargo)
 if cargo_path.is_absolute():
  env['PATH']=str(cargo_path.parent)+os.pathsep+env['PATH'];rustc=str(cargo_path.parent/'rustc')
 else:rustc='rustc'
 runs=[]
 def run(name,cmd,limit):
  (evidence/(name+'.command.json')).write_text(json.dumps({'argv':cmd,'cwd':str(crate),'timeout_s':limit,'jobs':a.jobs},indent=2)+'\n');start=time.monotonic()
  with(evidence/(name+'.stdout')).open('w')as so,(evidence/(name+'.stderr')).open('w')as se:
   try:r=subprocess.run(cmd,cwd=crate,env=env,stdout=so,stderr=se,timeout=limit);code=r.returncode
   except subprocess.TimeoutExpired:code=124
   except OSError as exc:se.write(str(exc)+'\n');code=127
  rec={'name':name,'exit':code,'elapsed_s':time.monotonic()-start};(evidence/(name+'.exit')).write_text(str(code)+'\n');(evidence/(name+'.timing.json')).write_text(json.dumps(rec,indent=2)+'\n');runs.append(rec);print(json.dumps(rec),flush=True)
  (out/'RUN_RECEIPT.json').write_text(json.dumps({'schema':'rei.v15.sspp_runner.2','mode':a.mode,'prepare_only':a.prepare_only,'execution_status':'FAILED'if code else'IN_PROGRESS','failed_stage':name if code else None,'exit':code,'source_sha256':spec['output_sha256'],'runs':runs,'scientific_admission':'NOT_INFERRED_FROM_EXIT'},indent=2)+'\n')
  if code:raise SystemExit(code)
  return(evidence/(name+'.stdout')).read_text()
 for name,cmd in [('rustc',[rustc,'-Vv']),('cargo',[cargo,'-Vv'])]:
  version=run(name,cmd,10)

 if not a.prepare_only:
  examples=['v15_ssprk_transport_diagnostic']if a.mode=='transport'else(['v15_ssprk_transport_diagnostic','v15_ssprk_coupled_diagnostic']if a.mode=='all'else['v15_ssprk_coupled_diagnostic'])
  cmd=[cargo,'build','--offline','--locked','--release','-j',str(a.jobs)]
  for example in examples:cmd+=['--example',example]
  run('build',cmd,180)
  run('targeted_tests',[cargo,'test','--offline','--locked','--release','-j',str(a.jobs),'--test','ssprk_transport','--test','ssprk_coupled','--','--nocapture'],120)
  runstart=time.monotonic()
  if a.mode in ['transport','all']:run('transport',[str(crate/'target/release/examples/v15_ssprk_transport_diagnostic'),str(evidence/'transport.csv')],60)
  if a.mode in ['fixed','birth','all']:
   for mode in (['fixed','birth']if a.mode=='all'else[a.mode]):
    remaining=min(180,int(300-(time.monotonic()-runstart)))
    if remaining<=0:raise SystemExit('300second total scientific-runtime budget exhausted')
    run('coupled_'+mode,[str(crate/'target/release/examples/v15_ssprk_coupled_diagnostic'),str(evidence/('coupled_'+mode+'.csv')),mode],remaining)
 outputs={}
 for p in sorted(evidence.glob('*.csv*')):outputs[p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 receipt={'schema':'rei.v15.sspp_runner.2','mode':a.mode,'prepare_only':a.prepare_only,'source_sha256':spec['output_sha256'],'runs':runs,'raw_outputs':outputs,'actual_native_tests_executed':0 if a.prepare_only else 14,'coupled_cases_executed':0 if a.prepare_only or a.mode=='transport'else(16 if a.mode=='all'else(6 if a.mode=='fixed'else 10)),'replays_do_not_add_unique_cases':True,'theory_status':'see independent research/review documents','execution_status':'PREPARED_ONLY'if a.prepare_only else'RUN_COMPLETE_REVIEW_REQUIRED','scientific_admission':'NOT_INFERRED_FROM_EXIT','session_ncp_status_at_delivery':'No new NCP run in delivery session; see EXTERNAL_EXECUTION_STATUS.json; this field does not classify this future runner execution','actual_execution_host':platform.node(),'actual_platform':platform.platform(),'actual_execution_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actual_host_classification':'not inferred from hostname','compiler_compatibility':'actual -Vv recorded; actual build/tests are compatibility evidence; no exact compiler-version gate','scope':'native CPU<=2 offline, no fullEoR/CaseB/signedBianchi promotion'}
 (out/'RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'README_RUN.md').write_text('# Native SSPRK run receipt\n\nThis directory records '+receipt['execution_status']+'. Numeric admission requires independent raw-data and source review. Prepare-only performs source reconstruction and compiler metadata checks; it does not compile, test, or run scientific cases. Every started native stage has command/stdout/stderr/exit/timing evidence, including failures. No network, installer, source normalization, automatic CFL subcycling, default/adaptive/checkpoint modification, or unconditional/stiff/full-EoR claim is part of this runner.\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
