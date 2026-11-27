"""Small synthetic contract controls, awaiting the parent's bounded runner.

Expected values follow event mechanics/energy bookkeeping independently of the
implementation path. These fixtures are neither measured rates nor an admission
of a physical collision source. No integration, scans, or historical suites run.
"""

import unittest
from dataclasses import replace
from math import ulp

from exchange_closure import (
    K_B, AngularTransport, CaloricSpecies, ConservativeSource, ContractError,
    EnergyAccount, EnergyTransfer, SpeciesPressure, TransportSource,
    PopulationSourceReceipt, project_population_sources,
    common_bulk_pressure, elastic_moment_kernel, monatomic_caloric,
    project_energy_transfers, temperature_rhs,
)


def mono(*args):
    return monatomic_caloric(*args, population_pool="thermal")


def synthetic_source():
    return TransportSource(
        source_id="synthetic-angle-control", immutable_locator="this-file:synthetic_source",
        projectile_id="fixture:a", target_id="fixture:b", energy_min_j=0,
        energy_max_j=100, full_com_angular_support=True,
        axisymmetric_about_relative_velocity=True, finite_mass_source_validated=False,
        count_convention="labelled_pair_once", evidence_status="conditional_model",
        uncertainty_locator="synthetic exact control; no source uncertainty estimate",
    )


def temperature(rows, t=100, theta=0, p=0, q=0, internal=()):
    return temperature_rhs(
        rows, temperature_k=t, expansion_s=theta, pressure_pa=p,
        centered_heat_w_m3=q, shear_work_w_m3=0, heat_flux_divergence_w_m3=0,
        common_temperature_contract="synthetic common-pool control",
        independent_internal_components=internal,
    )


