"""Independent positive q-ray/node measure evolution with MPFI200 kernels."""
from independent_stage import R,AD,m,Model,certify
from dataclasses import dataclass
import math,bisect
from functools import lru_cache

def interval(x):return R(float(x[0]),float(x[1]))
def inside(native,true):
 b=interval(native);return b.lower()<=true.lower() and true.upper()<=b.upper()
def intersect_nonnegative(x):return R(max(R(0).lower(),x.lower()),max(R(0).lower(),x.upper()))
@lru_cache(maxsize=2048)
def _g(q,h,t):return sum((R(float(q[i]))**2*(-R(2)*R(float(h[i]))*R(float(t))).exp() for i in range(3)),R(0)).sqrt()
def hat_scalar(x,nodes,j):
 e=nodes[j];lo=nodes[j-1] if j else e;hi=nodes[j+1] if j+1<len(nodes) else e
 if j and x<=lo:return R(0)
 if j+1<len(nodes) and x>=hi:return R(0)
 if x<=e:return R(1) if not j else (x-lo)/(e-lo)
 return R(1) if j+1==len(nodes) else (hi-x)/(hi-e)
def hat_range(x,nodes,j):
 values=[hat_scalar(R(x.lower()),nodes,j),hat_scalar(R(x.upper()),nodes,j)]
 for k in range(max(0,j-1),min(len(nodes),j+2)):
  if x.lower()<=nodes[k].lower()<=x.upper():values.append(R(1 if k==j else 0))
 return R(min(v.lower() for v in values),max(v.upper() for v in values))
def verner(energy,a):
 pars=[(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),(54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)][a]
 eth,e0,s0,ya,p,yw,y0,y1=[R(float(v)) for v in pars]
 if R(float(energy)).upper()<eth.lower():return R(0)
 x=R(float(energy))/e0-y0;y=(x*x+y1*y1).sqrt();return s0*((x-1)**2+yw*yw)*((p/2-R(5.5))*y.log()).exp()*(-p*(1+(y/ya).sqrt()).log()).exp()*R(float(1e-18))
def g(q,h,t):return _g(tuple(q),tuple(h),float(t))
@dataclass
class Radiation:
 time:float
 counts:list
 guard_n:list
 guard_u:list
 gas:list
 isotropic:bool=False
 qgroups:object=None

def initial(header):
 nodes=header['energy_nodes'];nd=len(header['qhat']);counts=[[R(0)]*len(nodes) for _ in range(nd)];birth=nodes.index(13.7)
 for row in counts:row[birth]=R(float(.05/nd))
 w=1.5*1.380649e-16*50000*(1+.083+.9+.083*(.3+2*.6))/1.602176634e-12
 # In FLRW g(q,t)=||q|| exp(-H*t), so every ray has the same
 # energy ratio. Positive transport/attenuation commute exactly with summation.
 # Normalized source weights sum to one; no angular approximation is changed.
 iso=header['geometry']=='FLRW'
 if iso:counts=[[R(float(.05/nd))*nd if k==birth else R(0) for k in range(len(nodes))]];nd=1
 groups=None
 if not iso:
  bins={}
  for q in header['qhat']:bins.setdefault(tuple(round(float(x)*float(x),12) for x in q),[]).append(q)
  groups=[];counts=[]
  for qs in bins.values():
   squares=[]
   for i in range(3):
    values=[R(float(q[i]))**2 for q in qs];squares.append(R(min(v.lower() for v in values),max(v.upper() for v in values)))
   groups.append((len(qs),squares));counts.append([R(float(.05/nd))*len(qs) if k==birth else R(0) for k in range(len(nodes))])
  nd=len(groups)
 return Radiation(0.,counts,[R(0)]*nd,[R(0)]*nd,[R(.9),R(.3),R(.6),R(w)],iso,groups)
def pre_stage(header,h,s,t):
 nodes=[R(float(v)) for v in header['energy_nodes']];nd=len(s.counts);out=[[R(0) for _ in nodes] for _ in range(nd)];gn=s.guard_n.copy();gu=s.guard_u.copy();jac=[]
 for d in range(nd):
  if s.isotropic:
   assert h==[h[0]]*3,'ISOTROPIC_MODEL_BINDING'
   ratio=(-R(float(h[0]))*(R(float(t))-R(float(s.time)))).exp();jac.append(R(1))
  elif s.qgroups is not None:
   multiplicity,squares=s.qgroups[d];hb=sum((R(float(x)) for x in h),R(0))/3;delta=[R(float(x))-hb for x in h];old=[squares[i]*(-2*delta[i]*R(float(s.time))).exp() for i in range(3)];den=sum(old,R(0));duration=R(float(t))-R(float(s.time))
   # Exact centering uses sum(w_i)=1. It preserves the original g ratio
   # while bounding binary q variations without spurious norm cancellation.
   shift=sum((old[i]/den*((-2*delta[i]*duration).exp()-1) for i in range(3)),R(0));ratio=(-hb*duration).exp()*(1+shift).sqrt()
   now=sum((squares[i]*(-2*delta[i]*R(float(t))).exp() for i in range(3)),R(0));jac.append(R(multiplicity)/(now*now.sqrt()))
  else:
   q=header['qhat'][d];gt=g(q,h,t);ratio=gt/g(q,h,s.time)
   jac.append((-sum((R(float(v)) for v in h),R(0))*R(float(t))).exp()/(gt**3))
  gu[d]*=ratio
  for k,amount in enumerate(s.counts[d]):
   if amount.upper()==0:continue
   e=nodes[k]*ratio
   if e.upper()<nodes[0].lower():gn[d]+=amount;gu[d]+=amount*e;continue
   assert e.lower()>=nodes[0].lower() and e.upper()<=nodes[-1].upper(),'UNIMPLEMENTED_OR_SPLIT_GUARD'
   # Hat support is [node[j-1],node[j+1]]. Monotonic nodes permit
   # omission only of provably identically zero weights. nextafter pads both
   # binary conversions, so this changes neither model nor enclosure arithmetic.
   lo=max(0,bisect.bisect_left(header['energy_nodes'],math.nextafter(float(e.lower()),-math.inf))-1)
   hi=min(len(nodes)-1,bisect.bisect_right(header['energy_nodes'],math.nextafter(float(e.upper()),math.inf)))
   for j in range(lo,hi+1):
    weight=hat_range(e,nodes,j)
    if weight.upper()!=0:out[d][j]+=amount*weight
 total=sum(jac,R(0));source=R(float(t-s.time))*R(float(5e-15));birth=header['energy_nodes'].index(13.7)
 for d in range(nd):out[d][birth]+=source*jac[d]/total
 return Radiation(t,out,gn,gu,s.gas,s.isotropic,s.qgroups)
