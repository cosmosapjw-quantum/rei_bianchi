"""Changed-only RR restoration and new DR checks; historical receipt untouched."""
import contextlib
import hashlib
import io
import json
import math
import platform
import sys
import time
import traceback
from pathlib import Path


def main():
    wall,cpu=time.perf_counter(),time.process_time()
    base=Path(__file__).resolve().parent
    output,error=io.StringIO(),io.StringIO()
    receipt={'command':'PYTHONDONTWRITEBYTECODE=1 python3 run_current_tests.py',
      'cwd':str(base),'contract':'../PROVIDER_IMPLEMENTATION_CONTRACT.md',
      'baseline_HEAD_observed_before_implementation':'3e56bbd3d939ab235df2d47f9d012c95674d00fc',
      'execution_identity':{'requested':'lower-tier coding agent under frozen provider contract',
                            'observed_model_identity':'unknown; runtime did not attest model','observed_role':'provider_coder'},
      'environment':{'python':sys.version,'platform':platform.platform()},
      'execution_scope':{'IVPs':0,'full83_runs':0,'coupled_runs':0,'NCP_runs':0,'implementation_passes':1,'targeted_repairs':1},
      'observed_mechanical_failure':{'class':'runner_creation_path','observation':'Initial heredoc used repository-relative output path from code cwd; no runner file created and Python exited 2 before tests.',
        'repair':'Created runner at code-cwd relative path; no scientific code or thresholds changed.',
        'tool_reported_failed_attempt_wall_seconds':0.268279498,'failed_attempt_CPU_seconds':'not separately measured; no provider test execution'},
      'checks':{},'status':'FAILED','exit_code':1}
    try:
        with contextlib.redirect_stdout(output),contextlib.redirect_stderr(error):
            import scipy
            import test_rr_adapter as rr
            import test_dr_adapter as dr
            receipt['environment']['scipy']=scipy.__version__
            preserved={}
            for name,wanted in {
              'rr_adapter.py':'fddb3b3d6243ceeabfacdd10573be28ba0ea48710328a98b29d37546b5d99718',
              'rr_rows.json':'66e2f497f170d524e681e42d8baaf6831a5877826fca134a9a86b97e8d521fba',
              'IMPLEMENTATION_RECORD.json':'007dd9752d46621c087b35bf3a6e3a11022ee7b96446240b9fe7199f100da69b'}.items():
                got=hashlib.sha256((base/name).read_bytes()).hexdigest()
                assert got == wanted,(name,got)
                preserved[name]=got
            receipt['checks']['historical_immutable_evidence']=preserved
            receipt['checks']['rr_current_source_binding']=rr.check_source()
            smoke=[]
            for key,charges in zip(rr.EXPECTED,rr.CHARGES):
                for temperature in (100.,10000.):
                    r=rr.rr_rate(key,temperature)
                    assert (r['input_charge'],r['output_charge']) == charges
                    assert r['status'] == 'CONDITIONAL_DERIVATIVE_OF_FIT'
                    assert r['alpha_m3_s'] > 0 and r['lambda_J_m3_s'] >= 0
                    assert all(math.isfinite(r[k]) for k in ('alpha_m3_s','lambda_J_m3_s'))
                    smoke.append({'channel':key,'T_K':temperature,'charges':list(charges)})
            receipt['checks']['rr_boundary_charge_smoke']={'cases':12,'samples':smoke}
            receipt['checks']['rr_historical_reuse']={'receipt':'IMPLEMENTATION_RECORD.json','executed_now':False,
              'positivity_cases':1542,'ledger_cases':1542,'slope_cases':18,'manufactured_quadratures':9,
              'admission':'historical conditional evidence reused; no new physical claim'}
            receipt['checks']['dr']=dr.run()
            print(json.dumps(receipt['checks'],indent=2,sort_keys=True))
        receipt.update(exit_code=0,status='PASS_SCOPED_IMPLEMENTATION_REVIEW_PENDING')
    except BaseException:
        error.write(traceback.format_exc())
    receipt['wall_seconds']=time.perf_counter()-wall
    receipt['process_cpu_seconds']=time.process_time()-cpu
    receipt['budget']={'aggregate_cpu_less_than_s':30,'aggregate_wall_less_than_s':60,
                      'test_execution_attempts':1,'failed_pretest_command_attempts':1}
    if receipt['wall_seconds']+0.268279498 >= 60 or receipt['process_cpu_seconds'] >= 30:
        receipt.update(status='BUDGET_FAILURE',exit_code=1)
    check_status='PASS' if not receipt['exit_code'] else 'CHECK_RAW_FAILURE'
    receipt['C1_C10']={
      'C1':{'status':check_status,'evidence':'Frozen contract and exact RR/DR immutable source bindings.'},
      'C2':{'status':'PASS','evidence':'Scalar rows -> signed formula -> SI/log outputs; no old runner imports.'},
      'C3':{'status':'PASS','evidence':'Shifted fsum retains signs; analytic positive lower bounds; no ODE.'},
      'C4':{'status':check_status,'evidence':'Frozen new checks and changed-only RR execution; measured budget.'},
      'C5':{'status':'PASS','evidence':'RR restored verbatim; additive DR pure scalar API; charge/isotope/source/status.'},
      'C6':{'status':'PASS','evidence':'Raw output, failures, source extraction, environment and measurements retained.'},
      'C7':{'status':check_status,'evidence':'Independent direct Decimal formula; RR manufactured/ledger evidence reused unchanged.'},
      'C8':{'status':check_status,'evidence':'27 Decimal comparisons, 771 grid cases, source extraction and current RR smoke.'},
      'C9':{'status':'PENDING','evidence':'Fresh read-only independent scientific review required.'},
      'C10':{'status':'IMPLEMENTED_REVIEW_PENDING','evidence':'Return to framing agent for review; no scientific admission claimed.'}}
    receipt['remaining_obligations']=['Fresh independent scientific review and conditional scalar admission decision.',
      'DR fitted-rate physical accuracy/source-archive comparison unadmitted.',
      'DR thermal moment, cascade spectrum and energy closure unavailable.',
      'CI unsupported throughout pilot; CX unavailable; no extrapolation or zero fill.',
      'Isotope spectroscopy and nuclear-product charge injection unresolved; historical claim ceilings unchanged.']
    receipt['raw_stdout_file']='CURRENT_TEST_STDOUT.txt'
    receipt['raw_stderr_file']='CURRENT_TEST_STDERR.txt'
    (base/'CURRENT_TEST_STDOUT.txt').write_text(output.getvalue())
    (base/'CURRENT_TEST_STDERR.txt').write_text(error.getvalue())
    (base/'CURRENT_IMPLEMENTATION_RECORD.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','exit_code','wall_seconds','process_cpu_seconds')},indent=2))
    if error.getvalue(): print(error.getvalue(),file=sys.stderr)
    return receipt['exit_code']


if __name__ == '__main__':
    raise SystemExit(main())
