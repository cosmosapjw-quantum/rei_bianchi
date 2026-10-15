import csv, hashlib, json, tempfile, unittest
from pathlib import Path
import numpy as np
from cold_history_tau import read_history, run, HE_TO_H, OPACITY_FACTOR

def fixture(root, *, bad_hash=False, bad_density=False, bad_clock=False):
    root=Path(root)
    p=root/"history.csv"
    header=["case_id","time_s","a","zbar","nH_proper_cm3",
            "ne_proper_cm3","x_HII","x_HeII","x_HeIII"]
    times=[0.,1.,3.] if not bad_clock else [0.,1.,1.]
    with p.open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(header)
        for i,t in enumerate(times):
            x,y,z=.25,.4,.1
            nh=2.
            ne=nh*(x+HE_TO_H*(y+2*z))
            if bad_density:ne+=.01
            w.writerow(["MANUFACTURED",t,.05+i*.001,20-i,nh,ne,x,y,z])
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    if bad_hash:digest="0"*64
    (root/"COMPLETED_CASE_INPUT.json").write_text(json.dumps({"history":{"sha256":digest}}))
    return p

class TestColdHistory(unittest.TestCase):
    def test_read_real_format_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=fixture(tmp)
            case, data, sha, meta=read_history(p)
            self.assertEqual(case,"MANUFACTURED")
            self.assertEqual(len(data["time_s"]),3)
            report=run(p,Path(tmp)/"results",reps=1)
            self.assertAlmostEqual(report["tau_trap_from_native_ne"],
                OPACITY_FACTOR*(3.*(2.*(.25+HE_TO_H*(.4+2*.1)))),places=13)
            self.assertEqual(report["rows"],3)
    def test_bad_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,"Byte identity"):
                read_history(fixture(tmp,bad_hash=True))
    def test_bad_density(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,"electron census mismatch"):
                run(fixture(tmp,bad_density=True),Path(tmp)/"results",reps=1)
    def test_bad_clock(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,"strictly increasing"):
                read_history(fixture(tmp,bad_clock=True))

if __name__=="__main__": unittest.main()
