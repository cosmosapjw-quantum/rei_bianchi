"""Focused BASS_HE→REI original source/receiver physics and negative controls."""
import csv
import io
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import crosswalk as cw

ROOT=Path(__file__).resolve().parents[1]
class Crosswalk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths=cw.ensure_source_inputs(ROOT)
        cls.p19,cls.states,cls.photon,cls.rei,cls.excess=cw.read_original(cls.paths)
        cls.result=json.loads((ROOT/'results/SCIENCE_RESULTS.json').read_text())

    def test_all_original_sha(self):
        for name in ('REI_STATE','REI_SOURCE','P19'):
            self.assertEqual(cw.filehash(self.paths[name]),cw.ARCHIVE_SHAS[name])

    def test_original_excess_git_blob(self):
        self.assertEqual(cw.gitblob(self.paths['CAL'].read_bytes()),cw.REI_HEATING_GITBLOB)

    def test_p19_numeric_projection(self):
        with ZipFile(self.paths['P19']) as f:
            self.assertEqual(cw.digest(f.read('data/P19_D1_ORIGINAL_HIGHZ_13.csv')),cw.P19_PROJECTION_SHA256)
        self.assertEqual(len(self.p19),13)

    def test_endpoint_interpolant(self):
        for kind in ('linear','log'):
            p=cw.p19_interpolate(self.p19,5.81,kind)
            self.assertAlmostEqual(p['species']['HI']['gamma_per_neutral_s']/float(self.p19[1]['Gamma_HI_s']),1.,delta=1e-13)

    def test_monotone_rate(self):
        p=cw.p19_interpolate(self.p19,5.95,'log')
        for s in cw.SPECIES:
            y=p['species'][s]['gamma_per_neutral_s']
            self.assertGreater(y,0)
            self.assertGreater(y,float(self.p19[2][f'Gamma_{s}_s']))
            self.assertLess(y,float(self.p19[1][f'Gamma_{s}_s']))

    def test_interpolation_sensitivity_is_not_10_percent(self):
        log=cw.p19_interpolate(self.p19,5.95,'log')['species']
        lin=cw.p19_interpolate(self.p19,5.95,'linear')['species']
        self.assertGreater(lin['HI']['gamma_per_neutral_s']/log['HI']['gamma_per_neutral_s'],5)
        self.assertGreater(lin['HeI']['gamma_per_neutral_s']/log['HeI']['gamma_per_neutral_s'],3)

    def test_wrong_interpolant(self):
        with self.assertRaises(ValueError): cw.p19_interpolate(self.p19,5.95,'bad')

    def test_physical_node_count_and_unique_join(self):
        self.assertEqual(len(self.states),46080)
        self.assertEqual(len(self.photon),46080)
        self.assertEqual(len(set(int(x['node']) for x in self.photon)),46080)

    def test_source_global_photon_budget(self):
        rows=[r for r in self.rei['group_rows'] if r['case']=='accepted_at_tick160']
        native=self.result['native_source_events_per_s']
        for k,s in enumerate(cw.SPECIES):
            tot=math.fsum(r['current_photons_per_s']*r['species_fraction'][k] for r in rows)
            self.assertAlmostEqual(tot,native[s],delta=max(1e-12*tot,1e-250))

    def test_source_primary_heat_and_units(self):
        a=self.result['native_total_photoheat_erg_s'];b=self.rei['snapshots'][2]['source_photoheat_erg_per_s']
        self.assertAlmostEqual(a,b,delta=1e-12*b)
        self.assertEqual(self.result['native_source_events_per_s']['HeII'],0)

    def test_native_original_neutral_moments(self):
        for s in cw.SPECIES:
            p=self.result['native_global_neutral_counts'][s]
            q=self.result['source_neutral_counts_recomputed'][s]
            self.assertLess(abs(p-q)/p,2e-7)

    def test_he_h_abundance_independent_reconstruction(self):
        j=self.result['helium_to_hydrogen_from_independent_owner_routes']
        self.assertEqual(j['expected'],.079)
        self.assertLess(abs(j['max']-.079)/.079,1e-5)
        self.assertLess(abs(j['min']-.079)/.079,1e-5)

    def test_heii_source_gap(self):
        r=self.result
        self.assertEqual(r['REI_hard_group_G3_current_photons_s'],float.fromhex('0x0.0000000000001p-1022'))
        self.assertGreater(r['P19_log_formal_HeII_event_demand_s'],1e48)
        self.assertGreater(r['P19_log_formal_HeII_threshold_energy_erg_s'],1e38)

    def test_key_ratio_and_source_scope(self):
        r=self.result
        self.assertAlmostEqual(r['P19_rate_over_native_rate_log']['HI'],72.28438289572635,delta=1e-8)
        self.assertAlmostEqual(r['P19_log_counterfactual']['ratio_formal_P19_excess_heat_to_REI'],7.11307759650658,delta=1e-9)
        self.assertTrue(r['NO_LOCAL_UVB_RATE_SUBSTITUTION'])
        self.assertEqual(r['canonical_delta'],0)
        self.assertEqual(r['REI_central_reported'],'28/88')
        self.assertEqual(r['BASS_HE_physical_reported'],'14/18')

    def test_46080_csv_sha_and_energy(self):
        r=self.result
        q=ROOT/'results'/r['source_data_csv']
        self.assertEqual(cw.filehash(q),r['source_data_csv_sha256'])
        import gzip
        with gzip.open(q,'rt') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),46080)
        self.assertTrue(all(math.isfinite(float(row['P19log_excess_heat_erg_s'])) and float(row['native_photoheat_erg_s'])>=0 for row in rows))

    def test_mutation_sha_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);(d/'inputs').mkdir()
            for name,fn in [('P19','REI_IGM_P19_D1_HIGHZ_SOURCE_20261101.zip'),('REI_STATE','REI_PR320_ORIGINAL_TICK160_NODE_PHYSICS.zip'),('REI_SOURCE','REI_IGM_TICK160_GLOBAL_PHOTON_JACOBIAN_CI_20261101.zip')]:
                if name=='P19': (d/'inputs'/fn).write_bytes(b'bad fixture')
                else: (d/'inputs'/fn).symlink_to(self.paths[name])
            (d/'inputs'/'REI_original_heating_moment_owner.csv').symlink_to(self.paths['CAL'])
            with self.assertRaises(ValueError):cw.ensure_source_inputs(d)

if __name__=='__main__': unittest.main()