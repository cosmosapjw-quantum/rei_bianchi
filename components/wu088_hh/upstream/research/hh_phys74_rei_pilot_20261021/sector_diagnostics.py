"""Separate matter/radiation STF stresses in one normal orthonormal frame.

H and sigma use proper-time s^-1; pi_m and pi_r use J/m^3.
Use kappa_time = c^2*kappa_E = 8*pi*G/c^2. A sector is a signed tensor sum,
not a sum of norms. This observer neither changes dynamics nor infers closure.
"""
from __future__ import annotations
import numpy as np
from tensor_adapter import tensor_norms, _frobenius


def sector_tensor_norms(H, sigma, pi_m, pi_r, *, kappa_time):
    """Return separate norms/work and auxiliary total/cross checks.

    Tensors must have identical (...,3,3) shapes. H may broadcast only to their
    existing batch shape. Each sector must already include its assigned species.
    Missing/unknown stresses must not be supplied as fabricated zero tensors.
    Undefined alignments are NaN, accompanied by explicit validity flags.
    """
    s, m, r = [np.asarray(a, dtype=float) for a in (sigma, pi_m, pi_r)]
    if s.shape[-2:] != (3, 3) or s.shape != m.shape or s.shape != r.shape:
        raise ValueError('sector and shear tensors require identical (...,3,3) shapes')
    h = np.broadcast_to(np.asarray(H, dtype=float), s.shape[:-2])
    # Original observer validates finite, positive H/kappa and symmetric STF data.
    dm = tensor_norms(h, s, m[..., None, :, :], kappa_time=kappa_time)
    dr = tensor_norms(h, s, r[..., None, :, :], kappa_time=kappa_time)
    dt = tensor_norms(h, s, np.stack((m, r), axis=-3), kappa_time=kappa_time)
    mn, rn = _frobenius(m), _frobenius(r)
    um = m / np.where(mn == 0, 1., mn)[..., None, None]
    ur = r / np.where(rn == 0, 1., rn)[..., None, None]
    cosine = np.sum(um * ur, axis=(-2, -1))
    defined = (mn > 0) & (rn > 0)
    cross = 2 * dm['Pi_F'] * dr['Pi_F'] * cosine
    out = {'Sigma_F': dt['Sigma_F'], 'Sigma_half': dt['Sigma_F']/np.sqrt(2.),
           'mr_alignment': np.where(defined, cosine, np.nan),
           'mr_alignment_defined': defined, 'mr_cross': cross}
    for tag, d in (('m', dm), ('r', dr), ('total', dt)):
        out['Pi_'+tag+'_F'] = d['Pi_F']
        out['Pi_'+tag+'_half'] = d['Pi_F']/np.sqrt(2.)
        out['work_'+tag] = d['work']
        out['shear_'+tag+'_alignment'] = d['alignment']
        out['shear_'+tag+'_alignment_defined'] = d['alignment_defined']
    out['norm_square_residual'] = dt['Pi_F']**2-(dm['Pi_F']**2+dr['Pi_F']**2+cross)
    out['work_additivity_residual'] = dt['work']-(dm['work']+dr['work'])
    for key, value in out.items():
        if 'alignment' not in key and not np.isfinite(value).all():
            raise ValueError('nonfinite derived diagnostic: '+key)
    return out


def lrs_sector_norms(H, s, pi_s_m, pi_s_r, *, kappa_time):
    """LRS convention: sigma=diag(-s,-s,2s), pi_X=diag(-p_X,-p_X,2p_X).

    pi_s_m/r are p_X=(P_parallel-P_perp)/3. Do not pass DeltaP directly.
    """
    h, sv, pm, pr = np.broadcast_arrays(*[np.asarray(v, dtype=float)
                                        for v in (H, s, pi_s_m, pi_s_r)])
    pattern = np.diag([-1., -1., 2.])
    out = sector_tensor_norms(h, sv[..., None, None]*pattern,
                             pm[..., None, None]*pattern, pr[..., None, None]*pattern,
                             kappa_time=kappa_time)
    out['Sigma_signed'] = np.sqrt(6.)*sv/h
    for tag, value in (('m', pm), ('r', pr), ('total', pm+pr)):
        out['Pi_'+tag+'_signed'] = kappa_time*np.sqrt(6.)*value/h**2
        out['pi_s_'+tag+'_J_m3'] = value
    return out
