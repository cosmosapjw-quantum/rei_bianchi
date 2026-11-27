"""United-atom data and Coulomb-singular regular nuclear initial conditions.

Electronic limits use a0/Eh. Radial inputs use x=R/L, E0=hbar^2/(2*mu*L^2).
The radial routine solves a DECLARED LOCAL POLYNOMIAL, not the unknown physical
inner optical curve. Complex binary64 arithmetic is explicit; exact-rational
positive majorants only bound the infinite SERIES tail, not floating-point error.
"""
from __future__ import annotations
from fractions import Fraction
import math
import numbers
import numpy as np
from scipy.special import roots_jacobi

class ContractError(ValueError):pass
class NumericalFailure(RuntimeError):pass


def real(v,name,lo=None,hi=None):
 if isinstance(v,(bool,str,complex)) or not isinstance(v,numbers.Real):raise ContractError(name+' must be real scalar')
 x=float(v)
 if not math.isfinite(x) or (lo is not None and x<lo) or (hi is not None and x>hi):raise ContractError(name+' outside declared range')
 return x


def integer(v,name,lo,hi):
 if isinstance(v,bool) or not isinstance(v,(int,np.integer)) or not lo<=v<=hi:raise ContractError(name+' must be bounded integer')
 return int(v)


def ua_limit(*,branch):
 if branch!='2p_sigma_to_1s_sigma':raise ContractError('explicit continued 2p_sigma -> 1s_sigma branch required, not arbitrary n2')
 d=256/(729*math.sqrt(2));f=4/3*(27/8)**3*d*d
 return {'schema':'bass-he.b5c2.united-atom.v1','branch':branch,'Z_united':3,
  'E_lower_Eh':-4.5,'E_upper_Eh':-1.125,'gap_Eh':27/8,
  'dipole_abs_a0':d,'dipole_exact_a0':'256/(729*sqrt(2))',
  'A_ta_div_alpha3':f,'A_factor_exact':'256/81',
  'V_coulomb_coefficient':2,'V_regular_limit_Eh':-5/8,
  'n2_m0_degenerate_basis':['2s','2p_z'],'generic_n2_dipole':'c_p * 256/(729*sqrt(2)) a0',
  'model':'INFINITE_NUCLEAR_MASS_CLAMPED_COULOMB_ZA1_ZB2_M0',
  'limit_not_finite_radius_table':True,'inner_matching_radius':None,
  'rate_coefficient':None,'cross_section':None,'heat':None,'photon_spectrum':None,
  'physical_accuracy_certified':False}


def nuclear_scaling(*,mass_ratio,length_a0):
 m=real(mass_ratio,'mu/me',0);L=real(length_a0,'L/a0',0)
 if m==0 or L==0:raise ContractError('positive mass and length required')
 try:E=1/(2*m*L*L);a=4*m*L;v=-5/8/E
 except (OverflowError,ZeroDivisionError) as ex:raise NumericalFailure("nuclear scaling arithmetic range") from ex
 if not all(math.isfinite(x) and x!=0 for x in (E,a,v)):raise NumericalFailure('scaling range')
 return {'energy_scale_Eh':E,'coulomb_coefficient':a,'regular_UA_value':v,
  'mu_over_me':m,'length_a0':L,'exact_isotope_selected':False,
  'width_scale':'g0 = alpha^3*(256/81)/energy_scale_Eh',
  'finite_radius_validity_bound':None}


def _polynomial(v,name):
 if not isinstance(v,(tuple,list,np.ndarray)) or len(v)<1 or len(v)>7:raise ContractError(name+' requires 1..7 ascending power coefficients')
 return [real(x,name) for x in v]


def _csum(ts):
 ts=list(ts);return complex(math.fsum(x.real for x in ts),math.fsum(x.imag for x in ts))


def _fraction(x):return Fraction.from_float(float(x))


def _positive_width(g,h):
 """Sufficient, not necessary test: Bernstein coefficients on [0,h] >=0.
 Exact rationals represent the supplied binary64 numbers, not printed decimals.
 """
 deg=len(g)-1;G=[_fraction(v)*_fraction(h)**j for j,v in enumerate(g)]
 bern=[sum((G[j]*Fraction(math.comb(k,j),math.comb(deg,j)) for j in range(k+1)),Fraction(0)) for k in range(deg+1)]
 if min(bern)<0:raise ContractError('width nonnegativity not established by Bernstein test')
 return bern


def series_majorant(ell,coulomb,b,h,order):
 """Exact-rational coefficient majorants and all omitted coefficient sums.

 |Re b|+|Im b| avoids irrational modulus and provides a valid upper bound.
 If D=(N+1)(N+2l+2)>W=sum(weights), summing the tail recurrence gives
 sum_{n>N}|t_n| <= boundary/(D-W). Also sum n|t_n| <= (N+1)*bound.
 Bounds refer to exact recurrence for supplied polynomial inputs; binary64
 coefficient construction, evaluation, quadrature and model errors are separate.
 """
 H=_fraction(h)
 weights={1:_fraction(coulomb)*H}
 for j,x in enumerate(b):weights[j+2]=(_fraction(abs(x.real))+_fraction(abs(x.imag)))*H**(j+2)
 vals=[Fraction(1)]
 for n in range(1,order+1):
  vals.append(sum((v*vals[n-s] for s,v in weights.items() if s<=n),Fraction(0))/ (n*(n+2*ell+1)))
 W=sum(weights.values(),Fraction(0));D=Fraction((order+1)*(order+2*ell+2))
 if W>=D:raise NumericalFailure('series-tail contraction condition not satisfied; smaller radius or separately approved order required')
 boundary=sum((v*sum(vals[max(0,order+1-s):order+1],Fraction(0)) for s,v in weights.items()),Fraction(0))
 bound=boundary/(D-W)
 def up(x):
  if not x:return 0.
  y=float(x)
  if not math.isfinite(y):raise NumericalFailure('majorant range')
  # Include the exact rational in the returned real interval endpoint.
  return math.nextafter(y,math.inf) if _fraction(y)<x else y
 return up(bound),up((order+1)*bound)


