from pathlib import Path
import hashlib
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[1]
AUTH=ROOT/'authority_m3'

def load_adapter():
    spec=importlib.util.spec_from_file_location('m3_h0_authority',AUTH/'m3_h0_authority.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m

def test_m3_h0_exact_source_identity():
    m=load_adapter()
    assert m.verify_sources()==m.EXPECTED
    assert m.EXPECTED=={
      'FROZEN_INPUTS.npz':'8482d2854ab620c58bb1d7a7a45cf88eb71fd75081242263a9ef48927f0a282c',
      'h0_fused.cpp':'d019713f8a9c6e864d60cc796104a0cdef629e491e6ab8de757995aa4f3672f2',
      'radial_wide.cpp':'2c20c3e3de8a69a64363806512dde8b3dbae6b818c8aec458893906d9b21399a',
    }

def test_m3_h0_manifest_and_regression_are_scoped():
    manifest=json.loads((AUTH/'M3_AUTHORITY_MANIFEST.json').read_text())
    reg=json.loads((AUTH/'M3_H0_SANDBOX_REGRESSION.json').read_text())
    assert manifest['status']=='SANDBOX_VERIFIED_EXACT_H0_MINIMAL_CLOSURE'
    assert manifest['claim_ceiling']['m3_authority_blocker_closed'] is True
    assert manifest['claim_ceiling']['full_pair_equivalence_on_ncp'] is False
    assert reg['status']=='PASS_EXACT_H0_ADAPTER_VS_HISTORICAL_CP4_H0FUSED'
    assert reg['all_output_array_equal'] is True
    assert reg['all_sumabs_array_equal'] is True
    assert len(reg['rows'])==12
