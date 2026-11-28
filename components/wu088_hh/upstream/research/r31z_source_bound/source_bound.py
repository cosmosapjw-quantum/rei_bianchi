"""R31Z source-bound mixed-block interpolation diagnostics.

Uses only the hash-locked archived z=0,2,4 mixed-block arrays. The producer
intake in parent commit d573e7b... establishes their common frozen basis/phase
and independent dotO definition. This module does not evaluate HH kernels or
admit a physical trajectory.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, tempfile
from numbers import Real
from pathlib import Path
import numpy as np
from scipy.linalg import norm

EXPECTED='565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079'
PARENT_COMMIT='d573e7b40446b07b1a5544644cf3f977b89264a6'
PARENT_TREE='374a17cff99bed80cc7e356f2e03a1c9d1f1a077'


def _finite_positive(x,name):
    if isinstance(x,(bool,np.bool_)) or not isinstance(x,Real) or not math.isfinite(float(x)) or float(x)<=0:
        raise ValueError(name+' must be a positive finite real number')
    return float(x)


def _norm2(x):
    a=np.asarray(x)
    if a.ndim==0:return float(abs(a))
    if a.ndim!=2:raise ValueError('matrix or scalar required')
    return float(norm(a,2))


def _combine(coeffs, arrays):
    result=np.asarray(arrays[0])*coeffs[0]
    for c,a in zip(coeffs[1:],arrays[1:]):result=result+c*np.asarray(a)
    return result.item() if np.asarray(result).ndim==0 else result


def quintic_hermite(values, derivatives, interval, s):
    """Unique degree<=5 Hermite interpolant at s=0,1/2,1.

    derivatives are with respect to physical time t, while s=(t-t0)/interval.
    Returns (value, physical-time derivative).
    """
    T=_finite_positive(interval,'interval')
    if len(values)!=3 or len(derivatives)!=3:raise ValueError('three values and derivatives required')
    s=float(s)
    if not math.isfinite(s):raise ValueError('finite s required')
    # Wolfram-verified quintic Hermite basis.
    by0=24*s**5-68*s**4+66*s**3-23*s**2+1
    bd0=4*s**5-12*s**4+13*s**3-6*s**2+s
    by2=16*s**4-32*s**3+16*s**2
    bd2=16*s**5-40*s**4+32*s**3-8*s**2
    by4=-24*s**5+52*s**4-34*s**3+7*s**2
    bd4=4*s**5-8*s**4+5*s**3-s**2
    dby0=120*s**4-272*s**3+198*s**2-46*s
    dbd0=20*s**4-48*s**3+39*s**2-12*s+1
    dby2=64*s**3-96*s**2+32*s
    dbd2=80*s**4-160*s**3+96*s**2-16*s
    dby4=-120*s**4+208*s**3-102*s**2+14*s
    dbd4=20*s**4-32*s**3+15*s**2-2*s
    val=_combine([by0,T*bd0,by2,T*bd2,by4,T*bd4],
                 [values[0],derivatives[0],values[1],derivatives[1],values[2],derivatives[2]])
    ds=_combine([dby0,T*dbd0,dby2,T*dbd2,dby4,T*dbd4],
                [values[0],derivatives[0],values[1],derivatives[1],values[2],derivatives[2]])
    return val, ds/T


def quadratic_three_nodes(values,s):
    if len(values)!=3:raise ValueError('three nodes required')
    s=float(s)
    if not math.isfinite(s):raise ValueError('finite s required')
    return _combine([2*s*s-3*s+1,4*s-4*s*s,2*s*s-s],values)


def cubic_two_endpoints(v0,v1,d0,d1,interval,s):
    T=_finite_positive(interval,'interval');s=float(s)
    h00=2*s**3-3*s**2+1;h10=s**3-2*s**2+s;h01=-2*s**3+3*s**2;h11=s**3-s**2
    dh00=6*s*s-6*s;dh10=3*s*s-4*s+1;dh01=-6*s*s+6*s;dh11=3*s*s-2*s
    val=_combine([h00,T*h10,h01,T*h11],[v0,d0,v1,d1])
    ds=_combine([dh00,T*dh10,dh01,T*dh11],[v0,d0,v1,d1])
    return val,ds/T


def curvature_lower_bounds(f0,fm,f1,d0,d1,interval):
    """Necessary C2 curvature lower bounds in the physical-time variable.

    Matrix bounds use the spectral norm and follow from integral remainder
    identities. They are mathematical lower bounds for exact supplied matrices;
    floating input/source error is not enclosed by this function.
    """
    T=_finite_positive(interval,'interval')
    sec=(np.asarray(f1)-np.asarray(f0))/T
    e0=2*_norm2(sec-np.asarray(d0))/T
    e1=2*_norm2(sec-np.asarray(d1))/T
    mid=8*_norm2(np.asarray(fm)-(np.asarray(f0)+np.asarray(f1))/2)/(T*T)
    dd=_norm2(np.asarray(d1)-np.asarray(d0))/T
    return {'endpoint0':e0,'endpoint1':e1,'midpoint':mid,'endpoint_derivative_difference':dd,
            'combined':max(e0,e1,mid,dd)}


def replay(path):
    path=Path(path);before=path.read_bytes()
    if hashlib.sha256(before).hexdigest()!=EXPECTED:raise ValueError('snapshot SHA-256 mismatch')
    with np.load(path,allow_pickle=False) as f:d={k:f[k] for k in f.files}
    v=_finite_positive(float(d['velocity']),'velocity');T=4/v
    O=[np.array(d['z0_od_O'],complex),np.array(d['direct_O'][:47,47:],complex),np.array(d['z4_od_O'],complex)]
    dot=[np.array(d['z0_j_dotO'],complex),np.array(d['direct_dotO'][:47,47:],complex),np.array(d['z4_j_dotO'],complex)]
    Dc=[np.array(d['z0_od_D_col'],complex),np.array(d['direct_D'][:47,47:],complex),np.array(d['z4_od_D_col'],complex)]
    Dr=[np.array(d['z0_od_D_row'],complex),np.array(d['direct_D'][47:,:47],complex),np.array(d['z4_od_D_row'],complex)]
    K=[(c-r.conj().T)/2 for c,r in zip(Dc,Dr)]
    sec=(O[2]-O[0])/T
    affine={
      'midpoint_O_chord_error_2norm':_norm2((O[0]+O[2])/2-O[1]),
      'secant_minus_dotO_z0_2norm':_norm2(sec-dot[0]),
      'secant_minus_dotO_z2_2norm':_norm2(sec-dot[1]),
      'secant_minus_dotO_z4_2norm':_norm2(sec-dot[2]),
      'affine_O_compatible_with_source_nodes':False,
      'common_frozen_frame_authority':'RECOVERED_SOURCE_AND_ARRAY_BOUND',
      'authority_parent_commit':PARENT_COMMIT,
      'interpretation':'Source-bound represented-array incompatibility; not a physical source-error enclosure.'}
    bt=curvature_lower_bounds(O[0],O[1],O[2],dot[0],dot[2],T)
    bz={k:(val/(v*v) if k in ('endpoint0','endpoint1','midpoint','endpoint_derivative_difference','combined') else val) for k,val in bt.items()}
    curv={'endpoint0_per_ta2':bt['endpoint0'],'endpoint1_per_ta2':bt['endpoint1'],
          'midpoint_per_ta2':bt['midpoint'],'endpoint_derivative_difference_per_ta2':bt['endpoint_derivative_difference'],
          'combined_per_ta2':bt['combined'],'combined_per_a02':bz['combined'],
          'certified_interval_arithmetic':False,
          'scope':'NECESSARY_C2_CURVATURE_OF_SOURCE_BOUND_REPRESENTED_MIXED_O'}
    # Node compatibility before any interpolation construction.
    node_comp={name:_norm2(dot[i]-Dc[i]-Dr[i].conj().T) for i,name in enumerate(('z0','z2','z4'))}
    # Unique 3-node quintic O plus quadratic K.
    max_o=max_dot=max_dc=max_dr=max_r=0.; coeff_samples=[]
    for i,s in enumerate((0.,.5,1.)):
        op,dp=quintic_hermite(O,dot,T,s);kp=quadratic_three_nodes(K,s)
        dc=dp/2+kp;dr=(dp/2-kp).conj().T
        max_o=max(max_o,_norm2(op-O[i]));max_dot=max(max_dot,_norm2(dp-dot[i]))
        max_dc=max(max_dc,_norm2(dc-Dc[i]));max_dr=max(max_dr,_norm2(dr-Dr[i]))
    for s in np.linspace(0,1,65):
        op,dp=quintic_hermite(O,dot,T,float(s));kp=quadratic_three_nodes(K,float(s))
        dc=dp/2+kp;dr=(dp/2-kp).conj().T
        max_r=max(max_r,_norm2(dp-dc-dr.conj().T))
    # High-degree coefficient diagnostics from fixed basis coefficients.
    a5=24*O[0]+4*T*dot[0]+16*T*dot[1]-24*O[2]+4*T*dot[2]
    a4=-68*O[0]-12*T*dot[0]+16*O[1]-40*T*dot[1]+52*O[2]-8*T*dot[2]
    quint={'degree_upper_bound':5,'highest_coefficient_2norm':_norm2(a5),'quartic_coefficient_2norm':_norm2(a4),
           'max_O_node_error_2norm':max_o,'max_dotO_node_error_2norm':max_dot,
           'max_D_col_node_error_2norm':max_dc,'max_D_row_node_error_2norm':max_dr,
           'max_metric_compatibility_residual_grid_2norm':max_r,
           'node_count':3,'grid_probe_count':65,'validated_between_nodes':False,
           'candidate_scope':'SOURCE_NODE_EXACT_STRUCTURE_PRESERVING_MIXED_BLOCK_INTERPOLANT_ONLY'}
    co,cd=cubic_two_endpoints(O[0],O[2],dot[0],dot[2],T,.5)
    cubic={'midpoint_O_error_2norm':_norm2(co-O[1]),'midpoint_dotO_error_2norm':_norm2(cd-dot[1]),
           'passes_direct_midpoint':False,'scope':'UNIQUE_TWO_ENDPOINT_CUBIC_HERMITE'}
    result={'schema':'WU088_R31Z_SOURCE_BOUND_INTERPOLATION_V1','parent_commit':PARENT_COMMIT,'parent_tree':PARENT_TREE,
            'input_sha256':EXPECTED,'input_bytes':len(before),'velocity_a0_per_ta':v,'interval_ta':T,
            'source_bound_affine_rejection':affine,'curvature_lower_bound':curv,
            'node_metric_compatibility':node_comp,'two_endpoint_cubic_hermite':cubic,
            'quintic_mixed_candidate':quint,
            'source_authority':{
              'Q_producer_rule_and_order':'RECOVERED_FROM_HASH_VERIFIED_ARCHIVE',
              'j_dotO_definition_units':'RECOVERED_FROM_HASH_VERIFIED_ARCHIVE',
              'endpoint_mixed_common_frozen_basis_phase':'SOURCE_AND_ARRAY_BOUND_Z0_Z4',
              'direct_z2_and_endpoint_representation':'SOURCE_BOUND_BY_R31S_POSTPROCESS_AND_FROZEN_PHASE_PIPELINE',
              'independent_physical_adequacy_review':False},
            'physical_source_affineness':'NOT_ESTABLISHED','physical_source_nonaffineness_claimed':False,'physical_transition_error_bound':False,'full_cell_bound':False,
            'source_error_enclosure':False,'certified_interval_arithmetic':False,
            'native_evaluations':0,'new_native_evaluations':0,'new_heavy_scientific_nodes':0,'new_stored_matrix_linear_algebra':True,
            'HH_trajectory_runs':0,'independent_review_admitted':False,'production_admitted':False,'H_skip_admitted':False,
            'input_unchanged':hashlib.sha256(path.read_bytes()).hexdigest()==EXPECTED}
    return result


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(argv)
    if a.out.exists():raise FileExistsError(a.out)
    result=replay(a.input);payload=(json.dumps(result,indent=2,allow_nan=False)+'\n').encode()
    a.out.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=a.out.parent,prefix='.'+a.out.name+'.')
    try:
        with os.fdopen(fd,'wb') as f:f.write(payload);f.flush();os.fsync(f.fileno())
        os.link(tmp,a.out)
    finally:Path(tmp).unlink(missing_ok=True)
    print(json.dumps({'affine':result['source_bound_affine_rejection'],'curvature':result['curvature_lower_bound'],
                      'quintic':result['quintic_mixed_candidate']},indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
