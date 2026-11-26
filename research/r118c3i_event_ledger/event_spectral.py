"""Accepted-event driven spectral energy replay; no thermal-history calibrated forcing."""
import sys,json,hashlib,numpy as np
from pathlib import Path
from scipy.optimize import brentq
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3g_spectral_cutoff'))
from spectral_coupling import SignedKompaneets,FreeFree,candidate,birth_scaled,abundance_from_clock,G,KB,ME,C,SIG,H0
sys.path.insert(0,str(D.parent/'r118c3h_chemistry_ledger'))
from inventory import cv,binding,thermal_pred,gas_residual,nested_edges
from event_inventory import species_events,transfer
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
CHANNELS=['RR_H','RR_HeI','RR_HeII','DR','CE_H','CE_HeI','CE_HeII']
def load(raw):
 r,e,v=[np.genfromtxt(raw/x,names=True,delimiter=',') for x in ['history.csv','event_ledger.csv','secondary_spectrum.csv']]
 assert np.array_equal(r['a'],e['a']) and np.array_equal(r['a'],v['a']) and len(r)>1
 Y=abundance_from_clock(r);f=np.stack([r[k] for k in ['xHII','xHeII','xHeIII']],axis=1)
 dif=lambda k:np.diff(e[k]);mat=lambda s:np.stack([dif(s+'_'+k) for k in ['H','HeI','HeII']],axis=1)
 dx=species_events(mat('photo'),mat('CI'),mat('RR'),dif('dr_events'),Y)
 cool=np.stack([np.diff(v[k]) for k in CHANNELS],axis=1)
 E,Q=transfer(dif('source_u'),r['J0'][:-1],r['J0'][1:],dif('photon_work'),dif('boundary_u'),cool)
 ff=np.diff(v['FF_birth']);birthT=np.divide(np.diff(v['FF_T_moment']),ff,out=(r['T'][1:]+r['T'][:-1])/2,where=ff>0)
 gas=np.diff(r['thermal']+r['binding'])+dif('thermal_work')
 native=gas-(Q+dif('cmb_input')-ff)
 assert np.max(abs(dx-np.diff(f,axis=0)))<1e-9 and np.max(abs(native))<1e-10 and np.min(E)>=-1e-14 and np.min(cool)>=-1e-14
 return r,e,v,Y,f,cool,E,Q,ff,birthT,dict(max_species_residual=float(np.max(abs(dx-np.diff(f,axis=0)))),max_native_gas_residual=float(np.max(abs(native))),sum_native_gas_residual=float(native.sum()),absorbed=float(E.sum()),non_spectral_input=float(Q.sum()),source=float(dif('source_u').sum()),cooling=cool.sum(axis=0).tolist())
