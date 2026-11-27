"""Actual C3S signed collision increment through a canonical DG two-moment owner.
Terminal snapshots only; no live trajectory or physical rate claim.
"""
import sys,json,numpy as np,importlib.util
from pathlib import Path
from scipy.constants import k,m_e,c
from numpy.polynomial.legendre import leggauss
from dg import remap,project,centers,density,check_full,update
D=Path(__file__).resolve().parent;P=D.parent/'r118c3s_moment_transport'
sp=importlib.util.spec_from_file_location('c3s_audit',P/'audit.py');prev=importlib.util.module_from_spec(sp);sp.loader.exec_module(prev)
from weak import moments
T=np.longdouble
def extended(e,k):
 e=np.array(e,dtype=T);dl=np.log(e[1]/e[0]);return np.r_[e[0]*np.exp(dl*np.arange(-k,0,dtype=T)),e,e[-1]*np.exp(dl*np.arange(1,k+1,dtype=T))]
def compare(e,N,V,d):
 # Fixed canonical grid with padding. Local and canonical V transform linearly.
 ce=extended(e,2);xe=extended(e,4);C=centers(ce);X=centers(xe);n,v=remap(e/d,N,V/d,ce)
 nr,vr=remap(ce*d,n,v*d,xe)
 z=slice(4,-4)
 errN=float(np.sum(abs(nr[z]-N))/max(np.sum(abs(N)),T('1e-300')))
 errV=float(np.sum(abs(vr[z]-V))/max(np.sum(abs(V)),T('1e-300')))
 nres=float(abs(n.sum()-N.sum())/max(np.sum(abs(N)),T('1e-300')))
 eres=float(abs(np.sum((v+C*n)*d)-np.sum(V+centers(e)*N))/max(np.sum(abs(V))+np.sum(abs(centers(e)*N)),T('1e-300')))
 tail=float(np.sum(abs(nr[:4]))+np.sum(abs(nr[-4:])))
 assert max(nres,eres)<1e-13
 return n,v,nr[z],vr[z],dict(N_rel=errN,V_rel=errV,N_res=nres,U_res=eres,tail_L1=tail)
def check_label(label):
 r,n,w,X,ed,q,xx,cap,e,delta,ref,hist,minmult,tailN,tailU=prev.reconstruct(P/label)
 E=np.exp(ed.astype(T));xc=centers(E);ng=np.exp((ed[:-1]+ed[1:])/2);theta=k*r['T'][-1]/(m_e*c*c);tr=r['T'][-1]*r['a'][-1]/2.7255
 N,U,info=moments(ed,n,w,theta,tr,delta,ref,8,4)
 A=N-w[:,None]*N.sum(axis=0);B=U-w[:,None]*U.sum(axis=0)+(ng-xc)*A
 # actual input moment histogram from C3S representation, exact signed N and U.
 dc=xx[:,0]/q[:,0];res=[];CN=[];CV=[];RN=[];RV=[];baseN=[];baseV=[];refN=[];refV=[];badref=badfull=0;min_ratio=1.
 for i,d in enumerate(dc):
  n0,v0=project(E,lambda x:w[i]*x*x*delta(np.log(x).astype(float).ravel())[i].reshape(x.shape),16)
  r0,s0=project(E,lambda x:w[i]*x*x*ref(np.log(x).astype(float).ravel())[i].reshape(x.shape),16)
  baseN.append(n0);baseV.append(v0);refN.append(r0);refV.append(s0)
  cn,cv,an,bn,diag=compare(E,A[i],B[i],T(d));CN.append(cn);CV.append(cv);RN.append(an);RV.append(bn);res.append(diag)
  # Full affine density need not be positive for a steep Planck tail.
  badref+=int(np.count_nonzero((r0<0)|(abs(s0)>r0*np.diff(E)/6)))
  dt=T(r['max_depth'][-1]);badfull+=int(np.count_nonzero((r0+n0+dt*an<0)|(abs(s0+v0+dt*bn)>(r0+n0+dt*an)*np.diff(E)/6)))
  z,g=leggauss(8);test=np.r_[E, (xc[:,None]+np.diff(E)[:,None]*z/2).ravel()];rv=w[i]*test*test*ref(np.log(test).astype(float))[i];sv=density(E,n0+dt*an,v0+dt*bn,test)
  min_ratio=min(min_ratio,float(min((rv+sv)/rv)))
 # aggregate error by absolute signed L1 rather than average of relative errors
 RN,RV=np.array(RN),np.array(RV);CN,CV=np.array(CN),np.array(CV)
 errN=float(np.sum(abs(RN-A))/np.sum(abs(A)));errV=float(np.sum(abs(RV-B))/np.sum(abs(B)))
 # compare original geometric-centered moment too, directly comparable to C3S.
 Vgeom=RV+(xc-ng)*RN;orig=U-w[:,None]*U.sum(axis=0)
 geo=float(np.sum(abs(Vgeom-orig))/np.sum(abs(orig)))
 old=json.loads((P/'ROUNDTRIP.json').read_text())[label]['quadrature']['8_4']
 out=dict(label=label,N_roundtrip=errN,V_roundtrip=errV,geometric_V_roundtrip=geo,old_nodal_N=old['local_roundtrip_N_relative'],old_nodal_V=old['local_roundtrip_center_U_relative'],max_global_N_res=max(a['N_res'] for a in res),max_global_U_res=max(a['U_res'] for a in res),bad_reference_affine=badref,bad_full_affine=badfull,min_sampled_full_ratio=min_ratio,raw_pair_energy_eV_H_tau=float(info['energy']*cap*e),shift_fraction_range=[float(min(abs(np.log(dc)))/np.diff(ed)[0]),float(max(abs(np.log(dc)))/np.diff(ed)[0])],scope='actual terminal replay; affine signed density projected between shifted grids, full reference separately sampled. Not native live.')
 np.savez_compressed(D/(label+'_dg.npz'),edges=E,local_N=A,local_V=B,canonical_N=CN,canonical_V=CV,returned_N=RN,returned_V=RV,base_N=np.array(baseN),base_V=np.array(baseV),ref_N=np.array(refN),ref_V=np.array(refV),d=dc)
 print(out,flush=True);return out
def run():
 rows=[check_label(l) for l in ['moment_512_8ray','moment_1024_8ray','moment_512_18ray']]
 (D/'ACTUAL_DG.json').write_text(json.dumps(dict(rows=rows,scope='global ray N/U exact, local shifted projection residual measured; no live promotion if positivity or local transport fails'),indent=2)+'\n')
if __name__=='__main__':run()
