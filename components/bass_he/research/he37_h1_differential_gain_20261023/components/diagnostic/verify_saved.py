"""Read-only verification; stdlib only, no scientific model or renderer import."""
from pathlib import Path
import csv,hashlib,json
P=Path(__file__).resolve().parent
manifest=json.loads((P/'FILE_MANIFEST.json').read_text())
errors=[]
for row in manifest['files']:
    p=P/row['path']
    if not p.is_file():errors.append('missing '+row['path']);continue
    if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append('hash '+row['path'])
    if p.stat().st_size!=row['bytes']:errors.append('bytes '+row['path'])
with (P/'outputs/h1_gain_moments.csv').open() as f:rows=list(csv.DictReader(f))
if len(rows)!=129 or float(rows[64]['temperature_K'])!=20000:errors.append('saved grid')
r=json.loads((P/'outputs/DIAGNOSTIC.json').read_text())
if r['status']!='PASS_SCOPED' or r['max_GL_relative_error']>=3e-12:errors.append('saved diagnostic acceptance')
if r['identity']['script_sha256']!=hashlib.sha256((P/'run_diagnostic.py').read_bytes()).hexdigest():errors.append('run script identity')
render=json.loads((P/'plots/RENDER_RECEIPT.json').read_text())
if render['input_csv_sha256']!=hashlib.sha256((P/'outputs/h1_gain_moments.csv').read_bytes()).hexdigest():errors.append('render source identity')
result={'status':'REUSED_COMPLETE_VERIFIED_PAYLOAD' if not errors else 'FAIL','files_checked':len(manifest['files']),'saved_rows':len(rows),
        'new_model_evaluations':0,'new_IVP':0,'new_benchmark':0,'new_render':0,'errors':errors}
print(json.dumps(result,indent=2))
raise SystemExit(1 if errors else 0)
