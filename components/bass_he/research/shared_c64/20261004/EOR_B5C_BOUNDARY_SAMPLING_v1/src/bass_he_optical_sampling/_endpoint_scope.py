"""Cross-distance and endpoint electronic references, not a scattering source.

All input distances are in a0; energies are in Eh, excluding nuclear repulsion.
Parent separated-equation and Galerkin kernels are imported without mutation.
Cross-R comparisons evaluate actual fields in the same Cartesian coordinates.
"""
from __future__ import annotations
import hashlib,json,math,numbers
from pathlib import Path
import numpy as np
from scipy.linalg import cholesky,eigh
from scipy.special import roots_laguerre,roots_legendre
from bass_he_prolate_variational.core import (ContractError,NumericalFailure,assemble,
 polynomial_basis,_basis,write_create_only)
from bass_he_two_state import core as cf

ANCHOR_SHA='4988850dbead28056fc6fe5bab41a12f3e44c3dce7eed40094bc9a9df3109f32'
ENDPOINT_CASES={(10.,n,m,16.) for n in (20,28) for m in (24,28)}|{(10.,28,28,12.)}

def real(x,name,lo=None,hi=None):
 if isinstance(x,(bool,str,complex)) or not isinstance(x,numbers.Real):raise ContractError(name+' must be real')
 v=float(x)
 if not math.isfinite(v) or (lo is not None and v<lo) or (hi is not None and v>hi):raise ContractError(name+' out of range')
 return v

def distance(R):return real(R,'R',.5,10.)

def cartesian_chart(R,lam,eta):
 a=distance(R)/2
 l,m=np.broadcast_arrays(np.asarray(lam,dtype=float),np.asarray(eta,dtype=float))
 if not np.all(np.isfinite(l)) or not np.all(np.isfinite(m)) or np.any(l<1) or np.any(abs(m)>1):raise ContractError('invalid prolate coordinates')
 return a*np.sqrt((l-1)*(l+1)*(1-m)*(1+m)), a*l*m

def prolate_chart(R,rho,z):
 a=distance(R)/2
 r,z=np.broadcast_arrays(np.asarray(rho,dtype=float),np.asarray(z,dtype=float))
 if not np.all(np.isfinite(r)) or not np.all(np.isfinite(z)) or np.any(r<0):raise ContractError('finite cylindrical rho>=0 and z required')
 ra=np.hypot(r,z+a);rb=np.hypot(r,z-a);total=ra+rb
 l=total/(2*a);m=2*z/total
 if np.any(l<1-1e-12) or np.any(abs(m)>1+1e-12):raise NumericalFailure('coordinate identity defect')
 # Only clamp roundoff at the known closed chart boundaries, not a physical cutoff.
 return np.maximum(l,1.),np.clip(m,-1.,1.)

