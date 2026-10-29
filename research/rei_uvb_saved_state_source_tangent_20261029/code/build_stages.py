from pathlib import Path
import json, hashlib
R=Path(__file__).resolve().parents[1]
steps=[
 ('R1','research objective and exact protected scope','CONTRACT.json','frozen ON_refined instantaneous source, no IVP'),
 ('R2','primary literature and original Git source reuse','SOURCE_RECONCILIATION.json','P19 2019, REI model topology, 7 saved numerical rows'),
 ('R3','definitions and claim scope','THEORY_KO.md','y per Href, z_mean, common rate scaling, isotope equality'),
 ('R4','construct competing derivative levels','THEORY_KO.md','instantaneous J_R vs unbound full D_a y and tau'),
 ('R5','derive source Jacobian and lognorm','THEORY_KO.md','J_y, J_R, B, rank1/rank2, mu1=0, energy ledger'),
 ('R6','distinct-author independent mathematical review','THEORY_KO.md','NOT_RUN: native subagent unavailable; Wolfram is algorithmic CAS'),
 ('R7','symbolic and numerical discrimination','results/RESULT.json','Wolfram four zero residuals, saved 7 source rows, 256 corner q0 check'),
 ('R8','scientific claim decision','REPORT_KO.md','frozen source-only, not trajectory/tau or observational posterior'),
 ('R9','math-to-code contract','CONTRACT.json','17x6 source, 17x17 photo-only, 17x2 parameter Jacobians'),
 ('R10','theory closeout and handoff','HANDOFF_NEXT_THREAD_KO.md','remaining actual full chemistry/clock/tau dependencies'),
 ('C1','code baseline and input authority','SOURCE_RECONCILIATION.json','PR261 source SHA and REI original model/CSV blobs'),
 ('C2','map source functions and state topology','code/source17.py','7 source transitions, rate/heating index, old A/Q'),
 ('C3','stable numeric implementation design','code/source17.py','matrix/loop derivative and positivity guards'),
 ('C4','bounded execution and resource contract','RESOURCE_AND_GATES.json','no IVP, no render, no old campaign, bounded new test'),
 ('C5','implement new source tangent','code/source17.py','F, J_y, J_R, B, electron/energy ports and envelopes'),
 ('C6','unit and metamorphic regression','results/TEST_STDERR.txt','15/15 actual new unittest PASS'),
 ('C7','scientific source crosscheck','results/CPP_COMPARISON.txt','C++20 direct-event 7/7 PASS, source numeric identity'),
 ('C8','numerical and reproducibility','results/TEST_TIME.txt','actual runtime, rank and support, no production speedup claim'),
 ('C9','distinct-author independent code review','code/source17_reference.cpp','NOT_RUN: C++ is independent algorithm, not independent author'),
 ('C10','scoped delivery and next node','HANDOFF_NEXT_THREAD_KO.md','add-only Draft PR, backup receipts and no physical admission')]
complete=0;entries=[]
for stage,objective,evidence,conclusion in steps:
    passed=stage not in ('R6','C9')
    if passed:complete+=1
    rec={'schema':'REI_UVB_SAVED17_STAGE_V1','stage':stage,'status':'COMPLETE_SCOPED' if passed else 'HOLD_DIFFERENT_AUTHOR_NOT_RUN',
         'stage_complete_count':complete,'stage_total':20,'original_working_DAG':'33/88','central_last_DAG':'28/88',
         'original_DAG_delta':0,'objective':objective,'evidence_file':evidence,'outcome':conclusion,
         'archive_semantics':'CLOSEOUT_RECONSTRUCTED_STAGE_CAPSULE','publication':'PENDING_GITHUB_ACK',
         'cloud_backup':'PENDING'}
    p=R/'stages'/f'{stage}.json';p.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
    entries.append({'stage':stage,'completed':passed,'completed_so_far':complete,'file':f'stages/{stage}.json','sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
ledger={'schema':'REI_UVB_SAVED17_STAGE_LEDGER_V1','stages':entries,'completed':complete,'total':20,
        'working_DAG':'33/88','central_last_DAG':'28/88','new_original_nodes':0,
        'original_budget':'CLOSED_NO_TRANSFER','independent_author_R6_C9':'NOT_RUN',
        'stage_files_are_closeout_reconstructed':True,'cloud_provider_ack':'PENDING'}
(R/'STAGE_LEDGER.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
print('stages',complete,'/20','files',len(entries))
