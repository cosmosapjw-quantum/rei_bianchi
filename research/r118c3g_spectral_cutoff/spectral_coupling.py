"""Scoped spectral replay and opt-in evolving gas response; prescribed chemistry.
Existing signed pair solver and Gaunt source used unchanged."""
import numpy as np,json,hashlib,sys
from pathlib import Path
from scipy.optimize import brentq
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3f_signed_thermal'))
from signed import SignedKompaneets,FreeFree
P=D.parent/'r118c3c_spectral_exchange/table_stages.csv';H=D/'inputs/history.csv';G=D.parent/'r118c3b_ff_balance/gauntff.dat'
KB=8.617333262145e-5;ME=510998.9499961642;C=299792458.;SIG=6.6524587051e-29;H0=2.1842852410855023e-18
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def electron_fraction(hii,heii,heiii,Y):
 return hii+Y*(heii+2*heiii)
def abundance_from_clock(r):
 u=np.column_stack((r['xHII'],r['xHeII']+2*r['xHeIII']));v=r['ne']*r['a']**3
 p,_,rank,_=np.linalg.lstsq(u,v,rcond=None)
 if rank!=2 or np.min(p)<=0 or np.max(abs(u@p-v))/np.max(abs(v))>1e-12:raise ValueError('inconsistent accepted EOS clock')
 return float(p[1]/p[0])
def birth_scaled(b,t,tref):
 f=lambda x:1.1+.34*np.exp(-(5.5-np.log10(x))**2/3)
 return b*np.sqrt(t/tref)*f(t)/f(tref)
def sink_stock(delta,s,amount,scale):
 # Explicit outward cutoff transfer, including Planck baseline in the available stock.
 if amount<0 or amount>s.c[0]*s.f0[0]+delta[0]:raise ValueError('cutoff domain')
 out=np.array(delta,copy=True);out[0]-=amount
 return out,amount,scale*s.x[0]*amount
def candidate(old,s,ff,T,Tr,clock,birth,frac,bb):
 d,du=s.advance(old,T/Tr,clock/2);d,fu,nn,ma=ff.advance(d,T,Tr,frac,birth,bb)
 d,du2=s.advance(d,T/Tr,clock/2)
 return d,(du+du2)*bb*15/np.pi**4,fu,nn,ma
def run(n,xmin,mode,label):
 v=np.genfromtxt(P,names=True,delimiter=',');r=np.genfromtxt(H,names=True,delimiter=',')
 assert len(v)==len(r)-1 and np.array_equal(v['a'],r['a'][1:])
 s=SignedKompaneets(np.geomspace(xmin,60,n+1));ff=FreeFree(G,s)
 dt=np.diff(np.log(r['a']))/(H0*np.sqrt(r['h'][1:]*r['h'][:-1]));ne=(r['ne'][1:]+r['ne'][:-1])/2*1e6
 th=(r['T'][1:]+r['T'][:-1])/2;Y=abundance_from_clock(r);d=np.zeros(n);T=float(r['T'][0])
 uc=uf=work=nc=nf=anal=0.;gres=0.;resid=0.;mx=0.;rows=[]
 for k,z in enumerate(v):
  a,t,tc,f,b,bb0,bbmid,bb1=[float(z[j]) for j in z.dtype.names];scale=bbmid*15/np.pi**4;old=d.copy()
  xe=electron_fraction((r['xHII'][k]+r['xHII'][k+1])/2,(r['xHeII'][k]+r['xHeII'][k+1])/2,(r['xHeIII'][k]+r['xHeIII'][k+1])/2,Y)
  cv=1.5*KB*(1+Y+xe)
  if mode=='replay':
   temp=th[k];clock=KB*temp/ME*C*SIG*ne[k]*dt[k]
   d,cu,fu,nn,ma=candidate(old,s,ff,temp,tc,clock,b,f,bbmid)
   T=float(r['T'][k+1]);energy=0.
  elif mode=='coupled':
   pred=T*(r['a'][k]/r['a'][k+1])**2
   def evaluate(tnew):
    temp=(T+tnew)/2;clock=KB*temp/ME*C*SIG*ne[k]*dt[k]
    d,cu,fu,nn,ma=candidate(old,s,ff,temp,tc,clock,birth_scaled(b,temp,t),f,bbmid)
    return cv*(tnew-pred)+cu+fu,d,cu,fu,nn,ma,clock,temp
   # Bracket near adiabatic solution, and expand if necessary; no accepted mutation.
   w=max(1e-4,abs(pred)*1e-4);lo=max(1e-6,pred-w);hi=pred+w
   for _ in range(20):
    if evaluate(lo)[0]*evaluate(hi)[0]<=0:break
    w*=2;lo=max(1e-6,pred-w);hi=pred+w
   else:raise ValueError('unbracketed gas residual')
   new=brentq(lambda q:evaluate(q)[0],lo,hi,xtol=1e-12,rtol=1e-14)
   energy,d,cu,fu,nn,ma,clock,temp=evaluate(new);T=new;gres=max(gres,abs(energy))
  else:raise ValueError('mode')
  assert np.min(s.f0+d/s.c)>=0
  uc+=cu;uf+=fu;nf+=nn;nc+=float((d-old).sum())-nn;mx=max(mx,ma)
  work+=(bb0*(s.x@old)+bbmid*(s.x@(d-old))-bb1*(s.x@d))*15/np.pi**4
  resid=max(resid,abs(scale*(s.x@(d-old))-cu-fu));anal+=4*clock*(1-tc/temp)*bbmid
  rows.append([a,T,cu,fu,energy])
  if (k+1)%100==0:print(label,k+1,T,flush=True)
 U=float(v['BB1'][-1]*15/np.pi**4*(s.x@d));ledger=float(U+work-uc-uf)
 assert abs(ledger)<1e-14 and gres<1e-14 and abs(nc)<1e-12*max(abs(nf),1e-30)
 out=dict(status='SCOPED_ACTUAL_CLOCK_'+mode.upper(),n=n,xmin=xmin,stages=len(v),terminal_T=T,helium_number_ratio=Y,compton=uc,ff=uf,terminal=U,work=float(work),ledger=ledger,stage_residual=resid,gas_residual=gres,number_compton_error=nc,ff_number=nf,analytic_planck=anal,relative_compton=uc/anal-1,max_tau=mx,source_hashes={str(p):sha(p) for p in (P,H,G)},scope='prescribed accepted H, chemistry, ne; reflecting frequency endpoints; coupled mode adiabatic+spectral only, not production or chemistry feedback')
 np.savez_compressed(D/(label+'.npz'),x=s.x,delta=d,c=s.c,rows=np.array(rows))
 (D/(label+'.json')).write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':
 n,xmin,mode,label=sys.argv[1:];run(int(n),float(xmin),mode,label)
