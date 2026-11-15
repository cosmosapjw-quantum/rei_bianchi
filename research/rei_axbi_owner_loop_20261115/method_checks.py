#!/usr/bin/env python3
"""Targeted geometry/quadrature and negative consumer-contract checks."""
import json
import math
from pathlib import Path
import tempfile

import numpy as np
import pandas as pd

from physics_consumer import (COLS, FHE, HERE, C_CM_S, interp, load_case,
                              require, validate_frame)


def main():
    mu, weights = np.polynomial.legendre.leggauss(8)
    weights = weights/2
    moments = {str(k): float(np.sum(weights*mu**k)) for k in [0, 1, 2, 4, 6]}
    exact = {'0': 1., '1': 0., '2': 1/3, '4': 1/5, '6': 1/7}
    require(np.min(weights)>0, 'ORIGINAL_GL8_POSITIVITY')
    require(max(abs(moments[k]-exact[k]) for k in exact)<2e-14, 'ORIGINAL_GL8_ISOTROPY')
    midpoint = -1+(np.arange(8)+.5)/4
    donor_weights = (1+(4/63)*(midpoint**2-21/64))/8
    donor = {'midpoint_mu2': float(np.mean(midpoint**2)),
             'corrected_mu2': float(np.sum(donor_weights*midpoint**2)),
             'min_corrected_weight': float(np.min(donor_weights)),
             'applied_to_original_GL8': False}
    require(abs(donor['corrected_mu2']-1/3)<2e-14, 'REC_SOURCE_GRID_MOMENT')
    a0 = 1/21; energy0 = 13.6
    d = pd.read_csv(HERE/'results/abundances.csv.gz',float_precision='round_trip')
    max_energy_error, max_jacobian_error = 0., 0.
    cases = {}
    for case, f in d.groupby('case',sort=True):
        checks = []
        for _,row in f.iloc[::40].iterrows():
            aa, b = float(row.a), float(row.b)
            D = np.exp(2*b)*(1-mu**2)+np.exp(-4*b)*mu**2
            formula = energy0*a0/aa*np.sqrt(D)
            # Independent route: conserved covariant momentum + tetrad norm.
            p_x = a0*energy0/C_CM_S*np.sqrt(1-mu**2)
            p_z = a0*energy0/C_CM_S*mu
            norm = C_CM_S*np.sqrt((p_x/(aa*np.exp(-b)))**2+
                                 (p_z/(aa*np.exp(2*b)))**2)
            error = float(np.max(abs(formula/norm-1)))
            jac_error = abs(float(np.sum(weights*D**(-1.5)))-1)
            max_energy_error=max(max_energy_error,error)
            max_jacobian_error=max(max_jacobian_error,jac_error)
            checks.append({'a':aa,'b':b,'mean_energy_eV_test_photons':float(np.sum(weights*formula)),
                           'energy_formula_vs_momentum_relative':error})
        cases[case]={'geometry_samples':len(checks),'endpoint':checks[-1]}
    require(max_energy_error<2e-14,'BASS_GEODESIC_CONSUMER')
    require(max_jacobian_error<2e-14,'ANGULAR_JACOBIAN_CALIBRATION')
    negatives=[]
    def rejects(label, fn):
        try:fn()
        except ValueError as e:negatives.append({'case':label,'rejected':True,'reason':str(e)})
        else:raise RuntimeError('NEGATIVE_CASE_ACCEPTED '+label)
    rejects('outside_source_domain',lambda:interp([1.1],np.array([0.,1.]),np.array([2.,3.])))
    rejects('nonmonotone_axis',lambda:interp([.2],np.array([0.,0.,1.]),np.array([1.,2.,3.])))
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'wrong.csv';path.write_text('not the original source\n')
        spec={'relative_input':'wrong.csv','bytes':path.stat().st_size,'sha256':'0'*64}
        rejects('modified_source_bytes',lambda:load_case(tmp,spec))
    aa=np.array([1/21,.1,.2]);nh=2e-7/aa**3;x=np.array([.0002,.1,.5])
    fixture=pd.DataFrame({'case_id':['CHECK']*3,'q_ref':[0.]*3,'time_s':[0.,1.,2.],
        'a':aa,'zbar':1/aa-1,'b':[0.]*3,'H_per_s':[1e-17]*3,'s_per_s':[0.]*3,
        'x_HI':1-x,'x_HII':x,'x_HeI':[1.]*3,'x_HeII':[0.]*3,'x_HeIII':[0.]*3,
        'nH_proper_cm3':nh,'ne_proper_cm3':nh*x,'temperature_K':[10.]*3})
    spec={'id':'CHECK','q_ref':0.,'rows':3}
    validate_frame(fixture,spec)
    bad=fixture.copy();bad['ne_proper_cm3']*=aa**3
    rejects('comoving_ne_as_proper',lambda:validate_frame(bad,spec))
    bad_time=fixture.copy();bad_time['time_s']=[0.,1.,1.]
    rejects('repeated_clock',lambda:validate_frame(bad_time,spec))
    bad_temp=fixture.copy();bad_temp['temperature_K']=[10.,-1.,10.]
    rejects('negative_temperature',lambda:validate_frame(bad_temp,spec))
    result={'status':'PASS_SCOPED_CONSUMER_METHODS','original_GL8_moments':moments,
        'REC_midpoint_rule_comparison':donor,
        'BASS_characteristic_original_background_check':cases,
        'characteristic_max_relative_difference':max_energy_error,
        'angular_jacobian_max_error':max_jacobian_error,
        'negative_cases':negatives,'negative_case_count':len(negatives),
        'actual_coupled_chemistry_rerun':False,
        'test_photons_are_actual_source_photon_population':False,
        'source_angular_grid_mutated':False,
        'author_independence':False,'subagents':0}
    (HERE/'results/METHOD_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