def cross_fields(left,right,*,chart_R,qr,qa,scale):
 """Positive full-space quadrature, Phi integrated. Fields exclude Phi=1/sqrt(2pi).

 The quadrature is not an enclosure. Repeated resolution checks remain empirical.
 Compute weighted fields before squaring to avoid avoidable product underflow.
 """
 R=distance(chart_R);scale=real(scale,'radial quadrature scale',.25,32.)
 if any(isinstance(q,bool) or not isinstance(q,(int,np.integer)) or not 16<=q<=128 for q in (qr,qa)):raise ContractError('quadrature size 16..128')
 if not left or not right:raise ContractError('nonempty field collections required')
 t,w=roots_laguerre(int(qr));m,v=roots_legendre(int(qa));l=1+t/scale
 rho,z=cartesian_chart(R,l[:,None],m[None,:])
 weight=(R/2)**3*((w*np.exp(t)/scale)[:,None]*v[None,:])*(l[:,None]**2-m[None,:]**2)
 if not np.all(np.isfinite(weight)) or np.any(weight<=0):raise NumericalFailure('positive quadrature weight failure')
 sq=np.sqrt(weight)
 def values(funcs):
  out=[]
  for f in funcs:
   x=np.asarray(f(rho,z),dtype=float)
   if x.shape!=rho.shape or not np.all(np.isfinite(x)):raise NumericalFailure('field shape or nonfinite value')
   out.append((x*sq).ravel())
  return out
 a=values(left);b=values(right)
 def ip(x,y):return math.fsum(float(s) for s in x*y)
 an=[math.sqrt(ip(x,x)) for x in a];bn=[math.sqrt(ip(x,x)) for x in b]
 if min(an+bn)<=0 or not all(math.isfinite(x) for x in an+bn):raise NumericalFailure('nonpositive field norm')
 cross=np.array([[ip(x/n,y/k) for y,k in zip(b,bn)] for x,n in zip(a,an)])
 dif=[]
 for i in range(min(len(a),len(b))):
  sign=-1. if cross[i,i]<0 else 1.
  delta=sign*a[i]/an[i]-b[i]/bn[i];dif.append(math.sqrt(ip(delta,delta)))
 return {'norm_left':an,'norm_right':bn,'overlap':cross.tolist(),'aligned_direct_L2':dif,
  'qr':int(qr),'qa':int(qa),'integration_chart_R_a0':R,'radial_scale':scale,
  'raw_coefficient_dot_used':False,'quadrature_error_bound':None,'physical_accuracy_certified':False}

def phase_alignment(overlap,*,minimum=.75,margin=.25):
 x=np.asarray(overlap,dtype=float)
 if x.shape!=(2,2) or not np.all(np.isfinite(x)):raise ContractError('finite two-state overlap required')
 for i in range(2):
  if abs(x[i,i])<minimum or abs(x[i,i])-abs(x[i,1-i])<margin:raise NumericalFailure('phase/branch overlap criterion not satisfied')
 return np.where(np.diag(x)<0,-1,1)

def load_anchor(path):
 p=Path(path)
 if p.is_symlink():raise ContractError('anchor symlink forbidden')
 b=p.read_bytes()
 if hashlib.sha256(b).hexdigest()!=ANCHOR_SHA:raise ContractError('anchor SHA mismatch')
 obj=json.loads(b);states=[]
 for x in obj['state_coefficients']:
  g=np.asarray(x['radial_g'],dtype=float);f=np.asarray(x['angular_f'],dtype=float);g.setflags(write=False);f.setflags(write=False)
  nodes=x['nodes_observed'];rn,an=(nodes['radial'],nodes['angular']) if isinstance(nodes,dict) else nodes
  states.append(cf.State(2.,x['label'],x['center'],x['p'],x['Aprime'],x['energy_Eh'],x['order'],g,f,tuple(x['CF_residual']),rn,an,x['root_evaluations'],x['root_message'],cf.DERIVED))
 if len(states)!=2:raise ContractError('two anchor states required')
 return tuple(states)

def seed_from_previous(state,new_R):
 R=distance(new_R)
 if not isinstance(state,cf.State) or not (0<abs(R-state.R)<=.25):raise ContractError('previous State and distinct step <= .25 required')
 return {'energy_Eh':state.energy_Eh,'Aprime':state.aprime,'p':state.p*R/state.R,'from_R_a0':state.R,'to_R_a0':R}

def cf_field(state,*,phase=1):
 if phase not in (-1,1):raise ContractError('real phase +/-1 required')
 norm=cf._norm(state,96,96)
 def f(rho,z):
  l,m=prolate_chart(state.R,rho,z)
  return phase*norm*cf.factors(state,l,coordinate='radial')*cf.factors(state,m,coordinate='angular')
 return f

def var_field(result,index):
 if not 0<=index<len(result['energies_Eh']):raise ContractError('state index')
 R=result['R_a0'];nr=result['nr'];na=result['na'];be=result['beta'];coeff=result['coefficients'][:,index].reshape(nr,na)
 def f(rho,z):
  from scipy.special import eval_laguerre,eval_legendre
  l,m=prolate_chart(R,rho,z);x=be*(l-1)
  L=np.stack([eval_laguerre(n,x) for n in range(nr)],axis=-1)
  P=np.stack([math.sqrt((2*j+1)/2)*eval_legendre(j,m) for j in range(na)],axis=-1)
  # Basis evaluation at the same physical point, not a cross-basis coefficient dot.
  return np.exp(-x/2)*np.einsum('...n,nm,...m->...',L,coeff,P,optimize=True)
 return f

