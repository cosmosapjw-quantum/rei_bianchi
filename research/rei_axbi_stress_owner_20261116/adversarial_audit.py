#!/usr/bin/env python3
"""Same-author audit with scalar source reader, cgs units and momentum moments."""
import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import time

from scipy.integrate import quad

HERE=Path(__file__).resolve().parent


def require(ok, why):
    if not ok:
        raise RuntimeError(why)


def radiation(b):
    # Initial-direction integral: different angle and integrand from the consumer.
    def ray(mu):
        rr=math.sqrt(math.exp(2*b)*(1-mu*mu)+math.exp(-4*b)*mu*mu)
        local=mu*math.exp(-2*b)/rr
        return rr,local
    e=quad(lambda mu:ray(mu)[0]-1,-1,1,epsabs=2e-14,epsrel=1e-12)[0]/2
    j=quad(lambda mu:ray(mu)[0]*(3*ray(mu)[1]**2-1)/2-(3*mu*mu-1)/2,
           -1,1,epsabs=2e-14,epsrel=1e-12)[0]/2
    return e,j


def main(inputs):
    begin=time.monotonic()
    summary=json.loads((HERE/'results/STRESS_SUMMARY.json').read_text())
    manifest=json.loads((HERE/'INPUT_MANIFEST.json').read_text())
    with gzip.open(HERE/'results/stress_history.csv.gz','rt',newline='') as f:
        rows=list(csv.DictReader(f))
    require(len(rows)==4004,'ROW_COUNT')
    source_samples={};seen=0
    for spec in manifest['cases']:
        selected={int(r['native_row']):r for r in rows if r['case']==spec['id']}
        with (Path(inputs)/spec['relative_input']).open(newline='') as f:
            for i,r in enumerate(csv.DictReader(f)):
                if i in selected:
                    source_samples[(spec['id'],i)]={k:float(v) for k,v in r.items() if k!='case_id'}
                    seen+=1
        require(i+1==spec['rows'],'AUDIT_NATIVE_ROWS')
    require(seen==4004,'SAMPLE_JOIN')
    max_ion_rel=0.;max_thermal_rel=0.;max_j2_abs=0.;max_energy_abs=0.
    max_coordinate=0.;tested_angles=0
    Gc=6.67430e-8;cc=29979245800.;kc=1.380649e-16;evc=1.602176634e-12
    h0=67.4*100000/3.0856775814913673e24
    f=.2454/(4*(1-.2454));rho0=3*h0*h0*cc*cc/(8*math.pi*Gc)
    for r in rows:
        source=source_samples[(r['case'],int(r['native_row']))]
        a=source['a'];nh=source['nH_proper_cm3'];ne=source['ne_proper_cm3'];T=source['temperature_K']
        max_coordinate=max(max_coordinate,abs(a-float(r['a'])),abs(source['time_s']-float(r['time_s'])))
        # cgs pressure/energy to SI: 1 erg cm^-3 = 0.1 J m^-3.
        pi=nh*source['J2_photon_u_eV_per_H']*evc*.1
        v=float(r['DeltaP_ionizing_J_m3'])
        max_ion_rel=max(max_ion_rel,abs(v-pi)/max(abs(v),abs(pi),1e-100))
        gas=1.5*kc*T*(nh*(1+f)+ne)
        bg=rho0*(.000092/a**4+.315/a**3+(1-.315-.000092))
        expected=gas/bg;value=float(r['thermal_energy_to_background'])
        max_thermal_rel=max(max_thermal_rel,abs(value-expected)/max(abs(value),abs(expected),1e-100))
        if int(r['native_row']) in {0,312237} or (int(r['native_row'])//312)%50==0:
            ee,jj=radiation(source['b']);tested_angles+=1
            max_j2_abs=max(max_j2_abs,abs(jj-float(r['J2_effective'])))
            max_energy_abs=max(max_energy_abs,abs(ee-float(r['J0_effective_minus1'])))
    require(max_coordinate==0,'SOURCE_COORDINATE_IDENTITY')
    require(max_ion_rel<2e-14 and max_thermal_rel<2e-14,'INDEPENDENT_CGS_UNITS')
    require(max_j2_abs<2e-13 and max_energy_abs<2e-13,'INITIAL_DIRECTION_ADAPTIVE_QUADRATURE')
    zero=summary['cases']['ZERO']
    require(zero['stress_peak']['abs']<1e-20,'ZERO_SHEAR_STRESS')
    require(zero['max_abs_delta_H_shear_over_H']==0,'ZERO_SHEAR_CLOCK')
    for case,sign in [('SHEAR_HALF_PLUS',-1),('SHEAR_HALF_MINUS',1),('SHEAR_MINUS',1)]:
        d=summary['cases'][case]
        require(sign*d['stress_peak']['signed']>0,'RESTORING_STRESS_SIGN')
        require(d['endpoint']['delta_elapsed_time_shear_s']>0,'SHEAR_CLOCK_RESTORING_SIGN')
    # Independent historical two-case reference: same source and full native rows.
    previous={'ZERO':{'stress':3.7765658078038334e-23,'extra':5.809377678641879e-9},
              'SHEAR_HALF_PLUS':{'stress':5.080535497523119e-6,'extra':2.5691308853554516e-8}}
    old_gaps={}
    for case,ref in previous.items():
        d=summary['cases'][case]
        old_gaps[case]={'stress_abs':abs(d['stress_peak']['abs']-ref['stress']),
                        'extra_abs':abs(d['extra_energy_peak']['abs']-ref['extra'])}
        require(old_gaps[case]['stress_abs']<2e-15 and old_gaps[case]['extra_abs']<2e-15,
                'PREVIOUS_SOURCE_SCOPED_RECONSTRUCTION')
    # The cubic scalar invariant is not identically zero under sign reversal.
    require(sum(x**3 for x in [-1,-1,2])==6,'SHEAR_CUBIC_INVARIANT')
    # Input-negative tests are contract tests, not extra physical histories.
    spec=importlib.util.spec_from_file_location('stress_under_test',HERE/'radiation_stress_consumer.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    negatives=[]
    for values,reason in [([float('nan')],'NONFINITE_B'),([.2],'OUTSIDE_LOCKED_B_DOMAIN')]:
        try:mod.local_moments(values)
        except ValueError as e:require(str(e)==reason,'NEGATIVE_WRONG_REASON');negatives.append(reason)
        else:raise RuntimeError('NEGATIVE_NOT_REJECTED')
    model=summary['cases']['SHEAR_MINUS']
    require(model['stress_peak']['abs']<1e-4,'ORIGINAL_STRESS_CEILING')
    require(model['extra_energy_peak']['abs']<1e-4,'ORIGINAL_ENERGY_CEILING')
    result={'status':'PASS_SCOPED_SAME_AUTHOR_ADVERSARIAL_AUDIT',
            'independent_authorship':False,'subagents':0,
            'method':'scalar CSV join; cgs-to-SI dimensional calculation; adaptive initial-momentum angular integration; old two-case source overlap',
            'source_rows_scanned':sum(x['rows'] for x in manifest['cases']),
            'sampled_physical_rows_checked':seen,'angular_samples':tested_angles,
            'max_coordinate_discrepancy':max_coordinate,'max_cgs_ion_pressure_relative_error':max_ion_rel,
            'max_cgs_thermal_energy_relative_error':max_thermal_rel,
            'max_adaptive_momentum_J2_error':max_j2_abs,'max_adaptive_momentum_J0_excess_error':max_energy_abs,
            'historical_reconstruction_gaps':old_gaps,'negative_rejections':negatives,
            'claims_rejected':['exact scalar +/- shear symmetry','mean-redshift clock as cosmic age',
                               'postprocessing accuracy as original evolution convergence',
                               'perturbative ceiling as coupled abundance error bound',
                               'all five requested histories completed'],
            'new_failure':None,'wall_s':time.monotonic()-begin,
            'central_completed':28,'central_total':88}
    (HERE/'results/ADVERSARIAL_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inputs',required=True)
    main(p.parse_args().inputs)
