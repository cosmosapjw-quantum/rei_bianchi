#!/usr/bin/env python3
"""Independent exact-rational corner oracle for the compiled Rust ABI.

Python is used here only as a validation driver.  The production numerical
path remains the Rust/MPFR library.
"""

from __future__ import annotations

import ctypes
from fractions import Fraction
from itertools import product
from pathlib import Path
import random
import sys


def _array(values):
    return (ctypes.c_double * len(values))(*map(float, values))


def _solve_two_by_two(matrix, rhs):
    determinant = matrix[0] * matrix[3] - matrix[1] * matrix[2]
    return (
        (rhs[0] * matrix[3] - matrix[1] * rhs[1]) / determinant,
        (matrix[0] * rhs[1] - rhs[0] * matrix[2]) / determinant,
    )


def _load(library_path: Path):
    library = ctypes.CDLL(str(library_path.resolve()))
    pointer = ctypes.POINTER(ctypes.c_double)
    function = library.rei_certify_linear_mpfr256
    function.argtypes = [ctypes.c_size_t] * 3 + [pointer] * 17 + [
        ctypes.POINTER(ctypes.c_uint32)
    ]
    function.restype = ctypes.c_int
    return function


def _verify_family(function, a_lower, a_upper, b_lower, b_upper) -> int:
    a_lower_ffi = _array(a_lower)
    a_upper_ffi = _array(a_upper)
    b_lower_ffi = _array(b_lower)
    b_upper_ffi = _array(b_upper)
    candidate_lower = _array([-4, -4])
    candidate_upper = _array([4, 4])
    outputs = [_array([99, 99]) for _ in range(7)]
    outputs.extend([_array([99] * 4), _array([99]), _array([99, 99]), _array([99, 99])])
    iterations = ctypes.c_uint32(99)
    status = function(
        2,
        4,
        2,
        a_lower_ffi,
        a_upper_ffi,
        b_lower_ffi,
        b_upper_ffi,
        candidate_lower,
        candidate_upper,
        *outputs,
        ctypes.byref(iterations),
    )
    if status != 0:
        raise AssertionError(f"Rust certificate status {status}")
    if list(outputs[0]) != [-4, -4] or list(outputs[1]) != [4, 4]:
        raise AssertionError("supplied candidate was not preserved")
    if iterations.value != 1:
        raise AssertionError("supplied candidate must be a one-image proof")

    krawczyk_lower = list(outputs[2])
    krawczyk_upper = list(outputs[3])
    checked = 0
    for matrix_bits in product((0, 1), repeat=4):
        matrix = [
            (a_upper if bit else a_lower)[index]
            for index, bit in enumerate(matrix_bits)
        ]
        for rhs_bits in product((0, 1), repeat=2):
            rhs = [
                (b_upper if bit else b_lower)[index]
                for index, bit in enumerate(rhs_bits)
            ]
            solution = _solve_two_by_two(matrix, rhs)
            for index in range(2):
                lower = Fraction.from_float(krawczyk_lower[index])
                upper = Fraction.from_float(krawczyk_upper[index])
                if not lower <= solution[index] <= upper:
                    raise AssertionError(
                        "under-enclosure at component "
                        f"{index}: {solution[index]} not in [{lower}, {upper}]"
                    )
            checked += 1
    return checked


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_fraction_corners.py LIBRARY")
    function = _load(Path(sys.argv[1]))
    generator = random.Random(0x524549)
    checked = 0
    for _ in range(96):
        centers = [
            Fraction(generator.randint(28, 36), 16),
            Fraction(generator.randint(-4, 4), 16),
            Fraction(generator.randint(-4, 4), 16),
            Fraction(generator.randint(44, 52), 16),
        ]
        radii = [Fraction(1, 32), Fraction(1, 64), Fraction(1, 64), Fraction(1, 32)]
        a_lower = [value - radius for value, radius in zip(centers, radii)]
        a_upper = [value + radius for value, radius in zip(centers, radii)]
        rhs_centers = [
            Fraction(generator.randint(-16, 16), 16),
            Fraction(generator.randint(-16, 16), 16),
        ]
        rhs_radii = [Fraction(1, 32), Fraction(1, 32)]
        b_lower = [value - radius for value, radius in zip(rhs_centers, rhs_radii)]
        b_upper = [value + radius for value, radius in zip(rhs_centers, rhs_radii)]
        checked += _verify_family(function, a_lower, a_upper, b_lower, b_upper)
    print(f"fraction_corner_oracle=PASS families=96 corner_systems={checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
