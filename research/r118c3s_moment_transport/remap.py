"""Canonical packet -> local finite-cell exact N/U moment admission.
Use existing actual native control (not rejected C3P shape)."""
import numpy as np, json,sys
from pathlib import Path
from scipy.constants import k,m_e,c,h,electron_volt
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;P=D.parent/'r118c3p_live_shape';KT0=8.617333262145e-5*2.7255
sys.path.insert(0,str(D.parent/'r118c3q_finite_jump'))
from experiments import actual,table
def run():
 rows=[]
 for name in ['angular_512','angular_1024']:
  p=P/name;r=table(p,'history');a=r['a'][-1];nh0=float((p/'NORMALIZATION.txt').read_text().split('=')[1]);z=table(p,'directional')
  nr=int(z['ray'].max()+1);nq=len(z)//nr;q=z['q'].reshape(nr,nq);xx=z['x'].reshape(nr,nq);N=z['N_per_H'].reshape(nr,nq);d=xx[:,0]/q[:,0];nm=int(np.sqrt(nr/2));_,w=leggauss(nm);w=np.repeat(w/(4*nm),2*nm)/d**3;w/=w.sum()
  X=table(p,'spectrum')['x'];dl=np.log(X[1]/X[0]);y=np.log(X);ed=np.r_[y-dl/2,y[-1]+dl/2];lo=np.exp(ed[:-1]);hi=np.exp(ed[1:]);xc=X;dx=hi-lo
  tc=2.7255/a;nh=nh0*1e6/a**3;bb=8*np.pi**5*k**4*tc**4/(15*h**3*c**3*nh*electron_volt);cap=bb*a/KT0*15/np.pi**4
  NN=np.zeros((nr,len(X)),np.longdouble);UU=NN.copy();tailN=tailU=0.;tailL1=0.
  for i in range(nr):
   j=np.searchsorted(ed,np.log(xx[i]),side='right')-1;ok=(j>=0)&(j<len(X));np.add.at(NN[i],j[ok],N[i,ok]);np.add.at(UU[i],j[ok],N[i,ok]*xx[i,ok]);tailN+=N[i,~ok].sum();tailU+=np.sum(N[i,~ok]*xx[i,~ok]);tailL1+=np.sum(abs(N[i,~ok]))
  errN=float(abs(NN.sum()+tailN-N.sum()));errU=float(abs(UU.sum()+tailU-np.sum(N*xx)))
  # Exact local conditional reference moments, not cell center approximation.
  z,g=leggauss(16);Y=(ed[:-1,None]+ed[1:,None])/2+np.diff(ed)[:,None]*z/2;x=np.exp(Y);b=(x-xc[:,None])/dx[:,None];rw=1/np.expm1(x[None,:,:]/d[:,None,None]);rw*=((1/np.expm1(x))/np.einsum('i,ijk->jk',w,rw))[None,:,:];wt=cap*w[:,None,None]*x**3*np.diff(ed)[:,None]*g/2;ref=rw*wt
  R=ref.sum(axis=2).astype(np.longdouble);A=(ref*b).sum(axis=2).astype(np.longdouble);B=(ref*b*b).sum(axis=2).astype(np.longdouble)
  D1=(UU-NN*xc)/dx;det=R*B-A*A;alpha=(B*NN-A*D1)/det;beta=(R*D1-A*NN)/det
  fN=R+NN;fU=R*xc+A*dx+UU
  margin=np.minimum(fU-lo*fN,hi*fN-fU)/(R*dx)
  minmult=np.minimum(1+alpha+beta*(lo-xc)/dx,1+alpha+beta*(hi-xc)/dx)
  bad=(fN<=0)|(margin<=0);neg=minmult<=0
  out=dict(name=name,number_res=errN,energy_res_eV_H=errU*KT0/a,tail_L1=float(tailL1),negative_full_moment_cells=int(bad.sum()),negative_affine_cells=int(neg.sum()),min_cone_margin=float(margin.min()),min_affine=float(minmult.min()),bad_x_range=[float(X[np.any(bad,axis=0)].min()),float(X[np.any(bad,axis=0)].max())] if bad.any() else [],affine_x_range=[float(X[np.any(neg,axis=0)].min()),float(X[np.any(neg,axis=0)].max())] if neg.any() else [])
  rows.append(out);np.savez_compressed(D/f'{name}_remap.npz',edges=ed,N=NN,U=UU,R=R,A=A,B=B,alpha=alpha,beta=beta,bad=bad,negative_affine=neg);print(out,flush=True)
 o=dict(rows=rows,scope='actual canonical packet stock -> finite physical cell moments with conditional normalized redshifted Planck reference; exact N/U projection, not live integration')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n')
if __name__=='__main__':run()
