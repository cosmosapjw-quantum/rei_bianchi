import sys
from pathlib import Path as _Path
sys.path.insert(0,str(_Path(__file__).resolve().parent.parent))
import csv
from pathlib import Path
import math
import unittest
import numpy as np
import igm_reference as ref

def repository_root():
    import os
    candidates=[]
    if os.environ.get('IGM_REPO_ROOT'): candidates.append(Path(os.environ['IGM_REPO_ROOT']))
    candidates.extend(Path(__file__).resolve().parents)
    for path in candidates:
        if (path/'rust/rei_microphysics/tests/data/igm_grackle').is_dir(): return path
    raise RuntimeError('Run tests inside repository tools/ or set IGM_REPO_ROOT to the repository root')

REPO=repository_root()
DATA=REPO/'rust/rei_microphysics/tests/data/igm_grackle/grackle_literal_reference.csv'

class SourceTests(unittest.TestCase):
    def test_independent_rates_match_pinned_literal_c_at_branch_joins(self):
        with DATA.open() as stream:
            for row in csv.DictReader(stream):
                t = float(row['T_K'])
                actual = ref.coefficients(t)
                for key in ref.RATE_COLUMNS:
                    expected = float(row[key])
                    self.assertLessEqual(abs(actual[key]-expected),2e-12*abs(expected),f'{key} T={t}')

    def test_positive_sed_quadrature_converges_to_analytic_number_and_energy(self):
        lo,hi = 13.7,100.0
        exact_energy = math.log(hi/lo)/(1/lo-1/hi)
        errors = []
        for n in (1,2,4,8,16):
            energy, weight = ref.spectral_nodes(lo,hi,n)
            self.assertGreater(len(weight),0)
            self.assertTrue(np.all(weight>0))
            errors.append(abs(weight.sum()-1)+abs(weight@energy-exact_energy)/exact_energy)
        self.assertTrue(all(b<a for a,b in zip(errors,errors[1:])),errors)
        self.assertLess(errors[-1],2e-6)

CONFIG = dict(h0=2.2e-18, omega_r=9e-5, omega_m=.3, omega_b=.048, omega_lambda=.69991, y_he=.24, tcmb0=2.7255, z_start=12., z_end=11.5, x_hii=2e-4, x_heii=0., x_heiii=0., temperature_k=30., source_rate=1e-15, energy_min_ev=13.7, energy_max_ev=100., birth_panels=16, energy_panels=2, max_packets=20000, max_steps=200000)

class PhysicsTests(unittest.TestCase):
    def test_birth_source_uses_proper_time_once_and_is_gas_step_independent(self):
        from scipy.integrate import quad
        cfg = dict(CONFIG, energy_panels=16)
        births = ref.build_births(cfg)
        self.assertGreater(len(births),0)
        t0,t1 = -math.log1p(cfg['z_start']),-math.log1p(cfg['z_end'])
        exact = cfg['source_rate']*quad(lambda l: 1/ref.background(cfg,l)['H'],t0,t1,epsabs=.01,epsrel=1e-13)[0]
        self.assertLess(abs(births[:,2].sum()/exact-1),2e-7)
        self.assertTrue(np.all(births[:,0]>t0)&np.all(births[:,0]<t1))
        np.testing.assert_array_equal(births,ref.build_births(dict(cfg,max_dln_a=1e-8)))

    def test_verner_cutoff_is_distinct_from_binding_and_has_three_owners(self):
        for i,c in enumerate(ref.CUTOFF):
            self.assertEqual(ref.cross_sections(np.array([np.nextafter(c,0)]))[0,i],0.)
            self.assertGreater(ref.cross_sections(np.array([c]))[0,i],0.)
        self.assertTrue(np.all(ref.cross_sections(np.array([70.]))>0))

    def test_local_coupled_equations_close_number_and_energy(self):
        cfg=CONFIG
        l=-math.log1p(12.)
        fractions=np.array([.2,.3,.1])
        w=1.5*ref.KB*40000*(1+ref.he_ratio(cfg)+fractions[0]+ref.he_ratio(cfg)*(fractions[1]+2*fractions[2]))
        gas=np.r_[fractions,w]
        ev=np.array([20.,40.,70.])
        photons=np.array([.01,.02,.03])
        out=ref.evaluate(cfg,l,gas,ev,photons)
        self.assertTrue(np.all(out['photo']>0))
        self.assertAlmostEqual(-sum(out['photon_dt']),sum(out['photo']),delta=1e-24)
        bdot=ref.EV*(ref.CHI[0]*out['gas_dt'][0]+ref.he_ratio(cfg)*(ref.CHI[1]*out['gas_dt'][1]+sum(ref.CHI[1:])*out['gas_dt'][2]))
        budget=out['gas_dt'][3]+bdot+ref.EV*np.dot(ev,out['photon_dt'])+out['escape']+out['work']+out['cmb_reservoir']
        self.assertLess(abs(budget),1e-12*abs(out['escape']+out['work']))

