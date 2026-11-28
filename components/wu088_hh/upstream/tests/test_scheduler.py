import copy
import math
import pytest
from wu088_hh.scheduler import order_tasks, predict_costs, verify_profile


def profile():
    return dict(schema='WU088_PAIR_COST_PROFILE_V1', scientific_driver_sha256='a'*64,
                model_sha256='b'*64, g=80, gamma_scale='unit',
                states=[dict(z=z,n=160,costs=[[i,j,(i+1)*(j+1)+z] for i in range(12) for j in range(12)]) for z in (0,16)])


def test_expensive_pair_is_submitted_first():
    tasks=[(0,0,'p0'),(0,1,'p1'),(1,0,'p2')]
    assert order_tasks(tasks,{(0,0):1.,(0,1):20.,(1,0):4.}) == [tasks[1],tasks[2],tasks[0]]


def test_equal_costs_have_canonical_tie_break():
    tasks=[(1,1,'a'),(0,2,'b'),(0,0,'c')]
    assert order_tasks(tasks,{(1,1):1,(0,2):1,(0,0):1}) == [tasks[2],tasks[1],tasks[0]]


def test_cost_prediction_interpolates_only_between_known_geometry():
    p=profile()
    costs,meta=predict_costs(p,n=192,z=8)
    assert costs[0,0] == pytest.approx(9*(192/160)**2)
    assert meta['costs_are_performance_predictions_only'] is True
    with pytest.raises(ValueError,match='outside'):
        predict_costs(p,n=160,z=32)


def test_profile_does_not_select_science_and_rejects_identity_change():
    p=profile()
    verify_profile(p,driver_sha='a'*64,model_sha='b'*64,g=80,gamma_scale='unit')
    with pytest.raises(ValueError,match='model'):
        verify_profile(p,driver_sha='a'*64,model_sha='c'*64,g=80,gamma_scale='unit')


@pytest.mark.parametrize('bad',[float('nan'),float('inf'),-1,0])
def test_bad_timing_is_rejected(bad):
    p=profile();p['states'][0]['costs'][0][2]=bad
    with pytest.raises(ValueError):
        predict_costs(p,n=160,z=8)


def test_duplicate_task_or_missing_cost_rejected():
    with pytest.raises(ValueError):
        order_tasks([(0,0,'a'),(0,0,'b')],{(0,0):1})
    with pytest.raises(ValueError):
        order_tasks([(0,0,'a')],{})
