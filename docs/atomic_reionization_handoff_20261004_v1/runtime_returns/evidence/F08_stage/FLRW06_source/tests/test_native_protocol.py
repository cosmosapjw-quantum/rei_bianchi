"""Manufactured protocol tests only; these are NOT native return records."""
import unittest,copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'research'))
from native_protocol import stdin_payload,validate_records,evidence_gate

def protocol_fixture():
    data=json.loads((ROOT/'inputs/CASES.json').read_text());ref=json.loads((ROOT/'results/NODE_REFERENCE_80DIGIT.json').read_text())
    out=[]
    for i,c in enumerate(data['cases']):
        if c.get('expect_error'):out.append({'kind':'photo','index':i,'status':'error','error':c['expected_error']})
        else:
            row={'kind':'photo','index':i,'status':'ok'}
            for k,v in ref['references'][c['id']].items():row[k]=list(map(float,v)) if isinstance(v,list) else float(v)
            out.append(row)
    p={'kind':'photon','status':'ok'}
    for k,v in ref['photon'].items():p[k]=list(map(float,v)) if isinstance(v,list) else float(v)
    out.append(p);return data,ref,out

class ProtocolTests(unittest.TestCase):
    def test_comparison_code_on_manufactured_records(self):
        d,r,o=protocol_fixture();v=validate_records(o,d,r);self.assertEqual(v['compared_values'],167)
    def test_expectation_file_has_no_native_execution_authority(self):
        with self.assertRaisesRegex(ValueError,'MISSING_NATIVE'):evidence_gate({'status':'PREPARED','native_calls':0})
    def test_missing_record(self):
        d,r,o=protocol_fixture()
        with self.assertRaisesRegex(ValueError,'COUNT'):validate_records(o[:-1],d,r)
    def test_permuted_output(self):
        d,r,o=protocol_fixture();o[0],o[1]=o[1],o[0]
        with self.assertRaisesRegex(ValueError,'IDENTITY'):validate_records(o,d,r)
    def test_wrong_event_count(self):
        d,r,o=protocol_fixture();o[0]['events'][0]*=2
        with self.assertRaisesRegex(ValueError,'DIFFERENCE'):validate_records(o,d,r)
    def test_invalid_input_false_success(self):
        d,r,o=protocol_fixture();o[-2]['status']='ok'
        with self.assertRaisesRegex(ValueError,'INVALID_INPUT_ACCEPTED'):validate_records(o,d,r)
    def test_sinks_not_written_into_probe_input(self):
        d,r,o=protocol_fixture();x=stdin_payload(d)
        d['photon_input']['absorption_proper_cm3_s']=[999.,888.,777.]
        self.assertEqual(stdin_payload(d),x)
    def test_nonfinite_result(self):
        d,r,o=protocol_fixture();o[0]['heat'][0]=float('nan')
        with self.assertRaisesRegex(ValueError,'NONFINITE'):validate_records(o,d,r)

if __name__=='__main__':unittest.main()
