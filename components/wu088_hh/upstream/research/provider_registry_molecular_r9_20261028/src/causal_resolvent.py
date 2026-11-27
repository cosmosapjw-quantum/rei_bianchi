"""R9 causal positive cell resolvent; saved certified factors are inputs.

This module checks finite domains and metadata consistency. The caller must
establish the actual kernel, factor, and cap inequalities from the identified
source. It does not manufacture those certificates or evaluate an old producer.
"""
from __future__ import annotations
from fractions import Fraction
import re

BITS = 128
SCALE = 1 << BITS
MAX_CELLS = 192
MAX_INTEGER_BITS = 8192
R8_PRIMARY_SHA256 = "520110d1cae1677491aecd7216621c25f1098470c939ee027d5df3bde183686b"

class DomainError(ValueError):
    pass

def Q(value):
    if isinstance(value, (bool, float)) or not isinstance(value, (int, str, Fraction)):
        raise DomainError("Require exact integer, bounded numeric string or Fraction")
    if isinstance(value, str) and (len(value) > 6000 or "e" in value.lower()):
        raise DomainError("Exact scalar text is outside the finite domain")
    try:
        q = Fraction(value)
    except (ValueError, ZeroDivisionError, TypeError) as exc:
        raise DomainError("Invalid exact scalar") from exc
    if max(abs(q.numerator).bit_length(), q.denominator.bit_length()) > MAX_INTEGER_BITS:
        raise DomainError("Exact scalar exceeds 8192-bit input domain")
    return q

