"""Opt-in exact-subnormal-tick count correction in the original failed branch.

Original source identity and both original post-rounding gates remain binding.
No originally passing result is changed.
"""
import hashlib

from moment_fit_diagnostic import ANCHOR, ORIGINAL_BLOB


CANDIDATE_HELPER = r'''
        fn rei_subnormal_count_candidate(n: f64, nodes: &[(f64, f64)])
            -> Option<(Vec<(f64, f64)>, usize, u128, u128, u128)> {
            if !(n > 0.0 && n.is_subnormal()) || nodes.is_empty() { return None; }
            let mut total = 0_u128;
            let mut largest = 0_u64;
            let mut index = 0_usize;
            for (i, &(_, number)) in nodes.iter().enumerate() {
                if !(number.is_finite() && number >= 0.0
                    && (number == 0.0 || number.is_subnormal())) { return None; }
                let ticks = if number == 0.0 { 0 } else { number.to_bits() };
                total = total.checked_add(ticks as u128)?;
                if ticks > largest { largest = ticks; index = i; }
            }
            if largest == 0 { return None; }
            let target = n.to_bits() as u128;
            let (candidate, distance) = if target >= total {
                let difference = target - total;
                ((largest as u128).checked_add(difference)?, difference)
            } else {
                let difference = total - target;
                ((largest as u128).checked_sub(difference)?, difference)
            };
            if distance == 0 || candidate == 0 || candidate > (1_u128 << 52) - 1 { return None; }
            let after = total.checked_sub(largest as u128)?.checked_add(candidate)?;
            if after != target { return None; }
            let mut corrected = nodes.to_vec();
            corrected[index].1 = f64::from_bits(candidate as u64);
            Some((corrected, index, total, after, distance))
        }
'''.encode()

INJECTION = CANDIDATE_HELPER + r'''
        if count_defect > 64.0 * f64::EPSILON * n && n > 0.0 && n.is_subnormal()
            && eval(lambda).1.abs() < 8.0 * f64::EPSILON {
            if let Some((corrected, index, before_ticks, after_ticks, l1_ticks)) =
                rei_subnormal_count_candidate(n, &result) {
                let corrected_count_defect = (sum(corrected.iter().map(|x| x.1)) - n).abs();
                let corrected_energy_defect = (sum(corrected.iter().map(|x| x.0 * x.1)) - u).abs();
                if corrected_count_defect <= 64.0 * f64::EPSILON * n
                    && corrected_energy_defect <= 128.0 * f64::EPSILON * energy_scale {
                    static REI_ROUNDING_REPORTED: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);
                    if !REI_ROUNDING_REPORTED.swap(true, std::sync::atomic::Ordering::Relaxed) {
                        eprintln!("REI_SUBNORMAL_COUNT_CORRECTION {{\"n\":{:.17e},\"u\":{:.17e},\"target_ticks\":\"{}\",\"before_total_ticks\":\"{}\",\"after_total_ticks\":\"{}\",\"index\":{},\"q\":{:.17e},\"before_largest_ticks\":\"{}\",\"after_largest_ticks\":\"{}\",\"l1_ticks\":\"{}\",\"count_defect_before\":{:.17e},\"count_defect_after\":{:.17e},\"count_tolerance\":{:.17e},\"energy_defect_before\":{:.17e},\"energy_defect_after\":{:.17e},\"energy_tolerance\":{:.17e},\"statistics_scope\":\"FIRST_SUCCESS_ONLY; total applications not recorded\"}}", n, u, n.to_bits(), before_ticks, after_ticks, index, corrected[index].0, result[index].1.to_bits(), corrected[index].1.to_bits(), l1_ticks, count_defect, corrected_count_defect, 64.0 * f64::EPSILON * n, energy_defect, corrected_energy_defect, 128.0 * f64::EPSILON * energy_scale);
                    }
                    diagnostics.max_count_relative_defect = diagnostics.max_count_relative_defect
                        .max(corrected_count_defect / n);
                    diagnostics.max_energy_relative_defect = diagnostics.max_energy_relative_defect
                        .max(corrected_energy_defect / energy_scale);
                    return Ok(corrected);
                }
            }
        }
'''.encode()


def rounding_identity():
    return hashlib.sha256(INJECTION).hexdigest()


def instrument_rounding(original: bytes, diagnostics: bool = False) -> bytes:
    blob=hashlib.sha1(b'blob '+str(len(original)).encode()+b'\0'+original).hexdigest()
    if blob != ORIGINAL_BLOB or original.count(ANCHOR) != 1:
        raise ValueError('SUBNORMAL_COUNT_ORIGINAL_IDENTITY_MISMATCH')
    addition=INJECTION
    if diagnostics:
        from moment_fit_diagnostic import INJECTION as DIAGNOSTIC_INJECTION
        addition += DIAGNOSTIC_INJECTION
    return original.replace(ANCHOR, addition+ANCHOR, 1)
