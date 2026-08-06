from __future__ import annotations
import importlib.util,sys
from pathlib import Path
import numpy as np
SCRIPT=Path(__file__).parents[1]/'analysis/build_atomic_moment_lock.py'
spec=importlib.util.spec_from_file_location('atomic_lock',SCRIPT); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
SOURCE=Path(__file__).parents[1]/'inputs/canonical_b2c2a_r1_src/multigroup_hhe_transmission.py'
physics=mod.load_module(SOURCE)

def test_unsupported_pairs_are_structural_zeros():
    for s,g in [('HeI','G1'),('HeII','G1'),('HeII','G2a'),('HeII','G2b')]:
        r=mod.compute(physics,s,g,n=96)
        assert not r['supported']; assert r['gray_sigma_cm2']==0.0
        assert all(x['absorbed_fraction']==0.0 and x['excess_eV']==0.0 for x in r['rows'])

def test_supported_moments_are_inside_group_energy_bounds():
    for s in mod.SUPPORT:
        for g in mod.SUPPORT[s]:
            r=mod.compute(physics,s,g,n=192)
            lo,hi=mod.GROUPS[g]; eth=mod.THRESH[s]
            assert r['gray_sigma_cm2']>0
            assert 0 <= r['thin_excess_eV'] <= hi-eth
            assert 0 <= r['thick_excess_eV'] <= hi-eth
            vals=np.array([x['excess_eV'] for x in r['rows']])
            assert np.all(np.diff(vals)>=-1e-8)

def test_primary_G3_is_exact_zero():
    occ=physics.source_occupation('MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD',n=128)
    assert occ['G3']==0.0
