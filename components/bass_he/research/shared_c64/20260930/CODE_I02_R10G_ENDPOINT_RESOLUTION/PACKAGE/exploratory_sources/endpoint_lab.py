"""Bounded isolated diagnostic. Original archived adapter is executed unchanged
except imports are replaced by explicitly transcribed dependency functions.
No BASS_HE package/scientific contour solver is imported. Not repository suite.
"""
import ast,math,hashlib,json,time
from pathlib import Path
import numpy as np
from functools import lru_cache
ROOT=Path(__file__).parent/'input'
def angular_momentum_operators(l):
    mvals=np.arange(-l,l+1,dtype=int);lp=np.zeros((len(mvals),len(mvals)),complex)
    for j,m in enumerate(mvals[:-1]):lp[j+1,j]=math.sqrt(float(l*(l+1))-m*(m+1))
    return mvals,.5*(lp+lp.conj().T),np.diag(mvals.astype(float)).astype(complex)
@lru_cache(None)
def angular_operators(l):
    m,lx,lz=angular_momentum_operators(l);ly=-1j*(lz@lx-lx@lz)
    for a in (lx,ly,lz):a.flags.writeable=False
    return lx,ly,lz
@lru_cache(None)
def molecular_x_basis(l):
    _,lx,_=angular_momentum_operators(l);w,v=np.linalg.eigh(lx)
    assert np.max(abs(w-np.arange(-l,l+1)))<5e-13
    return np.arange(-l,l+1),v
def epsilon_rotational(N,l,Z1=1.,Z2=2.):
    return 6.*Z1*Z2*(Z1+Z2)**2/(N**3*l*(l+1)*(2*l-1)*(2*l+1)*(2*l+3))
def s_sigma_boundary(l,Z1=1.,Z2=2.):return ((l+.5)**2-.5)/(Z1+Z2)
def projectile_velocity_au(E):return (2.*E/(27.07*1.836153))**.5
src=(ROOT/'inputs/R10D_coulomb_rotation.py').read_bytes()
assert hashlib.sha1(b'blob '+str(len(src)).encode()+b'\0'+src).hexdigest()=='543ff5e5c20ff2969547f03410cd30353998348c'
tree=ast.parse(src);tree.body=[x for x in tree.body if not isinstance(x,(ast.Import,ast.ImportFrom))]
exec(compile(tree,'ARCHIVED_coulomb_rotation.py','exec'),globals())

def eta_auditor(N,l,E,rho,Rcut):
    """Independent anomaly ODE derived in current loop; DOP853 diagnostic only."""
    from scipy.integrate import solve_ivp
    v=projectile_velocity_au(E);a=2/(.8*1836.153*v*v);b=math.hypot(a,rho)
    if a+b>=Rcut:return np.eye(l+1),0,0.
    bound=math.acosh((Rcut-a)/b);lx,ly,lz=angular_operators(l)
    eps=epsilon_rotational(N,l);dim=2*l+1
    def fun(s,U):
        R=a+b*math.cosh(s);H=eps*R**3/v*(lx@lx)-rho/R*lz
        return (-1j*H@U.reshape(dim,dim)).ravel()
    sol=solve_ivp(fun,(-bound,bound),np.eye(dim,dtype=complex).ravel(),method='DOP853',rtol=1e-12,atol=1e-14)
    assert sol.success
    U=sol.y[:,-1].reshape(dim,dim);V=molecular_x_basis(l)[1]
    Ps=abs(V.conj().T@U@V)**2;m=np.arange(-l,l+1)
    C=(abs(m)[None,:]==np.arange(l+1)[:,None]).astype(float)
    P=(C@Ps@C.T)/C.sum(1)[None,:]
    return P,sol.nfev,float(np.max(abs(U.conj().T@U-np.eye(dim))))

if __name__=='__main__':
    rows=[]
    for E in (.5,5.):
        a=2/(.8*1836.153*projectile_velocity_au(E)**2)
        r=a*np.array([.01,.05,.1,.25,.5,1,2,4])
        for N,l in [(2,1),(3,2)]:
            cut=author_cutoff(l)
            t=time.perf_counter();P=coulomb_rotation_batch(N,l,np.full(len(r),E),r,steps=1024,R_cut=cut)['P_abs']
            for x,p in zip(r,P):
                q,nfev,defect=eta_auditor(N,l,E,x,cut)
                rows.append(dict(E=E,N=N,l=l,rho=float(x),rho_over_a=float(x/a),offdiag_scale=float(np.max(abs(p-np.eye(l+1)))),eta_difference=float(np.max(abs(p-q))),eta_nfev=nfev,eta_unitarity=defect))
    out={'scope':'ROTATION_ONLY_NEW_LOW_RHO_DIAGNOSTICS_NO_DELTA_SOLVES','rows':rows,'max_eta_agreement':max(x['eta_difference'] for x in rows)}
    Path('/mnt/data/r10g_workspace/ENDPOINT_PROBE.json').write_text(json.dumps(out,indent=2)+'\n')
    for x in rows: print(x)
