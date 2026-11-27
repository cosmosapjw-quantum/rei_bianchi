"""Symbolic commutator check independent algebraic library, same author."""
import json
import sympy as s
p,y1,y2,k1,k2,l1,l2=s.symbols('p y1 y2 k1 k2 l1 l2')
x=s.Matrix([p,y1,y2])
FA=s.Matrix([-p*(k1*y1+k2*y2),-p*k1*y1,-p*k2*y2])
FB=s.Matrix([-p*(l1*y1+l2*y2),-p*l1*y1,-p*l2*y2])
comm=(FA.jacobian(x)*FB-FB.jacobian(x)*FA).applyfunc(s.factor)
wanted=s.Matrix([0,p*y1*y2*(k1*l2-k2*l1),-p*y1*y2*(k1*l2-k2*l1)])
assert comm==wanted,(comm,wanted)
assert s.simplify(sum(comm))==0
assert s.simplify(comm.subs({l1:s.Symbol('c')*k1,l2:s.Symbol('c')*k2}))==s.zeros(3,1)
result={'sympy':s.__version__,'commutator':[str(x) for x in comm],
        'total_extent_second_order_bracket':'ZERO','same_composition_or_proportional_rates':'COMMUTES','status':'PASS_DERIVED_SYMBOLIC_SAME_AUTHOR'}
print(json.dumps(result,indent=2))
