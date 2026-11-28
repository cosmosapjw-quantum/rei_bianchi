#!/usr/bin/env python3
"""Exact symbolic/rational spot checks for the subspace-witness theorem.

Fallback used because the explicitly requested Wolfram connector returned an
internal tool error in this loop. This script does not replace Wolfram; it
provides durable exact algebra for the research checkpoint.
"""
import json
import sympy as sp

q1,q2,o11,o12,o22,r11,r12,r22 = sp.symbols('q1 q2 o11 o12 o22 r11 r12 r22', real=True)
O=sp.Matrix([[o11,o12],[o12,o22]])
R=sp.Matrix([[r11,r12],[r12,r22]])
q=sp.Matrix([q1,q2])
num=(q.T*R*q)[0]
den=(q.T*O*q)[0]
y=sp.symbols('y', nonzero=True, real=True)
x=q*y
ambient=sp.cancel((x.T*R*x)[0]/(x.T*O*x)[0])
reduced=sp.cancel((y**2*num)/(y**2*den))
identity=sp.simplify(ambient-reduced)==0

O2=sp.eye(2);R2=sp.diag(1,-1);Q2=sp.Matrix([1,1])/sp.sqrt(2)
redR=(Q2.T*R2*Q2)[0];redO=(Q2.T*O2*Q2)[0]

R3=sp.diag(-2,1,3);O3=sp.eye(3)
Q3=sp.Matrix([[1/sp.sqrt(2),0],[1/sp.sqrt(2),0],[0,1]])
redR3=sp.simplify(Q3.T*R3*Q3)
fullvals=[sp.Rational(-2),sp.Rational(1),sp.Rational(3)]
redvals=sorted(list(redR3.eigenvals().keys()), key=lambda z: float(z))
interlace=(fullvals[0] <= redvals[0] <= fullvals[1] and fullvals[1] <= redvals[1] <= fullvals[2])

result={
  'schema':'WU088_R31X_EXACT_FALLBACK_V1',
  'rayleigh_lift_identity':bool(identity),
  'pass_asymmetry_reduced_quotient':str(sp.simplify(redR/redO)),
  'pass_asymmetry_full_eigenvalues':[str(v) for v in R2.eigenvals().keys()],
  'interlacing_full':[str(v) for v in fullvals],
  'interlacing_reduced':[str(v) for v in redvals],
  'interlacing_example_pass':bool(interlace),
  'method':'SymPy exact algebra/rational matrices; Wolfram connector failed internally this loop',
}
print(json.dumps(result,indent=2))
