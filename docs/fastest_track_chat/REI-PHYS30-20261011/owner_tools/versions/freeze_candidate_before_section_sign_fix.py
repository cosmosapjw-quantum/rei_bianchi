#!/usr/bin/env python3
"""Freeze complete PHYS30 review candidate; metadata and cached evidence only."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,stat
ROOT=Path(__file__).resolve().parents[1]
def rd(name):return json.loads((ROOT/name).read_bytes())
def ident(name):
 p=ROOT/name;b=p.read_bytes()
 assert p.resolve(strict=True)==p.absolute() and stat.S_ISREG(p.lstat().st_mode)
 return {'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'mode':format(stat.S_IMODE(p.stat().st_mode),'04o')}
def write(name,obj):
 with (ROOT/name).open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
freeze=rd('contributions/numerics/PREEXECUTION_FROZEN.json')
for row in freeze['files']:
 actual=ident(row['path']);assert all(actual[k]==row[k] for k in ('path','bytes','sha256','mode'))
raw=rd('contributions/numerics/PROFILE_SECOND_ORDER_FIRST.json')
rp=rd('portability/REPLAY_RECEIPT.json');s=rd('report/PHYS30_RESULTS_SUMMARY.json')
assert s['first_summary']==raw['summary']
assert all(s['profile_coefficients'][p][b]==raw['profile_results'][p]['branches'][b]['affine'] for p in raw['profile_results'] for b in raw['profile_results'][p]['branches'])
assert s['gap']==raw['gap_results'] and s['branch_profile_slopes']==raw['branch_profile_slopes']
assert s['total_execution']['new_main']==2 and rp['actual_exit_code']==0
assert s['replay']['byte_equal'] and s['replay']['parsed_json_equal']
assert ident('figures/PHYS30_PROFILE_SECOND_ORDER.png')['sha256']=='41d20d0f1ee279410e2d2913332b9e47fb9b10a66d58b5e3709cb23e7b7083b3'
fig=rd('figures/FIGURE_PROVENANCE.json')
for key in ('input','source','output'):
 rec=fig[key];actual=ident(rec['path']);assert all(actual[k]==rec[k] for k in ('path','bytes','sha256'))
proof=(ROOT/'contributions/theory/DERIVATION_KO.md').read_text()
proof=proof.replace('](../../','](../').replace('](THEORY_CLAIMS.json)','](../contributions/theory/THEORY_CLAIMS.json)').replace('](PROVENANCE.json)','](../contributions/theory/PROVENANCE.json)')
proof='\n'.join('#'+line if line.startswith('#') else line for line in proof.splitlines())+'\n'
report=(ROOT/'report/PHYS30_REPORT_KO.md').read_text()
assert report.endswith(proof)
assert not any(token in report for token in ('@NUMBER_TABLE@','@TERM_TABLE@','@FIRST_TIME@','@REPLAY_TIME@','§'))
links=[]
for target in re.findall(r'\]\(([^)]+)\)',report):
 if target.startswith(('https://','http://','#')):continue
 path=(ROOT/'report'/target).resolve()
 exists=path.is_file()
 pending=target in ('../independent/DECISION_REVIEW.json','../state/CLOSEOUT.json')
 assert exists or pending,target
 links.append({'target':target,'exists':exists,'expected_later_gate_record':pending and not exists})
full_read_names=['next/PHYS31_NEXT_HANDOFF_KO.md','portability/REPLAY_RECEIPT.json','portability/REPLAY_NOTE_KO.md','portability/POST_EXECUTION_PROVENANCE.json','figures/plot_cached.py','figures/FIGURE_PROVENANCE.json','figures/FIGURE_VISUAL_REVIEW.json','figures/DISPLAY_METADATA_FAILURE.json','evidence/VALIDATION_MATRIX_KO.md']
review={'task':'REI-PHYS30-20261011','recorded_utc':datetime.now(timezone.utc).isoformat(),'owner':'/root','classification':'OWNER_INTEGRATION_SELF_REVIEW_NONBLIND','report':ident('report/PHYS30_REPORT_KO.md'),'report_actual_read':'Complete new front matter and numeric tables actually displayed/read. Complete appended derivation previously actually read in666 lines; byte equality after only headings/relative-link changes verified here. No claim of a new independent physics proof from metadata.','full_semantic_read_files':[ident(p) for p in full_read_names],'summary':ident('report/PHYS30_RESULTS_SUMMARY.json'),'summary_read_scope':'All builder-defined metadata and values; complete coefficient dictionaries, slopes and gap fields compared exactly to observed raw, no formula reevaluation.','candidate_science_inputs_unchanged':14,'actual_figure_view':'Root directly viewed final PNG; labels, shared scales, nonzero-level limits and four net d values legible, no clipping or overlap needing correction.','figure':ident('figures/PHYS30_PROFILE_SECOND_ORDER.png'),'figure_render_by_root':0,'appendix_matches_read_theory_with_formatting_only':True,'links':links,'science_main_by_this_action':0,'physical_kernel_derivative_root_by_this_action':0,'metadata_failures_preserved':['evidence/REPORT_PATCH_FIRST_FAILURE.json','figures/DISPLAY_METADATA_FAILURE.json'],'distinct_final_decision':'PENDING /root/phys30_decision'}
write('evidence/OWNER_INTEGRATION_REVIEW.json',review)
paths=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name!='MANIFEST.json' and p!=ROOT/'evidence/CANDIDATE_FROZEN.json']
rows=[ident(p.relative_to(ROOT).as_posix()) for p in paths]
assert all(row['mode'] in ('0644','0755') for row in rows)
candidate={'task':'REI-PHYS30-20261011','status':'FROZEN_FOR_DISTINCT_NONBLIND_FINAL_REVIEW','created_utc':datetime.now(timezone.utc).isoformat(),'file_count':len(rows),'files':rows,'primary_report':'report/PHYS30_REPORT_KO.md','summary':'report/PHYS30_RESULTS_SUMMARY.json','claim_ledger':'evidence/CLAIM_LEDGER.json','first_and_replay_actual_main':2,'new_physical_kernel_derivative_root':0,'reviewer':'/root/phys30_decision','reviewer_role':'Distinct from candidate generation and scientific validation design; NONBLIND, same model/history/host.','append_only_after_freeze':['independent final review records','owner gate intake','state CLOSEOUT/RESEARCH_STATE','MANIFEST'],'final_archive_and_publication_receipts':'Detached future records, not preclaimed here.'}
write('evidence/CANDIDATE_FROZEN.json',candidate)
print(json.dumps({'status':candidate['status'],'candidate':ident('evidence/CANDIDATE_FROZEN.json'),'file_count':len(rows),'report':ident('report/PHYS30_REPORT_KO.md'),'summary':ident('report/PHYS30_RESULTS_SUMMARY.json'),'science_main':0},ensure_ascii=False))

