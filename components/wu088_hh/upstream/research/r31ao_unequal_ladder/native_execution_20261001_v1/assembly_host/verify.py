"""Record fresh bounded wrapper tests; never fabricate native build evidence."""
import argparse
from datetime import datetime,timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import unittest


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--outdir',type=Path,required=True)
    args=parser.parse_args();out=args.outdir.resolve();out.mkdir(parents=True,exist_ok=False)
    sys.dont_write_bytecode=True
    import assembly_host as host
    import test_assembly_host
    log=io.StringIO()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test_assembly_host))
    (out/'TEST_LOG.txt').write_text(log.getvalue())
    here=Path(__file__).resolve().parent
    record={'schema':'WU088_ASSEMBLY_HOST_WRAPPER_VERIFICATION_V1','created_utc':datetime.now(timezone.utc).isoformat(),
        'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
        'python':platform.python_version(),'command':[sys.executable,str(Path(__file__).resolve()),'--outdir',str(out)],
        'real_python_subprocess_cap_tests':True,'authority_fixture_backend_and_compiler_provenance':'MOCKED_SYNTHETIC_BOUNDARY_ONLY',
        'source_identity':host.source_identity(),'file_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(here.iterdir()) if p.suffix in ('.py','.json','.md')},
        'native_assembly_compiled':False,'native_assembly_executed':False,'actual_HH_runs':0,
        'complete_actual_primitive_coverage':False,'rigorous':False,'production_admitted':False}
    (out/'VERIFICATION.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:record[k] for k in ('status','tests_run','failures','errors','native_assembly_compiled','actual_HH_runs')}))
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main())
