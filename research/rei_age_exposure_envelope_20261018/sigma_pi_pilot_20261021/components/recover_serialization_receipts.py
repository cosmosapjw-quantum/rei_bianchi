#!/usr/bin/env python3
"""Repair only JSON receipts from complete saved arrays; no solver invocation."""
import sys,time,json,math
from pathlib import Path
sys.dont_write_bytecode=True
ENTRY_STARTED=time.monotonic()
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unified_pilot as u
import numpy as np

def main():
    base=u.ROOT/'z2_extension/results';inventory=json.loads((base/'SERIALIZATION_FAILURE_INVENTORY.json').read_text())
    manifest=json.loads((base/'MANIFEST.json').read_text());cases={c['id']:c for c in manifest['cases']};rows=[]
    for record in inventory['rows']:
        identifier=record['id'];c=cases[identifier];folder=base/'cases'/identifier;receipt=folder/'RESULT.json';original=folder/'RESULT.serialization_failure.json'
        old=json.loads(receipt.read_text())
        if old['status']!='FAILED_WORKER_EXIT' or original.exists():raise ValueError('RECOVERY_REQUIRES_UNMODIFIED_FAILURE:'+identifier)
        original_bytes=receipt.read_bytes();old_hash=u.sha(receipt);attempt_hash=u.sha(folder/'ATTEMPT.json')
        for name in ('raw.npz','tail.npz'):
            if u.sha(folder/name)!=record[name]['sha256']:raise ValueError('RAW_CHANGED_SINCE_FAILURE_INVENTORY')
        prefix_folder=u.ROOT/c['prefix_relative']
        for name,key in [('raw.npz','prefix_raw_sha256'),('INPUT.json','prefix_input_sha256'),('RESULT.json','prefix_result_sha256')]:
            if u.sha(prefix_folder/name)!=c[key]:raise ValueError('PREFIX_IDENTITY_MISMATCH')
        if json.loads((folder/'INPUT.json').read_text())!=c:raise ValueError('INPUT_IDENTITY_MISMATCH')
        with np.load(folder/'raw.npz') as f:raw={k:f[k] for k in f.files}
        with np.load(folder/'tail.npz') as f:tail={k:f[k] for k in f.files}
        with np.load(prefix_folder/'raw.npz') as f:prefix={k:f[k] for k in f.files}
        out={k:v for k,v in raw.items() if k not in ('x','raw_y')}
        sol=u.SimpleNamespace(t=raw['x'],y=raw['raw_y'],success=None);tail_sol=u.SimpleNamespace(t=tail['x'],y=tail['raw_y'])
        checks=u.tail_validate(c['config'],sol,out,prefix,tail_sol);checks.pop('solver_success')
        checks['saved_tail_endpoint_coverage']=bool(len(tail['x'])==33 and tail['x'][-1]==math.log(7.))
        checks['prefix_diagnostics_exact']=all(np.array_equal(raw[k][:121],prefix[k]) for k in prefix if k not in ('x','raw_y'))
        checks['combined_tail_exact']=bool(np.array_equal(raw['raw_y'][:,120:],tail['raw_y']) and np.array_equal(raw['x'][120:],tail['x']))
        if not all(checks.values()):raise ValueError('SAVED_RAW_GATE_FAILED:'+identifier+':'+str([k for k,v in checks.items() if not v]))
        # Original failure bytes are create-only; no raw or ATTEMPT rewrite.
        with original.open('xb') as f:f.write(original_bytes)
        result={'id':identifier,'config':c['config'],'status':'COMPLETED','exit':0,'checks':checks,
          'completion_basis':'SAVED_RAW_REVALIDATED_AFTER_SERIALIZATION_FAILURE',
          'historical_execution_status':old['status'],'recorded_supervisor_exit':old.get('exit'),
          'historical_failure_receipt_sha256':old_hash,'historical_failure_receipt_path':str(original),
          'nfev':None,'solver_message':None,'observed_solver_success':None,'worker_wall_s':None,'peak_rss_bytes':None,
          'unavailable_metadata_reason':'Original in-memory RESULT was not serialized; full saved endpoint coverage is the completion evidence.',
          'initial':{k:float(v[0]) for k,v in out.items()},'endpoint':{k:float(v[-1]) for k,v in out.items()},
          'raw_sha256':record['raw.npz']['sha256'],'raw_bytes':(folder/'raw.npz').stat().st_size,'tail_raw_sha256':record['tail.npz']['sha256'],
          'prefix_provenance':{k:v for k,v in c.items() if k.startswith('prefix_')},
          'executed_runner_sha256':'49d4464ecb4682846ace0d07411d3a9f9e49bc494fa8d641b567306725374d97',
          'recovery_execution':{'argv':sys.argv,'exit':0,'source_sha256':u.sha(__file__),'scientific_solver_calls':0},
          'independent_saved_raw_audit':'rei_unified_20261021/independent_audit/B2_RECEIPT_FAILURE_RAW_AUDIT.json'}
        u.atomic_json(receipt,result)
        if u.sha(original)!=old_hash or u.sha(folder/'ATTEMPT.json')!=attempt_hash:raise ValueError('FAILURE_PROVENANCE_CHANGED')
        rows.append({'id':identifier,'old_result_sha256':old_hash,'corrected_result_sha256':u.sha(receipt),'attempt_sha256_unchanged':attempt_hash,'raw_sha256_unchanged':record['raw.npz']['sha256'],'checks':checks})
    elapsed=time.monotonic()-ENTRY_STARTED
    report={'status':'PASS_SAVED_RAW_RECEIPTS_RECOVERED','recovered':len(rows),'ODE_calls':0,'argv':sys.argv,'exit':0,'elapsed_s':elapsed,'rows':rows,'source_sha256':u.sha(__file__)}
    u.atomic_json(base/'SERIALIZATION_RECEIPT_RECOVERY.json',report)
    u.atomic_json(base/'controllers'/(str(time.time_ns())+'.json'),{'profile':'sandbox','controller_elapsed_s':elapsed,'argv':sys.argv,'operation':'data_only_receipt_recovery','scientific_solver_calls':0})
    print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
