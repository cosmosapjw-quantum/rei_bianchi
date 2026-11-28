import copy
import pytest
from wu088_hh.promotion import validate_science_regression, sanitize_trusted_native_environment


def good():
    rows=[]
    for z in (16.0,64.0):
        for k in range(3):
            rows.append(dict(z=z,pair=[k,k],numerical_array_exact_equal=True,
                             max_abs_component_delta=0.0,observed_threads=12))
    return dict(schema='WU088_R31M_SCIENCE_RESOLUTION_NATIVE_REGRESSION_V1',
                tuning_profile_sha256='a'*64,build_key='b'*64,
                selected=dict(kernel_threads=12,processes=2,use_smt=True),
                rows=rows,all_exact=True,production_provider_promoted=False,
                promotion_eligible_pending_independent_review=True,
                heavy_pair_state_mutation=False,
                status='PASS_REPRESENTATIVE_NATIVE_EXACTNESS_NOT_PROMOTED')


def test_scoped_foreign_promotion_requires_exact_science_rows_and_matching_identity():
    r=validate_science_regression(good(),profile_sha256='a'*64,build_key='b'*64)
    assert r['status']=='PASS_SCOPED_FOREIGN_KERNEL_PROMOTION_ELIGIBLE'
    assert r['scope']=='FOREIGN_KERNEL_HEAVY_H_SOURCE_ONLY'
    assert r['kernel_threads']==12
    assert r['rows']==6


def test_scoped_foreign_promotion_rejects_any_nonexact_row():
    x=good();x['rows'][4]['numerical_array_exact_equal']=False
    with pytest.raises(ValueError,match='exact'):
        validate_science_regression(x,profile_sha256='a'*64,build_key='b'*64)


def test_scoped_foreign_promotion_rejects_profile_or_build_drift():
    with pytest.raises(ValueError,match='profile'):
        validate_science_regression(good(),profile_sha256='c'*64,build_key='b'*64)
    with pytest.raises(ValueError,match='build'):
        validate_science_regression(good(),profile_sha256='a'*64,build_key='c'*64)

def test_trusted_native_subprocess_env_removes_only_loader_injection_vars():
    src={'PATH':'/usr/bin','LD_LIBRARY_PATH':'/tmp/lib','LD_PRELOAD':'/tmp/pre.so','KEEP':'yes'}
    out=sanitize_trusted_native_environment(src,R31K_RUNTIME_ROOT='/runtime')
    assert 'LD_LIBRARY_PATH' not in out
    assert 'LD_PRELOAD' not in out
    assert out['PATH']=='/usr/bin'
    assert out['KEEP']=='yes'
    assert out['R31K_RUNTIME_ROOT']=='/runtime'
    assert src['LD_LIBRARY_PATH']=='/tmp/lib'
    assert src['LD_PRELOAD']=='/tmp/pre.so'
