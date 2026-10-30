"""Retrospective 20-stage evidence snapshots, not 20 separate science runs."""
import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
R={
 'R1':('scope','Freeze PR281 source, PR279/280 independent sibling, original 33/88 central28/88 fast4/7; choose 59.0207 eV BASS native local absorption'),
 'R2':('primary source','Read original BASS Python/SHA and 193 Y,n_b,H; PR280 NIST M1 energy and Verner 1996 original source-photo coefficients'),
 'R3':('definitions','BASS gas-rest Y=n_i/n_b, n_b m^-3, H s^-1, sigma m², threshold eV, local frozen and no IVP'),
 'R4':('constructive candidate','For a single 59.0207 eV line, calculate 193 local opacities, isotope-resolved first absorber fractions, initial electron kinetic energies'),
 'R5':('derivation','kappa_i=n_bY_i sigma_i; p_i=kappa_i/sum kappa; mean primary+binding=E; frozen tau_H=c kappa/H, not cosmological tau'),
 'R6':('math validation','Wolfram exact symbolic {0,0,0} for probability, energy and attenuation ODE; real different-author R6 NOT_RUN'),
 'R7':('physical data','Computed 4053 source-native ionic opacity rows +193 epoch histories and three PNG; no IVP'),
 'R8':('scope decision','HeII fraction early0 late .994507659, source-only; REI17 common F/J, line yield, RT and heat remain unbound'),
 'R9':('theory report','THEORY_KO.md, REPORT_KO.md and CONTRACT.json contain derived terms, source rows and sample data; no full cross-owner promotion'),
 'R10':('recovery','Two immutable original full source ZIPs nested in new full ZIP; handoff and future source request; NO_AUTO_NEXT_NODE')}
C={
 'C1':('baseline','Single static source-only computation, all physical units explicit, no cosmological/chemical re-integration'),
 'C2':('code source map','BASS original photo_cross_sections(E) with projected 129 original coefficients; PR280 NIST M1 energy and 193 event-capacity clock'),
 'C3':('formula to implementation','Vectorized kappa_i=n_b*Y_i*sigma_i, probability and primary energy; active ion index strict'),
 'C4':('resources','193x21 bounded light computation, no new IVP, original historic budget not reset'),
 'C5':('working implementation','code/m1_absorption.py writes 193 epoch and 4053 species rows, cross-checks two immutable full ZIP SHA and lineage'),
 'C6':('tests','Python 16/16 PASS including mpmath 80-digit independent HHe photo cross checks, original identity and tamper negative'),
 'C7':('scientific validation','HeII fraction .994507659 at z2; primary 4.824873 eV vs z20 39.446022 eV, full energy/p conservation'),
 'C8':('reproducibility','Source-inclusive clean ZIP extraction and deterministic regeneration of two CSV and one results JSON PASS'),
 'C9':('independent review','Real distinct-author C9 NOT_RUN; inherited cargo fmt CI on PR281 FAIL, new Git branch CI not promoted'),
 'C10':('delivery','Source-inclusive immutable ZIP, Library/Drive, separate Git Draft and handoff, no merge or auto-start')}
for coll in [R,C]:
 for k,(tag,evidence) in coll.items():
  status='NOT_RUN_DISTINCT_AUTHOR' if k in ('R6','C9') else 'PASS_SCOPED_REPLAY_RECORD'
  # R6 Wolfram same-author symbolic check was done but independent R6 was not.
  x={'schema':'REI_F4_M1_STAGE_RECORD_V1','stage':k,'name':tag,'status':status,
    'kind':'RETROSPECTIVE_AFTER_ACTUAL_SCIENCE_RUN_NOT_DISTINCT_LIVE_STAGE_JOB',
    'objective_evidence':evidence,'working_DAG':'33/88','central_DAG':'28/88','physical_fast_DAG':'4/7',
    'canonical_physical_delta':0,'new_auxiliary_source_scoped':'1/1','no_new_IVPs':True,'original_budget_reset':False}
  (ROOT/'stages'/f'{k}.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
(ROOT/'STAGE_LEDGER.json').write_text(json.dumps({'schema':'REI_F4_M1_SCOPED_STAGE_LEDGER_V1',
  'note':'All 20 stage records are retrospective documentary checkpoints after a single scientific calculation; not 20 independently executed production research jobs.',
  'stages':{k:('NOT_RUN_DISTINCT_AUTHOR' if k in ('R6','C9') else 'PASS_SCOPED_REPLAY_RECORD') for k in list(R)+list(C)},
  'scoped_status':'18/20','Git_posting':'PENDING','Drive_posting':'PENDING','full_new_archive':'PENDING',
  'working_DAG':'33/88','central_DAG':'28/88','physical_fast':'4/7','canonical_delta':0,'scoped_auxiliary':'1/1'},ensure_ascii=False,indent=2)+'\n')
print('STAGE_RECORDS=20; SCOPED=18/20; R6,C9=NOT_RUN; original=33/88 central28/88 fast4/7')
