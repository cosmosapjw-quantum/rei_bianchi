import struct
import unittest
from fractions import Fraction as F

from exact_gram.engine import ComplexDisk, Limits, ResourceLimit
from certificate_pipeline.synthetic import evaluate_synthetic_bundle, PipelineError


def matrix_bytes(scale, shape=(2,2)):
    # Synthetic binary64 diagonal values only, never science arrays.
    header = repr({'descr':'<c16','fortran_order':False,'shape':shape}).encode()
    header += b' ' * ((-(10+len(header)+1)) % 64) + b'\n'
    body = b''.join(struct.pack('<dd', scale if i==j else 0, 0)
                    for i in range(shape[0]) for j in range(shape[1]))
    return b'\x93NUMPY\x01\x00'+len(header).to_bytes(2,'little')+header+body


def fixture(radius=F(0)):
    raw = {'D_col':matrix_bytes(0),'D_row':matrix_bytes(0)}
    models = {name:{'D_col':matrix_bytes(s),'D_row':matrix_bytes(0),'K':matrix_bytes(s/2)}
              for name,s in (('R31AK',1),('R31Z',3),('R31AD',5))}
    balls = {key:[[ComplexDisk((F(0),F(0)),radius) for _ in range(2)] for _ in range(2)]
             for key in raw}
    return raw,models,balls


class PipelineTests(unittest.TestCase):
    def test_exact_synthetic_chain(self):
        r=evaluate_synthetic_bundle(*fixture(),scope='SYNTHETIC_ONLY')
        self.assertEqual(r['epsilon_arithmetic'],{'D_col':'0','D_row':'0','K':'0','Dmax':'0'})
        self.assertEqual(r['comparisons']['PRIMARY']['lower_gaps'],['1','2'])
        self.assertEqual(r['comparisons']['SECONDARY']['lower_gaps'],['2','4'])
        self.assertEqual(r['status'],'SYNTHETIC_REAL_RULE_SUPPORTED')
        self.assertFalse(r['rigorous'])
        self.assertIsNone(r['certified_epsilon'])
        self.assertFalse(r['independent_review_admitted'])

    def test_wide_balls_are_inconclusive(self):
        r=evaluate_synthetic_bundle(*fixture(F(10)),scope='SYNTHETIC_ONLY')
        self.assertEqual(r['status'],'SYNTHETIC_DECISION_BOUND_UNRESOLVED')
        self.assertEqual(r['epsilon_arithmetic']['D_col'],'20')

    def test_hh_scope_rejected_before_decoding(self):
        with self.assertRaises(PipelineError):
            evaluate_synthetic_bundle(None,None,None,scope='ACTUAL_HH')

    def test_missing_model_rejected(self):
        raw,models,balls=fixture();del models['R31AD']
        with self.assertRaises(PipelineError):
            evaluate_synthetic_bundle(raw,models,balls,scope='SYNTHETIC_ONLY')

    def test_scalar_and_shape_corruption_rejected(self):
        raw,models,balls=fixture();raw['D_col']=raw['D_col'][:-1]
        with self.assertRaises(PipelineError):
            evaluate_synthetic_bundle(raw,models,balls,scope='SYNTHETIC_ONLY')

    def test_resource_cap_is_not_a_pass(self):
        with self.assertRaises(ResourceLimit):
            evaluate_synthetic_bundle(*fixture(),scope='SYNTHETIC_ONLY',limits=Limits(max_entries=1))

    def test_model_only_resource_cap_is_classified(self):
        raw,models,balls=fixture();models['R31AK']['K']=matrix_bytes(1,shape=(3,2))
        with self.assertRaises(ResourceLimit):
            evaluate_synthetic_bundle(raw,models,balls,scope='SYNTHETIC_ONLY',limits=Limits(max_entries=4))

    def test_disk_shape_rejected(self):
        raw,models,balls=fixture();balls['D_col']=[]
        with self.assertRaises(PipelineError):
            evaluate_synthetic_bundle(raw,models,balls,scope='SYNTHETIC_ONLY')


if __name__=='__main__':unittest.main()
