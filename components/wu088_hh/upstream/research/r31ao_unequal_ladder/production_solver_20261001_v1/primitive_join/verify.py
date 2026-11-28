"""Fresh small Python-only component verification; create-only evidence directory."""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import unittest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir',type=Path,required=True)
    args=parser.parse_args();out=args.outdir.resolve();out.mkdir(parents=True,exist_ok=False)
    sys.dont_write_bytecode=True
    import join
    import test_join
    log=io.StringIO()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test_join))
    (out/'TEST_LOG.txt').write_text(log.getvalue())
    record={'schema':'WU088_PRIMITIVE_JOIN_VERIFICATION_V1','created_utc':datetime.now(timezone.utc).isoformat(),
        'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
        'python':platform.python_version(),'command':[sys.executable,str(Path(__file__).resolve()),'--outdir',str(out)],
        'scope':'Synthetic receipt arithmetic/coverage and Python preparation only; fixtures do not assert native execution',
        'unique_task_indices_in_synthetic_coverage':2592,
        'endpoint_engine_runs':0,'native_primitive_runs':0,'native_assembly_runs':0,'actual_HH_runs':0,
        'native_compiled':False,'rigorous':False,'production_admitted':False,
        'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).resolve().parent.iterdir()) if p.suffix in ('.py','.cpp','.md')},
        'upstream_module_sha256':join.modules_identity(),'native_source_identity':join.native.source_identity()['sha256'],
        'review_resolutions':['Persisted native envelope strips wrapper/result hash before strict raw-worker validator',
            'Native assembly input header SHA checked before preparation and archive/record macros compared at runtime',
            'Endpoint/native conditional evidence assumptions propagated through coverage and final disks',
            'Generated header reads bounded before allocation'],
        'test_correction':'Initializer call-count assertion excluded its function declaration after initial 5185-vs-5184 fixture assertion failure'}
    (out/'VERIFICATION.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(json.dumps({key:record[key] for key in ('status','tests_run','failures','errors','native_compiled','actual_HH_runs')}))
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main())
