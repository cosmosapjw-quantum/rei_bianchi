"""Conditional relativistic photon + stationary bare alpha -> d + d.

Per-event weights only; EXFOR DCS is never an encounter flux. No thermal port.
"""
from dataclasses import dataclass
import hashlib,importlib.util,json,math,sys
from pathlib import Path
from numbers import Real
ROOT=Path(__file__).resolve().parents[1];PREVIOUS=ROOT.parent/'continuation_event_20261027/src/reactive_event.py'
if hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()!='89bbcb99cb1487b7e3c132ab6b6d6d0093fbeed2479b112078f6c94f81542ce7':raise RuntimeError('EVENT03 stable product identity changed')
spec=importlib.util.spec_from_file_location('photon05_reactive_dependency',PREVIOUS);old=importlib.util.module_from_spec(spec);sys.modules[spec.name]=old;spec.loader.exec_module(old);product=old.product;ContractError=old.ContractError
EPS=sys.float_info.epsilon;J_PER_MEV=1.602176634e-13;C=299792458.0
CONVENTION='NIST2022_BARE_NUCLEAR_GROUND';PACKET=ROOT.parent/'continuation_20261027/sources/r3_update/raw/PROVIDER_ROWS.json';PACKET_SHA='d8b0b92f0374f73fa7f838db5ca07be45bd448696654b07c6db71c5847235ac2'
def finite(x,name):
 if isinstance(x,bool) or not isinstance(x,Real):raise ContractError(name+' must be a finite real')
 try:x=float(x)
 except (OverflowError,ValueError) as e:raise ContractError(name+' outside binary64') from e
 if not math.isfinite(x):raise ContractError(name+' must be finite')
 return x
def add(*args):
 try:r=math.fsum(args)
 except (ValueError,OverflowError) as e:raise ContractError('derived sum outside binary64') from e
 if not math.isfinite(r):raise ContractError('derived sum outside binary64')
 return r
def vector(v,name):
 try:a=tuple(finite(x,name) for x in v)
 except TypeError as e:raise ContractError(name+' must be a 3-vector') from e
 if len(a)!=3:raise ContractError(name+' must be a 3-vector')
 norm=math.hypot(*a)
 if abs(norm-1)>32*EPS:raise ContractError(name+' must be unit vector; no normalization')
 return a
def outer(q,E):return tuple(tuple(product(q[i],q[j],divisors=(E,)) for j in range(3)) for i in range(3))
@dataclass(frozen=True)
class Daughter:
 energy:float
 momentum_energy:tuple
 kinetic:float
 stress:tuple
 nr_excess:float
@dataclass(frozen=True)
class Event:
 A:float
 M:float
 photon_energy:float
 n:tuple
 u:tuple
 threshold:float
 rest_deficit:float
 cm_energy:float
 kappa:float
 plus:Daughter
 minus:Daughter
 photon_stress:tuple
 material_stress:tuple
 net_stress:tuple

def kernel(A,M,e,n,u):
 A,M,e=finite(A,'A'),finite(M,'M'),finite(e,'photon energy');n=vector(n,'photon direction');u=vector(u,'daughter CM direction')
 if A<=0 or M<=0 or e<=0:raise ContractError('positive endothermic channel required')
 A_half=product(A,0.5);e_half=product(e,0.5)
 if A_half>=M:raise ContractError('positive endothermic channel required')
 delta=add(M,M,-A);threshold=add(delta,product(delta,delta,divisors=(2.0,A)));excess=add(e,-threshold)
 if excess<0:raise ContractError('photon energy below threshold')
 W=product(A,add(A,product(2.0,e)),square_root=True);k=product(A_half,excess,square_root=True);gamma=product(add(A,e),divisors=(W,));eta=product(e,divisors=(W,))
 if not math.isfinite(gamma) or not math.isfinite(eta):raise ContractError('boost outside binary64')
 g=product(eta,eta,divisors=(add(gamma,1.0),));mu=add(*(product(n[i],u[i]) for i in range(3)))
 if abs(mu)>1+64*EPS:raise ContractError('direction dot out of range')
 mu=max(-1.0,min(1.0,mu));base=add(A_half,e_half);shift=product(eta,k,mu);offset=product(g,k,mu)
 def daughter(sign):
  E=add(base,sign*shift)
  if E<=0:raise ContractError('invalid daughter energy')
  q=tuple(add(product(sign,k,u[i]),product(add(sign*offset,e_half),n[i])) for i in range(3));mag=math.hypot(*q)
  if not math.isfinite(mag):raise ContractError('momentum outside binary64')
  K=product(mag,mag,divisors=(add(E,M),));nr=product(K,K,divisors=(2.0,M))
  return Daughter(E,q,K,outer(q,E),nr)
 p=daughter(1.0);m=daughter(-1.0);ps=tuple(tuple(-product(e,n[i],n[j]) for j in range(3)) for i in range(3));ms=tuple(tuple(add(p.stress[i][j],m.stress[i][j]) for j in range(3)) for i in range(3));net=tuple(tuple(add(ms[i][j],ps[i][j]) for j in range(3)) for i in range(3))
 return Event(A,M,e,n,u,threshold,delta,W,k,p,m,ps,ms,net)
