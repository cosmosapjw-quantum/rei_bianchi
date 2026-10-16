"""Independent exact SymPy check; no Wolfram result is asserted."""
import json
import sys
import sympy as s
K=s.Matrix([[2,1],[1,5]])
V=s.Matrix([[1],[0]])
u=s.Matrix([s.Rational(3,5),s.Rational(4,5)])
z=3+s.I; eta=s.Integer(1);J=(V.T*K*V); e1=s.Matrix([1])
t=(z*s.eye(1)-J).inv()*e1
E=K*V-V*J; d=u-V*e1
residual=d+E*t
identity=residual-(u-(z*s.eye(2)-K)*V*t)
assert identity.applyfunc(s.simplify)==s.zeros(2,1)
reference=(u.T*(z*s.eye(2)-K).inv()*u)[0]
compressed=t[0]
delta=((u.T*V-e1.T)*t)[0]
abs2=lambda x:s.simplify(s.conjugate(x)*x)
norm2=lambda x:s.simplify((s.conjugate(x).T*x)[0])
B=s.sqrt(norm2(u))*s.sqrt(norm2(residual))/eta+s.sqrt(abs2(delta))
error2=abs2(reference-compressed)
slack=s.simplify(B**2-error2)
assert slack.is_positive is True
# Algebraic scalar identity including the coordinate correction.
R=(z*s.eye(2)-K).inv()
assert s.simplify(reference-compressed-(u.T*R*residual)[0]-delta)==0
print(json.dumps({'tool':'SymPy independent exact rational check','sympy_version':s.__version__,
    'wolfram_status':'NOT_PASS; two MCP -32603 attempts recorded separately',
    'residual_identity_exact':True,'scalar_error_identity_exact':True,'bound_squared_slack_positive':True,
    'reference':str(reference),'compressed':str(compressed),'bound':str(s.simplify(B)),
    'squared_error':str(error2),'squared_bound_minus_squared_error':str(slack)},indent=2))
