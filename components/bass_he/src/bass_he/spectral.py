"""Holomorphic CF derivatives and nontrivial branch-point certification.

The matching indices select continued-fraction charts, not different equations.
Duplicate spectral roots are therefore NOT branch-point evidence.
Coulomb charges, R, p and energies use the legacy paper's atomic-unit convention.
"""
from __future__ import annotations
import hashlib, json
import numpy as np
from arseny_reimpl.term_complex import continue_complex_from_real, solve_complex_term


PAIR_MEMBERSHIP_POLICY_ID = "FINITE_CF_ADVERTISED_ORDINAL_PAIR_MEMBERSHIP_V2"


def _hex_float(x):
    x=float(x)
    if not np.isfinite(x):
        raise ValueError('finite membership binding scalar required')
    return x.hex()


def _hex_complex(z):
    z=complex(z)
    if not np.isfinite(z):
        raise ValueError('finite membership binding complex required')
    return [_hex_float(z.real), _hex_float(z.imag)]


def _pair_membership_binding(state_a,state_b,R,p,lam,*,depth,Z1,Z2,tolerance,probe_scale):
    return {
        'policy_id': PAIR_MEMBERSHIP_POLICY_ID,
        'state_a': [int(x) for x in state_a],
        'state_b': [int(x) for x in state_b],
        'R_complex128_hex': _hex_complex(R),
        'p_complex128_hex': _hex_complex(p),
        'lambda_complex128_hex': _hex_complex(lam),
        'depth': int(depth),
        'Z1_float64_hex': _hex_float(Z1),
        'Z2_float64_hex': _hex_float(Z2),
        'tolerance_float64_hex': _hex_float(tolerance),
        'probe_scale_float64_hex': _hex_float(probe_scale),
    }


