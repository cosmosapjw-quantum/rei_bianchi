"""New local derivative check only: imports frozen PR198, never integrates an IVP."""
from pathlib import Path
import hashlib, importlib.util, json, math, sys
import numpy as np

source = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(source / 'matter_radiation_20261021'))
import component_pilot as cp

model = cp.ComponentReduced()
y, initial = model.initial(0.0, 4e-4, -4e-4)
mom = model.momentum
q = mom._q
E = np.hypot(mom.mass, q)
v2 = q*q/(E*E)
pressure_weight = mom._numbers*q*q/E
B = float(np.sum(pressure_weight*v2)/np.sum(pressure_weight))
pm0 = mom.moments(0.0, 0.0).pi_s
analytic = -(1-B)*initial['realized']['signed_Pi_m0']

def S_prime_frozen(x):
    d = model.diagnostics(np.array([x]), y[:, None])
    rhs = model.rhs(x, y)
    return math.sqrt(3)*model.src.href/float(d['H_per_s'][0])*float(rhs[2])

checks=[]
for h in (1e-3,1e-4,1e-5):
    # 4th-order forward derivative valid within the model's x>=0 chart.
    c=(-25.,48.,-36.,16.,-3.)
    num=sum(c[k]*S_prime_frozen(k*h) for k in range(5))/(12*h)
    dpm=sum(c[k]*mom.moments(k*h,0.).pi_s for k in range(5))/(12*h)
    checks.append({'h':h,'S_second_numerical':num,'relative_error':abs(num-analytic)/abs(analytic),'matter_log_derivative':dpm/pm0,'matter_log_derivative_exact':-5+B})
out={'scope':'new initial cancellation-curvature identity; zero IVP solves',
     'mass_Tref':mom.mass,'cells':[mom.radial_cells,mom.angular_cells],'gauss':mom.gauss_order,
     'A_m':initial['A_m'],'k_r':initial['k'],'B_pressure_weighted_v2_over_c2':B,
     'initial':initial,'S_second_analytic':analytic,'checks':checks,
     'source_files':{str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source/'pilot.py',source/'vendor/canonical_fv.py',source/'vendor/lrs_boltzmann.py',source/'matter_radiation_20261021/component_pilot.py']}}
assert 0<B<1
assert min(c['relative_error'] for c in checks)<1e-7
out['status']='PASS_SCOPED_LOCAL_DERIVATIVE_NO_IVP'
print(json.dumps(out,indent=2))
