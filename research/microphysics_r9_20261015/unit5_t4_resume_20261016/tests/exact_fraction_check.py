"""Independent exact arithmetic sample; stdlib fallback when SymPy is absent."""
from fractions import Fraction as F
import json

class Q:
    def __init__(self,a=0,b=0):self.a,self.b=F(a),F(b)
    def __add__(self,o):
        if not isinstance(o,Q):o=Q(o)
        return Q(self.a+o.a,self.b+o.b)
    __radd__=__add__
    def __neg__(self):return Q(-self.a,-self.b)
    def __sub__(self,o):return self+-o if isinstance(o,Q) else self+Q(-o)
    def __rsub__(self,o):return -self+o
    def __mul__(self,o):
        if not isinstance(o,Q):o=Q(o)
        return Q(self.a*o.a-self.b*o.b,self.a*o.b+self.b*o.a)
    __rmul__=__mul__
    def __truediv__(self,o):
        if not isinstance(o,Q):o=Q(o)
        n=o.abs2();return self*Q(o.a/n,-o.b/n)
    def __eq__(self,o):
        if not isinstance(o,Q):o=Q(o)
        return self.a==o.a and self.b==o.b
    def abs2(self):return self.a*self.a+self.b*self.b
    def show(self):return {'real':str(self.a),'imaginary':str(self.b)}

z=Q(3,1);u=[Q(F(3,5)),Q(F(4,5))]
t=Q(1)/(z-2);d=[u[0]-1,u[1]];E=[Q(0),Q(1)]
r=[d[j]+E[j]*t for j in range(2)]
# Direct u-(zI-K)Vt for K=[[2,1],[1,5]], V=e1, J=2.
assert r==[u[0]-(z-2)*t,u[1]+t]
det=(z-2)*(z-5)-1
R=lambda x:[((z-5)*x[0]+x[1])/det,(x[0]+(z-2)*x[1])/det]
ref=sum((u[j]*R(u)[j] for j in range(2)),Q())
delta=(u[0]-1)*t
assert ref-t==sum((u[j]*R(r)[j] for j in range(2)),Q())+delta
r2=sum(x.abs2() for x in r);delta2=delta.abs2();error2=(ref-t).abs2()
# eta=||u||=1; B=sqrt(r2)+sqrt(delta2), so B^2>=r2+delta2.
assert sum(x.abs2() for x in u)==1
assert error2 <= r2+delta2
print(json.dumps({'tool':'Python fractions.Fraction; exact rational complex arithmetic',
  'sympy':'UNAVAILABLE in default and primary runtimes; see raw stderr',
  'wolfram':'NOT_PASS; actual MCP failures retained elsewhere',
  'residual_identity_exact':True,'scalar_error_identity_exact':True,
  'bound_check':'error^2 <= residual_norm^2 + abs(delta)^2 <= B^2; eta=norm(u)=1',
  'reference':ref.show(),'compressed':t.show(),'squared_error':str(error2),
  'residual_norm_squared':str(r2),'coordinate_delta_squared':str(delta2),
  'rational_lower_bound_on_B_squared':str(r2+delta2),'pass':True},indent=2))
