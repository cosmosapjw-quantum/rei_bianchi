from __future__ import annotations
import copy,json,unittest
from pathlib import Path
from decimal import Decimal,localcontext
from src.state_energy import evaluate_candidate,SpectroscopyContractError,C_CM_PER_S,H_J_S,EV_J
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'SPECTROSCOPY_SOURCE.json').read_text(encoding='utf8'))
class SpectroscopyTest(unittest.TestCase):
    def setUp(self):self.out=evaluate_candidate(D)
    def test_sign_endothermic(self):self.assertLess(Decimal(self.out['candidate_Q_release_meV_per_event']),0)
    def test_total_reference(self):self.assertAlmostEqual(float(self.out['candidate_Q_release_meV_per_event']),-20.95002115130039,places=10)
    def test_exact_dimensions(self):
        o=self.out
        with localcontext() as ctx:
            ctx.prec=60
            self.assertEqual(Decimal(o['candidate_Q_release_J_per_event']),Decimal(o['candidate_Q_release_cm1'])*H_J_S*C_CM_PER_S)
            self.assertEqual(Decimal(o['candidate_Q_release_meV_per_event']),Decimal(o['candidate_Q_release_J_per_event'])/EV_J*1000)
    def test_components_reconstruct_exact(self):
        p=self.out['components_cm1'];
        with localcontext() as ctx:
            ctx.prec=60
            self.assertEqual(sum(Decimal(z) for z in p.values()),Decimal(self.out['delta_E_products_minus_reactants_cm1']))
    def test_conservation_sign(self):
        with localcontext() as ctx:
            ctx.prec=60
            self.assertEqual(Decimal(self.out['candidate_Q_release_cm1']),-Decimal(self.out['delta_E_products_minus_reactants_cm1']))
    def test_HD_rotational_delta(self):self.assertAlmostEqual(float(self.out['HD_02_rotation_cm1']),267.0691991857914,places=10)
    def test_ip_offset_not_zero(self):self.assertGreater(Decimal(self.out['components_cm1']['isotopic_atomic_ionization_cm1']),Decimal(29))
    def test_ground_value_not_reused(self):self.assertGreater(abs(Decimal(self.out['candidate_Q_release_meV_per_event'])+Decimal('39.5')),Decimal(10))
    def test_uncertainty_aggregation_explicit_noninterval(self):
        self.assertGreater(Decimal(self.out['sum_reported_uncertainty_magnitudes_meV']),Decimal(0))
        self.assertIn('not_confidence_interval',self.out['uncertainty_semantics'])
    def test_physical_output_null(self):
        for f in ('physical_Q_event_J_per_event','physical_bath_delta_J_per_ref_m3','GL2022_PES_native_Q_J_per_event'):
            self.assertIsNone(self.out[f])
        self.assertEqual(self.out['production'],'NOT_ISSUED')
    def test_reject_forged_admission(self):
        d=copy.deepcopy(D);d['production_admission']=True
        with self.assertRaises(SpectroscopyContractError):evaluate_candidate(d)
    def test_reject_PES_claim(self):
        d=copy.deepcopy(D);d['source_native_GL2022_energy_zero_authenticated']=True
        with self.assertRaises(SpectroscopyContractError):evaluate_candidate(d)
    def test_reject_wrong_channel(self):
        d=copy.deepcopy(D);d['reaction']='H + HD(v0,j2) -> D + H2(v0,j1)'
        with self.assertRaises(SpectroscopyContractError):evaluate_candidate(d)
    def test_reject_source_SHA(self):
        d=copy.deepcopy(D);d['source_locks']['GL2022_supp_pdf_sha256']='0'*64
        with self.assertRaises(SpectroscopyContractError):evaluate_candidate(d)
    def test_reject_nan(self):
        d=copy.deepcopy(D);d['quantities']['rotation_H2_01_cm1']['value']='NaN'
        with self.assertRaises(SpectroscopyContractError):evaluate_candidate(d)
    def test_reject_numeric_no_origin(self):
        d=copy.deepcopy(D);d['quantities']['rotation_H2_01_cm1']['url']=''
        with self.assertRaises(SpectroscopyContractError):evaluate_candidate(d)
    def test_reject_literal_source_drift(self):
        d=copy.deepcopy(D);d['quantities']['dissociation_HD_00_cm1']['value']='36405.78366'
        with self.assertRaises(SpectroscopyContractError):evaluate_candidate(d)
    def test_reject_source_year_drift(self):
        d=copy.deepcopy(D);d['quantities']['dissociation_H2_00_cm1']['year']=2018
        with self.assertRaises(SpectroscopyContractError):evaluate_candidate(d)
    def test_reject_uncertainty_literal_drift(self):
        d=copy.deepcopy(D);d['quantities']['rotation_HD_02_kHz']['quoted_abs_uncertainty']='260'
        with self.assertRaises(SpectroscopyContractError):evaluate_candidate(d)
    def test_reject_forged_state_label(self):
        d=copy.deepcopy(D);d['state_labels']['exit']='H2(v0,j0), D+'
        with self.assertRaises(SpectroscopyContractError):evaluate_candidate(d)
    def test_reject_prior_HEAD_drift(self):
        d=copy.deepcopy(D);d['source_locks']['R21_HEAD']='0'*40
        with self.assertRaises(SpectroscopyContractError):evaluate_candidate(d)
    def test_source_immutability(self):
        source_before=json.dumps(D,sort_keys=True)
        evaluate_candidate(D)
        self.assertEqual(json.dumps(D,sort_keys=True),source_before)
if __name__=='__main__':unittest.main()
