import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import unittest
import tempfile

import photon_ledger_diagnosis as diagnosis


def write(path, value):
    path.write_text(json.dumps(value))


def physical(number, photo=0.):
    return dict(N=number, ledgers=[0.]*4+[photo, 0., 0.]+[0.]*7)


def fixture(tmp_path, residual=0.):
    write(tmp_path/'setup.json', dict(birth_count=2, births=[1., 2.],
                                    extra=14, source_inventory=[[1., 20.], [2., 40.]]))
    write(tmp_path/'endpoint.json', physical(2.+residual, 1.))
    write(tmp_path/'ledgers.json', dict(photon_normalized=abs(residual)/(6.+residual)))
    write(tmp_path/'solver_return.json', dict(status='COMPLETE', intervals=[
        dict(event=0, active=0, N=0.), dict(event=1, active=1, N=.75),
        dict(event=2, active=2, N=2.+residual)]))
    for event, photo in enumerate([0., .25, 1.]):
        np.save(tmp_path/f'accepted_coordinates_event{event}.npy', [0.]*8+physical(0., photo)['ledgers'])
    return tmp_path


class PhotonLedgerDiagnosisTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.tmp_path=Path(self.directory.name)

    def test_conservation_source_jump_and_intervals(self):
        tmp_path=self.tmp_path
        fixture(tmp_path)
        write(tmp_path/'observations.json', [
            dict(x=1., side='pre', active=0, physical=physical(0.)),
            dict(x=1., side='post', active=1, physical=physical(1.)),
            dict(x=2., side='pre', active=1, physical=physical(.75, .25)),
            dict(x=2., side='post', active=2, physical=physical(2.75, .25))])
        report=diagnosis.diagnose(tmp_path)
        assert report['original_gate']['fixed_gate_pass']
        assert report['endpoint']['decimal80']['residual']=='0'
        assert all(float(r['budget']['signed_local_delta_decimal80'])==0 for r in report['intervals']['records'])
        assert all(r['exact_stored_invariant_unchanged'] for r in report['source_jumps']['records'])
        assert report['history_interpretation']=='UNRESOLVED'


    def test_real_frozen_gate_failure_is_retained(self):
        tmp_path=self.tmp_path
        fixture(tmp_path, 1e-6)
        before={p.name:p.read_bytes() for p in tmp_path.iterdir()}
        report=diagnosis.diagnose(tmp_path)
        assert not report['original_gate']['fixed_gate_pass']
        assert not report['endpoint']['decimal80']['fixed_gate_pass']
        assert report['interpretation']=='UNRESOLVED'
        assert before=={p.name:p.read_bytes() for p in tmp_path.iterdir()}


    def test_final_addition_cancellation_and_roundoff_bound(self):
        report=diagnosis.budget(1e16, [1., -1e16, 0.], [1.])
        naive=0.
        for value in [1e16,1.,-1e16,0.,-1.]:
            naive+=value
        assert naive == -1.
        assert report['fsum']['residual']==0.
        assert float(report['decimal80']['residual'])==0.
        assert report['final_addition_roundoff_bound']>=1.
        assert report['term_count']==5

    def test_roundoff_only_near_gate_is_distinguished_from_history(self):
        tmp_path=self.tmp_path
        photo=2.00000002e-8
        write(tmp_path/'setup.json',dict(birth_count=1,births=[1.],extra=14,
                                       source_inventory=[[1.,20.]]))
        write(tmp_path/'endpoint.json',physical(1.,photo))
        exact=diagnosis.budget(1.,[photo,0.,0.],[1.])
        gross=exact['fsum']['gross']
        stored=math.nextafter(1e-8*gross,math.inf)
        write(tmp_path/'ledgers.json',dict(photon_residual=stored,photon_gross=gross,
                                         photon_normalized=stored/gross))
        write(tmp_path/'solver_return.json',dict(status='HOLD'))
        report=diagnosis.diagnose(tmp_path)
        assert not report['original_gate']['fixed_gate_pass']
        assert report['endpoint']['decimal80']['fixed_gate_pass']
        assert report['interpretation']=='FINAL_SUMMATION_ONLY'
        assert report['history_interpretation']=='UNRESOLVED'


    def test_signed_local_integration_drift(self):
        tmp_path=self.tmp_path
        fixture(tmp_path, 1e-6)
        report=diagnosis.diagnose(tmp_path)
        last=report['intervals']['records'][-1]['budget']
        assert float(last['signed_local_delta_decimal80'])>0.
        assert report['observations']['status']=='MISSING_DATA'
        assert report['source_jumps']['status']=='MISSING_DATA'


    def test_missing_interval_breaks_delta_chain(self):
        tmp_path=self.tmp_path
        fixture(tmp_path)
        (tmp_path/'accepted_coordinates_event1.npy').unlink()
        report=diagnosis.diagnose(tmp_path)
        assert report['intervals']['status']=='MISSING_DATA'
        assert report['intervals']['records'][1]['budget']['status']=='MISSING_DATA'
        assert report['intervals']['records'][2]['budget']['signed_local_delta_decimal80'] is None
        assert report['intervals']['records'][2]['budget']['local_delta_status']=='MISSING_PREVIOUS_INTERVAL'


    def test_missing_data_explicit(self):
        tmp_path=self.tmp_path
        report=diagnosis.diagnose(tmp_path)
        assert report['status']=='MISSING_DATA'
        assert set(report['required_missing'])=={'setup.json','endpoint.json','ledgers.json','solver_return.json'}
        assert report['endpoint']['status']=='MISSING_DATA'


    def test_positive_negative_finite_terms_and_zero_gross(self):
        result=diagnosis.budget(-2., [1.,-3.,4.], [-1.,1.])
        assert result['fsum']['gross']==12.
        assert result['fsum']['residual']==0.
        assert diagnosis.budget(0., [0.]*3, [])['status']=='ZERO_GROSS_UNDEFINED'

    def test_subnormal_contribution_survives_normal_cancellation(self):
        smallest=float.fromhex('0x0.0000000000001p-1022')
        result=diagnosis.budget(1.,[smallest,0.,0.],[1.])
        assert diagnosis.residual_fraction(result)==diagnosis.Fraction.from_float(smallest)
        assert result['exact_fraction']['residual']['numerator']=='1'


    def test_nonfinite_terms_rejected(self):
        for value in [float('nan'),float('inf'),-float('inf')]:
            with self.assertRaises(ValueError):
                diagnosis.budget(value,[0.]*3,[])


    def test_cli_reports_without_touching_source(self):
        tmp_path=self.tmp_path
        data=fixture(tmp_path)
        output=tmp_path/'diagnosis.json'
        result=subprocess.run([sys.executable,str(Path(diagnosis.__file__)),
                               '--data',str(data),'--out',str(output)],capture_output=True,text=True)
        assert result.returncode==0,result.stderr
        report=json.loads(output.read_text())
        assert report['fixed_target']==1e-8
        assert report['state_or_ledger_modified'] is False
        assert report['original_gate']['policy']=='STORED_GATE_UNCHANGED'


if __name__ == "__main__":
    unittest.main()