def radial_seed(*,ell,coulomb,potential,width,energy,radius,order=96):
 """Regular solution on [0,h] normalized by u(h)=1.

 -u''+[ell(ell+1)/x^2+a/x+v(x)-i*g(x)/2]u=e*u.
 Returns u'/u and J=integral_0^h g*|u/u(h)|^2 dx. No arbitrary core cutoff.
 No density, cross section, asymptotic matching or true-curve replacement.
 """
 ell=integer(ell,'ell',0,64);N=integer(order,'order',16,192)
 a=real(coulomb,'coulomb',0,1e8);e=real(energy,'energy',-1e8,1e8);h=real(radius,'radius',1e-12,1.)
 v=_polynomial(potential,'potential');g=_polynomial(width,'width');_positive_width(g,h)
 degree=max(len(v),len(g));b=[complex(v[j] if j<len(v) else 0,-.5*g[j] if j<len(g) else 0) for j in range(degree)];b[0]-=e
 tail,dtail=series_majorant(ell,a,b,h,N)
 weights=[a*h]+[z*h**(j+2) for j,z in enumerate(b)]
 t=np.empty(N+1,dtype=complex);t[0]=1
 for n in range(1,N+1):
  t[n]=_csum(complex(w)*t[n-s] for s,w in enumerate(weights,start=1) if s<=n)/(n*(n+2*ell+1))
  if not math.isfinite(t[n].real) or not math.isfinite(t[n].imag):raise NumericalFailure('series coefficient range')
 P=_csum(t);DP=_csum(n*z for n,z in enumerate(t));mass=math.fsum(abs(z) for z in t)
 if P==0 or abs(P)<1e-10*mass:raise NumericalFailure('matching near a zero or excessive cancellation')
 if tail/abs(P)>1e-13 or dtail/max(abs(P)+abs(DP),1e-300)>1e-12:raise NumericalFailure('declared series order does not meet truncation criterion')
 L=((ell+1)+DP/P)/h
 nq=N+len(g)+1
 x,w=roots_jacobi(nq,0.,float(2*ell+2));q=(x+1)/2;w=w*2.**(-(2*ell+3))
 G=np.array([math.fsum(gj*(h*qi)**j for j,gj in enumerate(g)) for qi in q])
 if np.any(G<0) or not np.all(np.isfinite(G)):raise NumericalFailure('width evaluation failed positivity/range')
 Q=np.polynomial.polynomial.polyval(q,t)/P
 J=h*math.fsum(float(wi*gi*abs(pi)**2) for wi,gi,pi in zip(w,G,Q))
 if any(z>0 for z in g) and J==0:raise NumericalFailure('positive absorption underflow')
 if not math.isfinite(J) or J<0:raise NumericalFailure('inner flux evaluation range')
 out={'schema':'bass-he.b5c2.radial-seed.v1','ell':ell,'match_radius':h,
  'coulomb_coefficient':a,'potential_power_coefficients':v,'width_power_coefficients':g,'energy':e,
  'order':N,'log_derivative':{'real':L.real,'imag':L.imag},
  'inner_absorption':J,'absorption_normalization':'u(match)=1; J=int g |u/u(match)|^2 dx',
  'regular_origin_exponent':ell+1,'matching_amplitude':[1.,0.],
  'series_scaled_coefficients':[[float(z.real),float(z.imag)] for z in t],
  'series_tail_absolute_bound':tail,'series_derivative_tail_bound':dtail,
  'tail_bound_scope':'exact supplied local polynomial, before endpoint normalization; excludes floating-point error',
  'tail_uses_exact_rational_majorant':True,'coefficient_sum_condition':mass/abs(P),
  'width_nonnegative_proof':'EXACT_RATIONAL_BERNSTEIN_SUFFICIENT_TEST',
  'quadrature':'Gauss-Jacobi with t^(2ell+2); polynomial exactness in real arithmetic','quadrature_points':nq,
  'flux_identity_absolute_defect':abs(L.imag+J/2),
  'arithmetic':'binary64/complex128; exact Fraction majorant only; no implicit fallback',
  'finite_local_model_only':True,'true_optical_remainder_bound':None,
  'floating_point_error_bound':None,'physical_accuracy_certified':False,
  'cross_section':None,'thermal_rate':None,'photon_spectrum':None,'heat':None}
 return out


def match_pair(seed,*,amplitude):
 if not isinstance(seed,dict) or seed.get('schema')!='bass-he.b5c2.radial-seed.v1':raise ContractError('radial seed required')
 if isinstance(amplitude,(str,bool)):raise ContractError('complex finite amplitude required')
 try:c=complex(amplitude)
 except (TypeError,ValueError) as ex:raise ContractError('complex amplitude required') from ex
 if c==0 or not math.isfinite(c.real) or not math.isfinite(c.imag):raise ContractError('nonzero finite amplitude required')
 L=complex(seed['log_derivative']['real'],seed['log_derivative']['imag']);du=c*L
 try:J=abs(c)**2*seed['inner_absorption']
 except OverflowError as ex:raise NumericalFailure('matching rescale arithmetic range') from ex
 if not all(math.isfinite(v) for v in (du.real,du.imag,J)):raise NumericalFailure('matching rescale range')
 return {'u':[c.real,c.imag],'du':[du.real,du.imag],'inner_absorption':J,
 'requires_accumulate_inner_absorption':True,'cross_section':None,'physical_accuracy_certified':False}