def _binding_sha256(binding):
    raw=json.dumps(binding,sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(raw).hexdigest()


def validate_pair_membership_certificate(ep):
    cert=ep.get('pair_membership')
    if not isinstance(cert,dict) or not cert.get('passed',False):
        raise ValueError('certified pair membership required')
    try:
        tolerance=float(cert['tolerance']); probe_scale=float(cert['probe_scale'])
        binding=cert['binding']; actual_sha=cert['binding_sha256']
    except (KeyError,TypeError,ValueError) as exc:
        raise ValueError('pair membership certificate binding mismatch') from exc
    expected=_pair_membership_binding(
        ep['state_a'],ep['state_b'],ep['R'],ep['p'],ep['lam'],
        depth=ep['depth'],Z1=ep['Z1'],Z2=ep['Z2'],
        tolerance=tolerance,probe_scale=probe_scale)
    if binding!=expected or actual_sha!=_binding_sha256(expected):
        raise ValueError('pair membership certificate binding mismatch')
    if cert.get('claim')!=PAIR_MEMBERSHIP_POLICY_ID:
        raise ValueError('pair membership certificate binding mismatch')
    if float(cert.get('max_scaled_matching_error',np.inf))>tolerance:
        raise ValueError('pair membership certificate binding mismatch')
    perm=cert.get('permutation')
    if not isinstance(perm,list) or sorted(perm) != [0,1]:
        raise ValueError('pair membership certificate binding mismatch')
    return cert


def _coefficients(s, p, lam, R, m, Z1, Z2, radial):
    """Three coefficients and analytic derivatives ordered p, lambda, R."""
    if radial:
        a=(Z1+Z2)*R; sig=a/(2*p)-m-1
        ds=np.array([-a/(2*p*p),0,(Z1+Z2)/(2*p)],complex)
        A=(s+1)*(s+m+1)
        B=2*s*(s+2*p-sig)-(m+sig)*(m+1)-2*p*sig+lam
        C=(s-1-sig)*(s-1-m-sig)
        dA=np.zeros(3,complex)
        dB=(-2*s-m-1-2*p)*ds+np.array([4*s-2*sig,1,0],complex)
        dC=-(2*s-2-m-2*sig)*ds
    else:
        b=(Z2-Z1)*R; fac=(s+2*m+1)/(2*(s+m)+3)
        A=fac*(b-2*p*(s+m+1)); B=(s+m)*(s+m+1)-lam
        fac2=0 if s==0 else s/(2*(s+m)-1)
        C=fac2*(b+2*p*(s+m))
        dA=np.array([-2*fac*(s+m+1),0,fac*(Z2-Z1)],complex)
        dB=np.array([0,-1,0],complex)
        dC=np.array([2*fac2*(s+m),0,fac2*(Z2-Z1)],complex)
    return complex(A),complex(B),complex(C),dA,dB,dC


def _subtract_product(B, dB, A, dA, C, dC, den, dden):
    if abs(den)<1e-270: raise FloatingPointError('CF chart pole')
    ac=A*C
    return B-ac/den, dB-(dA*C+A*dC)/den+ac*dden/(den*den)


def _cf(n0, p, lam, R, m, Z1, Z2, radial, depth):
    # Coefficients are built once, avoiding repeated coefficient work in each chart.
    cs=[_coefficients(s,p,lam,R,m,Z1,Z2,radial) for s in range(depth+1)]
    low=cs[0][1]; dl=cs[0][4]
    for s in range(1,n0+1):
        Aprev=cs[s-1][0]; dAprev=cs[s-1][3]
        A,B,C,dA,dB,dC=cs[s]
        low,dl=_subtract_product(B,dB,Aprev,dAprev,C,dC,low,dl)
    high=cs[depth][1]; dh=cs[depth][4]
    for s in range(depth-1,n0,-1):
        A,B,C,dA,dB,dC=cs[s]; Cn=cs[s+1][2]; dCn=cs[s+1][5]
        high,dh=_subtract_product(B,dB,A,dA,Cn,dCn,high,dh)
    A=cs[n0][0];dA=cs[n0][3];Cn=cs[n0+1][2];dCn=cs[n0+1][5]
    return _subtract_product(low,dl,A,dA,Cn,dCn,high,dh)


def spectral_system(state,R,p,lam,*,Z1=1.,Z2=2.,depth=96):
    N,l,m=state
    if not(1<=N and 0<=m<=l<N) or depth<=max(N-l-1,l-m)+4:
        raise ValueError('invalid state or continued-fraction depth')
    if Z1==Z2: raise NotImplementedError('asymmetric recurrence only')
    if not all(np.isfinite(x) for x in [p,lam,R,Z1,Z2]) or abs(p)==0 or abs(R)==0:
        raise ValueError('finite nonzero p and R required')
    r,dr=_cf(N-l-1,complex(p),complex(lam),complex(R),m,Z1,Z2,True,depth)
    a,da=_cf(l-m,complex(p),complex(lam),complex(R),m,Z1,Z2,False,depth)
    return np.array([r,a]),np.array([dr,da])


def spectral_certificate(state,R,p,lam,*,depth=96,Z1=1.,Z2=2.,rank_tol=1e-7):
    F,J=spectral_system(state,R,p,lam,depth=depth,Z1=Z1,Z2=Z2)
    u,s,vh=np.linalg.svd(J[:,:2]); ratio=float(s[-1]/s[0]); res=float(max(abs(F)))
    # A fold also needs nonzero left-null projections on F_R and F_zz[v,v].
    direction=vh.conj().T[:,-1]; left=u[:,-1].conj()
    h=2e-4; z=np.array([p,lam],complex)
    fp=spectral_system(state,R,*(z+h*direction),depth=depth,Z1=Z1,Z2=Z2)[0]
    fm=spectral_system(state,R,*(z-h*direction),depth=depth,Z1=Z1,Z2=Z2)[0]
    curvature=left@((fp-2*F+fm)/(h*h)); trans=left@J[:,2]
    return dict(residual=res,sigma_min_over_max=ratio,
                singular=bool(res<1e-8 and ratio<rank_tol),
                transversality=complex(trans),curvature=complex(curvature),
                simple_fold=bool(res<1e-8 and ratio<rank_tol and abs(trans)>1e-7 and abs(curvature)>1e-7))


def _pair_membership_certificate(state_a,state_b,R,p,lam,*,depth,Z1,Z2,
                                 tolerance=5e-6,probe_scale=1e-4):
    """Verify that the advertised ordinal states are the two local sheets.

    A simple fold of ``state_a`` is not sufficient to identify which second
    physical/ordinal state meets it.  We therefore compare two independently
    continued named states with the two square-root local roots generated from
    the fold null direction at a small positive-real displacement from the
    candidate.  The comparison is permutation-invariant in scaled ``(p,lambda)``
    space and fails closed when either advertised state approaches a different
    regular root.

    This is a finite-CF numerical membership certificate, not a proof about all
    possible branches of the exact two-centre spectrum.
    """
    if not np.isfinite(tolerance) or tolerance<=0:
        raise ValueError('positive finite pair-membership tolerance required')
    if not np.isfinite(probe_scale) or probe_scale<=0:
        raise ValueError('positive finite pair-membership probe_scale required')
    center=complex(R);zc=np.array([p,lam],complex)
    F,J=spectral_system(state_a,center,*zc,depth=depth,Z1=Z1,Z2=Z2)
    u,s,vh=np.linalg.svd(J[:,:2]);null=vh.conj().T[:,-1];left=u[:,-1].conj()
    h=2e-4
    fp=spectral_system(state_a,center,*(zc+h*null),depth=depth,Z1=Z1,Z2=Z2)[0]
    fm=spectral_system(state_a,center,*(zc-h*null),depth=depth,Z1=Z1,Z2=Z2)[0]
    curvature=left@((fp-2*F+fm)/(h*h));trans=left@J[:,2]
    if abs(curvature)<=1e-12 or abs(trans)<=1e-12:
        raise RuntimeError('pair membership cannot resolve degenerate fold geometry')
    radius=float(probe_scale*max(1.,abs(center)))
    probe=center+radius
    amp=np.sqrt(-2*trans*radius/curvature)

    def local_root(seed):
        q=solve_complex_term(state_a,probe,p0=seed[0],lam0=seed[1],depth=depth,
                             tol=2e-12,Z1=Z1,Z2=Z2)
        return np.array([q.p,q.separation_lambda],complex)

    local=(local_root(zc+amp*null),local_root(zc-amp*null))
    named=[]
    for state in (state_a,state_b):
        q=continue_complex_from_real(state,probe,depth=depth,tol=2e-11,Z1=Z1,Z2=Z2)
        named.append(np.array([q.p,q.separation_lambda],complex))
    scale=np.maximum(1.,np.maximum(abs(zc),np.maximum(abs(local[0]),abs(local[1]))))
    def distance(x,y):return float(np.linalg.norm((x-y)/scale))
    d=np.array([[distance(named[i],local[j]) for j in range(2)] for i in range(2)])
    options=((max(d[0,0],d[1,1]),d[0,0]+d[1,1],(0,1)),
             (max(d[0,1],d[1,0]),d[0,1]+d[1,0],(1,0)))
    best=min(options,key=lambda x:(x[0],x[1]))
    binding=_pair_membership_binding(state_a,state_b,R,p,lam,depth=depth,Z1=Z1,Z2=Z2,
                                    tolerance=tolerance,probe_scale=probe_scale)
    return dict(passed=bool(best[0] <= tolerance),
                tolerance=float(tolerance),probe_scale=float(probe_scale),probe_radius=radius,
                probe_R=probe,max_scaled_matching_error=float(best[0]),
                sum_scaled_matching_error=float(best[1]),permutation=list(best[2]),
                scaled_distance_matrix=d.tolist(),local_sheet_gap=float(np.linalg.norm(local[0]-local[1])),
                binding=binding,binding_sha256=_binding_sha256(binding),
                claim=PAIR_MEMBERSHIP_POLICY_ID)


def find_exceptional_point(state_a,state_b,R_seed,*,depth=96,Z1=1.,Z2=2.,tol=2e-11):
    if state_a[2]!=state_b[2]: raise ValueError('different m cannot coalesce in this model')
    # Nearby independently continued sheets give a seed, never a certificate.
    Rs=complex(R_seed); near=complex(Rs.real,.9*Rs.imag)
    a=continue_complex_from_real(state_a,near,depth=depth,tol=1e-10,Z1=Z1,Z2=Z2)
    b=continue_complex_from_real(state_b,near,depth=depth,tol=1e-10,Z1=Z1,Z2=Z2)
    z=np.array([(a.p+b.p)/2,(a.separation_lambda+b.separation_lambda)/2,Rs],complex)
    F,J=spectral_system(state_a,z[2],z[0],z[1],depth=depth,Z1=Z1,Z2=Z2)
    scale=np.array([max(1,abs(F[0])),max(1,abs(F[1])),max(1,np.linalg.norm(J[:,:2])**2)])
    def fun(x):
        f,j=spectral_system(state_a,x[2],x[0],x[1],depth=depth,Z1=Z1,Z2=Z2)
        return np.array([f[0],f[1],np.linalg.det(j[:,:2])])/scale
    for it in range(35):
        f=fun(z)
        if max(abs(f))<tol:break
        jac=np.empty((3,3),complex)
        for k in range(3):
            h=2e-6*max(1,abs(z[k])); e=np.zeros(3,complex);e[k]=h
            jac[:,k]=(fun(z+e)-fun(z-e))/(2*h)
        dz=np.linalg.solve(jac,-f)
        for n in range(24):
            candidate=z+2.**(-n)*dz
            try:fn=fun(candidate)
            except (ValueError,FloatingPointError):continue
            if max(abs(fn))<max(abs(f)):z=candidate;break
        else:raise RuntimeError('discriminant Newton failed to improve')
    else:raise RuntimeError('discriminant Newton iteration budget exhausted')
    cert=spectral_certificate(state_a,z[2],z[0],z[1],depth=depth,Z1=Z1,Z2=Z2)
    if not cert['simple_fold']:raise RuntimeError(f'branch candidate not a simple fold: {cert}')
    membership=_pair_membership_certificate(state_a,state_b,z[2],z[0],z[1],depth=depth,Z1=Z1,Z2=Z2)
    if not membership['passed']:
        raise RuntimeError(f'pair membership rejected advertised states: {membership}')
    return dict(state_a=tuple(state_a),state_b=tuple(state_b),R=z[2],p=z[0],lam=z[1],
                depth=int(depth),Z1=Z1,Z2=Z2,certificate=cert,pair_membership=membership,
                iterations=it+1,status='SPECTRAL_SIMPLE_FOLD_PAIR_MEMBERSHIP_CERTIFIED_NOT_YET_MONODROMY_CHECKED')


def monodromy(ep,*,radius=.01,steps=96):
    """One loop must swap and two loops restore distinct local sheets."""
    if radius<=0 or steps<24:raise ValueError('positive radius and >=24 steps required')
    state=ep['state_a']; center=ep['R'];depth=ep['depth'];Z1=ep['Z1'];Z2=ep['Z2']
    zc=np.array([ep['p'],ep['lam']],complex)
    _,J=spectral_system(state,center,*zc,depth=depth,Z1=Z1,Z2=Z2)
    u,s,vh=np.linalg.svd(J[:,:2]); null=vh.conj().T[:,-1];left=u[:,-1].conj()
    h=2e-4
    F=spectral_system(state,center,*zc,depth=depth,Z1=Z1,Z2=Z2)[0]
    fp=spectral_system(state,center,*(zc+h*null),depth=depth,Z1=Z1,Z2=Z2)[0]
    fm=spectral_system(state,center,*(zc-h*null),depth=depth,Z1=Z1,Z2=Z2)[0]
    curvature=left@((fp-2*F+fm)/h**2);trans=left@J[:,2]
    amp=np.sqrt(-2*trans*radius/curvature)
    def solve(R,z):
        p=solve_complex_term(state,R,p0=z[0],lam0=z[1],depth=depth,tol=2e-12,Z1=Z1,Z2=Z2)
        return np.array([p.p,p.separation_lambda])
    za=solve(center+radius,zc+amp*null);zb=solve(center+radius,zc-amp*null)
    a0=za.copy();b0=zb.copy();gap0=float(np.linalg.norm(a0-b0));mingap=gap0
    if gap0<1e-6:raise RuntimeError('monodromy starts on duplicate sheets')
    swap=None
    for k in range(1,2*steps+1):
        R=center+radius*np.exp(2j*np.pi*k/steps)
        za=solve(R,za);zb=solve(R,zb)
        mingap=min(mingap,float(np.linalg.norm(za-zb)))
        if k==steps:swap=float(max(np.linalg.norm(za-b0),np.linalg.norm(zb-a0))/gap0)
    ret=float(max(np.linalg.norm(za-a0),np.linalg.norm(zb-b0))/gap0)
    return dict(one_loop_swap_relative_error=swap,two_loop_return_relative_error=ret,
                minimum_distinct_sheet_gap=mingap,radius=radius,steps_per_loop=steps,
                passed=bool(swap<2e-6 and ret<2e-6 and mingap>1e-6))
