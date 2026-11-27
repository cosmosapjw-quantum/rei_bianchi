"""Create phase checkpoints and immutable complete source archive for WU R30.
One data-generation job preceded this archival builder; 20 stage records are
retrospective evidence objects, not 20 independently executed simulations.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,zipfile,shutil
ROOT=Path(__file__).resolve().parent
ARCH=ROOT/'archive'
PAR=ARCH/'WU_R29_SOURCE_ORIGINAL_20261030.zip'
PARSHA='65ed097acb02f8eb91ff6518c26c8ad61e721e3fadd9b904aa2157e3508cb0ea'
assert hashlib.sha256(PAR.read_bytes()).hexdigest()==PARSHA
s=json.loads((ROOT/'results'/'SUMMARY.json').read_text())
assert s['cases']==210 and s['line_resolved_rows']==840 and s['joint_H2_photon_product_rows']==2100

r_stages={
'R1':'Research question: new lab-measured Sung R(0)-R(3) line centers in original R29 5-level absorbing SQM network; keep 34/49',
'R2':'Exact original R29 verified source and REC164 Git source blob 23626dd9a77aa4e6214f6f9c792ea18270b3940c, DOI 10.1016/j.jqsrt.2022.108412',
'R3':'Differentiate original GL2022 computed SQM, Sung lab fitted centers, REC161 Einstein A transcription, and 2011 CDMS source; no raw EMAA data',
'R4':'Construct expected individual HD photon lines and photon/no-photon conditioned final H2 branch probability',
'R5':'Derive G and G0 resolvents, first-photon hazard, integrated line photon emission and product joint-probability formulas',
'R6':'Same-author CAS 2-state identities three True; genuine distinct-author R6 NOT_RUN',
'R7':'Actually execute source-native 210 conditions, 840 spectral rows, 2100 photon-tagged product rows and 75-digit mpmath check',
'R8':'Source-qualified conditional physical atlas, no full gas cooling and no canonical DAG promotion',
'R9':'THEORY_KO maps all source terms, units, actor and first-event physics to src/spectral.py and results CSV columns',
'R10':'Preserve original R29 ZIP bytes, source provenance, 2011-to-2022 ladder shift and next EMAA/PES owner obligations',
}
c_stages={
'C1':'Fix source-anchored R29 parent SHA and REC164 measured four lines with 7 T, two reaction policies, 3 densities, 5 initial J',
'C2':'Bind original immutable R29 source-rate, A and energy arrays, and Sung four numeric line centers by Git source blob',
'C3':'Construct 5x5 photon/no-photon transient generators and two resolvent factorizations with explicit units',
'C4':'Only original 210 cases, 840 line records and 2100 product branches; no interpolation or IVP rerun',
'C5':'Executed src/spectral.py to generate physical CSV+JSON derived source observables',
'C6':'Actually run 20/20 normal Python, 20/20 python -O and compileall',
'C7':'Separate construction mpmath75 210 cases, 840 lines and 2100 product channels, Wolfram 3 identities True',
'C8':'Source guard/tamper tests and data byte comparison, original archive verified, no scientifically unjustified fit-error widening',
'C9':'No actual distinct-author C9, self-contained code/test review only: NOT_RUN',
'C10':'Immutable original-source ZIP, Library stage/phase objects and Git Draft child publication / exact handoff',
}
progress={'canonical_DAG':{'completed':34,'total':49},'R30_aux_science':{'completed':1,'total':1,'scope':'SCOPED_NEW_SPECTRAL_JOINT_PHYSICS'},'production':'NOT_ISSUED','L4':False,'physical_Q':None,'owner_ACK':None,'PES_native_threshold':None,'R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN','native_subagent':'NOT_RUN'}
( ROOT/'stages').mkdir(exist_ok=True)
( ROOT/'checkpoints').mkdir(exist_ok=True)
for kind,desc in [('R',r_stages),('C',c_stages)]:
 for i in range(1,11):
  code=f'{kind}{i}'
  o={'schema':'wu.r30.stage.v1','stage':code,'research_source':'GL2022 original SQM R29 + Sung2022 REC164 four-line fitted observation',
    'contract':'THEORY_FIRST_PHYSICAL_DATA_FIRST',
    'scientific_deliverable':desc[code],
    'status':'NOT_RUN' if code in ('R6','C9') else 'COMPLETE_SCOPED',
    'reported_execution':'retrospective checkpoint after actual science run; not independent phase-time experimental job',
    'original_parent_sha256':PARSHA,'Sung_visible_source_sha256':hashlib.sha256((ROOT/'sources/REC164_SUNG2022_PRIMARY_TABLE4_LOCK.json').read_bytes()).hexdigest(),
    'source_data_counts':{'cases':210,'lines':840,'joint_products':2100},**progress}
  (ROOT/'stages'/f'{code}.json').write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
receipt={'schema':'wu.r30.science_run_snapshot.v1','actual_new_calculations':{'primary_atlas':1,'independent_mpmath_75':1,'Wolfram_two_level_CAS':1},'data_counts':{'cases':210,'line_records':840,'product_joint_records':2100},'original_parent_SHA256':PARSHA,'source_git_REC164_blob':'23626dd9a77aa4e6214f6f9c792ea18270b3940c','central_DAG':'34/49','native_subagent':'NOT_RUN','distinct_author_R6':'NOT_RUN','distinct_author_C9':'NOT_RUN'}
(ROOT/'checkpoints'/'RUN_SNAPSHOT.json').write_text(json.dumps(receipt,indent=2)+'\n')
phase_names=['P01_THEORY','P02_PHYSICAL_CODE','P03_VALIDATION','P04_HANDOFF']
phase_files=[
 ['THEORY_KO.md','sources/REC164_SUNG2022_PRIMARY_TABLE4_LOCK.json']+[f'stages/R{i}.json' for i in range(1,11)],
 ['src/__init__.py','src/spectral.py','results/SUMMARY.json','results/R30_CASES_210.csv','results/R30_CASES_210.json','results/R30_PHOTON_ATLAS_840.csv','results/R30_RESTRICTED_H2_JOINT_2100.csv']+[f'stages/C{i}.json' for i in range(1,6)],
 ['tests/test_r30.py','tests/independent_mpmath.py','results/INDEPENDENT_MP75.json']+[f'evidence/{x}' for x in ['UNITTEST.log','UNITTEST_O.log','COMPILEALL.log','mp75.log','first_run.log','WOLFRAM_SYMBOLIC.json']]+[f'stages/C{i}.json' for i in range(6,10)],
 ['HANDOFF_NEXT_THREAD_KO.md','REPORT_KO.md','README_REPLAY.md','checkpoints/RUN_SNAPSHOT.json','stages/C10.json'],
]
for ph,fl in zip(phase_names,phase_files):
 for f in fl:assert (ROOT/f).is_file(),(ph,f)
for code in list(r_stages)+list(c_stages):
 p=ARCH/f'WU_R30_STAGE_{code}_20261030.zip'
 with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  z.write(ROOT/'stages'/f'{code}.json',f'stages/{code}.json')
  z.write(ROOT/'checkpoints'/'RUN_SNAPSHOT.json','checkpoints/RUN_SNAPSHOT.json')
  z.write(ROOT/'README_REPLAY.md','README_REPLAY.md')
for ph,fl in zip(phase_names,phase_files):
 with zipfile.ZipFile(ARCH/f'WU_R30_{ph}_SOURCE_20261030.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for f in fl:z.write(ROOT/f,f)
files=['THEORY_KO.md','REPORT_KO.md','README_REPLAY.md','HANDOFF_NEXT_THREAD_KO.md','build_delivery.py',
       'sources/REC164_SUNG2022_PRIMARY_TABLE4_LOCK.json','src/__init__.py','src/spectral.py','tests/test_r30.py','tests/independent_mpmath.py','checkpoints/RUN_SNAPSHOT.json',
       'results/R30_CASES_210.csv','results/R30_CASES_210.json','results/R30_PHOTON_ATLAS_840.csv','results/R30_RESTRICTED_H2_JOINT_2100.csv','results/SUMMARY.json','results/INDEPENDENT_MP75.json',
      *[f'evidence/{x}' for x in ['UNITTEST.log','UNITTEST_O.log','COMPILEALL.log','mp75.log','first_run.log','WOLFRAM_SYMBOLIC.json']],
       *[f'stages/{code}.json' for code in list(r_stages)+list(c_stages)],
       'archive/WU_R29_SOURCE_ORIGINAL_20261030.zip',
       *[f'archive/WU_R30_STAGE_{code}_20261030.zip' for code in list(r_stages)+list(c_stages)],
       *[f'archive/WU_R30_{ph}_SOURCE_20261030.zip' for ph in phase_names]]
manifest={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in files}
(ROOT/'checkpoints'/'MANIFEST_SHA256.json').write_text(json.dumps({'schema':'wu.r30.backup_integrity.v1','files':manifest},indent=2)+'\n')
files.append('checkpoints/MANIFEST_SHA256.json')
full=ARCH/'WU_R30_SOURCE_ORIGINAL_20261030.zip'
with zipfile.ZipFile(full,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for f in files:z.write(ROOT/f,f)
with zipfile.ZipFile(full) as z:
 assert z.testzip() is None
 for f,h in manifest.items():assert hashlib.sha256(z.read(f)).hexdigest()==h
 print(json.dumps({'archive':str(full),'bytes':full.stat().st_size,'sha256':hashlib.sha256(full.read_bytes()).hexdigest(),'members':len(z.namelist()),'manifest_SHA_pass':len(manifest),'stage_ZIPs':20,'phase_ZIPs':4},indent=2))
