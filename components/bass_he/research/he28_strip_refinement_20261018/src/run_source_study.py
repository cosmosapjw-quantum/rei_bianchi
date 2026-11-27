"""Frozen future-kernel controls, independent of native chemistry and tables."""
from __future__ import annotations
import argparse
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
import json
import time
import numpy as np
from refined_source import RefinedSourceModel, GridSpec, RESEARCH
from physics import sigma_cm2, shape, Y_HE, BIND_EV, C_CM_S, A_BIRTH

FEATURES = ('survival', 'surviving_energy_eV', 'HI_event', 'HeI_event',
            'HeII_event', 'HI_heat_eV', 'HeI_heat_eV', 'HeII_heat_eV')


def features(energy, age, nh):
    lam = C_CM_S*nh*sigma_cm2(energy)*np.array([1-1e-5, Y_HE*(1-1e-5), Y_HE*1e-5])
    total = lam.sum(axis=1)
    survival = np.exp(-total*age)
    loss = -np.expm1(-total*age)
    events = loss[:, None]*np.divide(lam,total[:, None],out=np.zeros_like(lam),where=total[:, None]>0)
    return np.c_[survival, energy*survival, events, events*(energy[:, None]-BIND_EV)]


@lru_cache(maxsize=128)
def reference(age, nh, order):
    z, w = np.polynomial.legendre.leggauss(order)
    ee, ww = [], []
    for lo, hi in zip((13.6,24.59,54.42), (24.59,54.42,100.)):
        ee.extend((lo+hi)/2+(hi-lo)/2*z)
        ww.extend((hi-lo)/2*w)
    e = np.array(ee); weight = np.array(ww)*shape(e)
    return weight@features(e,age,nh)/weight.sum()


def run(output, signed=False):
    output = Path(output); output.mkdir(parents=True,exist_ok=False)
    rows = []; start=time.perf_counter()
    qs = (-.005,0.,.005) if signed else (0.,)
    for q in qs:
        for m in (4,8,16):
            for strips in (1,2,4,8,16):
                spec=GridSpec(q=q,m=m,strips=strips,angles=4)
                model=RefinedSourceModel(None,spec=spec,tabulate=False)
                for frac in (.1,.37,.9):
                    t=frac*model.t_end; x=model.x(t)
                    nh=1.89819845071402689e-7/(A_BIRTH*np.exp(x))**3
                    raw, report=model.source_moments(t)
                    e=model.geometry(t)[0]
                    for age in (1e10,1e11):
                        ref=reference(age,nh,128); check=reference(age,nh,256)
                        if np.max(abs(ref-check))>2e-13:
                            raise AssertionError('HE28_REFERENCE_STABILITY')
                        actual=raw@features(e,age,nh)/raw.sum()
                        rows.append(dict(**asdict(spec),time_fraction=frac,age_s=age,
                            photon_modes=model.K,reference=ref.tolist(),actual=actual.tolist(),
                            abs_defect=abs(actual-ref).tolist(),
                            source_moment_error=report['max_relative_moment_error'],
                            local_source_moment_error=report['max_angle_band_relative_error'],
                            reference_stability=float(np.max(abs(ref-check)))))
                print(q,m,strips,'done',flush=True)
    grouped=[]
    for q in qs:
        for m in (4,8,16):
            for strips in (1,2,4,8,16):
                rr=[r for r in rows if (r['q'],r['m'],r['strips'])==(q,m,strips)]
                grouped.append(dict(q=q,m=m,strips=strips,modes=rr[0]['photon_modes'],
                                    max_abs_defect=np.max([r['abs_defect'] for r in rr],axis=0).tolist()))
    # Exact numerical replay of the inherited q=0/r=1 future-kernel comparison.
    prior=json.loads((RESEARCH/'he27_sourcecut_native_20261016/results/FUTURE_KERNEL_CONTROL.json').read_text())
    parity=[]
    for old in prior['cases']:
        current=next(r for r in rows if r['q']==0 and r['m']==old['m'] and r['strips']==1
                     and r['time_fraction']==old['time_fraction'] and r['age_s']==old['frozen_age_s'])
        parity.append(float(max(abs(np.array(current['actual'])-old['admitted']))))
    summary=dict(scope='SOURCE_ONLY_FROZEN_FUTURE_KERNEL_NO_NATIVE_CHEMISTRY',
        features=FEATURES,cases=len(rows),groups=grouped,
        max_source_moment_error=max(r['source_moment_error'] for r in rows),
        max_angle_band_error=max(r['local_source_moment_error'] for r in rows),
        inherited_cases_checked=len(parity),inherited_max_abs_difference=max(parity),
        wall_s=time.perf_counter()-start,
        native_runs=0,native_acceptance='NOT_RUN',continuous_spectral_claim='HOLD')
    for name,data in [('CASES.json',rows),('SUMMARY.json',summary)]:
        with (output/name).open('x') as f:json.dump(data,f,indent=2,allow_nan=False)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--signed',action='store_true')
    args=ap.parse_args();run(args.out,args.signed)
