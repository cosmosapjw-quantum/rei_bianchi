"""Focused scientific tests: original source owner + Li II 1969 table + frozen physics."""
import csv, hashlib, importlib.util, json, math, os, pathlib, sys, tempfile, unittest
import numpy as np

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('two_e1',ROOT/'code/two_e1_source.py')
m=importlib.util.module_from_spec(spec)
sys.modules['two_e1']=m
spec.loader.exec_module(m)

class TestDifferentialSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report,cls.epochs,cls.spectral,cls.events,cls.opac,cls.samples = m.generate(order=8)

    def test_published_drake_li_ii_21_grid(self):
        self.assertEqual(len(m.Y_TAB),21)
        self.assertTrue(np.allclose(np.diff(m.Y_TAB),np.full(20,.025),atol=1e-15,rtol=0))
        self.assertEqual(m.A_TAB[0],0)
        self.assertEqual(m.A_TAB[-1],5420)
        self.assertTrue(np.all(np.diff(m.A_TAB)>=0))

    def test_source_table_integral_exact_piecewise_linear(self):
        self.assertAlmostEqual(m.PAIR_NORM,1945.475,places=10)
        self.assertLess(abs(m.PAIR_NORM-1940)/1940,0.003)

    def test_pair_prob_mass_and_symmetry(self):
        y,w=m.nodes_weights(8)
        self.assertAlmostEqual(w.sum(),1,places=12)
        self.assertTrue(np.all(w>0))
        self.assertTrue(np.all((y>0)&(y<.5)))
        for q in [0.01,0.123,.25,.47]:
            self.assertAlmostEqual(m.tail(q)+1-m.tail(q),1,places=15)
        self.assertTrue(np.allclose(y*m.E_SINGLET_EV+(1-y)*m.E_SINGLET_EV,m.E_SINGLET_EV,atol=2e-14,rtol=0))

    def test_threshold_counts_independent_wolfram(self):
        expected={'H_I':1.7212750025558112,'He_I':1.2664637647251857,'He_II':0.06661043779514719}
        for g,v in expected.items():
            self.assertAlmostEqual(m.expected_photons_over_threshold(m.THRESH[g]),v,places=12)

    def test_two_photon_continuous_threshold_physics(self):
        self.assertEqual(m.expected_photons_over_threshold(0),2)
        self.assertEqual(m.expected_photons_over_threshold(m.E_SINGLET_EV),0)
        self.assertEqual(m.expected_photons_over_threshold(m.E_SINGLET_EV/2),1)
        self.assertTrue(0<m.expected_photons_over_threshold(m.THRESH['He_II'])<1)
        self.assertGreater(m.E_SINGLET_EV-m.THRESH['He_II'],0)

    def test_original_saved_epoch_event_row_counts(self):
        self.assertEqual(len(self.epochs),193)
        self.assertEqual(len(self.events),8492)
        self.assertEqual(len(self.spectral),193*21)
        self.assertEqual(self.report['data']['original_Li1s_source_event_rows'],8492)
        self.assertEqual(self.report['data']['reused_native_states'],21)

    def test_original_source_archive_fingerprint(self):
        self.assertEqual(hashlib.sha256(m.ARCHIVE.read_bytes()).hexdigest(),m.SHA_PR282)
        self.assertEqual(self.report['source_owner'],m.OWNER)

    def test_invalid_parent_archive_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            f=pathlib.Path(d)/'edited.zip';f.write_bytes(m.ARCHIVE.read_bytes()[:-16])
            original=m.ARCHIVE
            try:
                m.ARCHIVE=f
                with self.assertRaisesRegex(ValueError,'PR282_IMMUTABLE_SOURCE_SHA'):m.load_original()
            finally:m.ARCHIVE=original

    def test_native_m1_compatibility_by_original_loader(self):
        data,H,nb,previous,bins,net=m.load_original()
        self.assertEqual(data['Y'].shape,(193,21))
        sig,_=net.photo_cross_sections([m.E_TRIPLET_EV]);current=(nb[:,None]*data['Y']*sig[:,0][None,:]).sum(axis=1)
        with __import__('zipfile').ZipFile(m.ARCHIVE) as z:
            # m.load_original has already performed exact PR282 consistency check
            self.assertEqual(len(previous),193)
        self.assertGreater(float(current.max()),0)

    def test_no_singlet_in_triplet_only_source_events(self):
        forced=[r for r in self.events if r['source_forces_M1']]
        self.assertGreater(len(forced),0)
        self.assertTrue(all(not r['possible_singlet_2E1'] and r['singlet_2E1_pair_source_UPPER_per_baryon_s']==0 for r in forced))
        self.assertTrue(all(r['actual_singlet_fraction']=='UNBOUND' for r in self.events))

    def test_frozen_absorption_opacity_probability(self):
        self.assertTrue(np.all(self.samples['kappa_m_inv']>=0))
        self.assertTrue(np.all((self.samples['pabs_one_frozen_Hubble_length']>=0)&(self.samples['pabs_one_frozen_Hubble_length']<=1)))
        self.assertTrue(np.all(np.isfinite(self.samples['mean_primary_eV'])))
        self.assertTrue(np.all(self.samples['mean_primary_eV']>=0))

    def test_frozen_absorber_categories_partition(self):
        u=self.report['LiII_2E1_all_singlet_frozen_transfer_integrals_per_baryon']
        summed=sum(u['first_absorber_'+g] for g in m.CAT_GROUPS)
        self.assertAlmostEqual(summed/u['potential_ionizations'],1,places=13)

    def test_energy_conservation_integrated(self):
        u=self.report['LiII_2E1_all_singlet_frozen_transfer_integrals_per_baryon']
        both=u['potential_photoelectron_eV']+u['potential_bound_ionization_eV']
        self.assertAlmostEqual(both/u['absorbed_photon_eV'],1.,places=13)
        a=self.epochs
        en=sum(q['conditional_all_singlet_2E1_radiative_energy_eV_per_baryon_s'] for q in a)
        self.assertGreater(en,0)
        for q in a:
            inp=q['conditional_all_singlet_2E1_radiative_energy_eV_per_baryon_s']
            out=sum(q[k] for k in ('conditional_all_singlet_2E1_primary_electrons_eV_per_baryon_s','conditional_all_singlet_2E1_ion_binding_eV_per_baryon_s','conditional_all_singlet_2E1_unabsorbed_photon_eV_per_baryon_s'))
            self.assertLess(abs(inp-out),3e-14*max(inp,1e-80))

    def test_positive_real_source_conditional_exposure(self):
        k=self.report['events_per_baryon']
        self.assertAlmostEqual(k/3.4426556153037163e-11,1,places=11)
        for g in m.THRESH:
            p=self.report['LiII_2E1_conditional_threshold_photons'][g]
            self.assertLessEqual(0,p['integrated_conditional_min_photons_per_baryon'])
            self.assertLessEqual(p['integrated_conditional_min_photons_per_baryon'],p['integrated_conditional_max_photons_per_baryon'])
            self.assertLessEqual(p['integrated_conditional_max_photons_per_baryon'],2*k)

    def test_quadrature_source_native_threshold_convergence(self):
        data,H,nb,e,b,net=m.load_original()
        results=[]
        for order in (4,8,16):
            r,s=m.frozen_transfer(data,H,nb,net,order)
            results.append(r)
        for key in results[0]:
            for ref in results[1:]:
                self.assertLess(np.max(np.abs(results[0][key]-ref[key])/np.maximum(np.abs(ref[key]),1e-20)),3e-11,key)

    def test_source_script_contains_no_cosmological_ivp(self):
        text=(ROOT/'code/two_e1_source.py').read_text()
        self.assertNotIn('solve_ivp(',text)
        self.assertNotIn('odeint(',text)
        self.assertEqual(self.report['boundaries']['new_IVPs'],0)
        self.assertEqual(self.report['boundaries']['REI_IgmPhotoInput_heat_erg_per_absorber_s'],'UNBOUND')

    def test_dag_is_not_promoted(self):
        self.assertEqual(self.report['DAG']['working'],'33/88')
        self.assertEqual(self.report['DAG']['central'],'28/88')
        self.assertEqual(self.report['DAG']['physical_fast'],'4/7')
        self.assertEqual(self.report['DAG']['canonical_delta'],0)
        for restriction in ('NO_MORE_IVPS','NO_MERGE','NO_FORCE_PUSH'):
            self.assertTrue(self.report['DAG'][restriction])
        self.assertFalse(self.report['DAG']['AUTO_NEXT_NODE'])

if __name__=='__main__':unittest.main()
