"""Opt-in exact-count base plus a single subnormal-tick pair transfer.

Only the original failed moment gate is instrumented. Fixed nodes, positive
support, compensated sums and both original tolerances remain binding. The pair
search covers all ordered eligible pairs for one tick, not larger redistributions.
"""
import hashlib

from moment_fit_diagnostic import ANCHOR, ORIGINAL_BLOB
from subnormal_count_rounding import CANDIDATE_HELPER


PAIR_HELPER = r'''
        struct ReiSubnormalPairRepair {
            nodes: Vec<(f64, f64)>,
            count_index: Option<usize>,
            pair: Option<(usize, usize)>,
            before_ticks: u128,
            after_ticks: u128,
            count_distance: u128,
            l1_ticks: u128,
        }
        fn rei_subnormal_ticks(number: f64) -> u128 {
            if number == 0.0 { 0 } else { number.to_bits() as u128 }
        }
        fn rei_subnormal_l1(original: &[(f64, f64)], corrected: &[(f64, f64)]) -> u128 {
            original.iter().zip(corrected).map(|(a, b)|
                rei_subnormal_ticks(a.1).abs_diff(rei_subnormal_ticks(b.1))).sum()
        }
        fn rei_subnormal_pair_candidate(n: f64, u: f64, energy_scale: f64,
            nodes: &[(f64, f64)]) -> Option<ReiSubnormalPairRepair> {
            if !(n > 0.0 && n.is_subnormal()) || nodes.is_empty() { return None; }
            let mut total = 0_u128;
            for &(q, number) in nodes {
                if !(q.is_finite() && q > 0.0 && number.is_finite() && number >= 0.0
                    && (number == 0.0 || number.is_subnormal())) { return None; }
                total = total.checked_add(rei_subnormal_ticks(number))?;
            }
            let target = n.to_bits() as u128;
            let (base, count_index, count_distance) = if total == target {
                (nodes.to_vec(), None, 0)
            } else {
                let (fixed, index, _, _, distance) = rei_subnormal_count_candidate(n, nodes)?;
                (fixed, Some(index), distance)
            };
            let passes = |candidate: &[(f64, f64)]| {
                (sum(candidate.iter().map(|x| x.1)) - n).abs() <= 64.0 * f64::EPSILON * n
                && (sum(candidate.iter().map(|x| x.0 * x.1)) - u).abs()
                    <= 128.0 * f64::EPSILON * energy_scale
            };
            if passes(&base) {
                return Some(ReiSubnormalPairRepair {
                    l1_ticks: rei_subnormal_l1(nodes, &base), nodes: base,
                    count_index, pair: None, before_ticks: total, after_ticks: target,
                    count_distance,
                });
            }
            // Lexicographic exhaustive search of the eligible L1=2-tick shell.
            for donor in 0..base.len() {
                let donor_bits = base[donor].1.to_bits();
                if base[donor].1 == 0.0 || donor_bits < 2 { continue; }
                for receiver in 0..base.len() {
                    if donor == receiver { continue; }
                    let receiver_bits = base[receiver].1.to_bits();
                    if base[receiver].1 == 0.0 || receiver_bits < 1
                        || receiver_bits >= (1_u64 << 52) - 1 { continue; }
                    let mut candidate = base.clone();
                    candidate[donor].1 = f64::from_bits(donor_bits - 1);
                    candidate[receiver].1 = f64::from_bits(receiver_bits + 1);
                    if passes(&candidate) {
                        return Some(ReiSubnormalPairRepair {
                            l1_ticks: rei_subnormal_l1(nodes, &candidate), nodes: candidate,
                            count_index, pair: Some((donor, receiver)), before_ticks: total,
                            after_ticks: target, count_distance,
                        });
                    }
                }
            }
            None
        }
'''.encode()

