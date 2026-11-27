"""Cross-check compiled direct canonical kernel against prior Python weak oracle.
Independent manufactured nonzero signed state on actual terminal geometry.
"""
import sys,numpy as np,json
from pathlib import Path
from numpy.polynomial.legendre import leggauss
from numpy.polynomial.hermite import hermgauss
from scipy.constants import k,m_e,c
D=Path(__file__).resolve().parent
from replay import Owner,ray,raygrid,T
from collision import library
sys.path.insert(0,str(D.parent/'r118c3t_cell_moments'))
from direct_dg import rhs as oracle
from positive import Cell
def run():
 z=np.load(D/'replay_1024.npz');F=z['F'];h=np.genfromtxt(D/'birth_1024_32ray/history.csv',names=True,delimiter=',');n,w0=raygrid(2);d,nl,w,_=ray(F,n,w0)
 e=np.geomspace(.08,3.1,33,dtype=T);o=Owner(e,n,w0)
 a=.01*(3*n[:,2,None]**2-1)*np.exp(-np.log(o.c)**2)[None,:];b=.002*n[:,0,None]*np.cos(np.log(o.c))[None,:]
 N=o.M0*a+o.M1*b;V=o.h*(o.M1*a+o.M2*b);A,B,margin=o.coefficients(N,V);assert margin>0 and np.max(abs(A-a))<1e-15 and np.max(abs(B-b))<1e-15
 delta,ref=o.occupation(N,V,d,w);ed=np.log([.1,3.]);th=k*h['T'][-1]/(m_e*c*c);tr=h['T'][-1]*h['a'][-1]/2.7255
 q,v,info=oracle(ed,e,d,nl,w,th,tr,delta,ref,8,4)
 x,y=np.zeros(N.shape),np.zeros(N.shape);diag=np.zeros(6);z,wq=leggauss(4);zh,wh=hermgauss(8);wh/=np.sqrt(np.pi);ff=lambda q:np.ascontiguousarray(q,dtype=np.float64)
 rc=library()(len(d),len(e)-1,*[ff(t) for t in [e,d,nl,w,w0,A,B]],*ed,th,tr,8,ff(zh),ff(wh),4,ff(z),ff(wq),x,y,diag);assert rc==0
 norm=lambda x:float(np.sum(abs(x)))
 nr=norm(q-x)/norm(q);vr=norm(v-y)/norm(v);assert max(nr,vr)<1e-9,(nr,vr)
 # Additional positive reference test with a nontrivial exponential tilt.
 base=lambda q:q*q/np.exp(q)
 c0=Cell(np.geomspace(.1,500,129,dtype=T),base,32)
 t=np.exp(T('.3')+T('1.7')*c0.z);M=c0.B*t;f,err=c0.solve(M.sum(axis=1),c0.h*(M*c0.z).sum(axis=1));assert err<1e-12
 out=dict(N_relative=nr,V_relative=vr,compiled_N_res=float(diag[0]),compiled_U_res=float(diag[1]),nonzero_exponential_tilt_error=err,scope='manufactured signed state on actual terminal geometry, independent C3T Python direct weak oracle; not a new actual native trajectory')
 (D/'CROSSCHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run()