def adapter(A,M,e,n,u,flux,*,mass_convention):
 # All input validation and kernel computation precede any zero-flux result.
 if mass_convention==CONVENTION:
  if finite(A,'A')!=3727.3794118 or finite(M,'M')!=1875.61294500:raise ContractError('canonical nuclear masses required for source convention')
 elif mass_convention=='SYNTHETIC_CONTROL':
  if finite(A,'A')!=2.0 or finite(M,'M')!=2.0:raise ContractError('synthetic control requires A=M=2')
 else:raise ContractError('explicit bare nuclear or synthetic control convention required')
 f=finite(flux,'event flux')
 if f<0:raise ContractError('event flux must be nonnegative')
 ev=kernel(A,M,e,n,u);J=J_PER_MEV
 rest=product(ev.rest_deficit,f,J);kin=product(add(ev.plus.kinetic,ev.minus.kinetic),f,J);photon=-product(ev.photon_energy,f,J)
 return {'consumer':'HE_PHOTON_ALPHA_DD_EXPLICIT_EVENT_RECOIL','mass_convention':mass_convention,'synthetic_control':mass_convention=='SYNTHETIC_CONTROL','Gamma_photon':-f,'Gamma_alpha':-f,'Gamma_deuteron':product(2.0,f),'material_count':f,'photon_energy_source_W_m3':photon,'population_rest_energy_witness_W_m3':rest,'material_kinetic_source_W_m3':kin,'photon_momentum_source':tuple(-product(ev.photon_energy,x,f,J,divisors=(C,)) for x in ev.n),'deuteron_momentum_source':tuple(product(add(ev.plus.momentum_energy[i],ev.minus.momentum_energy[i]),f,J,divisors=(C,)) for i in range(3)),'net_stress_source':tuple(tuple(product(ev.net_stress[i][j],f,J) for j in range(3)) for i in range(3)),'independent_binding_rhs':None,'Gamma_thermal':None,'Cv':None,'species_heating':None,'thermal_deposition':None,'birth_pool':'UNASSIGNED','global_species_ID_mapping':None,'physical_rate_admitted':False,'physical_global_consumer_admitted':False}
def source_rows():
 raw=PACKET.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=PACKET_SHA:raise ContractError('EXFOR packet identity mismatch')
 d=json.loads(raw);rows=[x for x in d['rows'] if x['id']=='EXFOR_M0475002']
 if len(rows)!=1:raise ContractError('EXFOR source identity mismatch')
 return rows[0]
def native_event(row_number,phi_rad,flux,*,mass_convention):
 if isinstance(row_number,bool) or not isinstance(row_number,int) or not 1<=row_number<=12:raise ContractError('native EXFOR row number required')
 phi=finite(phi_rad,'explicit CM azimuth');record=source_rows();table=record['raw_values'];rows=table['rows']
 if len(rows)!=12 or record['units']!={'EN':'MEV','ANG-CM':'ADEG','DATA-CM':'NB/SR','ERR-S':'NB/SR'}:raise ContractError('native table structure changed')
 row=rows[row_number-1]
 if row['source_row_1based']!=row_number:raise ContractError('native row identity changed')
 v=row['values'];theta=math.radians(float(v['ANG-CM']));u=(math.sin(theta)*math.cos(phi),math.sin(theta)*math.sin(phi),math.cos(theta));n=(0.0,0.0,1.0)
 event=kernel(3727.3794118,1875.61294500,float(v['EN']),n,u)
 source=adapter(3727.3794118,1875.61294500,float(v['EN']),n,u,flux,mass_convention=mass_convention)
 return {'source_row':row_number,'values':dict(v),'units':dict(record['units']),'phi_rad':phi,'phi_scope':'explicit representative plane, not observed azimuthal distribution','event':event,'source':source,'DCS_or_ERROR_used_as_event_flux':False,'half_factor_applied':False}
