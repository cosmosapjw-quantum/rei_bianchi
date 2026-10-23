"""Verify self-contained fresh-copy inputs/imports without diagnostic execution."""
import hashlib
import json
from local_flows import BASE, rate, LAMBDA

manifest=json.loads((BASE/'inputs/copy_manifest.json').read_text())
rows=[]
for row in manifest['copies']:
    observed=hashlib.sha256((BASE/row['copy']).read_bytes()).hexdigest()
    if observed != row['source_sha256']:
        raise ValueError('Immutable input SHA256 mismatch: '+row['copy'])
    rows.append({'copy':row['copy'],'sha256':observed,'matches_baseline_source':True})
result={'status':'PREPARE_ONLY_PASS','fresh_directory':str(BASE),'copies':rows,
        'alpha_1000K_m3_s':rate(1000.)[0],'lambda_neutron_s-1':LAMBDA,
        'imports':'local_flows, numpy, scipy.special','scientific_diagnostic_executed':False}
(BASE/'results/prepare_only.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
