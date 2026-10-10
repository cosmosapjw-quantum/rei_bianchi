"""Bind binary point outputs, events, checkpoint and final conservation to MPFI audit.
No production evaluator. Frozen numerical ledger limit is 1e-12. Binary point
representation comparisons use a stricter 3e-14 scaled allowance, not fit error.
"""
from dataclasses import dataclass
import math,struct
from pathlib import Path
from independent_stage import R,Model,m,AD
CHI=[13.598434599702,24.587389011,54.41776];F=.083;C=29979245800.;EV=1.602176634e-12;KB=1.380649e-16

def close(a,b,scale=1.,label='POINT_BINDING'):
 assert math.isfinite(float(a)) and math.isfinite(float(b)) and abs(float(a)-float(b))<=3e-14*max(abs(float(a)),abs(float(b)),scale),(label,a,b)
def ledger_close(a,b,scale,label):
 assert math.isfinite(float(a)) and math.isfinite(float(b)) and abs(float(a)-float(b))<=1e-12*scale,(label,a,b)
def nonnegative(v):
 if isinstance(v,list):
  for x in v:nonnegative(x)
 else:assert math.isfinite(v) and v>=0,('NONNEGATIVE',v)
def g(q,h,t):return math.sqrt(sum(q[i]*q[i]*math.exp(-2*h[i]*t) for i in range(3)))
def energy(gas,escape):return gas[3]+CHI[0]*gas[0]+F*(CHI[1]*gas[1]+(CHI[1]+CHI[2])*gas[2])+escape
@dataclass
class Point:
 time:float
 counts:list
 gn:list
 gu:list
 gas:list
 escape:float=0.
 redshift:float=0.
 thermal:float=0.
 source_n:float=0.
 source_u:float=0.
 absorbed:float=0.
 packets:object=None
 compensation:object=None

def initial(header):
 nd=len(header['qhat']);nodes=header['energy_nodes'];p=[[0.]*len(nodes) for _ in range(nd)]
 for row in p:row[nodes.index(13.7)]=.05/nd
 w=1.5*KB*50000*(1+F+.9+F*(.3+2*.6))/EV
 return Point(0.,p,[0.]*nd,[0.]*nd,[.9,.3,.6,w])
def number(s):return math.fsum(x for row in s.counts for x in row)+math.fsum(s.gn)
def photon_energy(s,nodes):return math.fsum(row[k]*nodes[k] for row in s.counts for k in range(len(nodes)))+math.fsum(s.gu)
def events(a,gas,photons):
 model=Model(a['n_h_cm3'],F,a['h_mean_per_s'],a['energies_ev'],a['sigma_cm2'],a['dt_s']);t=model.temperature([AD(R(float(v))) for v in gas+[1.]*3]).v;nh=model.nh;ne=nh*R(gas[0])+model.nhe*(R(gas[1])+2*R(gas[2]));lower=[nh*(1-R(gas[0])),model.nhe*(1-R(gas[1])-R(gas[2])),model.nhe*R(gas[1])];up=[nh*R(gas[0]),model.nhe*R(gas[1]),model.nhe*R(gas[2])];dt=R(a['dt_s']);ci=[];rr=[];kin=[]
 for ab in range(3):
  l=R(float([315614,570670,1263030][ab]))/t
  if ab==1:alpha=R(3e-14)*(R(.654)*l.log()).exp();gg=R(-.654)
  else:
   u=(R(.470)*(l/R(.522)).log()).exp();alpha=R(float(2 if ab==2 else 1))*R(1.269e-13)*(R(1.503)*l.log()).exp()/(R(1.923)*(1+u).log()).exp();gg=R(-1.503)+R(1.923)*R(.470)*u/(1+u)
  beta=R(float([21.11,32.38,19.95][ab]))*(R(-1.5)*t.log()).exp()*(-l/2).exp()*(R(float([-1.089,-1.146,-1.089][ab]))*l.log()).exp()/(R(float([1.101,1.056,1.275][ab]))*(1+(R(float([.874,.987,.735][ab]))*(l/R(float([.354,.416,.553][ab]))).log()).exp()).log()).exp()
  ci.append(dt*lower[ab]*ne*beta/nh);rr.append(dt*up[ab]*ne*alpha/nh);kin.append(model.kb*t*(R(1.5)+gg)/model.ev)
 dr=[dt*up[1]*ne*pref*(R(-1.5)*t.log()).exp()*(-b/t).exp()/nh for pref,b in [(model.da,model.b1),(R(.3)*model.da,model.b12)]]
 photo=[[dt*model.c*nh*lo*R(float(sig))*R(float(pn)) for lo,sig in zip([1-R(gas[0]),R(F)*(1-R(gas[1])-R(gas[2])),R(F)*R(gas[1])],sigs)] for sigs,pn in zip(a['sigma_cm2'],photons)]
 escape=sum((rr[i]*(model.chi[i]+kin[i]) for i in range(3)),R(0))+sum((d*(model.chi[1]+model.kb*b/model.ev) for d,b in zip(dr,[model.b1,model.b12])),R(0));thermal=2*model.hmean*dt*R(gas[3])
 for key,true in [('collision_events',ci),('recombination_events',rr),('dr_events',dr)]:
  for x,y in zip(a[key],true):close(x,float(y.center()),1e-15,key)
 for native,true in zip(a['photo_events'],photo):
  for x,y in zip(native,true):close(x,float(y.center()),1e-15,'PHOTO_EVENT')
 close(a['thermal_work'],float(thermal.center()),1e-15,'THERMAL_EVENT')
 return float(escape.center()),float(thermal.center()),math.fsum(float(x.center()) for p in photo for x in p)

