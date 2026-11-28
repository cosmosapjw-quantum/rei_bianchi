from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from research.wu_hd_source_bound_r18_20261029.src.native_rates import (
    PDF_SHA256, PDF_SIZE, SourceContractError, load_native_grid,
)
from research.wu_hd_source_grid_r20_20261029.src.grid_exposure import Segment
from research.wu_hd_nominal_exchange_r19_20261029.src.nominal_exchange import ModelContractError
from research.wu_hd_thermal_mechanical_ledger_r21_20261029.src.thermal_ledger import (
    K_B_J_PER_K, NU, ConditionalCaloricLedger, build_ledger,
    source_chemical_energy_release_from_qualified_levels,
)

SOURCE = Path(__file__).resolve().parents[3] / 'ORIGINAL_SOURCES' / 'GL2022_CSIC_supplement.pdf'
UNIT='research.wu_hd_thermal_mechanical_ledger_r21_20261029.src.thermal_ledger'

class LedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid=load_native_grid(SOURCE)

    def test_01_source_byte_identity(self):
        self.assertEqual(SOURCE.stat().st_size, PDF_SIZE)
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), PDF_SHA256)

    def test_02_exact_source_105_255_extent(self):
        flow,led=build_ledger(self.grid,(1e6,1e6,0,0),[Segment(105,5e9),Segment(255,5e9)])
        self.assertAlmostEqual(flow.extent_reference_m_minus3,660441.4261460102,places=6)
        self.assertAlmostEqual(led.total_particles_per_ref_m3,2e6)
        self.assertEqual(led.source_pdf_sha256,PDF_SHA256)
        self.assertEqual(led.reaction_temperature_nodes_K,(105,255))
        self.assertTrue(led.reaction_extent_events_per_ref_m3>0)

    def test_03_temperature_jump_heat_and_isothermal_null(self):
        _, led=build_ledger(self.grid,(1e6,1e6,0,0),[Segment(105,5e9),Segment(255,5e9)])
        expected=1.5*2e6*K_B_J_PER_K*150
        self.assertAlmostEqual(led.thermal_internal_change_J_per_ref_m3,expected,delta=expected*1e-14)
        self.assertEqual(led.pressure_work_by_material_J_per_ref_m3,0)
        self.assertEqual(led.bath_known_intercept_J_per_ref_m3,-expected)

    def test_04_expansion_isothermal_pressure_work_exact(self):
        dt=1e10;th=2e-12;T=105;N=3e6
        _,l=build_ledger(self.grid,(1e6,1e6,1e6,0),[Segment(T,dt,th)])
        self.assertAlmostEqual(l.pressure_work_by_material_J_per_ref_m3,N*K_B_J_PER_K*T*th*dt,delta=1e-27)
        self.assertAlmostEqual(l.bath_known_intercept_J_per_ref_m3,-l.pressure_work_by_material_J_per_ref_m3,delta=1e-27)
        self.assertAlmostEqual(l.volume_ratio_final, math.exp(th*dt))

    def test_05_compression_reverses_pressure_work(self):
        _,l=build_ledger(self.grid,(1e6,1e6,0,0),[Segment(105,1e10,-1e-11)])
        self.assertLess(l.pressure_work_by_material_J_per_ref_m3,0)
        self.assertGreater(l.bath_known_intercept_J_per_ref_m3,0)
        self.assertLess(l.volume_ratio_final,1)

    def test_06_missing_reactant_does_not_hide_work(self):
        _,l=build_ledger(self.grid,(0,1e6,0,1e6),[Segment(105,1e9,1e-11)])
        self.assertEqual(l.reaction_extent_events_per_ref_m3,0)
        self.assertLess(l.bath_known_intercept_J_per_ref_m3,0)

    def test_07_reaction_preserves_four_count_and_covectors(self):
        start=(100.,200.,30.,40.)
        flow,l=build_ledger(self.grid,start,[Segment(105,1e12,1e-13),Segment(255,1e12,-1e-13)])
        end=[v*l.volume_ratio_final for v in flow.final_state_m_minus3]
        for cov in ((1,1,0,2),(0,1,1,0),(1,0,1,0),(1,1,1,1)):
            self.assertAlmostEqual(math.fsum(a*b for a,b in zip(cov,start)),math.fsum(a*b for a,b in zip(cov,end)),delta=2e-10)

    def test_08_first_law_affine_synthetic_Q(self):
        _,l=build_ledger(self.grid,(3e6,2e6,1e5,7e5),[Segment(105,1e9,3e-12),Segment(255,2e9,-4e-12)])
        for q in (0.,1e-23,-8e-23):
            dchem=-q*l.reaction_extent_events_per_ref_m3
            dmat=dchem+l.thermal_internal_change_J_per_ref_m3
            dbath=q*l.reaction_extent_events_per_ref_m3+l.bath_known_intercept_J_per_ref_m3
            self.assertAlmostEqual(dmat+dbath+l.pressure_work_by_material_J_per_ref_m3,0,delta=1e-24)

    def test_09_energy_gauge_shift(self):
        orig=[1e-19,2e-19,3e-19,4e-19]
        covs=[(1,1,0,2),(0,1,1,0),(1,0,1,0),(1,1,1,1)]
        q=source_chemical_energy_release_from_qualified_levels(orig)
        for cov in covs:
            shifted=[e+6.25e-21*x for e,x in zip(orig,cov)]
            self.assertAlmostEqual(source_chemical_energy_release_from_qualified_levels(shifted),q,delta=1e-34)

    def test_10_no_physical_Q_issuance(self):
        _,l=build_ledger(self.grid,(1e6,1e6,0,0),[Segment(105,1e9)])
        doc=l.as_json()
        aff=doc['affine_bath_delta_per_reference_m3']
        self.assertIsNone(aff['physical_Q_event_J_per_event'])
        self.assertIsNone(aff['physical_bath_delta_J_per_ref_m3'])
        self.assertFalse(doc['admission']['physical_state_energy_Q'])
        self.assertEqual(doc['admission']['production'],'NOT_ISSUED')
        with self.assertRaises(SourceContractError):
            source_chemical_energy_release_from_qualified_levels((1.,2.,3.,4.),source_admitted=True)
        with self.assertRaises(SourceContractError):
            ConditionalCaloricLedger(0.,0.,105,105,1.,0.,0.,0.,PDF_SHA256,(105,))

    def test_11_unsupported_temperature_rejected(self):
        with self.assertRaises(SourceContractError):
            build_ledger(self.grid,(1e6,1e6,0,0),[Segment(100,1e9)])

    def test_12_invalid_source_or_negative_state_rejected(self):
        with self.assertRaises((SourceContractError,ModelContractError)):
            build_ledger(object(),(1e6,1e6,0,0),[Segment(105,1e9)])
        with self.assertRaises(ModelContractError):
            build_ledger(self.grid,(1e6,-1e6,0,0),[Segment(105,1e9)])

    def test_13_negative_temperature_or_bad_segment_rejected(self):
        with self.assertRaises(ModelContractError):
            Segment(105,-1.)
        with self.assertRaises(ModelContractError):
            build_ledger(self.grid,(1e6,1e6,0,0),[])
        with self.assertRaises(ModelContractError):
            build_ledger(self.grid,(1e6,1e6,0,0),[{'temperature_K':105,'duration_s':1}])

    def test_14_source_label_and_state_forbidden(self):
        with self.assertRaises(SourceContractError):
            self.grid.lookup(105,product_j=2)
        with self.assertRaises(SourceContractError):
            self.grid.lookup(105,method='EQM')

    def test_15_theta_zero_continuous_limit(self):
        _,m=build_ledger(self.grid,(5e5,2e5,0,0),[Segment(105,1e10,0.)])
        _,p=build_ledger(self.grid,(5e5,2e5,0,0),[Segment(105,1e10,1e-30)])
        self.assertAlmostEqual(p.reaction_extent_events_per_ref_m3,m.reaction_extent_events_per_ref_m3,delta=1e-6)
        self.assertAlmostEqual(p.bath_known_intercept_J_per_ref_m3,m.bath_known_intercept_J_per_ref_m3,delta=2e-32)

    def test_16_cli_create_only_and_json_admission(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);sched=t/'schedule.json';out=t/'out.json'
            sched.write_text(json.dumps({'schema':'wu.r20.schedule.v1','segments':[{'temperature_K':105,'duration_s':1e9,'theta_s':0.0}]}))
            cmd=[sys.executable,'-m',UNIT,'--source-pdf',str(SOURCE),'--schedule-json',str(sched),'--initial-m3','1e6','1e6','0','0','--output',str(out)]
            r=subprocess.run(cmd,text=True,capture_output=True,timeout=25)
            self.assertEqual(r.returncode,0,r.stderr)
            d=json.loads(out.read_text())
            self.assertIsNone(d['ledger']['affine_bath_delta_per_reference_m3']['physical_bath_delta_J_per_ref_m3'])
            again=subprocess.run(cmd,text=True,capture_output=True,timeout=25)
            self.assertEqual(again.returncode,2)
            self.assertIn('FileExistsError',again.stderr)

    def test_17_invalid_energy_labels(self):
        for e in ((1.,2.,3.),(1.,2.,3.,float('nan')),(1.,2.,3.,True)):
            with self.assertRaises(ModelContractError):
                source_chemical_energy_release_from_qualified_levels(e)

    def test_18_comoving_count_under_varying_expansion(self):
        flow,l=build_ledger(self.grid,(8e6,5e6,7e5,2e5),[Segment(105,1e9,1e-10),Segment(255,1e9,-5e-11)])
        self.assertAlmostEqual(math.fsum(flow.final_state_m_minus3)*flow.volume_ratio,l.total_particles_per_ref_m3,delta=l.total_particles_per_ref_m3*4e-14)

if __name__=='__main__':unittest.main()
