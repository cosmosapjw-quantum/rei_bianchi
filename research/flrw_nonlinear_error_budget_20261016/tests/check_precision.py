"""C8 fixed small precision/conditioning cases; not a benchmark or native run."""
import json
import math
import platform
import time
from test_implementation import packet,subject


wall,cpu=time.perf_counter(),time.process_time()
epsilon=2.0**-40
j=[[1,1,0,0],[1,1+epsilon,0,0],[0,0,1,0],[0,0,0,1]]
near=subject.solve_scaled([0,epsilon,0,0],j,[1]*4,[1]*4)
assert near['status']=='LINEAR_SYSTEM_DIAGNOSTIC'
assert near['metrics']['delta']==[1,-1,0,0]
assert near['metrics']['kappa_inf']>1e12
# Consistently rescale an otherwise identical small linear system.
factor=2.0**-100
scaled=subject.solve_scaled([0,epsilon*factor,0,0],
    [[x*factor for x in row] for row in j],[1]*4,[1]*4)
assert scaled['status']=='LINEAR_SYSTEM_DIAGNOSTIC'
assert scaled['metrics']['delta']==near['metrics']['delta']
assert math.isclose(scaled['metrics']['kappa_inf'],near['metrics']['kappa_inf'],rel_tol=1e-12,abs_tol=1e-14)
p=packet();p['old_state'][3]=10;p['residual'][3]=1e-12
cooling=subject.analyze_stage(p)
assert cooling['status']=='SYNTHETIC_LINEARIZED_DIAGNOSTIC'
m=cooling['metrics']
assert m['residual_scales'][3]==10 and m['state_scales'][3]==.001
assert m['residual_scales'][3]/m['state_scales'][3]==10000
assert math.isclose(m['native_scaled_residual_inf'],1e-13,rel_tol=1e-12)
assert math.isclose(m['scaled_correction_inf'],1e-9,rel_tol=1e-12)
print(json.dumps(dict(status='PASS_SCOPED',scope='FIXED_SMALL_SYNTHETIC_PRECISION_ONLY',
    near_singular=near,consistent_matrix_rescaling=scaled,unequal_old_current_energy=cooling,
    python=platform.python_version(),wall_seconds=time.perf_counter()-wall,cpu_seconds=time.process_time()-cpu,
    native_builds=0,NCP_runs=0,native_solver_runs=0,oracle_reexecutions=0,physical_history_reads=0),indent=2,allow_nan=False))
