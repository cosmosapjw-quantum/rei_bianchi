"""Certified endpoints, coupled sheet tracking, regularized quadrature and durable caches."""
from __future__ import annotations
import hashlib,json,os,tempfile,fcntl
from pathlib import Path
import numpy as np
from arseny_reimpl.term_complex import continue_complex_from_real
from .spectral import spectral_system


def _energy(z,R):return -2*z[0]*z[0]/(R*R)


def _newton(state,R,z,ep,tol=2e-11):
    x=z.copy()
    for _ in range(24):
        f,j=spectral_system(state,R,*x,depth=ep['depth'],Z1=ep['Z1'],Z2=ep['Z2'])
        if max(abs(f))<tol:return x,float(max(abs(f)))
        dz=np.linalg.solve(j[:,:2],-f)
        for k in range(16):
            trial=x+2.**(-k)*dz
            fn=spectral_system(state,R,*trial,depth=ep['depth'],Z1=ep['Z1'],Z2=ep['Z2'])[0]
            if max(abs(fn))<max(abs(f)):x=trial;break
        else:raise RuntimeError('spectral Newton failed')
    raise RuntimeError('spectral Newton budget exhausted')


def _advance_pair(R0,za,zb,R1,ep,stats,level=0):
    if level>16:raise RuntimeError('sheet-tracking refinement budget exhausted')
    try:
        solutions=[];residuals=[]
        for state,z in [(ep['state_a'],za),(ep['state_b'],zb)]:
            _,j=spectral_system(state,R0,*z,depth=ep['depth'],Z1=ep['Z1'],Z2=ep['Z2'])
            predicted=z-np.linalg.solve(j[:,:2],j[:,2])*(R1-R0)
            zn,res=_newton(state,R1,predicted,ep);solutions.append(zn);residuals.append(res)
        na,nb=solutions
        g0=_energy(zb,R0)-_energy(za,R0);g1=_energy(nb,R1)-_energy(na,R1)
        expected=g0*np.sqrt((R1-ep['R'])/(R0-ep['R']))
        ratio=g1/expected
        if not np.isfinite(ratio) or abs(ratio-1)>.65:raise RuntimeError('unresolved sheet jump or coalescence')
        stats['max_spectral_residual']=max(stats['max_spectral_residual'],*residuals)
        stats['minimum_normalized_sheet_gap']=min(stats['minimum_normalized_sheet_gap'],abs(g1)/np.sqrt(abs(R1-ep['R'])))
        stats['accepted_continuation_steps']+=1
        return na,nb
    except (RuntimeError,ValueError,FloatingPointError,np.linalg.LinAlgError):
        stats['bisected_continuation_steps']+=1
        mid=(R0+R1)/2
        ma,mb=_advance_pair(R0,za,zb,mid,ep,stats,level+1)
        return _advance_pair(mid,ma,mb,R1,ep,stats,level+1)


