"""Authorized evidence-only repair; reads stored evidence, executes no solver/oracle."""
import json
from campaign import P,dump,sha,finite_checks
E=P/'evidence'
preserved={p.name:sha(p) for p in E.iterdir() if p.name.startswith('FIRST_') or p.name in ('BUILD_RECEIPT.json','CAMPAIGN_RECEIPT.json','DECIMAL80_REFERENCE.json','PRELAUNCH.json','STALE_BINARY_NEGATIVE.json')}
v=json.loads((E/'VALIDATION.json').read_text())
dump('VALIDATION_BEFORE_REPAIR.json',v)
rows=[json.loads(line) for line in (E/'FIRST_CAMPAIGN.stdout').read_text().splitlines()]
refs=json.loads((E/'DECIMAL80_REFERENCE.json').read_text())['epochs']
checks,ledgers=finite_checks([r for r in rows if r['kind']=='trajectory'],refs)
v['checks']=[r for r in v['checks'] if not r['name'].startswith(('chemistry_','energy_','baryon_','helium_'))]+checks
v['ledger_relative_errors']=ledgers
v['denominator_policy']='finite identity residual denominators are absolute epoch term sums; final-ledger scales in the trajectory norm and max(|native|,|reference|) per epoch are comparison-only, never initial or residual scales'
v['repair']={'authority':'Astra one minimal evidence/validation/report repair','builds':0,'native_solver_runs':0,'reference_runs':0,'raw_receipts_preserved':True}
dump('VALIDATION.json',v)
assert preserved=={name:sha(E/name) for name in preserved}
dump('VALIDATION_REPAIR_RECEIPT.json',{'status':'PASS','preserved_sha256':preserved,'builds':0,'native_solver_runs':0,'reference_runs':0,'checks':len(v['checks']),'ledger_max_relative_error':max(r['relative_error'] for r in ledgers)})
print(json.dumps({'status':v['status'],'checks':len(v['checks']),'ledger_max_relative_error':max(r['relative_error'] for r in ledgers),'finite_max':max(r['value'] for r in checks if not r['name'].startswith('ledger_'))}))