def optical_diagnostic(R,e_lower,e_upper,d):
 R=distance(R);el=real(e_lower,'El');eu=real(e_upper,'Eu');d=real(d,'dipole')
 if not el<eu<0:raise ContractError('ordered negative electronic energies')
 gap=eu-el;V=math.fsum([eu,.5,2/R]);sc=math.fsum([abs(eu),.5,2/R]);A=4/3*gap**3*d*d
 return {'R_a0':R,'E_lower_Eh':el,'E_upper_Eh':eu,'gap_Eh':gap,'dipole_signed_a0':d,'dipole_abs_a0':abs(d),
  'V_entrance_Eh':V,'V_naive_sum_Eh':eu+.5+2/R,'V_sum_condition_number':sc/abs(V) if V else None,
  'A_ta_div_alpha3':A,'roundoff_scale_Eh':np.finfo(float).eps*sc,
  'roundoff_scale_is_error_bound':False,'physical_accuracy_certified':False,
  'cross_section':None,'thermal_rate':None,'heat':None,'recoil':None,'photon_spectrum':None}

def registered_endpoint(R,nr,na,beta):
 R=distance(R);nr,na,beta=_basis(nr,na,beta)
 if (R,nr,na,beta) not in ENDPOINT_CASES:raise ContractError('unregistered endpoint/basis/scale combination')
 return {'R':R,'nr':nr,'na':na,'beta':beta}

def solve_endpoint(R,nr,na,beta):
 """Independent generalized solve at explicitly registered endpoints. No CF input."""
 cfg=registered_endpoint(R,nr,na,beta)
 a=assemble(R,nr,na,beta,backend='analytic')
 try:
  cholesky(a['S'],lower=True,check_finite=True)
  vals,vec=eigh(a['H'],a['S'],type=1,driver='gvx',subset_by_index=[0,3],check_finite=True)
 except Exception as e:raise NumericalFailure('endpoint generalized eigensolve failed') from e
 for i in range(4):
  if i<2:
   eta=1. if i==0 else -1.;endpoint=np.tile(np.sqrt((2*np.arange(na)+1)/2)*eta**np.arange(na),nr)
   signvalue=float(endpoint@vec[:,i])
  else:signvalue=float(vec[np.argmax(abs(vec[:,i])),i])
  if signvalue<0:vec[:,i]*=-1
 mass=vec.T@a['S']@vec;res=a['H']@vec-(a['S']@vec)*vals
 scales=np.linalg.norm(a['H'])*np.linalg.norm(vec,axis=0)+abs(vals)*np.linalg.norm(a['S']@vec,axis=0)
 rel=np.linalg.norm(res,axis=0)/scales;z=vec.T@a['Z']@vec;dz=vec.T@a['Dz']@vec
 if np.max(rel)>1e-10 or np.max(abs(mass-np.eye(4)))>1e-10:raise NumericalFailure('endpoint algebraic validation failed')
 return {'R_a0':float(R),'nr':nr,'na':na,'beta':float(beta),'energies_Eh':vals,'coefficients':vec,
  'mass_gram':mass,'dipole_matrix_a0':z,'derivative_matrix':dz,'relative_matrix_residuals':rel,
  'dipole_length_a0':float(z[0,1]),'dipole_velocity_a0':float(dz[0,1]/(vals[1]-vals[0])),
  'driver':'scipy.linalg.eigh:gvx:type1','CF_or_printed_seed_used':False,'physical_accuracy_certified':False}

