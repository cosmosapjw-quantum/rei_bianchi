
#![allow(dead_code)]
#[derive(Debug)] enum ForwardError { InvalidInput(&'static str) }
fn bad(tag:&'static str)->ForwardError { ForwardError::InvalidInput(tag) }
#[derive(Default)] struct Diagnostics { max_count_relative_defect:f64, max_energy_relative_defect:f64 }
fn sum(xs:impl Iterator<Item=f64>)->f64 {
 let (mut total,mut correction)=(0.0,0.0);
 for x in xs { let y=x-correction;let next=total+y;correction=(next-total)-y;total=next; }
 total
}
fn trial(n:f64,u:f64,width:f64,result:Vec<(f64,f64)>,enabled:bool,f:f64)
 ->Result<Vec<(f64,f64)>,ForwardError> {
 let count_defect=(sum(result.iter().map(|x|x.1))-n).abs();
 let energy_defect=(sum(result.iter().map(|x|x.0*x.1))-u).abs();
 let energy_scale=u.abs().max(n*width);
 let lambda=0f64;let eval=|_:f64|(Vec::<f64>::new(),f,0f64);
 let mut diagnostics=Diagnostics::default();
 if count_defect>64.0*f64::EPSILON*n || energy_defect>128.0*f64::EPSILON*energy_scale {
  if enabled {

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

  }
  return Err(bad("AXBI_COVARIANT_MOMENT_FIT"));
 }
 Ok(result)
}
fn main() {
 let eta=f64::from_bits(1);

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

 let nodes0=vec![(1.70607059180523919e+01f64,8.79737553616299461e-313f64),(1.70566425953415184e+01f64,1.51201752243015279e-312f64),(1.70499094180882302e+01f64,1.42021715187899706e-312f64),(1.70414139718049285e+01f64,9.82884332774444007e-313f64),(1.70323033648368174e+01f64,5.66902605949671962e-313f64),(1.70238079185535121e+01f64,2.93526473056583012e-313f64),(1.70170747413002239e+01f64,1.38545766258952735e-313f64),(1.70130114185893504e+01f64,4.93409348948156560e-314f64),(1.70110391438588202e+01f64,4.37995537260147596e-314f64),(1.70069758211479432e+01f64,7.52789197601767240e-314f64),(1.70002426438946550e+01f64,7.07084484394081472e-314f64),(1.69917471976113532e+01f64,4.89349294741386923e-314f64),(1.69826365906432422e+01f64,2.82244187979781846e-314f64),(1.69741411443599368e+01f64,1.46138225818514834e-314f64),(1.69674079671066487e+01f64,6.89778753539979937e-315f64),(1.69633446443957752e+01f64,2.45654049732874772e-315f64),(1.69613723696652450e+01f64,2.18065137511024977e-315f64),(1.69573090469543679e+01f64,3.74791672327988066e-315f64),(1.69505758697010833e+01f64,3.52036635638712005e-315f64),(1.69420804234177780e+01f64,2.43632668086600272e-315f64),(1.69329698164496669e+01f64,1.40521107029457680e-315f64),(1.69244743701663616e+01f64,7.27579385079310996e-316f64),(1.69177411929130770e+01f64,3.43420618418033111e-316f64),(1.69136778702021999e+01f64,1.22303949662134925e-316f64),(1.69117055954716697e+01f64,1.08568237956500552e-316f64),(1.69076422727607927e+01f64,1.86597784277907813e-316f64),(1.69009090955075081e+01f64,1.75268720680387194e-316f64),(1.68924136492242027e+01f64,1.21297562644838598e-316f64),(1.68833030422560917e+01f64,6.99613406897211620e-317f64),(1.68748075959727863e+01f64,3.62240433601693497e-317f64),(1.68680744187195018e+01f64,1.70979074760873906e-317f64),(1.68640110960086247e+01f64,6.08915651807856875e-318f64),(1.68620388212780945e+01f64,5.40529555438740734e-318f64),(1.68579754985672210e+01f64,9.29015843091942098e-318f64),(1.68512423213139328e+01f64,8.72611332700122028e-318f64),(1.68427468750306275e+01f64,6.03904838027734952e-318f64),(1.68336362680625165e+01f64,3.48316774383724655e-318f64),(1.68251408217792147e+01f64,1.80348782701430226e-318f64),(1.68184076445259265e+01f64,8.51255345158634146e-319f64),(1.68143443218150530e+01f64,3.03163620944647292e-319f64),(1.68123720470845193e+01f64,2.69112616633268580e-319f64),(1.68083087243736458e+01f64,4.62529435667199777e-319f64),(1.68015755471203576e+01f64,4.34446744357583324e-319f64),(1.67930801008370523e+01f64,3.00668589433148997e-319f64),(1.67839694938689448e+01f64,1.73417041690277537e-319f64),(1.67754740475856394e+01f64,8.97914904751881469e-320f64),(1.67687408703323513e+01f64,4.23809511002621286e-320f64),(1.67646775476214778e+01f64,1.50937054804500819e-320f64),(1.67627052728909440e+01f64,1.33990603152146063e-320f64),(1.67586419501800705e+01f64,2.30283997526605014e-320f64),(1.67519087729267824e+01f64,2.16301939749297737e-320f64),(1.67434133266434806e+01f64,1.49701890689897703e-320f64),(1.67343027196753695e+01f64,8.63626748930498959e-321f64),(1.67258072733920642e+01f64,4.47129409486328122e-321f64),(1.67190740961387760e+01f64,2.10966030774212274e-321f64),(1.67150107734279025e+01f64,7.50979781678694747e-322f64),(1.67130384986973723e+01f64,6.66988621885682835e-322f64),(1.67089751759864953e+01f64,1.14623229835169198e-321f64),(1.67022419987332071e+01f64,1.07706310793391747e-321f64),(1.66937465524499054e+01f64,7.46039125220282282e-322f64),(1.66846359454817943e+01f64,4.29837111881884493e-322f64),(1.66761404991984890e+01f64,2.22329540628560945e-322f64),(1.66694073219452008e+01f64,1.03753785626661774e-322f64),(1.66653439992343273e+01f64,3.95252516672997235e-323f64),(1.66633717245037971e+01f64,3.45845952088872581e-323f64),(1.66593084017929201e+01f64,5.92878775009495853e-323f64),(1.66525752245396355e+01f64,5.43472210425371199e-323f64),(1.66440797782563301e+01f64,3.95252516672997235e-323f64),(1.66349691712882191e+01f64,1.97626258336498618e-323f64),(1.66264737250049137e+01f64,9.88131291682493088e-324f64),(1.66197405477516291e+01f64,4.94065645841246544e-324f64),(1.66156772250407521e+01f64,0.00000000000000000e+00f64),(1.66137049503102219e+01f64,0.00000000000000000e+00f64),(1.66096416275993448e+01f64,4.94065645841246544e-324f64),(1.66029084503460602e+01f64,4.94065645841246544e-324f64),(1.65944130040627549e+01f64,0.00000000000000000e+00f64),(1.65853023970946438e+01f64,0.00000000000000000e+00f64),(1.65768069508113385e+01f64,0.00000000000000000e+00f64),(1.65700737735580539e+01f64,0.00000000000000000e+00f64),(1.65660104508471768e+01f64,0.00000000000000000e+00f64),(1.65640381761166466e+01f64,0.00000000000000000e+00f64),(1.65599748534057731e+01f64,0.00000000000000000e+00f64),(1.65532416761524850e+01f64,0.00000000000000000e+00f64),(1.65447462298691796e+01f64,0.00000000000000000e+00f64),(1.65356356229010686e+01f64,0.00000000000000000e+00f64),(1.65271401766177668e+01f64,0.00000000000000000e+00f64),(1.65204069993644787e+01f64,0.00000000000000000e+00f64),(1.65163436766536051e+01f64,0.00000000000000000e+00f64),(1.65143714019230714e+01f64,0.00000000000000000e+00f64),(1.65103080792121979e+01f64,0.00000000000000000e+00f64),(1.65035749019589097e+01f64,0.00000000000000000e+00f64),(1.64950794556756044e+01f64,0.00000000000000000e+00f64),(1.64859688487074969e+01f64,0.00000000000000000e+00f64),(1.64774734024241916e+01f64,0.00000000000000000e+00f64),(1.64707402251709034e+01f64,0.00000000000000000e+00f64),(1.64666769024600299e+01f64,0.00000000000000000e+00f64),(1.64647046277294962e+01f64,0.00000000000000000e+00f64),(1.64606413050186227e+01f64,0.00000000000000000e+00f64),(1.64539081277653345e+01f64,0.00000000000000000e+00f64),(1.64454126814820327e+01f64,0.00000000000000000e+00f64),(1.64363020745139217e+01f64,0.00000000000000000e+00f64),(1.64278066282306163e+01f64,0.00000000000000000e+00f64),(1.64210734509773282e+01f64,0.00000000000000000e+00f64),(1.64170101282664547e+01f64,0.00000000000000000e+00f64),(1.64150378535359245e+01f64,0.00000000000000000e+00f64),(1.64109745308250474e+01f64,0.00000000000000000e+00f64),(1.64042413535717628e+01f64,0.00000000000000000e+00f64),(1.63957459072884575e+01f64,0.00000000000000000e+00f64),(1.63866353003203464e+01f64,0.00000000000000000e+00f64),(1.63781398540370411e+01f64,0.00000000000000000e+00f64),(1.63714066767837565e+01f64,0.00000000000000000e+00f64),(1.63673433540728794e+01f64,0.00000000000000000e+00f64),(1.63653710793423492e+01f64,0.00000000000000000e+00f64),(1.63613077566314722e+01f64,0.00000000000000000e+00f64),(1.63545745793781876e+01f64,0.00000000000000000e+00f64),(1.63460791330948823e+01f64,0.00000000000000000e+00f64),(1.63369685261267712e+01f64,0.00000000000000000e+00f64),(1.63284730798434659e+01f64,0.00000000000000000e+00f64),(1.63217399025901813e+01f64,0.00000000000000000e+00f64),(1.63176765798793042e+01f64,0.00000000000000000e+00f64),(1.63157043051487740e+01f64,0.00000000000000000e+00f64),(1.63116409824379005e+01f64,0.00000000000000000e+00f64),(1.63049078051846124e+01f64,0.00000000000000000e+00f64),(1.62964123589013070e+01f64,0.00000000000000000e+00f64),(1.62873017519331960e+01f64,0.00000000000000000e+00f64),(1.62788063056498942e+01f64,0.00000000000000000e+00f64),(1.62720731283966060e+01f64,0.00000000000000000e+00f64),(1.62680098056857290e+01f64,0.00000000000000000e+00f64)];
 let n=f64::from_bits(1244638132025);let u=f64::from_bits(21215026808689);
 let width=3.46126704877696234e+00f64;
 assert!(trial(n,u,width,nodes0.clone(),false,0.0).is_err());
 let fixed=trial(n,u,width,nodes0.clone(),true,7.28135986364630949e-17f64).unwrap();
 let found=match rei_subnormal_pair_search(n,u,u,&nodes0,65536).unwrap() {
  ReiSubnormalSearchOutcome::Found(value)=>value,_=>panic!("captured candidate missing") };
 assert_eq!(found.k,1);assert_eq!(found.repair.pair,Some((24,0)));
 assert_eq!(found.evaluations,625);assert_eq!(found.intervals,3430);
 assert_eq!(found.repair.count_distance,0);assert_eq!(found.repair.l1_ticks,2);
 assert_eq!((sum(fixed.iter().map(|x|x.1))-n).abs().to_bits(),0);
 assert_eq!((sum(fixed.iter().map(|x|x.0*x.1))-u).abs().to_bits(),1);
 for (a,b) in nodes0.iter().zip(&fixed) {assert_eq!(a.0.to_bits(),b.0.to_bits());assert_eq!(a.1>0.0,b.1>0.0);}
 println!("fixture=0 k={} donor=24 receiver=0 evaluations={} intervals={} L1={}",found.k,found.evaluations,found.intervals,found.repair.l1_ticks);

 let nodes1=vec![(1.70607078809318367e+01f64,2.21934985263217512e-313f64),(1.70566526461536405e+01f64,3.81442835059640203e-313f64),(1.70499328711054474e+01f64,3.58283980692129590e-313f64),(1.70414543347755227e+01f64,2.47956244468288667e-313f64),(1.70323618622213040e+01f64,1.43014835482340320e-313f64),(1.70238833258913793e+01f64,7.40491220433396980e-314f64),(1.70171635508431862e+01f64,3.49515062377246908e-314f64),(1.70131083160649865e+01f64,1.24474391407825375e-314f64),(1.70111399670933423e+01f64,1.10494922830941694e-314f64),(1.70070847323151462e+01f64,1.89909205070157419e-314f64),(1.70003649572669531e+01f64,1.78379090400649895e-314f64),(1.69918864209370284e+01f64,1.23450144954969743e-314f64),(1.69827939483828096e+01f64,7.12028939130366036e-315f64),(1.69743154120528850e+01f64,3.68668869939427708e-315f64),(1.69675956370046919e+01f64,1.74013302838698462e-315f64),(1.69635404022264922e+01f64,6.19721504827088072e-316f64),(1.69615720532548480e+01f64,5.50121830071435619e-316f64),(1.69575168184766518e+01f64,9.45502255399484695e-316f64),(1.69507970434284587e+01f64,8.88097197846302141e-316f64),(1.69423185070985340e+01f64,6.14622080373384522e-316f64),(1.69332260345443153e+01f64,3.54498335999544912e-316f64),(1.69247474982143906e+01f64,1.83549423946349614e-316f64),(1.69180277231661975e+01f64,8.66361204653971922e-317f64),(1.69139724883880014e+01f64,3.08541179653677172e-317f64),(1.69120041394163572e+01f64,2.73889539736649256e-317f64),(1.69079489046381575e+01f64,4.70737842307206247e-317f64),(1.69012291295899644e+01f64,4.42157577485663074e-317f64),(1.68927505932600397e+01f64,3.06002324519392758e-317f64),(1.68836581207058209e+01f64,1.76494329565399741e-317f64),(1.68751795843758963e+01f64,9.13838640517344846e-318f64),(1.68684598093277032e+01f64,4.31335612985720994e-318f64),(1.68644045745495070e+01f64,1.53613408408022852e-318f64),(1.68624362255778628e+01f64,1.36361624186538205e-318f64),(1.68583809907996631e+01f64,2.34366461958191234e-318f64),(1.68516612157514700e+01f64,2.20137371357963334e-318f64),(1.68431826794215453e+01f64,1.52349588485960943e-318f64),(1.68340902068673266e+01f64,8.78715513754490629e-319f64),(1.68256116705374019e+01f64,4.54975171942287118e-319f64),(1.68188918954892088e+01f64,2.14750573621356223e-319f64),(1.68148366607110127e+01f64,7.64813619762249650e-320f64),(1.68128683117393685e+01f64,6.78895603950456876e-320f64),(1.68088130769611723e+01f64,1.16683483578327196e-319f64),(1.68020933019129792e+01f64,1.09598582216963721e-319f64),(1.67936147655830545e+01f64,7.58489579495481695e-320f64),(1.67845222930288358e+01f64,4.37495129392423815e-320f64),(1.67760437566989111e+01f64,2.26529098618211541e-320f64),(1.67693239816507180e+01f64,1.06915805760045752e-320f64),(1.67652687468725183e+01f64,3.80924612943601086e-321f64),(1.67633003979008741e+01f64,3.37940901755412636e-321f64),(1.67592451631226780e+01f64,5.81021199509305936e-321f64),(1.67525253880744849e+01f64,5.45448473008736185e-321f64),(1.67440468517445602e+01f64,3.77466153422712360e-321f64),(1.67349543791903415e+01f64,2.17882949815989726e-321f64),(1.67264758428604168e+01f64,1.12646967251804212e-321f64),(1.67197560678122237e+01f64,5.33590897508546268e-322f64),(1.67157008330340240e+01f64,1.87744945419673687e-322f64),(1.67137324840623798e+01f64,1.67982319586023825e-322f64),(1.67096772492841836e+01f64,2.91498731046335461e-322f64),(1.67029574742359905e+01f64,2.71736105212685599e-322f64),(1.66944789379060659e+01f64,1.87744945419673687e-322f64),(1.66853864653518471e+01f64,1.08694442085074240e-322f64),(1.66769079290219224e+01f64,5.43472210425371199e-323f64),(1.66701881539737293e+01f64,2.47032822920623272e-323f64),(1.66661329191955332e+01f64,9.88131291682493088e-324f64),(1.66641645702238890e+01f64,9.88131291682493088e-324f64),(1.66601093354456893e+01f64,1.48219693752373963e-323f64),(1.66533895603974962e+01f64,1.48219693752373963e-323f64),(1.66449110240675715e+01f64,9.88131291682493088e-324f64),(1.66358185515133528e+01f64,4.94065645841246544e-324f64),(1.66273400151834281e+01f64,4.94065645841246544e-324f64),(1.66206202401352350e+01f64,0.00000000000000000e+00f64),(1.66165650053570388e+01f64,0.00000000000000000e+00f64),(1.66145966563853946e+01f64,0.00000000000000000e+00f64),(1.66105414216071949e+01f64,0.00000000000000000e+00f64),(1.66038216465590018e+01f64,0.00000000000000000e+00f64),(1.65953431102290772e+01f64,0.00000000000000000e+00f64),(1.65862506376748584e+01f64,0.00000000000000000e+00f64),(1.65777721013449337e+01f64,0.00000000000000000e+00f64),(1.65710523262967406e+01f64,0.00000000000000000e+00f64),(1.65669970915185445e+01f64,0.00000000000000000e+00f64),(1.65650287425469003e+01f64,0.00000000000000000e+00f64),(1.65609735077687041e+01f64,0.00000000000000000e+00f64),(1.65542537327205110e+01f64,0.00000000000000000e+00f64),(1.65457751963905864e+01f64,0.00000000000000000e+00f64),(1.65366827238363676e+01f64,0.00000000000000000e+00f64),(1.65282041875064429e+01f64,0.00000000000000000e+00f64),(1.65214844124582498e+01f64,0.00000000000000000e+00f64),(1.65174291776800501e+01f64,0.00000000000000000e+00f64),(1.65154608287084059e+01f64,0.00000000000000000e+00f64),(1.65114055939302098e+01f64,0.00000000000000000e+00f64),(1.65046858188820167e+01f64,0.00000000000000000e+00f64),(1.64962072825520920e+01f64,0.00000000000000000e+00f64),(1.64871148099978733e+01f64,0.00000000000000000e+00f64),(1.64786362736679486e+01f64,0.00000000000000000e+00f64),(1.64719164986197555e+01f64,0.00000000000000000e+00f64),(1.64678612638415558e+01f64,0.00000000000000000e+00f64),(1.64658929148699116e+01f64,0.00000000000000000e+00f64),(1.64618376800917154e+01f64,0.00000000000000000e+00f64),(1.64551179050435223e+01f64,0.00000000000000000e+00f64),(1.64466393687135977e+01f64,0.00000000000000000e+00f64),(1.64375468961593789e+01f64,0.00000000000000000e+00f64),(1.64290683598294542e+01f64,0.00000000000000000e+00f64),(1.64223485847812611e+01f64,0.00000000000000000e+00f64),(1.64182933500030650e+01f64,0.00000000000000000e+00f64),(1.64163250010314208e+01f64,0.00000000000000000e+00f64),(1.64122697662532211e+01f64,0.00000000000000000e+00f64),(1.64055499912050280e+01f64,0.00000000000000000e+00f64),(1.63970714548751033e+01f64,0.00000000000000000e+00f64),(1.63879789823208846e+01f64,0.00000000000000000e+00f64),(1.63795004459909599e+01f64,0.00000000000000000e+00f64),(1.63727806709427668e+01f64,0.00000000000000000e+00f64),(1.63687254361645707e+01f64,0.00000000000000000e+00f64),(1.63667570871929264e+01f64,0.00000000000000000e+00f64),(1.63627018524147303e+01f64,0.00000000000000000e+00f64),(1.63559820773665336e+01f64,0.00000000000000000e+00f64),(1.63475035410366090e+01f64,0.00000000000000000e+00f64),(1.63384110684823902e+01f64,0.00000000000000000e+00f64),(1.63299325321524655e+01f64,0.00000000000000000e+00f64),(1.63232127571042724e+01f64,0.00000000000000000e+00f64),(1.63191575223260763e+01f64,0.00000000000000000e+00f64),(1.63171891733544321e+01f64,0.00000000000000000e+00f64),(1.63131339385762359e+01f64,0.00000000000000000e+00f64),(1.63064141635280428e+01f64,0.00000000000000000e+00f64),(1.62979356271981182e+01f64,0.00000000000000000e+00f64),(1.62888431546438994e+01f64,0.00000000000000000e+00f64),(1.62803646183139747e+01f64,0.00000000000000000e+00f64),(1.62736448432657781e+01f64,0.00000000000000000e+00f64),(1.62695896084875820e+01f64,0.00000000000000000e+00f64)];
 let n=f64::from_bits(313989944336);let u=f64::from_bits(5352011796590);
 let width=3.46126704877696234e+00f64;
 assert!(trial(n,u,width,nodes1.clone(),false,0.0).is_err());
 let fixed=trial(n,u,width,nodes1.clone(),true,3.07533787930965028e-17f64).unwrap();
 let found=match rei_subnormal_pair_search(n,u,u,&nodes1,65536).unwrap() {
  ReiSubnormalSearchOutcome::Found(value)=>value,_=>panic!("captured candidate missing") };
 assert_eq!(found.k,3);assert_eq!(found.repair.pair,Some((0,14)));
 assert_eq!(found.evaluations,164);assert_eq!(found.intervals,2348);
 assert_eq!(found.repair.count_distance,1);assert_eq!(found.repair.l1_ticks,7);
 assert_eq!((sum(fixed.iter().map(|x|x.1))-n).abs().to_bits(),0);
 assert_eq!((sum(fixed.iter().map(|x|x.0*x.1))-u).abs().to_bits(),0);
 for (a,b) in nodes1.iter().zip(&fixed) {assert_eq!(a.0.to_bits(),b.0.to_bits());assert_eq!(a.1>0.0,b.1>0.0);}
 println!("fixture=1 k={} donor=0 receiver=14 evaluations={} intervals={} L1={}",found.k,found.evaluations,found.intervals,found.repair.l1_ticks);
assert_eq!(rei_signed_interval(-4,-3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-4,-3,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-4,-3,2,5).unwrap(),None);assert_eq!(rei_signed_interval(-4,-2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-4,-2,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-4,-2,2,5).unwrap(),None);assert_eq!(rei_signed_interval(-4,-1,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-4,-1,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-4,-1,2,5).unwrap(),None);assert_eq!(rei_signed_interval(-4,0,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-4,0,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-4,0,2,5).unwrap(),None);assert_eq!(rei_signed_interval(-4,1,0,5).unwrap(),Some((4,4)));assert_eq!(rei_signed_interval(-4,1,1,5).unwrap(),Some((3,5)));assert_eq!(rei_signed_interval(-4,1,2,5).unwrap(),Some((2,5)));assert_eq!(rei_signed_interval(-4,2,0,5).unwrap(),Some((2,2)));assert_eq!(rei_signed_interval(-4,2,1,5).unwrap(),Some((2,2)));assert_eq!(rei_signed_interval(-4,2,2,5).unwrap(),Some((1,3)));assert_eq!(rei_signed_interval(-4,3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-4,3,1,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(-4,3,2,5).unwrap(),Some((1,2)));assert_eq!(rei_signed_interval(-3,-3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-3,-3,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-3,-3,2,5).unwrap(),None);assert_eq!(rei_signed_interval(-3,-2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-3,-2,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-3,-2,2,5).unwrap(),None);assert_eq!(rei_signed_interval(-3,-1,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-3,-1,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-3,-1,2,5).unwrap(),None);assert_eq!(rei_signed_interval(-3,0,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-3,0,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-3,0,2,5).unwrap(),None);assert_eq!(rei_signed_interval(-3,1,0,5).unwrap(),Some((3,3)));assert_eq!(rei_signed_interval(-3,1,1,5).unwrap(),Some((2,4)));assert_eq!(rei_signed_interval(-3,1,2,5).unwrap(),Some((1,5)));assert_eq!(rei_signed_interval(-3,2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-3,2,1,5).unwrap(),Some((1,2)));assert_eq!(rei_signed_interval(-3,2,2,5).unwrap(),Some((1,2)));assert_eq!(rei_signed_interval(-3,3,0,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(-3,3,1,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(-3,3,2,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(-2,-3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-2,-3,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-2,-3,2,5).unwrap(),None);assert_eq!(rei_signed_interval(-2,-2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-2,-2,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-2,-2,2,5).unwrap(),None);assert_eq!(rei_signed_interval(-2,-1,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-2,-1,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-2,-1,2,5).unwrap(),None);assert_eq!(rei_signed_interval(-2,0,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-2,0,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-2,0,2,5).unwrap(),Some((1,5)));assert_eq!(rei_signed_interval(-2,1,0,5).unwrap(),Some((2,2)));assert_eq!(rei_signed_interval(-2,1,1,5).unwrap(),Some((1,3)));assert_eq!(rei_signed_interval(-2,1,2,5).unwrap(),Some((1,4)));assert_eq!(rei_signed_interval(-2,2,0,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(-2,2,1,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(-2,2,2,5).unwrap(),Some((1,2)));assert_eq!(rei_signed_interval(-2,3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-2,3,1,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(-2,3,2,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(-1,-3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-1,-3,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-1,-3,2,5).unwrap(),None);assert_eq!(rei_signed_interval(-1,-2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-1,-2,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-1,-2,2,5).unwrap(),None);assert_eq!(rei_signed_interval(-1,-1,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-1,-1,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-1,-1,2,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(-1,0,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-1,0,1,5).unwrap(),Some((1,5)));assert_eq!(rei_signed_interval(-1,0,2,5).unwrap(),Some((1,5)));assert_eq!(rei_signed_interval(-1,1,0,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(-1,1,1,5).unwrap(),Some((1,2)));assert_eq!(rei_signed_interval(-1,1,2,5).unwrap(),Some((1,3)));assert_eq!(rei_signed_interval(-1,2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-1,2,1,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(-1,2,2,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(-1,3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(-1,3,1,5).unwrap(),None);assert_eq!(rei_signed_interval(-1,3,2,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(0,-3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(0,-3,1,5).unwrap(),None);assert_eq!(rei_signed_interval(0,-3,2,5).unwrap(),None);assert_eq!(rei_signed_interval(0,-2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(0,-2,1,5).unwrap(),None);assert_eq!(rei_signed_interval(0,-2,2,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(0,-1,0,5).unwrap(),None);assert_eq!(rei_signed_interval(0,-1,1,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(0,-1,2,5).unwrap(),Some((1,2)));assert_eq!(rei_signed_interval(0,0,0,5).unwrap(),Some((1,5)));assert_eq!(rei_signed_interval(0,0,1,5).unwrap(),Some((1,5)));assert_eq!(rei_signed_interval(0,0,2,5).unwrap(),Some((1,5)));assert_eq!(rei_signed_interval(0,1,0,5).unwrap(),None);assert_eq!(rei_signed_interval(0,1,1,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(0,1,2,5).unwrap(),Some((1,2)));assert_eq!(rei_signed_interval(0,2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(0,2,1,5).unwrap(),None);assert_eq!(rei_signed_interval(0,2,2,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(0,3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(0,3,1,5).unwrap(),None);assert_eq!(rei_signed_interval(0,3,2,5).unwrap(),None);assert_eq!(rei_signed_interval(1,-3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(1,-3,1,5).unwrap(),None);assert_eq!(rei_signed_interval(1,-3,2,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(1,-2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(1,-2,1,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(1,-2,2,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(1,-1,0,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(1,-1,1,5).unwrap(),Some((1,2)));assert_eq!(rei_signed_interval(1,-1,2,5).unwrap(),Some((1,3)));assert_eq!(rei_signed_interval(1,0,0,5).unwrap(),None);assert_eq!(rei_signed_interval(1,0,1,5).unwrap(),Some((1,5)));assert_eq!(rei_signed_interval(1,0,2,5).unwrap(),Some((1,5)));assert_eq!(rei_signed_interval(1,1,0,5).unwrap(),None);assert_eq!(rei_signed_interval(1,1,1,5).unwrap(),None);assert_eq!(rei_signed_interval(1,1,2,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(1,2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(1,2,1,5).unwrap(),None);assert_eq!(rei_signed_interval(1,2,2,5).unwrap(),None);assert_eq!(rei_signed_interval(1,3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(1,3,1,5).unwrap(),None);assert_eq!(rei_signed_interval(1,3,2,5).unwrap(),None);assert_eq!(rei_signed_interval(2,-3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(2,-3,1,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(2,-3,2,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(2,-2,0,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(2,-2,1,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(2,-2,2,5).unwrap(),Some((1,2)));assert_eq!(rei_signed_interval(2,-1,0,5).unwrap(),Some((2,2)));assert_eq!(rei_signed_interval(2,-1,1,5).unwrap(),Some((1,3)));assert_eq!(rei_signed_interval(2,-1,2,5).unwrap(),Some((1,4)));assert_eq!(rei_signed_interval(2,0,0,5).unwrap(),None);assert_eq!(rei_signed_interval(2,0,1,5).unwrap(),None);assert_eq!(rei_signed_interval(2,0,2,5).unwrap(),Some((1,5)));assert_eq!(rei_signed_interval(2,1,0,5).unwrap(),None);assert_eq!(rei_signed_interval(2,1,1,5).unwrap(),None);assert_eq!(rei_signed_interval(2,1,2,5).unwrap(),None);assert_eq!(rei_signed_interval(2,2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(2,2,1,5).unwrap(),None);assert_eq!(rei_signed_interval(2,2,2,5).unwrap(),None);assert_eq!(rei_signed_interval(2,3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(2,3,1,5).unwrap(),None);assert_eq!(rei_signed_interval(2,3,2,5).unwrap(),None);assert_eq!(rei_signed_interval(3,-3,0,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(3,-3,1,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(3,-3,2,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(3,-2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(3,-2,1,5).unwrap(),Some((1,2)));assert_eq!(rei_signed_interval(3,-2,2,5).unwrap(),Some((1,2)));assert_eq!(rei_signed_interval(3,-1,0,5).unwrap(),Some((3,3)));assert_eq!(rei_signed_interval(3,-1,1,5).unwrap(),Some((2,4)));assert_eq!(rei_signed_interval(3,-1,2,5).unwrap(),Some((1,5)));assert_eq!(rei_signed_interval(3,0,0,5).unwrap(),None);assert_eq!(rei_signed_interval(3,0,1,5).unwrap(),None);assert_eq!(rei_signed_interval(3,0,2,5).unwrap(),None);assert_eq!(rei_signed_interval(3,1,0,5).unwrap(),None);assert_eq!(rei_signed_interval(3,1,1,5).unwrap(),None);assert_eq!(rei_signed_interval(3,1,2,5).unwrap(),None);assert_eq!(rei_signed_interval(3,2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(3,2,1,5).unwrap(),None);assert_eq!(rei_signed_interval(3,2,2,5).unwrap(),None);assert_eq!(rei_signed_interval(3,3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(3,3,1,5).unwrap(),None);assert_eq!(rei_signed_interval(3,3,2,5).unwrap(),None);assert_eq!(rei_signed_interval(4,-3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(4,-3,1,5).unwrap(),Some((1,1)));assert_eq!(rei_signed_interval(4,-3,2,5).unwrap(),Some((1,2)));assert_eq!(rei_signed_interval(4,-2,0,5).unwrap(),Some((2,2)));assert_eq!(rei_signed_interval(4,-2,1,5).unwrap(),Some((2,2)));assert_eq!(rei_signed_interval(4,-2,2,5).unwrap(),Some((1,3)));assert_eq!(rei_signed_interval(4,-1,0,5).unwrap(),Some((4,4)));assert_eq!(rei_signed_interval(4,-1,1,5).unwrap(),Some((3,5)));assert_eq!(rei_signed_interval(4,-1,2,5).unwrap(),Some((2,5)));assert_eq!(rei_signed_interval(4,0,0,5).unwrap(),None);assert_eq!(rei_signed_interval(4,0,1,5).unwrap(),None);assert_eq!(rei_signed_interval(4,0,2,5).unwrap(),None);assert_eq!(rei_signed_interval(4,1,0,5).unwrap(),None);assert_eq!(rei_signed_interval(4,1,1,5).unwrap(),None);assert_eq!(rei_signed_interval(4,1,2,5).unwrap(),None);assert_eq!(rei_signed_interval(4,2,0,5).unwrap(),None);assert_eq!(rei_signed_interval(4,2,1,5).unwrap(),None);assert_eq!(rei_signed_interval(4,2,2,5).unwrap(),None);assert_eq!(rei_signed_interval(4,3,0,5).unwrap(),None);assert_eq!(rei_signed_interval(4,3,1,5).unwrap(),None);assert_eq!(rei_signed_interval(4,3,2,5).unwrap(),None);
 // Budget exhaustion is a distinct outcome, never NoSolution.
 let n=f64::from_bits(313989944336);let u=f64::from_bits(5352011796590);
 match rei_subnormal_pair_search(n,u,u,&nodes1,1).unwrap() {
  ReiSubnormalSearchOutcome::Budget{next_k,evaluations,intervals}=>{assert!(next_k>=1);assert_eq!(evaluations,1);assert_eq!(intervals,2348);},
  _=>panic!("budget must not imply infeasibility")
 }
 assert_eq!(rei_checked_positive_shift(1,126).unwrap(),1_i128<<126);
 assert!(rei_checked_positive_shift(3,126).is_err());
 assert!(rei_checked_positive_shift(1,127).is_err());
 assert!(rei_signed_interval(i128::MIN,1,1,5).is_err());
 assert!(rei_round_dyadic_product(i128::MAX,2,1).is_err());
 assert_eq!(rei_round_dyadic_product(1,1,2).unwrap(),0);
 assert_eq!(rei_round_dyadic_product(1,3,2).unwrap(),2);
 assert_eq!(rei_round_dyadic_product(1,5,2).unwrap(),2);
 // Normal U, subnormal q, and an unrepresentable common denominator are unsupported.
 assert!(rei_subnormal_pair_search(2.0*eta,f64::MIN_POSITIVE,f64::MIN_POSITIVE,&[(1.0,2.0*eta)],10).is_err());
 assert!(rei_subnormal_pair_search(2.0*eta,eta,eta,&[(eta,2.0*eta)],10).is_err());
 assert!(rei_subnormal_pair_search(2.0*eta,eta,eta,&[(1e-200,2.0*eta)],10).is_err());
 assert!(rei_subnormal_pair_search(2.0*eta,eta,eta,&[(f64::MAX,2.0*eta)],10).is_err());
 // Equal-q intervals retain their full positivity range; no sign pruning.
 assert_eq!(rei_signed_interval(0,0,1,12).unwrap(),Some((1,12)));
 assert_eq!(rei_signed_interval(2,0,1,12).unwrap(),None);
 assert_eq!(rei_signed_interval(7,-2,1,10).unwrap(),Some((3,4)));
 for (n,u,v) in [(1.0,1.0,vec![(1.0,1.0)]),(10.0*eta,10.0*eta,vec![(1.0,10.0*eta)])] {
  let got=trial(n,u,1.0,v.clone(),true,0.0).unwrap();
  assert!(v.iter().zip(&got).all(|(a,b)|a.0.to_bits()==b.0.to_bits()&&a.1.to_bits()==b.1.to_bits()));
 }
 assert!(trial(1.0,1.0,1.0,vec![(1.0,1.1)],true,0.0).is_err());
 assert!(trial(n,u,3.4612670487769624,nodes1,true,1e-8).is_err());
 match rei_subnormal_pair_search(2.0*eta,5.0*eta,5.0*eta,&[(1.0,eta),(2.0,eta)],65536).unwrap() {
  ReiSubnormalSearchOutcome::NoSolution{evaluations,intervals}=>{assert_eq!(evaluations,0);assert_eq!(intervals,0);},
  _=>panic!("no eligible donor")
 }
 println!("signed_intervals=189 controls=PASS");
}
