"""Independent audit of completed native finite-moment runs and local/canonical round trip.
Native conditional reference is piecewise angular multiplier of scalar Planck.
No inference of full angular-energy physical collision kernel from this test.
"""
import numpy as np,json,sys
from pathlib import Path
from scipy.constants import k,m_e,c,h,electron_volt
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;KT0=8.617333262145e-5*2.7255
sys.path.insert(0,str(D.parent/'r118c3r_subcell_moments'))
from weak import moments
def table(p,n):
 f=p/(n+'.csv.gz');return np.genfromtxt(f if f.exists() else p/(n+'.csv'),names=True,delimiter=',')
def reconstruct(p):
 r=table(p,'history');a=r['a'][-1];nh0=float((p/'NORMALIZATION.txt').read_text().split('=')[1]);z=table(p,'directional')
 nr=int(z['ray'].max()+1);nq=len(z)//nr;q=z['q'].reshape(nr,nq);xx=z['x'].reshape(nr,nq);N=z['N_per_H'].reshape(nr,nq);d=xx[:,0]/q[:,0];nm=int(np.sqrt(nr/2));assert 2*nm*nm==nr
 _,w=leggauss(nm);w=np.repeat(w/(4*nm),2*nm)/d**3;w/=w.sum()
 dirs=np.stack([z[k].reshape(nr,nq)[:,0] for k in ['nx','ny','nz']],axis=1)
 X=table(p,'spectrum')['x'];dl=np.log(X[1]/X[0]);y=np.log(X);ed=np.r_[y-dl/2,y[-1]+dl/2];lo=np.exp(ed[:-1]);hi=np.exp(ed[1:]);dx=hi-lo;tc=2.7255/a;nh=nh0*1e6/a**3
 bb=8*np.pi**5*k**4*tc**4/(15*h**3*c**3*nh*electron_volt);cap=bb*a/KT0*15/np.pi**4
 # Direct histogram on actual physical finite cells, retain tails separately.
 def hist(N):
  A=np.zeros((nr,len(X)),np.longdouble);B=A.copy();tails=np.zeros(2,np.longdouble)
  for i in range(nr):
   j=np.searchsorted(ed,np.log(xx[i]),side='right')-1;ok=(j>=0)&(j<len(X));np.add.at(A[i],j[ok],N[i,ok]);np.add.at(B[i],j[ok],N[i,ok]*(xx[i,ok]-X[j[ok]]));tails+=np.array([np.sum(N[i,~ok]),np.sum(N[i,~ok]*xx[i,~ok])])
  return A,B,tails
 NN,UU,tail=hist(N/cap)
 # Same reference class as native, higher-order reference moment quadrature.
 ratio=1/np.expm1(X[None,:]/d[:,None]);ratio/= (w@ratio)[None,:]
 z0,gw=leggauss(16);Y=y[:,None]+dl/2*z0;x=np.exp(Y);b=(x-X[:,None])/dx[:,None];R=ratio[:,:,None]/np.expm1(x);weight=w[:,None,None]*x**3*dl/2*gw
 rr=R*weight;m0=rr.sum(axis=2).astype(np.longdouble);m1=(rr*b).sum(axis=2).astype(np.longdouble);m2=(rr*b*b).sum(axis=2).astype(np.longdouble)
 V=UU/dx;det=m0*m2-m1*m1;aa=(m2*NN-m1*V)/det;beta=(m0*V-m1*NN)/det
 minmult=float(min((1+aa+beta*(lo-X)/dx).min(),(1+aa+beta*(hi-X)/dx).min()));assert minmult>0
 def ref(t):
  j=np.clip(np.searchsorted(ed,t,side='right')-1,0,len(X)-1);return ratio[:,j]/np.expm1(np.exp(t))
 def delta(t):
  j=np.clip(np.searchsorted(ed,t,side='right')-1,0,len(X)-1);b=(np.exp(t)-X[j])/dx[j];return ref(t)*(aa[:,j]+beta[:,j]*b)
 return r,dirs,w,X,ed,q,xx,cap,KT0/a,delta,ref,hist,minmult,float(tail[0]),float(tail[1])
def check_roundtrip(label):
 p=D/label;r,n,w,X,ed,q,xx,cap,e,delta,ref,hist,minmult,tailN,tailU=reconstruct(p);theta=k*r['T'][-1]/(m_e*c*c);tr=r['T'][-1]*r['a'][-1]/2.7255
 results={}
 for gh,gl in [(4,2),(8,4)]:
  N,U,o=moments(ed,n,w,theta,tr,delta,ref,gh,gl)
  # weak() uses geometric center; X is identical to numerical precision.
  A=N-w[:,None]*N.sum(axis=0);B=U-w[:,None]*U.sum(axis=0)
  depth=float(r['max_depth'][-1]);stock=np.zeros_like(q,dtype=np.longdouble)
  for i in range(len(w)):
   d=xx[i,0]/q[i,0];t=X/d;j=np.searchsorted(q[i],t,side='right')-1;assert min(j)>=0 and max(j)<q.shape[1]-1
   h=(A[i]*(t-q[i,j])+B[i]/d)/(q[i,j+1]-q[i,j]);np.add.at(stock[i],j,A[i]-h);np.add.at(stock[i],j+1,h)
  # Independently recover local moments, not just global sums.
  v,u,tail=hist(stock)
  nr=float(np.sum(abs(v-A))/max(np.sum(abs(A)),1e-300));ur=float(np.sum(abs(u-B))/max(np.sum(abs(B)),1e-300))
  rayN=np.sum(stock,axis=1)-A.sum(axis=1);rayU=np.sum(stock*xx,axis=1)-np.sum(A*X+B,axis=1)
  errN=float(max(abs(rayN))/max(np.sum(abs(A)),1e-300));errU=float(max(abs(rayU))/max(np.sum(abs(A*X))+np.sum(abs(B)),1e-300))
  assert max(errN,errU)<1e-10
  results[f'{gh}_{gl}']=dict(weak=o,number_zero_mean=float(abs(A.sum())),energy_zero_mean=float(abs(np.sum(A*X+B))),canonical_ray_N_relative=errN,canonical_ray_U_relative=errU,local_roundtrip_N_relative=nr,local_roundtrip_center_U_relative=ur,tail_N=float(tail[0]),tail_U=float(tail[1]),unprojected_energy_eV_H_tau=float(o['energy']*cap*e),angular_increment_L1_H=float(np.sum(abs(stock))*cap*depth))
 return dict(label=label,min_affine_ratio=minmult,input_tail_N=tailN,input_tail_U=tailU,quadrature=results,scope='one terminal-state replay; local histogram then conservative ray-global deposit, not a native stage identity. Large cellwise round-trip error means no full local moment owner certification.')
