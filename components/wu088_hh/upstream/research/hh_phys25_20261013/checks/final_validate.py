"""Independent formulas and exact certificate-closure checks for PHYS25.
No previous ODE campaign or producer interval pass is re-executed.
"""
from pathlib import Path
from fractions import Fraction as F
import sys,json,hashlib,platform,math,time
import mpmath
from mpmath import mp,iv
D=Path(__file__).resolve().parents[1];sys.path.insert(0,str(D/'src'))
import sheldon_model as M
mp.dps=65;iv.dps=50
checks=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail})
 if not ok: raise AssertionError(name)
def close(name,a,b,tol='1e-50'):
 rel=abs(a-b)/max(mp.mpf('1e-100'),abs(a),abs(b));check(name,rel<mp.mpf(tol),mp.nstr(rel,8))
def mfrac(x):
 q=F(x);return mp.mpf(q.numerator)/q.denominator
start=time.monotonic()
# Direct integrations are independent of the producer closed primitives.
for spin in ['singlet','triplet']:
 for e in map(mp.mpf,['1','1.1','1.5','2']):
  r0=M.turning(e,spin)
  g=mp.quad(lambda r:r*M.screened(r)**2*(1-M.potential(r,spin)/e-r*M.potential_prime(r,spin)/(2*e)),[r0,1,2,5,mp.inf])
  close(f'g_direct_{spin}_{e}',g,M.gfun(e,spin))
  close(f'gprime_direct_derivative_{spin}_{e}',mp.diff(lambda t:M.gfun(t,spin),e),M.gprime(e,spin))
  close(f'turning_{spin}_{e}',M.potential(r0,spin),e)
 for mode in ['source','restored']:
  close(f'threshold_closed_vs_integral_{spin}_{mode}',M.threshold_g_closed(spin,mode),M.threshold_g(spin,mode))
for r in map(mp.mpf,['.4','.5','1','2','5']):
 close(f'C0_radial_vs_closed_{r}',M.c0_radial(r),M.c0_closed(r))
for e in map(mp.mpf,['1.001','1.01','1.1','1.5','2']):
 close(f'phase_direct_{e}',mp.quad(lambda t:t*t/(1+t*t)**6,[0,mp.sqrt(e-1)]),M.phase(e))
for x in map(mp.mpf,['.5','1','2','4','8']):
 a,b=M.endpoints(M.e1_interval(iv.mpf(str(x))));check(f'E1_interval_{x}',mfrac(a)<=mp.e1(x)<=mfrac(b))
for spin in ['singlet','triplet']:
 for e in map(mp.mpf,['1','1.4','2']):
  q=mp.mpf('1e-16');r0=M.turning(e,spin)
  vals=[1-M.potential(r0+t,spin)/e-(r0+t)*M.potential_prime(r0+t,spin)/(2*e) for t in map(mp.mpf,['0','.1','1','5','50'])]
  check(f'J_positive_samples_{spin}_{e}',min(vals)>0)
# These negative controls enforce the declared source window and state types.
for val in ['2.0001','3']:
 try:M.sigma_tag_a02(val);ok=False
 except ValueError:ok=True
 check('source_window_refusal_'+val,ok)
check('below_threshold_zero',M.sigma_tag_a02('.99')==0)
check('threshold_zero',M.sigma_tag_a02('1')==0)
try:M.potential(mp.mpf(1),'bad');ok=False
except ValueError:ok=True
check('spin_refusal',ok)
# Exact rational audit of the stored interval result; do not rerun the producer.
audit=json.loads((D/'results/PARTIAL_RATE_INTERVAL.json').read_text())
print('INTERVAL_KEYS',list(audit))
# filled below after schema inspection
(D/'checks/VALIDATION_BASE.json').write_text(json.dumps({'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),'checks':checks,'seconds':time.monotonic()-start,'python':platform.python_version(),'mpmath':mpmath.__version__,'independence':'same assistant; direct quadrature and derivatives vs closed producer; no external reviewer'},indent=2)+'\n')
print('BASE_CHECKS',len(checks),'seconds',time.monotonic()-start)
