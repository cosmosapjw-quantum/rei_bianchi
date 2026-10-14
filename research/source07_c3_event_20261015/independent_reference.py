"""Independent SciPy DOP853 reference for frozen HeII cutoff crossing.

This directly solves N'(t)=-lambda(E(t))N, and Q'(t)=
lambda(E(t))N(E(t)-I_HeII) along E(t)=E0 exp(-H t).
No runtime coupling to Rust's midpoint integrator is used.
"""
import csv, json, math, pathlib
from scipy.integrate import solve_ivp

E0 = 54.9
CHI_FIT = 54.42
BIND = 54.41776
H = 1e-16
DURATION = 1e15
C_CM_S = 29979245800.0
DENSITY = 1e-10
CROSS = CHI_FIT
def verner_heii(E):
    if E < CHI_FIT:
        return 0.0
    e0,sigma0,ya,p,yw,y0,y1=(1.720,1.369e4,32.88,2.963,0.,0.,0.)
    x=E/e0-y0
    y=math.hypot(x,y1)
    return sigma0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+math.sqrt(y/ya))**(-p)*1e-18

t_cross=math.log(E0/CHI_FIT)/H
def derivatives(x,vector):
    t=x*t_cross
    energy=E0*math.exp(-H*t)
    lam=DENSITY*C_CM_S*verner_heii(energy)
    n,a,heat=vector
    rate=t_cross*lam*n
    return [-rate,rate,rate*(energy-BIND)]

sol=solve_ivp(derivatives,(0.0,1.0),[1.0,0.0,0.0],method='DOP853',
              atol=1e-16,rtol=5e-13)
assert sol.success
n,a,q=(float(x) for x in sol.y[:,-1])
target={
  'setup':{'E_emit_eV':E0,'H_per_s':H,'T_s':DURATION,'threshold_eV':CHI_FIT,
           'binding_eV':BIND,'nHeII_proper_cm3':DENSITY},
  'crossing_time_s':t_cross,
  'independent_scipy_reference':{'absorbed_per_H':a,'heat_eV_per_H':q,
    'final_survival_photons_per_H':n},
  'solver':{'method':'DOP853','nfev':sol.nfev,'rtol':5e-13,'atol':1e-16}
}
input_path=pathlib.Path(__file__).parent/'evidence/BENCH_C3.csv'
rows=[]
for line in input_path.read_text().splitlines():
    if not line.startswith('REFINE,'):continue
    _,s,absorbed,heat,work=line.split(',')
    row={'slices':int(s),'absorbed_per_H':float(absorbed),
         'heat_eV_per_H':float(heat),
         'difference_vs_scipy_photons_per_H':float(absorbed)-a,
         'difference_vs_scipy_heat_eV_per_H':float(heat)-q}
    rows.append(row)
assert len(rows)==8
assert abs(rows[-1]['difference_vs_scipy_photons_per_H'])<1e-9
assert abs(rows[-1]['difference_vs_scipy_heat_eV_per_H'])<1e-6
target['rust_refinement_comparison']=rows
out=pathlib.Path(__file__).parent/'evidence/INDEPENDENT_SCIPY.json'
out.write_text(json.dumps(target,indent=2))
print(json.dumps({'reference':target['independent_scipy_reference'],
                  'rust_last':rows[-1],'crossing_s':t_cross},indent=2))
