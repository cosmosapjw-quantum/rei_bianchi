import csv, json, math, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import exposure as e

class ExposureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o=e.compute()

    def test_immutability_positive(self):
        events,epochs=e.source_load()
        self.assertEqual((len(events),len(epochs)),(98,14))
        self.assertTrue(all(float(r['photoelectrons_created_per_Href_s'])>0 for r in events))

    def test_corrupt_archive_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.zip';p.write_bytes(b'bad')
            with patch.object(e,'PARENT',p):
                with self.assertRaisesRegex(ValueError,'PARENT_ZIP_SHA_MISMATCH'):
                    e.source_load()

    def test_positive_integrals(self):
        for r in self.o['interval_events']:
            for key in e.QUANTITIES:
                self.assertGreater(r['loglinear_'+key],0)
                self.assertGreater(r['trapezoid_'+key],0)

    def test_grains_and_order(self):
        self.assertEqual([len(self.o[k]) for k in ['interval_events','interval_summaries','totals','cumulative']], [84,12,2,14])
        self.assertEqual({r['scenario'] for r in self.o['totals']},set(e.SCENARIOS))
        self.assertEqual(len(self.o['crossovers']),2)
        for r in self.o['interval_events']:
            self.assertGreater(r['dt_s'],0)
            self.assertGreater(r['t_end_s'],r['t_begin_s'])
            self.assertGreater(r['from_saved_z'],r['to_saved_z'])

    def test_energy_ledgers(self):
        for r in self.o['interval_events']+self.o['interval_summaries']+self.o['totals']:
            for p in ['loglinear_','trapezoid_']:
                ion=r[p+e.QUANTITIES[2]]; heat=r[p+e.QUANTITIES[1]]; absorbed=r[p+e.QUANTITIES[3]]
                self.assertAlmostEqual((heat+ion)/absorbed,1,places=13)

    def test_interval_sums(self):
        for r in self.o['interval_summaries']:
            subset=[x for x in self.o['interval_events'] if x['scenario']==r['scenario'] and x['interval_index']==r['interval_index']]
            self.assertEqual(len(subset),7)
            for kind in ('loglinear_','trapezoid_'):
                for key in e.QUANTITIES:
                    self.assertAlmostEqual(sum(x[kind+key] for x in subset)/r[kind+key],1,places=13)

    def test_cumulative_and_totals(self):
        for r in self.o['totals']:
            rows=sorted([x for x in self.o['cumulative'] if x['scenario']==r['scenario']], key=lambda x:x['time_knot_index'])
            self.assertEqual(len(rows),7)
            for k in e.QUANTITIES:
                self.assertAlmostEqual(rows[-1]['loglinear_'+k]/r['loglinear_'+k],1,places=13)
            self.assertEqual(rows[0]['loglinear_photoelectrons_per_Href'],0)
            self.assertGreater(r['electron_interpolant_sensitivity_frac'],0)
            self.assertLess(r['electron_interpolant_sensitivity_frac'],1)

    def test_logarithmic_mean_inequality(self):
        for a,b in [(1,1),(1,3),(5,7),(1e-30,2e-30),(1e-15,1e-15*(1+1e-12))]:
            v=e.logmean(a,b)
            self.assertLessEqual(v/(0.5*(a+b)),1+1e-12)
            self.assertGreaterEqual(v/math.sqrt(a*b),1-1e-12)

    def test_bad_nonpositive(self):
        for a,b in [(0,1),(-1,2),(1,float('nan'))]:
            with self.assertRaises(ValueError):e.logmean(a,b)

    def test_interpolation_is_not_proved_error(self):
        result=e.run()
        self.assertIsNone(result['physical_tau'])
        self.assertIsNone(result['actual_rei_p19_trajectory'])
        self.assertTrue(result['interpolant_sensitivity_is_not_error_bound'])
        self.assertEqual(result['new_ivps'],0)

    def test_crossover_bracketing(self):
        for r in self.o['crossovers']:
            self.assertGreater(r['at_mean_z_label_linear_time_proxy'],min(r['bracketed_z']))
            self.assertLess(r['at_mean_z_label_linear_time_proxy'],max(r['bracketed_z']))
        self.assertAlmostEqual(self.o['crossovers'][0]['at_elapsed_proper_s_proxy']/self.o['crossovers'][1]['at_elapsed_proper_s_proxy'],1,places=12)

    def test_source_historical_charge_change_not_exposure(self):
        # This large source-only integral may exceed a change in a frozen charge field.
        # This is allowed; it MUST NOT be equated with an evolved ionic fraction.
        for r in self.o['totals']:
            self.assertGreater(r['loglinear_photoelectrons_per_Href'],1)

if __name__=='__main__':unittest.main()
