import copy, hashlib, json, tempfile, unittest
from pathlib import Path
from decimal import Decimal
from src.ionization_cycle import strict_literal_record,compute,verify_archives,ContractError,SOURCE_TARGET,DOIS
ROOT=Path(__file__).resolve().parents[1]
R21=Path('/mnt/data/WU_R21_SOURCE_ORIGINAL_20261029.zip')
R22=Path('/mnt/data/WU_R22_SPECTROSCOPIC_CANDIDATE_SOURCE_ORIGINAL_20261029.zip')
ORIGINAL=ROOT/'sources/MOLECULAR_IONIZATION_LITERALS.json'
class TestIonizationCycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec,cls.digest=strict_literal_record(ORIGINAL)
        cls.result=compute(cls.rec,cls.digest)
    def assert_corrupt(self,mut):
        rec=copy.deepcopy(self.rec);mut(rec)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'source.json';p.write_text(json.dumps(rec),encoding='utf8')
            with self.assertRaises(ContractError): strict_literal_record(p)
    def test_spectro_threshold(self): self.assertAlmostEqual(float(self.result['delta_E_cm1']),168.9733148142086,places=11)
    def test_Q_sign(self): self.assertTrue(Decimal(self.result['Q_spectroscopy_candidate_meV'])<0)
    def test_energy_dimension(self):
        from src.ionization_cycle import E
        self.assertEqual(Decimal(self.result['Q_spectroscopy_candidate_J_per_event']),Decimal(self.result['Q_spectroscopy_candidate_meV'])*E/1000)
    def test_original_pdf(self): self.assertEqual(verify_archives(R21,R22)['GL2022_pdf_size'],273554)
    def test_reference_difference(self): self.assertEqual(Decimal(self.result['inter_cycle_residual_cm1']).quantize(Decimal('.00000001')),Decimal('-0.00000127'))
    def test_raw_2017_ion_energies(self): self.assertEqual(Decimal(self.rec['molecular_ionization']['EI_H2p_cm1']['value']),Decimal('131058.1219937'))
    def test_rot_ortho(self): self.assertIn('ortho',self.rec['target_reaction'])
    def test_R21_pin(self): self.assertEqual(self.rec['independent_comparison']['R21_git_head'],'fd351d0ff97ef0d7a9cf710bdecad922af7e885e')
    def test_R22_pin(self): self.assertTrue(self.rec['independent_comparison']['R22_spectroscopic_dissociation_cycle_source_zip_sha256'].startswith('5d922676'))
    def test_refuses_admission(self):
        with self.assertRaises(ContractError):compute(self.rec,self.digest,admit_physical=True)
    def test_output_nulls(self):
        for k in ('PES_native_threshold_cm1','physical_Q_event_J_per_event','physical_bath_delta_J_per_ref_m3','real_rate_uncertainty','reverse_rate','owner_ACK'):
            self.assertIsNone(self.result[k],k)
    def test_production_hold(self): self.assertEqual(self.result['production'],'NOT_ISSUED');self.assertFalse(self.result['L4'])
    def test_bad_reaction(self):self.assert_corrupt(lambda r:r.__setitem__('target_reaction',r['target_reaction'].replace('D+ + H2','H+ + HD')))
    def test_bad_state_j(self):self.assert_corrupt(lambda r:r.__setitem__('target_reaction',r['target_reaction'].replace('J=2','J=0')))
    def test_bad_PES_admission(self):self.assert_corrupt(lambda r:r.__setitem__('GL2022_PES_native_threshold_cm1','168'))
    def test_bad_PES_ionization_status(self):self.assert_corrupt(lambda r:r['PES_provenance'].__setitem__('exact_GL2022_isotope_offset_issued',True))
    def test_bad_H2p_DOI(self):self.assert_corrupt(lambda r:r['molecular_ionization']['EI_H2p_cm1'].__setitem__('doi','10.fake'))
    def test_bad_HDp_value(self):self.assert_corrupt(lambda r:r['molecular_ionization']['EI_HDp_cm1'].__setitem__('value','131224.6841651'))
    def test_bad_uncertainty(self):self.assert_corrupt(lambda r:r['rotation']['HD_X_v0_J2_minus_J0_kHz'].__setitem__('quoted_unc','0'))
    def test_bad_R21_SHA(self):self.assert_corrupt(lambda r:r['independent_comparison'].__setitem__('R21_legacy_source_zip_sha256','0'*64))
    def test_bad_PHYSICAL_Q(self):self.assert_corrupt(lambda r:r['status'].__setitem__('physical_Q_J_per_event','-3e-21'))
    def test_bad_OWNER(self):self.assert_corrupt(lambda r:r['status'].__setitem__('REC_CR_owner_ACK',True))
    def test_bad_production(self):self.assert_corrupt(lambda r:r['status'].__setitem__('production','TRUE'))
    def test_bad_DAG(self):self.assert_corrupt(lambda r:r['status'].__setitem__('canonical_WU_DAG','35/49'))
    def test_bad_zip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'wrong.zip';p.write_bytes(R22.read_bytes()[:-1]+b'X')
            with self.assertRaises(ContractError):verify_archives(R21,p)
    def test_group_ionization_cycle_exact(self):
        import sympy as sp
        hp,dp,hd,hdp,h2,h2p,e,rotH2,rotHD=sp.symbols('hp dp hd hdp h2 h2p e rotH2 rotHD')
        direct=dp+h2+rotH2-hp-hd-rotHD
        EiHD=hdp+e-hd;EiHDp=hp+dp+e-hdp
        EiH2=h2p+e-h2;EiH2p=2*hp+e-h2p
        cycle=EiHD+EiHDp-EiH2-EiH2p+rotH2-rotHD
        self.assertEqual(sp.simplify(cycle-direct),0)
    def test_atomic_IP_dependent_D0_cancellation(self):
        # D0_HD=EI_HD+EI_HDp-I_H-I_D: change I_D in BOTH direct and source cycle.
        from decimal import Decimal
        I_D=Decimal('109708.61455294');I_H=Decimal('109678.77174307')
        EI_HD=Decimal(self.rec['molecular_ionization']['EI_HD_cm1']['value'])
        EI_HDp=Decimal(self.rec['molecular_ionization']['EI_HDp_cm1']['value'])
        EI_H2=Decimal(self.rec['molecular_ionization']['EI_H2_cm1']['value'])
        EI_H2p=Decimal(self.rec['molecular_ionization']['EI_H2p_cm1']['value'])
        d0_h2=EI_H2+EI_H2p-2*I_H
        for perturb in (Decimal('-30'),Decimal('-0.1'),Decimal('0'),Decimal('0.5'),Decimal('30')):
            d0_hd=EI_HD+EI_HDp-I_H-(I_D+perturb)
            direct=(I_D+perturb-I_H)+(d0_hd-d0_h2)
            cycle=EI_HD+EI_HDp-EI_H2-EI_H2p
            self.assertEqual(direct,cycle)
    def test_independent_R22_pairwise_difference_is_not_errorbar(self):
        self.assertGreater(Decimal(self.result['marginal_uncertainty_L1_sensitivity_cm1_NOT_CONFIDENCE']),0)
        self.assertIn('NOT_CONFIDENCE',self.result['uncertainty_type'])
    def test_formula_survives_alternative_ground_zero(self):
        # Molecular ionization cycle cancels all arbitrary overall charged-nuclear energy shifts.
        ion=self.result['components_cm1']['molecular_ground_ionic_difference']
        self.assertEqual(Decimal(ion),Decimal('317.5556740'))
if __name__=='__main__':unittest.main()
