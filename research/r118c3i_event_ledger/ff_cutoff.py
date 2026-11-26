"""Low-frequency Gaunt-table valid FF emission/effective absorption, same spacing."""
import sys,numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3g_spectral_cutoff'))
from spectral_coupling import SignedKompaneets,FreeFree,P,H,G,KB,ME,C,SIG,H0
def grid(target,n=8192):
 base=np.geomspace(1e-10,60.,n+1);h=np.log(base[1]/base[0])
 k=max(0,int(np.floor(np.log(base[0]/target)/h)))
 return np.r_[base[0]*np.exp(-h*np.arange(k,0,-1)),base]
def ff_step(s,ff,d,t,tc,frac,birth,bb):
 x=s.x;v=x*tc/t;scale=bb*15/np.pi**4
 amp=birth*tc/t*ff.g(v,t,frac)*np.diff(s.edges)/ff.norm(t,frac)
 tau=amp*(-np.expm1(-v))/(scale*x*s.c)
 fe=1/np.expm1(v);inc=(s.c*(fe-s.f0)-d)*(-np.expm1(-tau));dn=d+inc
 # spontaneous emission, effective absorption (including stimulated-emission correction).
 gross=s.c*tau*fe;absorb=gross-inc
 if np.min(absorb)<-1e-15*np.max(gross) or np.min(s.f0+dn/s.c)<0:raise ValueError('FF domain')
 return dn,inc,gross,absorb,tau
def run(cut,label):
 r=np.genfromtxt(H,names=True,delimiter=',');v=np.genfromtxt(P,names=True,delimiter=',');assert np.array_equal(r['a'][1:],v['a'])
 edges=grid(cut);s=SignedKompaneets(edges);ff=FreeFree(G,s);d=np.zeros(len(s.x));dt=np.diff(np.log(r['a']))/(H0*np.sqrt(r['h'][1:]*r['h'][:-1]));ne=(r['ne'][1:]+r['ne'][:-1])/2*1e6;th=(r['T'][1:]+r['T'][:-1])/2
 net=em=ab=energy=ge=ae=cu=0.;max_tau=0.;min_u=np.inf
 for k,z in enumerate(v):
  a,t,tc,frac,birth,bb0,bbmid,bb1=[float(z[j]) for j in z.dtype.names];temp=th[k];clock=KB*temp/ME*C*SIG*ne[k]*dt[k];sc=bbmid*15/np.pi**4
  d,c1=s.advance(d,temp/tc,clock/2);d,inc,gross,absorb,tau=ff_step(s,ff,d,t,tc,frac,birth,bbmid);d,c2=s.advance(d,temp/tc,clock/2)
  net+=inc.sum();em+=gross.sum();ab+=absorb.sum();energy+=sc*(s.x@inc);ge+=sc*(s.x@gross);ae+=sc*(s.x@absorb);cu+=(c1+c2)*sc;max_tau=max(max_tau,np.max(tau));min_u=min(min_u,np.min(s.x*tc/t))
 assert abs(em-ab-net)<1e-12*max(abs(em),abs(ab),1e-30) and abs(ge-ae-energy)<1e-12*max(abs(ge),abs(ae),1e-30)
 out=dict(status='SCOPED_FF_EFFECTIVE_ABSORPTION',n=len(s.x),xmin=float(edges[0]),min_gaunt_u=float(min_u),gross_emission_number=float(em),effective_absorption_number=float(ab),net_number=float(net),gross_energy=float(ge),absorbed_energy=float(ae),net_energy=float(energy),compton_energy=float(cu),max_tau=float(max_tau),number_closure=float(em-ab-net),energy_closure=float(ge-ae-energy),scope='fixed accepted thermal history, Gaunt table valid interval, reflecting Compton ends; effective absorption not total microscopic stimulated/absorption count; no plasma cutoff or x=0 claim')
 np.savez_compressed(D/(label+'.npz'),edges=edges,delta=d,x=s.x)
 (D/(label+'.json')).write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run(float(sys.argv[1]),sys.argv[2])