def contour_geometry(ep,rho,*,panels=32):
    """Eq56 geometry-only action. Simpson in regularized s, not irregular X.

    X(s)=Re Xc+i Im Xc*(2s-s²), dX/ds=2i Im Xc*(1-s).
    The simple-fold gap is O(1-s), so the transformed integrand is smooth at s=1.
    Distinct sheets are tracked and failed continuation cannot become zero action.
    This numerical solver does not establish the collision model's physical validity.
    """
    if not ep['certificate']['simple_fold']:raise ValueError('certified simple fold required')
    if not np.isfinite(rho) or rho<0 or not isinstance(panels,int) or panels<8 or panels%2:
        raise ValueError('finite rho>=0 and even panels>=8 required')
    Rc=complex(ep['R']);Xc=np.sqrt(Rc*Rc-rho*rho)
    if Xc.real<0:Xc=-Xc
    if Xc.imag<=0:raise ValueError('upper half-plane geometry required')
    x0=Xc.real;R0=complex(np.sqrt(x0*x0+rho*rho))
    states=[ep['state_a'],ep['state_b']];zs=[]
    for state in states:
        p=continue_complex_from_real(state,R0,Z1=ep['Z1'],Z2=ep['Z2'],depth=ep['depth'],tol=2e-11)
        zs.append(np.array([p.p,p.separation_lambda],complex))
    if abs(_energy(zs[0],R0)-_energy(zs[1],R0))<1e-7:
        raise RuntimeError('real anchor did not produce distinct sheets')
    stats=dict(max_spectral_residual=0.,minimum_normalized_sheet_gap=float('inf'),
               accepted_continuation_steps=0,bisected_continuation_steps=0)
    samples=[];f=[];prevR=R0
    for k in range(panels):
        s=k/panels;X=x0+1j*Xc.imag*(2*s-s*s)
        R=np.sqrt(X*X+rho*rho)
        if abs(R-prevR)>abs(-R-prevR):R=-R
        if k:zs=list(_advance_pair(prevR,zs[0],zs[1],R,ep,stats))
        gap=_energy(zs[1],R)-_energy(zs[0],R)
        f.append(gap*(2j*Xc.imag*(1-s)))
        samples.append(dict(s=s,R=R,gap=gap))
        prevR=R
    f.append(0j)
    val=(f[0]+f[-1]+4*sum(f[1:-1:2])+2*sum(f[2:-1:2]))/(3*panels)
    return dict(rho=float(rho),panels=panels,delta=float(abs(val.imag)),integral=val,
                endpoint_assumption='SIMPLE_FOLD_CERTIFICATE_REQUIRED',
                method='SIMPSON_IN_REGULARIZED_S_WITH_COUPLED_SHEET_TRACKING',
                source_model='STRAIGHT_LINE_STATIC_COULOMB_CURVES',samples=samples,**stats)


def radial_quadrature(cutoffs,*,order=2):
    """Gauss nodes in u=rho²; include every discontinuity before integrating.

    2*pi*rho*d rho = pi*d u. Returned positive weights already include pi.
    Nodes are strictly interior, so discontinuous support endpoints are not sampled.
    """
    c=np.asarray(cutoffs,float)
    if c.ndim!=1 or len(c)<2 or np.any(~np.isfinite(c)) or c[0]!=0 or np.any(np.diff(c)<=0):
        raise ValueError('cutoffs must start at 0 and strictly increase')
    if not isinstance(order,int) or order<1:raise ValueError('positive integer order required')
    x,w=np.polynomial.legendre.leggauss(order);rs=[];ws=[]
    for lo,hi in zip(c[:-1]**2,c[1:]**2):
        rs.extend(np.sqrt((hi-lo)*x/2+(hi+lo)/2));ws.extend(np.pi*(hi-lo)*w/2)
    return np.array(rs),np.array(ws)


