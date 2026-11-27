"""Small source-only reproduction of HE27 adaptive-reference stall diagnosis.

Run with the pinned HE25 venv from the isolated HE27 checkout.  This script
does not open the native owner or perform a chemistry integration.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = Path('/root/BASS_HE_HE27_SOURCECUT_20261016')
sys.path.insert(0, str(ROOT / 'research/he27_sourcecut_native_20261016/src'))
from sourcecut import SourceCutModel as V1
from sourcecut import _CUTS, _cut_children, _moments, _target, sigma_cm2, shape, BIND_EV
from sourcecut_v2 import SourceCutModel as V2


class NoOwner:
    pass


def stencil(model, fraction, h_fraction=1e-9):
    t = fraction * model.t_end
    h = h_fraction * model.t_end
    a, b, c = (model.source(t + offset * h) for offset in (0, 1, 2))
    return {'step_fraction': h_fraction,
            'max_relative_mode_step': float(np.max(abs(b-a)) / max(a.max(), 1e-300)),
            'second_difference_over_first': float(np.linalg.norm(c-2*b+a) /
                                                  np.linalg.norm(b-a))}


def main():
    old = V1(NoOwner(), 4, 4, 0.)
    t = .0009449402471520216 * old.t_end
    x = old.x(t)
    energy = old.geometry(t)[0]
    sigma = sigma_cm2(energy)
    mu, aw, group, panels = old._groups[0]
    children = _cut_children(panels, x, old.q, mu)
    conditions = []
    truncated = None
    for band in range(3):
        lo, hi = _CUTS[band:band+2]
        kids = [c for c in children if lo <= (c['low_ev']+c['high_ev'])/2 < hi]
        selected = np.arange(group.start,group.stop)
        selected = selected[(energy[group] >= lo) &
                            (energy[group] < hi if band < 2 else energy[group] <= hi)]
        matrix = _moments(band+1,energy[selected],sigma[selected])
        singular = np.linalg.svd(matrix,compute_uv=False)
        conditions.append(float(singular[0]/singular[-1]))
        if band == 2:
            target = _target(3,kids)
            jac = np.exp(-3*x)/old.factor(x,old.mu0)**2
            base = old.weights[selected] * shape(energy[selected]) * jac[selected]
            metric = np.maximum(base,base.max()*1e-14)
            weighted = matrix*np.sqrt(metric)
            error = target-matrix@base
            correction,_,rank,_=np.linalg.lstsq(weighted,error,rcond=1e-9)
            projected=base+np.sqrt(metric)*correction
            truncated={'rank':int(rank),'all_rows':len(target),
                       'max_relative_defect':float(np.max(abs(target-matrix@projected)/
                                                        np.maximum(abs(target),1e-30))),
                       'minimum_mode':float(projected.min())}
    new = V2(NoOwner(),4,4,0.,source_table_nodes=512)
    # Uniform interpolation wrongly bridges a real fixed-K threshold event.
    whole = np.linspace(0,old.t_end,257)
    values = np.array([old.source_moments(t0)[0] for t0 in whole])
    probe = .330034*old.t_end
    k = min(int(.330034*256),255)
    f = (probe-whole[k])/(whole[k+1]-whole[k])
    uniform = (1-f)*values[k]+f*values[k+1]
    e = old.geometry(probe)[0];s = sigma_cm2(e)
    observed = np.r_[sum(uniform),np.dot(uniform,e),
        (uniform[:,None]*s).sum(axis=0),
        (uniform[:,None]*s*(e[:,None]-BIND_EV)).sum(axis=0)]
    truth = np.asarray(old.source_moments(probe)[1]['donor_raw'])
    uniform_defect=float(np.max(abs(observed-truth)/np.maximum(abs(truth),1e-30)))
    times=[.0001273786026739819,.0009449402471520216,.0113,.237,.501,.773,.991]
    max_admission=max(new.source_moments(f*new.t_end)[1]['max_relative_moment_error']
                      for f in times)
    result={
        'schema':'bass_he.he27.source_conditioning_repair.v1',
        'scope':'SOURCE_ONLY_NO_NATIVE_REFERENCE_RERUN',
        'original_sourcecut_sha256':hashlib.sha256((ROOT/'research/he27_sourcecut_native_20261016/src/sourcecut.py').read_bytes()).hexdigest(),
        'v2_sourcecut_sha256':hashlib.sha256((ROOT/'research/he27_sourcecut_native_20261016/src/sourcecut_v2.py').read_bytes()).hexdigest(),
        'stall_time_fraction':.0009449402471520216,
        'fixed_band_matrix_condition_numbers':conditions,
        'v1_stencil':stencil(old,.0009449402471520216),
        'v2_stencil':stencil(new,.0009449402471520216),
        'truncated_svd_rcond_1e-9':truncated,
        'unchanged_eight_moment_gate_relative':3e-13,
        'uniform_256_crossing_relative_defect':uniform_defect,
        'event_segmented_v2_512_max_sampled_relative_defect':max_admission,
        'source_table_sha256':new.source_table_sha256,
        'source_table_diagnostics':new.source_table_diagnostics,
        'historical_exact_breakpoint_dense_probe_max_relative':{
            'q_minus_0p005':{'256':1.430085679468966e-13,'512':3.6683187350961764e-14,'1024':1.0055289933766168e-14},
            'q_zero':{'256':1.439396133111342e-13,'512':3.70556054966568e-14,'1024':9.869080860918646e-15},
            'q_plus_0p005':{'256':1.4356719516543912e-13,'512':3.686939642380929e-14,'1024':9.4966627152236e-15}},
        'interpretation':'rcond truncation violates fixed gate; uniform interpolation crosses cutoff events; exact-event segmented positive interpolation removes the measured early source-mode jitter while preserving the donor moment gate.'
    }
    output=HERE/'REPAIR_DIAGNOSIS.json'
    temporary=HERE/'REPAIR_DIAGNOSIS.json.tmp'
    with temporary.open('x') as stream:
        json.dump(result,stream,indent=2,sort_keys=True)
        stream.flush();__import__('os').fsync(stream.fileno())
    temporary.replace(output)
    directory=__import__('os').open(HERE,__import__('os').O_RDONLY)
    try:__import__('os').fsync(directory)
    finally:__import__('os').close(directory)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':
    main()
