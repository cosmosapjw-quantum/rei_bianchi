#!/usr/bin/env python3
"""Create retrospective evidence-backed stage notes, NOT 20 independent jobs."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
map_r={
'R1':('source-scope','Choose original PR283 2E1 pair J, freeze source 33/88 central28/88 fast4/7 and forbid IVP/merge/force'),
'R2':('source-intake','Read actual PR283 original ZIP 11,153,561 B SHA91c4..., original Drake 1969 OCR-partial source, original BASS21 193 epoch and Verner source'),
'R3':('definitions','Fix gas rest Y=n_i/n_b, n_b[m-3], H[s-1], c, E_low=yEs, E_high=(1-y)Es and conditional paired absorption'),
'R4':('candidate','Construct five outcomes ESC,H_I,He_I,He_II,Li_I and 5x5 correlated two-photon first-absorber law'),
'R5':('derivation','Show joint J_ab=integral p(y)pi_a(Elo)pi_b(Ehi), P0+P1+P2=1, E[N]=P1+2P2, covariance P2-pL*pH'),
'R6':('independent-math-review','Same-run Wolfram exact symbolic cancellations {0,0,0,True}, but genuine different-author R6 NOT_RUN'),
'R7':('science-data','Compute 193 BASS source epochs x25 pair joint outcomes=4825 physical conditional source rows'),
'R8':('decision','Covariance sign changes +/- in actual frozen source, retain conditional OCR/branching and reject physical tau/heat/CMB'),
'R9':('write-theory','THEORY_KO.md, REPORT_KO.md and CONTRACT.json contain exact formula and actual units/state/limitations'),
'R10':('handoff','Source-inclusive full ZIP, Git and provider backups, final report and next unit; no auto_next'),
}
map_c={
'C1':('baseline','Existing PR283 conditional single-photon counts and 193 saved source; add genuinely new 5x5 pair joint law'),
'C2':('callgraph','Verified PR283/PR282 nested exact SHAs, original 193 source snapshot and native BASS21 photo_cross_sections'),
'C3':('algorithm','Evaluate 2 complementary photon energies jointly at each source y; split at all BASS thresholds; integrate 5x5 categories'),
'C4':('resource','Only bounded 193x216x25 sample operations plus 4/8/16 quadrature; no IVP, prior budgets not reset'),
'C5':('implementation','code/pair_joint.py writes 193 epoch and 4825 per-pair channel rows, provenance-guarded real original sources'),
'C6':('targeted-tests','New independent tests check SHA guard, 193/4825, probabilities, first moment, covariance, zero HeII-low, no IVP'),
'C7':('science-validation','Original PR283 first absorption mean exactly reused; sign-changing pair covariance source-specific'),
'C8':('reproducibility','Compared 4/8/16 Gauss orders; froze CSV, JSON and figures and clean-restore source-inclusive ZIP'),
'C9':('independent-implementation-review','Different-author C9 NOT_RUN; same-run tests/Wolfram are not external author review; inherited full cargo fmt failure untouched'),
'C10':('delivery','Independent Draft PR only, exact source backup on Drive/Library, 20 historical stage records, no merge'),
}
records={}
for group in (map_r,map_c):
    for stage,(name,evidence) in group.items():
        status='NOT_RUN_DISTINCT_AUTHOR' if stage in ('R6','C9') else 'PASS_SCOPED_RETROSPECTIVE'
        rec={'schema':'REI_F4_LII_2E1_PAIR_STAGE_V1','stage':stage,'name':name,
             'execution_record_type':'RETROSPECTIVE_AFTER_SINGLE_ACTUAL_SCIENCE_RUN_NOT_20_INDEPENDENT_SCIENCE_RUNS',
             'status':status,'objective_evidence':evidence,'working_DAG':'33/88','central_DAG':'28/88','physical_fast':'4/7',
             'canonical_delta':0,'new_auxiliary_scoped':'1/1','no_new_IVPs':True,'original_budget_reset':False}
        (R/'stages'/f'{stage}.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
        records[stage]=status
(R/'STAGE_LEDGER.json').write_text(json.dumps({'schema':'REI_F4_LII_2E1_PAIR_STAGES_V1','count':20,'scoped':18,'not_run':['R6','C9'],
    'note':'These are 20 retrospective evidence checkpoints after one actual source-owned science computation, not separate physical jobs',
    'stages':records,'original_working':'33/88','original_central':'28/88','physical_fast':'4/7',
    'canonical_delta':0,'new_auxiliary':'1/1_CONDITIONAL','new_IVPs':0},ensure_ascii=False,indent=2)+'\n')
print('RECORDS20_SCOPE18_R6C9_NOT_RUN')
