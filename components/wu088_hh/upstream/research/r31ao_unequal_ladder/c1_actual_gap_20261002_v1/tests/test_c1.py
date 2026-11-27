from pathlib import Path
from fractions import Fraction as Q
import copy, json, shutil, tempfile, unittest, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import exact_gap_binding as b
import machine_predicate_bridge as p

class IntakeTests(unittest.TestCase):
    def test_actual_source_bound_shapes_and_nine_members(self):
        x=b.load_inputs(ROOT)
        self.assertIsInstance(x,dict,'source-bound actual intake is required')
        self.assertEqual(len(x['raw_col']),47)
        self.assertEqual(len(x['raw_row']),2)
        self.assertEqual(set(x['models']),{'R31AK','R31Z','R31AD'})
        self.assertEqual(len(x['bindings']['prediction_members']),9)
        self.assertTrue(all(isinstance(z[0],Q) for row in x['raw_col'] for z in row))
    def test_changed_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);shutil.copytree(ROOT/'inputs',r/'inputs');shutil.copytree(ROOT/'authority',r/'authority');shutil.copytree(ROOT/'vendor',r/'vendor');shutil.copy(ROOT/'SOURCE_LOCK.json',r)
            (r/'inputs/C.exact_dyadic.json').write_text('{}')
            with self.assertRaises(ValueError): b.load_inputs(r)
    def test_lock_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);(r/'SOURCE_LOCK.json').write_text('{}')
            with self.assertRaises(ValueError): b.load_inputs(r)
    def test_stored_K_is_not_reconstructed(self):
        x=b.load_inputs(ROOT)
        self.assertIsInstance(x,dict,'independent stored K required')
        different=False
        for m in x['models'].values():
            for i in range(47):
                for j in range(2):
                    dc=m['D_col'][i][j];dr=m['D_row'][j][i]
                    reconstructed=((dc[0]-dr[0])/2,(dc[1]+dr[1])/2)
                    different |= reconstructed != m['K'][i][j]
        self.assertTrue(different)
    def test_fortran_row_layout_recorded(self):
        x=b.load_inputs(ROOT)
        self.assertIsInstance(x,dict,'Fortran row semantics required')
        self.assertEqual(sum(y['fortran_order'] for y in x['bindings']['prediction_members']),3)
    def test_preoutput_selected_hashes_match(self):
        x=b.load_inputs(ROOT)
        self.assertIsInstance(x,dict,'pre-output array identities required')
        self.assertTrue(all(x['bindings']['selected_array_hashes_verified'].values()))

class ScalarTests(unittest.TestCase):
    def test_primary_secondary_boundary_difference_preserved(self):
        a='0.9999999999'; z='0.0'; one='1.0'
        x=p.audit_tokens([a,z],[one,z],'PRIMARY')
        y=p.audit_tokens([a,z],[one,z],'SECONDARY')
        self.assertIsInstance(x,dict,'exact source-operation replay required')
        self.assertTrue(x['rne']['frozen_binary64_supported'])
        self.assertFalse(y['rne']['frozen_binary64_supported'])
    def test_known_wide_margin_is_mode_robust(self):
        x=p.audit_tokens(['0.05','0.054'],['0.109','0.142'],'SECONDARY')
        self.assertIsInstance(x,dict)
        self.assertTrue(x['all_ieee_modes_supported'])
    def test_exact_strict_tie_is_not_improvement(self):
        x=p.audit_tokens(['0.0','0.0'],['1e-10','0.0'],'PRIMARY')
        self.assertIsInstance(x,dict)
        self.assertFalse(x['rne']['frozen_binary64_supported'])
    def test_invalid_comparison_rejected(self):
        with self.assertRaises(ValueError):p.audit_tokens(['0.0']*2,['1.0']*2,'WHATEVER')
    def test_nonfinite_tokens_rejected(self):
        for token in ['NaN','Infinity','-1.0','1e999999',True,1.0]:
            with self.subTest(token=token),self.assertRaises(ValueError):p.audit_tokens([token,'0.0'],['1.0','1.0'],'PRIMARY')
    def test_wrong_metric_count_rejected(self):
        with self.assertRaises(ValueError):p.audit_tokens(['0.0'],['1.0'],'PRIMARY')

class ActualTests(unittest.TestCase):
    def test_actual_four_gaps_and_missing_epsilon(self):
        result=b.evaluate(ROOT)
        self.assertIsInstance(result,dict,'actual Gram evaluation required')
        self.assertEqual(result['status'],'C1_REPRESENTED_GAPS_VERIFIED__CONTINUOUS_TARGET_UNRESOLVED')
        self.assertEqual(result['final_verdict'],'UNRESOLVED_INPUTS')
        self.assertIsNone(result['epsilon'])
        self.assertFalse(result['admission']['continuous_target_certificate'])
        self.assertEqual(set(result['represented_gaps']),{'PRIMARY','SECONDARY'})
        for c in result['represented_gaps'].values():
            for v in c.values():
                self.assertGreater(Q(v['lo']),0)
                self.assertGreaterEqual(Q(v['hi']),Q(v['lo']))
    def test_historical_scalar_replay_matches_both_verdicts(self):
        r=b.evaluate(ROOT)
        self.assertIsInstance(r,dict)
        for v in r['machine_bridge'].values():
            self.assertTrue(v['archived_verdict_matches'])
            self.assertTrue(v['all_ieee_modes_supported'])
            self.assertFalse(v['historical_fenv_verified'])
    def test_retrospective_eta_covers_both_endpoints(self):
        r=b.evaluate(ROOT)
        self.assertIsInstance(r,dict)
        for comp,met in r['legacy_comparison'].items():
            for k,d in met.items():
                g=Q(d['reconstructed_rne_gap']); e=Q(d['eta_upper'])
                iv=r['represented_gaps'][comp][k]
                self.assertGreaterEqual(e,abs(g-Q(iv['lo'])))
                self.assertGreaterEqual(e,abs(g-Q(iv['hi'])))
        self.assertFalse(r['arithmetic']['eta_added_to_direct_route'])

if __name__=='__main__':unittest.main()