REPAIR = r'''
        if n > 0.0 && n.is_subnormal() && eval(lambda).1.abs() < 8.0 * f64::EPSILON {
            if let Some(repair) = rei_subnormal_pair_candidate(n, u, energy_scale, &result) {
                let corrected_count_defect = (sum(repair.nodes.iter().map(|x| x.1)) - n).abs();
                let corrected_energy_defect = (sum(repair.nodes.iter().map(|x| x.0 * x.1)) - u).abs();
                static REI_PAIR_COUNT_REPORTED: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);
                static REI_PAIR_REPORTED: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);
                let (mode, reported) = if repair.pair.is_some() {
                    ("pair", &REI_PAIR_REPORTED)
                } else { ("count-only", &REI_PAIR_COUNT_REPORTED) };
                if !reported.swap(true, std::sync::atomic::Ordering::Relaxed) {
                    let pair_json = if let Some((donor, receiver)) = repair.pair {
                        let base_bits = |index: usize| {
                            if repair.count_index == Some(index) {
                                let original_ticks = rei_subnormal_ticks(result[index].1);
                                if repair.after_ticks >= repair.before_ticks {
                                    (original_ticks + repair.count_distance) as u64
                                } else { (original_ticks - repair.count_distance) as u64 }
                            } else { result[index].1.to_bits() }
                        };
                        format!("{{\"donor\":{},\"receiver\":{},\"donor_q\":{:.17e},\"receiver_q\":{:.17e},\"donor_base_bits\":\"{}\",\"receiver_base_bits\":\"{}\",\"donor_after_bits\":\"{}\",\"receiver_after_bits\":\"{}\",\"transfer_ticks\":\"1\"}}", donor, receiver, result[donor].0, result[receiver].0, base_bits(donor), base_bits(receiver), repair.nodes[donor].1.to_bits(), repair.nodes[receiver].1.to_bits())
                    } else { "null".to_string() };
                    let count_json = if let Some(index) = repair.count_index {
                        format!("{{\"index\":{},\"q\":{:.17e},\"before_bits\":\"{}\",\"after_bits\":\"{}\"}}", index, result[index].0, result[index].1.to_bits(), if repair.after_ticks >= repair.before_ticks { (rei_subnormal_ticks(result[index].1) + repair.count_distance) as u64 } else { (rei_subnormal_ticks(result[index].1) - repair.count_distance) as u64 })
                    } else { "null".to_string() };
                    eprintln!("REI_SUBNORMAL_PAIR_CORRECTION {{\"mode\":\"{}\",\"n\":{:.17e},\"u\":{:.17e},\"target_ticks\":\"{}\",\"before_total_ticks\":\"{}\",\"after_total_ticks\":\"{}\",\"count_correction_distance_ticks\":\"{}\",\"actual_l1_ticks\":\"{}\",\"count_correction\":{},\"pair\":{},\"count_defect_before\":{:.17e},\"count_defect_after\":{:.17e},\"count_tolerance\":{:.17e},\"energy_defect_before\":{:.17e},\"energy_defect_after\":{:.17e},\"energy_tolerance\":{:.17e},\"statistics_scope\":\"FIRST_SUCCESS_PER_MODE_ONLY; total applications not recorded\"}}", mode, n, u, n.to_bits(), repair.before_ticks, repair.after_ticks, repair.count_distance, repair.l1_ticks, count_json, pair_json, count_defect, corrected_count_defect, 64.0 * f64::EPSILON * n, energy_defect, corrected_energy_defect, 128.0 * f64::EPSILON * energy_scale);
                }
                diagnostics.max_count_relative_defect = diagnostics.max_count_relative_defect
                    .max(corrected_count_defect / n);
                diagnostics.max_energy_relative_defect = diagnostics.max_energy_relative_defect
                    .max(corrected_energy_defect / energy_scale);
                return Ok(repair.nodes);
            }
        }
'''.encode()

INJECTION = CANDIDATE_HELPER + PAIR_HELPER + REPAIR


def pair_rounding_identity():
    return hashlib.sha256(INJECTION).hexdigest()


def instrument_pair_rounding(original: bytes, diagnostics: bool = False) -> bytes:
    blob = hashlib.sha1(b'blob ' + str(len(original)).encode() + b'\0' + original).hexdigest()
    if blob != ORIGINAL_BLOB or original.count(ANCHOR) != 1:
        raise ValueError('SUBNORMAL_PAIR_ORIGINAL_IDENTITY_MISMATCH')
    addition = INJECTION
    if diagnostics:
        from moment_fit_diagnostic import INJECTION as DIAGNOSTIC_INJECTION
        addition += DIAGNOSTIC_INJECTION
    return original.replace(ANCHOR, addition + ANCHOR, 1)
