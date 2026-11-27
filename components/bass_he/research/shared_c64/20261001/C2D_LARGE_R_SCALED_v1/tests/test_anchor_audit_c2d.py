"""Pure standard-library scalar fixtures; no eigensolves or integrations."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"code"))
from anchor_audit import evaluate_anchors, merge_observation_values, InputError


class AnchorAuditTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((ROOT/"CONTRACT.json").read_text())
        self.anchor = self.contract["spherical_anchor"]
        self.R = self.anchor["R"]
        self.local = -1./4096
        self.prolate = dict(R=self.R, energies=[-2., -.5],
                            direct={str(q): dict(L_O_bar=self.local+6., L_B_bar=self.local)
                                    for q in (16, 24, 32)})
        self.observations = {label: self.observation(label) for label in ("l72", "l96")}

    def row(self, local=None, momentum=.5625):
        local = self.local if local is None else local
        total = local+(self.R/3)*momentum
        return dict(L_O_over_minus_i_hbar=total, L_center_over_minus_i_hbar=local,
                    L_O_bar=total, L_B_bar=local, p_x_over_minus_i_hbar=momentum,
                    dipole_x=.375, origin_center="B", origin_shift_center_to_O=self.R/3,
                    Q_O=total/self.R, Q_B=-self.R**2*local)

    def observation(self, label):
        specifications = {**self.anchor["configurations"], **self.anchor["fallback_configurations"]}
        spec = specifications[label]
        quality, identities = [], []
        for m, energy in enumerate((-2., -.5)):
            digest = str(m+1)*64
            meta = dict(origin_center="B", origin_shift_center_to_O=self.R/3,
                        nuclear_positions=[-self.R, 0.], angular_lmax=spec["lmax"],
                        degree=spec["degree"], rmax=spec["rmax"],
                        radial_quadrature=spec["quadrature"], radial_elements_actual=spec["elements"],
                        explicit_boundaries=deepcopy(spec["boundaries"]), solver_tol=spec["tol"],
                        ritz_eigenvalues=[energy, energy+.25], ritz_residuals=[1e-12, 1e-11],
                        discrete_sector_gap=.25)
            quality.append(dict(energy=energy, phase_probe=1., residual=1e-12, mass_norm=1.,
                                state_sha256=digest, state_bytes=100, state_file="STATE.npz", metadata=meta))
            identities.append(dict(state_sha256=digest, state_bytes=100, data_sha256="a"*64))
        return dict(R=self.R, sectors=[0, 1], energies=[-2., -.5], phase_probes=[1., 1.],
                    new_eigensolves=0, direct={str(q): self.row() for q in (14, 22, 30)},
                    states=identities, state_values=quality)

    def evaluate(self):
        return evaluate_anchors(self.observations, self.prolate, self.contract)

    def assert_fails_gate(self, result, name):
        self.assertFalse(result["accepted"])
        self.assertTrue(any(name in gate["name"] for gate in result["failures"]), result)

    def test_complete_exact_manufactured_input_passes_with_signed_scaled_values(self):
        result = self.evaluate()
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["levels"]["l96"]["Q_B"], .25)
        self.assertEqual(result["levels"]["l96"]["Q_O"], (self.local+6.)/self.R)
        self.assertEqual(result["new_eigensolves"], 0)
        self.assertEqual(result["new_operator_integrations"], 0)

    def test_Q_B_agreement_detects_scaled_error_below_raw_cap(self):
        self.prolate["direct"]["32"]["L_B_bar"] += 2e-7
        self.assert_fails_gate(self.evaluate(), "Q_B_agreement")

    def test_Q_B_angular_increment_uses_x_squared(self):
        self.observations["l96"]["direct"] = {str(q): self.row(self.local+3e-8) for q in (14,22,30)}
        self.assert_fails_gate(self.evaluate(), "original_l72_to_l96.Q_B_increment")

    def test_both_terminal_quadrature_increments_required(self):
        self.observations["l96"]["direct"]["14"] = self.row(self.local+2e-9)
        self.assert_fails_gate(self.evaluate(), "q14_to_q22.Q_B")

    def test_momentum_Q_B_cubic_amplification_and_origin_Q_B_square(self):
        self.observations["l96"]["direct"] = {str(q): self.row(momentum=.5625+2e-11) for q in (14,22,30)}
        result = self.evaluate()
        self.assert_fails_gate(result, "Q_B_momentum_induced")
        self.assertFalse(any("Q_O_momentum" in gate["name"] for gate in result["failures"]))
        self.setUp()
        for row in self.observations["l96"]["direct"].values():
            row["L_O_over_minus_i_hbar"] += 2e-10
            row["L_O_bar"] = row["L_O_over_minus_i_hbar"]
            row["Q_O"] = row["L_O_bar"]/self.R
        self.assert_fails_gate(self.evaluate(), "Q_B_origin")

    def test_explicit_mesh_and_quality_identity_are_bound(self):
        for mutation, gate in (("mesh", "metadata.explicit_boundaries"),
                               ("phase", "phase_binding"), ("hash", "state_sha256_binding"),
                               ("energy", "energy_binding"), ("ritz", "selected_lowest_ritz")):
            with self.subTest(mutation=mutation):
                self.setUp()
                state = self.observations["l96"]["state_values"][0]
                if mutation == "mesh": state["metadata"]["explicit_boundaries"][1] *= .9
                if mutation == "phase": state["phase_probe"] = 2.
                if mutation == "hash": state["state_sha256"] = "b"*64
                if mutation == "energy": state["energy"] += 1e-9
                if mutation == "ritz": state["metadata"]["ritz_eigenvalues"][0] += 1e-9
                self.assert_fails_gate(self.evaluate(), gate)

    def test_fallback_requires_both_levels_and_preserves_original_angular_gate(self):
        self.observations["h"] = self.observation("h")
        self.assertEqual(self.evaluate()["status"], "UNKNOWN")
        self.observations["p"] = self.observation("p")
        self.assertTrue(self.evaluate()["accepted"])
        self.observations["l72"]["direct"] = {str(q): self.row(self.local+3e-8) for q in (14,22,30)}
        self.assert_fails_gate(self.evaluate(), "original_l72_to_l96.Q_B_increment")

    def test_fallback_spread_cannot_select_attractive_level(self):
        self.observations["h"] = self.observation("h")
        self.observations["p"] = self.observation("p")
        self.observations["p"]["direct"] = {str(q): self.row(self.local+3e-8) for q in (14,22,30)}
        self.assert_fails_gate(self.evaluate(), "fallback_l96_h_p.Q_B_spread")

    def test_missing_malformed_and_nonfinite_inputs_fail_closed(self):
        for mutation in ("missing", "nan", "hash", "order", "redundant", "unknown_label"):
            with self.subTest(mutation=mutation):
                self.setUp()
                obs = self.observations["l96"]
                if mutation == "missing": del obs["state_values"]
                if mutation == "nan": obs["direct"]["30"]["L_center_over_minus_i_hbar"] = float("nan")
                if mutation == "hash": obs["states"][0]["state_sha256"] = None
                if mutation == "order": del obs["direct"]["14"]
                if mutation == "redundant": obs["direct"]["30"]["Q_B"] *= -1
                if mutation == "unknown_label": self.observations["l97"] = self.observation("l96")
                result = self.evaluate()
                self.assertFalse(result["accepted"])
                self.assertIn(result["status"], ("FAIL", "UNKNOWN"))
                json.dumps(result, allow_nan=False)

    def test_frozen_quadrature_extension_and_merge_identity(self):
        for label in ("l72", "l96"):
            extra = deepcopy(self.observations[label])
            extra["direct"] = {str(q): self.row() for q in (40,48)}
            self.observations[label] = merge_observation_values(self.observations[label], extra)
        self.assertTrue(self.evaluate()["accepted"])
        altered = deepcopy(self.observations["l96"])
        altered["states"][0]["state_sha256"] = "b"*64
        with self.assertRaises(InputError):
            merge_observation_values(self.observations["l96"], altered)
        altered = deepcopy(self.observations["l96"])
        altered["direct"]["30"] = self.row(self.local+1e-9)
        with self.assertRaises(InputError):
            merge_observation_values(self.observations["l96"], altered)


if __name__ == "__main__":
    unittest.main()
