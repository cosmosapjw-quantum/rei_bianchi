import json
from pathlib import Path
import tempfile
import unittest

from receipt_output import write_receipt


class ReceiptOutput(unittest.TestCase):
    def test_new_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "result.json"
            write_receipt(p, {"status": "PASS"})
            self.assertEqual(json.loads(p.read_text()), {"status": "PASS"})
            self.assertEqual(list(Path(d).iterdir()), [p])

    def test_existing_receipt_is_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "result.json"
            p.write_bytes(b"original failure record\n")
            with self.assertRaises(FileExistsError):
                write_receipt(p, {"status": "PASS"})
            self.assertEqual(p.read_bytes(), b"original failure record\n")
            self.assertEqual(list(Path(d).iterdir()), [p])

    def test_nonfinite_receipt_leaves_no_output(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "result.json"
            with self.assertRaises(ValueError):
                write_receipt(p, {"residual": float("nan")})
            self.assertEqual(list(Path(d).iterdir()), [])

    def test_missing_destination_directory(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                write_receipt(Path(d) / "missing/result.json", {})
            self.assertEqual(list(Path(d).iterdir()), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
