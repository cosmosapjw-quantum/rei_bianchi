"""Exact-dyadic fixed-cell replay. No native solver or external access.

Reads a retained native diagnostic vector and creates a separate assessment.
The optional candidate cap bounds this diagnostic only; exhaustion is reported
distinctly and is never taken as a proof that no admissible correction exists.
"""
import argparse
from fractions import Fraction
import hashlib
import heapq
import json
import math
from pathlib import Path
import struct

def ticks(x):
    return 0 if x == 0.0 else struct.unpack(">Q", struct.pack(">d", x))[0]

def from_ticks(t):
    return struct.unpack(">d", struct.pack(">Q", t))[0]

def original_sum(values):
    total = correction = 0.0
    for value in values:
        y = value - correction
        nxt = total + y
        correction = (nxt-total)-y
        total = nxt
    return total

def assess(path, max_candidates):
    payload = path.read_bytes()
    raw = json.loads(payload)
    cell = raw["diagnostics"][0] if "diagnostics" in raw else raw["cell"]
    rows = cell["nodes_q_probability_number"]
    qf = [row[0] for row in rows]
    q = [Fraction(x) for x in qf]
    old = [ticks(row[2]) for row in rows]
    T, U, tau = ticks(cell["n"]), ticks(cell["u"]), ticks(cell["energy_tolerance"])
    eps = 2.0**-52
    assert 64*eps*cell["n"] == cell["count_tolerance"]
    assert 128*eps*max(abs(cell["u"]), cell["n"]*(cell["hi"]-cell["lo"])) == cell["energy_tolerance"]
    assert 0 < T < 2**52 and 0 <= U < 2**52
    assert all(x > 0 and math.isfinite(float(x)) for x in q)
    assert all(math.isfinite(row[2]) and row[2] >= 0 and 0 <= t < 2**52
               for row, t in zip(rows, old))
    margin = 2**52 - (max(q)*max(T, sum(old)) + Fraction(len(q), 2))
    assert margin > 0, "EXACT_SUBNORMAL_ENERGY_LEMMA_OUTSIDE_DOMAIN"
    delta = T-sum(old)
    largest = max(range(len(old)), key=lambda i: old[i])
    base = old.copy()
    base[largest] += delta
    assert 0 < base[largest] < 2**52 and sum(base) == T
    rounded = lambda qi, ti: round(qi*ti)
    base_terms = [rounded(qi, ti) for qi, ti in zip(q, base)]
    E = sum(base_terms)
    real = lambda ts: sum((qi*ti for qi, ti in zip(q, ts)), Fraction())
    products_match = all(ticks(qi*from_ticks(ti)) == rounded(qj, ti)
                         for qi, qj, ti in zip(qf, q, base))
    assert products_match
    assert ticks(original_sum(qi*from_ticks(ti) for qi, ti in zip(qf, base))) == E
    heap = []
    all_pairs = nonempty = k1_passes = 0
    for a, ta in enumerate(base):
        if ta < 2:
            continue
        for b, tb in enumerate(base):
            if a == b or tb < 1:
                continue
            all_pairs += 1
            C = E-base_terms[a]-base_terms[b]
            if abs(C+rounded(q[a], ta-1)+rounded(q[b], tb+1)-U) <= tau:
                k1_passes += 1
            A = Fraction(C-U)+q[a]*ta+q[b]*tb
            D = q[b]-q[a]
            if D:
                endpoints = sorted(((-tau-1-A)/D, (tau+1-A)/D))
                low = max(1, math.ceil(endpoints[0]))
                high = min(ta-1, math.floor(endpoints[1]))
            else:
                low, high = (1, ta-1) if abs(A) <= tau+1 else (1, 0)
            if low <= high:
                heapq.heappush(heap, (low, a, b, high, C))
                nonempty += 1
    checks = 0
    found = None
    if abs(E-U) <= tau:
        status = "EXACT_COUNT_BASE_ALREADY_PASSES"
        corrected = base
    else:
        while heap and checks < max_candidates:
            k, a, b, high, C = heapq.heappop(heap)
            checks += 1
            energy = C+rounded(q[a], base[a]-k)+rounded(q[b], base[b]+k)
            if abs(energy-U) <= tau:
                corrected = base.copy()
                corrected[a] -= k
                corrected[b] += k
                found = dict(donor=a, receiver=b, transfer_ticks=k,
                    donor_q_ratio=str(q[a]), receiver_q_ratio=str(q[b]),
                    donor_base_ticks=base[a], receiver_base_ticks=base[b],
                    donor_after_ticks=corrected[a], receiver_after_ticks=corrected[b],
                    energy_after_ticks=energy, pair_interval_upper=high,
                    fixed_energy_response_delta_ticks=str(k*(q[b]-q[a])))
                status = "MINIMUM_SINGLE_PAIR_K_FOUND"
                break
            if k < high:
                heapq.heappush(heap, (k+1, a, b, high, C))
        else:
            corrected = None
            status = ("SEARCH_BUDGET_EXHAUSTED_NO_FEASIBILITY_CLAIM"
                      if heap else "COMPLETE_SINGLE_PAIR_INTERVAL_SEARCH_NO_SOLUTION")
    def signed_machine_energy(ts):
        return ticks(original_sum(qi*from_ticks(ti) for qi, ti in zip(qf, ts)))-U
    result = dict(schema="REI_EXACT_DYADIC_PAIR_REPLAY_V1",
        input_path=str(path), input_sha256=hashlib.sha256(payload).hexdigest(),
        T=T, U=U, energy_tolerance_ticks=tau,
        count_tolerance_ticks=ticks(cell["count_tolerance"]),
        exact_subnormal_energy_margin_ticks=str(margin),
        actual_rounded_products_equal_exact_dyadic_ties_even=products_match,
        original=dict(count_signed_defect_ticks=sum(old)-T,
            stored_energy_signed_defect_ticks=signed_machine_energy(old),
            real_energy_signed_defect_ticks=str(real(old)-U),
            real_energy_signed_defect_ticks_approx=float(real(old)-U)),
        exact_count_base=dict(index=largest, signed_count_correction_ticks=delta,
            count_signed_defect_ticks=sum(base)-T,
            stored_energy_signed_defect_ticks=signed_machine_energy(base),
            real_energy_signed_defect_ticks=str(real(base)-U),
            real_energy_signed_defect_ticks_approx=float(real(base)-U)),
        candidate_search=dict(status=status, directed_pairs=all_pairs,
            nonempty_exact_intervals=nonempty, k1_successes=k1_passes,
            max_candidates=max_candidates, exact_candidates_tested=checks,
            order="increasing (k,donor,receiver)", candidate=found),
        scientific_admission="NOT_ISSUED",
        claim_scope="Retained fixed cell only; no full solver execution")
    if corrected is not None:
        count = original_sum(from_ticks(t) for t in corrected)
        energy = original_sum(qi*from_ticks(t) for qi, t in zip(qf, corrected))
        result["corrected"] = dict(
            count_signed_defect_ticks=sum(corrected)-T,
            stored_energy_signed_defect_ticks=ticks(energy)-U,
            real_energy_signed_defect_ticks=str(real(corrected)-U),
            real_energy_signed_defect_ticks_approx=float(real(corrected)-U),
            original_count_gate=abs(count-cell["n"]) <= cell["count_tolerance"],
            original_energy_gate=abs(energy-cell["u"]) <= cell["energy_tolerance"],
            L1_from_base_ticks=sum(abs(a-b) for a,b in zip(corrected, base)),
            L1_from_original_ticks=sum(abs(a-b) for a,b in zip(corrected, old)),
            support_unchanged=all((a>0)==(b>0) for a,b in zip(corrected, old)),
            node_bits_unchanged=True)
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-candidates", type=int, default=100000)
    args = parser.parse_args()
    if args.max_candidates <= 0:
        parser.error("positive candidate budget required")
    result = assess(args.input, args.max_candidates)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["candidate_search"]["status"],
        "checks": result["candidate_search"]["exact_candidates_tested"],
        "candidate": result["candidate_search"]["candidate"],
        "corrected": result.get("corrected")}, indent=2))

if __name__ == "__main__":
    main()

