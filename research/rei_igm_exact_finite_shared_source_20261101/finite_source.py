#!/usr/bin/env python3
"""Exact finite global photon-competition response and all-X source-only remainder.

This is a SAME-CLOCK source operator, NOT a validated full 26-event time-map.
Original model owner and physically source-owned inputs are provided by PR332.
"""
from __future__ import annotations
import numpy as np

EV_ERG=1.602176634e-12
SPECIES=('HI','HeI','HeII')

def source_response(n0,n1,accepted_lo,accepted_hi,coefficients,external,current,excess_ev):
    """Exact first-order + finite nonlinear quotient remainder.

    n0,n1,accepted_lo,accepted_hi: [node,neutral-species] original physical counts.
    coefficients: [photon-group,species] source owner units reciprocal particles.
    external,current: [group] exact frozen source forcing selected at one time.
    excess_ev: [species,group] original photo-electron excess energy in eV.
    All-X bound quantifies marginal original node population box at FIXED forcing.
    """
    n0,n1,lo,hi=(np.asarray(x,dtype=float) for x in (n0,n1,accepted_lo,accepted_hi))
    c,e,j,q=(np.asarray(x,dtype=float) for x in (coefficients,external,current,excess_ev))
    if n0.ndim!=2 or n0.shape[1]!=3 or any(x.shape!=n0.shape for x in (n1,lo,hi)):
        raise ValueError('original [N,3] neutral species shape')
    if c.ndim!=2 or c.shape[1]!=3 or e.shape!=(len(c),) or j.shape!=e.shape or q.shape!=(3,len(c)):
        raise ValueError('original group/species dimension mismatch')
    if not all(np.isfinite(x).all() for x in (n0,n1,lo,hi,c,e,j,q)):
        raise ValueError('nonfinite original source')
    if any(np.any(x<0) for x in (n0,n1,lo,hi,c,e,j)) or np.any(lo>hi):
        raise ValueError('negative or inverted photon source')
    if np.any(n1<lo-1e-13*np.maximum(1,hi)) or np.any(n1>hi+1e-13*np.maximum(1,hi)):
        raise ValueError('real source representative not in original interval')
    s0=np.sum(n0.astype(np.longdouble),axis=0,dtype=np.longdouble).astype(float)
    s1=np.sum(n1.astype(np.longdouble),axis=0,dtype=np.longdouble).astype(float)
    slo=np.sum(lo.astype(np.longdouble),axis=0,dtype=np.longdouble).astype(float)
    shi=np.sum(hi.astype(np.longdouble),axis=0,dtype=np.longdouble).astype(float)
    N=len(n0)
    fp0=np.zeros((N,3));fp1=np.zeros((N,3));lin=np.zeros((N,3));rem=np.zeros((N,3));remB=np.zeros((N,3))
    heat0=np.zeros(N);heat1=np.zeros(N);heat_lin=np.zeros(N);heat_rem=np.zeros(N);heat_remB=np.zeros(N)
    groups=[]
    for g in range(len(c)):
        cg, eg, jg =c[g], e[g], j[g]
        d0=float(eg+np.dot(cg,s0))
        dd=float(np.dot(cg,s1-s0))
        d1=d0+dd
        direct_d1=float(eg+np.dot(cg,s1))
        if abs(d1-direct_d1)>64*np.finfo(float).eps*max(1e-300,abs(d1)):
            raise AssertionError('inconsistent group denominator arithmetic')
        dlo=float(eg+np.dot(cg,slo)); dhi=float(eg+np.dot(cg,shi))
        if d0<=0 or d1<=0 or dlo<=0 or dhi<dlo:raise ValueError('undefined photon competition denominator')
        # Linear perturbation about original initial material, same fixed t and source.
        dn=n1-n0
        fg0=(jg*cg/d0)[None,:]*n0
        fg1=(jg*cg/d1)[None,:]*n1
        lg=(jg*cg/d0)[None,:]*(dn-n0*(dd/d0))
        rg=-(dd/d1)*lg
        # Correlated, cancellation-safe finite response rather than subtraction of two large rates.
        delta=lg+rg
        rawdelta=fg1-fg0
        fscale=np.maximum(np.maximum(np.abs(fg0),np.abs(fg1)),1e-300)
        if np.any(np.abs(rawdelta-delta)>128*np.finfo(float).eps*fscale):
            raise AssertionError('independent source rates and correlated delta incompatible')
        # Analytic all-box outer bound, with shared THREE group neutral moments.
        maxdd=max(abs(dlo-d0),abs(dhi-d0))
        maxdn=np.maximum(abs(lo-n0),abs(hi-n0))
        lbound=(jg*cg/d0)[None,:]*(maxdn+n0*(maxdd/d0))
        rbound=lbound*(maxdd/dlo)
        if np.any(np.abs(rg)>rbound+5e-14*np.maximum(1e-150, rbound)):
            raise AssertionError('original finite source outside accepted population outer box')
        fp0+=fg0;fp1+=fg1;lin+=lg;rem+=rg;remB+=rbound
        heat0+=fg0@(q[:,g]*EV_ERG);heat1+=fg1@(q[:,g]*EV_ERG)
        heat_lin+=lg@(q[:,g]*EV_ERG);heat_rem+=rg@(q[:,g]*EV_ERG)
        heat_remB+=rbound@(np.abs(q[:,g])*EV_ERG)
        p0=cg*s0/d0;p1=cg*s1/d1
        dS=s1-s0
        lshare=(cg*dS-p0*dd)/d0
        rshare=-(dd/d1)*lshare
        dlmax=np.maximum(np.abs(slo-s0),np.abs(shi-s0))
        lshareB=(cg*dlmax+p0*maxdd)/d0
        rshareB=(maxdd/dlo)*lshareB
        fracscale=np.maximum(np.maximum(np.abs(p0),np.abs(p1)),1e-300)
        if np.any(np.abs((p1-p0)-(lshare+rshare))>128*np.finfo(float).eps*fracscale):
            raise AssertionError('global photon group exact rational remainder')
        if abs((jg*np.sum(p0))+(jg*eg/d0)-jg)>2e-12*max(1,abs(jg)):
            raise AssertionError('original photon conservation')
        groups.append(dict(group=g,current_per_s=jg,denominator_initial=d0,denominator_accepted=d1,
            delta_denominator_over_initial=dd/d0,external_initial_fraction=eg/d0,
            initial_neutral_moments=s0.tolist(),accepted_neutral_moments=s1.tolist(),
            accepted_marginal_moments_lo=slo.tolist(),accepted_marginal_moments_hi=shi.tolist(),
            source_initial_fraction=p0.tolist(),source_accepted_fraction=p1.tolist(),
            exact_delta_species_events_per_s=(jg*(p1-p0)).tolist(),
            linear_species_events_per_s=(jg*lshare).tolist(),
            exact_nonlinear_remainder_events_per_s=(jg*rshare).tolist(),
            allX_accepted_box_remainder_bound_species_events_per_s=(jg*rshareB).tolist(),
            exact_local_photon_owner_residual_max=float(np.max(np.abs(delta-lg-rg))),
            source_inherited_excess_eV=q[:,g].tolist()))
    return dict(group_rows=groups,initial_photo_events_per_s=fp0,accepted_photo_events_per_s=fp1,
        change_photo_events_per_s=fp1-fp0,linear_change_photo_events_per_s=lin,
        exact_remainder_photo_events_per_s=rem,allX_remainder_bound_photo_events_per_s=remB,
        initial_photoheat_erg_per_s=heat0,accepted_photoheat_erg_per_s=heat1,
        linear_photoheat_erg_per_s=heat_lin,exact_remainder_photoheat_erg_per_s=heat_rem,
        allX_remainder_photoheat_bound_erg_per_s=heat_remB)
