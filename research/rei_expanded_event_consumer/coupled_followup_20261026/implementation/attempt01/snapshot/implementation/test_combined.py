"""Single changed-dependency child; no prior suites, evolution or quadrature."""
import json
import os
from pathlib import Path
import traceback

from test_normalized_beta_client import run_tests as client_checks
from test_moving_exchange import run_tests as exchange_checks

HERE=Path(__file__).resolve().parent;UNIT=HERE.parent


def main():
    output=Path(os.environ['FOLLOWUP_OUTPUT_DIR']);checks=[]
    def write(name,value):(output/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    def checkpoint(label):write('checks_partial.json',checks);print(label,flush=True)
    try:
        checks.extend(dict(lane='normalized_beta',**row) for row in client_checks())
        checkpoint('normalized_client_complete')
        checks.extend(dict(lane='moving_exchange',**row) for row in exchange_checks(UNIT/'stopping/IMPLEMENTATION_CONTRACT.json'))
        checkpoint('moving_exchange_complete')
        results={'checks':checks,'pass_count':sum(r['pass'] for r in checks),'total':len(checks),
          'passed':all(r['pass'] for r in checks),'scope':'normalized_beta_count_suboperator_and_conditional_moving_exchange',
          'empirical_rate_admission':False,'full_client_admission':False,'actual_endpoint_thermal_activation':False,
          'legacy_source_semantic_replacement':False,'thermal_heat':None,'prior_test_groups_replayed':0,
          'source_atom_scans':0,'quadrature':False,'IVPs':0,'requested_executor':'gpt-6.1-sol/high','observed_runtime_model':'UNEXPOSED'}
        write('TEST_RESULTS.json',results)
        return 0 if results['passed'] else 1
    except BaseException as exc:
        write('FAILURE.json',{'class':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()})
        checkpoint('exception');raise


if __name__=='__main__':raise SystemExit(main())
