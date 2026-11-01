#!/usr/bin/env python3
"""Real REI 26-event original-source finite-photon-share remainder atlas.

Loads PR332's SHA-locked ORIGINAL four-photon-group owner; does not integrate
an IVP, alter population sources, or replace the accepted parent.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from finite_remainder import finite_source_certificate, f

NODES=46080
SRC_ID="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_ID="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
ORIGINAL_PR332_HEAD="2e3305c8ba9bff5d00412c5d79d9c1aa1e6f6e9a"
REPORTED="28/88"


def load_orig(repo):
    path=repo/'research/rei_igm_tick160_global_photon_20261101/photon_global_feedback.py'
    spec=importlib.util.spec_from_file_location("actual_owner_pr332_global_photon",path)
    if spec is None or spec.loader is None:raise RuntimeError("PR332 source absent")
    o=importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name]=o
    spec.loader.exec_module(o)
    return o


def ceil_f(q:F)->float:
    if q<0:raise ValueError('negative upper')
    x=float(q)
    if not math.isfinite(x):raise OverflowError('rational out of IEEE range')
    if F(x)<q:x=math.nextafter(x,math.inf)
    assert F(x)>=q
    return x


def fl(q:F)->float:
    return float(q)


def run(repo,out):
    orig=load_orig(repo)
    if orig.SOURCE_SHA != SRC_ID or orig.STATE_SHA != STATE_ID:
        raise ValueError("source provenance drift")
    source,mod,model,p0,p1,frozen,t160=orig.context(repo)
    # Same physically accepted source parent. Three lane state array identities were
    # verified by orig.context and are not tripled as independent data.
    if p1.shape!=(NODES,5):raise ValueError('incorrect original node count')
    s0=[F(float(np.sum(p1[:,j],dtype=np.longdouble))) for j in orig.INDICES]
    sb=[mod.iv.sum_interval(mod._I(frozen['lo'][:,j],frozen['hi'][:,j])) for j in orig.INDICES]
    slo=[F(float(q.lo)) for q in sb];shi=[F(float(q.hi)) for q in sb]
    # A few ulps are possible when converting longdouble sums and interval sums.
    # Conservatively include the base point; fail for a material inconsistency.
    union_expansion=[]
    for j in range(3):
        gap=max(slo[j]-s0[j], s0[j]-shi[j], F(0))
        if gap>abs(s0[j])*F(1,10**9):raise ValueError('significant original moment enclosure disagreement')
        union_expansion.append(fl(gap / s0[j]))
        slo[j]=min(slo[j],s0[j]);shi[j]=max(shi[j],s0[j])
    base=mod.trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=repo,lane=orig.LANES[0])
    duration=float(base.forcing.duration_seconds(0))
    dt=duration/F(orig.NT)
    tick0=duration*orig.L/orig.NT
    gam=float(mod.sdirk.GAMMA)
    sites=(('begin',tick0),('quarter_sdirk',tick0+gam*float(dt)/2),
           ('half',tick0+float(dt)/2),('full_sdirk',tick0+gam*float(dt)),
           ('end',tick0+float(dt)))
    countH=F(float(model.n_h_total))
    if countH<=0:raise ValueError('nonpositive H inventory')
    rows=[];summaries=[]
    for tag,t in sites:
        forcing=model.forcing_bounds(t,t)
        z0=F(orig.midpoint(forcing.z));zlo=F(float(forcing.z.lo));zhi=F(float(forcing.z.hi))
        if not -1<zlo<=z0<=zhi:raise ValueError('nonexpanding or invalid original z bounds')
        c0=np.asarray(orig.coefficients(model,mod,float(z0)),float)
        ratio_lo=((1+zlo)/(1+z0))**2
        ratio_hi=((1+zhi)/(1+z0))**2
        total_absbound=F(0); total_heatbound=F(0); total_remainder=F(0)
        for g in range(4):
            c=[F(float(v)) for v in c0[g]]
            elo=F(float(forcing.external_subgrid[g].lo));ehi=F(float(forcing.external_subgrid[g].hi))
            emid=F(orig.midpoint(forcing.external_subgrid[g]))
            # SOURCE FORCING: represented original c_mid and scale coefficient (1+z)^2.
            A0=[c[j]*s0[j] for j in range(3)]+[emid]
            Alo=[c[j]*ratio_lo*slo[j] for j in range(3)]+[elo]
            Ahi=[c[j]*ratio_hi*shi[j] for j in range(3)]+[ehi]
            cert=finite_source_certificate(A0,Alo,Ahi)
            jhi=F(float(forcing.current[g].hi))
            if jhi<0:raise ValueError('negative original owner photon current')
            photons=sum(cert['rows'][s]['delta_abs_bound'] for s in range(3))*jhi
            # This is an instantaneous frozen-state source-share sensitivity;
            # it excludes local N_i numerator changes and all subsequent thermal/chemical evolution.
            heat=F(0)
            for s in range(3):
                excess=F(float(model.excess_eV[s,g]))
                if excess<0: raise ValueError('negative physical excess energy')
                heat+=jhi*cert['rows'][s]['delta_abs_bound']*excess*F(float(mod.rim.EV_ERG))
            total_absbound+=photons
            total_heatbound+=heat
            total_remainder+=jhi*sum(cert['rows'][s]['remainder_abs_bound'] for s in range(3))
            rows.append({
                'site':tag,'time_s':float(t),'g':g,'z':float(z0),
                'p0':list(map(fl,[x['p0'] for x in cert['rows']])),
                'p_outer_lower':list(map(fl,[x['pmin'] for x in cert['rows']])),
                'p_outer_upper':list(map(ceil_f,[x['pmax'] for x in cert['rows']])),
                'max_abs_delta_share_upward':list(map(ceil_f,[x['delta_abs_bound'] for x in cert['rows']])),
                'max_abs_exact_nonlinear_remainder_upward':list(map(ceil_f,[x['remainder_abs_bound'] for x in cert['rows']])),
                'eta_lower':float(cert['eta_min']),'eta_upper':ceil_f(max(F(0),cert['eta_max'])),
                'eta_max_abs_upward':ceil_f(cert['eta_abs_bound']),
                'photon_share_total_photons_per_s_bound':ceil_f(photons),
                'heat_share_erg_per_s_bound':ceil_f(heat),
                'structural_zero_channels':[j for j in range(4) if Ahi[j]==0],
                'original_current_hi_per_s':float(jhi),
                'original_h_inventory':float(countH)
            })
        summaries.append({
            'site':tag,'same_parent_and_forcing':True,'shared_parent_source_nodes':NODES,
            'per_h_source_share_tick_abs_count_upper':ceil_f(total_absbound*dt/countH),
            'per_h_source_share_tick_heat_erg_upper':ceil_f(total_heatbound*dt/countH),
            'per_h_source_share_tick_heat_eV_upper':ceil_f(total_heatbound*dt/countH/F(float(mod.rim.EV_ERG))),
            'per_h_nonlinear_second_order_photon_count_upper':ceil_f(total_remainder*dt/countH),
        })
    result={
        'schema':'REI_26EVENT_TICK160_EXACT_FINITE_GLOBAL_PHOTON_COMPETITION_REMAINDER_V1',
        'source_owner':'cosmosapjw-quantum/rei_bianchi',
        'original_source_archive_sha256':SRC_ID,
        'original_accept_state_array_sha256':STATE_ID,
        'parent_pr332_head':ORIGINAL_PR332_HEAD,
        'original_parent_tick':160,'original_full_interval_ticks':131072,
        'science_status':'DERIVED_EXACT_REPRESENTED_GROUP_SOURCE_FROZEN_PARENT_BOX_NONCANONICAL',
        'scope':'ORIGINAL_FROZEN_PARENT_MARGINAL_BOX_X, ORIGINAL_REPRESENTED_SOURCE_COEFFICIENTS AND FOUR_PHOTON_GROUPS, FIVE_FIXED_CLOCK_PROBES; NOT ACTUAL TIME_EVOLVED_STAGE_PARENT_X',
        'original_source_26event_validity':'original instantaneous photo-group owner only; no complete 26-event map Jacobian or remainder',
        'frozen_original_local_error':2.1245050576368385e-4,'strict_original_gate':2e-4,
        'central_dag_reported':REPORTED,'working_dag_reported':'33/88',
        'canonical_delta':0,'first_interval':'BLOCKED_MINIMUM_STEP',
        'node_count':NODES,'unique_physical_parent_instances':1,
        'moment_box_union_expansion_relative':union_expansion,
        'source_group_rows':rows,'clock_site_totals':summaries,
        'photon_conservation':'exact 4-channel algebra including E_external; all finite source path shares sum to 1',
        'interpretation':'finite rate/share outer bounds, no time-integrated photon or full chemical flow claim; no tolerance change',
        'new_owner_ivps':0,'no_merge':True,'no_force_push':True,'auto_next_node':False,'production':'HOLD'
    }
    out.mkdir(parents=True,exist_ok=True)
    (out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
    print('ACTUAL_SOURCE_FINITE_REMAINDER',json.dumps({'rows':len(rows),'sites':summaries,'central':'28/88','canonical_delta':0},sort_keys=True))
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2]);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();run(a.repo.resolve(),a.out.resolve())
