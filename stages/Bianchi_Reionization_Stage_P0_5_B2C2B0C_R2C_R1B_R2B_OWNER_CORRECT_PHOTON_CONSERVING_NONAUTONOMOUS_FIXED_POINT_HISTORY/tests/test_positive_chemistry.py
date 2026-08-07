"""RED 2 — positive H/He chemistry.

Material state is

    Y_i = (N_HI, N_HII, N_HeI, N_HeII, N_HeIII, U_resolved)_i

and the reaction map must preserve

    N_s >= 0
    N_HI  + N_HII               = N_H
    N_HeI + N_HeII + N_HeIII    = N_He

with no clipping anywhere. An infeasible demand must terminate the trajectory,
not be truncated into a feasible-looking state — a clipped state is a silent
mass-conservation violation that every downstream auditor would then treat as
real.

Recombination and transfer counts are inputs, not modelled here: the input lock
forbids a recombination surrogate, so this module never invents a rate.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

MODULE = Path(__file__).parents[1] / "analysis/positive_chemistry.py"


def _load():
    spec = importlib.util.spec_from_file_location("r2b_positive_chemistry", MODULE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _state(m, **kw):
    base = dict(
        N_HI=1.0e6,
        N_HII=4.0e5,
        N_HeI=8.0e4,
        N_HeII=1.5e4,
        N_HeIII=2.0e3,
        U_resolved=3.0e10,
    )
    base.update(kw)
    return m.MaterialState(**base)


def test_hydrogen_nuclei_are_conserved_exactly():
    m = _load()
    y0 = _state(m)
    y1 = m.apply_reaction_map(
        state=y0,
        absorbed_HI=2.5e5,
        absorbed_HeI=1.0e4,
        absorbed_HeII=5.0e2,
        recombination_HII_to_HI=7.0e4,
        recombination_HeII_to_HeI=3.0e3,
        recombination_HeIII_to_HeII=1.0e2,
        resolved_heating=0.0,
    )

    assert y1.N_HI + y1.N_HII == pytest.approx(y0.N_H, rel=1e-15)


def test_helium_nuclei_are_conserved_exactly():
    m = _load()
    y0 = _state(m)
    y1 = m.apply_reaction_map(
        state=y0,
        absorbed_HI=2.5e5,
        absorbed_HeI=1.0e4,
        absorbed_HeII=5.0e2,
        recombination_HII_to_HI=7.0e4,
        recombination_HeII_to_HeI=3.0e3,
        recombination_HeIII_to_HeII=1.0e2,
        resolved_heating=0.0,
    )

    assert y1.N_HeI + y1.N_HeII + y1.N_HeIII == pytest.approx(y0.N_He, rel=1e-15)


def test_all_species_stay_nonnegative():
    m = _load()
    y0 = _state(m)
    y1 = m.apply_reaction_map(
        state=y0,
        absorbed_HI=9.9e5,
        absorbed_HeI=7.9e4,
        absorbed_HeII=1.4e4,
        recombination_HII_to_HI=0.0,
        recombination_HeII_to_HeI=0.0,
        recombination_HeIII_to_HeII=0.0,
        resolved_heating=0.0,
    )

    for value in (y1.N_HI, y1.N_HII, y1.N_HeI, y1.N_HeII, y1.N_HeIII):
        assert value >= 0.0


def test_infeasible_hydrogen_demand_fails_closed_without_clipping():
    m = _load()
    y0 = _state(m)

    with pytest.raises(m.InfeasibleReaction) as excinfo:
        m.apply_reaction_map(
            state=y0,
            absorbed_HI=1.0e6 + 1.0,  # one photon beyond the HI reservoir
            absorbed_HeI=0.0,
            absorbed_HeII=0.0,
            recombination_HII_to_HI=0.0,
            recombination_HeII_to_HeI=0.0,
            recombination_HeIII_to_HeII=0.0,
            resolved_heating=0.0,
        )

    assert excinfo.value.species == "N_HI"


def test_infeasible_heii_demand_fails_closed():
    m = _load()
    y0 = _state(m)

    with pytest.raises(m.InfeasibleReaction):
        m.apply_reaction_map(
            state=y0,
            absorbed_HI=0.0,
            absorbed_HeI=0.0,
            absorbed_HeII=1.5e4 + 1.0,
            recombination_HII_to_HI=0.0,
            recombination_HeII_to_HeI=0.0,
            recombination_HeIII_to_HeII=0.0,
            resolved_heating=0.0,
        )


def test_recombination_supply_extends_the_feasible_demand():
    m = _load()
    y0 = _state(m)
    # Demand exceeding the bare reservoir becomes feasible once recombination
    # refills it within the same interval.
    y1 = m.apply_reaction_map(
        state=y0,
        absorbed_HI=1.05e6,
        absorbed_HeI=0.0,
        absorbed_HeII=0.0,
        recombination_HII_to_HI=1.0e5,
        recombination_HeII_to_HeI=0.0,
        recombination_HeIII_to_HeII=0.0,
        resolved_heating=0.0,
    )

    assert y1.N_HI >= 0.0
    assert y1.N_HI + y1.N_HII == pytest.approx(y0.N_H, rel=1e-15)


def test_zero_input_is_the_identity_on_material_state():
    m = _load()
    y0 = _state(m)
    y1 = m.apply_reaction_map(
        state=y0,
        absorbed_HI=0.0,
        absorbed_HeI=0.0,
        absorbed_HeII=0.0,
        recombination_HII_to_HI=0.0,
        recombination_HeII_to_HeI=0.0,
        recombination_HeIII_to_HeII=0.0,
        resolved_heating=0.0,
    )

    assert y1 == y0


def test_only_resolved_heating_moves_the_thermal_variable():
    m = _load()
    y0 = _state(m)
    y1 = m.apply_reaction_map(
        state=y0,
        absorbed_HI=1.0e5,
        absorbed_HeI=0.0,
        absorbed_HeII=0.0,
        recombination_HII_to_HI=0.0,
        recombination_HeII_to_HeI=0.0,
        recombination_HeIII_to_HeII=0.0,
        resolved_heating=4.2e9,
    )

    assert y1.U_resolved == pytest.approx(y0.U_resolved + 4.2e9, rel=1e-15)


def test_negative_or_nonfinite_input_fails_closed():
    m = _load()
    y0 = _state(m)
    with pytest.raises(ValueError):
        m.apply_reaction_map(
            state=y0,
            absorbed_HI=-1.0,
            absorbed_HeI=0.0,
            absorbed_HeII=0.0,
            recombination_HII_to_HI=0.0,
            recombination_HeII_to_HeI=0.0,
            recombination_HeIII_to_HeII=0.0,
            resolved_heating=0.0,
        )
    with pytest.raises(ValueError):
        m.apply_reaction_map(
            state=y0,
            absorbed_HI=float("inf"),
            absorbed_HeI=0.0,
            absorbed_HeII=0.0,
            recombination_HII_to_HI=0.0,
            recombination_HeII_to_HeI=0.0,
            recombination_HeIII_to_HeII=0.0,
            resolved_heating=0.0,
        )


def test_state_rejects_negative_species_at_construction():
    m = _load()
    with pytest.raises(ValueError):
        m.MaterialState(
            N_HI=-1.0,
            N_HII=0.0,
            N_HeI=0.0,
            N_HeII=0.0,
            N_HeIII=0.0,
            U_resolved=0.0,
        )
