import csv
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from e11.verify_telemetry import verify

class TelemetryConsumerTests(unittest.TestCase):
    def create(self,root,corrupt=False):
        p=Path(root);out=p/'candidate';e7=p/'e7'
        out.mkdir();e7.mkdir();(e7/'data/histories').mkdir(parents=True)
        src=['step','s','BH','BY','BZ','bindMicro','thermalMicro']
        full=[dict(zip(src,[str(i),'1',str(i+1),'0.01','0.02','-0.03','-0.04'])) for i in range(3)]
        for target in (e7/'data/histories/OFF_N384_P512_O4.csv',out/'OWNER_INTERNAL_5.csv'):
            if target==out/'OWNER_INTERNAL_5.csv' and corrupt:full[1]['BH']='2.01'
            with target.open('w',newline='') as fd:
                w=csv.DictWriter(fd,fieldnames=src);w.writeheader();w.writerows(full)
        with (out/'OWNER_ACCEPTED_STAGES.csv').open('w',newline='') as fd:
            fd.write('step,stage,count,min,max,any,all,continuity_checks,continuity_max_relative\n1,0,1,1000,10000,true,true,1,0\n2,0,1,1000,10000,true,true,1,0\n')
        (out/'READY.json').write_text(json.dumps({'task':'E11_SHADOW_INTERNAL_TELEMETRY','mode':'OFF','N':384,'steps':2,'rows':3}))
        return out,e7
    def test_good_synthetic_fixture(self):
        with TemporaryDirectory() as tmp:
            out,e7=self.create(tmp)
            r=verify(out,e7,'OFF',2)
            self.assertEqual(r['matched_bits'],15)
    def test_false_telemetry_rejected(self):
        with TemporaryDirectory() as tmp:
            out,e7=self.create(tmp,corrupt=True)
            with self.assertRaises(ValueError):verify(out,e7,'OFF',2)
    def test_stage_absence_rejected(self):
        with TemporaryDirectory() as tmp:
            out,e7=self.create(tmp)
            (out/'OWNER_ACCEPTED_STAGES.csv').unlink()
            with self.assertRaises(FileNotFoundError):verify(out,e7,'OFF',2)
if __name__=='__main__':unittest.main()
