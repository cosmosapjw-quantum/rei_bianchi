"""Frozen exact controls; hand oracles do not call another kernel implementation."""
import copy
import csv
from fractions import Fraction as F
import json
import math
from pathlib import Path
import sys
import unittest
from tdcs54 import (ContractError,exact,ratio_profile,feasible_scale_interval,
    minimax_profile,pair_contrast,source_angle_vectors,
    conditional_printing_ratio_interval,validate_source_rows,serialized)

UNIT=Path(__file__).resolve().parents[1]


def source():
    rows=list(csv.DictReader((UNIT/'source/jones2000_tableIV_cross_sections.csv').read_text().splitlines()))
    meta=json.loads((UNIT/'source/SOURCE_METADATA.json').read_text())
    return rows,meta


class Controls(unittest.TestCase):
    def test_01_positive_exact_inputs(self):
        for v in ['1.20',12,F(3,5)]:self.assertGreater(exact(v),0)
        self.assertEqual(exact('1.20'),F(6,5))
        for value in [True,False,1.0,float('nan'),float('inf'),'NaN','Inf','1/2','-1','0',0,F(0),-1,None,{},'1_0']:
            with self.assertRaises(ContractError):exact(value)
        self.assertEqual(exact(0,zero_allowed=True),0)

    def test_02_ratio_scale_direction(self):
        p=ratio_profile(['2','6'],['1','3'])
        self.assertEqual(p['ratios'],[F(2),F(2)])
        optimum=minimax_profile(p['ratios'])
        self.assertEqual(optimum['free_scale'],2)
        self.assertEqual(optimum['free_delta'],0)
        self.assertEqual(optimum['witness_u'],[1,1])
        for a,b in [([],[]),([1],[1,2]),([0],[1]),([1.0],[1])]:
            with self.assertRaises(ContractError):ratio_profile(a,b)

    def test_03_feasible_constructive_witness(self):
        r=feasible_scale_interval([1,F(11,10)],F(1,10))
        self.assertTrue(r['feasible']);self.assertEqual(r['lower'],1);self.assertEqual(r['upper'],F(10,9))
        self.assertEqual(r['witness_u'],[1,F(11,10)])
        for u in r['witness_u']:self.assertTrue(F(9,10)<=u<=F(11,10))

    def test_04_touching_and_empty(self):
        r=feasible_scale_interval([9,11],F(1,10),10,10)
        self.assertTrue(r['feasible']);self.assertEqual(r['lower'],10);self.assertEqual(r['upper'],10)
        self.assertEqual(r['witness_u'],[F(9,10),F(11,10)])
        for r in [feasible_scale_interval([1,2],F(1,10)),feasible_scale_interval([1],0,2,3)]:
            self.assertFalse(r['feasible']);self.assertIsNone(r['witness_scale']);self.assertIsNone(r['witness_u'])

    def test_05_single_equal_and_constrained_q(self):
        for values in [[F(3,2)],[F(3,2)]*3]:
            r=minimax_profile(values);self.assertEqual(r['free_scale'],F(3,2));self.assertEqual(r['free_delta'],0)
        r=minimax_profile([4,8],F(1,4),F(1,2))
        self.assertEqual(r['free_scale'],6);self.assertEqual(r['free_delta'],F(1,3))
        self.assertEqual(r['constrained_scale'],F(1,2));self.assertEqual(r['constrained_delta'],15)
        self.assertTrue(r['constrained_q_at_least_one'])
        r=minimax_profile([1,3],5,6)
        self.assertEqual(r['constrained_scale'],5);self.assertEqual(r['constrained_delta'],F(4,5))

    def test_06_delta_and_bounds_errors(self):
        self.assertTrue(feasible_scale_interval([1,1],0)['feasible'])
        self.assertFalse(feasible_scale_interval([1,2],0)['feasible'])
        for delta in [1,F(11,10),-1,True,.1]:
            with self.assertRaises(ContractError):feasible_scale_interval([1],delta)
        for low,high in [(0,1),(2,1),(None,1),(1,None),(1.,2)]:
            with self.assertRaises(ContractError):minimax_profile([1],low,high)

    def test_07_independent_anchor_oracles(self):
        data=['1.52','1.24']
        for model,expected_q,expected_delta,expected_scale in [
            (['1.83','.99'],F(1891,1254),F(637,3145),F(9435,9424)),
            (['2.58','1.51'],F(3999,2869),F(565,3434),F(1717,1178))]:
            pair=pair_contrast(*model,*data,F(1,10))
            self.assertEqual(pair['nominal_ratio'],F(38,31));self.assertEqual(pair['scale_free_Q'],expected_q)
            self.assertEqual(pair['two_point_minimum_delta'],expected_delta)
            opt=minimax_profile(ratio_profile(model,data)['ratios'],F(13,20),F(27,20))
            self.assertEqual(opt['free_scale'],expected_scale);self.assertEqual(opt['free_delta'],expected_delta)
        for model,L,U in [(['1.83','.99'],F(915,836),F(55,62)),(['2.58','1.51'],F(645,418),F(755,558))]:
            feasible=feasible_scale_interval(ratio_profile(model,data)['ratios'],F(1,10))
            self.assertEqual(feasible['free_lower'],L);self.assertEqual(feasible['free_upper'],U);self.assertFalse(feasible['feasible'])
        self.assertEqual(pair_contrast('1.83','.99',*data,F(1,10))['theory_ratio'],F(61,33))
        self.assertEqual(pair_contrast('2.58','1.51',*data,F(1,10))['theory_ratio'],F(258,151))
        r=minimax_profile(ratio_profile(['2.58','1.51'],data)['ratios'],F(13,20),F(27,20))
        self.assertEqual(r['constrained_scale'],F(27,20));self.assertEqual(r['constrained_delta'],F(44,171))

    def test_08_pair_cancellation_and_sharp_endpoints(self):
        a=pair_contrast(3,2,5,7,F(1,10));b=pair_contrast(21,14,15,21,F(1,10))
        self.assertEqual(a['scale_free_Q'],b['scale_free_Q'])
        self.assertEqual(a['Q_lower'],F(9,11));self.assertEqual(a['Q_upper'],F(11,9))
        for first,second,endpoint in [(F(9,10),F(11,10),'Q_lower'),(F(11,10),F(9,10),'Q_upper')]:
            r=pair_contrast(first,second,1,1,F(1,10));self.assertEqual(r['scale_free_Q'],r[endpoint])
        self.assertEqual(a['nominal_ratio_sensitivity_lower'],F(5,7)*F(9,11))
        self.assertEqual(a['nominal_ratio_sensitivity_upper'],F(5,7)*F(11,9))

    def test_09_geometry_signs_and_units(self):
        for fast,angle in [(4,146),(10,140)]:
            r=source_angle_vectors(fast,210)
            for direction in [r['fast_direction'],r['slow_direction']]:
                self.assertLessEqual(abs(math.fsum(x*x for x in direction)-1),2e-14)
            self.assertEqual(r['small_pair_angle_deg'],angle);self.assertEqual(r['slow_polar_angle_deg'],150)
            self.assertLessEqual(abs(r['dot']-math.cos(math.radians(angle))),2e-14)
            self.assertLessEqual(abs(r['slow_direction'][0]-.5),2e-14)
            self.assertLessEqual(abs(r['slow_direction'][2]+math.sqrt(3)/2),2e-14)
            self.assertFalse(r['finite_mass_frame_transform'])
        with self.assertRaises(ContractError):source_angle_vectors(4.,210)

    def test_10_printing_interval_exact_and_not_naive_gate(self):
        r=conditional_printing_ratio_interval('.91','1.09','.84')
        self.assertEqual(r['nominal_recomputed_ratio'],F(91,109))
        self.assertEqual(r['ratio_lower'],F(181,219));self.assertEqual(r['ratio_upper'],F(183,217))
        self.assertGreater(abs(r['residual']),F(1,200));self.assertTrue(r['compatible'])
        self.assertEqual(r['overlap_lower'],F(167,200));self.assertEqual(r['overlap_upper'],F(183,217))
        self.assertFalse(conditional_printing_ratio_interval(1,1,2)['compatible'])
        with self.assertRaises(ContractError):conditional_printing_ratio_interval('.001','1','1')

    def test_11_all_source_values_and_groups(self):
        rows,meta=source();r=validate_source_rows(rows,meta)
        expected=[['0.94','1.01','0.81'],['1.83','2.58','1.52'],['1.22','1.34','1.21'],['0.99','1.51','1.24'],['0.91','0.99','1.09'],['0.42','0.67','0.61'],['0.48','0.51','0.53'],['0.14','0.24','0.17']]
        self.assertEqual([[row[k] for k in ['CDW_EIS_TDCS_au','CCC99_TDCS_au','experiment_TDCS_au']] for row in rows],expected)
        self.assertEqual(r['source_values'],24);self.assertEqual(r['groups']['located_anchors_2'],[1,3])
        self.assertEqual(r['groups']['binary_peak_heights_4'],[0,2,4,6]);self.assertEqual(r['located_points'],2)
        self.assertFalse(r['physical_provider_admitted']);self.assertEqual(r['fast_energy'],'NOT_EVALUATED')
        located=list(csv.DictReader((UNIT/'source/jones2000_located_tdcs.csv').read_text().splitlines()))
        self.assertEqual(located,[{k:v for k,v in rows[i].items() if k!='source_lobe'} for i in [1,3]])

    def test_12_source_metadata_and_unknown_angles_rejected(self):
        rows,meta=source()
        for change in ['fake_angle','zero','float','missing','extra_factor']:
            altered=copy.deepcopy(rows)
            if change=='fake_angle':altered[0]['slow_angle_clockwise_deg']='90'
            elif change=='zero':altered[0]['CCC99_TDCS_au']='0'
            elif change=='float':altered[0]['CDW_EIS_TDCS_au']=.94
            elif change=='missing':del altered[0]['source_lobe']
            else:altered[0]['spin_weight']='.25'
            with self.assertRaises(ContractError):validate_source_rows(altered,meta)
        for key,value in [('unit','SI'),('representation','raw_amplitudes'),('nucleus','finite_mass'),('physical_provider_admitted',True)]:
            m={**meta,key:value}
            with self.assertRaises(ContractError):validate_source_rows(rows,m)

    def test_13_all16printed_controls(self):
        rows,_=source();controls=json.loads((UNIT/'source/PRINTED_RATIO_CONTROLS.json').read_text())
        cdw=['1.16','1.20','1.01','0.80','0.84','0.69','0.91','0.82'];ccc=['1.25','1.70','1.11','1.22','0.91','1.10','0.96','1.41']
        self.assertEqual(controls['CDW_EIS'],cdw);self.assertEqual(controls['CCC99'],ccc)
        count=0
        for name,column in [('CDW_EIS','CDW_EIS_TDCS_au'),('CCC99','CCC99_TDCS_au')]:
            for row,printed in zip(rows,controls[name]):
                self.assertTrue(conditional_printing_ratio_interval(row[column],row['experiment_TDCS_au'],printed)['compatible']);count+=1
        self.assertEqual(count,16)

    def test_14_allCDW_summary_discrepancy_and_serialization(self):
        rows,_=source();ratios=ratio_profile([r['CDW_EIS_TDCS_au'] for r in rows],[r['experiment_TDCS_au'] for r in rows])['ratios']
        r=minimax_profile(ratios)
        self.assertEqual(r['free_delta'],F(1593,5849));self.assertNotEqual(r['free_delta'],F(26,100))
        encoded=serialized({'delta':r['free_delta'],'huge':F(10)**400,'tiny':F(1,10)**400})
        self.assertEqual(encoded['delta']['numerator'],'1593');self.assertEqual(encoded['delta']['denominator'],'5849')
        self.assertNotIn('Infinity',json.dumps(encoded));self.assertNotIn('NaN',json.dumps(encoded))
        summaries=json.loads((UNIT/'source/PAPER_APPROXIMATE_SUMMARIES.json').read_text())
        self.assertEqual(summaries['all_reported_features_8']['CDW_EIS']['reported_percent'],'26%')


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','test_methods':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),
            'oracle':'independent frozen hand-Fraction constants and direct geometry norms',
            'geometry_absolute_tolerance':2e-14,'exact_algebra':'Fraction equality',
            'source_cross_section_values':24,'printed_ratio_controls':16,'located_points':2,
            'old_suite_runs':0,'physical_provider_admitted':False}
    (UNIT/'results/test_report.json').write_text(json.dumps(report,indent=2)+'\n')
    sys.exit(0 if result.wasSuccessful() else 1)
