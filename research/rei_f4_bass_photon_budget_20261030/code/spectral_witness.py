"""Finite-energy nonnegative H/He six-moment spectral construction (no IVP).

Source: pinned BASS 21-state sigma and 71 fixed original log-bin centres;
Puchwein2019 PR261 six rate/heating moments on seven stored REI redshifts.
No rewrite of original BASS power-law UV, no inferred physical redshift/clock,
no P19 extension to z=20, no claim of unique spectrum or Li rate.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from scipy.optimize import linprog
from . import upstream_native_rate as parent

SPECIES = (1, 7, 8)  # H1I, He3I, He3II in source BASS 21-state convention
NOMINAL_BETA = parent.NOMINAL_BETA
NOMINAL_KAPPA = parent.NOMINAL_KAPPA
FLUX_UNIT = 1e9  # m^-2 s^-1 per nonnegative energy bin, numerical scaling only


def six_moment_matrix(net):
    """Return M with [Gamma_HI, HeI, HeII; heat_HI, HeI, HeII].

    Rates = M@Phi; [Gamma]=s^-1, [heat]=eV/s, Phi=m^-2 s^-1.
    Original BASS energy nodes and original sigma, not free cross-section fits.
    """
    energies = np.array(net.photon_energy_eV, dtype=float)
    sig, _ = net.photo_cross_sections(energies)
    thresholds = np.array(net.transition_energy_eV[list(SPECIES)], dtype=float)
    block = sig[list(SPECIES)]
    heat = block * np.maximum(0., energies[None, :] - thresholds[:, None])
    return energies, np.vstack((block, heat)), sig


def target_six(z):
    """Pinned P19 log-knot interpolation and PR261 nominal beta,kappa.

    Output order is ion H, HeI, HeII, heat H, HeI, HeII.
    """
    if not math.isfinite(z) or not 2.4 <= z <= 4.75:
        raise ValueError("P19_REDSHIFT_DOMAIN_2.4_TO_4.75")
    rows = np.array(parent.json.loads((parent.SRC/'P19_13_KNOTS.json').read_text())['rows'], float)
    if rows.shape != (13, 7) or not np.all(np.diff(rows[:, 0]) > 0):
        raise ValueError('P19_SOURCE_SHAPE_INVALID')
    log_moments = np.array([np.interp(z, rows[:, 0], np.log(rows[:, k])) for k in range(1, 7)])
    common = math.log(10)*(NOMINAL_BETA + NOMINAL_KAPPA*(z-3.6))
    target = np.exp(log_moments + common)
    return target[[0,2,4,1,3,5]]


def nonnegative_witness(matrix, target):
    """Minimum total bin-integrated photon number flux, with six exact equalities.

    No extra assumption of BASS power-law spectral shape, smoothness, or fixed
    total energy. This selects one LP vertex, not a physically unique spectrum.
    """
    M = np.asarray(matrix,float); target = np.asarray(target,float)
    if M.shape[0] != 6 or M.shape[1] < 6 or target.shape != (6,):
        raise ValueError('DIMENSION_MISMATCH')
    if not np.isfinite(M).all() or not np.isfinite(target).all() or np.any(target <= 0):
        raise ValueError('INVALID_MOMENT_OR_COEFFICIENT')
    A = M*(FLUX_UNIT/target[:,None])
    out = linprog(np.ones(M.shape[1]), A_eq=A, b_eq=np.ones(6),
                  bounds=(0, None), method='highs', options={'primal_feasibility_tolerance':1e-9})
    if not out.success:
        raise RuntimeError('NONNEGATIVE_SIX_MOMENT_LP_FAILED:'+out.message)
    y = np.asarray(out.x,float)
    rel_err = np.max(np.abs(A@y - 1.))
    if np.min(y) < -1e-12 or rel_err > 1e-10:
        raise ArithmeticError('SIX_MOMENT_RECONSTRUCTION_RESIDUAL')
    nz = np.flatnonzero(y > 1e-9)
    if len(nz)>6:
        raise ArithmeticError('LP_VERTEX_SUPPORT_GT6')
    return dict(flux=y*FLUX_UNIT,active_indices=nz,scaled_matrix=A,
                flux_total=float(np.sum(y)*FLUX_UNIT),rel_err=float(rel_err))


def li_blind_witness(energies, matrix, sig, flux):
    """A Li-I-positive / H-He-zero energy bin and positive null perturbation.

    For any lambda >=0 in m^-2 s^-1, M(Phi+lambda e_j)=M Phi;
    LiI rate increases by lambda*sigma_LiI(E_j) >0.
    """
    e = np.asarray(energies,float); M=np.asarray(matrix,float)
    li = np.asarray(sig[13],float)
    hits = [j for j,x in enumerate(e) if 5.392 < x < 13.6
            and li[j] > 0 and np.array_equal(M[:,j],np.zeros(6))]
    if not hits:
        raise ValueError('NO_H_HE_BLIND_LI_CHANNEL')
    k=min(hits,key=lambda i:abs(e[i]-10.0))
    lam = FLUX_UNIT  # finite illustrative perturbation; not an empirical prior
    alt=np.array(flux,float,copy=True);alt[k]+=lam
    assert np.array_equal(M[:,k],np.zeros(6))
    return dict(index=int(k),energy_eV=float(e[k]),sigma_LiI_m2=float(li[k]),
                delta_photon_flux_m2_s=lam,
                delta_Gamma_LiI_s=float(lam*li[k]),
                max_absolute_HHe_moment_change=float(np.max(np.abs(M@alt-M@flux))),
                alternate_flux=alt)



def conditional_li_photo_bounds(energies, matrix, sig, target):
    """Exact-in-represented-data LP bounds for extra Li charge families.

    Unconstrained nonnegative photon flux within the original BASS fixed bins.
    LiI has a positive H/He-blind ray -> unbounded upper limit.
    LiII/LiIII have finite analytic upper from the measured HeII rate.
    """
    A=np.asarray(matrix,dtype=float)*(FLUX_UNIT/np.asarray(target,float)[:,None])
    li1 = np.asarray(sig[13],float)
    scale=1.e-13
    c=li1*FLUX_UNIT/scale
    low=linprog(c,A_eq=A,b_eq=np.ones(6),bounds=(0,None),method='highs')
    high=linprog(-c,A_eq=A,b_eq=np.ones(6),bounds=(0,None),method='highs')
    if not low.success or high.status!=3:
        raise ArithmeticError('LI1_LP_EXPECTED_FINITE_MIN_UNBOUNDED_MAX_FAILED')
    # LP dual certificate (scaled): y^T b = c^T x and A^T y <= c.
    dual=low.eqlin.marginals
    dual_slack=np.max(A.T@dual-c)
    dual_gap=abs(np.sum(dual)-low.fun)
    if dual_slack>2e-7 or dual_gap>2e-7 or np.max(abs(A@low.x-1))>1e-9:
        raise ArithmeticError('LI1_DUAL_RECONSTRUCTION_FAILED')
    # For Li II/III energies, sigma_HeII(E)>0 by nested thresholds.
    # Thus sigma_LiX(E) <= Rmax sigma_HeII(E) on the full finite BASS grid,
    # giving Gamma_LiX <= Rmax Gamma_HeII for all Phi>=0.
    upper={}
    heII=np.asarray(sig[8],float)
    for index,label in [(14,'LiII'),(15,'LiIII')]:
        enabled=sig[index]>0
        if np.any(enabled & (heII<=0)):
            raise ArithmeticError('LI_ION_HEII_THRESHOLD_ORDER_INVALID')
        ratio=float(np.max(sig[index,enabled]/heII[enabled]))
        upper[label]=dict(max_sigma_ratio_to_HeII=ratio,
                          gamma_upper_s=ratio*float(target[2]))
    return dict(LiI_gamma_lower_s=float(low.fun*scale),LiI_gamma_upper='UNBOUNDED',
                LiI_dual_max_violation_scaled=float(dual_slack),
                LiI_dual_gap_scaled=float(dual_gap),Li_higher_upper=upper)

def seven_saved_witnesses():
    parent.source_manifest_check()
    net=parent.new_native_network()
    energies,M,sig=six_moment_matrix(net)
    rows=parent.json.loads((parent.SRC/'REI_SAVED7.json').read_text())['rows']
    if len(rows)!=7:raise ValueError('EXPECTED_7_SAVED_ROWS')
    cases=[]
    for row in rows:
        z=float(row['z']);t=target_six(z)
        lp=nonnegative_witness(M,t)
        blind=li_blind_witness(energies,M,sig,lp['flux'])
        bounds=conditional_li_photo_bounds(energies,M,sig,t)
        active=lp['active_indices']
        predicted=M@lp['flux']
        y_li7=float(row['y'][13]);d_li7=float(y_li7*blind['delta_Gamma_LiI_s'])
        cases.append(dict(z=z,source_elapsed_proper_s=float(row['elapsed_proper_s']),
                          target_six=t.tolist(), reconstructed_six=predicted.tolist(),
                          max_rel_error=lp['rel_err'],sum_photon_number_flux_m2_s=lp['flux_total'],
                          support_size=int(len(active)),
                          support_energies_eV=energies[active].tolist(),
                          support_bin_flux_m2_s=lp['flux'][active].tolist(),
                          base_LiI_photo_rate_s=float(sig[13]@lp['flux']),
                          Li_rate_bounds=bounds,
                          LiI_blind=dict(index=blind['index'], energy_eV=blind['energy_eV'],
                                         sigma_LiI_m2=blind['sigma_LiI_m2'],
                                         delta_flux_m2_s=blind['delta_photon_flux_m2_s'],
                                         delta_Gamma_LiI_s=blind['delta_Gamma_LiI_s'],
                                         delta_Li7_photo_source_per_Href_s=d_li7,
                                         h_he_six_change=blind['max_absolute_HHe_moment_change'])))
    return dict(schema='REI_F4_NONNEGATIVE_SIX_MOMENT_WITNESS_V1',
                domain='seven saved REI mean redshifts 2.4..4.75 only',
                frame='conditional external local isotropic prescribed spectrum',
                energy_support_eV=[5.,200.],
                number_of_BASS_original_bin_centres=len(energies),
                positive_equality_moments=6,cases=cases,
                new_ivps=0,source_photon_spectrum_changed='hypothetical only',
                full_REI_chemistry='not bound',physical_Thomson_tau='not computed')
