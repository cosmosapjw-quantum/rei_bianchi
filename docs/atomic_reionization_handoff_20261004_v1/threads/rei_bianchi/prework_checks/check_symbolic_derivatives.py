"""Symbolic prework only: thermal rate derivatives and event identity."""
from pathlib import Path
import json
import sympy as s

T,A,B=s.symbols('T A B', positive=True)
beta=A*s.sqrt(T)*s.exp(-B/T)
first=beta*(s.Rational(1,2)/T+B/T**2)
second=beta*((s.Rational(1,2)/T+B/T**2)**2-s.Rational(1,2)/T**2-2*B/T**3)
assert s.simplify(s.diff(beta,T)-first)==0
assert s.simplify(s.diff(beta,T,2)-second)==0
theta=s.symbols('theta',real=True)
assert s.simplify(s.diff(beta.subs(T,s.exp(theta)),theta,2)-(T**2*second+T*first).subs(T,s.exp(theta)))==0
I,R,x0,dt,psi=s.symbols('I R x0 dt psi')
k=I+R;Jx=I/k*dt+(x0-I/k)*psi
assert s.simplify(I*(dt-Jx)-R*Jx-(I-k*x0)*psi)==0
out={'status':'SYMBOLIC_IDENTITIES_CHECKED','sympy_version':s.__version__,
 'checks':['beta_first_derivative','beta_second_derivative','logT_chain_second_derivative','integrated_hydrogen_event_balance'],
 'assumptions':['T>0','k!=0 for event expression; k=0 explicit separate branch'],
 'not_claimed':['uniform interval derivative enclosure','atomic fit validity','real solver nonlinear remainder']}
Path(__file__).with_name('SYMBOLIC_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print('SYMBOLIC_IDENTITIES_CHECKED: 4')
