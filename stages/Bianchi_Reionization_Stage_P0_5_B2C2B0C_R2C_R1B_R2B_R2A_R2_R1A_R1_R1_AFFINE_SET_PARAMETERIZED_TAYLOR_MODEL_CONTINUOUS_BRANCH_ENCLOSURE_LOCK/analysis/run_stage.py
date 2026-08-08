"""Execute the durable affine/Taylor branch-family rank and coherent-auditor stage."""
from __future__ import annotations
import hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path

HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;REPO=STAGE.parents[1];DATA=STAGE/'data';RECEIPTS=STAGE/'receipts'
LANES=('LOCAL_NEUTRAL_HAZARD_PRIMARY','RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR')

def _load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
rank=_load('affine_tm_run_rank',HERE/'branch_rank.py');decision=_load('affine_tm_run_decision',HERE/'decision.py')

def env():
 e=dict(os.environ);e['PYTHONUNBUFFERED']='1';e['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
 for n in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'):e[n]='1'
 return e

def main():
 DATA.mkdir(parents=True,exist_ok=True);RECEIPTS.mkdir(parents=True,exist_ok=True);started=time.perf_counter();lanes=[]
 for lane in LANES:
  out=DATA/f'{lane.lower()}_coherent_audit.json';log=RECEIPTS/f'{lane.lower()}_worker.log'
  with log.open('w') as h:
   p=subprocess.run([sys.executable,str(HERE/'coherent_auditor.py'),'--lane',lane,'--output',str(out)],cwd=REPO,env=env(),stdout=h,stderr=subprocess.STDOUT,text=True,timeout=600)
  if p.returncode:raise RuntimeError(f'worker failed {lane}: {log}')
  lanes.append(json.loads(out.read_text()))
 rank_result=rank.audit_source_safe_rank(REPO)
 max_width=max(max(x['coherent_empirical_widths'].values()) for x in lanes)
 max_res=max(max(x['withheld_max_absolute_residual'].values()) for x in lanes)
 outside=sum(x['adversarial_outside_count'] for x in lanes)
 verdict=decision.classify(source_safe_rank_lower_bound=rank_result.source_safe_rank_lower_bound,
   global_parameter_rank=rank_result.global_parameter_rank,adversarial_outside_count=outside,
   coherent_width_max=max_width,coherent_empirical_residual=max_res)
 result={
  'stage':'P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-AFFINE-SET-PARAMETERIZED-TAYLOR-MODEL-CONTINUOUS-BRANCH-ENCLOSURE-LOCK',
  'verdict':'DURABLE_FAIL_CLOSED_R2_R1A_R1_R1_SOURCE_SAFE_PARAMETER_RANK_NOT_REPRESENTED_COHERENT_GLOBAL_TAYLOR_AUDITOR_NARROW_SPARSE_LOCAL_GENERATOR_LOCK_AUTHORIZED',
  'completed':True,'continuous_parameter_certified':False,'production_history_authorized':False,
  'production_node_chemistry_authorized':False,'R2C_R2_authorized':False,'B2C2B_authorized':False,
  'source_safe_rank_audit':rank_result.to_dict(),'coherent_auditor':lanes,
  'coherent_max_empirical_width':max_width,'coherent_max_withheld_residual':max_res,
  'adversarial_outside_count':outside,'decision':verdict,
  'next_stage':'P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-SPARSE-LOCAL-GENERATOR-AFFINE-TAYLOR-MODEL-ENCLOSURE-LOCK',
  'elapsed_s':float(time.perf_counter()-started),
 }
 (STAGE/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 (DATA/'SOURCE_SAFE_RANK_AUDIT.json').write_text(json.dumps(rank_result.to_dict(),indent=2,sort_keys=True)+'\n')
 print(json.dumps({'verdict':result['verdict'],'rank':rank_result.source_safe_rank_lower_bound,'outside':outside,'elapsed_s':result['elapsed_s']},indent=2))
if __name__=='__main__':main()
