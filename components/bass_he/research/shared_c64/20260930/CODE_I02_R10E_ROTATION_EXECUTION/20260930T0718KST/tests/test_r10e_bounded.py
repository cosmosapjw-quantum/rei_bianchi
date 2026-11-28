import json

import numpy as np
import pytest

from coulomb_rotation import author_cutoff, coulomb_rotation_batch
from r10e_gate import TABLE, dop853_probability, fixed_rhos
from r10e_lanes import HERE, input_probabilities, prepare_inputs


def test_fixed_node_and_table_identity():
    table, frozen, nodes = prepare_inputs()
    gate = json.loads((HERE/'GATE_PRECOMMITTED.json').read_text())
    assert len(nodes) == 105
    assert [float(x).hex() for x in nodes] == gate['rho_hex']
    assert len(table['rows']) == 360
    assert len(frozen['records']) == 5


def test_dop853_independently_agrees_at_smallest_rho():
    rho = float(fixed_rhos(TABLE)[0])
    cut = author_cutoff(2)
    reference, meta = dop853_probability(3, 2, 0.5, rho, cut, rtol=1e-12, atol=1e-14)
    magnus = coulomb_rotation_batch(3, 2, [0.5], [rho], steps=1024, R_cut=cut)['P_abs'][0]
    assert meta['success'] and meta['accepted_steps'] > 0
    assert np.max(np.abs(reference-magnus)) <= 1e-8


def test_frozen_and_dynamic_delta_are_separate():
    table, frozen, nodes = prepare_inputs()
    dynamic, static = input_probabilities(table, nodes[:1], np.array([0.5,5.0]), frozen)
    assert dynamic.shape == static.shape == (2,5)
    assert np.all((0 <= dynamic) & (dynamic <= 1))
    assert np.all((0 <= static) & (static <= 1))
    assert not np.array_equal(dynamic, static)


def test_lane_gate_fails_closed_on_unadmitted_convergence(tmp_path, monkeypatch):
    # A wrong local gate file must fail before any transport evaluation.
    import r10e_lanes
    original = json.loads((HERE/'EXTENDED_CONVERGENCE.json').read_text())
    original['status'] = 'R10E_ROTATION_NUMERICS_UNRESOLVED'
    (tmp_path/'EXTENDED_CONVERGENCE.json').write_text(json.dumps(original))
    monkeypatch.setattr(r10e_lanes, 'HERE', tmp_path)
    with pytest.raises(RuntimeError, match='R10E_NUMERICAL_GATE_REQUIRED'):
        r10e_lanes.prepare_inputs()
