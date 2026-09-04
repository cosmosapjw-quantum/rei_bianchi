"""Exact M2 sign tests. The initial commit deliberately lacks the implementation."""
from functools import lru_cache
import importlib.util
from pathlib import Path
import unittest
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research/rei_math_m2_spacetime_sign/derive_constraint_sign.py"

@lru_cache(maxsize=1)
def load_module():
    assert MODULE.is_file(), "M2_IMPLEMENTATION_ABSENT"
    spec = importlib.util.spec_from_file_location("rei_m2_sign", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class SpacetimeSignTests(unittest.TestCase):
    def data(self):
        return load_module().derive()

    def zeros(self, expressions):
        for expression in expressions:
            self.assertEqual(sp.expand(expression), 0)

    def test_01_gauss(self):
        d = self.data()
        self.assertEqual(len(d["gauss_residuals"]), 81)
        self.zeros(d["gauss_residuals"])

    def test_02_codazzi(self):
        d = self.data()
        self.assertEqual(len(d["codazzi_residuals"]), 27)
        self.zeros(d["codazzi_residuals"])

    def test_03_hamiltonian(self):
        d = self.data()
        self.zeros([2*d["G"][0,0]-d["R3"]-sp.trace(d["K"])**2+sp.trace(d["K"]*d["K"])])
        self.zeros([d["E"][0,0]-(d["R3"]/2+3*d["H"]**2-sp.trace(d["sigma"]**2)/2-d["Lambda"]-d["kappa"]*d["rho"])])
        self.assertFalse(set(d["G"][0,0].free_symbols) & set(d["Kdot"]))

    def test_04_momentum_from_curvature(self):
        d = self.data()
        for i in range(3):
            self.zeros([d["Ricci"][0,i+1]-d["divK"][i], d["Ricci"][i+1,0]-d["divK"][i]])
            self.zeros([-d["E"][i+1,0]+d["divK"][i]+d["kappa"]*d["q"][i]])

    def test_05_output_first_adapter(self):
        d = self.data()
        self.assertEqual(len(d["adapter_residuals"]), 16)
        self.zeros(d["adapter_residuals"])
        self.zeros(d["output_gauss_residuals"])
        self.zeros(d["output_codazzi_residuals"])

    def test_06_independent_coordinate_witness(self):
        result = load_module().coordinate_witness()
        self.assertEqual(len(result["mixed_residuals"]), 3)
        self.zeros(result["mixed_residuals"])
        self.zeros([result["hamiltonian_residual"]])
        self.assertNotEqual(result["ricci_03"], 0)

    def test_07_previous_claim_counterexample(self):
        result = load_module().class_b_report()
        A,N22,N23,S12,S13,kappa,q3 = sp.symbols("A N22 N23 S12 S13 kappa_G q3", real=True)
        carrier = N22*S12+(N23-3*A)*S13
        self.zeros([result["geometric_carrier"]-carrier])
        self.zeros([result["projected_momentum"]+carrier+kappa*q3])
        self.zeros([result["prior_minus_derived"]-2*carrier])
        self.assertNotEqual(sp.expand(result["prior_minus_derived"]), 0)
        self.assertEqual(result["type_V_counterexample_derived"], 3)
        self.assertEqual(result["type_V_counterexample_prior"], -3)

    def test_08_scaling_and_K_parity(self):
        d = self.data()
        z = sp.Symbol("z", real=True)
        sub = {s:z*s for s in d["weight1_symbols"]}
        sub.update({s:z*z*s for s in d["Kdot"]})
        self.zeros([x.xreplace(sub)-z*z*x for x in d["G"]])
        reverse = {s:-s for s in d["K_symbols"]}
        self.zeros([d["G"][0,0].xreplace(reverse)-d["G"][0,0]])
        self.zeros([d["Ricci"][0,i+1].xreplace(reverse)+d["Ricci"][0,i+1] for i in range(3)])

    def test_09_hostile_mutations(self):
        rows = load_module().mutation_records()
        self.assertEqual(len(rows), 8)
        for row in rows:
            self.assertEqual(sp.sympify(row["locked_residual"]), 0)
        classes = {c:[r for r in rows if r["class"]==c] for c in ["A","B"]}
        self.assertEqual(len(classes["A"]), 4)
        self.assertEqual(len(classes["B"]), 4)
        self.assertTrue(all(sp.sympify(r["flip_3A_residual"])==0 for r in classes["A"]))
        self.assertTrue(all(sp.sympify(r["flip_3A_residual"])!=0 for r in classes["B"]))
        for key in ["epsilon_flip_residual", "drop_S13_residual", "drop_N22_residual", "order_flip_residual", "q_sign_residual"]:
            self.assertTrue(any(sp.sympify(r[key])!=0 for r in rows), key)

    def test_10_claim_firewall(self):
        status = load_module().claim_boundary()
        self.assertEqual(status["native_runtime"], "NOT_RUN")
        self.assertEqual(status["provider_export"], "NOT_AUTHORIZED")
        self.assertEqual(status["authority_effect_on_BASS"], "NONE")
        self.assertEqual(status["constraint_propagation"], "NOT_RUN")
        self.assertEqual(status["first_interval"], "NO_PASS_FIRST_CANONICAL_INTERVAL")

if __name__ == "__main__":
    unittest.main()
