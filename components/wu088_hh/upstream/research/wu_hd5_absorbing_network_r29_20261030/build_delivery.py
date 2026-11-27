"""Prepare source-backed bounded R29 stage evidence and archived phase copies.
Stage JSONs represent scientific work evidenced by source/output, not 20 separate experiments.
"""
from __future__ import annotations
import csv,hashlib,json,os,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path,obj):
 p=ROOT/path;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');return p

def run_checked(name,cmd):
 r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=90)
 (ROOT/'delivery'/f'{name}.log').write_text('CMD: '+' '.join(cmd)+'\nEXIT: '+str(r.returncode)+'\n'+r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(f'{name}: exit {r.returncode}, {r.stderr[-500:]}')
 return {'command':cmd,'exit_code':r.returncode,'log':'delivery/'+name+'.log'}

def archive(path,paths):
 path.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name in sorted(set(paths)):
   fp=ROOT/name
   if fp.is_file():z.write(fp,name)
 with zipfile.ZipFile(path) as z:
  if z.testzip():raise RuntimeError('ZIP CRC '+str(path))
 return {'filename':path.name,'size_bytes':path.stat().st_size,'sha256':sha(path),'member_count':len(zipfile.ZipFile(path).namelist()),'crc':'PASS'}

def main():
 checks=[
  run_checked('TEST_NORMAL',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_r29.py','-q']),
  run_checked('TEST_OPTIMIZED',[sys.executable,'-O','-m','unittest','discover','-s','tests','-p','test_r29.py','-q']),
  run_checked('COMPILEALL',[sys.executable,'-m','compileall','-q','src','tests']),
  run_checked('INDEPENDENT_MPMATH',[sys.executable,'tests/independent_mpmath.py']),
 ]
 summary=json.loads((ROOT/'results/SUMMARY.json').read_text())
 mp=json.loads((ROOT/'results/INDEPENDENT_MPMATH.json').read_text())
 assert summary['num_cases']==210 and mp['rows']==210
 assert len(list(csv.DictReader(open(ROOT/'results/PRODUCT_BRANCHING_2100.csv'))))==2100
 assert len(list(csv.DictReader(open(ROOT/'sources/GL2022_1560_INELASTIC_SOURCE_TOKENS.csv'))))==1560
 checks_file=write_json('delivery/VALIDATION.json',{'schema':'wu.r29.actual_execution_v1','tests_normal':'20/20_PASS','tests_optimized':'20/20_PASS','mpmath_independent_same_author':mp,'source_input_cells_used':{'reactive':350,'inelastic_down':70},'outputs':{'conditional_case_rows':210,'H2_product_branching_rows':2100,'upward_counterfactual_rows':14},'actual_commands':checks,'independent_different_author_R6_C9':'NOT_RUN','original_PDF_identity':'TEST_NORMAL_via_R28_zip_payload_hash','initial_failed_run':'Regex originally assumed two-digit exponents, source also contains valid one-digit exponent; repaired parser and tests WITHOUT changing source bytes'})
 names=['R'+str(i) for i in range(1,11)]+['C'+str(i) for i in range(1,11)]
 phase={**{f'R{i}':'P01_THEORY' for i in range(1,11)},**{f'C{i}':'P02_CODE' if i<=5 else 'P03_VALIDATION' if i<=9 else 'P04_HANDOFF' for i in range(1,11)}}
 evidence={
  'R1':['DAG_DELTA.json','THEORY_KO.md'],'R2':['SOURCE_IDENTITY.json','sources/GL2022_700_SOURCE.json','sources/GL2022_1560_INELASTIC_SOURCE_TOKENS.csv'],
  'R3':['THEORY_KO.md','DAG_DELTA.json'],'R4':['THEORY_KO.md'],'R5':['THEORY_KO.md'],
  'R6':['THEORY_KO.md'],'R7':['results/SUMMARY.json','results/ATLAS_210_STATE_CASES.json'],
  'R8':['DAG_DELTA.json','REPORT_KO.md'],'R9':['THEORY_KO.md','src/network.py'],'R10':['README_REPLAY.md','REPORT_KO.md'],
  'C1':['README_REPLAY.md'],'C2':['SOURCE_IDENTITY.json','src/network.py'],'C3':['src/network.py','src/counterfactual.py'],
  'C4':['README_REPLAY.md','results/SUMMARY.json'],'C5':['src/network.py','results/ATLAS_210_STATE_CASES.csv','results/PRODUCT_BRANCHING_2100.csv'],
  'C6':['delivery/TEST_NORMAL.log','delivery/TEST_OPTIMIZED.log','tests/test_r29.py'],
  'C7':['results/INDEPENDENT_MPMATH.json','tests/independent_mpmath.py'],
  'C8':['delivery/VALIDATION.json','SOURCE_IDENTITY.json'],'C9':['tests/test_r29.py','delivery/VALIDATION.json'],
  'C10':['README_REPLAY.md','REPORT_KO.md','DAG_DELTA.json']}
 state_descriptions={
  'R1':'fix fixed-T, fixed-nHplus five-HD-level restricted chemistry sink source question',
  'R2':'recover actual original GL2022 R26/R28 source rates and REC161/162/163 source records',
  'R3':'exclude suspect R26 J3 at 2505, R28 J1 1505, printed 15K source zero and J5 duplicate; source energy provenance',
  'R4':'candidate full reversible thermal rotational collision graph plus chemical sink/radiative transitions',
  'R5':'derive detailed balance, absorbing resolvent, photon counts and restricted H2 product branching',
  'R6':'genuinely distinct-author review not dispatched; native subagent not exposed',
  'R7':'Wolfram 3state symbolic check and 210 genuine source-driven conditional case calculation',
  'R8':'interpret positivity/domain and 1984 observed laboratory line crosswalk; keep physical Q/owner unadmitted',
  'R9':'math-to-code column generator and output contract with original SI rate/tokens',
  'R10':'theory handoff, domain and original source preservation',
  'C1':'define 210 case and 2100 product branching source-dependent target',
  'C2':'trace source token to kinetic matrix and source-dependent result',
  'C3':'build 5state irreversible chemical sink with thermal upscattering and A terms',
  'C4':'implement exact seven temperature native grid, three density ratios two policy slices',
  'C5':'generate actual original-rate-derived 210 cases, 2100 H2 product and 14 counterfactual rows',
  'C6':'20/20 unittest normal and -O, compileall actual pass',
  'C7':'full 210/210 same-author independent mpmath75 source-token re-evaluation and SciPy DOP853 check',
  'C8':'R28 entire ZIP SHA, internal PDF SHA and 4 current source text hash hardcoded; deterministic re-run',
  'C9':'different-author code review not dispatched; same-author checks are not C9 PASS',
  'C10':'source-complete archive, phase/source checkpoints, draft PR handoff'}
 for st in names:
  unrun=st in ('R6','C9')
  write_json('stages/'+st+'.json',{
   'schema':'wu.r29.research_stage_evidence.v1','stage':st,'phase':phase[st],
   'status':'NOT_RUN_DISTINCT_AUTHOR' if unrun else 'COMPLETE_SCOPED_EVIDENCE',
   'work_evidence':state_descriptions[st],
   'evidence_paths':evidence[st],
   'one_independent_execution_per_stage':False,'retrospective_stage_evidence_snapshot':True,
   'original_Git_parent_pr':167,'parent_head':'cd85b157fdfdf6be0bbe372ff5c282c20a4ca07e',
   'canonical_DAG':{'complete':34,'total':49},
   'physical_Q':None,'owner_ACK':None,'production':'NOT_ISSUED','full_A':None,'HH_R10':'OFF','L4':False})
 source_refs=['SOURCE_IDENTITY.json','DAG_DELTA.json']
 stage_receipts=[]
 for st in names:
  subject=[x for x in evidence[st] if Path(ROOT/x).is_file()]
  archive_path=ROOT/'archives'/(f'WU_R29_STAGE_{st}_20261030.zip')
  rec=archive(archive_path,['stages/'+st+'.json']+source_refs+subject[:2]);rec.update({'stage':st,'stage_status':'NOT_RUN' if st in ('R6','C9') else 'SCOPED','DAG':'34/49'})
  stage_receipts.append(rec)
 write_json('delivery/STAGE_ARCHIVE_LEDGER.json',{'schema':'wu.r29.stage_zip_backup_ledger.v1','retrospective_evidence_not_20_experiments':True,'stages':stage_receipts,'each_zip_created_with_real_files':True,'library_receipt':'PENDING_EXPLICIT_UPLOAD','remote_Git_stage_record':'PENDING_PUBLICATION','canonical_DAG':'34/49'})
 phases={
  'P01_THEORY':['THEORY_KO.md','REPORT_KO.md','DAG_DELTA.json','SOURCE_IDENTITY.json','README_REPLAY.md']+[f'stages/R{i}.json' for i in range(1,11)],
  'P02_PHYSICAL_CODE':['src/__init__.py','src/network.py','src/counterfactual.py']+[str(x.relative_to(ROOT)) for x in (ROOT/'sources').glob('*')]+[str(x.relative_to(ROOT)) for x in (ROOT/'results').glob('*')]+[f'stages/C{i}.json' for i in range(1,6)],
  'P03_VALIDATION':['delivery/VALIDATION.json','tests/test_r29.py','tests/independent_mpmath.py']+[str(x.relative_to(ROOT)) for x in (ROOT/'delivery').glob('*.log')]+[f'stages/C{i}.json' for i in range(6,10)],
  'P04_HANDOFF':['README_REPLAY.md','REPORT_KO.md','DAG_DELTA.json','SOURCE_IDENTITY.json','delivery/STAGE_ARCHIVE_LEDGER.json','stages/C10.json'],
 }
 phase_receipts=[]
 for p,paths in phases.items():
  rec=archive(ROOT/'archives'/f'WU_R29_{p}_SOURCE_20261030.zip',paths)
  rec['phase']=p;rec['DAG']='34/49';phase_receipts.append(rec)
 write_json('delivery/PHASE_ARCHIVE_LEDGER.json',{'schema':'wu.r29.phase_backup_ledger.v1','phase_archives':phase_receipts,'DAG':'34/49'})
 print('ARTIFACTS 20 STAGES',len(stage_receipts),'4 PHASES',len(phase_receipts),'CHECKS',checks)
 return stage_receipts,phase_receipts
if __name__=='__main__':main()