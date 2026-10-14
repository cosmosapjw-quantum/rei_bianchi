#!/usr/bin/env python3
"""Record actual owner consumption and metadata checks; no scientific execution."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_bytes())
def rec(p):
    b=(ROOT/p).read_bytes();return {'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
freeze=read('contributions/numerics/PREEXECUTION_FROZEN.json')
for row in freeze['files']:assert rec(row['path'])==row,row['path']
raw=read('contributions/numerics/SECOND_ORDER_FIRST.json'); replay=read('portability/REPLAY_RECEIPT.json')
assert len(raw['checks'])==238 and all(row['pass'] for row in raw['checks'])
assert (ROOT/'contributions/numerics/SECOND_ORDER_FIRST.json').read_bytes()==(ROOT/'portability/REPLAY_RESULT.json').read_bytes()
assert replay['status']=='REPLAY_PASS' and replay['new_program_replay_invocations']==1
assert replay['actual_counts']==raw['summary']['actual_counts']
for key in ['preexecution_restore','postexecution_restore']:
    assert replay[key]['all_pass'] and len(replay[key]['files'])==26
    for row in replay[key]['files']:
        assert all(row[k] for k in ['size_equal','sha256_equal','archive_byte_equal','regular_file','mode_100644'])
assert read('figures/DISPLAY_RECEIPT.json')['status']=='VISUALLY_INSPECTED_PASS'
syntax=[]
for p in sorted((ROOT/'owner_tools').glob('*.py')):
    ast.parse(p.read_text(),filename=str(p));syntax.append(p.relative_to(ROOT).as_posix())
future={'independent/DECISION_REVIEW.json','independent/DECISION_REVIEW_KO.md','state/CLOSEOUT.json'}
link_records=[]
for rel in ['report/PHYS29_REPORT_KO.md','README_KO.md','next/PHYS30_NEXT_HANDOFF_KO.md']:
    p=ROOT/rel
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if target.startswith(('https://','http://','#')):continue
        q=(p.parent/target).resolve();resolved=q.relative_to(ROOT).as_posix()
        exists=q.exists();assert exists or resolved in future,(rel,target)
        link_records.append({'from':rel,'target':target,'exists_at_candidate_check':exists,'authorized_future_gate_file':resolved in future})
obj={
 'task':'REI-PHYS29-20261011','recorded_utc':datetime.now(timezone.utc).isoformat(),'owner':'/root',
 'role':'NONBLIND owner synthesis and candidate/validation coordination; not distinct final reviewer',
 'status':'OWNER_CONSUMPTION_COMPLETE_READY_FOR_DISTINCT_REVIEW',
 'actual_read_scope':[
  {'path':'contributions/theory/DERIVATION_KO.md','scope':'Full637lines consumed before first GO; theory claims and provenance also read'},
  {'path':'contributions/numerics/second_order_width.py','scope':'Full initial code in bounded ranges and all actual finalv3 diffs before GO; owner preexecution receipt records25 identities'},
  {'path':'contributions/numerics/PROTOCOL.json','scope':'Full initial protocol plus all finalv3 changes; no post-first change'},
  {'path':'contributions/numerics/SECOND_ORDER_FIRST.json','scope':'Full actual identity bytes and JSON parse; selected complete kernels,primarychain/decomposition,bivariate scalar fields,delta.05comparison,scales and summary read; all238stored pass flags verified programmatically, not238newexecutions'},
  {'path':'contributions/numerics/EXECUTION.json','scope':'Full with stdout and empty stderr'},
  {'path':'contributions/numerics/NUMERICS_NOTE_KO.md','scope':'Full actual note and POSTEXECUTION_PROVENANCE read'},
  {'path':'portability/REPLAY_RECEIPT.json','scope':'Execution,environment,command,times,counts,identity,status and every pre/post payload row consumed/checked; aggregate tool-output truncation followed by selected missing execution read'},
  {'path':'portability/REPLAY_NOTE_KO.md','scope':'Full actual note and USAGE read'},
  {'path':'portability/PROVENANCE.json','scope':'Full actual provenance read'},
  {'path':'report/PHYS29_REPORT_KO.md','scope':'Authored from retained evidence; full actual readback in ranges, aggregation-truncated tail reread; later notation-only kappa clarification observed in patch'},
  {'path':'next/PHYS30_NEXT_HANDOFF_KO.md','scope':'Full actual readback; proposed profile scope checked with theory contributor, no PHYS30 result promoted'},
  {'path':'figures/PHYS29_SECOND_ORDER_DECOMPOSITION.png','scope':'Three actual image views; two layout corrections preserved; final visualPASS, cached values only'}
 ],
 'critical_reasoning_checked':[
  'd is half the right second derivative and dimensionless',
  'Physical support-preserving one-sided C2 root argument; exact-root existence premises conditional',
  'Fixed actual W requires V_second=−2/3 exactly once',
  'Complete geometry plus implicit mixed and variance-curvature contributions; dV=1/3 cancels in gap',
  'Stored numerical points retain response A, use corrected same-level numerator identity, no root correction/enclosure',
  'k_second requires log derivative4; separate kernel paths and independent bivariate versus chain postprocessing',
  'Single width residuals and lower overshoot stated with signs; no convergence/validity-window bound',
  'First main1 plus replay1 only, all forbidden scientific operations0; identical replay not independent physics',
  'Next fixed symmetric profile question is proposed only; identical center interval is explicit',
  'Review authority, archive, Git and delivery staged without preclaim or hashcycle'
 ],
 'all_preexecution_frozen_payloads_unchanged':len(freeze['files']),
 'first_replay_bytes_equal':True,'stored_check_flags_true':238,
 'metadata_script_ast_only':syntax,'internal_links':link_records,
 'core_identities':[rec(p) for p in ['contributions/numerics/PREEXECUTION_FROZEN.json','contributions/numerics/SECOND_ORDER_FIRST.json',
  'contributions/numerics/EXECUTION.json','portability/REPLAY_RECEIPT.json','report/PHYS29_REPORT_KO.md',
  'report/PHYS29_RESULTS_SUMMARY.json','next/PHYS30_NEXT_HANDOFF_KO.md','figures/PHYS29_SECOND_ORDER_DECOMPOSITION.png']],
 'new_scientific_main':0,'new_physical_kernel_or_derivatives':0,'new_physical_roots':0,
 'final_decision':'NOT_THIS_ROLE; future independent/DECISION_REVIEW.json',
 'protected':read('PHYSICS_CONTRACT.json')['protected_state']}
p=ROOT/'evidence/OWNER_CANDIDATE_REVIEW.json';assert not p.exists();p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'owner_review':rec(p.relative_to(ROOT).as_posix()),'metadata_links':len(link_records),'syntax_only':len(syntax),'scientific_executions':0},ensure_ascii=False))
