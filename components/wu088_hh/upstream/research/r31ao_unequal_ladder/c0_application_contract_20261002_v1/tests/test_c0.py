import copy,json,sys,tempfile,unittest,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from c0_contract import derive_channels,validate_contract

class ChannelTests(unittest.TestCase):
    def test_all_49_preserved(self):
        self.assertEqual(len(derive_channels(ROOT)['rows']),49)
    def test_negative_and_positive_ritz_split(self):
        self.assertEqual(derive_channels(ROOT)['summary'].get('neutral_negative_energy'),25)
        self.assertEqual(derive_channels(ROOT)['summary'].get('neutral_positive_energy'),22)
    def test_actual_center_order_and_missing_duplicate_ground(self):
        r=derive_channels(ROOT)['rows']
        self.assertEqual([(x['row'],x.get('active_center'),x.get('j')) for x in r if x['row'] in (0,23,24,46)],[(0,0,0),(23,0,23),(24,1,1),(46,1,23)])
    def test_exact_gap_ground_zero(self):
        r=derive_channels(ROOT)['rows'];self.assertEqual([x['represented_gap_Eh'] for x in r if x['row']==0],['0/1'])
    def test_positive_states_not_physical_ionization(self):
        r=derive_channels(ROOT)['rows'];p=[x for x in r if x['kind']=='POSITIVE_ENERGY_PSEUDOSTATE']
        self.assertEqual(len(p),22);self.assertTrue(all(x['free_electron_delta'] is None and x['physical_rate_admitted'] is False for x in p))
    def test_ionic_electron_count_zero_and_no_threshold_fabrication(self):
        q=[x for x in derive_channels(ROOT)['rows'] if x['row']>=47]
        self.assertEqual(len(q),2);self.assertTrue(all(x['free_electron_delta']==0 and x['physical_threshold_J'] is None for x in q))
    def test_exact_source_q_not_fresh_symmetrization(self):
        q=derive_channels(ROOT)['q_columns'];self.assertEqual(len(q),25)
        self.assertEqual(q[8],{'column':8,'rows':[8,31],'weights_hex':['0x1.6a09e667f3bccp-1','-0x1.6a09e667f3bccp-1']})
    def test_corrupt_source_fails_before_processing(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);shutil.copytree(ROOT/'sources',p/'sources');shutil.copyfile(ROOT/'SOURCE_LOCK.json',p/'SOURCE_LOCK.json')
            f=p/'sources/FROZEN_INPUTS.npz';f.write_bytes(f.read_bytes()+b'X')
            with self.assertRaisesRegex(ValueError,'SOURCE_IDENTITY'):derive_channels(p)

# Integration tests use real generated declarations; no numerical HH fixtures.
class AdmissionTests(unittest.TestCase):
    def setUp(self):
        if not (ROOT/'APPLICATION_CONTRACT.json').exists():
            self.skipTest('declarations not generated in channel red stage')
        self.a=json.loads((ROOT/'APPLICATION_CONTRACT.json').read_text());self.c=json.loads((ROOT/'HH_CHANNEL_CROSSWALK.json').read_text());self.o=json.loads((ROOT/'RELEVANCE_OBLIGATIONS.json').read_text())
    def bad(self):self.assertTrue(validate_contract(self.a,self.c,self.o),'invalid contract was accepted')
    def test_valid_explicit_unresolved_contract(self):self.assertEqual(validate_contract(self.a,self.c,self.o),[])
    def test_duplicate_owner_rejected(self):self.a['processes'].append(copy.deepcopy(self.a['processes'][0]));self.bad()
    def test_alias_redshift_rejected(self):self.a['namespaces']['geometry_coordinate']='cosmological_redshift';self.bad()
    def test_alias_Doppler_rejected(self):self.a['namespaces']['hh_matrix']='doppler_factor';self.bad()
    def test_fabricated_domain_rejected(self):self.a['physical_domain']['temperature_K']['value']=[100,1e6];self.bad()
    def test_audit_sed_not_production_domain(self):self.a['audit_fixture']['is_physical_production_domain']=True;self.bad()
    def test_unadmitted_rate_must_not_replace_baseline(self):self.a['processes'][0]['hh_replaces_baseline']=True;self.bad()
    def test_ionic_count_mutation_rejected(self):self.c['rows'][47]['free_electron_delta']=1;self.bad()
    def test_pseudostate_admission_rejected(self):self.c['rows'][5]['physical_rate_admitted']=True;self.bad()
    def test_negligibility_needs_bound(self):self.c['rows'][0]['relevance']='PROVED_IRRELEVANT_IN_DOMAIN';self.bad()
    def test_duplicate_basis_row_rejected(self):self.c['rows'][1]['row']=0;self.bad()
    def test_missing_provider_is_not_certified(self):self.a['processes'][0]['provider_admitted']=True;self.bad()
    def test_gate_promotion_rejected(self):self.a['physical_application_admitted']=True;self.bad()
    def test_critical_obligation_not_deleted(self):self.o['items']=[x for x in self.o['items'] if x['id']!='O_HMINUS'];self.bad()

if __name__=='__main__':unittest.main()