def run(raw,n,label,timing="endpoint"):
 if timing not in ("endpoint","midpoint"):raise ValueError("timing")
 r,e,v,Y,f,cool,absorb,Q,ff,birthT,checks=load(raw);a=r['a'];cs=cv(f,Y);bs=binding(f,Y)
 assert np.max(abs(cs*r['T']-r['thermal']))<1e-14 and np.max(abs(bs-r['binding']))<1e-14
 s=SignedKompaneets(nested_edges(n=n));ffsolver=FreeFree(G,s);d=np.zeros(len(s.x));T=float(r['T'][0]);w=cs[0]*T;w0=w
 dt=np.diff(np.log(a))/(H0*np.sqrt(r['h'][1:]*r['h'][:-1]));ne=(r['ne'][1:]+r['ne'][:-1])*0.5e6;am=np.sqrt(a[:-1]*a[1:]);bb=v['BB_U'];fm=(f[1:]+f[:-1])/2
 frac=4*Y*fm[:,2]/(fm[:,0]+Y*fm[:,1]+4*Y*fm[:,2])
 uc=uf=wg=wr=0.;Ucool=np.zeros(7);Wcool=np.zeros(7);rows=[];max_g=0.;anal=0.;nc=0.;nf=0.
 for k in range(len(dt)):
  tc=2.7255/am[k];scale=np.sqrt(bb[k]*bb[k+1])*15/np.pi**4;old=d.copy();ratio=a[k]/a[k+1]
  w_ad=thermal_pred(w,a[k],a[k+1]);Tprev=T;R=ratio if timing=="midpoint" else 1.
  def ev(tnew):
   temp=(Tprev+tnew)/2;clock=KB*temp/ME*C*SIG*ne[k]*dt[k]
   ds,cu,fu,nn,ma=candidate(old,s,ffsolver,temp,tc,clock,birth_scaled(ff[k],temp,birthT[k]),frac[k],np.sqrt(bb[k]*bb[k+1]))
   res=cs[k+1]*tnew-w_ad-R*(Q[k]-(bs[k+1]-bs[k])-cu-fu)
   return res,ds,cu,fu,nn,ma,temp,clock
  pred=(w_ad+R*(Q[k]-(bs[k+1]-bs[k])))/cs[k+1]
  assert pred>0
  width=max(abs(pred)*1e-4,1e-4)
  for _ in range(20):
   lo=max(1e-6,pred-width);hi=pred+width
   if ev(lo)[0]*ev(hi)[0]<=0:break
   width*=2
  else:raise ValueError('unbracketed')
  Tnew=brentq(lambda x:ev(x)[0],lo,hi,xtol=1e-12,rtol=1e-14);res,d,cu,fu,nn,ma,temp,clock=ev(Tnew)
  assert abs(res)<1e-14 and min(s.f0+d/s.c)>=0
  T=Tnew;neww=cs[k+1]*T;max_g=max(max_g,abs(res));workg=w-w_ad+(1-R)*(Q[k]-(bs[k+1]-bs[k])-cu-fu)
  Uold=bb[k]*15/np.pi**4*(s.x@old);Unew=bb[k+1]*15/np.pi**4*(s.x@d);workr=Uold+scale*(s.x@(d-old))-Unew
  # Independent explicit bolometric non-FF emission stocks, isotropic midpoint redshift.
  newcool=ratio*Ucool+np.sqrt(ratio)*cool[k];workcool=Ucool+cool[k]-newcool
  Ucool=newcool;Wcool+=workcool;wg+=workg;wr+=workr;uc+=cu;uf+=fu;nf+=nn;nc+=float((d-old).sum())-nn
  anal+=4*clock*(1-tc/temp)*np.sqrt(bb[k]*bb[k+1]);rows.append([a[k+1],T,neww,bs[k+1],Q[k],cu,fu,workg,workr,res,*Ucool]);w=neww
 U=bb[-1]*15/np.pi**4*(s.x@d)
 total=w-w0+bs[-1]-bs[0]+U+r['J0'][-1]-r['J0'][0]+wg+wr+(e['photon_work'][-1]-e['photon_work'][0])+Ucool.sum()+Wcool.sum()+(e['boundary_u'][-1]-e['boundary_u'][0])-(e['source_u'][-1]-e['source_u'][0])
 assert abs(total)<1e-11 and abs(U+wr-uc-uf)<1e-14 and abs(nc)<1e-12*max(abs(nf),1e-30)
 out=dict(status='PRESCRIBED_NATIVE_EVENT_DRIVEN_SPECTRAL_GAS',n=n,stages=len(dt),timing=timing,terminal_T=T,native_T=float(r['T'][-1]),delta_T=T-float(r['T'][-1]),source_checks=checks,compton=uc,freefree=uf,analytic_planck=anal,relative_compton=uc/anal-1,global_total=float(total),max_gas_residual=max_g,rad_residual=float(U+wr-uc-uf),compton_number_error=float(nc),cooling_channels=CHANNELS,cooling_stocks=Ucool.tolist(),cooling_work=Wcool.tolist(),source_hashes={x:sha(raw/x) for x in ['history.csv','event_ledger.csv','secondary_spectrum.csv']},scope='prescribed accepted chemistry, primary stocks and event/cooling input; thermal forcing from source and primary work, NOT native thermal endpoint; separate midpoint isotropic cooling stock, not native anisotropic radiation transport; no production change')
 np.savez_compressed(D/(label+'.npz'),rows=np.array(rows),x=s.x,delta=d,edges=s.edges)
 (D/(label+'.json')).write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':
 raw,n,label,*timing=sys.argv[1:];run(Path(raw),int(n),label,*(timing or ['endpoint']))
