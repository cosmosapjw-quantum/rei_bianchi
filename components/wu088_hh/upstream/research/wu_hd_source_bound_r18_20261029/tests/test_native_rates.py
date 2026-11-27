"""New R18 primary: original PDF, independent row oracle, contracts and CLI.

Run with WU_R18_SOURCE_PDF=/absolute/original.pdf python3 tests/test_native_rates.py.
The exact source data (not a surrogate) are required.
"""
from fractions import Fraction as F
from dataclasses import replace
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

LEAF = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LEAF / "src"))
from native_rates import (PDF_SHA256, PDF_SIZE, TEMPERATURES_K, SourceContractError,
                          ExtractionExecutionError, _table2_row, decode_printed_token,
                          load_native_grid, main, NativeGrid, PrintedCell)


class TestNativeSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_pdf = Path(os.environ["WU_R18_SOURCE_PDF"])
        cls.grid = load_native_grid(cls.source_pdf)
        cls.oracle = json.loads((LEAF / "reviews/r18_source/INDEPENDENT_SOURCE_REVIEW.json").read_text())
        cls.page_text = subprocess.check_output(
            ["pdftotext", "-layout", "-f", "6", "-l", "6", str(cls.source_pdf), "-"]).decode()

    def test_original_identity(self):
        self.assertEqual(self.source_pdf.stat().st_size, PDF_SIZE)
        self.assertEqual(hashlib.sha256(self.source_pdf.read_bytes()).hexdigest(), PDF_SHA256)
        self.assertEqual(self.grid.source_sha256, self.oracle["source"]["sha256"])

    def test_every_native_cell_against_independent_source(self):
        self.assertEqual(len(self.grid.cells), 10)
        for c, oracle in zip(self.grid.cells, self.oracle["cells"]):
            self.assertEqual(c.temperature_K, oracle["temperature_K"])
            self.assertEqual(c.original_token, oracle["source_token"])
            cm = oracle["printed_value_cm3_per_s_exact"]
            si = oracle["printed_value_m3_per_s_exact"]
            self.assertEqual(c.nominal_cm3_s, F(int(cm["numerator"]), int(cm["denominator"])))
            self.assertEqual(c.nominal_m3_s, F(int(si["numerator"]), int(si["denominator"])))

    def test_negative_exponent_and_si_first_last(self):
        self.assertEqual(decode_printed_token("3.99(14)"), F(399,10**16))
        self.assertEqual(self.grid.lookup(15).nominal_m3_s, F(399,10**22))
        self.assertEqual(self.grid.lookup(3005).nominal_m3_s, F(13,62500000000000000))

    def test_all_lookup_values(self):
        for c in self.grid.cells:
            self.assertIs(self.grid.lookup(c.temperature_K), c)
            self.assertGreater(c.nominal_m3_s, 0)
            self.assertEqual(c.nominal_cm3_s / c.nominal_m3_s, 10**6)

    def test_discrete_domain_guard(self):
        for t in [0, -1, 205, 295, 300, 3006, 15.0, F(15), True, "15"]:
            with self.assertRaises(SourceContractError):
                self.grid.lookup(t)

    def test_source_state_method_guards(self):
        for kwargs in [{"initial_j":7},{"initial_j":8},{"product_j":0},
                       {"initial_v":1},{"product_v":1},{"method":"TIQM"},
                       {"method":"EQM"},{"initial_v":False},{"product_j":True}]:
            with self.assertRaises(SourceContractError):
                self.grid.lookup(15, **kwargs)

    def test_raw_spin_and_physical_scope(self):
        data = self.grid.as_json()
        self.assertFalse(data["reaction"]["raw_thermal_spin_factor_applied"])
        self.assertEqual(data["reaction"]["thermal_odd_spin_factor_if_used"],
                         {"numerator":"3","denominator":"4"})
        self.assertIsNone(data["precision"]["physical_rate_uncertainty"])
        self.assertIsNone(data["precision"]["true_rate_enclosure"])
        self.assertFalse(data["consumer"]["physical_admission"])
        self.assertEqual(data["domain"]["missing_j7_j8"], "MISSING_NOT_ZERO")
        self.assertEqual(data["consumer"]["HH_R10"], "OFF")

    def test_nominal_rationals_roundtrip(self):
        data = json.loads(json.dumps(self.grid.as_json()))
        for c, row in zip(self.grid.cells, data["cells"]):
            val = row["nominal_m3_s_exact"]
            self.assertEqual(c.nominal_m3_s,F(int(val["numerator"]),int(val["denominator"])))
            self.assertEqual(row["source_cell"]["table"],2)

    def test_bad_token_guards(self):
        for token in ["3.99e-14","3.99(-14)","-3.99(14)","0.00(10)","3.99(14)junk",
                      "3.99(1234)","9"*33, "3.99(14) ",None,True]:
            with self.assertRaises(SourceContractError):
                decode_printed_token(token)

    def test_source_table_order_guard(self):
        text = self.page_text.replace("Table 2:", "Table 4:", 1)
        with self.assertRaises(SourceContractError):
            _table2_row(text)
        with self.assertRaises(SourceContractError):
            _table2_row(self.page_text + "\nTable 2: duplicate")

    def test_source_caption_guard(self):
        prefix, rest = self.page_text.split("Table 2:",1)
        altered = rest.replace("j ′ = 1","j ′ = 9",1)
        self.assertNotEqual(altered, rest)
        with self.assertRaises(SourceContractError):
            _table2_row(prefix+"Table 2:"+altered)

    def test_temperature_order_guard(self):
        prefix, rest = self.page_text.split("Table 2:",1)
        lines=rest.splitlines()
        i=next(i for i,line in enumerate(lines) if line.lstrip().startswith("T [K]"))
        lines[i]=lines[i].replace("3005","3006")
        with self.assertRaises(SourceContractError):
            _table2_row(prefix+"Table 2:"+"\n".join(lines))

    def test_missing_or_duplicate_row_guard(self):
        prefix, rest = self.page_text.split("Table 2:",1)
        lines=rest.splitlines()
        i=next(i for i,line in enumerate(lines) if line.lstrip().startswith("(0,2)"))
        for altered in [lines[:i]+lines[i+1:],lines[:i]+[lines[i]]+lines[i:]]:
            with self.assertRaises(SourceContractError):
                _table2_row(prefix+"Table 2:"+"\n".join(altered))

    def test_wrong_pdf_and_same_size_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            wrong=Path(d)/"wrong.pdf";wrong.write_bytes(b"%PDF-wrong")
            with self.assertRaises(SourceContractError): load_native_grid(wrong)
            raw=bytearray(self.source_pdf.read_bytes());raw[-20]^=1;wrong.write_bytes(raw)
            with self.assertRaises(SourceContractError): load_native_grid(wrong)

    def test_extractor_error_class_separate(self):
        with patch("native_rates.subprocess.run",side_effect=FileNotFoundError("injected")):
            with self.assertRaises(ExtractionExecutionError):
                load_native_grid(self.source_pdf)

    def test_unattested_source_constructor_rejected(self):
        synthetic = tuple(PrintedCell(t, "1.00(0)", F(1)) for t in TEMPERATURES_K)
        with self.assertRaises(SourceContractError):
            NativeGrid(synthetic, PDF_SHA256, "a"*64)
        with self.assertRaises(SourceContractError):
            replace(self.grid, cells=synthetic)
        with self.assertRaises(SourceContractError):
            PrintedCell(15,"3.99(14)",F(1))

    def test_verified_bytes_survive_source_path_replacement(self):
        original_run = subprocess.run
        raw = self.source_pdf.read_bytes()
        with tempfile.TemporaryDirectory() as d:
            copied = Path(d)/"mutable.pdf"
            copied.write_bytes(raw)
            def swap_path_then_extract(argv, **kwargs):
                copied.write_bytes(b"x"*len(raw))
                self.assertEqual(argv[-2:], ["-", "-"])
                self.assertEqual(kwargs["input"], raw)
                return original_run(argv, **kwargs)
            with patch("native_rates.subprocess.run", side_effect=swap_path_then_extract):
                verified = load_native_grid(copied)
            self.assertEqual(verified.lookup(15).original_token, "3.99(14)")
            self.assertNotEqual(copied.read_bytes(), raw)
        with patch("native_rates.subprocess.run",return_value=subprocess.CompletedProcess([],1,b"",b"injected failure")):
            with self.assertRaises(ExtractionExecutionError):
                load_native_grid(self.source_pdf)

    def test_stoichiometric_conservation(self):
        nu=(-1,-1,1,1)
        for conserved in [(1,1,0,2),(0,1,1,0),(1,0,1,0)]:
            self.assertEqual(sum(a*b for a,b in zip(nu,conserved)),0)

    def test_supported_cli_and_exclusive_output(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"native.json"
            self.assertEqual(main(["--source-pdf",str(self.source_pdf),"--output",str(out),
                                   "--temperature-K","105"]),0)
            decoded=json.loads(out.read_text())
            self.assertEqual(decoded["cells"][0]["original_token"],"1.15(10)")
            before=out.read_bytes()
            self.assertEqual(main(["--source-pdf",str(self.source_pdf),"--output",str(out)]),2)
            self.assertEqual(out.read_bytes(),before)
            bad=Path(d)/"offgrid.json"
            self.assertEqual(main(["--source-pdf",str(self.source_pdf),"--output",str(bad),
                                   "--temperature-K","205"]),2)
            self.assertFalse(bad.exists())


if __name__ == "__main__":
    started_cpu=time.process_time();started_wall=time.monotonic()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(TestNativeSource)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={"schema":"wu.r18.primary_execution.v1","command":"WU_R18_SOURCE_PDF=original.pdf python3 tests/test_native_rates.py",
            "tests_run":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),
            "cpu_seconds":time.process_time()-started_cpu,"wall_seconds":time.monotonic()-started_wall,
            "exit_code":0 if result.wasSuccessful() else 1,"scope":"actual original native printed source and injected failure guards",
            "physical_ODE_runs":0,"old_suite_replays":0,
            "module_sha256":hashlib.sha256((LEAF/"src/native_rates.py").read_bytes()).hexdigest()}
    (LEAF/"results/PRIMARY_EXECUTION.json").write_text(json.dumps(report,indent=2)+"\n")
    if result.wasSuccessful():
        (LEAF/"results/NATIVE_ROW_COMPUTED.json").write_text(json.dumps(TestNativeSource.grid.as_json(),indent=2)+"\n")
    raise SystemExit(report["exit_code"])

