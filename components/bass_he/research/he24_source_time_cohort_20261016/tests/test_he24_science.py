"""HE24 source-timing theorem and immutable experimental readback tests.
These tests do not promote the conditional light pilot to full cosmological EoR.
"""
from __future__ import annotations
import hashlib,json,math,sys
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import quad

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from source_age_bias import phi1_minus, events

@pytest.mark.parametrize('tau',[0.,1e-12,1e-8,1e-5,0.0001,0.01,.1,1.,4.,16.,64.,256.])
def test_phi1_exact_integral(tau):
    actual=float(phi1_minus(np.asarray(tau)))
    exact=quad(lambda u:math.exp(-tau*u),0.,1.,epsabs=2e-13,epsrel=2e-13)[0]
    assert math.isclose(actual,exact,rel_tol=3e-14,abs_tol=5e-16)

@pytest.mark.parametrize('tau',[0.,1e-12,1e-8,.01,1.,3.,10.,64.,256.])
def test_distributed_emission_survival_not_less_than_old(tau):
    frac=float(phi1_minus(np.asarray(tau)))
    assert math.exp(-tau)-2e-16<=frac<=1.+2e-16
    if tau>.0001:
        assert frac>math.exp(-tau)

def test_reject_invalid_tau():
    for tau in (-1.,float('nan'),float('inf')):
        with pytest.raises(ValueError,match='HE24_TAU'):
            phi1_minus(np.array([tau]))

def test_competing_species_conserves_photons_and_heat():
    tau=np.array([0.,1.,10.])
    src=np.array([.2,.5,.3])
    rates=np.array([[0.,0.,0.],[1.,2.,0.],[5.,3.,2.]])
    energy=np.array([15.,40.,80.]);b=np.array([13.598434599702,24.587389011,54.41776])
    r=events(tau,src,rates,energy,b)
    for lane in ['midpoint','uniform']:
        a=r['absorbed_'+lane]
        assert np.all(a>=0)
        assert abs(r['surviving_'+lane]+a.sum()-1)<5e-16
        assert np.all(r['heat_'+lane]>=0)
        assert math.isclose(float(np.dot(a,b)+r['heat_'+lane].sum()),
           float(np.sum(src[:,None]*(1-(np.exp(-tau) if lane=='midpoint' else phi1_minus(tau)))[:,None]*np.divide(rates,rates.sum(axis=1)[:,None],out=np.zeros_like(rates),where=rates.sum(axis=1)[:,None]>0)*energy[:,None])),
           abs_tol=1e-12)

def read_sample(rel):return json.loads((ROOT/'results'/rel).read_text())

def test_original_he23_byte_identity_and_replay_against_saved_checkpoint():
    j=read_sample('time_replay/q+0.0000_m4_n8/STATUS.json')['result']
    # exact measured native values from immutable HE23 q0,m4,n8 checkpoint
    assert j['temperature_final_K']==8.241604377695229
    assert j['native_evaluator_calls']==104
    assert j['absorbed']==[3.204082552502866e-06,2.54271592711306e-07,1.4499797283305684e-14]

def test_tight_newton_does_not_explain_source_timing_difference():
    n=16
    orig=read_sample(f'time_replay/q+0.0000_m4_n{n}/STATUS.json')['result']
    tight=read_sample(f'tight_newton/q+0.0000_m4_n{n}/RESULT.json')['result']
    alternate=read_sample(f'continuous_birth/q0_m4_n{n}/RESULT.json')['result']
    assert abs(orig['temperature_final_K']-tight['temperature_final_K'])<2e-10
    assert abs(orig['temperature_final_K']-alternate['temperature_final_K'])>1e-3
    assert abs(tight['energy_defect'])<abs(orig['energy_defect'])

def test_continuous_birth_actual_native_6_scales_and_shrinking_differences():
    ns=(2,4,8,16,32,64)
    new=[];old=[]
    for n in ns:
        original=read_sample(f'time_replay/q+0.0000_m4_n{n}/STATUS.json')
        alt=read_sample(f'continuous_birth/q0_m4_n{n}/RESULT.json')
        assert original['status']==alt['status']=='PASS_SCOPED'
        assert alt['result']['number_defect']<1e-16
        assert abs(alt['result']['energy_defect'])<4e-12
        assert alt['max_photo_ledger']<5e-19
        assert alt['result']['max_support_crossing']==0
        new.append(alt['result']['temperature_final_K'])
        old.append(original['result']['temperature_final_K'])
    newdiff=np.abs(np.diff(new));olddiff=np.abs(np.diff(old))
    assert np.all(newdiff[1:]<newdiff[:-1])
    assert olddiff[1]>olddiff[0]
    assert max(newdiff)<2.5e-7
    assert olddiff[-1]>1e-4

def test_signed_shear_and_energy_alternative_controls():
    vals={}
    for q in (-.005,0.,.005):
        tag=f'q{q:+.4f}_m4_n16' if q else 'q0_m4_n16'
        j=read_sample('continuous_birth/'+tag+'/RESULT.json')
        assert j['status']=='PASS_SCOPED'
        vals[q]=j['result']['temperature_final_K']
    assert abs(vals[-.005]-vals[0.])<1e-10
    assert abs(vals[.005]-vals[0.])<1e-10
    t={}
    for m in (4,8,16):
        tag='q0_m4_n16' if m==4 else f'q+0.0000_m{m}_n16'
        t[m]=read_sample('continuous_birth/'+tag+'/RESULT.json')['result']['temperature_final_K']
    assert abs(t[16]-t[8])<5e-11
    assert abs(t[8]-t[4])<5e-10

def test_first_cohort_stiffness_excludes_asymptotic_small_tau():
    j=read_sample('FIRST_COHORT_OPTICAL_DEPTH.json')
    rows=j['results']
    assert [i['n'] for i in rows]==[2,4,8,16,32,64]
    assert rows[-1]['tau_mean_weighted']>1.
    assert rows[-1]['fraction_tau_ge_1']>.8
    assert rows[0]['fraction_tau_ge_10']>.99

def test_first_cohort_uniform_source_absorption_bias_positive():
    j=read_sample('SOURCE_AGE_BIAS.json')
    rows=j['results']
    for r in rows:
        assert r['surviving_uniform']>r['surviving_midpoint']
        assert r['overabsorbed_total_fraction_of_emission']>0
        assert abs(r['number_ledger_midpoint'])<1e-13
        assert abs(r['number_ledger_uniform'])<1e-13

def test_binary_source_identity_from_prior_readback():
    j=read_sample('time_replay/SUMMARY.json')
    assert j['binary_sha256']=='981ad6dde18be7951c6b0200a49e6482b0e6fae644437197375bdd18ced5eafe'
    assert j['source_owner']=='f7830e2f55e7a1938bc3c98f61b60651f8dae474'
