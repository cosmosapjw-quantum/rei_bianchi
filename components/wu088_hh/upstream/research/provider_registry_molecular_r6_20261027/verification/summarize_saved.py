"""Read saved R6 results; no production/reference import or solver execution."""
from pathlib import Path
from fractions import Fraction
import hashlib, json

P=Path(__file__).resolve().parents[1]
def rounded(q,digits=15,up=False):
    q=Fraction(q); scale=10**digits
    units=-((-q.numerator*scale)//q.denominator) if up else q.numerator*scale//q.denominator
    whole,part=divmod(units,scale)
    return str(whole)+'.'+str(part).rjust(digits,'0')
primary=json.loads((P/'raw/PRIMARY_RESULTS.json').read_text())
ref=json.loads((P/'raw/INDEPENDENT_RESULTS.json').read_text())
blocks=[]
for b in primary['graph']['blocks']:
    blocks.append({'mu':b['mu'],'degree':b['N'],'H_approx':float(Fraction(b['H'])),
                   'H_exact':b['H'],'beta_lower_decimal_floor':rounded(b['beta_lower']),
                   'rho_upper_decimal_ceiling':rounded(b['rho_upper'],up=True),
                   'rho_exact':b['rho_upper'],'bits':b['precision_bits']})
width=max(Fraction(x['hi'])-Fraction(x['lo']) for x in primary['thermal']['pi'])
out={'schema':'WU_R6_SAVED_RESULT_SUMMARY_V1','operation':'POSTPROCESS_SAVED_RESULTS_NO_SCIENCE_REPLAY',
     'input_sha256':{n:hashlib.sha256((P/'raw'/n).read_bytes()).hexdigest() for n in ('PRIMARY_RESULTS.json','INDEPENDENT_RESULTS.json')},
     'source_blocks':blocks,'maximum_pi_width_exact':str(width),'maximum_pi_width_approx':float(width),
     'lambda_approx':float(Fraction(primary['graph']['lambda'])),
     'primary':{k:primary[k] for k in ('case_count','failure_count','groups','actual_cpu_seconds_at_finalize','actual_process_cpu_seconds_at_finalize','actual_wall_seconds_at_finalize')},
     'independent':{k:ref[k] for k in ('case_count','mismatch_count','precision','actual_cpu_seconds_at_finalize','actual_process_cpu_seconds_at_finalize','actual_wall_seconds_at_finalize')},
     'display_policy':'beta decimals are rounded downward and rho decimals upward. H, lambda and widths labelled approximate are descriptive; exact rationals are retained.',
     'physical_consumer_admission':False,'old_science_replays':0}
(P/'raw/SAVED_RESULT_SUMMARY.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'postprocess':'complete','source_blocks':len(blocks),'primary_cases':primary['case_count'],'reference_cases':ref['case_count'],'new_solver_runs':0}))