def stage(header,h,s,a):
 nodes=header['energy_nodes'];t=a['time_s'];dt=a['dt_s'];assert t==s.time+dt
 for x,y in zip(a['old_gas'],s.gas):close(x,y,1.,'OLD_GAS')
 out=[[0.]*len(nodes) for _ in s.counts];gn=s.gn.copy();gu=[];jac=[]
 for d,q in enumerate(header['qhat']):
  gt=g(q,h,t);ratio=gt/g(q,h,s.time);gu.append(s.gu[d]*ratio);jac.append(math.exp(-sum(h)*t)/(gt**3))
  for k,v in enumerate(s.counts[d]):
   if v==0:continue
   e=nodes[k]*ratio
   if e<10:gn[d]+=v;gu[d]+=v*e;continue
   for j in range(len(nodes)):
    if j==0:w=1. if e<=nodes[0] else (nodes[1]-e)/(nodes[1]-nodes[0]) if e<nodes[1] else 0.
    elif j+1==len(nodes):w=1. if e>=nodes[j] else (e-nodes[j-1])/(nodes[j]-nodes[j-1]) if e>nodes[j-1] else 0.
    elif e<=nodes[j-1] or e>=nodes[j+1]:w=0.
    elif e<=nodes[j]:w=(e-nodes[j-1])/(nodes[j]-nodes[j-1])
    else:w=(nodes[j+1]-e)/(nodes[j+1]-nodes[j])
    out[d][j]+=v*w
 pre=Point(t,out,gn,gu,s.gas);tn=number(pre);tu=photon_energy(pre,nodes);sn=dt*5e-15;su=sn*13.7
 for key,v in [('transport_n',tn),('transport_u',tu),('source_n',sn),('source_u',su)]:close(a[key],v,.05 if key.endswith('_n') else .685,key)
 for d in range(len(out)):out[d][nodes.index(13.7)]+=sn*jac[d]/sum(jac)
 gas=a['point_gas'];nonnegative(gas);assert gas[0]<=1 and gas[1]+gas[2]<=1
 for i,x in enumerate(gas):assert a['out_gas'][i][0]<=x<=a['out_gas'][i][1],'POINT_GAS_BOX'
 idx=a['group_indices'];groups=[math.fsum(row[k] for row in out) for k in idx];pn=a['point_photons'];nonnegative(pn)
 for j,k in enumerate(idx):
  lower=[1-gas[0],F*(1-gas[1]-gas[2]),F*gas[1]];opacity=C*a['n_h_cm3']*sum(lower[i]*a['sigma_cm2'][j][i] for i in range(3));expected=groups[j]/(1+dt*opacity);ledger_close(pn[j],expected,.05,'POINT_PHOTON_BE');factor=a['point_factors'][j];close(factor,1/(1+dt*opacity),1.,'POINT_FACTOR')
  assert a['out_photons'][j][0]<=pn[j]<=a['out_photons'][j][1],'POINT_PHOTON_BOX'
  for ray in out:ray[k]*=pn[j]/groups[j] if groups[j] else factor
 # Independent exact-binary implicit gas residual, separate from model fit uncertainty.
 model=Model(a['n_h_cm3'],F,a['h_mean_per_s'],a['energies_ev'],a['sigma_cm2'],dt);old=m.J;m.J=AD
 try:rhs,_=model.coupled([R(float(x)) for x in gas],[R(float(x)) for x in groups])
 finally:m.J=old
 residual=max(m.absmax(R(gas[i])-R(s.gas[i])-R(dt)*rhs[i].v)/(s.gas[3] if i==3 else 1.) for i in range(4));assert residual<=R(1e-12).lower(),('POINT_IMPLICIT_RESIDUAL',t,residual)
 assert math.isfinite(a['point_residual']) and 0<=a['point_residual']<=1e-12,'REPORTED_POINT_RESIDUAL'
 de,tw,absorb=events(a,gas,pn);escape=a['point_escape_ev_per_h'];close(escape,s.escape+de,energy(s.gas,s.escape),'ESCAPE_EVENT');nonnegative(escape)
 next=Point(t,out,gn,gu,list(gas),escape,s.redshift+photon_energy(s,nodes)-tu,s.thermal+tw,s.source_n+sn,s.source_u+su,s.absorbed+absorb,list(zip(a['energies_ev'],pn,a['sigma_cm2'])))
 # Separate compensated reconstruction of the five long-history ledgers.
 increments=[photon_energy(s,nodes)-tu,tw,sn,su,absorb];names=['redshift','thermal','source_n','source_u','absorbed'];old_comp=s.compensation or [0.]*5;next.compensation=[]
 for name,inc,correction in zip(names,increments,old_comp):
  previous=getattr(s,name);y=inc-correction;total=previous+y;next.compensation.append((total-previous)-y);setattr(next,name,total)
 step_n=abs(tn+sn-number(next)-absorb)/max(number(s)+sn,.05);step_u=abs(energy(next.gas,next.escape)+photon_energy(next,nodes)+tw-energy(s.gas,s.escape)-tu-su)/max(energy(s.gas,s.escape)+photon_energy(s,nodes)+su,.685);assert max(step_n,step_u,abs(tn-number(s))/max(number(s)+sn,.05))<=1e-12,('STEP_LEDGER',t,step_n,step_u)
 return next,max(step_n,step_u)

