"""Wire/schema tests only, no claim to have executed real Rust microphysics."""
from pathlib import Path
import sys
import pytest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from he21_photo import Y_HE
from he22_native_client import parse_native_point


def valid_native_text():
    nh=.00175757
    raw={
        'NH_CM3':[nh],'NHE_CM3':[nh*Y_HE],
        'FRACTION_DT':[1e-12,2e-12,3e-12],
        'W_DT_EV_PER_H_S':[4e-12], 'TEMP_K':[8.2],
        'PHOTO_EVENTS':[1e-17,2e-17,3e-17],
        'THERMAL_MICRO':[1e-27], 'BINDING_MICRO':[2e-27],
        'ESCAPE':[3e-27], 'CMB_TO_GAS':[1e-27],
        'PHOTO_INPUT':[5e-27], 'CI_EVENTS':[0.,0.,0.],
        'RR_EVENTS':[0.,0.,0.], 'DR_EVENTS':[0.],
    }
    body='\n'.join(k+'\t'+'\t'.join(f'{v:.17e}' for v in vals) for k,vals in raw.items())
    return 'HE22_NATIVE_POINT_V1\n'+body+'\n',nh


def test_valid_schema_positive():
    txt,nh=valid_native_text();p=parse_native_point(txt,nh)
    assert p.temperature_K==8.2
    assert p.photo_events_cm3_s.shape==(3,)
    assert abs(p.w_dt_ev_per_h_s-4e-12)<1e-20


def test_reject_wrong_epoch_density():
    txt,nh=valid_native_text()
    with pytest.raises(AssertionError,match='DENSITY_OR_HELIUM'):
        parse_native_point(txt,nh*2)


def test_reject_malformed_native_response():
    txt,nh=valid_native_text()
    with pytest.raises(ValueError,match='SCHEMA'):parse_native_point(txt.replace('HE22_NATIVE_POINT_V1','OLD',1),nh)
    with pytest.raises(ValueError,match='DUPLICATE'):parse_native_point(txt+'ESCAPE\t0\n',nh)
    with pytest.raises(ValueError,match='FIELDS'):parse_native_point('HE22_NATIVE_POINT_V1\nNH_CM3\t.001\n',nh)
    with pytest.raises(ValueError,match='NONFINITE'):parse_native_point(txt.replace('TEMP_K\t8.19999999999999929e+00','TEMP_K\tnan'),nh)
