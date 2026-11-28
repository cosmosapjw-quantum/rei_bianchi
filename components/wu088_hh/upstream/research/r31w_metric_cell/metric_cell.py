"""Research diagnostics for moving metrics. No HH kernels or propagation.

Theorems assume exact Hermitian matrices and positive-definite overlaps. These
binary64 calculations report defects and roundoff diagnostics, NOT interval
certificates. No symmetrization or repair is applied to input matrices.
"""
from __future__ import annotations
import math
from numbers import Real
import numpy as np
from scipy.linalg import eig, solve_triangular

HERMITICITY_RTOL = 1.e-12

def _number(x, name):
    if isinstance(x, (bool, np.bool_)) or not isinstance(x, Real) or not math.isfinite(x):
        raise ValueError(name+' must be a finite real number, not bool')
    return float(x)

def _matrix(x, name, shape=None, hermitian=False):
    a=np.array(x,dtype=np.complex128,copy=True)
    if a.ndim!=2 or not a.size or not np.isfinite(a).all():
        raise ValueError(name+' must be a finite nonempty matrix')
    if shape is not None and a.shape!=shape:
        raise ValueError(name+' shape mismatch')
    if hermitian:
        if a.shape[0]!=a.shape[1]:raise ValueError(name+' must be square')
        gap=float(np.linalg.norm(a-a.conj().T,2))
        if gap>HERMITICITY_RTOL*max(1.,float(np.linalg.norm(a,2))):
            raise ValueError(name+' Hermiticity prerequisite failed')
    return a

def pullback(overlap, connection, dot_overlap, frame, dot_frame):
    """Pull back O,D,dotO, including Q† O dotQ for square or rectangular Q.

Full column rank is checked numerically. A rectangular Q is a subspace
compression, NOT an invertible coordinate change or a physical admission.
"""
    o=_matrix(overlap,'O',hermitian=True)
    d=_matrix(connection,'D',shape=o.shape)
    od=_matrix(dot_overlap,'dotO',shape=o.shape,hermitian=True)
    q=_matrix(frame,'frame');qd=_matrix(dot_frame,'dot_frame',shape=q.shape)
    if q.shape[0]!=len(o) or q.shape[1]>len(o) or np.linalg.matrix_rank(q)!=q.shape[1]:
        raise ValueError('frame must have full column rank in the given space')
    oq=q.conj().T@o@q
    dq=q.conj().T@d@q+q.conj().T@o@qd
    odq=qd.conj().T@o@q+q.conj().T@od@q+q.conj().T@o@qd
    return {'O':oq,'D':dq,'dotO':odq,'R':odq-dq-dq.conj().T}

def diagnose(overlap, residual):
    """SVD diagnostic and signed Rayleigh witness, with numerical gaps exposed.

General eig (not eigh) avoids silently imposing Hermiticity on R. Cholesky's
reconstruction gap for the actual supplied O is reported explicitly.
"""
    o=_matrix(overlap,'O',hermitian=True)
    r=_matrix(residual,'R',shape=o.shape,hermitian=True)
    try:c=np.linalg.cholesky(o).conj().T
    except np.linalg.LinAlgError as exc:raise ValueError('positive-definite O required') from exc
    w=solve_triangular(c,np.eye(len(c)),lower=False)
    e=w.conj().T@r@w
    vals,vecs=eig(e)
    eta=float(np.linalg.norm(e,2))
    j=int(np.argmax(np.abs(vals.real)));x=w@vecs[:,j]
    norm=np.vdot(x,o@x)
    if norm.real<=0 or abs(norm.imag)>1.e-10*max(1.,norm.real):
        raise ValueError('invalid metric witness norm')
    x=x/math.sqrt(float(norm.real)); n=np.vdot(x,o@x);rho=np.vdot(x,r@x)/n
    den=np.linalg.norm(r,2)*np.linalg.norm(x)+abs(rho)*np.linalg.norm(o,2)*np.linalg.norm(x)
    residual_norm=float(np.linalg.norm(r@x-rho*(o@x)))
    return {'eta_svd':eta,'lambda_min_real':float(min(vals.real)),
        'lambda_max_real':float(max(vals.real)),
        'max_eigenvalue_imag':float(max(abs(vals.imag))),
        'witness_rate':float(rho.real),'witness_rate_imag':float(rho.imag),
        'witness_norm':float(n.real),'witness_norm_imag':float(n.imag),
        'witness_vector_real':x.real.tolist(),'witness_vector_imag':x.imag.tolist(),
        'witness_eigen_residual':residual_norm,
        'witness_relative_eigen_residual':residual_norm/float(den) if den else 0.,
        'overlap_hermiticity_gap':float(np.linalg.norm(o-o.conj().T,2)),
        'residual_hermiticity_gap':float(np.linalg.norm(r-r.conj().T,2)),
        'cholesky_reconstruction_gap':float(np.linalg.norm(c.conj().T@c-o,2)),
        'whitened_hermiticity_gap':float(np.linalg.norm(e-e.conj().T,2)),
        'certified':False,'scope':'BINARY64_REPRESENTED_MATRIX_DIAGNOSTIC',
        'time_unit':'caller supplied time unit; rates are inverse time'}

def affine_endpoint_diagnostic(o0,o1,d0,d1,delta_time):
    """Endpoint numerics for the exact-affine theorem, not a fitted-data bound.

Caller supplies COMPLETE matrices in one common coordinate field. The
represented functions must actually be affine; endpoint data cannot prove
that an unknown physical function between the points is affine.
"""
    dt=_number(delta_time,'delta_time')
    if dt<=0:raise ValueError('positive delta_time required')
    o0=_matrix(o0,'O0',hermitian=True);o1=_matrix(o1,'O1',shape=o0.shape,hermitian=True)
    d0=_matrix(d0,'D0',shape=o0.shape);d1=_matrix(d1,'D1',shape=o0.shape)
    slope=(o1-o0)/dt
    a=diagnose(o0,slope-d0-d0.conj().T);b=diagnose(o1,slope-d1-d1.conj().T)
    lo=min(a['lambda_min_real'],b['lambda_min_real']);hi=max(a['lambda_max_real'],b['lambda_max_real'])
    return {'endpoints':[a,b],'lower_log_norm_rate':lo,'upper_log_norm_rate':hi,
        'uniform_eta_numeric':max(a['eta_svd'],b['eta_svd']),
        'lower_log_norm_change':lo*dt,'upper_log_norm_change':hi*dt,
        'certified':False,'scope':'ENDPOINT_NUMERICS_FOR_EXACT_AFFINE_REPRESENTATION_ONLY'}

def conditional_witness_lower_bound(abs_witness_rate,eps_overlap,eps_residual):
    """Derived conditional bound. This function does NOT estimate input errors."""
    a=_number(abs_witness_rate,'witness');b=_number(eps_overlap,'eps_overlap');c=_number(eps_residual,'eps_residual')
    if a<0 or not 0<=b<1 or c<0:raise ValueError('require a>=0, 0<=eps_overlap<1, eps_residual>=0')
    return max(0.,a-c)/(1+b)
