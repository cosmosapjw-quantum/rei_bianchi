"""R31Y: auxiliary low-rank defect model and algebraic sector diagnostics.

No source-array symmetrization, physical labels, kernels, or propagation.
All floating-point results are diagnostics, not interval certificates.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import numpy as np
from scipy import linalg as la

EXPECTED='565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079'
HERMITICITY_RTOL=1e-12
RANK_RTOL=1e-12


def matrix(a,name,hermitian=False):
    x=np.array(a,dtype=np.complex128,copy=True)
    if x.ndim!=2 or not x.size or not np.isfinite(x).all():
        raise ValueError(name+' must be a finite nonempty matrix')
    if hermitian:
        if x.shape[0]!=x.shape[1]:raise ValueError(name+' must be square')
        if la.norm(x-x.conj().T,2)>HERMITICITY_RTOL*max(1.,la.norm(x,2)):
            raise ValueError(name+' violates Hermiticity prerequisite')
    return x


def eig_sorted(a,b=None,vectors=False):
    # Use all entries: do not silently replace a triangle by its adjoint.
    w,v=la.eig(a,b)
    order=np.argsort(w.real);w=w[order];v=v[:,order]
    return (w,v) if vectors else w


def analyze(overlap,residual,neutral):
    o=matrix(overlap,'O',True);r=matrix(residual,'R',True);n=len(o)
    if r.shape!=o.shape or type(neutral) is not int or not 0<neutral<n:
        raise ValueError('shape or neutral split invalid')
    m=n-neutral
    if neutral<m:raise ValueError('full-column-rank mixed block requires p>=m')
    b=r[:neutral,neutral:];f=r[neutral:,neutral:]
    sb=la.svdvals(b)
    if sb[0]==0 or sb[-1]<=RANK_RTOL*sb[0]:raise ValueError('mixed block is numerically rank deficient')
    try:l=la.cholesky(o,lower=True)
    except la.LinAlgError as exc:raise ValueError('O must be positive definite') from exc
    ub,tb=la.qr(b,mode='economic')
    z=la.block_diag(ub,np.eye(m))
    k=np.block([[np.zeros((m,m)),tb],[tb.conj().T,f]])
    # Explicit auxiliary model. The original R is not changed or replaced.
    r0=np.block([[np.zeros((neutral,neutral)),b],[b.conj().T,f]])
    oz=la.solve(o,z,assume_a='gen');g=z.conj().T@oz
    small,v=eig_sorted(k@g,vectors=True)
    # Independent whitening/QR route; expose Cholesky reconstruction error.
    li=la.solve_triangular(l,np.eye(n),lower=True)
    u,t=la.qr(li@z,mode='economic');h=t@k@t.conj().T
    symroute=eig_sorted(h)
    raw=eig_sorted(r,o);aux=eig_sorted(r0,o)
    active=lambda a: np.array(sorted(a[np.argsort(np.abs(a))[-2*m:]],key=lambda x:x.real))
    er=r-r0;ew=li@er@li.conj().T
    wr=li@r@li.conj().T;w0=li@r0@li.conj().T
    lifts=oz@v;rel=[];rawrel=[]
    for j in range(2*m):
        x=lifts[:,j];den=(la.norm(r0,2)+abs(small[j])*la.norm(o,2))*la.norm(x)
        rel.append(float(la.norm(r0@x-small[j]*o@x)/den))
        rawrel.append(float(la.norm(r@x-small[j]*o@x)/den))
    return dict(
        small_dimension=2*m, mixed_singular_values=sb.tolist(),
        small_eigenvalues_real=small.real.tolist(),small_eigenvalues_imag=small.imag.tolist(),
        small_positive_negative_counts=[int(sum(small.real>0)),int(sum(small.real<0))],
        raw_spectrum_real=raw.real.tolist(),raw_spectrum_imag=raw.imag.tolist(),
        small_vs_auxiliary_spectral_gap=float(max(abs(small-active(aux)))),
        small_vs_raw_spectral_gap=float(max(abs(small-active(raw)))),
        direct_vs_whitening_QR_gap=float(max(abs(small-symroute))),
        lifted_max_relative_residual_auxiliary=max(rel),lifted_max_relative_residual_raw=max(rawrel),
        raw_minus_auxiliary_norm=float(la.norm(er,2)),whitened_remainder_norm=float(la.norm(ew,2)),
        whitened_raw_singular_norm=float(la.norm(wr,2)),whitened_auxiliary_singular_norm=float(la.norm(w0,2)),
        factorization_R0_gap=float(la.norm(z@k@z.conj().T-r0,2)),
        raw_overlap_hermiticity_gap=float(la.norm(o-o.conj().T,2)),
        raw_residual_hermiticity_gap=float(la.norm(r-r.conj().T,2)),
        raw_minus_cholesky_metric_gap=float(la.norm(o-l@l.conj().T,2)),
        small_whitening_matrix_hermiticity_gap=float(la.norm(h-h.conj().T,2)),
        whitened_QR_orthogonality_gap=float(la.norm(u.conj().T@u-np.eye(2*m),2)),
        auxiliary_exact_hermitian_inertia_theorem=[m,m,n-2*m],
        general_eigensolver_used=True,certified=False,
        remainder_scope='NUMERICAL_NORM; WEYL_BOUND_CONDITIONAL_ON_EXACT_HERMITIAN_SPD_INPUTS',
        source_error_enclosure=False,raw_matrix_repaired=False,
        small_matrix_real=h.real.tolist(),small_matrix_imag=h.imag.tolist())


def sector_diagnostic(overlap,residual,frame):
    o=matrix(overlap,'O',True);r=matrix(residual,'R',True);q=matrix(frame,'Q')
    if r.shape!=o.shape or q.shape[0]!=len(o) or not 0<q.shape[1]<len(o):raise ValueError('sector dimensions invalid')
    if la.norm(q.conj().T@q-np.eye(q.shape[1]),2)>1e-12:raise ValueError('Euclidean orthonormal Q required')
    qm=la.null_space(q.conj().T);p=q@q.conj().T;j=2*p-np.eye(len(o))
    wp=eig_sorted(q.conj().T@r@q,q.conj().T@o@q)
    wm=eig_sorted(qm.conj().T@r@qm,qm.conj().T@o@qm)
    full=eig_sorted(r,o);union=np.array(sorted(np.r_[wp,wm],key=lambda x:x.real))
    return dict(dimensions=[q.shape[1],qm.shape[1]],
        involution_square_gap=float(la.norm(j@j-np.eye(len(o)),2)),
        O_commutator_norm=float(la.norm(o@j-j@o,2)),R_commutator_norm=float(la.norm(r@j-j@r,2)),
        O_cross_norm=float(la.norm(q.conj().T@o@qm,2)),R_cross_norm=float(la.norm(q.conj().T@r@qm,2)),
        retained_nonzero_real=wp.real[abs(wp)>1e-12].tolist(),
        complement_nonzero_real=wm.real[abs(wm)>1e-12].tolist(),
        max_eigenvalue_imag=float(max(max(abs(wp.imag)),max(abs(wm.imag)))),
        full_vs_sector_union_gap=float(max(abs(full-union))),
        diagnostic_nonzero_cutoff_inverse_time=1e-12,
        physical_sector_labels_assigned=False,exact_symmetry_of_raw_bytes_proven=False,
        scope='POINTWISE_ALGEBRAIC_SECTORS; NOT_PHYSICAL_PARITY_OR_PROPAGATION_DECOUPLING')


def replay(path):
    path=Path(path);before=path.read_bytes()
    if hashlib.sha256(before).hexdigest()!=EXPECTED:raise ValueError('snapshot SHA-256 mismatch')
    with np.load(path,allow_pickle=False) as f:d={k:f[k] for k in f.files}
    dt=4/float(d['velocity'])
    if not np.isfinite(dt) or dt<=0:raise ValueError('positive finite time interval required')
    def put(base,col,row,ion):
        a=np.array(base,dtype=np.complex128,copy=True)
        if a.shape!=(49,49):raise ValueError('49x49 snapshot expected')
        a[:47,47:]=col;a[47:,:47]=row;a[47:,47:]=ion;return a
    o=put(d['direct_O'],(d['z0_od_O']+d['z4_od_O'])/2,(d['z0_od_O_row']+d['z4_od_O_row'])/2,(d['z0_ion_O']+d['z4_ion_O'])/2)
    conn=put(d['direct_D'],(d['z0_od_D_col']+d['z4_od_D_col'])/2,(d['z0_od_D_row']+d['z4_od_D_row'])/2,(d['z0_ion_D']+d['z4_ion_D'])/2)
    od=put(d['direct_dotO'],(d['z4_od_O']-d['z0_od_O'])/dt,(d['z4_od_O_row']-d['z0_od_O_row'])/dt,(d['z4_ion_O']-d['z0_ion_O'])/dt)
    r=od-conn-conn.conj().T
    return dict(schema='WU088_R31Y_LOW_RANK_REPLAY_V1',input_sha256=EXPECTED,input_bytes=len(before),
        diagnostic_dtype='complex128; unchanged extended-precision source retained',
        represented_matrix_hashes={k:hashlib.sha256(a.tobytes()).hexdigest() for k,a in [('O',o),('R',r)]},
        lowrank=analyze(o,r,47),sectors=sector_diagnostic(o,r,d['direct_Q']),
        input_unchanged=hashlib.sha256(path.read_bytes()).hexdigest()==EXPECTED,
        time_unit='t_a=hbar/E_h; all rates inverse t_a',
        Q_authority='Q_AUTHORITY_BLOCKED',mixed_frame_authority='MIXED_FRAME_AUTHORITY_BLOCKED',
        full_cell_bound=False,source_error_enclosure=False,physical_transition_error_bound=False,
        native_evaluations=0,new_heavy_scientific_nodes=0,new_stored_matrix_linear_algebra=True,
        HH_trajectory_runs=0,independent_review_admitted=False,production_admitted=False)


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',required=True,type=Path);ap.add_argument('--out',required=True,type=Path)
    a=ap.parse_args(argv)
    if a.out.exists():raise FileExistsError(a.out)
    result=replay(a.input);content=(json.dumps(result,indent=2,allow_nan=False)+'\n').encode()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=a.out.parent,prefix='.'+a.out.name+'.')
    try:
        with os.fdopen(fd,'wb') as f:f.write(content);f.flush();os.fsync(f.fileno())
        os.link(tmp,a.out)
        dfd=os.open(a.out.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(dfd)
        finally:os.close(dfd)
    finally:Path(tmp).unlink(missing_ok=True)
    print(json.dumps({'small_eigenvalues_real':result['lowrank']['small_eigenvalues_real'],
        'complement_modes':result['sectors']['complement_nonzero_real'],
        'whitened_remainder_norm':result['lowrank']['whitened_remainder_norm']},indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
