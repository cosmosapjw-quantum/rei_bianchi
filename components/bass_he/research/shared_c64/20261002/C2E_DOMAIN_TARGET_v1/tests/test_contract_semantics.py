"""Manufactured counterexamples to known authority/target promotion errors."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
from validate_contract import validate

class ContractSemantics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.base=json.loads((ROOT/'contract/C2E_TARGET_AND_DOMAIN_CONTRACT.json').read_bytes())
    def reject(self,code,mutate):
        c=copy.deepcopy(self.base);mutate(c);r=validate(c)
        self.assertFalse(r['contract_valid']);self.assertIn(code,r['errors']);self.assertFalse(r['physical_launch_enabled'])
    def test_frozen_contract_valid_but_launch_disabled(self):
        r=validate(self.base);self.assertTrue(r['contract_valid']);self.assertFalse(r['physical_launch_enabled']);self.assertEqual(r['production_domain_status'],'UNRESOLVED')
    def test_reject_proxy_cutoff(self):
        self.reject('DIAGNOSTIC_CUTOFF_PROMOTION',lambda c:c['collision_domain'].update(diagnostic_cutoffs_imported_as_physical_domain=True))
    def test_reject_unregistered_physical_interval(self):
        self.reject('UNREGISTERED_PRODUCTION_INPUT',lambda c:c['collision_domain'].update(production_R_interval=[.013,64]))
    def test_reject_energy_frame_alias(self):
        self.reject('ENERGY_FRAME_ALIASING',lambda c:c['collision_domain'].update(source_energy_frames_are_interchangeable=True))
    def test_reject_charge_center_as_mass_center(self):
        self.reject('ORIGIN_CM_ALIASING',lambda c:c['conventions'].update(nuclear_center_of_mass_is_electronic_origin=True))
    def test_reject_bright_pair_full_gap(self):
        self.reject('OMITTED_DEGENERATE_PARTNER',lambda c:c['targets']['fixed_pair'].update(full_H_external_gap=.1))
    def test_reject_missing_pi_partner(self):
        self.reject('CLUSTER_MULTIPLICITY',lambda c:c['targets']['large_R_rank5'].update(sector_ranks={'m0':3,'m_plus1':1,'m_minus1':0}))
    def test_reject_incoming_channel_in_pair(self):
        self.reject('PAIR_INCOMING_CHANNEL_ALIAS',lambda c:c['targets']['fixed_pair'].update(incoming_H1s_included=True))
    def test_reject_ritz_gap_certificate(self):
        self.reject('GAP_CERTIFICATE_NOT_ESTABLISHED',lambda c:c['targets']['large_R_rank5'].update(certified_external_gap_lower_bound=.05))
    def test_reject_global_UA_correlation_claim(self):
        self.reject('UNPROVED_GLOBAL_CORRELATION',lambda c:c['targets']['large_R_rank5'].update(actual_UA_correlation_established=True))
    def test_reject_L2_as_observable_certificate(self):
        self.reject('ENCLOSURE_PROMOTION',lambda c:c['error_contract'].update(L2_projector_error_certifies_Ly_matrix_elements=True))
    def test_reject_D1_replacement(self):
        self.reject('D1_MODEL_PROMOTION',lambda c:c['targets']['D1_model'].update(replaced_by_rank5_or_rank6_automatically=True))
    def test_reject_Eq55_promotion(self):
        self.reject('GLOBAL_GATE_MUTATION',lambda c:c['global_gates'].update(Eq55_next_node_authorized=True))
    def test_reject_tolerance_copy(self):
        self.reject('UNREGISTERED_NUMERICAL_CONTRACT',lambda c:c['error_contract'].update(new_numeric_tolerances={'projector':1e-8}))
    def test_reject_missing_structure(self):
        r=validate({});self.assertFalse(r['contract_valid']);self.assertIn('MISSING_OR_MALFORMED_REQUIRED_FIELD',r['errors'])

if __name__=='__main__':unittest.main(verbosity=2)
