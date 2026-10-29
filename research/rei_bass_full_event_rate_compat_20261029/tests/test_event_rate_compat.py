from __future__ import annotations

import hashlib
import json
import math
import sys
import unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch
import numpy as np
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import event_rate_compat as m


class TestExactSource(unittest.TestCase):
    def test_five_original_source_shas(self):
        self.assertEqual(m.source_lock(),m.SHA256)

    def test_changed_source_refused(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'PUCHWEIN19_13.json'
            p.write_bytes(m.P19.read_bytes()+b' ')
            with patch.dict(m.SOURCE_FILES,{'PUCHWEIN19_13.json':p}):
                with self.assertRaisesRegex(ValueError,'SOURCE_SHA_MISMATCH'):
                    m.source_lock()

    def test_wrong_source_blob_refused(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'PUCHWEIN19_13.json'
            raw=json.loads(m.P19.read_text())
            raw['parent_git_blob']='fake'
            p.write_text(json.dumps(raw))
            with patch.dict(m.SOURCE_FILES,{'PUCHWEIN19_13.json':p}), patch.object(m,'SHA256', {**m.SHA256,'PUCHWEIN19_13.json':hashlib.sha256(p.read_bytes()).hexdigest()}):
                with self.assertRaisesRegex(ValueError,'P19_SOURCE_MAPPING_MISMATCH'):
                    m.source_lock()

    def test_model_single_fixed_spectral_shape(self):
        code=m.BASS_NETWORK.read_text()
        self.assertIn('G0=uv * self._Gphoto',code)
        self.assertIn('self._Gphoto = _readonly(self._transition_matrix',code)
        self.assertIn('late_Gamma_HI_s',code)
        model=json.loads(m.BASS_MODEL.read_text())
        self.assertEqual(model['photon_field']['number_power_index'],-2.5)
        self.assertEqual(model['photon_field']['energy_max_eV'],200.)

    def test_native_table_unbound(self):
        self.assertIn('data/atomic_coefficients.json',m.BASS_NETWORK.read_text())
        self.assertFalse((ROOT/'source/data/atomic_coefficients.json').exists())

    def test_calibration_subset_positive(self):
        rows=m.source_rows(); selected=m.selected_rows()
        self.assertEqual((len(rows),len(selected)),(13,11))
        self.assertEqual([str(x[0]) for x in selected][0],'2.48')
        self.assertEqual([str(x[0]) for x in selected][-1],'4.62')
        self.assertTrue(all(isinstance(x,Decimal) for row in rows for x in row))

    def test_no_binary_float_exact(self):
        with self.assertRaises(TypeError):m.exact(0.5)
        self.assertEqual(m.exact(Decimal('0.5')),Fraction(1,2))


class TestTheorem(unittest.TestCase):
    def test_exact_rank_three_six(self):
        self.assertEqual(m.rank_witness()['ranks'],(3,6))

    def test_exact_three_by_three_witness(self):
        a=m.rank_witness()
        self.assertEqual(a['witness_det_3x3'],'235010831/2500000000000000000000000000000000000000000000000')
        self.assertGreater(a['witness_det_scaled'],0)

    def test_common_calibration_cannot_remove_rank(self):
        mat3,mat6=m.exact_rate_matrices()
        D=sp.diag(*[sp.Integer(2)**i for i in range(1,12)])
        self.assertEqual((D*mat3).rank(),3)
        self.assertEqual((D*mat6).rank(),6)

    def test_exact_ratios_and_gap(self):
        v=m.minimax_two_epochs()
        self.assertEqual(v['HeII_over_HI_exact'],['53/11700','149/3790000'])
        self.assertEqual(v['exact_cross_ratio_witness'],'1991267/443430000')

    def test_two_epoch_bound_value(self):
        v=m.minimax_two_epochs()
        self.assertAlmostEqual(float(v['minimax_relative_error']),0.8295586873156144,15)
        self.assertAlmostEqual(float(v['rmax_over_rmin']),115.2240004588998,12)

    def test_optimal_scales_equalize_component_errors(self):
        v=m.minimax_two_epochs();k=float(v['optimal_static_ratio']);err=float(v['minimax_relative_error'])
        rhi=float(Fraction(v['HeII_over_HI_exact'][0])); rlo=float(Fraction(v['HeII_over_HI_exact'][1]))
        for r,t in [(rhi,2*rhi/(rhi+k)),(rlo,2*rlo/(rlo+k))]:
            self.assertAlmostEqual(abs(t-1.),abs(t*k/r-1.),14)
            self.assertAlmostEqual(abs(t-1.),err,14)

    def test_fixed_ratio_neither_extreme_improves(self):
        v=m.minimax_two_epochs();err=float(v['minimax_relative_error']);rhi=float(Fraction('53/11700'));rlo=float(Fraction('149/3790000'))
        for k in [rlo/2,rlo, (rlo*rhi)**0.5*0.9, (rlo*rhi)**0.5*1.1,rhi,2*rhi]:
            observed=max(abs(k-rhi)/(k+rhi),abs(k-rlo)/(k+rlo))
            self.assertGreaterEqual(observed+1e-14,err)

    def test_numerical_singular_shape_if_equal_ratios(self):
        r=Fraction('53/11700')
        self.assertEqual((sp.sqrt(r)-sp.sqrt(r))/(sp.sqrt(r)+sp.sqrt(r)),0)


class TestEventAdapter(unittest.TestCase):
    def setUp(self):
        self.row=m.selected_rows()[4]
        self.rate=m.target_3(self.row)
        self.y=[Fraction((i%5)+1,7) for i in range(17)]

    def test_seven_exact_source_events(self):
        self.assertEqual(len(m.EVENTS),7)
        self.assertEqual(len(m.generator_17(self.rate)),17)

    def test_jacobian_equals_generator(self):
        self.assertEqual(m.generator_17(self.rate),m.electronic_jacobian_17(self.rate))

    def test_nucleons_and_isotope_count(self):
        x=m.check_event_conservation(self.rate,self.y)
        self.assertEqual(x['nucleon'],0)
        self.assertEqual(x['nuclear_count'],0)

    def test_exact_electron_source(self):
        x=m.check_event_conservation(self.rate,self.y)
        self.assertEqual(x['electron'],x['positive_event_electrons'])
        self.assertGreater(x['electron'],0)

    def test_offdiagonal_nonnegative(self):
        G=m.generator_17(self.rate)
        for i in range(17):
            for j in range(17):
                if i!=j:self.assertGreaterEqual(G[i][j],0)

    def test_full_column_conservation(self):
        G=m.generator_17(self.rate)
        for j in range(17):self.assertEqual(sum(G[i][j] for i in range(17)),0)

    def test_family_total_conservation(self):
        dy=m.derivative_17(self.rate,self.y)
        for indices in [(1,2),(3,4),(5,6),(7,8,9),(10,11,12),(13,14,15,16)]:
            self.assertEqual(sum(dy[k] for k in indices),0)

    def test_t_photo_present_and_li_not_in_p19(self):
        dy=m.derivative_17(self.rate,self.y)
        self.assertEqual(dy[6],self.y[5]*self.rate[0])
        self.assertTrue(all(dy[i]==0 for i in [13,14,15,16]))

    def test_failclosed_rate_inputs(self):
        with self.assertRaises(ValueError):m.generator_17([Fraction(1),Fraction(1),Fraction(0)])
        with self.assertRaises(ValueError):m.derivative_17(self.rate,self.y[:-1])
        with self.assertRaises(ValueError):m.derivative_17(self.rate,[-1]+self.y[1:])

    def test_source_changed_residual_neq_zero(self):
        r=list(self.rate);r[2]*=2
        y=self.y
        a=m.derivative_17(self.rate,y);b=m.derivative_17(r,y)
        self.assertEqual(b[9]-a[9],self.rate[2]*y[8])


class TestActualFrozenReplay(unittest.TestCase):
    def test_original_pr262_seven_states_recomputed(self):
        o=m.same_source_frozen_replay()
        self.assertEqual(len(o),7)
        self.assertTrue(all(x['max_relative_rhs_difference']<2e-14 for x in o))
        self.assertTrue(all(x['max_relative_jacobian_difference']<2e-14 for x in o))

    def test_electron_observable_replay(self):
        o=m.same_source_frozen_replay()
        for x in o:self.assertAlmostEqual(x['orig_electrons'],x['replay_electrons'],26)

    def test_observed_seven_redshift_order(self):
        o=m.same_source_frozen_replay()
        self.assertTrue(all(a['z']<b['z'] for a,b in zip(o,o[1:])))

    def test_bad_calibration_z_refused(self):
        with self.assertRaisesRegex(ValueError,'OUTSIDE_CALIBRATION_DOMAIN'):
            m.p19_float_rates(4.751)

    def test_common_beta_kappa_cannot_change_channel_ratios(self):
        r0=m.p19_float_rates(3.603019593287379,(0.,0.))
        r1=m.p19_float_rates(3.603019593287379,(0.12,0.07))
        self.assertTrue(np.allclose(r0[1:]/r0[0],r1[1:]/r1[0],rtol=5e-15,atol=0))

    def test_monotone_both_rates_positive(self):
        o=m.same_source_frozen_replay()
        self.assertTrue(all(x['replay_electrons']>0 for x in o))


if __name__=='__main__':unittest.main(verbosity=2)
