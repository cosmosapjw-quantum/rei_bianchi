#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/(ROOT.name+'_FULL.zip')

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

# One bounded R1..R10/C1..C10 cycle, method steps not independent physics simulations.
steps={
'R1':'Frozen scientific question and source-owner handoff; evidence/PREREGISTERED_OBJECTIVE.md',
'R2':'Primary Ferrett/Drake/Langer and FS2010 & official Grackle literature compared to actual PR294/PR295 source locks',
'R3':'Different native K and Ferrett n2+n3 denominators, HHe 5-state versus REI17 owners, units and proper clocks distinguished',
'R4':'Conservative HHe source map, photon/energy-balance alternative and energy-only secondary-ionization simplex formulated',
'R5':'Derived conserved 5-component F5, EOS electron-loading and threshold-owner difference with no double-count source policy',
'R6':'One same-author hostile reviewer pass; distinct-author R6 explicitly NOT_RUN; documented 10 concrete attacks/corrections',
'R7':'Numerical original 192 saved intervals and Wolfram symbolic mass/charge exact identities; geometry/heat still conditional',
'R8':'Bounded-source physics admitted as source-scoped auxiliary; no true heat, shared F/J, native REI17, IVP or CMB promotion',
'R9':'THEORY_KO.md links definitions to computational equations and source data outputs, with SI/CGS units noted',
'R10':'Clean-restorable ZIP, publisher-free Git subtree target, explicit handoff and report',
'C1':'Two immutable parent archives, 193 native BASS epoch chemistry/thermal, 192 causal arrival records and 579 photo source events',
'C2':'Map source columns/owners into state Y=(H I,H II,He I,He II,He III), original Href norm, Cv and thresholds',
'C3':'Use original saved proper interval, avoid new quadrature/IVP, preserve all 192 source rows, conservative heat/secondary bounds',
'C4':'Source-owner immutable independent branch from PR295, read-only input PR294, small deterministic CPU-only physical loop',
'C5':'code/science.py computes per-interval 5-component F, thermal coefficients, secondary energy cone; code/plot_science.py makes plots',
'C6':'21 targeted Python tests including source hash guard, conservation, thermodynamics, EOS and recorded original source',
'C7':'21 tests + Wolfram exact identities; original BASS owner observational compatibility remains conditional',
'C8':'19-digit CSV, six PNGs, exact replay/manifest and independent clean archive restore; clock/EOS residuals measured',
'C9':'Same-author adversarial source/model review only; native distinct-author C9 NOT_RUN',
'C10':'Source-inclusive checksum and real Library/Drive backup readback, independent Draft PR if created, no release or merge'}

for key,description in steps.items():
    evidence={'schema':'PHYS_MATH_RESEARCH_LOOP_STAGE_RECORD_V1','stage':key,'selected_scope':'R1-R10_AND_C1-C10_ONE_BOUNDED_SCIENCE_UNIT',
      'status':'COMPLETED_SCOPED_SELF_REVIEW' if key in ('R6','C9') else 'COMPLETED_SCOPED',
      'actual_scientific_work':description,
      'backing_artifacts':['evidence/PREREGISTERED_OBJECTIVE.md','THEORY_KO.md','REPORT_KO.md','ADVERSARIAL_AUDIT_KO.md','results/LI2E1_HHE_CAUSAL_SOURCE_192.csv','results/RESULT.json'],
      'progress':{'WORKING':'33/88','CENTRAL':'28/88','F4_FAST':'4/7','CANONICAL_PHYSICAL_DELTA':0,'AUXILIARY':'1/1_SCOPED'},
      'publication_and_backup':'see final verified provider/readback + Git receipts, no automatic per-stage remote claim',
      'distinct_author_independent_review':'NOT_RUN',
      'no_new_IVP':True,'production':'HOLD'}
    (ROOT/'stages'/(key+'.json')).write_text(json.dumps(evidence,ensure_ascii=False,sort_keys=True,indent=2)+'\n')

res=ROOT/'results'
outputs=sorted([p for p in res.iterdir() if p.is_file()])
outsha={p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in outputs}
(ROOT/'evidence'/'OUTPUT_SHA256.json').write_text(json.dumps(outsha,indent=2,sort_keys=True)+'\n')
allfiles=sorted((p for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts and p.suffix!='.pyc'),key=lambda x:x.relative_to(ROOT).as_posix())
m={'schema':'REI_F4_20261031_SHA256_SOURCE_INCLUSIVE_MANIFEST_V1','entries':[{'name':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in allfiles]}
(ROOT/'MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in allfiles+[ROOT/'MANIFEST.json']:
  f=zipfile.ZipInfo(ROOT.name+'/'+p.relative_to(ROOT).as_posix(),date_time=(2026,10,31,0,0,0))
  f.compress_type=zipfile.ZIP_DEFLATED
  f.external_attr=(0o100644<<16)
  z.writestr(f,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
with zipfile.ZipFile(OUT) as z:assert z.testzip() is None
print(json.dumps({'zip':str(OUT),'bytes':OUT.stat().st_size,'sha256':digest(OUT),'manifest_entries':len(allfiles),'zip_members':len(allfiles)+1,'generated_results':len(outputs)},indent=2))
