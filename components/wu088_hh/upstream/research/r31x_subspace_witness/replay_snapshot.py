#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path
import numpy as np
from subspace_witness import analyze_pencil

EXPECTED="565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079"

def insert(base,col,row,ionic):
    a=np.array(base,dtype=np.complex128,copy=True)
    a[:47,47:]=col; a[47:,:47]=row; a[47:,47:]=ionic
    return a

def compute(path):
    p=Path(path); raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED: raise ValueError("snapshot SHA-256 mismatch")
    with np.load(p,allow_pickle=False) as f: d={k:f[k] for k in f.files}
    v=float(d['velocity']); dt=4/v
    O=insert(d['direct_O'],(d['z0_od_O']+d['z4_od_O'])/2,
             (d['z0_od_O_row']+d['z4_od_O_row'])/2,(d['z0_ion_O']+d['z4_ion_O'])/2)
    D=insert(d['direct_D'],(d['z0_od_D_col']+d['z4_od_D_col'])/2,
             (d['z0_od_D_row']+d['z4_od_D_row'])/2,(d['z0_ion_D']+d['z4_ion_D'])/2)
    dotO=insert(d['direct_dotO'],(d['z4_od_O']-d['z0_od_O'])/dt,
                (d['z4_od_O_row']-d['z0_od_O_row'])/dt,(d['z4_ion_O']-d['z0_ion_O'])/dt)
    R=dotO-D-D.conj().T
    result=analyze_pencil(O,R,d['direct_Q'])
    block_attribution={}
    for name,w in result['witnesses'].items():
        x=np.array(w['vector_real'])+1j*np.array(w['vector_imag'])
        xn,xi=x[:47],x[47:]
        nn=np.vdot(xn,R[:47,:47]@xn)
        cross=np.vdot(xn,R[:47,47:]@xi)+np.vdot(xi,R[47:,:47]@xn)
        ionic=np.vdot(xi,R[47:,47:]@xi)
        block_attribution[name]={
            'neutral_neutral_real':float(nn.real),'neutral_neutral_imag':float(nn.imag),
            'neutral_ionic_cross_real':float(cross.real),'neutral_ionic_cross_imag':float(cross.imag),
            'ionic_ionic_real':float(ionic.real),'ionic_ionic_imag':float(ionic.imag),
            'sum_real':float((nn+cross+ionic).real),
        }
    result['block_attribution_47_plus_2']=block_attribution
    O0c=np.array(d['z0_od_O'],dtype=np.complex128); O4c=np.array(d['z4_od_O'],dtype=np.complex128)
    D0c=np.array(d['z0_od_D_col'],dtype=np.complex128); D4c=np.array(d['z4_od_D_col'],dtype=np.complex128)
    D0r=np.array(d['z0_od_D_row'],dtype=np.complex128); D4r=np.array(d['z4_od_D_row'],dtype=np.complex128)
    midDc=(D0c+D4c)/2; midDr=(D0r+D4r)/2
    slope=(O4c-O0c)/dt
    directDc=np.array(d['direct_D'][:47,47:],dtype=np.complex128)
    directDr=np.array(d['direct_D'][47:,:47],dtype=np.complex128)
    directDot=np.array(d['direct_dotO'][:47,47:],dtype=np.complex128)
    directR=directDot-directDc-directDr.conj().T
    termDot=slope-directDot
    termD=-(midDc-directDc)-(midDr-directDr).conj().T
    hybridCross=slope-midDc-midDr.conj().T
    result['mixed_block_interpolation']={
        'midpoint_O_error_2norm':float(np.linalg.norm((O0c+O4c)/2-d['direct_O'][:47,47:],2)),
        'midpoint_D_col_error_2norm':float(np.linalg.norm(midDc-directDc,2)),
        'midpoint_D_row_error_2norm':float(np.linalg.norm(midDr-directDr,2)),
        'secant_slope_minus_direct_z2_dotO_2norm':float(np.linalg.norm(termDot,2)),
        'secant_slope_minus_endpoint_z0_dotO_2norm':float(np.linalg.norm(slope-np.array(d['z0_j_dotO'],dtype=np.complex128),2)),
        'secant_slope_minus_endpoint_z4_dotO_2norm':float(np.linalg.norm(slope-np.array(d['z4_j_dotO'],dtype=np.complex128),2)),
        'direct_z2_cross_residual_2norm':float(np.linalg.norm(directR,2)),
        'hybrid_cross_residual_2norm':float(np.linalg.norm(hybridCross,2)),
        'derivative_mismatch_term_2norm':float(np.linalg.norm(termDot,2)),
        'connection_interpolation_mismatch_term_2norm':float(np.linalg.norm(termD,2)),
        'decomposition_closure_2norm':float(np.linalg.norm(termDot+termD+directR-hybridCross,2)),
        'affine_endpoint_derivative_compatibility':'FAIL_IN_ARCHIVED_REPRESENTATION_CONDITIONAL_ON_COMMON_ENDPOINT_FRAME',
        'physical_source_affineness_claim':False,
    }
    for name,w in result['witnesses'].items():
        x=np.array(w['vector_real'])+1j*np.array(w['vector_imag']); xn,xi=x[:47],x[47:]
        def cc(C): return np.vdot(xn,C@xi)+np.vdot(xi,C.conj().T@xn)
        result['mixed_block_interpolation'][name+'_witness_decomposition']={
            'derivative_mismatch_real':float(cc(termDot).real),
            'connection_interpolation_mismatch_real':float(cc(termD).real),
            'direct_z2_residual_real':float(cc(directR).real),
            'hybrid_cross_real':float(cc(hybridCross).real),
        }
    result['residual_block_norms']={
        'neutral_neutral_2norm':float(np.linalg.norm(R[:47,:47],2)),
        'neutral_ionic_2norm':float(np.linalg.norm(R[:47,47:],2)),
        'neutral_ionic_singular_values':[float(x) for x in np.linalg.svd(R[:47,47:],compute_uv=False)],
        'ionic_ionic_2norm':float(np.linalg.norm(R[47:,47:],2)),
        'full_R_2norm':float(np.linalg.norm(R,2)),
    }
    result.update({
        "source_snapshot_sha256":EXPECTED,
        "source_bytes":len(raw),
        "velocity_a0_per_ta":v,
        "endpoint_dt_ta":dt,
        "fixed_Q_sha256":hashlib.sha256(np.ascontiguousarray(d['direct_Q']).tobytes()).hexdigest(),
        "min_overlap_eigenvalue_full":float(np.linalg.eigvalsh(O).min()),
        "min_overlap_eigenvalue_reduced":float(np.linalg.eigvalsh(d['direct_Q'].T@O@d['direct_Q']).min()),
        "source_changed":hashlib.sha256(p.read_bytes()).hexdigest()!=EXPECTED,
        "new_native_evaluations":0,
        "new_heavy_scientific_nodes":0,
        "HH_trajectory_runs":0,
        "production_admitted":False,
        "full_cell_interval_bound":False,
        "historical_authority_input_blocked":True,
        "interpretation":"At the stored hybrid z=2 represented point, reduced nonzero Ritz values are ambient full49 witnesses. Full49 stored-matrix eigensolve is lightweight linear algebra, not a new native HH node."
    })
    return result

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    if a.out.exists(): raise FileExistsError(a.out)
    result=compute(a.input); payload=(json.dumps(result,indent=2,allow_nan=False)+'\n').encode()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=a.out.parent,prefix='.'+a.out.name+'.')
    try:
        with os.fdopen(fd,'wb') as f: f.write(payload); f.flush(); os.fsync(f.fileno())
        os.link(tmp,a.out)
    finally: Path(tmp).unlink(missing_ok=True)
    print(json.dumps({
        'eta_full_point':result['eta_full_point'],
        'eta_reduced_point':result['eta_reduced_point'],
        'lambda_full_min':result['lambda_full_min'],
        'lambda_full_max':result['lambda_full_max'],
        'projection_residuals':result['extremal_full_eigenvector_O_projection_residual'],
        'full_nonzero':result['full_nonzero_generalized_eigenvalues_tol1e-12'],
        'reduced_nonzero':result['reduced_nonzero_generalized_eigenvalues_tol1e-12'],
    },indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
