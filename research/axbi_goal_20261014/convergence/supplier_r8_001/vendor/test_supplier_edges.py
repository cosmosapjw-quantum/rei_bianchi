"""Changed-surface integration and preserved owner contract checks (tests-after)."""
import hashlib,io,json,pathlib,tempfile,unittest,sys
from contextlib import redirect_stdout
from fractions import Fraction as Q
import test_combined_reducer as T
ROOT=T.ROOT
from source_pair_guard import require_source_relation,SourceRelationHold
from reconstruction_support import reconstruction_norm,interpolation_envelope
class SupplierEdges(unittest.TestCase):
    def test_reviewed_pair_allows_refinement_but_no_science_admission(self):
        with tempfile.TemporaryDirectory() as d:
            res,_=T.run_pair(pathlib.Path(d),unequal=True,relation=True,kind='REFINEMENT')
            self.assertEqual(res['status'],'DIAGNOSTIC_REDUCTION_COMPLETE_RESPONSE_UNRESOLVED')
            self.assertEqual(res['scientific_admission'],'NOT_ISSUED');self.assertEqual(res['solver_runs'],0)
            self.assertTrue(res['source_relation_status'].startswith('DECLARED_REVIEWED'))
            self.assertTrue(all(x['true_ivp_error'] is None for x in res['metrics']))
    def test_actual_T1_relation_binds_actual_two_source_hashes(self):
        relation=json.loads((ROOT/'supplier/T1_SOURCE_RELATION.json').read_text());v=relation['source_relation']
        out=require_source_relation({'source_identity':{'sha256':v['reference_sha256']}},
          {'source_identity':{'sha256':v['candidate_sha256']}},relation)
        self.assertEqual(out,'DECLARED_REVIEWED_SEMANTIC_RELATION_NOT_PROVED_BY_REDUCER')
        self.assertFalse(relation['run_authorized_now'])
    def test_wrong_pair_not_accepted_by_real_relation(self):
        relation=json.loads((ROOT/'supplier/T1_SOURCE_RELATION.json').read_text());v=relation['source_relation']
        with self.assertRaises(SourceRelationHold):require_source_relation({'source_identity':{'sha256':'0'*64}},
          {'source_identity':{'sha256':v['candidate_sha256']}},relation)
    def test_default_sampling_retains_numerical_values(self):
        orig=T.load(ROOT/'vendor/compare_histories_original.py','original_for_parity')
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);res,manifest=T.run_pair(root,mode='SAMPLED_ONLY')
            with redirect_stdout(io.StringIO()):old=orig.run(root/'manifest.json',root/'old_out')
            self.assertEqual(len(res['metrics']),len(old['metrics']))
            for new,prior in zip(res['metrics'],old['metrics']):
                for k in ['sampled_sup_absolute_difference','signed_difference_at_sup','endpoint_difference','initial_difference']:
                    self.assertEqual(new[k],prior[k])
                self.assertNotIn('reconstruction_sup_exact',new)
            self.assertEqual((root/'out/milestones.csv').read_bytes(),(root/'old_out/milestones.csv').read_bytes())
    def test_invalid_mode_has_no_comparison_csv(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);res,_=T.run_pair(root,mode='TRUE_IVP_FROM_SAMPLES')
            self.assertEqual(res['status'],'HOLD_RECONSTRUCTION_NORM_MODE')
            self.assertFalse((root/'out/comparison_summary.csv').exists())
    def test_missing_witness_is_not_zero_radius(self):
        r=interpolation_envelope(0,1,Q(1,2),None,0,0)
        self.assertIsNone(r['radius']);self.assertIn('UNKNOWN',r['status'])
    def test_union_norm_refuses_unmatched_coverage(self):
        with self.assertRaises(ValueError):reconstruction_norm([(0,0),(1,1)],[(0,0),(2,1)],'LN_A')
    def test_union_norm_uses_stored_float_not_exact_log(self):
        r=reconstruction_norm([(0.,0.),(1.,.1)],[(0.,0.),(1.,.2)],'LN_A')
        self.assertEqual(r['sup_absolute_difference'],Q.from_float(.2)-Q.from_float(.1))
        self.assertIsNone(r['true_ivp_error'])
    def test_relation_nonobject_is_rejected(self):
        with self.assertRaises(SourceRelationHold):require_source_relation({'source_identity':{'sha256':'0'*64}},
             {'source_identity':{'sha256':'1'*64}},{'source_relation':['not','a','relation']})
    def test_other_floors_are_preserved(self):
        orig=T.load(ROOT/'vendor/compare_histories_original.py','original_for_floors');case={'factors':(.7546,.06135)}
        for name in ['x_HI','x_HII','x_HeI','x_HeII','x_HeIII','Y_H_I','Y_He_III','Y_electron','Tgas_K','ne_cm3']:
            self.assertEqual(T.M.floor(name,case),orig.floor(name,case))
    def test_vendor_helpers_preserved_byte_identical(self):
        for f in ['source_pair_guard.py','reconstruction_support.py']:
            self.assertEqual((ROOT/'vendor'/f).read_bytes(),(ROOT/'supplier'/f).read_bytes())
        self.assertEqual(hashlib.sha256((ROOT/'vendor/compare_histories_original.py').read_bytes()).hexdigest(),
                         'b49fbed5f31a45e866915846357d1ddfdef8708ff7ba97ed17695ec8a5c3dc60')
    def test_owner_incomplete_history_remains_hold(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);_,manifest=T.run_pair(root)
            p=pathlib.Path(manifest['candidate']['terminal']['path']);p.write_text('status=STOPPED_CHECKPOINTED\n')
            manifest['candidate']['terminal']['sha256']=T.sha(p)
            (root/'manifest.json').write_text(json.dumps(manifest))
            with redirect_stdout(io.StringIO()):res=T.M.run(root/'manifest.json',root/'incomplete')
            self.assertEqual(res['status'],'UNKNOWN_INCOMPLETE_HISTORY');self.assertIsNone(res['metrics'])
if __name__=='__main__':unittest.main(verbosity=2)
