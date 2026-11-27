"""Eight distinct controls, executed only inside the authorized one-shot campaign."""
import copy
from fractions import Fraction as F
from pathlib import Path
import unittest
from tangent13 import (construct,dual,evaluate,isolate,load_inputs,solve3,signed_ratio,vec)
from verify_certificate import verify

SAVED=None
OFFICIAL=None
RESULT=None

class Controls(unittest.TestCase):
    def test_01_polynomial_root_and_rejections(self):
        # q(z)=(z-5/6)^2 is a rational double-root polynomial.
        p=vec(['25/36','-5/3','1'])
        self.assertEqual(evaluate(p,F(5,6)),0)
        self.assertGreaterEqual(evaluate(p,F(1,2)),0)
        exact=isolate(vec(['-17/20','1','0']))
        self.assertTrue(exact['exact_root']);self.assertEqual(exact['bracket'],[F(17,20)]*2)
        generic=isolate(vec(['-5/6','1','0']))
        self.assertEqual(generic['bisections'],80)
        self.assertLessEqual(generic['bracket'][0],F(5,6));self.assertGreaterEqual(generic['bracket'][1],F(5,6))
        with self.assertRaisesRegex(ValueError,'bracket'):isolate(vec(['1','1','0']))
        with self.assertRaisesRegex(ValueError,'derivative'):isolate(vec(['.6375','-1.6','1']))
    def test_02_exact_linear_system(self):
        matrix=[vec(x) for x in [['1','2','3'],['0','1','4'],['5','6','0']]]
        self.assertEqual(solve3(matrix,vec(['14','14','17'])),vec(['1','2','3']))
        with self.assertRaisesRegex(ValueError,'singular'):solve3([vec(['1','0','0'])]*3,vec(['1','1','1']))
    def test_03_manufactured_dual(self):
        # d=(1,0,0), h=(0,1,0), v(1)=(1,1,1): k=2d+3h+5v.
        d=vec(['1','0','0']);h=vec(['0','1','0'])
        q=dual(vec(['7','8','5']),d,h,F(1))
        self.assertEqual([q['alpha'],q['lambda'],q['mu']],vec(['2','3','5']))
        with self.assertRaisesRegex(ValueError,'negative'):dual(vec(['7','4','5']),d,h,F(1))
    def test_04_signed_moments_manual(self):
        # b=(2,-3,1), k in [1,2]x[3,5]x[7,11], D=2.
        self.assertEqual(signed_ratio(vec(['2','-3','1']),vec(['1','3','7']),vec(['2','5','11']),vec(['1','0','0'])),[F(-3),F(3)])
    def test_05_source_and_vertex_binding(self):
        a,case,rows,windows=load_inputs(SAVED,OFFICIAL)
        self.assertEqual(len(RESULT['normalized_envelope']['vertices']),case['polytopes']['outer']['unique_vertices'])
        self.assertEqual(verify(RESULT,SAVED,OFFICIAL)['status'],'PASS')
        bad=copy.deepcopy(RESULT);bad['normalized_envelope']['vertices'][0][0]='999'
        with self.assertRaisesRegex(ValueError,'outer vertices'):verify(bad,SAVED,OFFICIAL)
    def test_06_actual_dual_and_negative_control(self):
        for g in RESULT['objectives']:
            self.assertGreaterEqual(F(RESULT['objectives'][g]['dual']['lambda']),0)
            self.assertGreaterEqual(F(RESULT['objectives'][g]['dual']['mu']),0)
        bad=copy.deepcopy(RESULT);bad['objectives']['CAPS']['dual']['lambda']='-1'
        with self.assertRaisesRegex(ValueError,'multiplier sign'):verify(bad,SAVED,OFFICIAL)
    def test_07_actual_square_and_window_rejection(self):
        self.assertEqual(len(RESULT['square_witness']['data']),4)
        self.assertGreater(F(RESULT['square_witness']['a']),0)
        bad=copy.deepcopy(RESULT);bad['square_witness']['coefficients'][1]='0'
        with self.assertRaisesRegex(ValueError,'square identity'):verify(bad,SAVED,OFFICIAL)
    def test_08_brackets_and_width_rejection(self):
        for geom,o in RESULT['objectives'].items():
            self.assertLessEqual(F(o['width']),F(1,10**10))
            self.assertGreaterEqual(F(o['width']),0)
        bad=copy.deepcopy(RESULT);bad['objectives']['CAPS']['minimum_bracket'][0]='1'
        with self.assertRaisesRegex(ValueError,'final bounds'):verify(bad,SAVED,OFFICIAL)
