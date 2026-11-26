"""C3H endpoint-energy solver and nested cutoff replay (conditional, no autonomous chemistry)."""
import numpy as np,json,sys,hashlib
from pathlib import Path
from scipy.optimize import brentq
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3g_spectral_cutoff'))
from spectral_coupling import SignedKompaneets,FreeFree,candidate,birth_scaled,abundance_from_clock,P,H,G,KB,ME,C,SIG,H0
from inventory import cv,binding,thermal_pred,nested_edges,gas_residual
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(n,cut,mode,label):
 r=np.genfromtxt(H,names=True,delimiter=',');v=np.genfromtxt(P,names=True,delimiter=',');assert np.array_equal(r['a'][1:],v['a'])
 Y=abundance_from_clock(r);f=np.stack([r[k] for k in ['xHII','xHeII','xHeIII']],axis=1);cs=cv(f,Y);bs=binding(f,Y);ws=cs*r['T']
 assert np.max(abs(ws-r['thermal']))<1e-14 and np.max(abs(bs-r['binding']))<1e-14
 edges=nested_edges(n=n,cut=cut);s=SignedKompaneets(edges);ff=FreeFree(G,s);d=np.zeros(len(s.x));T=float(r['T'][0]);w=float(ws[0])
 dt=np.diff(np.log(r['a']))/(H0*np.sqrt(r['h'][1:]*r['h'][:-1]));ne=(r['ne'][1:]+r['ne'][:-1])/2*1e6
 uc=uf=nf=nc=work=wg=qext=0.;max_g=max_rad=0.;anal=0.;rows=[]
 for k,z in enumerate(v):
  a,t,tc,fraction,b,bb0,bbmid,bb1=[float(z[j]) for j in z.dtype.names];a0=r['a'][k];old=d.copy();R=a0/a;scale=bbmid*15/np.pi**4
  w_ad=thermal_pred(w,a0,a);Q=bs[k+1]-bs[k]
  if mode=='calibrated':
   # Effective legacy midpoint radiation exchange: native CMB stock includes C and FF absorption;
   # legacy FF emission is represented by birth. Aggregate accepted steps, not exact substage flux.
   legacy=(r['cmb'][k+1]-R*r['cmb'][k])/np.sqrt(R)+b
   Q=ws[k+1]-thermal_pred(ws[k],a0,a)+bs[k+1]-bs[k]+legacy
  if mode=='replay':
   temp=(r['T'][k]+r['T'][k+1])/2;clock=KB*temp/ME*C*SIG*ne[k]*dt[k]
   d,cu,fu,nn,ma=candidate(old,s,ff,temp,tc,clock,b,fraction,bbmid);T=float(r['T'][k+1]);neww=ws[k+1];res=0.
  else:
   def ev(tnew):
    temp=(T+tnew)/2;clock=KB*temp/ME*C*SIG*ne[k]*dt[k]
    d,cu,fu,nn,ma=candidate(old,s,ff,temp,tc,clock,birth_scaled(b,temp,t),fraction,bbmid)
    res=gas_residual(tnew,cs[k+1],w,bs[k],bs[k+1],a0,a,Q,cu+fu)
    return res,d,cu,fu,nn,ma,temp,clock
   pred=(w_ad+bs[k]-bs[k+1]+Q)/cs[k+1]
   if pred<=0:raise ValueError('external source produces nonpositive prediction')
   z0=max(abs(pred)*1e-4,1e-4)
   for _ in range(20):
    lo=max(1e-6,pred-z0);hi=pred+z0
    if ev(lo)[0]*ev(hi)[0]<=0:break
    z0*=2
   else:raise ValueError('unbracketed energy')
   T=brentq(lambda t:ev(t)[0],lo,hi,xtol=1e-12,rtol=1e-14)
   res,d,cu,fu,nn,ma,temp,clock=ev(T);neww=cs[k+1]*T
   max_g=max(max_g,abs(res));qext+=Q;wg+=w-w_ad
  assert min(s.f0+d/s.c)>=0
  Uold=bb0*15/np.pi**4*(s.x@old);Unew=bb1*15/np.pi**4*(s.x@d)
  wr=Uold+scale*(s.x@(d-old))-Unew;work+=wr
  max_rad=max(max_rad,abs(Unew-Uold+wr-cu-fu))
  uc+=cu;uf+=fu;nf+=nn;nc+=float((d-old).sum())-nn;anal+=4*clock*(1-tc/temp)*bbmid
  rows.append([a,T,neww,bs[k+1],Q,cu,fu,w-w_ad,wr,res])
  w=neww
  if (k+1)%160==0:print(label,k+1,T,flush=True)
 U=float(v['BB1'][-1]*15/np.pi**4*(s.x@d));rad=U+work-uc-uf;total=None if mode=='replay' else w+bs[-1]-ws[0]-bs[0]+U+wg+work-qext
 assert abs(rad)<1e-14 and (total is None or abs(total)<1e-12) and abs(nc)<1e-12*max(abs(nf),1e-30)
 out=dict(status='SCOPED_ENERGY_'+mode.upper(),n=len(s.x),parent_n=n,xmin=float(edges[0]),dlog=float(np.log(edges[1]/edges[0])),terminal_T=float(T),thermal_final=float(w),binding_change=float(bs[-1]-bs[0]),external_energy=float(qext),gas_work=float(wg),rad_work=float(work),compton=float(uc),freefree=float(uf),ff_number=float(nf),compton_number_error=float(nc),analytic_planck=float(anal),relative_compton=float(uc/anal-1),rad_residual=float(rad),total_residual=None if total is None else float(total),max_gas_residual=float(max_g),max_rad_residual=float(max_rad),source_hashes={str(p):sha(p) for p in [H,P,G]},scope='prescribed composition and expansion; binding-funded mode Qext=DeltaB; calibrated mode effective legacy midpoint source, not prediction; reflecting ends')
 np.savez_compressed(D/(label+'.npz'),edges=edges,x=s.x,delta=d,rows=np.array(rows))
 (D/(label+'.json')).write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':
 n,c,mode,label=sys.argv[1:];run(int(n),float(c),mode,label)
