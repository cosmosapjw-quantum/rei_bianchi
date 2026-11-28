"""Mixed-response contracts and an EXACT SYNTHETIC isothermal BE family.

The toy has two coordinates (x,P), q=k(1-x)^2, no H/He thermal model.
Its certificates cannot be imported as native ENERGY06E certificates.
No native solver, scientific dispatch, calibration or tolerance fitting occurs.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
import hashlib,json
from pathlib import Path

class Unresolved(ValueError):pass
@dataclass(frozen=True)
class Box:
 lo:Q
 hi:Q
 def __post_init__(self):
  if type(self.lo)is not Q or type(self.hi)is not Q or self.lo>self.hi:raise Unresolved('NUMERICAL:EXACT_RATIONAL_BOX_REQUIRED')
 def __add__(a,b):
  b=asbox(b);return Box(a.lo+b.lo,a.hi+b.hi)
 __radd__=__add__
 def __neg__(a):return Box(-a.hi,-a.lo)
 def __sub__(a,b):return a+-asbox(b)
 def __rsub__(a,b):return asbox(b)+-a
 def __mul__(a,b):
  b=asbox(b);v=[a.lo*b.lo,a.lo*b.hi,a.hi*b.lo,a.hi*b.hi];return Box(min(v),max(v))
 __rmul__=__mul__
 def inverse(a):
  if a.lo<=0<=a.hi:raise Unresolved('MATHEMATICAL:ZERO_DENOMINATOR')
  return Box(1/a.hi,1/a.lo)
 def __truediv__(a,b):return a*asbox(b).inverse()
 def mid(a):return (a.lo+a.hi)/2
 def contains(a,b):return a.lo<=b.lo<=b.hi<=a.hi
 def maxabs(a):return max(abs(a.lo),abs(a.hi))
def asbox(x):
 if isinstance(x,Box):return x
 if type(x)is not Q and type(x)is not int:raise Unresolved('NUMERICAL:FLOAT_INPUT_REFUSED')
 return Box(Q(x),Q(x))
Z=asbox(0);ONE=asbox(1)
@dataclass(frozen=True)
class Jet:
 value:Box
 gradient:tuple
 hessian:tuple
 @staticmethod
 def constant(v):return Jet(asbox(v),(Z,)*3,((Z,)*3,)*3)
 @staticmethod
 def variable(v,i):
  g=list((Z,)*3);g[i]=ONE;return Jet(asbox(v),tuple(g),((Z,)*3,)*3)
 def __add__(a,b):
  b=asjet(b);return Jet(a.value+b.value,tuple(a.gradient[i]+b.gradient[i]for i in range(3)),tuple(tuple(a.hessian[i][j]+b.hessian[i][j]for j in range(3))for i in range(3)))
 __radd__=__add__
 def __neg__(a):return Jet(-a.value,tuple(-x for x in a.gradient),tuple(tuple(-x for x in row)for row in a.hessian))
 def __sub__(a,b):return a+-asjet(b)
 def __rsub__(a,b):return asjet(b)+-a
 def __mul__(a,b):
  b=asjet(b);return Jet(a.value*b.value,tuple(a.gradient[i]*b.value+a.value*b.gradient[i]for i in range(3)),tuple(tuple(a.hessian[i][j]*b.value+a.gradient[i]*b.gradient[j]+a.gradient[j]*b.gradient[i]+a.value*b.hessian[i][j]for j in range(3))for i in range(3)))
 __rmul__=__mul__
 def inverse(a):
  r=a.value.inverse();return Jet(r,tuple(-r*r*g for g in a.gradient),tuple(tuple(2*r*r*r*a.gradient[i]*a.gradient[j]-r*r*a.hessian[i][j]for j in range(3))for i in range(3)))
 def __truediv__(a,b):return a*asjet(b).inverse()
def asjet(x):return x if isinstance(x,Jet)else Jet.constant(x)
@dataclass(frozen=True)
class ToyState:
 x:Jet
 photons:Jet
@dataclass(frozen=True)
class ToyModel:
 A:Q=Q(1)
 k:Q=Q(1,10)
 def validate(self):
  if type(self.A)is not Q or type(self.k)is not Q or self.A<=0 or self.k<=0:raise Unresolved('MODEL:SYNTHETIC_POSITIVE_CONSTANTS_REQUIRED')

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()
def residual(x,old,lam,source,h,m):
 # Source is future birth ONLY. All previous photons and sensitivities survive.
 n=old.photons+h*source;u=1-x;den=1+h*m.A*u
 return x-old.x-h*(m.A*u*n/den+lam*m.k*u*u)
def full_chain_M(x,photons,lam,h,m):
 # d/dx of eliminated photon term includes dP/dx: M>=1 exactly.
 u=1-x;den=1+h*m.A*u
 return 1+h*m.A*photons/(den*den)+2*h*lam*m.k*u

def synthetic_stage_family(old,lam_box,source_box,h,m=ToyModel()):
 m.validate()
 if type(h)is not Q or not 0<h<=Q(1,16) or not (0<=old.x.value.lo<=old.x.value.hi<1) or old.photons.value.lo<0 or lam_box.lo<0 or source_box.lo<0:
  raise Unresolved('MODEL:BOUNDED_SYNTHETIC_DOMAIN_ONLY')
 lam=Jet.variable(lam_box,1);source=Jet.variable(source_box,2);domain=Box(Q(0),Q(1));centre=Q(1,2)
 n=old.photons.value+h*source_box
 matrix=full_chain_M(domain,n,lam_box,h,m)
 # Fixed rational inverse at one predeclared centre. Never tuned to a sign/scale.
 c=1/full_chain_M(asbox(centre),asbox(n.mid()),asbox(lam_box.mid()),h,m).lo
 b=1-c*matrix;q=b.maxabs();f0=residual(Jet.constant(centre),old,lam,source,h,m).value
 image=centre-c*f0+b*(domain-centre)
 if not q<1 or not domain.lo<image.lo<=image.hi<domain.hi:raise Unresolved('MATHEMATICAL:SYNTHETIC_STRICT_TUBE_NOT_CLOSED')
 x=Jet.variable(image,0);r=residual(x,old,lam,source,h,m)
 # The algebraic closed form is tighter than a dependency-expanded Jet interval.
 # It is the SAME full chain derivative, not a new Jacobian model.
 M=full_chain_M(image,n,lam_box,h,m)
 grad=[Z]*3
 for a in [1,2]:grad[a]=-r.gradient[a]/M
 hes=[[Z]*3 for _ in range(3)]
 for a in [1,2]:
  for bindex in [1,2]:hes[a][bindex]=-(r.hessian[a][bindex]+r.hessian[0][a]*grad[bindex]+r.hessian[0][bindex]*grad[a]+r.hessian[0][0]*grad[a]*grad[bindex])/M
 xout=Jet(image,tuple(grad),tuple(tuple(row)for row in hes))
 pout=(old.photons+h*source)/(1+h*m.A*(1-xout))
 binding={'kind':'SYNTHETIC_ISOTHERMAL_ONLY','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'model':str(m),'old_x':str(old.x),'old_photons':str(old.photons),'lambda':str(lam_box),'source':str(source_box),'h':str(h),'fixed_C':str(c),'full_chain_M':str(M),'root_box':str(domain),'image':str(image),'scaled_contraction':str(q),'native_trusted':False}
 binding['certificate_sha256']=digest(binding)
 return ToyState(xout,pout),binding

def synthetic_family(initial,lam_box,source_box,h,scheme):
 if scheme not in ('full','twohalf'):raise Unresolved('MODEL:UNKNOWN_SCHEME')
 state=initial;certs=[]
 for step in ([h]if scheme=='full'else[h/2,h/2]):
  state,cert=synthetic_stage_family(state,lam_box,source_box,step);certs.append(cert)
 mixed=lam_box.hi*source_box.hi*state.x.hessian[1][2]
 if lam_box.lo!=0 or source_box.lo!=0:raise Unresolved('MODEL:RECTANGLE_MUST_START_AT_ZERO')
 return {'state':state,'mixed_interval':mixed,'certificates':certs,'native_certified':False,'interpretation':'I=L*S integral_0^1 integral_0^1 x_lambdaS(aL,bS) da db; synthetic whole discrete root family only'}

@dataclass(frozen=True)
class CornerIdentity:
 initial_state_sha256:str
 theta_sha256:str
 source_law_sha256:str
 birth_measure_sha256:str
 clock:Q
 duration:Q
 lam:Q
 source:Q
 scheme:str

def validate_four_corners(corners):
 if set(corners)!={'LS','L0','0S','00'}:raise Unresolved('IDENTITY:FOUR_CORNERS_REQUIRED')
 anchor=corners['LS'];L=anchor.lam;S=anchor.source
 if type(L)is not Q or type(S)is not Q or L<=0 or S<=0:raise Unresolved('IDENTITY:POSITIVE_EXACT_L_S_REQUIRED')
 fields=['initial_state_sha256','theta_sha256','source_law_sha256','birth_measure_sha256','clock','duration','scheme']
 for label,expected in {'LS':(L,S),'L0':(L,Q(0)),'0S':(Q(0),S),'00':(Q(0),Q(0))}.items():
  c=corners[label]
  if any(getattr(c,k)!=getattr(anchor,k)for k in fields)or(c.lam,c.source)!=expected:raise Unresolved('IDENTITY:CORNER_STATE_THETA_LAW_MEASURE_CLOCK_MISMATCH')
  if c.scheme not in ('full','twohalf')or type(c.clock)is not Q or type(c.duration)is not Q or c.duration<=0:raise Unresolved('IDENTITY:SCHEME_CLOCK_DOMAIN')
  for k in fields[:4]:
   v=getattr(c,k)
   if type(v)is not str or len(v)!=64 or any(ch not in '0123456789abcdef'for ch in v):raise Unresolved('IDENTITY:SHA256_REQUIRED')
 return True

def native_mixed_response(corners,certificate=None,authorization=None):
 validate_four_corners(corners)
 # ENERGY06E actual native family producer is absent; an arbitrary JSON claim
 # cannot replace the trusted exporter or exact human authorization.
 if authorization is None:raise Unresolved('AUTHORIZATION:EXACT_NEW_NATIVE_SCOPE_MISSING')
 raise Unresolved('NUMERICAL:TRUSTED_NATIVE_ROOT_PRECONDITIONER_FAMILY_MISSING')

def correlated_polynomial_difference(coefficients,L,S):
 """Synthetic exact shared Taylor polynomial; same coefficient noise cancels.
 Coefficients (lambda power,S power) are rational enclosures. No native proof.
 """
 if type(L)is not Q or type(S)is not Q:raise Unresolved('NUMERICAL:EXACT_PARAMETERS_REQUIRED')
 out=Z
 for (a,b),coef in coefficients.items():
  if type(a)is not int or type(b)is not int or a<0 or b<0:raise Unresolved('MODEL:NONNEGATIVE_INTEGER_POWERS_REQUIRED')
  if a and b:out+=coef*(L**a)*(S**b)
 return out
