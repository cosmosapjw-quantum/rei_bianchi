#!/usr/bin/env python3
"""Exact symbolic checks for the bounded evaluation-site stage."""
from __future__ import annotations
import json
from pathlib import Path
import sympy as sp

HERE=Path(__file__).resolve().parent;STAGE=HERE.parent
A11,A12,A21,A22,z1,z2,dA11,dA12,dA21,dA22,db1,db2=sp.symbols(
    'A11 A12 A21 A22 z1 z2 dA11 dA12 dA21 dA22 db1 db2')
A=sp.Matrix([[A11,A12],[A21,A22]])
z=sp.Matrix([z1,z2]);dA=sp.Matrix([[dA11,dA12],[dA21,dA22]]);db=sp.Matrix([db1,db2])
dz=A.inv()*(db-dA*z)
implicit_residual=sp.simplify(A*dz+dA*z-db)

x,C,U0,w=sp.symbols('x C U0 w', real=True)
R=sp.Function('R')
root=C*sp.exp(x)-U0-w*R(x)
root_derivative_residual=sp.simplify(sp.diff(root,x)-(C*sp.exp(x)-w*sp.diff(R(x),x)))

h1,h2,h3,H=sp.symbols('h1 h2 h3 H', nonzero=True)
dh1,dh2,dh3=sp.symbols('dh1 dh2 dh3')
hs=(h1,h2,h3);dhs=(dh1,dh2,dh3);Hexpr=sum(hs);dH=sum(dhs)
dq=[sp.simplify(dh/Hexpr-h/Hexpr*dH/Hexpr) for h,dh in zip(hs,dhs)]
owner_sum_residual=sp.simplify(sum(dq))

# Stoichiometric tangent-space identities for H and He blocks.
a,b,c,d,e=sp.symbols('a b c d e')
h_transfer=sp.Matrix([-a,a,0,0,0])
he_transfer=sp.Matrix([0,0,-b+c,b-c-d+e,d-e])
cH=sp.Matrix([[1,1,0,0,0]]);cHe=sp.Matrix([[0,0,1,1,1]])
h_invariant=sp.simplify((cH*h_transfer)[0]);he_invariant=sp.simplify((cHe*he_transfer)[0])

result={
 'classification':'EXACT_SYMBOLIC_LOCAL_CERTIFICATE_IDENTITIES',
 'implicit_tangent_residual':[sp.sstr(v) for v in implicit_residual],
 'root_derivative_residual':sp.sstr(root_derivative_residual),
 'owner_normalization_derivative_sum_residual':sp.sstr(owner_sum_residual),
 'hydrogen_tangent_invariant_residual':sp.sstr(h_invariant),
 'helium_tangent_invariant_residual':sp.sstr(he_invariant),
 'pass':bool(implicit_residual==sp.zeros(2,1) and root_derivative_residual==0 and owner_sum_residual==0 and h_invariant==0 and he_invariant==0),
 'claim_boundary':'Exact algebra validates tangent and invariant identities only; it does not bound the four-site nonlinear remainder.',
}
(STAGE/'data/EXACT_SYMBOLIC_VALIDATION.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['pass'] else 1)