def dump_state(s):
 return {'R_a0':s.R,'label':s.label,'center':s.center,'p':s.p,'Aprime':s.aprime,'energy_Eh':s.energy_Eh,
  'order':s.order,'radial_g':s.radial_coefficients.tolist(),'angular_f':s.angular_coefficients.tolist(),
  'CF_residual':list(s.residual),'nodes_observed':[s.radial_nodes,s.angular_nodes],
  'root_evaluations':s.root_evaluations,'root_message':s.root_message,'convention':s.convention}


def cf_jacobian(R,p,ap,order,*,center):
 """Differentiate the finite CF algebra, columns (R,p,Aprime), not full-H eigenvalues."""
 R=distance(R);p=real(p,'p',1e-10,100.);ap=real(ap,'Aprime')
 n=cf._order(order)
 if center not in ('A','B'):raise ContractError('explicit angular centre')
 dR=np.array([1.,0.,0.]);dp=np.array([0.,1.,0.]);dA=np.array([0.,0.,1.])
 sig=3*R/(2*p)-1;dsig=3/(2*p)*dR-3*R/(2*p*p)*dp
 a,b,c=cf.radial_coefficients(R,p,ap,n)
 ss=np.arange(n+1,dtype=float)
 db=(4*ss-2*sig)[:,None]*dp-(2*ss+2*p+1)[:,None]*dsig-dA
 dc=-2*(ss-1-sig)[:,None]*dsig
 sign=1. if center=='A' else -1.;pp=sign*p;dpp=sign*dp
 aa,ab,ac=cf.angular_coefficients(R,pp,ap,n,convention=cf.DERIVED)
 da=(ss+1)[:,None]/(2*ss+3)[:,None]*(2*(ss+1)[:,None]*dpp-dR)
 dbb=np.broadcast_to(dA,(n+1,3))
 dcc=ss[:,None]/(2*ss-1)[:,None]*(2*ss[:,None]*dpp+dR)
 rg=rf=0.;drg=np.zeros(3);drf=np.zeros(3)
 for j in range(n,0,-1):
  den=b[j]-a[j]*rg;denf=ab[j]+aa[j]*rf
  if den==0 or denf==0 or not math.isfinite(den+denf):raise NumericalFailure('CF derivative pole')
  dd=db[j]-a[j]*drg;ddf=dbb[j]+da[j]*rf+aa[j]*drf
  rgnew=c[j]/den;rfnew=ac[j]/denf
  drg=(dc[j]-rgnew*dd)/den;drf=(dcc[j]-rfnew*ddf)/denf;rg,rf=rgnew,rfnew
 F=np.array([a[0]*rg-b[0],aa[0]*rf+ab[0]])
 J=np.stack([a[0]*drg-db[0],da[0]*rf+aa[0]*drf+dbb[0]])
 if not np.all(np.isfinite(J)):raise NumericalFailure('nonfinite differentiated CF')
 return F,J

def tangent_predictor(state,new_R):
 R=distance(new_R)
 if not isinstance(state,cf.State) or not 0<abs(R-state.R)<=.125:raise ContractError('A1 tangent step must be in (0,.125]')
 F,J=cf_jacobian(state.R,state.p,state.aprime,state.order,center=state.center)
 if max(abs(F))>1e-9:raise ContractError('tangent requires accepted finite-CF root')
 cond=float(np.linalg.cond(J[:,1:]))
 if not math.isfinite(cond) or cond>1e10:raise NumericalFailure('ill-conditioned tangent Jacobian')
 dz=np.linalg.solve(J[:,1:],-J[:,0]);pred=np.array([state.p,state.aprime])+(R-state.R)*dz
 if pred[0]<=0:raise NumericalFailure('nonpositive tangent p prediction')
 return {'energy_Eh':float(-2*pred[0]**2/R**2),'Aprime':float(pred[1]),'p':float(pred[0]),
 'from_R_a0':state.R,'to_R_a0':R,'strategy':'FINITE_CF_IMPLICIT_TANGENT',
 'dp_dR_dAprime_dR':dz.tolist(),'jacobian_condition':cond,'physical_derivative_certified':False}
