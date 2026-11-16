#!/usr/bin/env python3
"""Independent symbolic calculation; diagnostic reduction, not cosmology."""
import json
from pathlib import Path
import sympy as s
N,S,k,h=s.symbols('N S k h',nonnegative=True)
B=lambda n,dt:(n+S*dt)/(1+k*dt)
d=s.factor(B(N,h)-B(B(N,h/2),h/2))
assert s.simplify(d-h*h*k*(N*k-S)/((h*k+1)*(h*k+2)**2))==0
assert d.subs(k,0)==0 and d.subs({S:0,N:0})==0
out={'status':'SYMBOLICALLY_CHECKED','backend':'SymPy '+s.__version__,'equation':'dN/dt=S-kappa*N; frozen source and opacity',
     'exact_defect':str(d),'zero_photon_IC':str(s.factor(d.subs(N,0))),'series':str(s.series(d,h,0,3)),
     'scope':'diagnostic reduction only, not the coupled AXBI solver and not an evolution error bound',
     'original_DAG':'10/17','expansion_DAG':'28/88'}
Path(__file__).resolve().parents[1].joinpath('SCALAR_DEFECT_CHECK.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