def stage(header,h,s,a):
 t=float(a['time_s']);dt=float(a['dt_s']);assert t==s.time+dt,'STAGE_TIME'
 incoming=pre_stage(header,h,s,t);idx=a['group_indices'];assert len(idx)==len(set(idx)) and idx==sorted(idx),'GROUP_ORDER'
 for k in range(len(header['energy_nodes'])):
  true=sum((row[k] for row in incoming.counts),R(0))
  if k in idx:
   j=idx.index(k);assert a['energies_ev'][j]==header['energy_nodes'][k],'ENERGY_IDENTITY';assert inside(a['parent_photons'][j],true),('PHOTON_INHERITANCE',t,k)
  else:assert true.upper()==0,('OMITTED_POSITIVE_GROUP',t,k)
 for i in range(4):assert inside(a['parent_gas'][i],s.gas[i]),('GAS_INHERITANCE',t,i)
 nh=1e-4*math.exp(-sum(h)*t);hm=sum(h)/3;assert a['n_h_cm3']==nh and a['f_he']==.083 and a['h_mean_per_s']==hm,'STAGE_DENSITY_TIME'
 for j,e in enumerate(a['energies_ev']):
  for ab in range(3):
   reference=verner(e,ab);native=float(a['sigma_cm2'][j][ab])
   if reference.upper()==0:assert native==0,'INACTIVE_SIGMA'
   else:assert abs((R(native)-reference)/reference).upper()<R(float(3e-12)).lower(),'SIGMA_BINARY_PARAMETER_BINDING'
 proof=certify(nh,.083,hm,a['energies_ev'],a['sigma_cm2'],dt,a['parent_gas'],a['parent_photons'],a['centre'],a['out_gas'],a['preconditioner'],a['out_photons'])
 Y=[interval(b) for b in a['out_gas']];low=[1-Y[0],R(.083)*(1-Y[1]-Y[2]),R(.083)*Y[1]]
 for j,k in enumerate(idx):
  opacity=R(float(29979245800))*R(nh)*sum((low[ab]*R(float(a['sigma_cm2'][j][ab])) for ab in range(3)),R(0));factor=1/(1+R(dt)*opacity)
  for row in incoming.counts:row[k]*=factor
 incoming.gas=Y
 return incoming,proof

def observables(header,s):
 nodes=[R(float(v)) for v in header['energy_nodes']];groups=[sum((row[k] for row in s.counts),R(0)) for k in range(len(nodes))];N=sum(groups,R(0))+sum(s.guard_n,R(0));U=sum((groups[k]*nodes[k] for k in range(len(nodes))),R(0))+sum(s.guard_u,R(0));gas=s.gas
 # Exact declared fHe; coupledstage's rounded density ratio is separately enclosed.
 particle=1+R(.083)+gas[0]+R(.083)*(gas[1]+2*gas[2]);T=2*R(float(1.602176634e-12))*gas[3]/(3*R(float(1.380649e-16))*particle)
 w0=1.5*1.380649e-16*50000*(1+.083+.9+.083*(.3+2*.6))/1.602176634e-12
 return [*gas[:3],T.log(),gas[3]/R(w0),N/R(.05),U/(R(.05)*R(13.7)),*[x/R(.05) for x in groups],sum(s.guard_n,R(0))/R(.05),sum(s.guard_u,R(0))/(R(.05)*R(13.7))]
def trial(header,h,s,row):
 dt=float(row['dt_s']);a=row['audits'];assert len(a)==3
 full,p0=stage(header,h,s,a[0]);half,p1=stage(header,h,s,a[1]);two,p2=stage(header,h,half,a[2]);assert full.time==s.time+dt and half.time==s.time+dt/2 and two.time==full.time,'TRIAL_TOPOLOGY'
 of=observables(header,full);ot=observables(header,two);local=max(m.absmax(x-y) for x,y in zip(of,ot));width=max(x.absolute_diameter() for x in ot);assert local<R(float(2e-4)).lower(),'STRICT_LOCAL_GATE';assert width<R(float(2e-3)).lower(),'STRICT_PUBLIC_WIDTH'
 return two,{'local':m.upper(local),'width':m.upper(width),'q':max(p['q'] for p in [p0,p1,p2])}
