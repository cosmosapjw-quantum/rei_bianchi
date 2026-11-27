#!/usr/bin/env python3
"""Small publication-only tests that run in BASS_HE GitHub CI.

This is NOT an original 46k physical replay: use source-inclusive ZIP for that.
"""
import csv,hashlib,math,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'results/SCIENCE_RESULTS.json'
RESULT=json.loads(DATA.read_text())
EV=1.602176634e-12
class PublishedScience(unittest.TestCase):
    def test_authority(self):
        self.assertEqual(RESULT['project_repo'],'cosmosapjw-quantum/BASS_HE')
        self.assertEqual(RESULT['central_owner'],'cosmosapjw-quantum/rei_bianchi')
        self.assertTrue(RESULT['NO_LOCAL_UVB_RATE_SUBSTITUTION'])
    def test_scope(self):
        self.assertEqual(RESULT['canonical_delta'],0)
        self.assertEqual(RESULT['RUX04'],'NOT_ADMITTED')
        self.assertEqual(RESULT['BASS_HE_physical_reported'],'14/18')
        self.assertEqual(RESULT['REI_central_reported'],'28/88')
    def test_nodes_reported(self):
        self.assertEqual(RESULT['physical_nodes'],46080)
        self.assertEqual(RESULT['measured_observations'],0)
    def test_p19_bracket(self):
        a=RESULT['P19_log'];self.assertEqual(a['source_bracket'],[5.81,6.14]);self.assertAlmostEqual(a['fraction'],14/33,delta=1e-14)
    def test_excess_events(self):
        for kind in ('log','linear'):
            d=RESULT[f'P19_{kind}_counterfactual']
            self.assertAlmostEqual(sum(d['absorbed_events_per_s'].values())/d['total_absorbed_events_per_s'],1,delta=1e-14)
    def test_energy_units(self):
        for kind in ('log','linear'):
            d=RESULT[f'P19_{kind}_counterfactual']; z=RESULT[f'P19_{kind}']['species']
            en=sum(RESULT['native_global_neutral_counts'][sp]*z[sp]['excess_heat_eV_per_neutral_s']*EV for sp in ('HI','HeI','HeII'))
            self.assertAlmostEqual(en/d['total_excess_heat_erg_s'],1,delta=1e-14)
    def test_native_heii_unresolved(self):
        self.assertEqual(RESULT['native_source_events_per_s']['HeII'],0)
        self.assertGreater(RESULT['P19_log_formal_HeII_event_demand_s'],1e48)
    def test_original_source_chemical_energy_separate(self):
        self.assertLess(RESULT['P19_log_formal_HeII_threshold_energy_erg_s'],5e38)
        self.assertGreater(RESULT['P19_log_formal_HeII_threshold_energy_erg_s'],3e38)
    def test_native_heat_reconstruction(self):
        a=RESULT['native_total_photoheat_erg_s'];b=RESULT['owner_original_total_photoheat_erg_s']
        self.assertAlmostEqual(a/b,1,delta=1e-12)
    def test_witnesses(self):
        with (ROOT/'results/NINE_ORIGINAL_NODE_WITNESSES.csv').open(newline='') as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),9)
        for x in rows:
            self.assertGreater(float(x['N_HI']),0)
            self.assertGreater(float(x['P19log_HeII_events_s']),0)
    def test_owner_csv_exact_git_blob(self):
        p=ROOT/'inputs/REI_original_heating_moment_owner.csv';b=p.read_bytes();g=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
        self.assertEqual(g,RESULT['native_heating_owner_blob'])
    def test_input_p19_git_blob(self):
        # Original 13-row Table D1 projection is already published in parent BASS_HE PR141.
        p=ROOT.parents[1]/'research/rei_igm_p19_highz_20261101/data/P19_D1_ORIGINAL_HIGHZ_13.csv'
        if p.is_file():self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),RESULT['source_table_projection_sha256'])
        else:self.skipTest('parent Git tree not checked out: source-inclusive ZIP is definitive')
    def test_group_matrix(self):
        with (ROOT/'results/ORIGINAL_FOUR_GROUP_PHOTON_ENERGY.csv').open(newline='') as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),4)
        self.assertEqual(rows[-1]['group'],'G3')
        assert all(float(r['source_excess_heat_erg_s'])>=0 for r in rows)
    def test_publication_sha_identity(self):
        for key,name in [('source_witness_csv_sha256','NINE_ORIGINAL_NODE_WITNESSES.csv'),('source_4_group_csv_sha256','ORIGINAL_FOUR_GROUP_PHOTON_ENERGY.csv')]:
            digest=hashlib.sha256((ROOT/'results'/name).read_bytes()).hexdigest()
            self.assertEqual(digest,RESULT[key])
if __name__=='__main__':unittest.main()