class HistoryTests(unittest.TestCase):
    def test_zero_source_neutral_limit_is_adiabatic_and_no_photon_floor(self):
        cfg=dict(CONFIG,source_rate=0.,x_hii=0.,z_end=11.995,output_panels=2,birth_panels=1,energy_panels=1)
        result=ref.solve_history(cfg)
        self.assertEqual(len(result['rows']),3)
        row=result['rows'][-1]
        self.assertEqual(row['Nactive'],0.)
        self.assertEqual(row['x_hii'],0.)
        self.assertEqual(row['x_heii'],0.)
        self.assertEqual(row['x_heiii'],0.)
        exact=30*((1+cfg['z_end'])/(1+cfg['z_start']))**2
        self.assertLess(abs(row['T']/exact-1),1e-10)
        self.assertLess(abs(row['energy_residual']),1e-25)

    def test_small_source_history_grows_neutral_helium_and_closes_ledgers(self):
        cfg=dict(CONFIG,z_end=11.995,output_panels=2,birth_panels=1,energy_panels=1)
        result=ref.solve_history(cfg)
        self.assertEqual(len(result['rows']),3)
        row=result['rows'][-1]
        self.assertGreater(row['x_heii'],0.)
        self.assertGreater(row['x_heiii'],0.)
        self.assertGreater(row['abs_HI'],0.)
        self.assertLess(abs(row['number_residual']),1e-10*max(1e-10,row['emitted_N']))
        self.assertLess(abs(row['energy_residual']),1e-10*max(1e-20,row['emitted_E']))
        self.assertEqual(result['stats']['completed'],True)

class EventAndReadoutTests(unittest.TestCase):
    def test_born_subcutoff_photons_outflow_at_actual_birth_energy(self):
        cfg=dict(CONFIG,z_end=11.999,output_panels=2,birth_panels=1,energy_panels=1,energy_min_ev=10.,energy_max_ev=12.)
        result=ref.solve_history(cfg)
        row=result['rows'][-1]
        self.assertEqual(row['out_N'],row['emitted_N'])
        self.assertLess(abs(row['out_E']-row['emitted_E']),1e-28)
        self.assertEqual(row['Nactive'],0.)
        self.assertEqual(row['redshift_E'],0.)
        self.assertEqual(len(result['packets']),0)

    def test_exact_cutoff_removes_survivors_and_closes_number_energy(self):
        cfg=dict(CONFIG,z_end=11.999,output_panels=2,birth_panels=1,energy_panels=1,energy_min_ev=13.60001,energy_max_ev=13.6001)
        result=ref.solve_history(cfg,rtol=1e-11,atol=1e-14)
        row=result['rows'][-1]
        self.assertEqual(row['Nactive'],0.)
        self.assertGreater(row['out_N'],0.)
        self.assertLess(abs(row['out_E']/(ref.CUTOFF[0]*ref.EV*row['out_N'])-1),1e-14)
        self.assertLess(abs(row['number_residual']),1e-10*row['emitted_N'])
        self.assertLess(abs(row['energy_residual']),1e-10*row['emitted_E'])

    def test_authoritative_log_counts_survive_ieee_readout_extinction(self):
        cfg=dict(CONFIG,z_end=11.98,output_panels=2,birth_panels=1,energy_panels=1)
        result=ref.solve_history(cfg)
        packets=result['packets']
        self.assertEqual(len(packets),len(result['births']))
        self.assertTrue(np.any((packets[:,4]<-750)&(packets[:,6]==0)))
        self.assertGreater(result['stats']['ieee_tail_packets'],0)
        self.assertLess(result['stats']['ieee_underflow_N_bound'],1e-20)
        self.assertLess(result['stats']['ieee_underflow_E_bound'],1e-30)

class ConfigTests(unittest.TestCase):
    def test_manifest_requires_exact_keys_and_identity(self):
        path=REPO/'configs/igm_manufactured_v1.cfg'
        cfg=ref.read_config(path)
        self.assertEqual(cfg.get('source_rate'),1e-15)
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            bad=Path(tmp)/'bad.cfg'
            bad.write_text(path.read_text()+'source_rate=2e-15\n')
            with self.assertRaises(ValueError): ref.read_config(bad)
            bad.write_text(path.read_text().replace('temperature_k=30\n',''))
            with self.assertRaises(ValueError): ref.read_config(bad)

if __name__ == '__main__': unittest.main()