def report(header,h,s,row):
 nodes=header['energy_nodes'];particles=1+F+s.gas[0]+F*(s.gas[1]+2*s.gas[2]);T=2*EV*s.gas[3]/(3*KB*particles)
 values={'time_s':s.time,'w_ev_per_h':s.gas[3],'temperature_K':T,'photon_n':number(s),'photon_u_ev_per_h':photon_energy(s,nodes),'lower_guard_n':math.fsum(s.gn),'lower_guard_u':math.fsum(s.gu),'escape_ev_per_h':s.escape,'redshift_work_ev_per_h':s.redshift,'thermal_work_ev_per_h':s.thermal,'source_n':s.source_n,'source_u':s.source_u,'absorbed_n':s.absorbed}
 for key,v in values.items():
  if key in ['photon_n','photon_u_ev_per_h','redshift_work_ev_per_h']:ledger_close(row[key],v,.05 if key=='photon_n' else max(.685,energy(s.gas,s.escape)),'REPORT_'+key)
  else:close(row[key],v,max(1.,energy(s.gas,s.escape)) if key not in ['time_s','temperature_K'] else max(1.,v),'REPORT_'+key)
 for x,y in zip(row['fractions'],s.gas[:3]):close(x,y,1.,'REPORT_FRACTION')
 from independent_radiation import verner
 gamma=[C*(1e-4*math.exp(-sum(h)*s.time))*math.fsum(pn*sig[ab] for e,pn,sig in s.packets) for ab in range(3)]
 for x,y in zip(row['gamma_per_s'],gamma):close(x,y,1e-25,'REPORT_GAMMA')
 for key,lim in [('local_bound',2e-4),('public_width',2e-3),('ledger',1e-12)]:assert math.isfinite(row[key]) and 0<=row[key]<lim,('REPORTED_GATE',key)
 for i,x in enumerate(s.gas):assert row['gas_parent'][i][0]<=x<=row['gas_parent'][i][1],'REPORT_GAS_BOX'
 return values

def trial(header,h,s,row):
 full,l0=stage(header,h,s,row['audits'][0]);half,l1=stage(header,h,s,row['audits'][1]);two,l2=stage(header,h,half,row['audits'][2]);assert full.time==s.time+row['dt_s'] and half.time==s.time+row['dt_s']/2 and two.time==full.time
 report(header,h,two,row);return two,max(l0,l1,l2)
def cumulative(header,s):
 init=initial(header);nodes=header['energy_nodes'];e0=energy(init.gas,0)+photon_energy(init,nodes)
 return [abs(number(s)+s.absorbed-s.source_n-.05)/(.05+s.source_n),abs(energy(s.gas,s.escape)+photon_energy(s,nodes)+s.redshift+s.thermal-s.source_u-e0)/(e0+s.source_u)]
def checkpoint(header,s,path,accepted,rejected):
 rows=Path(path).read_text().splitlines();v=rows[0].split();assert int(v[4])==accepted and int(v[5])==rejected
 f=lambda x:struct.unpack('>d',bytes.fromhex(x))[0]
 vals=[f(x) for x in rows[1].split()];expect=[s.time,*s.gas,s.escape,s.redshift,s.thermal,s.source_n,s.source_u,s.absorbed]
 for x,y in zip(vals,expect):close(x,y,1.,'CHECKPOINT_GAS_LEDGER')
 assert len(vals)==len(expect);n=int(rows[4]);assert n==len(s.counts)*len(header['energy_nodes'])
 for raw,x in zip(rows[5:5+n],(x for ray in s.counts for x in ray)):
  point,lo,hi=map(f,raw.split());ledger_close(point,x,.05,'CHECKPOINT_PHOTON');assert lo<=point<=hi
 pos=5+n;assert int(rows[pos])==len(s.gn)
 for raw,gn,gu in zip(rows[pos+1:],s.gn,s.gu):
  x,u,nlo,nhi,ulo,uhi=map(f,raw.split());close(x,gn,1e-15,'CHECKPOINT_GUARD_N');close(u,gu,1e-15,'CHECKPOINT_GUARD_U');assert nlo<=x<=nhi and ulo<=u<=uhi
 assert len(rows)==pos+1+len(s.gn)
 return int(v[7])