class ExchangeClosureControls(unittest.TestCase):
    def test_reactive_birth_is_relative_kinetic_energy(self):
        # Two units of mass born at velocity 3 into a bulk moving at 1.
        result = ConservativeSource(2, (6, 0, 0), 9).centered((1, 0, 0))
        self.assertEqual(result["centered_heat_w_m3"], 4)
        self.assertEqual(result["acceleration_source_kg_m2_s2"], (4, 0, 0))

    def test_reactive_heat_is_galilean_invariant(self):
        source = ConservativeSource(2, (6, 0, 0), 9)
        shifted = source.change_frame((0.5, 1, -2))
        self.assertEqual(shifted.centered((0.5, -1, 2))["centered_heat_w_m3"], 4)

    def test_drag_dissipation_is_not_pairwise_opposite_heat(self):
        qa = ConservativeSource(0, (-1, 0, 0), 0).centered((1, 0, 0))["centered_heat_w_m3"]
        qb = ConservativeSource(0, (1, 0, 0), 0).centered((-1, 0, 0))["centered_heat_w_m3"]
        self.assertEqual((qa, qb), (1, 1))
        self.assertEqual(qa + qb - 2, 0)  # R_a.u_a + R_b.u_b = -2

    def test_finite_mass_isotropic_exchange_in_com(self):
        result = elastic_moment_kernel(2, 3, (3, 0, 0), (-2, 0, 0),
                                       AngularTransport(2, 2, 2), synthetic_source(),
                                       purpose="conditional_algebra")
        # Exact mechanics gives -12; equivalent reduced-mass arithmetic can
        # differ by one rounding unit. This is an explicit arithmetic oracle bound.
        self.assertAlmostEqual(result["momentum_a_kg_m3_s"][0], -12, delta=8 * ulp(12.0))
        self.assertEqual(result["momentum_a_kg_m3_s"][1:], (0, 0))
        self.assertAlmostEqual(result["kinetic_a_j_m2"], 0, delta=1e-13)
        for i, expected in enumerate((-40, 20, 20)):
            self.assertAlmostEqual(result["total_stf_j_m2"][i][i], expected)
        for i, expected in enumerate((-24, 12, 12)):
            self.assertAlmostEqual(result["second_moment_a_j_m2"][i][i], expected)

    def test_stationary_equal_mass_target_receives_half_energy_for_isotropic_angles(self):
        result = elastic_moment_kernel(1, 1, (2, 0, 0), (0, 0, 0),
                                       AngularTransport(1, 1, 1), synthetic_source(),
                                       purpose="conditional_algebra")
        self.assertEqual(result["relative_energy_j"], 1)
        self.assertEqual((result["kinetic_a_j_m2"], result["kinetic_b_j_m2"]), (-1, 1))

    def test_large_mass_sum_preserves_finite_moments_or_rejects_nonrepresentable_values(self):
        # API edge control: each mass, reduced mass and output are finite although
        # ma+mb exceeds binary64. Exact mu=5e307, mu*sigma1=1/2, V=1/2, g=1.
        source = replace(synthetic_source(), energy_max_j=1e308)
        result = elastic_moment_kernel(1e308, 1e308, (1, 0, 0), (0, 0, 0),
                                       AngularTransport(1e-308, 1e-308, 1e-308), source,
                                       purpose="conditional_algebra")
        self.assertAlmostEqual(result["momentum_a_kg_m3_s"][0], -0.5, delta=1e-15)
        self.assertAlmostEqual(result["kinetic_a_j_m2"], -0.25, delta=1e-15)
        with self.assertRaises(ContractError):
            elastic_moment_kernel(1, 1, (1e308, 0, 0), (0, 0, 0),
                                  AngularTransport(1, 1, 1), source,
                                  purpose="conditional_algebra")

    def test_backward_scattering_transfers_momentum_but_preserves_l2(self):
        result = elastic_moment_kernel(1, 1, (2, 0, 0), (0, 0, 0),
                                       AngularTransport(1, 2, 0), synthetic_source(),
                                       purpose="conditional_algebra")
        self.assertEqual(result["kinetic_b_j_m2"], 2)
        self.assertTrue(all(x == 0 for row in result["total_stf_j_m2"] for x in row))

    def test_angular_moment_cone_and_source_scope_rejections(self):
        with self.assertRaises(ContractError):
            AngularTransport(1, 0, 1).validate()
        for source, purpose in (
            (synthetic_source(), "physical_evaluation"),
            (replace(synthetic_source(), full_com_angular_support=False), "conditional_algebra"),
            (replace(synthetic_source(), energy_max_j=0.5), "conditional_algebra"),
        ):
            with self.assertRaises(ContractError):
                elastic_moment_kernel(1, 1, (2, 0, 0), (0, 0, 0),
                                      AngularTransport(1, 1, 1), source, purpose=purpose)

    def test_monatomic_expansion_and_particle_count_are_distinct(self):
        self.assertAlmostEqual(temperature([mono("e:th", 2, 0, 100)],
                                            theta=3, p=200 * K_B)["temperature_rate_k_s"], -200)
        output = temperature([mono("e:th", 2, 1, 100)], q=6 * K_B)
        self.assertAlmostEqual(output["temperature_rate_k_s"], -48)
        self.assertAlmostEqual(output["particle_count_power_w_m3"] / K_B, 150)

    def test_equilibrium_molecular_capacity_requires_unique_internal_owner(self):
        molecule = CaloricSpecies("H2:thermal", 1, 0, 25 * K_B, 2.5 * K_B, 10,
                                  "synthetic classical rigid-rotor caloric control", "thermal", ("H2:rotation",))
        rows = [mono("H:thermal", 1, 0, 10), molecule]
        self.assertAlmostEqual(temperature(rows, t=10, theta=3, p=20 * K_B)["temperature_rate_k_s"], -15)
        with self.assertRaises(ContractError):
            temperature(rows, t=10, internal=("H2:rotation",))

    def test_nonthermal_birth_is_excluded_until_pool_transfer(self):
        receipts = [
            PopulationSourceReceipt("birth", "e:fast", "nonthermal", 3, "WU", "synthetic:birth"),
            PopulationSourceReceipt("thermalize", "e:fast", "nonthermal", -1, "CR", "synthetic:stop"),
            PopulationSourceReceipt("thermalize", "e:thermal", "thermal", 1, "CR", "synthetic:stop"),
        ]
        owners = {"birth": "WU", "thermalize": "CR"}
        self.assertEqual(project_population_sources(receipts, owners),
                         {"thermal": {"e:thermal": 1}, "nonthermal": {"e:fast": 2}})
        with self.assertRaises(ContractError):
            project_population_sources(receipts + receipts[:1], owners)
        with self.assertRaises(ContractError):
            temperature([replace(mono("e:fast", 2, 3, 100), population_pool="nonthermal")])

    def test_energy_projection_has_one_binding_owner(self):
        accounts = [
            EnergyAccount("fast", "fast:kinetic", "nonthermal_kinetic", "evolved", "bass_cr"),
            EnergyAccount("thermal", "thermal:kinetic", "thermal_kinetic", "evolved", "BASS_HE"),
            EnergyAccount("binding", "H:binding", "chemical_binding", "population_derived", "WU088_HH"),
        ]
        transfers = [
            EnergyTransfer("stop:001", "bass_cr", "fast", "thermal", 5, "synthetic:stop"),
            EnergyTransfer("ci:001", "WU088_HH", "thermal", "binding", 2, "synthetic:ci"),
        ]
        owners = {"stop:001": "bass_cr", "ci:001": "WU088_HH"}
        result = project_energy_transfers(accounts, transfers, owners)
        self.assertEqual(result["evolved_rhs_w_m3"], {"fast": -5, "thermal": 3})
        self.assertEqual(result["population_derivative_witness_w_m3"], {"binding": 2})
        self.assertEqual(result["conservation_residual_w_m3"], 0)
        with self.assertRaises(ContractError):
            project_energy_transfers(accounts + [replace(accounts[-1], account_id="binding-copy",
                                                         representation="evolved")], transfers, owners)
        with self.assertRaises(ContractError):
            project_energy_transfers(accounts, transfers + transfers[:1], owners)
        with self.assertRaises(ContractError):
            project_energy_transfers(accounts, transfers, {"stop:001": "BASS_HE", "ci:001": "WU088_HH"})

    def test_nuclear_daughter_energy_is_not_automatically_heat(self):
        accounts = [
            EnergyAccount("mass", "nuclear:mass", "nuclear_mass", "population_derived", "WU088_HH"),
            EnergyAccount("fast", "daughter:kinetic", "nonthermal_kinetic", "evolved", "bass_cr"),
            EnergyAccount("nu", "neutrino:escape", "neutrino_escaped", "evolved", "WU088_HH"),
            EnergyAccount("thermal", "thermal:kinetic", "thermal_kinetic", "evolved", "BASS_HE"),
        ]
        transfers = [EnergyTransfer("decay:k", "WU088_HH", "mass", "fast", 7, "synthetic:decay"),
                     EnergyTransfer("decay:nu", "WU088_HH", "mass", "nu", 3, "synthetic:decay")]
        result = project_energy_transfers(accounts, transfers,
                                         {"decay:k": "WU088_HH", "decay:nu": "WU088_HH"})
        self.assertEqual(result["evolved_rhs_w_m3"]["thermal"], 0)
        self.assertEqual(result["population_derivative_witness_w_m3"]["mass"], -10)

    def test_common_bulk_retains_drift_stress(self):
        identity = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        result = common_bulk_pressure([
            SpeciesPressure("a", 1, (1, 0, 0), identity),
            SpeciesPressure("b", 1, (-1, 0, 0), identity),
        ])
        self.assertEqual(result["bulk_m_s"], (0, 0, 0))
        self.assertEqual(result["pressure_pa"], ((4, 0, 0), (0, 2, 0), (0, 0, 2)))
        self.assertEqual(result["drift_energy_j_m3"], 1)


if __name__ == "__main__":
    unittest.main()
