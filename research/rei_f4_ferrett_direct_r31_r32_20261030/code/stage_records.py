#!/usr/bin/env python3
"""Transparent retrospective R/C scientific task mapping; not 20 independent runs."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
STAGES={
'R1':('Fix exact scope/SSOT','REI F4 source-owned 80–92.5 eV direct R31 × R32, 193 BASS epochs'),
'R2':('Read original physical sources','User-uploaded Ferrett 1987 PDF printed Tables I–IV pixel-reviewed; PR289 source SHA pinned'),
'R3':('Separate source claim and hypothesis','R31/R32 directly measured ratios; Rc/Table IV uses author-derived assumptions; BASS photoevent cross-owner'),
'R4':('Construct alternative physical projection','Direct ratio partition f3S,f_n2rest,f_n3; unknown 1S range, no assumed Rp'),
'R5':('Analytical derivation','Normalization and ratio monotonicity; energy partition and Simpson x/H'),
'R6':('Same-author hostile audit','Explicit 3P vs 1S counterexample and original Table IV model-derived correction; different-author NOT_RUN'),
'R7':('Run source-conditioned calculation','1158 actual source-bin rows + 193 time-history rows and reference spectrum plot'),
'R8':('Qualify conditional claim','No actual BASS/REI common σ, no gas heat, no production, canonical_delta0'),
'R9':('Write reusable science result','THEORY_KO and REPORT_KO; units and uncertainties'),
'R10':('Preserve and handoff','Source-inclusive archive, original PDF/PR289 exact lock, next source owner'),
'C1':('Freeze code baseline','Original PR289 at exact live source commit, source PDF SHA'),
'C2':('Map theory to original file input','PR289 original 1544 source rows / 193 epoch clock; direct R31 & R32 lab table'),
'C3':('Design discretization','Piecewise-linear lab ratio interpolation; original Simpson dx/H; explicit uncertainty rectangle'),
'C4':('Set bounded execution','No new IVP; 193×2×3 source events; one Python run'),
'C5':('Implement runnable data path','code/direct_r31.py and production three CSV + RESULT.json'),
'C6':('Test implementation','21/21 Python tests + negative source SHA guards'),
'C7':('Scientific validation','Wolfram exact closure/derivatives, photoelectron energy conservation, parent strict native exposure'),
'C8':('Reproducibility and domain guards','Exact source ZIP/PDF SHA, strict 80–92.5 domain, no 97.303 eV; no interpolation error certificate'),
'C9':('Same-author hostile check','Source/Rp/3P/uncertainty hostile tests; different-author NOT_RUN'),
'C10':('Publish and handoff','Full ZIP, Git tracked code+measurements/stage JSON, two-provider source readback after ACK'),
}
for n,(label,evidence) in STAGES.items():
    rec={'stage':n,'name':label,'evidence':evidence,
         'status':'SCOPED_COMPLETE_RECORDED' if n not in ('R6','C9') else 'SELF_AUDIT_ONLY_DIFFERENT_AUTHOR_NOT_RUN',
         'retrospective':True,
         'actual_scientific_loops_in_this_unit':1,
         'canonical_progress':{'working':'33/88','central':'28/88','F4_fast':'4/7','physical_delta':0},
         'backup_in_master_archive':True,
         'git_publish_status':'PENDING_ACTUAL_ACK',
         'provider_readback_status':'PENDING_ACTUAL_ACK'}
    (ROOT/'stages'/f'{n}.json').write_text(json.dumps(rec,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf8')
ledger={'schema':'FERRETT_DIRECT_R31_R32_STAGE_LEDGER_V1',
        'scoped_completed':18,'total_stages':20,
        'different_author_R6':'NOT_RUN','different_author_C9':'NOT_RUN','native_subagent':'NOT_RUN',
        'one_bounded_scientific_work_unit':True,'records_are_retrospective':True,
        'new_physical_source_rows':1158,
        'original_DAG':{'working':'33/88','central':'28/88','F4_fast':'4/7','canonical_delta':0},
        'stages':[{**json.loads((ROOT/'stages'/f'{n}.json').read_text())} for n in STAGES]}
(ROOT/'STAGE_LEDGER.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf8')
print('Stage records created:',len(STAGES))
