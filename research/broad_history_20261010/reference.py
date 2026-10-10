#!/usr/bin/env python3
"""Independent adaptive reference for the explicitly reduced R15/HG97-B lane.

No primary model or advance function is imported. Published rates and the
dust+Lambda+shear background are independently transcribed below. This is an
implementation comparison, not independent physical-model validation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
# Shared declared constants; these match the source-bound background convention.
MPC_CM = 3.0856775814913673e24
G_CGS = 6.67430e-8
M_PROTON_G = 1.67262192369e-24
C_CM_S = 2.99792458e10
SIGMA_T_CM2 = 6.6524587321e-25
FIELDS = ('Q', 'Nrec', 'Nemit', 'Nexcess', 'tau', 'elapsed_s')


def default_config():
    return dict(h=.6774, omega_m=.309, omega_lambda=.691,
                omega_b=.02230/.6774**2, Y=.2453,
                z_start=20., z_end=4., r=0., T_K=20000., C=3.,
                fesc=.2, Q_initial=0.)


def run_reference(config=None, epochs=801, *, rtol=2e-12, max_step=.01):
    """Return DOP853 dense-output samples and independent event observables.

    config uses the reference's declared names, not the primary implementation's
    API. epochs may be a positive count or an explicit monotonically increasing
    x=ln(a/a_i) grid including both endpoints.
    """
    cfg = default_config()
    if config is not None:
        unknown = set(config) - set(cfg)
        if unknown:
            raise ValueError(f'Unknown reference parameters: {sorted(unknown)}')
        cfg.update(config)
    if not all(math.isfinite(float(v)) for v in cfg.values()):
        raise ValueError('NONFINITE_CONFIG')
    if not (0 <= cfg['Q_initial'] < 1 and abs(cfg['r']) < 1
            and cfg['z_start'] > cfg['z_end'] > -1 and cfg['h'] > 0
            and cfg['omega_m'] > 0 and cfg['omega_lambda'] > 0
            and 0 < cfg['omega_b'] <= cfg['omega_m'] and 0 < cfg['Y'] < 1
            and cfg['T_K'] > 0 and cfg['C'] >= 0 and cfg['fesc'] >= 0):
        raise ValueError('CONFIG_DOMAIN')
    xi = 1.0 / (1.0 + cfg['z_start'])
    span = math.log((1.0 + cfg['z_start']) / (1.0 + cfg['z_end']))
    # H^2 = Hfid^2 Om a^-3 + Hfid^2 OL + s0^2 a^-6.
    Hfid = cfg['h'] * 1e7 / MPC_CM
    rho_b = cfg['omega_b'] * 3 * Hfid**2 / (8 * math.pi * G_CGS)
    nH0 = (1-cfg['Y']) * rho_b / M_PROTON_G
    nHe0 = cfg['Y'] * rho_b / (4 * M_PROTON_G)
    Hi = math.sqrt(Hfid**2 * (cfg['omega_m']/xi**3 + cfg['omega_lambda'])
                   / (1-cfg['r']**2))
    s0 = cfg['r'] * Hi * xi**3
    # Hui-Gnedin1997 AppendixA HII case-B rate, not the cooling coefficient.
    lam = 2 * 157807.0 / cfg['T_K']
    alpha = 2.753e-14 * lam**1.5 / (1+(lam/2.740)**.407)**2.242

    def rates(x):
        a = xi * math.exp(x)
        zp1 = 1/a
        H = math.sqrt(Hfid**2 * (cfg['omega_m']/a**3 + cfg['omega_lambda'])
                      + s0**2/a**6)
        # Robertson2015 SFRD and effective escaping photon production.
        sfr = .01376*zp1**3.26 / (1+(zp1/2.59)**5.68)
        source = cfg['fesc'] * 10**53.14 * sfr / MPC_CM**3 / nH0
        ne_inside = (nH0+nHe0)/a**3
        recombination = cfg['C'] * alpha * ne_inside
        return source/H, recombination/H, C_CM_S*SIGMA_T_CM2*ne_inside/H, 1/H

    def before(x, state):
        A, B, optical, clock = rates(x)
        q = state[0]
        return (A-B*q, B*q, A, 0., optical*q, clock)

    def overlap(x, state):
        return state[0]-1
    overlap.terminal = True
    overlap.direction = 1
    # Explicitly scaled absolute clock tolerance avoids forcing a sub-second
    # global clock error at early times while Q/counters remain tightly resolved.
    atol = np.array([2e-14,2e-14,2e-14,2e-14,2e-15,.01])
    y0 = [cfg['Q_initial'],0.,0.,0.,0.,0.]
    begin = time.perf_counter()
    pre = solve_ivp(before, (0.,span), y0, method='DOP853', rtol=rtol,
                    atol=atol, dense_output=True, events=overlap,
                    max_step=max_step)
    if not pre.success:
        raise RuntimeError(pre.message)
    hit = None
    post = None
    no_release = {'required':False}
    if len(pre.t_events[0]):
        hit = float(pre.t_events[0][0])
        yhit = pre.y_events[0][0].copy()
        if abs(yhit[0]-1) > 2e-13:
            raise RuntimeError('OVERLAP_ROOT_RESIDUAL')
        # Exact event-boundary representation, not clipping a failed abundance.
        yhit[0] = 1.
        source_at_hit, sink_at_hit, _, _ = rates(hit)
        ratio = source_at_hit/sink_at_hit if sink_at_hit else math.inf
        umin = ((1+cfg['z_end'])/2.59)**5.68
        derivative_lower = -.26 + 5.68*umin/(1+umin)
        # S/R increases in x over this interval: denominator H cancels.
        # This verifies that post-overlap release cannot occur for this config.
        no_release = dict(required=True, verified=derivative_lower>0 and ratio>=1,
                          source_over_recombination_at_overlap=ratio,
                          d_log_source_over_recombination_dx_lower=derivative_lower,
                          basis='analytic monotonic S/R over fixed source law')
        if not no_release['verified']:
            raise RuntimeError('POST_OVERLAP_RELEASE_NOT_EXCLUDED')

        def after(x, state):
            A, B, optical, clock = rates(x)
            if A < B:
                raise RuntimeError('POST_OVERLAP_SOURCE_BELOW_SINK')
            return (0.,B,A,A-B,optical,clock)

        post = solve_ivp(after,(hit,span),yhit,method='DOP853',rtol=rtol,
                         atol=atol,dense_output=True,max_step=max_step)
        if not post.success:
            raise RuntimeError(post.message)
    if isinstance(epochs,int):
        if epochs<2:
            raise ValueError('NEED_TWO_EPOCHS')
        grid = np.linspace(0.,span,epochs)
    else:
        grid = np.asarray(epochs,dtype=float)
        if (grid.ndim!=1 or len(grid)<2 or not np.isfinite(grid).all()
                or grid[0]!=0 or abs(grid[-1]-span)>1e-14 or np.any(np.diff(grid)<=0)):
            raise ValueError('GRID_DOMAIN')
    states = np.empty((len(FIELDS),len(grid)))
    pre_mask = np.ones(len(grid),dtype=bool) if hit is None else grid<=hit
    states[:,pre_mask] = pre.sol(grid[pre_mask])
    if post is not None:
        states[:,~pre_mask] = post.sol(grid[~pre_mask])
    if not np.isfinite(states).all():
        raise RuntimeError('NONFINITE_RESULT')
    q,rec,emitted,excess,tau,elapsed = states
    ledger = q-cfg['Q_initial']+rec+excess-emitted
    endpoint_pre = hit if hit is not None else span
    observables = {}
    for name,target in [('z50',.5),('z90',.9)]:
        if cfg['Q_initial'] <= target <= pre.sol(endpoint_pre)[0]:
            x_event = brentq(lambda x:float(pre.sol(x)[0])-target,0,endpoint_pre,
                             xtol=5e-15,rtol=1e-14)
            observables[name] = math.exp(-x_event)/xi-1
        else:
            observables[name] = None
    observables.update(z_overlap=None if hit is None else math.exp(-hit)/xi-1,
                       Q_final=float(q[-1]),tau_20_to_4=float(tau[-1]),
                       elapsed_s=float(elapsed[-1]),Nrec=float(rec[-1]),
                       Nemit=float(emitted[-1]),Nexcess=float(excess[-1]))
    metadata = dict(method='DOP853 + terminal overlap event + separate capped IVP',
                    rtol=rtol,atol=atol.tolist(),max_step_log_a=max_step,
                    nfev_pre=pre.nfev,nfev_post=0 if post is None else post.nfev,
                    accepted_steps_pre=len(pre.t)-1,
                    accepted_steps_post=0 if post is None else len(post.t)-1,
                    elapsed_wall_s=time.perf_counter()-begin,
                    no_release_proof=no_release,alpha_B_cm3_s=alpha,
                    nH0_cm3=nH0,nHe0_cm3=nHe0,s0_per_s=s0,
                    max_abs_photon_ledger=float(np.max(np.abs(ledger))),
                    min_Q=float(q.min()),max_Q=float(q.max()),
                    min_counters=float(states[1:4].min()),
                    source_imports='No primary model/advance import',
                    scope='reduced mean-volume filling factor; CR/RCT/HH OFF')
    rows = [dict(x=float(x),z=float(math.exp(-x)/xi-1),
                 **{f:float(states[j,i]) for j,f in enumerate(FIELDS)})
            for i,x in enumerate(grid)]
    return dict(config=cfg,metadata=metadata,observables=observables,history=rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs',type=int,default=801)
    args = parser.parse_args()
    out = HERE/'evidence'
    out.mkdir(exist_ok=True)
    sources = [Path(__file__).resolve(),HERE/'SCIENTIFIC_CONTRACT.md',
               HERE/'EXTERNAL_SOURCE_CONTRACT.md']
    before_hash = {str(p.relative_to(HERE)):sha(p) for p in sources}
    start = time.perf_counter()
    products = []
    for r,tag in [(0.,'r0'),(.1,'r0p1')]:
        result = run_reference({'r':r},epochs=args.epochs)
        result['producer_sha256'] = before_hash
        json_path = out/f'REFERENCE_{tag}.json'
        csv_path = out/f'REFERENCE_{tag}.csv'
        json_path.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        with csv_path.open('w',newline='') as file:
            writer = csv.DictWriter(file,fieldnames=list(result['history'][0]))
            writer.writeheader()
            writer.writerows(result['history'])
        products.extend([json_path,csv_path])
        print(json.dumps(dict(case=tag,observables=result['observables'],
                              metadata=result['metadata']),allow_nan=False))
    after_hash = {str(p.relative_to(HERE)):sha(p) for p in sources}
    if before_hash != after_hash:
        raise RuntimeError('REFERENCE_SOURCE_CHANGED_DURING_RUN')
    receipt = dict(schema='rei_accel_independent_reference_execution_v1',
                   command=[sys.executable,*sys.argv],exit_code=0,
                   python=platform.python_version(),numpy=np.__version__,
                   scipy=scipy.__version__,platform=platform.platform(),
                   producer_hashes_before=before_hash,producer_hashes_after=after_hash,
                   elapsed_wall_s=time.perf_counter()-start,
                   output_sha256={p.name:sha(p) for p in products},
                   contributor_role='reference implementation; not final reviewer',
                   independence='Separately transcribed equations, adaptive integration and event cap; same published model and declared constants')
    (out/'REFERENCE_EXECUTION.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':
    main()
