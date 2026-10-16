"""Targeted source-backed tests; V4 sweep is intentionally not repeated."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "donor"))
sys.path.insert(0, str(HERE.parent / "lrs_threshold_oracle_20261015"))
from dynamic_chemistry import Gas
from recomb_thermal import evolve_thermal
from rate_table import CaseARates, RateDomainError
from native_interface import point_terms
from study_v5 import GAS, H0, N_STAR, T0, rays, run


def test_owner_grid_and_domain():
    provider = CaseARates()
    assert provider.exact_grid_parity() < 1e-13
    assert provider.sha256 == "33396b071c840b40ad79d68ee626de59f12bb2cf0b1df2159627efd7fde42aec"
    with pytest.raises(RateDomainError):
        provider(9999.0)
    with pytest.raises(RateDomainError):
        provider(24001.0)


def test_provider_domain_even_without_active_recombination():
    neutral=Gas(.4,0.,.1,0.,0.)
    with pytest.raises(RateDomainError):
        evolve_thermal(rays(0.,0.),neutral,.01,temperature_initial_K=9999.,
                       atomic_rates=CaseARates(),n_star_cm3=N_STAR,h0_s=H0)
    with pytest.raises(RateDomainError):
        evolve_thermal(rays(0.,0.),neutral,.5,temperature_initial_K=T0,
                       max_step=.01,atomic_rates=CaseARates(),
                       n_star_cm3=N_STAR,h0_s=H0)


def test_native_point_cgs_and_x_mapping():
    provider = CaseARates()
    x = .02
    p = point_terms(rays(0.), GAS, x, N_STAR, H0, T0, provider)
    assert p["species_order"] == ("HI", "HII", "HeI", "HeII", "HeIII")
    assert p["dt_dX_s"] == 1/H0
    assert p["ne_cm3"] == pytest.approx(N_STAR*__import__('math').exp(-3*x)*GAS.electrons)
    assert p["rr_events_cm3_s"][0] == pytest.approx(p["ne_cm3"]*N_STAR*__import__('math').exp(-3*x)*GAS.HII*provider(T0)[0])
    assert all(v >= 0 for v in p["gamma_s"] + p["heat_erg_per_absorber_s"])
    assert (p["selected_thermal_micro_erg_cm3_s"]+
            p["selected_binding_micro_erg_cm3_s"]+
            p["selected_escape_erg_cm3_s"]) == pytest.approx(
                p["photo_input_erg_cm3_s"], rel=1e-12)


@pytest.mark.parametrize("gas", [Gas(.37,.03,0,0,0), Gas(0,0,.085,.012,.003), GAS])
def test_recombination_only_conservation(gas):
    r = evolve_thermal(rays(0., 0.), gas, .05, temperature_initial_K=T0,
                       max_step=.0025, atomic_rates=CaseARates(),
                       n_star_cm3=N_STAR, h0_s=H0)
    assert max(abs(r.hydrogen_residual),abs(r.helium_residual),
               abs(r.photon_reaction_residual),abs(r.electron_reaction_residual)) < 1e-12
    assert abs(r.energy_residual_ev) < 1e-11
    assert min(*r.final.as_tuple(), *r.photons_final) >= 0
    assert sum(r.recomb_events) > 0 and sum(r.photo_events) == 0
    assert r.escaped_recomb_energy_ev > 0


def test_independent_radau_refinement_and_small_signed_shear_near_evenness():
    results = run()["cases"]
    for case in results.values():
        rows = case["refinement"]
        assert rows[-1]["T_abs_error_K"] < .001
        assert rows[-1]["ne_abs_error"] < 1e-10
        assert rows[-1]["T_abs_error_K"] < rows[-2]["T_abs_error_K"]
        assert abs(rows[-1]["energy_residual_ev"]) < 1e-11
        assert abs(rows[-1]["electron_residual"]) < 1e-11
    minus = results["mixed_LRS_minus"]["refinement"][-1]
    plus = results["mixed_LRS_plus"]["refinement"][-1]
    assert abs(minus["T_K"]-plus["T_K"]) < 1e-5
    assert abs(minus["ne"]-plus["ne"]) < 1e-10
