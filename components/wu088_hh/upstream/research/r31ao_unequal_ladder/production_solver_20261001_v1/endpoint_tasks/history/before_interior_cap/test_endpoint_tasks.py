import copy
import hashlib
import io
import json
import struct
import tempfile
import unittest
from unittest import mock
import zipfile
from fractions import Fraction as Q
from pathlib import Path

import planner as p


def toy_record(coefficient_bits=0x3ff0000000000000, extra=False):
    """Generated binary64 fixture only; no actual input path or payload."""
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_STORED) as z:
        for name,spec in p.adapter.SPEC.items():
            shape=tuple(spec['shape']); n=1
            for d in shape:n*=d
            bits=[0]*n
            if name=='exponents.npy':bits=[0x3ff0000000000000+(i<<48) for i in range(12)]
            if name in ('v.npy','pref.npy'):bits=[0x3ff0000000000000]
            if name=='C.npy':
                bits[0]=coefficient_bits
                if extra:bits[81]=0xc008000000000000
            header=repr({'descr':'<f8','fortran_order':spec['fortran_order'],'shape':shape}).encode('ascii')
            header+=b' '*((-(10+len(header)+1))%64)+b'\n'
            raw=b'\x93NUMPY\x01\x00'+struct.pack('<H',len(header))+header+b''.join(struct.pack('<Q',b) for b in bits)
            z.writestr(name,raw)
    data=stream.getvalue()
    return p.adapter.decode_npz(data,expected_archive_sha256=hashlib.sha256(data).hexdigest(),scope='SYNTHETIC_ONLY'),data


WINDOW={'l_t':'1/4','T_t':'4','l_u':'1/4','T_u':'4'}


class EndpointTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record,cls.archive=toy_record()
        cls.plan=p.build_plan(cls.record,WINDOW,precision_bits=24,panels=1)

    def test_complete_index_bijection_and_canonical_parameters(self):
        plan=self.plan
        self.assertEqual(len(plan['tasks']),2592)
        self.assertEqual([x['index'] for x in plan['tasks']],list(range(2592)))
        first=plan['tasks'][0]['parameters'];last=plan['tasks'][-1]['parameters']
        self.assertEqual(first,{'a':'1','b':'1','mu':'1','q1':'0','q2':'1','d1':['0','0','0'],'d2':['-2','0','-3/4']})
        self.assertEqual(last,{'a':'27/16','b':'27/16','mu':'1','q1':'1','q2':'0','d1':['-2','0','-3/4'],'d2':['0','0','0']})
        self.assertEqual(plan['tasks'][p.primitive_index(1,2,1,3,4)]['indices'],{'active':1,'field':2,'orbital':1,'ia':3,'ib':4})
        for bad in (-1,2592,True,'0'):
            with self.assertRaises(p.EndpointError):p.evaluate_task(plan,bad)

    def test_source_formula_equivalence_and_disjoint_accounting(self):
        result=p.evaluate_task(self.plan,0)
        C=p.engine.gaussian_field_majorant(Q(1),Q(1),(Q(0),)*3,(Q(-2),Q(0),Q(-3,4)),0,'s','O',24)
        ref=p.engine.complement_bound(0,0,Q(1),Q(1),Q(1),Q(1,4),Q(4),Q(1,4),Q(4),C,24,1)
        self.assertEqual(ref['bound'],C*(ref['E_t']*ref['W_u']+ref['J_t']*ref['E_u']))
        self.assertGreaterEqual(Q(result['endpoint_radius']),ref['bound'])
        self.assertLess(Q(result['endpoint_radius']),ref['bound']*(1+Q(1,1<<23))**4)
        self.assertEqual(result['accounting'],p.ACCOUNTING)
        self.assertFalse(result['scientific_admission'])
        self.assertEqual(result['status'],'CONDITIONAL_TAIL_BOUND')

    def test_signed_coefficient_absolute_scaling_and_sum(self):
        unit=p.evaluate_task(self.plan,0)
        record,_=toy_record(0xc008000000000000)
        triple=p.evaluate_task(p.build_plan(record,WINDOW,precision_bits=24,panels=1),0)
        # Upward rounding is deliberately not an exact linear map.
        ratio=Q(triple['endpoint_radius'])/(3*Q(unit['endpoint_radius']))
        self.assertLess(ratio,(1+Q(1,1<<23))**4)
        self.assertGreater(ratio,1/(1+Q(1,1<<23))**4)
        record,_=toy_record(extra=True)
        plan=p.build_plan(record,WINDOW,precision_bits=24,panels=1)
        result=p.evaluate_task(plan,0)
        self.assertEqual([(t['i'],t['j'],t['k']) for t in plan['terms']],[(0,0,0),(1,0,0)])
        subtotal=sum((Q(t['contribution']) for t in result['terms']),Q(0))
        self.assertGreaterEqual(Q(result['endpoint_radius']),subtotal)
        self.assertLess(Q(result['endpoint_radius']),subtotal*(1+Q(1,1<<23))**len(result['terms']))

    def test_complex_absolute_upper_is_outward(self):
        self.assertEqual(p.complex_abs_upper('3','4',24),Q(5))
        upper=p.complex_abs_upper('1','1',24)
        self.assertGreaterEqual(upper*upper,Q(2))
        with self.assertRaises(p.EndpointError):p.complex_abs_upper(1.0,'1',24)

    def test_plan_identity_rejects_parameter_window_and_source_changes(self):
        for mutate in (lambda x:x['tasks'][0]['parameters'].__setitem__('a','2'),
                       lambda x:x['window'].__setitem__('T_t','8'),
                       lambda x:x['source_hashes'].__setitem__('endpoint_bound/engine.py','0'*64)):
            changed=copy.deepcopy(self.plan);mutate(changed)
            changed['plan_sha256']=p.digest({k:v for k,v in changed.items() if k!='plan_sha256'})
            with self.assertRaises(p.EndpointError):p.validate_plan(changed)

    def test_invalid_windows_caps_and_donor(self):
        for value in ('1/3','0','-1','1.0',0.25):
            with self.assertRaises(p.EndpointError):p.build_plan(self.record,{**WINDOW,'l_t':value})
        with self.assertRaises(p.EndpointError):p.build_plan(self.record,WINDOW,caps={'wall_seconds':0})
        changed=copy.deepcopy(self.record);changed['fields']['C']['values']=['0']*729
        changed['canonical_record_sha256']=p.adapter._record_digest(changed)
        with self.assertRaises(p.EndpointError):p.build_plan(changed,WINDOW)

    def test_pinned_scope_cannot_be_self_asserted(self):
        record=copy.deepcopy(self.record);record['scope']='FROZEN107_PINNED'
        record['archive_sha256']=p.adapter.FROZEN107_ARCHIVE_SHA256
        record['canonical_record_sha256']=p.adapter._record_digest(record)
        with self.assertRaises(p.EndpointError):p.build_plan(record,WINDOW)
        with self.assertRaises(p.EndpointError):p.build_plan(record,WINDOW,source_archive_bytes=self.archive)

    def test_result_identity_incomplete_and_duplicate_coverage(self):
        result=p.evaluate_task(self.plan,0)
        self.assertEqual(p.validate_result(self.plan,result),result)
        incomplete=p.collect(self.plan,[result])
        self.assertEqual(incomplete['status'],'INCOMPLETE_ENDPOINT_COVERAGE')
        self.assertEqual(incomplete['missing_count'],2591)
        with self.assertRaises(p.EndpointError):p.collect(self.plan,[result,result])
        changed=copy.deepcopy(result);changed['task_sha256']='0'*64
        changed['result_sha256']=p.digest({k:v for k,v in changed.items() if k!='result_sha256'})
        with self.assertRaises(p.EndpointError):p.validate_result(self.plan,changed)

    def test_cooperative_resource_refusal_is_not_bound(self):
        record,_=toy_record(extra=True)
        plan=p.build_plan(record,WINDOW,precision_bits=24,panels=1,caps={'max_engine_calls':1})
        result=p.evaluate_task(plan,0)
        self.assertEqual(result['status'],'INCONCLUSIVE_RESOURCE_LIMIT')
        self.assertIsNone(result['endpoint_radius'])

    def test_guarded_run_and_identity_checked_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);planpath=folder/'plan.json';out=folder/'result.json'
            p.write_new(planpath,self.plan)
            first=p.run_task(planpath,0,out)
            self.assertEqual(first['status'],'CONDITIONAL_TAIL_BOUND')
            self.assertEqual(p.run_task(planpath,0,out,resume=True)['result_sha256'],first['result_sha256'])
            with self.assertRaises(p.EndpointError):p.run_task(planpath,0,out)
            with self.assertRaises(p.EndpointError):p.run_task(planpath,1,out,resume=True)

    def test_guarded_resource_status_is_preserved(self):
        plan=p.build_plan(self.record,WINDOW,precision_bits=24,panels=1,caps={'max_engine_calls':1})
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);planpath=folder/'plan.json';out=folder/'result.json'
            p.write_new(planpath,plan)
            result=p.run_task(planpath,0,out)
            self.assertEqual(result['status'],'INCONCLUSIVE_RESOURCE_LIMIT')
            self.assertIsNone(result['endpoint_radius'])
            with self.assertRaises(p.EndpointError):p.run_task(planpath,0,out,resume=True)

    def test_worker_cannot_substitute_different_task(self):
        wrong=p.evaluate_task(self.plan,1)
        process=mock.Mock(returncode=0)
        process.communicate.return_value=(p.encoded(wrong),b'')
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);planpath=folder/'plan.json';out=folder/'result.json'
            p.write_new(planpath,self.plan)
            with mock.patch.object(p.subprocess,'Popen',return_value=process):
                result=p.run_task(planpath,0,out)
            self.assertEqual(result['status'],'INCONCLUSIVE_EXECUTION')
            self.assertIsNone(result['endpoint_radius'])
            self.assertEqual(result['index'],0)

    def test_upward_dyadic_independent_inequality_all_scales(self):
        for bits in (16,24,64,128,512):
            for exponent in (-10000,-200,-1,0,1,200,10000):
                scale=Q(1<<exponent) if exponent>=0 else Q(1,1<<(-exponent))
                for factor in (Q(1),Q(3,2),Q(7,5),1-Q(1,1<<(bits+2)),1+Q(1,1<<(bits+2))):
                    q=scale*factor;upper=p.upward_dyadic(q,bits)
                    self.assertGreaterEqual(upper,q)
                    self.assertLess(upper,q*(1+Q(1,1<<(bits-1))))
                    self.assertFalse(upper.denominator&(upper.denominator-1))
                    self.assertEqual(p.upward_dyadic(upper,bits),upper)

    def test_upward_dyadic_domain_and_work_caps(self):
        self.assertEqual(p.upward_dyadic(Q(0),128),0)
        for invalid in (Q(-1),True,1.0,'1/3'):
            with self.assertRaises((p.EndpointError,p.LimitReached)):p.upward_dyadic(invalid,128)
        with self.assertRaises(p.LimitReached):p.upward_dyadic(Q(1<<65536),128)
        with self.assertRaises(p.EndpointError):p.upward_dyadic(Q(1),0)

    def test_arithmetic_policy_is_identity_bound(self):
        self.assertEqual(self.plan['arithmetic_policy']['version'],'RELATIVE_DYADIC_UPPER_V1')
        changed=copy.deepcopy(self.plan);changed['arithmetic_policy']['significand_bits']=16
        with self.assertRaises(p.EndpointError):p.validate_plan(changed)
        result=p.evaluate_task(self.plan,0)
        self.assertEqual(result['arithmetic_policy'],self.plan['arithmetic_policy'])
        self.assertTrue(all(Q(t['field_majorant']).denominator&(Q(t['field_majorant']).denominator-1)==0 for t in result['terms']))


if __name__=='__main__':unittest.main()
