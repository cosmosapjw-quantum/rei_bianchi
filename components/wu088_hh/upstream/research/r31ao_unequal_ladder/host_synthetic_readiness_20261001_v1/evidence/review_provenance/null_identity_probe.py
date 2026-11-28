"""Four targeted synthetic missing-identity probes; no native build or HH data."""
from pathlib import Path
import hashlib
import json
import sys
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root))
source=root/'provenance_gate.py'
before=hashlib.sha256(source.read_bytes()).hexdigest()
from test_provenance_gate import ProvenanceGateTests

cases=[]
for mode in ('compiler_null','binary_null','configure_log_null','install_log_null'):
    fixture=ProvenanceGateTests()
    fixture.setUp()
    try:
        if mode=='compiler_null':
            fixture.record['compiler']['sha256']=None
            fixture.compiler.write_bytes(b'altered compiler without an expected identity')
        elif mode=='binary_null':
            item=fixture.record['libraries']['flint']
            item['binary_sha256']=None
            Path(item['binary_path']).write_bytes(b'\x7fELFaltered binary without expected identity')
        else:
            stage='configure' if mode=='configure_log_null' else 'install'
            log=next(x for x in fixture.record['libraries']['flint']['build_logs'] if x['stage']==stage)
            log['sha256']=None
            Path(log['path']).write_text('altered stage log without expected identity')
        try:
            result=fixture.verify()
            cases.append({'case':mode,'accepted':True,'status':result['verification']['status']})
        except Exception as exc:
            cases.append({'case':mode,'accepted':False,'exception':type(exc).__name__,'message':str(exc)})
    finally:
        fixture.doCleanups()
after=hashlib.sha256(source.read_bytes()).hexdigest()
print(json.dumps({'scope':'SYNTHETIC_FIXTURES_ONLY_PIN_TABLE_PATCHED_BY_TEST_FIXTURE',
                 'source_sha256_before':before,'source_sha256_after':after,
                 'source_stable_during_probe':before==after,'cases':cases,
                 'native_builds':0,'actual_HH_runs':0},indent=2))
