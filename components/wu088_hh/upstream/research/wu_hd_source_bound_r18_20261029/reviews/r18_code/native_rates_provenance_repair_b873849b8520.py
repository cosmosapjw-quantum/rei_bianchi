"""Exact decoding of one original GL2022 SQM printed reactive row.

This module supplies source nominal values on ten discrete temperatures.
Source uncertainty, interpolation, Boltzmann populations, density/clock coupling
and physical consumer admission are deliberately separate inputs.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, InitVar, field
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

PDF_SHA256 = "a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754"
PDF_SIZE = 273554
PDF_URL = "https://digital.csic.es/bitstream/10261/305186/2/h_hd_rate_supplementary_material.pdf"
RECORD_URL = "https://digital.csic.es/handle/10261/305186"
TEMPERATURES_K = (15, 55, 105, 255, 505, 1005, 1505, 2005, 2505, 3005)
SOURCE_DOI = "10.1063/5.0128598"
_SOURCE_ISSUANCE = object()


class SourceContractError(ValueError):
    """Wrong source identity, unsupported source domain, or malformed table."""


class ExtractionExecutionError(RuntimeError):
    """Observed external extractor failure, separate from source/model failure."""


def decode_printed_token(token: str) -> Fraction:
    """Decode a(x)=a*10**(-x) exactly in cm^3/s; no uncertainty inferred."""
    if type(token) is not str or len(token) > 32:
        raise SourceContractError("a bounded original printed token is required")
    match = re.fullmatch(r"([0-9]{1,6}(?:\.[0-9]{1,8})?)\(([0-9]{1,3})\)", token)
    if match is None:
        raise SourceContractError("expected source a(x) notation with negative exponent -x")
    mantissa = Fraction(match[1])
    exponent = int(match[2])
    if mantissa <= 0:
        raise SourceContractError("this selected source row requires positive printed values")
    return mantissa / (10 ** exponent)


def _table2_row(page_text: str) -> tuple[str, ...]:
    """Parse mathematics from an extracted page; this alone certifies no source."""
    if type(page_text) is not str:
        raise SourceContractError("page text required")
    starts = list(re.finditer(r"Table\s+2\s*:", page_text))
    ends = list(re.finditer(r"Table\s+3\s*:", page_text))
    if len(starts) != 1 or len(ends) != 1 or ends[0].start() <= starts[0].end():
        raise SourceContractError("unique ordered Table2/Table3 boundaries required")
    block = page_text[starts[0].end():ends[0].start()]
    caption = block.split("T [K]")[0]
    if not re.search(r"v\s*[′']\s*=\s*0\b", caption) or not re.search(r"j\s*[′']\s*=\s*1\b", caption):
        raise SourceContractError("Table2 product vprime0,jprime1 caption mismatch")
    headers = re.findall(r"^\s*T\s*\[K\]\s+(.+)$", block, re.MULTILINE)
    if len(headers) != 1:
        raise SourceContractError("one temperature header required")
    try:
        temperatures = tuple(int(x) for x in headers[0].split())
    except ValueError as exc:
        raise SourceContractError("invalid temperature header") from exc
    if temperatures != TEMPERATURES_K:
        raise SourceContractError("source temperature order/count changed")
    rows = re.findall(r"^\s*\(\s*0\s*,\s*(\d+)\s*\)\s+([^\n\r]+)$", block, re.MULTILINE)
    if tuple(int(j) for j, _ in rows) != tuple(range(7)):
        raise SourceContractError("source initial-state row coverage/order changed")
    target = tuple(values.split() for j, values in rows if j == "2")
    if len(target) != 1 or len(target[0]) != len(TEMPERATURES_K):
        raise SourceContractError("exactly ten cells in unique initial (0,2) row required")
    tokens = tuple(target[0])
    for token in tokens:
        decode_printed_token(token)
    return tokens


@dataclass(frozen=True)
class PrintedCell:
    temperature_K: int
    original_token: str
    nominal_cm3_s: Fraction

    def __post_init__(self) -> None:
        if type(self.temperature_K) is not int or self.temperature_K not in TEMPERATURES_K:
            raise SourceContractError("printed cell temperature is outside source grid")
        if type(self.nominal_cm3_s) is not Fraction or self.nominal_cm3_s != decode_printed_token(self.original_token):
            raise SourceContractError("printed token and exact nominal value disagree")

    @property
    def nominal_m3_s(self) -> Fraction:
        return self.nominal_cm3_s / 10**6


@dataclass(frozen=True)
class NativeGrid:
    cells: tuple[PrintedCell, ...]
    source_sha256: str
    extracted_page_sha256: str
    _issuance: InitVar[object] = None
    _source_verified: bool = field(init=False, default=False, repr=False)

    def __post_init__(self, _issuance: object) -> None:
        # An ordinary-API provenance guard; private/reflection abuse is outside
        # the supported API. Only the PDF-verified loader issues source grids.
        if _issuance is not _SOURCE_ISSUANCE:
            raise SourceContractError("construct native source grids through load_native_grid")
        if (type(self.cells) is not tuple or len(self.cells) != len(TEMPERATURES_K)
                or any(type(c) is not PrintedCell for c in self.cells)
                or tuple(c.temperature_K for c in self.cells) != TEMPERATURES_K
                or self.source_sha256 != PDF_SHA256
                or type(self.extracted_page_sha256) is not str
                or re.fullmatch(r"[0-9a-f]{64}", self.extracted_page_sha256) is None):
            raise SourceContractError("native grid source/order/identity invariant failed")
        for c in self.cells:
            if c.nominal_cm3_s != decode_printed_token(c.original_token):
                raise SourceContractError("native grid cell exactness invariant failed")
        object.__setattr__(self, "_source_verified", True)

    def _require_verified(self) -> None:
        if self._source_verified is not True:
            raise SourceContractError("unattested grid cannot issue a native source value")

    def lookup(self, temperature_K: int, *, initial_v: int = 0,
               initial_j: int = 2, product_v: int = 0, product_j: int = 1,
               method: str = "SQM") -> PrintedCell:
        self._require_verified()
        labels = (initial_v, initial_j, product_v, product_j)
        if any(type(x) is not int for x in labels) or labels != (0, 2, 0, 1) or method != "SQM":
            raise SourceContractError("only original SQM HD(v0,j2)->H2(v0,j1) is exported")
        if type(temperature_K) is not int or temperature_K not in TEMPERATURES_K:
            raise SourceContractError("temperature must equal a supplied discrete integer-K source point")
        return self.cells[TEMPERATURES_K.index(temperature_K)]

    def as_json(self) -> dict:
        self._require_verified()
        def rational(x: Fraction) -> dict[str, str]:
            return {"numerator": str(x.numerator), "denominator": str(x.denominator)}
        return {
            "schema": "wu.r18.native_printed_rate_grid.v1",
            "value_kind": "SOURCE_NATIVE_PRINTED_NOMINAL",
            "source": {"doi": SOURCE_DOI, "record_url": RECORD_URL, "pdf_url": PDF_URL,
                       "pdf_sha256": self.source_sha256, "pdf_size_bytes": PDF_SIZE,
                       "extraction": "pdftotext -layout -f 6 -l 6",
                       "extracted_page_sha256": self.extracted_page_sha256},
            "reaction": {"initial": ["H+", "HD(v=0,j=2)"],
                         "final": ["D+", "H2(v=0,j=1)"], "method": "SQM",
                         "raw_thermal_spin_factor_applied": False,
                         "thermal_odd_spin_factor_if_used": rational(Fraction(3, 4)),
                         "thermal_population_applied": False},
            "domain": {"temperature_K": list(TEMPERATURES_K), "kind": "discrete",
                       "interpolation": "NOT_PROVIDED", "extrapolation": "NOT_PROVIDED",
                       "exported_initial_vj": [0, 2], "exported_product_vj": [0, 1],
                       "supplement_initial_j_support": list(range(7)),
                       "main_article_initial_j_max": 8, "missing_j7_j8": "MISSING_NOT_ZERO"},
            "precision": {"printed_decimal_decoding": "exact rational",
                          "rounding_rule": "UNSPECIFIED",
                          "physical_rate_uncertainty": None, "true_rate_enclosure": None},
            "consumer": {"state_density_clock_bound": False, "physical_admission": False,
                         "HH_R10": "OFF", "production": "NOT_ISSUED", "L4": False},
            "cells": [{"temperature_K": c.temperature_K, "original_token": c.original_token,
                       "nominal_cm3_s_exact": rational(c.nominal_cm3_s),
                       "nominal_m3_s_exact": rational(c.nominal_m3_s),
                       "source_cell": {"pdf_page": 6, "table": 2, "row": "(0,2)",
                                       "temperature_column_1based": i + 1}}
                      for i, c in enumerate(self.cells)]
        }


def load_native_grid(pdf_path: str | Path, *, timeout_seconds: float = 20) -> NativeGrid:
    """Validate original bytes, extract Table2, and preserve token provenance."""
    path = Path(pdf_path)
    if path.stat().st_size != PDF_SIZE:
        raise SourceContractError("original supplement byte size mismatch")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != PDF_SHA256 or not raw.startswith(b"%PDF-"):
        raise SourceContractError("original supplement SHA256 mismatch")
    if not 0 < timeout_seconds <= 30:
        raise SourceContractError("extractor timeout must be in (0,30] seconds")
    try:
        execution = subprocess.run(
            ["pdftotext", "-layout", "-f", "6", "-l", "6", str(path), "-"],
            capture_output=True, check=False, timeout=timeout_seconds)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ExtractionExecutionError(f"current pdftotext execution failed: {exc}") from exc
    if execution.returncode != 0:
        raise ExtractionExecutionError(
            f"pdftotext exit {execution.returncode}: {execution.stderr.decode(errors='replace')}")
    try:
        text = execution.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ExtractionExecutionError("pdftotext did not return UTF-8 text") from exc
    tokens = _table2_row(text)
    cells = tuple(PrintedCell(t, token, decode_printed_token(token))
                  for t, token in zip(TEMPERATURES_K, tokens))
    return NativeGrid(cells, digest, hashlib.sha256(execution.stdout).hexdigest(),
                      _issuance=_SOURCE_ISSUANCE)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--temperature-K", type=int)
    args = parser.parse_args(argv)
    try:
        grid = load_native_grid(args.source_pdf)
        data = grid.as_json()
        if args.temperature_K is not None:
            cell = grid.lookup(args.temperature_K)
            data["cells"] = [c for c in data["cells"] if c["temperature_K"] == cell.temperature_K]
            data["query_temperature_K"] = cell.temperature_K
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    except (SourceContractError, ExtractionExecutionError, OSError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

