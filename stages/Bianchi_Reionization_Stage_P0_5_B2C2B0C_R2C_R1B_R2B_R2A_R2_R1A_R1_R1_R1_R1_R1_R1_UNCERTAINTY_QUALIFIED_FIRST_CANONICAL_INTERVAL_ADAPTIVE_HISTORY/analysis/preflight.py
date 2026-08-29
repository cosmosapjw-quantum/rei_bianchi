#!/usr/bin/env python3
"""Read-only prerequisite/environment checks; performs no science calculation."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,platform,subprocess,sys,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;REPO=STAGE.parents[1]
PRE=REPO/'stages'/('Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_'
 'R1_R1_R1_R1_R1_CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK')
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 if spec is None or spec.loader is None:raise ImportError(path)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
runtime_contract=load('adaptive_history_preflight_runtime_contract',HERE/'runtime_contract.py')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def command(*args):return subprocess.run(args,cwd=REPO,text=True,capture_output=True,check=False)
def run():
 lock=json.loads((STAGE/'INPUT_LOCK.json').read_text());checks=[]
 def check(name,passed,observed,expected=None):checks.append({'name':name,'passed':bool(passed),'observed':observed,'expected':expected})
 head=command('git','rev-parse','HEAD');check('git_head_readable',head.returncode==0,head.stdout.strip())
 tracked=command('git','status','--porcelain=v1','--untracked-files=no');check('tracked_worktree_clean',tracked.returncode==0 and not tracked.stdout.strip(),tracked.stdout.strip(),'empty')
 ancestor=command('git','merge-base','--is-ancestor',lock['predecessor']['integration_commit'],'HEAD');check('integration_commit_is_ancestor',ancestor.returncode==0,ancestor.returncode,0)
 check('predecessor_sha256sums',sha(PRE/'SHA256SUMS')==lock['predecessor']['sha256sums_sha256'],sha(PRE/'SHA256SUMS'),lock['predecessor']['sha256sums_sha256'])
 verify=subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=PRE,text=True,capture_output=True,check=False);check('predecessor_payloads_verify',verify.returncode==0,verify.returncode,0)
 stage_verify=subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=STAGE,text=True,capture_output=True,check=False);check('current_stage_payloads_verify',stage_verify.returncode==0,stage_verify.returncode,0)
 bundle=REPO/'artifacts/compact'/('Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_'
 'CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK_compact_bundle.zip')
 check('predecessor_bundle_sha256',sha(bundle)==lock['predecessor']['compact_bundle_sha256'],sha(bundle),lock['predecessor']['compact_bundle_sha256'])
 check('predecessor_bundle_size',bundle.stat().st_size==lock['predecessor']['compact_bundle_size_bytes'],bundle.stat().st_size,lock['predecessor']['compact_bundle_size_bytes'])
 with zipfile.ZipFile(bundle) as archive:bad_member=archive.testzip()
 check('predecessor_bundle_crc',bad_member is None,bad_member,'no bad member')
 try:
  import numpy,scipy,pandas
  dependencies={'numpy':numpy.__version__,'scipy':scipy.__version__,'pandas':pandas.__version__}
 except Exception as error:
  dependencies={'error':f'{type(error).__name__}: {error}'}
 check('runtime_dependencies',dependencies=={'numpy':'2.3.5','scipy':'1.17.0','pandas':'2.2.3'},dependencies,{'numpy':'2.3.5','scipy':'1.17.0','pandas':'2.2.3'})
 check('jax_absent_import_guard_required',importlib.util.find_spec('jax') is None,importlib.util.find_spec('jax') is not None,False)
 mem_kib=None
 try:
  for line in Path('/proc/meminfo').read_text().splitlines():
   if line.startswith('MemAvailable:'):mem_kib=int(line.split()[1]);break
 except OSError:pass
 check('memory_for_three_workers',mem_kib is None or mem_kib>=3*700*1024,mem_kib,'>= 2150400 KiB or unavailable')
 try:contract=runtime_contract.build(REPO,STAGE);contract_error=None
 except Exception as error:contract={};contract_error=f'{type(error).__name__}: {error}'
 check('runtime_contract_closed',contract_error is None,contract_error or contract.get('sha256'),'valid clean runtime contract')
 return {'all_passed':all(x['passed'] for x in checks),'calculation_started':False,'checks':checks,'classification':'PREFLIGHT_ONLY_NO_SCIENCE_RESULT','environment':{'machine':platform.machine(),'platform':platform.platform(),'python':sys.version.split()[0]},'runtime_contract_sha256':contract.get('sha256'),'stage_id':lock['stage_id']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--output');a=p.parse_args();result=run();payload=json.dumps(result,indent=2,sort_keys=True)+'\n'
 if a.output:
  target=Path(a.output);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(payload)
 print(payload,end='');return 0 if result['all_passed'] else 2
if __name__=='__main__':raise SystemExit(main())
