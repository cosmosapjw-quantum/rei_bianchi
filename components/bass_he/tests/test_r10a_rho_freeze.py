import math
import json
from pathlib import Path

import numpy as np
import pytest

from bass_he.eq54 import BRANCHES, DeltaSurrogate, surrogate_geometry_mapping
from arseny_reimpl.cross_section import projectile_velocity_au
from scripts.r10a_rho_freeze import frozen_geometry_mapping, assemble_three_lanes, probability_ratio, validate_holdout_gate


def synthetic_surrogate():
    return DeltaSurrogate({b.name: [(f*b.support_cutoff, 0.2+0.1*f*f)
                                    for f in (0., .25, .5, 1.)] for b in BRANCHES})


def test_frozen_mapping_preserves_branch_support_order_and_constant_delta():
    s=synthetic_surrogate()
    rhos=np.array([0., 0.2, max(b.support_cutoff for b in BRANCHES)+1.])
    frozen=frozen_geometry_mapping(s,rhos)
    dynamic=surrogate_geometry_mapping(s,rhos)
    assert list(frozen)==list(dynamic)
    for (name,rho),rec in frozen.items():
        assert rec['delta']==pytest.approx(float(s.evaluate(name,[0.])[0]))
        assert rho<=next(b.support_cutoff for b in BRANCHES if b.name==name)
    assert all(rho!=rhos[-1] for _,rho in frozen)


def test_three_lanes_isolated_and_ratio_identity():
    s=synthetic_surrogate()
    rho=np.array([.2])
    out=assemble_three_lanes(s,rho,energies=(.5,5.),rotation_steps=8)
    assert tuple(out['lanes'])==('F2-RHO','F2-FROZEN','F1-RHO')
    assert out['components'].shape==(1,54)
    for name,prob in out['lanes'].items():
        assert prob.shape==(1,2,10)
        assert np.all(prob>=-2e-13)
        assert np.max(abs(prob.sum(-1)-1.))<3e-10
    assert not np.allclose(out['lanes']['F2-RHO'],out['lanes']['F2-FROZEN'])
    d=float(s.evaluate(BRANCHES[0].name,rho)[0]);d0=float(s.evaluate(BRANCHES[0].name,[0.])[0])
    for energy in (.5,5.):
        v=projectile_velocity_au(energy)
        p_rho=math.exp(-2*d/v);p_frozen=math.exp(-2*d0/v)
        assert probability_ratio(d0,d,v)==pytest.approx(p_frozen/p_rho,abs=5e-13)


def test_surrogate_no_extrapolation_and_holdout_gate():
    s=synthetic_surrogate();b=BRANCHES[0]
    with pytest.raises(ValueError,match='coverage'):
        s.evaluate(b.name,[np.nextafter(b.support_cutoff,np.inf)])
    rows=[dict(branch=b.name,rho=.5*b.support_cutoff,delta=5.)]
    with pytest.raises(ValueError,match='holdout'):
        validate_holdout_gate(s,rows,threshold=2e-4)


def test_actual_r10a_quadrature_node_rejects_surrogate_admission():
    root=Path(__file__).resolve().parents[1]
    p=root/'research/shared_c64/20260929/CODE_I02_R10A_RHO_FREEZE_IMPACT/20260929T1535KST/attempt2'
    manifest=json.loads((p/'SURROGATE_MANIFEST.json').read_text())
    sentinel=json.loads((p/'SURROGATE_RANK_SENTINEL.json').read_text())
    s=DeltaSurrogate({name:[(x['rho'],x['delta']) for x in rows]
                      for name,rows in manifest['anchors'].items()})
    with pytest.raises(ValueError,match='holdout'):
        validate_holdout_gate(s,[{'branch':'Q23','rho':sentinel['rho'],
                                  'delta':sentinel['exact_delta']}],threshold=2e-4)
