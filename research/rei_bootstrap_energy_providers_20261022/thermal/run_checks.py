"""Bounded standard-library checks and machine-readable scalar receipt."""
import json
import platform
import subprocess
import sys
import unittest
from pathlib import Path
import test_thermal_ledger as tests

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]


def git(*args):
    return subprocess.check_output(['git',*args],cwd=REPO,text=True).strip()


def main():
    tests.RECORDS.clear()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.ScalarChecks)
    result=unittest.TextTestRunner(verbosity=2,stream=sys.stdout).run(suite)
    controls=tests.discrimination_controls()
    receipt={
      'classification':'EXECUTED_SCALAR_CHECKS_PENDING_INDEPENDENT_REVIEW',
      'scalar_checks_passed':result.wasSuccessful(),
      'interpreter':sys.executable,'python_version':platform.python_version(),
      'executor':{'requested':'lower-tier coding agent under frozen Astra contract',
                  'observed':'unknown; runtime model identity not exposed'},
      'baseline_HEAD':git('rev-parse','HEAD'),
      'dirty_path_summary':git('status','--short'),
      'changed_files':[str(p.relative_to(REPO)) for p in sorted(ROOT.iterdir()) if p.is_file()],
      'fixture_ids':[f'T{i}' for i in range(1,9)],
      'unit_test_methods':result.testsRun,
      'numerical_identity_checks':len(tests.RECORDS),
      'invalid_input_rejections':12,
      'discrimination_checks':len(controls),
      'checks':tests.RECORDS,'discrimination_results':controls,
      'maximum_normalized_residual':max(r['normalized_residual'] for r in tests.RECORDS),
      'maximum_normalized_residual_definition':'abs(residual)/(64 eps sum(abs(identity terms))); zero-scale exact-zero -> 0',
      'reused29':{'directory':'/workspace/scratch/d855c1e0c0ed/recovery_checkpoint/published_a7bff87',
                  'receipt':'LEDGER_CHECKS_RESULT.json','review':'LEDGER_CHECKS_REVIEW.json',
                  'status':'reused by reference without rerun or relabeling'},
      'physical_IVPs':0,'old83_reruns':0,'NCP_runs':0,
      'limits':{'wall_seconds_per_command':60,'memory_expectation_MiB':128},
      'claim_boundary':'Scalar supplied-moment arithmetic only; no scientific admission or predictive provider/spectral/coupled/production claim.'}
    (ROOT/'THERMAL_SCALAR_RESULT.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'numerical_identity_checks':len(tests.RECORDS),
                      'discrimination_checks':len(controls),
                      'maximum_normalized_residual':receipt['maximum_normalized_residual'],
                      'all_controls_detected':all(c['detected'] for c in controls)}))
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__':
    raise SystemExit(main())
