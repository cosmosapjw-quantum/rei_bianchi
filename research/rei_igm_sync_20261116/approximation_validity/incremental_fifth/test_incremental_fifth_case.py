"""Admission and parity tests; no physical history is evolved or admitted."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from incremental_fifth_case import admit, parity, sha


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.history=self.root/'history.csv'
        self.history.write_bytes(b'fixture bytes; not physical data\n')
        self.manifest=self.root/'composition.json'
        self.value={'schema':'rei.axbi.plus_complete_composition.v1','admission':{
            'status':'COMPLETE_COMPOSED_HISTORY','case_id':'SHEAR_PLUS','q_ref':.01,
            'zbar_start':20.,'zbar_end':4.,'rows':3,'native_terminal_accepted':2,
            'boundary_checks_passed':True,'terminal_checkpoint_matches':True,
            'original_physics_identity_verified':True,
            'bytes':self.history.stat().st_size,'sha256':sha(self.history)}}

    def tearDown(self):self.tmp.cleanup()

    def save(self):self.manifest.write_text(json.dumps(self.value))

    def test_admission_checks_only_metadata_and_bytes(self):
        self.save()
        self.assertEqual(admit(self.manifest,self.history)['rows'],3)

    def test_partial_history_rejected_before_read(self):
        self.value['admission']['status']='STOPPED_CHECKPOINTED';self.save()
        with patch('incremental_fifth_case.sha',side_effect=AssertionError('must not read')):
            with self.assertRaisesRegex(ValueError,'ENDPOINT_NOT_ADMITTED'):
                admit(self.manifest,self.history)

    def test_wrong_physics_case_domain_or_composition_rejected(self):
        for field,bad in [('case_id','SHEAR_MINUS'),('q_ref',-.01),('zbar_end',8.),
                          ('boundary_checks_passed',False),('terminal_checkpoint_matches',False),
                          ('original_physics_identity_verified',False),('native_terminal_accepted',1)]:
            with self.subTest(field=field):
                saved=self.value['admission'][field];self.value['admission'][field]=bad;self.save()
                with self.assertRaises(ValueError):admit(self.manifest,self.history)
                self.value['admission'][field]=saved

    def test_corrupted_bytes_rejected(self):
        self.save();self.history.write_bytes(b'x'*self.value['admission']['bytes'])
        with self.assertRaisesRegex(ValueError,'SOURCE_SHA'):admit(self.manifest,self.history)


class ResponseTests(unittest.TestCase):
    def test_parity_extracts_linear_cubic_and_quadratic_terms(self):
        q=.01;x0=np.array([.1,.3,.7]);a=np.array([.4,-.2,.5]);b=np.array([.8,.9,-.4]);c=np.array([.3,.2,.1])
        plus=x0+a*q+b*q*q+c*q**3;minus=x0-a*q+b*q*q-c*q**3
        odd,even=parity(plus,minus,x0)
        np.testing.assert_allclose(odd,a*q+c*q**3,atol=1e-16,rtol=0)
        np.testing.assert_allclose(even,b*q*q,atol=1e-16,rtol=0)


if __name__=='__main__':unittest.main()
