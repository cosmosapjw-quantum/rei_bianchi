"""Small retrospective stage evidence map, not 20 fictitious live science runs."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
R=[
('R1','source question and frozen scientific contract','CONTRACT.json'),
('R2','primary Li II lifetimes/NIST levels and parent archive read','THEORY_KO.md'),
('R3','state charge/energy threshold semantic alignment','THEORY_KO.md'),
('R4','M1 and 2E1 state-resolved alternative construction','THEORY_KO.md'),
('R5','sharp photon threshold count theorem and kinematic energy ledger','THEORY_KO.md'),
('R6','Wolfram exact residual=0; distinct-author review not executed','THEORY_KO.md'),
('R7','actual 193-epoch saved source diagnostics','results/RESULT.json'),
('R8','scoped physical admissibility and unbound heat/source gates','THEORY_KO.md'),
('R9','derived equations mapped to radiative_atlas.py','code/radiative_atlas.py'),
('R10','handoff and science notes checkpoint','HANDOFF_NEXT_THREAD_KO.md'),]
C=[
('C1','source/baseline/units and no-IVP contract','CONTRACT.json'),
('C2','original PR279 data and PR277 nested source SHA read','code/radiative_atlas.py'),
('C3','sharp count bounds and saved x/H Simpson postprocessing','code/radiative_atlas.py'),
('C4','193x2x22 and 3-threshold output design','code/radiative_atlas.py'),
('C5','concrete executable source-data generator','code/radiative_atlas.py'),
('C6','28 scoped target tests and negative source SHA control','tests/test_radiative.py'),
('C7','source event/energy conserved and NIST threshold count checks','tests/test_radiative.py'),
('C8','193 sample/8492 source capacity and reproducibility checks','results/RESULT.json'),
('C9','distinct-author reviewer not executed','tests/test_radiative.py'),
('C10','source-inclusive package and clean restore handoff','HANDOFF_NEXT_THREAD_KO.md'),]
records=[]
for stage,desc,evidence in R+C:
    state='NOT_RUN' if stage=='C9' else 'PARTIAL_DISTINCT_AUTHOR_NOT_RUN' if stage=='R6' else 'SCOPED_PASS'
    v={'schema':'REI_F4_RADIATIVE_STAGE_V1','stage':stage,'status':state,
       'science_result':desc,'evidence_relpath':evidence,
       'backed_up_locally':True,
       'publication_type':'RETROSPECTIVE_AFTER_SCIENCE_EXECUTION',
       'original_SOURCE_SHA':'6e50586131ab6f8f76b72ee8c7125dfd3225211d528609c862e01a305a0ab6d3',
       'working_dag':'33/88','central_dag':'28/88','f4_fast_dag':'4/7','canonical_physical_delta':0,
       'no_new_IVPs':True,'no_merge':True,'no_force_push':True,'production':'HOLD'}
    out=ROOT/'stages'/f'{stage}.json'
    out.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
    records.append(v)
(ROOT/'STAGE_LEDGER.json').write_text(json.dumps({'schema':'REI_RADIATIVE_STAGE_LEDGER_V1','completed_scoped':18,'total':20,'R6':'PARTIAL_DISTINCT_AUTHOR_NOT_RUN','C9':'NOT_RUN_DISTINCT_AUTHOR','publication_timing':'retrospective after scientific calculation, not 20 live contemporaneous runs','stages':records},indent=2,ensure_ascii=False)+'\n')
print('STAGES',len(records))