def export(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): export(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [export(v) for v in value]
    return value

def up(q):
    q = Fraction(q)
    if q < 0:
        raise DomainError("Positive upper arithmetic received a negative value")
    n = -((-q.numerator * SCALE) // q.denominator)
    if n.bit_length() > MAX_INTEGER_BITS:
        raise DomainError("Dyadic output exceeds the finite arithmetic domain")
    return Fraction(n, SCALE)

def _seq(values, size, label):
    if not isinstance(values, (tuple, list)) or len(values) != size:
        raise DomainError(label + " has wrong shape")
    return values

def _vec(values, size, label, nonnegative=True):
    out = tuple(Q(x) for x in _seq(values, size, label))
    if nonnegative and any(x < 0 for x in out):
        raise DomainError(label + " must be nonnegative")
    return out

def _sha(value):
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise DomainError("Require lowercase SHA256 identity")
    return value

def _binding(value):
    if not isinstance(value, dict):
        raise DomainError("Require an explicit nominal-family binding")
    out = {}
    for key in ("clock", "family_id"):
        if not isinstance(value.get(key), str) or not value[key].strip():
            raise DomainError("Missing " + key)
        out[key] = value[key]
    ids = value.get("state_ids")
    if not isinstance(ids, (list, tuple)) or not 1 <= len(ids) <= 16:
        raise DomainError("Require 1..16 ordered state identifiers")
    if any(not isinstance(x, str) or not x for x in ids) or len(set(ids)) != len(ids):
        raise DomainError("State identifiers must be distinct nonempty strings")
    out["state_ids"] = tuple(ids)
    out["source_sha256"] = _sha(value.get("source_sha256"))
    for key, expected in (("norm", "l1_on_kerP"), ("generator_scope", "nominal_K")):
        if value.get(key) != expected:
            raise DomainError("Incompatible " + key)
        out[key] = expected
    for key in ("uniform_all_starts", "nonexpansive", "same_family_composition"):
        if value.get(key) is not True:
            raise DomainError("Missing certified premise " + key)
        out[key] = True
    return out

def _caps(record, kind, count, delta, cells, binding):
    if record is None:
        return None
    if not isinstance(record, dict) or record.get("source_kind") != "saved_R8_" + kind:
        raise DomainError("Wrong cap kind")
    if _sha(record.get("source_sha256")) != R8_PRIMARY_SHA256:
        raise DomainError("Cap source differs from frozen R8 primary")
    pointer = record.get("source_pointer")
    pattern = r"/(?:hd_cases/[0-3]|controls/[0-4])/certificate/" + kind
    if not isinstance(pointer, str) or re.fullmatch(pattern, pointer) is None:
        raise DomainError("Cap pointer does not identify the prescribed saved array")
    if Q(record.get("delta")) != delta or type(record.get("cells")) is not int or record["cells"] != cells:
        raise DomainError("Cap grid differs from the common exact clock")
    if _binding(record.get("binding")) != binding:
        raise DomainError("Cap family/clock/state binding differs")
    return tuple(_vec(row, 2, "cap upper") for row in _seq(record.get("upper"), count, "cap array"))

def sweep(B, g, delta, initial, kernel, coarse_factors, *, binding,
          whole_caps=None, point_caps=None, bits=128):
    """One causal sweep. Minima of valid bounds stay exact, without rerounding.

    For a raw result no earlier whole-trajectory envelope is required. For a
    capped result the caller additionally proves each source-backed cap on its
    exact closed cell or grid point. Rounded outputs need not be discrete
    supersolutions. Raw dominance over an arbitrary older bound is not assumed.
    """
    if type(bits) is not int or bits != BITS:
        raise DomainError("This contract fixes 128 dyadic bits")
    _seq(B, 2, "B")
    first = _vec(B[0], 2, "B row", nonnegative=False)
    second = _vec(B[1], 2, "B row", nonnegative=False)
    a, b, c, d = first[0], first[1], second[0], second[1]
    if min(a, b, c) < 0:
        raise DomainError("a,b,c must be nonnegative")
    gr, ge = _vec(g, 2, "g")
    R0, E0 = _vec(initial, 2, "initial")
    delta = Q(delta)
    if delta <= 0 or abs(d) * delta > 16:
        raise DomainError("Require delta>0 and abs(d*delta)<=16")
    common = _binding(binding)
    if not isinstance(kernel, dict) or _binding(kernel.get("binding")) != common:
        raise DomainError("Kernel binding differs")
    cells = kernel.get("cells")
    if type(cells) is not int or not 1 <= cells <= MAX_CELLS:
        raise DomainError("Require 1..192 cells")
    if Q(kernel.get("delta")) != delta or type(kernel.get("bits")) is not int or kernel["bits"] != BITS:
        raise DomainError("Kernel grid/precision differs")
    h = _vec(kernel.get("h"), cells + 1, "kernel")
    if h[0] != 1 or any(x > 1 for x in h) or any(h[n + 1] > h[n] for n in range(cells)):
        raise DomainError("Require h0=1 and nonincreasing h in [0,1]")
    if not isinstance(coarse_factors, dict):
        raise DomainError("Require certified scalar factor record")
    f = coarse_factors
    if Q(f.get("d")) != d or Q(f.get("delta")) != delta or type(f.get("bits")) is not int or f["bits"] != BITS:
        raise DomainError("Scalar factors have wrong d/grid/precision")
    e, phi = Q(f.get("e_upper")), Q(f.get("phi_upper"))
    if e <= 0 or phi <= 0:
        raise DomainError("Scalar upper factors must be positive")
    if (d <= 0 and e > 1) or (d == 0 and (e != 1 or phi < delta)) or (d > 0 and (e < 1 or phi < delta)):
        raise DomainError("Scalar upper factors contradict elementary sign/domain conditions")
    wc = _caps(whole_caps, "whole_cells", cells, delta, cells, common)
    pc = _caps(point_caps, "endpoints", cells + 1, delta, cells, common)
    D = 1 - delta * a - delta * b * phi * c
    if D <= 0:
        raise DomainError("The exact cell-resolvent determinant must be positive")
    powers = [Fraction(1)]
    for _ in range(cells):
        powers.append(up(powers[-1] * e))
    raw_whole, whole, F, L, A_bases, B_bases = [], [], [], [], [], []
    raw_ends = [(R0, E0)]
    ends = [tuple(min(x, pc[0][k]) if pc is not None else x for k, x in enumerate((R0, E0)))]
    for n in range(cells):
        A = up(h[n] * R0 + delta * sum((h[n-j-1] * F[j] for j in range(n)), Fraction(0)) + delta * gr)
        p0, shift = (n, 1) if d <= 0 else (n + 1, 0)
        Bb = up(powers[p0] * E0 + phi * sum((powers[n-j-shift] * L[j] for j in range(n)), Fraction(0)) + phi * ge)
        # D is exact: never replace this denominator by an upper rounding.
        rawR = up((A + delta * b * Bb) / D)
        rawE = up(Bb + phi * c * rawR)
        raw_whole.append((rawR, rawE))
        pair = tuple(min(x, wc[n][k]) if wc is not None else x for k, x in enumerate((rawR, rawE)))
        whole.append(pair)
        A_bases.append(A); B_bases.append(Bb)
        F.append(up(a * pair[0] + b * pair[1] + gr))
        L.append(up(c * pair[0] + ge))
        rr = up(h[n+1] * R0 + delta * sum((h[n-j] * F[j] for j in range(n+1)), Fraction(0)))
        ee = up(powers[n+1] * E0 + phi * sum((powers[n-j] * L[j] for j in range(n+1)), Fraction(0)))
        raw_ends.append((rr, ee))
        ep = tuple(min(x, pair[k]) for k, x in enumerate((rr, ee)))
        if pc is not None:
            ep = tuple(min(x, pc[n+1][k]) for k, x in enumerate(ep))
        ends.append(ep)
    return {"schema":"WU_R9_CAUSAL_CELL_SWEEP_V1", "mode":"capped" if wc is not None or pc is not None else "raw",
            "B":(first,second), "g":(gr,ge), "delta":delta, "cells":cells, "initial":(R0,E0), "binding":common,
            "e_upper":e, "phi_upper":phi, "D":D, "powers":powers, "A_base":A_bases, "B_base":B_bases,
            "raw_whole_cells":raw_whole, "whole_cells":whole, "raw_endpoints":raw_ends, "endpoints":ends,
            "F_upper":F, "L_upper":L, "rounding":"exact rational sums followed by stated upward dyadic128 scalars; exact cap minima",
            "certificate_validity":"external source premise; metadata/finite-domain consistency checked here",
            "physical_consumer_admitted":False, "new_generator_or_ODE_calls":0}
