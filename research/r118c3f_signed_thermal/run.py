import numpy as np,json,hashlib
from pathlib import Path
from scipy.optimize import brentq
from signed import SignedKompaneets,FreeFree
D=Path(__file__).resolve().parent;P=D.parent/'r118c3c_spectral_exchange/table_stages.csv';H=Path('/home/cosmosapjw/Downloads/bass_r118c3b_table/history.csv');G=D.parent/'r118c3b_ff_balance/gauntff.dat'
v=np.genfromtxt(P,names=True,delimiter=',');r=np.genfromtxt(H,names=True,delimiter=',')
assert len(v)==len(r)-1 and np.array_equal(v['a'],r['a'][1:])
kb=8.617333262145e-5;me=510998.9499961642;c=299792458.;sig=6.6524587051e-29;H0=2.1842852410855023e-18
dt=np.diff(np.log(r['a']))/(H0*np.sqrt(r['h'][1:]*r['h'][:-1]))
ne=(r['ne'][1:]+r['ne'][:-1])/2*1e6
th=(r['T'][1:]+r['T'][:-1])/2
clock=kb*th/me*c*sig*ne*dt
rows=[];closed=[]
for n in (128,256,512,1024):
 s=SignedKompaneets(np.geomspace(1e-10,60,n+1));ff=FreeFree(G,s)
 d=np.zeros(n);uc=uf=work=nc=nf=0.;anal=0.;max_tau=0.;resid=0.
 for k,z in enumerate(v):
    a,t,tc,f,b,bb0,bbmid,bb1=[float(z[j]) for j in z.dtype.names]
    scale=bbmid*15/np.pi**4;old=d.copy()
    d,du=s.advance(d,th[k]/tc,clock[k]/2);cu=du*scale
    d,du,nn,ma=ff.advance(d,t,tc,f,b,bbmid);fu=du;nf+=nn;max_tau=max(max_tau,ma)
    d,du=s.advance(d,th[k]/tc,clock[k]/2);cu+=du*scale
    nc+=float((d-old).sum())-nn;uc+=cu;uf+=fu
    work+=(bb0*(s.x@old)+bbmid*(s.x@(d-old))-bb1*(s.x@d))*15/np.pi**4
    resid=max(resid,abs(scale*(s.x@(d-old))-cu-fu))
    anal+=4*clock[k]*(1-tc/th[k])*bbmid
 U=float(v['BB1'][-1]*15/np.pi**4*(s.x@d))
 row=dict(n=n,stages=len(v),thermal_clock=float(clock.sum()),compton_energy=uc,ff_energy=uf,terminal=U,work=float(work),ledger=float(U+work-uc-uf),max_stage_ledger=resid,analytic_planck=anal,relative_compton=uc/anal-1,compton_number_error=nc,ff_number=nf,total_delta_number=float(d.sum()),max_tau=max_tau)
 assert abs(row['ledger'])<1e-15 and abs(nc)<1e-12*max(abs(nf),1e-30)
 rows.append(row);print(row,flush=True)
 if n==1024:np.savez_compressed(D/'SPECTRUM.npz',x=s.x,delta=d,c=s.c)
 for t0 in (float(r['T'][0]),100.):
    z=v[0];tc=float(z['Tcmb']);bb=float(z['BBmid']);frac=float(z['z2frac']);b0=float(z['birth'])
    cv=1.5*kb*(1+.245/(4*(1-.245))+float(r['xHII'][0]))
    def calc(t):
      y=kb*t/me*c*sig*ne[0]*dt[0];delta=np.zeros(n);delta,cu=s.advance(delta,t/tc,y/2)
      b=b0*np.sqrt(t/float(z['T']))*(1.1+.34*np.exp(-(5.5-np.log10(t))**2/3))/(1.1+.34*np.exp(-(5.5-np.log10(float(z['T'])))**2/3))
      delta,fu,_,_=ff.advance(delta,t,tc,frac,b,bb);delta,cu2=s.advance(delta,t/tc,y/2)
      return (cu+cu2)*bb*15/np.pi**4,fu
    def fun(t):return cv*(t-t0)+sum(calc(t))
    t=brentq(fun,min(t0,tc),max(t0,tc),xtol=1e-13);cu,fu=calc(t);res=fun(t)
    closed.append(dict(n=n,T0=t0,T=t,deltaT=t-t0,gas_energy=cv*(t-t0),compton=cu,freefree=fu,residual=res))
    assert abs(res)<1e-14
    print(closed[-1],flush=True)
out=dict(status='SCOPED_SIGNED_COMPTON_FF_ACTUAL_CLOCK',rows=rows,closed=closed,source_hashes={str(P):hashlib.sha256(P.read_bytes()).hexdigest(),str(H):hashlib.sha256(H.read_bytes()).hexdigest(),str(G):hashlib.sha256(G.read_bytes()).hexdigest()},scope='actual C3B gas and electron history replay, fixed-composition closed cell with physical Cv; not live coupled chemistry; finite reflecting Compton boundary')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
