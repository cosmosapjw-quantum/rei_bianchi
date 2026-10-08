"""Pure exact-binary arithmetic witnesses; no provider, observer or evolution."""
import json
import math
import struct
from decimal import Decimal, localcontext
from fractions import Fraction as F


def decimal(q):
    with localcontext() as ctx:
        ctx.prec = 80
        return str(Decimal(q.numerator) / Decimal(q.denominator))


def main():
    eps = 1.602176634e-12
    chi = 13.598434599702
    a = 2.5091851155235384e-296
    b = 5.5049080207218545e-307
    rounded_threshold = eps * chi * a
    heat = b - rounded_threshold
    bits = struct.pack(">d", heat).hex()
    exact_heat = F(b) - F(eps) * F(chi) * F(a)
    assert bits == "0002bdc74d339a20"
    assert exact_heat > 0 and heat > 0 and math.isfinite(heat)
    assert F(heat) == F(b) - F(rounded_threshold)
    normal_min = float.fromhex("0x1p-1022")
    assert 0 < heat < normal_min < heat / eps

    n = 3.05511443136939113e-301
    factor = 2.1938860412919833e-11
    u = factor * n
    kernel_product_error = abs(F(factor) * F(n) - F(u))
    wrapper_bound = F(1, 2**1085)
    assert u == 6.70257290553098821e-312
    assert kernel_product_error > wrapper_bound

    tiny_n = math.ldexp(1.0, -1064)
    assert tiny_n > 0 and eps * 13.7 * tiny_n == 0
    assert F(eps) * F(13.7) * F(tiny_n) > 0
    print(json.dumps({
        "status": "PASS_EXACT_FINITE_ARITHMETIC_WITNESSES",
        "heat_bits": bits,
        "heat_exact": decimal(exact_heat),
        "heat_arithmetic_defect": decimal(abs(F(heat)-exact_heat)),
        "final_rounded_operand_subtraction_exact": True,
        "kernel_U_product_error": decimal(kernel_product_error),
        "postkernel_wrapper_bound": decimal(wrapper_bound),
        "error_over_wrapper_bound": decimal(kernel_product_error/wrapper_bound),
        "future_N_positive_U_zero_witness": True,
        "upstream_kernel_provider_error": "NOT_INCLUDED",
        "extra_provider_observer_RHS_advance_calls": [0, 0, 0, 0],
    }, indent=2))


if __name__ == "__main__":
    main()
