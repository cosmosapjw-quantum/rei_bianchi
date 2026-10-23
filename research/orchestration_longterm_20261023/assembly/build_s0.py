#!/usr/bin/env python3
"""Build a partial-intake snapshot without private conversations/provider inventories."""
import json,pathlib,re,hashlib,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'assembly'; OUT.mkdir(exist_ok=True)
pattern=re.compile(r'(rei[_ -]?bianchi|rec[_ -]?bianchi|bass[_ -]?(he|cr)|wu088|orchestration|angular.thermo|hh_phys|c23b|thermal|numerics)',re.I)
initial=json.loads((ROOT/'intake/initial_sources.json').read_text())
items=[]
for x in initial['library']['items']:
 if x.get('modified_at','')>='2026-10-22' and pattern.search(x.get('name','')):
  items.append({k:x[k] for k in ['name','file_id','library_file_id','modified_at','size_bytes'] if k in x})
coverage={'schema':'SOURCE_COVERAGE_V1','as_of':'2026-10-23','snapshot':'S0_INTAKE_PARTIAL','complete':False,'scope':'Task-relevant intake metadata and saved source copies; no claim of exhaustive review or source admission.', 'library':{'enumerated':len(initial['library']['items']),'pagination_complete':initial['library'].get('next_cursor') is None,'selection':'modified >= 2026-10-22 UTC and task-name match; filename selection does not prove scientific relevance','selected_metadata':items},'drive':{'folder_rows_scanned':1000,'folder_capped':True,'search_rows':4,'limit':'indexing/search limited; no exhaustive Drive claim'},'dropbox':{'dossier_pages_saved':6,'rows_saved':3366,'has_more':False,'search_rows':20,'limit':'immediate dossier folder listing exhausted; search result completeness does not imply provider completeness'},'conversation':{'search_calls_reported':3,'last_call_threads_reported':7,'limit':'last response truncated; private conversation bodies excluded'},'repositories':{'status':'authority coverage reports pending; source copies do not imply full repository traversal'},'source_metadata':['intake/initial_sources.json','intake/drive_dossier.json','intake/drive_scan.json','intake/db_dossier.json','intake/db_dossier2.json','intake/dropbox_scan.json','intake/context3.json']}
(OUT/'SOURCE_COVERAGE.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
selected=[OUT/'SOURCE_COVERAGE.json',pathlib.Path(__file__).resolve()]
for area in ['atomic','thermal','rei','numerics']:
 for f in (ROOT/area).rglob('*'):
  if f.is_file() and ('sources' in f.relative_to(ROOT).parts or f.suffix=='.md' or f.name in {'LONGTERM_CONTRACTS.json','LONGTERM_SURVEY.json'}):selected.append(f)
manifest={'stage':'S0','partial_intake':True,'excluded':'Private conversation bodies, raw giant provider inventories and unrelated items','files':[]}
for f in sorted(set(selected)):
 b=f.read_bytes();manifest['files'].append({'path':str(f.relative_to(ROOT)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(OUT/'S0_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(OUT/'ORCHESTRATION_LONGTERM_20261023_S0_INTAKE.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(set(selected+[OUT/'S0_MANIFEST.json'])):z.write(f,str(f.relative_to(ROOT)))
print(json.dumps({'zip':str(OUT/'ORCHESTRATION_LONGTERM_20261023_S0_INTAKE.zip'),'members':len(selected)+1,'library_selected':len(items)}))
