#!/usr/bin/env python3
"""Scientific analysis guards: separability counterexample and native mutations."""
import copy
from decimal import Decimal as D, localcontext
from pathlib import Path
import unittest

import analyze_br05_pair as audit


class PairAudit(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.rows = audit.read_rows(self.root / "reused_br04/evidence/native/ap_n16_r4.csv")

    def test_exact_additive_and_coupled_error_models(self):
        # f(h,e)=5+3h+2e is separable, while adding 7he has mixed difference 7/4.
        # h,e halve along each axis; this is an independently prescribed surface.
        with localcontext() as ctx:
            ctx.prec = 96
            for interaction in (D(0), D(7)):
                values = [D(5) + 3*h + 2*e + interaction*h*e
                          for h, e in ((D(1), D(1)), (D('.5'), D(1)),
                                       (D(1), D('.5')), (D('.5'), D('.5')))]
                result = audit.rectangle(*values)
                self.assertEqual(result["D_tr"], interaction / 4)

    def test_declared_parent_configuration_and_ledgers(self):
        with localcontext() as ctx:
            ctx.prec = 96
            maxima, rows = audit.check_native(self.rows, 16, 4)
        self.assertEqual(len(rows), 16)
        self.assertLess(max(maxima.values()), D('3e-10'))

    def test_photon_ledger_mutation_is_detected(self):
        corrupted = copy.deepcopy(self.rows)
        corrupted[-1]['photons_com3'] = str(D(corrupted[-1]['photons_com3']) + D('1e-5'))
        with self.assertRaisesRegex(ValueError, 'ledger|age variance'):
            audit.check_native(corrupted, 16, 4)

    def test_species_negative_and_axis_mutations_are_detected(self):
        for key, value in (('DI', '-1e-30'), ('refinement', '8'), ('opacity', '2'),
                           ('cx_rtol', '1e-14'), ('birth_mode', 'off')):
            with self.subTest(key=key):
                corrupted = copy.deepcopy(self.rows)
                corrupted[-1][key] = value
                with self.assertRaises(ValueError):
                    audit.check_native(corrupted, 16, 4)

    def test_empty_history_is_not_reclassified_as_solution_failure(self):
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            audit.check_native([], 16, 8)


if __name__ == '__main__':
    unittest.main()
