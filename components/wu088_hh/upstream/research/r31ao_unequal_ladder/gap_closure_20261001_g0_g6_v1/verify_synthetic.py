"""Run only this overlay's declared synthetic/exact/static suites.

No original scientific suite, actual array payload or native binary is run.
Use a new output directory; existing verification records are not overwritten.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

SUITES={
    'G1_exact_theorem':['theorem_checks.test_exact_helpers'],
    'G2_exact_decoder':['exact_raw_decoder.test_decoder'],
    'G3_exact_gram':['exact_gram.test_engine','exact_gram.test_resource_review'],
    'G4_callback_static_exact':['validated_callback.test_contract'],
    'G4_assembly_static_exact':['validated_callback.test_assembly'],
    'G4_optional_point_oracle':['validated_callback.test_high_precision_optional'],
    'G5_endpoint':['endpoint_bound.test_endpoint','endpoint_bound.test_input_contract'],
    'G6_synthetic_pilot':['interior_pilot.test_interior'],
    'G6_Petras_draft_static':['interior_pilot.test_native_draft'],
    'synthetic_pipeline':['certificate_pipeline.test_pipeline'],
    'host_process_guard':['host_guard.test_guard'],
    'Frozen107_shaped_synthetic_adapter':['frozen_input.test_adapter'],
}
LOCAL_IMPORT_SUITES={
    'G1_exact_theorem':'theorem_checks',
    'G4_callback_static_exact':'validated_callback',
    'G4_assembly_static_exact':'validated_callback',
    'G4_optional_point_oracle':'validated_callback',
}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parent
    output=Path(args.output).resolve();output.mkdir(parents=True,exist_ok=False)
    records=[]
    for name,modules in SUITES.items():
        workdir=root
        if name in LOCAL_IMPORT_SUITES:
            workdir=root/LOCAL_IMPORT_SUITES[name]
            modules=[m.rsplit('.',1)[-1] for m in modules]
        argv=[sys.executable,'-B','-m','unittest',*modules,'-v']
        start=time.monotonic()
        run=subprocess.run(argv,cwd=workdir,capture_output=True,text=True,timeout=60)
        log=run.stdout+run.stderr;(output/(name+'.log')).write_text(log)
        count=re.search(r'Ran (\d+) tests?',log)
        skipped=re.search(r'OK \(skipped=(\d+)\)',log)
        records.append({'suite':name,'command':argv,'cwd_relative_to_loop':str(workdir.relative_to(root)),
                        'exit_code':run.returncode,
                        'tests':int(count.group(1)) if count else None,
                        'skipped':int(skipped.group(1)) if skipped else 0,
                        'wall_seconds':time.monotonic()-start,'log':name+'.log'})
    source_ids=[];syntax=[]
    for file in sorted(root.rglob('*')):
        if '__pycache__' in file.parts or not file.is_file() or file.suffix not in ('.py','.cpp','.hpp','.sh'):
            continue
        data=file.read_bytes();rel=str(file.relative_to(root))
        source_ids.append({'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
        if file.suffix=='.py':
            ast.parse(data,filename=rel);syntax.append({'path':rel,'kind':'PYTHON_AST','exit_code':0})
        elif file.suffix=='.sh':
            run=subprocess.run(['bash','-n',str(file)],capture_output=True,text=True)
            syntax.append({'path':rel,'kind':'BASH_SYNTAX','exit_code':run.returncode,'stderr':run.stderr})
    ok=all(r['exit_code']==0 and r['tests'] for r in records) and all(r['exit_code']==0 for r in syntax)
    report={'schema':'WU088_FRESH_SYNTHETIC_INTEGRATION_VERIFICATION_V1',
            'status':'PASS_WITH_EXPLICIT_OPTIONAL_SKIPS' if ok else 'FAIL',
            'python':platform.python_version(),'suites':records,'syntax':syntax,
            'source_identities':source_ids,'science_commands':0,'native_builds':0,
            'numerical_certificate_runs':0,'rigorous':False,'certified_epsilon':None,
            'certified_eta':None,'historical_test_counts_changed':False}
    (output/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'suites':records},ensure_ascii=False))
    raise SystemExit(0 if ok else 1)


if __name__=='__main__':main()
