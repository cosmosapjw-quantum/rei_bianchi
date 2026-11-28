#!/usr/bin/env python3
"""Published-receipt guard tests. Original source-native physics is tested elsewhere."""
from pathlib import Path
import importlib.util,shutil,tempfile,unittest

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("published_hei_photon_receipt",HERE/"verify_published_receipt.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
class ReceiptTests(unittest.TestCase):
    def test_frozen_source_free_receipt(self):
        mod.verify()
    def test_modification_fails_under_explicit_checks(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)
            for fn in mod.KNOWN:
                shutil.copy2(HERE/"results"/fn,out/fn)
            p=out/"SCIENCE_RESULT.json"
            p.write_bytes(p.read_bytes()+b" ")
            with self.assertRaisesRegex(ValueError,"HASH_DRIFT"):
                mod.verify(out)
    def test_source_code_not_falsely_certified(self):
        from json import loads
        d=loads((HERE/"results/SCIENCE_RESULT.json").read_text())
        self.assertFalse(d["official_tick161"])
        self.assertFalse(d["photon_transport_admitted"])
        self.assertEqual(d["nodes_read"],46080)
        self.assertEqual(d["canonical_delta"],0)
if __name__=="__main__":
    unittest.main()
