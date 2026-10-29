import csv, importlib.util, json, math, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'code/physical_data.py'
spec=importlib.util.spec_from_file_location('physical_data_tested',path)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class PhotoDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hashes,cls.table,cls.epochs,cls.events,cls.checks,cls.a=mod.calc()
    def test_primary_hashes(self):self.assertEqual(len(self.hashes),5)
    def test_saved_epoch_count(self):self.assertEqual(len(self.epochs),14)
    def test_event_count(self):self.assertEqual(len(self.events),98)
    def test_p19_knots(self):self.assertEqual(len(self.table),13)
    def test_positive_ionization(self):self.assertTrue(all(r['gamma_per_target_s']>0 for r in self.events))
    def test_positive_heating(self):self.assertTrue(all(r['heat_per_target_eV_s']>0 for r in self.events))
    def test_event_baryon_charge(self):
        self.assertLess(max(r['charge_difference'] for r in self.checks),1e-28)
        self.assertLess(max(r['baryon_residual'] for r in self.checks),1e-28)
    def test_absorbed_energy_ledger(self):
        for r in self.events:
            self.assertAlmostEqual(r['photoheat_eV_per_Href_s']+r['ionization_storage_eV_per_Href_s'],r['absorbed_photon_eV_per_Href_s'],delta=3e-30)
        self.assertLess(max(r['absorbed_energy_ledger_difference'] for r in self.checks),4e-30)
    def test_beta_kappa_changes_scale_not_excess_energy(self):
        for fid,cal in zip(self.epochs[0::2],self.epochs[1::2]):
            self.assertEqual(fid['saved_z'],cal['saved_z'])
            self.assertAlmostEqual(fid['mean_photoheat_eV_per_photoionization'],cal['mean_photoheat_eV_per_photoionization'],delta=1e-12)
    def test_one_photoelectron_per_event(self):
        for r in self.events:
            self.assertTrue(r['from_state'].split('_')[0] in ('H1','D','T','He3','He4'))
        self.assertEqual(set(r['event_index'] for r in self.events),set(range(1,8)))
    def test_mean_photon_energy_ordering(self):
        self.assertTrue(all(r['mean_absorbed_photon_eV_per_photoionization']>=r['mean_threshold_eV_per_photoionization'] for r in self.epochs))
    def test_photo_energy_eV_physical(self):
        for r in self.table:
            for k in ('HI','HeI','HeII'):
                self.assertGreater(r['Excess_'+k+'_eV_per_event'],0)
    def test_log_interpolation_no_extrapolation(self):
        port,bb,p19,rows,geo=mod.s.load_parent()
        for z in (-1,0,2.32,5,15.2):
            with self.assertRaises(ValueError):port.p19_moments(z,rows)
    def test_p19_source_d1_identity(self):
        p=json.loads((mod.PR261/'source/PUCHWEIN2019_13_ROW_PROJECTION.json').read_text())
        self.assertIn('rates_fiducial.txt',p['source'])
        self.assertNotIn('equivalent-equilibrium',p['source'])
    def test_selected_frozen_rows_are_not_new_ivp(self):
        data=json.loads((mod.PR262/'source/ON_REFINED_7_SAVED_ROWS.json').read_text())
        self.assertEqual(data['rows'][3]['z'],3.603019593287379)
        self.assertEqual(len(data['rows']),7)
    def test_21_no_fake_tau(self):
        with tempfile.TemporaryDirectory() as td:
            result=mod.run(td)
            self.assertIsNone(result['physical_tau'])
            self.assertEqual(result['new_ivps'],0)
            self.assertTrue((Path(td)/'REI_FROZEN_49_EVENTS_TWO_SCENARIOS.csv').is_file())
    def test_wrong_input_hash_fails_closed(self):
        # No modification of original sources, only immutable binding monkeypatch.
        label='rei_7_saved'; p,expected=mod.IMMUTABLE[label]
        with tempfile.NamedTemporaryFile() as junk:
            junk.write(b'corrupt');junk.flush()
            with patch.dict(mod.IMMUTABLE,{label:(Path(junk.name),expected)}):
                with self.assertRaisesRegex(ValueError,'SOURCE_IDENTITY_MISMATCH'):
                    mod.source_hashes()
    def test_17_nonnegative_populations(self):
        for r in mod.s.saved_rows(): self.assertTrue(all(y>=0 for y in r['y']))
    def test_event_scenarios_not_same_source_history(self):
        self.assertEqual({r['scenario'] for r in self.epochs},{'P19_D1_fiducial','P19_D1_BB13_GLs_nominal'})

if __name__=='__main__': unittest.main()
