import numpy as np,math,time,json
from pathlib import Path
from endpoint_lab import angular_operators,epsilon_rotational,molecular_x_basis,projectile_velocity_au,eta_auditor

def eta_magnus(N,l,E,r,cut,steps):
 E,r=np.broadcast_arrays(np.asarray(E,float),np.asarray(r,float));E=E.ravel();r=r.ravel()
 v=np.array([projectile_velocity_au(x) for x in E]);a=2/(.8*1836.153*v*v);b=np.hypot(a,r)
 active=a+b<cut;ix=np.flatnonzero(active);dim=2*l+1
 U=np.broadcast_to(np.eye(dim,dtype=complex),(len(r),dim,dim)).copy();lx,ly,lz=angular_operators(l)
 if len(ix):
  aa=a[ix];bb=b[ix];rr=r[ix];vv=v[ix];smax=np.arccosh((cut-aa)/bb);eps=epsilon_rotational(N,l)
  m=np.arange(-l,l+1)
  for parity in (0,1):
   inds=np.flatnonzero((m-m[0])%2==parity);X=(lx@lx)[np.ix_(inds,inds)];Z=lz[np.ix_(inds,inds)]
   W=np.broadcast_to(np.eye(len(inds),dtype=complex),(len(ix),len(inds),len(inds))).copy()
   def H(y):
    R=aa+bb*np.cosh(smax*y)
    return (smax*eps*R**3/vv)[:,None,None]*X-(smax*rr/R)[:,None,None]*Z
   h=2./steps
   for k in range(steps):
    mid=-1+(k+.5)*h;d=h/(2*np.sqrt(3));H1=H(mid-d);H2=H(mid+d)
    K=.5*h*(H1+H2)+1j*np.sqrt(3)*h*h/12*(H1@H2-H2@H1)
    ev,V=np.linalg.eigh(K);W=((V*np.exp(-1j*ev)[:,None,:])@V.conj().swapaxes(-2,-1))@W
   U[ix[:,None,None],inds[None,:,None],inds[None,None,:]]=W
 V=molecular_x_basis(l)[1];ps=abs(V.conj().T@U@V)**2;m=np.arange(-l,l+1);C=(abs(m)[None,:]==np.arange(l+1)[:,None]).astype(float)
 return (C@ps@C.T)/C.sum(1)[None,None,:],U

if __name__=='__main__':
 out=[]
 for E in (.5,5.):
  a=2/(.8*1836.153*projectile_velocity_au(E)**2);r=a*np.array([.01,.05,.1,.25,.5,1,2,4])
  for N,l in [(2,1),(3,2)]:
   cut=(l+.5)**2/3
   P64,U=eta_magnus(N,l,E,r,cut,64);P128,U=eta_magnus(N,l,E,r,cut,128);P256,U=eta_magnus(N,l,E,r,cut,256)
   for x,p0,p1,p2,u in zip(r,P64,P128,P256,U):
    q,n,d=eta_auditor(N,l,E,x,cut)
    out.append(dict(E=E,N=N,l=l,rho=float(x),delta64_128=float(np.max(abs(p0-p1))),delta128_256=float(np.max(abs(p1-p2))),dopdiff=float(np.max(abs(p2-q))),unitarity=float(np.max(abs(u.conj().T@u-np.eye(2*l+1))))))
 Path('/mnt/data/r10g_workspace/ETA_PROTOTYPE.json').write_text(json.dumps(out,indent=2)+'\n')
 print('MAX128_256',max(x['delta128_256'] for x in out),'MAX_DOP',max(x['dopdiff'] for x in out),'MAX_U',max(x['unitarity'] for x in out))
 for x in out:
  if x['delta128_256']>1e-7:print(x)
