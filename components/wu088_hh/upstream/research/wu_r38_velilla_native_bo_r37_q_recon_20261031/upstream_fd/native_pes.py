"""Exact source-backed native callable for Velilla et al. (2008) EPAPS h3plus.f.

Build the original unchanged Fortran 77 by separating program units to avoid
modern gfortran intra-file rank/array-bound checking of an implicit interface.
No source statement, coefficient, call or expression is edited.
"""
from __future__ import annotations
import ctypes as C
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]


def build(source: pathlib.Path | None = None, output: pathlib.Path | None = None) -> pathlib.Path:
    source = source or ROOT / "original" / "h3plus.f"
    output = output or ROOT / "build" / "libvelilla2008.so"
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = source.read_bytes().splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if re.match(rb"^\s{6}(subroutine|function) ", line, re.I)]
    if len(starts) != 12:
        raise ValueError(f"Expected exactly twelve unchanged Fortran program units, got {len(starts)}")
    unitdir = output.parent / "units"
    unitdir.mkdir(exist_ok=True)
    objs = []
    for i, start in enumerate(starts):
        unit = unitdir / f"unit_{i:02d}.f"
        obj = unit.with_suffix(".o")
        unit.write_bytes(b"".join(lines[start:starts[i+1] if i + 1 < len(starts) else len(lines)]))
        subprocess.run(["gfortran", "-O2", "-fPIC", "-c", str(unit), "-o", str(obj)], check=True, capture_output=True)
        objs.append(str(obj))
    subprocess.run(["gfortran", "-shared", *objs, "-llapack", "-lblas", "-o", str(output)], check=True, capture_output=True)
    return output


class NativePES:
    def __init__(self, path: pathlib.Path | None = None):
        self.lib = C.CDLL(str(path or ROOT / "build" / "libvelilla2008.so"))
        self.lib.h2_.argtypes = [C.POINTER(C.c_double)]
        self.lib.h2_.restype = C.c_double
        self.lib.dimh3p_.argtypes = [C.POINTER(C.c_double)] * 6
        self.lib.dimh3p_.restype = None

    def h2(self, r: float) -> float:
        return float(self.lib.h2_(C.byref(C.c_double(r))))

    def dimh3p(self, r1: float, r2: float, r3: float) -> tuple[float, float, float]:
        if min(r1, r2, r3) <= 0 or min(r1+r2-r3, r1+r3-r2, r2+r3-r1) <= 1e-10:
            raise ValueError("Triangle must be strictly nondegenerate with positive separations")
        vals = [C.c_double(x) for x in [r1, r2, r3, 0., 0., 0.]]
        self.lib.dimh3p_(*[C.byref(v) for v in vals])
        return (vals[3].value, vals[4].value, vals[5].value)
