"""Opt-in exact dyadic intervals for fixed-support subnormal pair transfers.

The 65536-candidate ceiling is a computation budget, never a feasibility test.
Only original failed gates are instrumented; every accepted vector passes both
unchanged compensated-sum gates. Minimum k is relative to one fixed count base
and a single pair, not arbitrary multi-pair corrections.
"""
import hashlib

from moment_fit_diagnostic import ANCHOR, ORIGINAL_BLOB
from subnormal_count_rounding import CANDIDATE_HELPER
from subnormal_moment_rounding import PAIR_HELPER


SEARCH_HELPER = r'''
        const REI_PAIR_SEARCH_MAX_EVALUATIONS: usize = 65536;
        struct ReiSubnormalSearchRepair {
            repair: ReiSubnormalPairRepair,
            k: u64,
            evaluations: usize,
            intervals: usize,
            pair_base_bits: Option<(u64, u64)>,
        }
        enum ReiSubnormalSearchOutcome {
            Found(ReiSubnormalSearchRepair),
            Budget { next_k: u64, evaluations: usize, intervals: usize },
            NoSolution { evaluations: usize, intervals: usize },
        }
        fn rei_checked_positive_shift(value: i128, shift: u32) -> Result<i128, &'static str> {
            if value < 0 || shift >= 127 || value > (i128::MAX >> shift) {
                return Err("I128_SHIFT_OVERFLOW");
            }
            Ok(value << shift)
        }
        fn rei_floor_div(n: i128, d: i128) -> Result<i128, &'static str> {
            if d <= 0 { return Err("DIVISOR_DOMAIN"); }
            (n / d).checked_sub(if n % d < 0 { 1 } else { 0 }).ok_or("I128_OVERFLOW")
        }
        fn rei_ceil_div(n: i128, d: i128) -> Result<i128, &'static str> {
            if d <= 0 { return Err("DIVISOR_DOMAIN"); }
            (n / d).checked_add(if n % d > 0 { 1 } else { 0 }).ok_or("I128_OVERFLOW")
        }
        fn rei_signed_interval(b0: i128, b1: i128, radius: i128,
            upper: i128) -> Result<Option<(u64, u64)>, &'static str> {
            if radius < 0 { return Err("INTERVAL_DOMAIN"); }
            let neg_radius = radius.checked_neg().ok_or("I128_OVERFLOW")?;
            let (low, high) = if b1 > 0 {
                (rei_ceil_div(neg_radius.checked_sub(b0).ok_or("I128_OVERFLOW")?, b1)?,
                 rei_floor_div(radius.checked_sub(b0).ok_or("I128_OVERFLOW")?, b1)?)
            } else if b1 < 0 {
                let slope = b1.checked_neg().ok_or("I128_OVERFLOW")?;
                (rei_ceil_div(b0.checked_sub(radius).ok_or("I128_OVERFLOW")?, slope)?,
                 rei_floor_div(b0.checked_add(radius).ok_or("I128_OVERFLOW")?, slope)?)
            } else if b0 >= neg_radius && b0 <= radius { (1, upper) }
            else { return Ok(None); };
            let low = low.max(1);
            let high = high.min(upper);
            if low > high { return Ok(None); }
            Ok(Some((u64::try_from(low).map_err(|_| "INTEGER_RANGE")?,
                     u64::try_from(high).map_err(|_| "INTEGER_RANGE")?)))
        }
        fn rei_subnormal_value_ticks(value: f64) -> Result<i128, &'static str> {
            if !(value.is_finite() && value >= 0.0 && (value == 0.0 || value.is_subnormal())) {
                return Err("ENERGY_TICK_DOMAIN_UNSUPPORTED");
            }
            Ok(if value == 0.0 { 0 } else { value.to_bits() as i128 })
        }
        fn rei_round_dyadic_product(a: i128, ticks: i128, denominator: i128)
            -> Result<i128, &'static str> {
            let product = a.checked_mul(ticks).ok_or("I128_OVERFLOW")?;
            let quotient = product / denominator;
            let twice_remainder = (product % denominator).checked_mul(2).ok_or("I128_OVERFLOW")?;
            quotient.checked_add(if twice_remainder > denominator
                || (twice_remainder == denominator && quotient % 2 != 0) { 1 } else { 0 })
                .ok_or("I128_OVERFLOW")
        }
        fn rei_subnormal_pair_search(n: f64, u: f64, energy_scale: f64,
            nodes: &[(f64, f64)], budget: usize)
            -> Result<ReiSubnormalSearchOutcome, &'static str> {
            if !(n > 0.0 && n.is_subnormal()) || nodes.is_empty() {
                return Err("COUNT_DOMAIN_UNSUPPORTED");
            }
            let mut total = 0_u128;
            for &(q, number) in nodes {
                if !(q.is_finite() && q > 0.0 && number.is_finite() && number >= 0.0
                    && (number == 0.0 || number.is_subnormal())) {
                    return Err("STORED_NODE_DOMAIN_UNSUPPORTED");
                }
                total = total.checked_add(rei_subnormal_ticks(number)).ok_or("U128_OVERFLOW")?;
            }
            let target = n.to_bits() as u128;
            let (base, count_index, count_distance) = if total == target {
                (nodes.to_vec(), None, 0)
            } else {
                let (fixed, index, _, _, distance) = rei_subnormal_count_candidate(n, nodes)
                    .ok_or("EXACT_COUNT_BASE_UNAVAILABLE")?;
                (fixed, Some(index), distance)
            };
            let count_tolerance = 64.0 * f64::EPSILON * n;
            let energy_tolerance = 128.0 * f64::EPSILON * energy_scale;
            let passes = |candidate: &[(f64, f64)]| {
                (sum(candidate.iter().map(|x| x.1)) - n).abs() <= count_tolerance
                && (sum(candidate.iter().map(|x| x.0 * x.1)) - u).abs() <= energy_tolerance
            };
            if passes(&base) {
                return Ok(ReiSubnormalSearchOutcome::Found(ReiSubnormalSearchRepair {
                    repair: ReiSubnormalPairRepair {
                        l1_ticks: rei_subnormal_l1(nodes, &base), nodes: base,
                        count_index, pair: None, before_ticks: total, after_ticks: target,
                        count_distance,
                    }, k: 0, evaluations: 0, intervals: 0, pair_base_bits: None,
                }));
            }
            // The general pair search requires an exact subnormal energy lattice.
            rei_subnormal_value_ticks(count_tolerance)?;
            let energy_target = rei_subnormal_value_ticks(u)?;
            let tau = rei_subnormal_value_ticks(energy_tolerance)?;
            let mut parts = Vec::with_capacity(base.len());
            let mut denominator_shift = 0_u32;
            for &(q, _) in &base {
                if !q.is_normal() { return Err("Q_REPRESENTATION_UNSUPPORTED"); }
                let bits = q.to_bits();
                let exponent = ((bits >> 52) & 0x7ff) as i32 - 1023 - 52;
                let significand = ((bits & ((1_u64 << 52) - 1)) | (1_u64 << 52)) as i128;
                denominator_shift = denominator_shift.max((-exponent).max(0) as u32);
                parts.push((significand, exponent));
            }
            let denominator = rei_checked_positive_shift(1, denominator_shift)?;
            let mut coefficients = Vec::with_capacity(base.len());
            for (significand, exponent) in parts {
                let shift = exponent + denominator_shift as i32;
                let shift = u32::try_from(shift).map_err(|_| "Q_REPRESENTATION_UNSUPPORTED")?;
                coefficients.push(rei_checked_positive_shift(significand, shift)?);
            }
            let max_coefficient = *coefficients.iter().max().ok_or("Q_REPRESENTATION_UNSUPPORTED")?;
            let t = i128::try_from(target).map_err(|_| "INTEGER_RANGE")?;
            let twice_bound = max_coefficient.checked_mul(t).and_then(|v| v.checked_mul(2))
                .and_then(|v| (base.len() as i128).checked_mul(denominator).and_then(|m| v.checked_add(m)))
                .ok_or("I128_OVERFLOW")?;
            let twice_normal = (1_i128 << 53).checked_mul(denominator).ok_or("I128_OVERFLOW")?;
            if twice_bound >= twice_normal { return Err("SUBNORMAL_ENERGY_BOUND_UNSUPPORTED"); }
            let mut terms = Vec::with_capacity(base.len());
            let mut energy = 0_i128;
            for (i, &(q, number)) in base.iter().enumerate() {
                let term = rei_subnormal_value_ticks(q * number)?;
                let exact = rei_round_dyadic_product(coefficients[i], rei_subnormal_ticks(number) as i128, denominator)?;
                if term != exact { return Err("RN_PRODUCT_IDENTITY_UNSUPPORTED"); }
                energy = energy.checked_add(term).ok_or("I128_OVERFLOW")?;
                terms.push(term);
            }
            if rei_subnormal_value_ticks(sum(base.iter().map(|x| x.0 * x.1)))? != energy {
                return Err("SUBNORMAL_SUM_IDENTITY_UNSUPPORTED");
            }
            let radius = tau.checked_add(1).and_then(|v| v.checked_mul(denominator)).ok_or("I128_OVERFLOW")?;
            let mut heap = std::collections::BinaryHeap::new();
            let mut intervals = 0_usize;
            for donor in 0..base.len() {
                let donor_ticks = rei_subnormal_ticks(base[donor].1) as i128;
                if donor_ticks < 2 { continue; }
                for receiver in 0..base.len() {
                    let receiver_ticks = rei_subnormal_ticks(base[receiver].1) as i128;
                    if donor == receiver || receiver_ticks < 1 { continue; }
                    let upper = (donor_ticks - 1).min(((1_i128 << 52) - 1) - receiver_ticks);
                    let c = energy.checked_sub(terms[donor]).and_then(|v| v.checked_sub(terms[receiver])).ok_or("I128_OVERFLOW")?;
                    let b0 = c.checked_sub(energy_target).and_then(|v| v.checked_mul(denominator))
                        .and_then(|v| coefficients[donor].checked_mul(donor_ticks).and_then(|a| v.checked_add(a)))
                        .and_then(|v| coefficients[receiver].checked_mul(receiver_ticks).and_then(|b| v.checked_add(b)))
                        .ok_or("I128_OVERFLOW")?;
                    let b1 = coefficients[receiver].checked_sub(coefficients[donor]).ok_or("I128_OVERFLOW")?;
                    if let Some((low, high)) = rei_signed_interval(b0, b1, radius, upper)? {
                        heap.push(std::cmp::Reverse((low, donor, receiver, high)));
                        intervals += 1;
                    }
                }
            }
            let mut evaluations = 0_usize;
            while let Some(&std::cmp::Reverse((next_k, _, _, _))) = heap.peek() {
                if evaluations >= budget {
                    return Ok(ReiSubnormalSearchOutcome::Budget { next_k, evaluations, intervals });
                }
                let std::cmp::Reverse((k, donor, receiver, high)) = heap.pop().unwrap();
                evaluations += 1;
                let donor_bits = base[donor].1.to_bits();
                let receiver_bits = base[receiver].1.to_bits();
                let mut candidate = base.clone();
                candidate[donor].1 = f64::from_bits(donor_bits - k);
                candidate[receiver].1 = f64::from_bits(receiver_bits + k);
                if passes(&candidate) {
                    return Ok(ReiSubnormalSearchOutcome::Found(ReiSubnormalSearchRepair {
                        repair: ReiSubnormalPairRepair {
                            l1_ticks: rei_subnormal_l1(nodes, &candidate), nodes: candidate,
                            count_index, pair: Some((donor, receiver)), before_ticks: total,
                            after_ticks: target, count_distance,
                        }, k, evaluations, intervals, pair_base_bits: Some((donor_bits, receiver_bits)),
                    }));
                }
                if k < high { heap.push(std::cmp::Reverse((k + 1, donor, receiver, high))); }
            }
            Ok(ReiSubnormalSearchOutcome::NoSolution { evaluations, intervals })
        }
'''.encode()