def jsonable(x):
    if isinstance(x,complex) or isinstance(x,np.complexfloating):return {'__complex__':[float(x.real),float(x.imag)]}
    if isinstance(x,dict):return {str(k):jsonable(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [jsonable(v) for v in x]
    if isinstance(x,np.ndarray):return jsonable(x.tolist())
    if isinstance(x,np.generic):return x.item()
    return x


def unjsonable(x):
    if isinstance(x,dict):
        if set(x)=={'__complex__'}:return complex(*x['__complex__'])
        return {k:unjsonable(v) for k,v in x.items()}
    if isinstance(x,list):return [unjsonable(v) for v in x]
    return x


def _canonical(x):return json.dumps(jsonable(x),sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def atomic_json(path,obj):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(jsonable(obj),indent=2,sort_keys=True,allow_nan=False).encode()+b'\n'
    fd,tmp=tempfile.mkstemp(prefix='.'+p.name,dir=p.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)
        fd=os.open(p.parent,os.O_RDONLY)
        try:os.fsync(fd)
        finally:os.close(fd)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


class EvidenceCache:
    """Content-addressed cache. Caller must include transitive source identity in key.

    Reads verify both the key and payload hash. A tampered entry is an error, never
    silently recalculated or treated as validated. No executable serialization.
    """
    def __init__(self,root):self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
    def _path(self,key):return self.root/(hashlib.sha256(_canonical(key)).hexdigest()+'.json')
    def put(self,key,payload):
        p=self._path(key)
        # Per-key interprocess exclusion; the lock inode persists to avoid the
        # unlink/recreate split-lock race. The payload is still published atomically.
        with p.with_suffix('.lock').open('a+b') as lock:
            fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
            if p.exists():
                existing=self.get(key)
                if _canonical(existing)!=_canonical(payload):raise ValueError('immutable cache conflict')
                return
            atomic_json(p,dict(key=key,payload=payload,payload_sha256=hashlib.sha256(_canonical(payload)).hexdigest()))
    def get(self,key):
        p=self._path(key)
        if not p.exists():return None
        obj=json.loads(p.read_text());raw=obj['payload']
        if _canonical(obj['key'])!=_canonical(key) or hashlib.sha256(_canonical(raw)).hexdigest()!=obj['payload_sha256']:
            raise ValueError('cache key/payload hash mismatch')
        return unjsonable(raw)

class AdaptiveQuadratureError(RuntimeError):
    """Raised when the bounded adaptive Eq54 quadrature cannot meet its budget."""


# QUADPACK QK15 nodes/weights on [-1,1].  The 7-point Gauss nodes are the
# Kronrod entries at indices 1,3,5,7.  All physical discontinuities are split
# before this open rule is applied, so support endpoints are never sampled.
_GK15_X=np.array([
    .9914553711208126,.9491079123427585,.8648644233597691,
    .7415311855993944,.5860872354676911,.4058451513773972,
    .20778495500789847,0.0])
_GK15_WK=np.array([
    .022935322010529225,.06309209262997855,.10479001032225018,
    .14065325971552592,.1690047266392679,.19035057806478542,
    .20443294007529889,.20948214108472783])
_GK15_WG=np.array([
    .1294849661688697,.27970539148927667,.3818300505051189,
    .4179591836734694])


def _gk15_interval(evaluate,u0,u1):
    mid=.5*(u0+u1);half=.5*(u1-u0)
    # Order nodes as symmetric pairs followed by the centre.  evaluate_many is
    # deliberately vector-valued so the expensive geometry can be batched.
    us=[]
    for x in _GK15_X[:-1]:us.extend((mid-half*x,mid+half*x))
    us.append(mid)
    us=np.asarray(us,float);rhos=np.sqrt(us)
    vals=np.asarray(evaluate(rhos),float)
    if vals.ndim==1:vals=vals[:,None]
    if vals.shape[0]!=15 or np.any(~np.isfinite(vals)):
        raise ValueError('evaluate must return finite shape (n_nodes,n_components)')
    high=np.zeros(vals.shape[1]);low=np.zeros(vals.shape[1])
    # Kronrod: pair weights for the first seven abscissae plus centre.
    for j,w in enumerate(_GK15_WK[:-1]):high+=w*(vals[2*j]+vals[2*j+1])
    high+=_GK15_WK[-1]*vals[-1]
    # Gauss-7 subset: xgk indices 1,3,5 and centre index 7.
    for w,j in zip(_GK15_WG[:-1],(1,3,5)):
        high_pair=vals[2*j]+vals[2*j+1]
        low+=w*high_pair
    low+=_GK15_WG[-1]*vals[-1]
    # Eq54 after u=rho^2: 2*pi*rho drho = pi du.
    scale=np.pi*half
    return dict(u0=float(u0),u1=float(u1),high=scale*high,low=scale*low,
                error=scale*np.abs(high-low),evaluations=15)


def _gk15_nodes(u0,u1):
    mid=.5*(u0+u1);half=.5*(u1-u0);us=[]
    for x in _GK15_X[:-1]:us.extend((mid-half*x,mid+half*x))
    us.append(mid)
    return np.asarray(us,float)


def _gk15_reduce(u0,u1,vals):
    vals=np.asarray(vals,float)
    if vals.ndim==1:vals=vals[:,None]
    if vals.shape[0]!=15 or np.any(~np.isfinite(vals)):
        raise ValueError('evaluate must return finite shape (n_nodes,n_components)')
    high=np.zeros(vals.shape[1]);low=np.zeros(vals.shape[1])
    for j,w in enumerate(_GK15_WK[:-1]):high+=w*(vals[2*j]+vals[2*j+1])
    high+=_GK15_WK[-1]*vals[-1]
    for w,j in zip(_GK15_WG[:-1],(1,3,5)):low+=w*(vals[2*j]+vals[2*j+1])
    low+=_GK15_WG[-1]*vals[-1]
    scale=np.pi*.5*(u1-u0)
    return dict(u0=float(u0),u1=float(u1),high=scale*high,low=scale*low,
                error=scale*np.abs(high-low),evaluations=15)


def _gk15_batch(evaluate,specs):
    specs=list(specs)
    if not specs:return []
    nodes=[_gk15_nodes(a,b) for a,b in specs]
    all_u=np.concatenate(nodes)
    vals=np.asarray(evaluate(np.sqrt(all_u)),float)
    if vals.ndim==1:vals=vals[:,None]
    if vals.shape[0]!=len(all_u) or np.any(~np.isfinite(vals)):
        raise ValueError('evaluate must return finite shape (n_nodes,n_components)')
    return [_gk15_reduce(a,b,vals[15*i:15*(i+1)]) for i,(a,b) in enumerate(specs)]


_GK7_X=np.array([.9604912687080203,.7745966692414834,.43424374934680256,0.0])
_GK7_WK=np.array([.10465622602646727,.26848808986833344,.4013974147759622,.45091653865847414])
_GK7_WG=np.array([5./9.,8./9.])

def _gk7_nodes(u0,u1):
    mid=.5*(u0+u1);half=.5*(u1-u0);us=[]
    for x in _GK7_X[:-1]:us.extend((mid-half*x,mid+half*x))
    us.append(mid)
    return np.asarray(us,float)

def _gk7_reduce(u0,u1,vals):
    vals=np.asarray(vals,float)
    if vals.ndim==1:vals=vals[:,None]
    if vals.shape[0]!=7 or np.any(~np.isfinite(vals)):
        raise ValueError('evaluate must return finite shape (n_nodes,n_components)')
    high=np.zeros(vals.shape[1]);low=np.zeros(vals.shape[1])
    for j,w in enumerate(_GK7_WK[:-1]):high+=w*(vals[2*j]+vals[2*j+1])
    high+=_GK7_WK[-1]*vals[-1]
    low+=_GK7_WG[0]*(vals[2]+vals[3])+_GK7_WG[1]*vals[-1]
    scale=np.pi*.5*(u1-u0)
    return dict(u0=float(u0),u1=float(u1),high=scale*high,low=scale*low,
                error=scale*np.abs(high-low),evaluations=7)

def _gk7_batch(evaluate,specs):
    specs=list(specs)
    if not specs:return []
    nodes=[_gk7_nodes(a,b) for a,b in specs];all_u=np.concatenate(nodes)
    vals=np.asarray(evaluate(np.sqrt(all_u)),float)
    if vals.ndim==1:vals=vals[:,None]
    if vals.shape[0]!=len(all_u) or np.any(~np.isfinite(vals)):
        raise ValueError('evaluate must return finite shape (n_nodes,n_components)')
    return [_gk7_reduce(a,b,vals[7*i:7*(i+1)]) for i,(a,b) in enumerate(specs)]


def adaptive_seed_rhos(cutoffs,*,rule='gk15'):
    c=np.asarray(cutoffs,float)
    if c.ndim!=1 or len(c)<2 or c[0]!=0 or np.any(~np.isfinite(c)) or np.any(np.diff(c)<=0):
        raise ValueError('cutoffs must be finite, start at 0 and strictly increase')
    if rule=='gk15':node_fn=_gk15_nodes
    elif rule=='gk7':node_fn=_gk7_nodes
    else:raise ValueError("rule must be 'gk7' or 'gk15'")
    r=[]
    for a,b in zip(c[:-1],c[1:]):r.extend(np.sqrt(node_fn(a*a,b*b)).tolist())
    return np.asarray(r,float)


def adaptive_vector_quadrature(evaluate,cutoffs,*,rtol=1e-4,atol=1e-10,max_intervals=128,rule='gk15'):
    """Adaptive finite Eq54 integral with known discontinuities pre-split.

    `evaluate(rhos)` returns one or more nonnegative/finite indexed-state
    integrands *without* the cylindrical Jacobian.  Integration is performed in
    u=rho^2, for which 2*pi*rho drho = pi du.  A 7/15 Gauss-Kronrod pair gives a
    local vector error estimate.  The global stopping test is component-wise,
    never only on a summed total.

    The estimator is numerical rather than interval-rigorous.  Budget exhaustion
    is an explicit unresolved result, not silently accepted convergence.
    """
    c=np.asarray(cutoffs,float)
    if c.ndim!=1 or len(c)<2 or c[0]!=0 or np.any(~np.isfinite(c)) or np.any(np.diff(c)<=0):
        raise ValueError('cutoffs must be finite, start at 0 and strictly increase')
    if not np.isfinite(rtol) or rtol<=0 or not np.isfinite(atol) or atol<0:
        raise ValueError('require finite rtol>0 and atol>=0')
    if not isinstance(max_intervals,int) or max_intervals<len(c)-1:
        raise ValueError('max_intervals smaller than mandatory split count')
    if rule=='gk15':batch_rule=_gk15_batch;evals_per=15;rule_name='GAUSS_KRONROD_7_15'
    elif rule=='gk7':batch_rule=_gk7_batch;evals_per=7;rule_name='GAUSS_KRONROD_3_7'
    else:raise ValueError("rule must be 'gk7' or 'gk15'")
    intervals=batch_rule(evaluate,[(a*a,b*b) for a,b in zip(c[:-1],c[1:])])
    neval=evals_per*len(intervals);refinements=0
    while True:
        total=sum((x['high'] for x in intervals),np.zeros_like(intervals[0]['high']))
        err=sum((x['error'] for x in intervals),np.zeros_like(total))
        tol=atol+rtol*np.abs(total)
        if np.all(err<=tol):
            return dict(integral=total,component_error_estimate=err,component_tolerance=tol,
                        converged=True,interval_count=len(intervals),evaluations=neval,
                        refinements=refinements,known_splits_preserved=c.tolist(),
                        method='SUPPORT_SPLIT_ADAPTIVE_'+rule_name+'_IN_U_RHO2',
                        error_claim='EMBEDDED_NUMERICAL_ESTIMATE_NOT_INTERVAL_BOUND')
        if len(intervals)>=max_intervals:
            worst=float(np.max(err/np.maximum(tol,np.finfo(float).tiny)))
            raise AdaptiveQuadratureError(f'adaptive quadrature budget exhausted; worst normalized component error={worst:.6g}')
        # Refine the interval carrying the largest normalized component error.
        denom=np.maximum(tol,np.finfo(float).tiny)
        scores=[float(np.max(x['error']/denom)) for x in intervals]
        k=int(np.argmax(scores));old=intervals.pop(k);mid=.5*(old['u0']+old['u1'])
        children=batch_rule(evaluate,[(old['u0'],mid),(mid,old['u1'])])
        intervals[k:k]=children;neval+=2*evals_per;refinements+=1