def run():
 labels=['elastic_512_8ray','moment_512_8ray','moment_1024_8ray','moment_512_18ray']
 mesh=table(D.parent/'r118c3k_metric_spectral/mode3_on2048','history')['a'];rows={};raw={}
 for label in labels:
  p=D/label;assert (p/'RETURN.txt').read_text().startswith('status=COMPLETE')
  a=table(p,'history');raw[label]=a;assert np.array_equal(a['a'],mesh) and len(a)==484 and max(a['metric'])<1.6e-4
  d=table(p,'directional');s=table(p,'shape');assert np.array_equal(d['q'],s['q'])
  E=KT0/a['a'][-1]*s['x'];N=s['N_per_H'];n=np.stack([s[j] for j in ['nx','ny','nz']],axis=1)
  U=float(N@E);P=(n.T*(N*E))@n;Pi=P-np.eye(3)*U/3
  # Actual combined ray stress and energy, excluding bolometric cooling.
  nd=d['N_per_H'];Ud=float(nd@E);Pd=(n.T*(nd*E))@n;Pid=Pd-np.eye(3)*Ud/3
  assert abs(U-a['shape_U'][-1])<1e-11*max(np.sum(abs(N*E)),1e-300)
  assert abs(N.sum()-a['shape_N'][-1])<1e-11*max(np.sum(abs(N)),1e-300)
  assert abs(Ud-a['spec'][-1])<1e-14
  sec=a['cool']+a['spec'];tr=a['secPxx']+a['secPyy']+a['secPzz'];ledger=a['primary']+a['w']+a['b']+sec-a['w'][0]-a['b'][0]-a['source']+a['thermal_work']+a['photon_work']+a['boundary']+a['secondary_work']
  assert max(abs(ledger-a['ledger']))<1e-14 and max(abs(tr-sec))<1e-14 and max(abs(a['N_dir']-a['N_source']))<1e-12
  assert min(a['canonical_min_full_ratio'])>0
  proj=table(p,'projected');assert min(proj['delta']+1/np.expm1(proj['x']))>=0
  rows[label]=dict(accepted=int(a['accepted'][-1]),rejected=int(a['rejected'][-1]),T=float(a['T'][-1]),shape_l1=float(np.sum(abs(N))),shape_U=U,shape_N=float(N.sum()),shape_Pi_norm=float(np.linalg.norm(Pi)),total_Pi_norm=float(np.linalg.norm(Pid)),total_Pi=Pid.tolist(),shape_moved=float(a['shape_moved_l1'][-1]),max_shape_number_res=float(max(a['shape_num_res'])),max_shape_energy_res=float(max(a['shape_U_res'])),max_shape_mean_res=float(max(a['shape_mean_res'])),fullhalf_abs=float(max(a['shape_fullhalf_abs'])),fullhalf_rel=float(max(a['shape_fullhalf_rel'])),ledger=float(max(abs(ledger))),trace=float(max(abs(tr-sec))),number=float(max(abs(a['N_dir']-a['N_source']))),min_canonical=float(min(a['canonical_min_full_ratio'])),metric=float(max(a['metric'])))
 a,b=raw['elastic_512_8ray'],raw['moment_512_8ray'];comp={k:float(max(abs(a[k]-b[k]))) for k in ['T','h','xHII','spec','N_dir','S0','S1','S2','S3','S4']}
 comp['total_Pi_delta']=float(np.linalg.norm(np.array(rows['elastic_512_8ray']['total_Pi'])-np.array(rows['moment_512_8ray']['total_Pi'])))
 o=dict(rows=rows,path_diff=comp,frequency_shape_L1_ratio=rows['moment_1024_8ray']['shape_l1']/rows['moment_512_8ray']['shape_l1'],angle_shape_Pi_relative=abs(rows['moment_512_18ray']['shape_Pi_norm']-rows['moment_512_8ray']['shape_Pi_norm'])/max(rows['moment_512_18ray']['shape_Pi_norm'],1e-300),scope='native shadow live finite-rate conditional angular part; scalar chemistry owns mean; no physical microscopic kernel or full paired reference evolution')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
 v={label:check_roundtrip(label) for label in ['moment_512_8ray','moment_1024_8ray','moment_512_18ray']}
 (D/'ROUNDTRIP.json').write_text(json.dumps(v,indent=2)+'\n');print('ROUNDTRIP',v,flush=True)
if __name__=='__main__':run()