SEARCH_REPAIR = r'''
        if n > 0.0 && n.is_subnormal() && eval(lambda).1.abs() < 8.0 * f64::EPSILON {
            match rei_subnormal_pair_search(n, u, energy_scale, &result, REI_PAIR_SEARCH_MAX_EVALUATIONS) {
                Ok(ReiSubnormalSearchOutcome::Found(found)) => {
                    let repair = found.repair;
                    let corrected_count_defect = (sum(repair.nodes.iter().map(|x| x.1)) - n).abs();
                    let corrected_energy_defect = (sum(repair.nodes.iter().map(|x| x.0 * x.1)) - u).abs();
                    static REI_SEARCH_COUNT_REPORTED: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);
                    static REI_SEARCH_PAIR_REPORTED: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);
                    let (mode, reported) = if repair.pair.is_some() {
                        ("pair-search", &REI_SEARCH_PAIR_REPORTED)
                    } else { ("count-only", &REI_SEARCH_COUNT_REPORTED) };
                    if !reported.swap(true, std::sync::atomic::Ordering::Relaxed) {
                        let pair_json = if let Some((donor, receiver)) = repair.pair {
                            let (donor_base, receiver_base) = found.pair_base_bits.unwrap();
                            format!("{{\"donor\":{},\"receiver\":{},\"donor_q\":{:.17e},\"receiver_q\":{:.17e},\"donor_base_bits\":\"{}\",\"receiver_base_bits\":\"{}\",\"donor_after_bits\":\"{}\",\"receiver_after_bits\":\"{}\"}}", donor, receiver, result[donor].0, result[receiver].0, donor_base, receiver_base, repair.nodes[donor].1.to_bits(), repair.nodes[receiver].1.to_bits())
                        } else { "null".to_string() };
                        eprintln!("REI_SUBNORMAL_PAIR_SEARCH_CORRECTION {{\"mode\":\"{}\",\"n\":{:.17e},\"u\":{:.17e},\"target_ticks\":\"{}\",\"before_total_ticks\":\"{}\",\"after_total_ticks\":\"{}\",\"count_correction_distance_ticks\":\"{}\",\"actual_l1_ticks\":\"{}\",\"accepted_k\":\"{}\",\"candidate_evaluations\":{},\"nonempty_intervals\":{},\"pair\":{},\"count_defect_before\":{:.17e},\"count_defect_after\":{:.17e},\"count_tolerance\":{:.17e},\"energy_defect_before\":{:.17e},\"energy_defect_after\":{:.17e},\"energy_tolerance\":{:.17e},\"minimum_scope\":\"SINGLE_PAIR_FROM_FIXED_COUNT_BASE_ONLY\",\"statistics_scope\":\"FIRST_SUCCESS_PER_MODE_ONLY\"}}", mode, n, u, n.to_bits(), repair.before_ticks, repair.after_ticks, repair.count_distance, repair.l1_ticks, found.k, found.evaluations, found.intervals, pair_json, count_defect, corrected_count_defect, 64.0 * f64::EPSILON * n, energy_defect, corrected_energy_defect, 128.0 * f64::EPSILON * energy_scale);
                    }
                    diagnostics.max_count_relative_defect = diagnostics.max_count_relative_defect.max(corrected_count_defect / n);
                    diagnostics.max_energy_relative_defect = diagnostics.max_energy_relative_defect.max(corrected_energy_defect / energy_scale);
                    return Ok(repair.nodes);
                }
                Ok(ReiSubnormalSearchOutcome::Budget { next_k, evaluations, intervals }) => {
                    eprintln!("REI_SUBNORMAL_PAIR_SEARCH_STATUS {{\"status\":\"SEARCH_BUDGET_EXHAUSTED\",\"next_k\":\"{}\",\"candidate_evaluations\":{},\"nonempty_intervals\":{},\"budget\":{},\"feasibility_claim\":\"NOT_ISSUED\"}}", next_k, evaluations, intervals, REI_PAIR_SEARCH_MAX_EVALUATIONS);
                }
                Ok(ReiSubnormalSearchOutcome::NoSolution { evaluations, intervals }) => {
                    eprintln!("REI_SUBNORMAL_PAIR_SEARCH_STATUS {{\"status\":\"COMPLETE_SINGLE_PAIR_INTERVAL_SEARCH_NO_SOLUTION\",\"candidate_evaluations\":{},\"nonempty_intervals\":{},\"scope\":\"FIXED_COUNT_BASE_SINGLE_PAIR_ONLY\"}}", evaluations, intervals);
                }
                Err(reason) => {
                    eprintln!("REI_SUBNORMAL_PAIR_SEARCH_STATUS {{\"status\":\"UNSUPPORTED\",\"reason\":\"{}\",\"feasibility_claim\":\"NOT_ISSUED\"}}", reason);
                }
            }
        }
'''.encode()

INJECTION = CANDIDATE_HELPER + PAIR_HELPER + SEARCH_HELPER + SEARCH_REPAIR


def search_rounding_identity():
    return hashlib.sha256(INJECTION).hexdigest()


def instrument_pair_search(original: bytes, diagnostics: bool = False) -> bytes:
    blob = hashlib.sha1(b'blob ' + str(len(original)).encode() + b'\0' + original).hexdigest()
    if blob != ORIGINAL_BLOB or original.count(ANCHOR) != 1:
        raise ValueError('SUBNORMAL_PAIR_SEARCH_ORIGINAL_IDENTITY_MISMATCH')
    addition = INJECTION
    if diagnostics:
        from moment_fit_diagnostic import INJECTION as DIAGNOSTIC_INJECTION
        addition += DIAGNOSTIC_INJECTION
    return original.replace(ANCHOR, addition + ANCHOR, 1)
