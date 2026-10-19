
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

  }
  return Err(bad("AXBI_COVARIANT_MOMENT_FIT"));
 }
 Ok(result)
}

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

fn main() {
 let eta=f64::from_bits(1);
 let first=vec![(1.70606999820844116e+01f64,1.69809363747175183e-310f64),(1.70566122005563692e+01f64,2.91853783441636064e-310f64),(1.70498384935290268e+01f64,2.74134223271880488e-310f64),(1.70412919096467270e+01f64,1.89719038933713474e-310f64),(1.70321264621734549e+01f64,1.09425101187942332e-310f64),(1.70235798782911552e+01f64,5.66572876514107474e-311f64),(1.70168061712638128e+01f64,2.67424850984922108e-311f64),(1.70127183897357739e+01f64,9.52392304622319258e-312f64),(1.70107342430692761e+01f64,8.45431040238420984e-312f64),(1.70066464615412336e+01f64,1.45305442696263339e-311f64),(1.69998727545138948e+01f64,1.36483393160041574e-311f64),(1.69913261706315915e+01f64,9.44555476207708382e-312f64),(1.69821607231583194e+01f64,5.44795499400288584e-312f64),(1.69736141392760196e+01f64,2.82080025383975409e-312f64),(1.69668404322486772e+01f64,1.33142993392389483e-312f64),(1.69627526507206383e+01f64,4.74168207832563380e-313f64),(1.69607685040541405e+01f64,4.20915330006965138e-313f64),(1.69566807225261016e+01f64,7.23433200971736691e-313f64),(1.69499070154987592e+01f64,6.79510802635082896e-313f64),(1.69413604316164594e+01f64,4.70266480711961823e-313f64),(1.69321949841431874e+01f64,2.71237707752421967e-313f64),(1.69236484002608840e+01f64,1.40439375088584062e-313f64),(1.69168746932335452e+01f64,6.62879931461484069e-314f64),(1.69127869117055027e+01f64,2.36074449810851734e-314f64),(1.69108027650390049e+01f64,2.09561403131216902e-314f64),(1.69067149835109660e+01f64,3.60176182373394997e-314f64),(1.68999412764836237e+01f64,3.38308507890147859e-314f64),(1.68913946926013239e+01f64,2.34131894263295492e-314f64),(1.68822292451280518e+01f64,1.35041303016031020e-314f64),(1.68736826612457520e+01f64,6.99206477138999165e-315f64),(1.68669089542184096e+01f64,3.30028484903173199e-315f64),(1.68628211726903707e+01f64,1.17534547720080890e-315f64),(1.68608370260238729e+01f64,1.04334479260647887e-315f64),(1.68567492444958305e+01f64,1.79321162224872580e-315f64),(1.68499755374684916e+01f64,1.68433888175338037e-315f64),(1.68414289535861883e+01f64,1.16567406313296316e-315f64),(1.68322635061129162e+01f64,6.72331057467949860e-316f64),(1.68237169222306164e+01f64,3.48114405095188080e-316f64),(1.68169432152032741e+01f64,1.64311505709896073e-316f64),(1.68128554336752352e+01f64,5.85170066363693220e-317f64),(1.68108712870087373e+01f64,5.19450788131134376e-317f64),(1.68067835054806949e+01f64,8.92787491479341013e-317f64),(1.68000097984533561e+01f64,8.38582956595322845e-317f64),(1.67914632145710527e+01f64,5.80354951985889015e-317f64),(1.67822977670977806e+01f64,3.34733921648257105e-317f64),(1.67737511832154809e+01f64,1.73315955859138418e-317f64),(1.67669774761881420e+01f64,8.18058580348914949e-318f64),(1.67628896946600996e+01f64,2.91339147842728738e-318f64),(1.67609055479936018e+01f64,2.58619156381246345e-318f64),(1.67568177664655629e+01f64,4.44492581134473390e-318f64),(1.67500440594382205e+01f64,4.17505727427332821e-318f64),(1.67414974755559207e+01f64,2.88941941329107010e-318f64),(1.67323320280826486e+01f64,1.66654271130002554e-318f64),(1.67237854442003453e+01f64,8.62890591118195502e-319f64),(1.67170117371730065e+01f64,4.07287955805690001e-319f64),(1.67129239556449640e+01f64,1.45047792306073160e-319f64),(1.67109398089784662e+01f64,1.28758447962687262e-319f64),(1.67068520274504273e+01f64,2.21301884085211152e-319f64),(1.67000783204230849e+01f64,2.07863298518329246e-319f64),(1.66915317365407851e+01f64,1.43857094099595756e-319f64),(1.66823662890675131e+01f64,8.29733845625789446e-320f64),(1.66738197051852133e+01f64,4.29590079058963870e-320f64),(1.66670459981578709e+01f64,2.02764541053247582e-320f64),(1.66629582166298320e+01f64,7.22323974219902448e-321f64),(1.66609740699633342e+01f64,6.41297208301938014e-321f64),(1.66568862884352917e+01f64,1.10176639022597979e-320f64),(1.66501125814079529e+01f64,1.03506752803741151e-320f64),(1.66415659975256496e+01f64,7.16395186469807489e-321f64),(1.66324005500523775e+01f64,4.13038879923282111e-321f64),(1.66238539661700777e+01f64,2.13930424649259754e-321f64),(1.66170802591427353e+01f64,1.00789391751614295e-321f64),(1.66129924776146964e+01f64,3.60667921464109977e-322f64),(1.66110083309481986e+01f64,3.21142669796810254e-322f64),(1.66069205494201562e+01f64,5.48412866883783664e-322f64),(1.66001468423928173e+01f64,5.13828271674896406e-322f64),(1.65916002585105176e+01f64,3.55727265005697512e-322f64),(1.65824348110372455e+01f64,2.07507571253323549e-322f64),(1.65738882271549421e+01f64,1.08694442085074240e-322f64),(1.65671145201276033e+01f64,4.94065645841246544e-323f64),(1.65630267385995609e+01f64,1.97626258336498618e-323f64),(1.65610425919330631e+01f64,1.48219693752373963e-323f64),(1.65569548104050241e+01f64,2.96439387504747927e-323f64),(1.65501811033776818e+01f64,2.47032822920623272e-323f64),(1.65416345194953820e+01f64,1.97626258336498618e-323f64),(1.65324690720221099e+01f64,9.88131291682493088e-324f64),(1.65239224881398066e+01f64,4.94065645841246544e-324f64),(1.65171487811124678e+01f64,4.94065645841246544e-324f64),(1.65130609995844253e+01f64,0.00000000000000000e+00f64),(1.65110768529179275e+01f64,0.00000000000000000e+00f64),(1.65069890713898886e+01f64,0.00000000000000000e+00f64),(1.65002153643625462e+01f64,0.00000000000000000e+00f64),(1.64916687804802464e+01f64,0.00000000000000000e+00f64),(1.64825033330069743e+01f64,0.00000000000000000e+00f64),(1.64739567491246746e+01f64,0.00000000000000000e+00f64),(1.64671830420973322e+01f64,0.00000000000000000e+00f64),(1.64630952605692933e+01f64,0.00000000000000000e+00f64),(1.64611111139027955e+01f64,0.00000000000000000e+00f64),(1.64570233323747530e+01f64,0.00000000000000000e+00f64),(1.64502496253474142e+01f64,0.00000000000000000e+00f64),(1.64417030414651109e+01f64,0.00000000000000000e+00f64),(1.64325375939918388e+01f64,0.00000000000000000e+00f64),(1.64239910101095390e+01f64,0.00000000000000000e+00f64),(1.64172173030821966e+01f64,0.00000000000000000e+00f64),(1.64131295215541577e+01f64,0.00000000000000000e+00f64),(1.64111453748876599e+01f64,0.00000000000000000e+00f64),(1.64070575933596210e+01f64,0.00000000000000000e+00f64),(1.64002838863322786e+01f64,0.00000000000000000e+00f64),(1.63917373024499788e+01f64,0.00000000000000000e+00f64),(1.63825718549767068e+01f64,0.00000000000000000e+00f64),(1.63740252710944034e+01f64,0.00000000000000000e+00f64),(1.63672515640670646e+01f64,0.00000000000000000e+00f64),(1.63631637825390222e+01f64,0.00000000000000000e+00f64),(1.63611796358725243e+01f64,0.00000000000000000e+00f64),(1.63570918543444854e+01f64,0.00000000000000000e+00f64),(1.63503181473171431e+01f64,0.00000000000000000e+00f64),(1.63417715634348433e+01f64,0.00000000000000000e+00f64),(1.63326061159615712e+01f64,0.00000000000000000e+00f64),(1.63240595320792714e+01f64,0.00000000000000000e+00f64),(1.63172858250519290e+01f64,0.00000000000000000e+00f64),(1.63131980435238901e+01f64,0.00000000000000000e+00f64),(1.63112138968573923e+01f64,0.00000000000000000e+00f64),(1.63071261153293499e+01f64,0.00000000000000000e+00f64),(1.63003524083020075e+01f64,0.00000000000000000e+00f64),(1.62918058244197077e+01f64,0.00000000000000000e+00f64),(1.62826403769464356e+01f64,0.00000000000000000e+00f64),(1.62740937930641358e+01f64,0.00000000000000000e+00f64),(1.62673200860367935e+01f64,0.00000000000000000e+00f64),(1.62632323045087546e+01f64,0.00000000000000000e+00f64)];
 let n=f64::from_bits(240243477644326);let u=f64::from_bits(4094958919588752);
 assert!(trial(n,u,3.4612670487769624,first.clone(),false,0.0).is_err());
 let fixed=trial(n,u,3.4612670487769624,first.clone(),true,6.769278295586412e-17).unwrap();
 assert_eq!((sum(fixed.iter().map(|x|x.1))-n).abs().to_bits(),0);
 assert_eq!((sum(fixed.iter().map(|x|x.0*x.1))-u).abs().to_bits(),4);
 assert_eq!(rei_subnormal_l1(&first,&fixed),5);
 let nodes=vec![(1.70607059180523919e+01f64,8.79737553616299461e-313f64),(1.70566425953415184e+01f64,1.51201752243015279e-312f64),(1.70499094180882302e+01f64,1.42021715187899706e-312f64),(1.70414139718049285e+01f64,9.82884332774444007e-313f64),(1.70323033648368174e+01f64,5.66902605949671962e-313f64),(1.70238079185535121e+01f64,2.93526473056583012e-313f64),(1.70170747413002239e+01f64,1.38545766258952735e-313f64),(1.70130114185893504e+01f64,4.93409348948156560e-314f64),(1.70110391438588202e+01f64,4.37995537260147596e-314f64),(1.70069758211479432e+01f64,7.52789197601767240e-314f64),(1.70002426438946550e+01f64,7.07084484394081472e-314f64),(1.69917471976113532e+01f64,4.89349294741386923e-314f64),(1.69826365906432422e+01f64,2.82244187979781846e-314f64),(1.69741411443599368e+01f64,1.46138225818514834e-314f64),(1.69674079671066487e+01f64,6.89778753539979937e-315f64),(1.69633446443957752e+01f64,2.45654049732874772e-315f64),(1.69613723696652450e+01f64,2.18065137511024977e-315f64),(1.69573090469543679e+01f64,3.74791672327988066e-315f64),(1.69505758697010833e+01f64,3.52036635638712005e-315f64),(1.69420804234177780e+01f64,2.43632668086600272e-315f64),(1.69329698164496669e+01f64,1.40521107029457680e-315f64),(1.69244743701663616e+01f64,7.27579385079310996e-316f64),(1.69177411929130770e+01f64,3.43420618418033111e-316f64),(1.69136778702021999e+01f64,1.22303949662134925e-316f64),(1.69117055954716697e+01f64,1.08568237956500552e-316f64),(1.69076422727607927e+01f64,1.86597784277907813e-316f64),(1.69009090955075081e+01f64,1.75268720680387194e-316f64),(1.68924136492242027e+01f64,1.21297562644838598e-316f64),(1.68833030422560917e+01f64,6.99613406897211620e-317f64),(1.68748075959727863e+01f64,3.62240433601693497e-317f64),(1.68680744187195018e+01f64,1.70979074760873906e-317f64),(1.68640110960086247e+01f64,6.08915651807856875e-318f64),(1.68620388212780945e+01f64,5.40529555438740734e-318f64),(1.68579754985672210e+01f64,9.29015843091942098e-318f64),(1.68512423213139328e+01f64,8.72611332700122028e-318f64),(1.68427468750306275e+01f64,6.03904838027734952e-318f64),(1.68336362680625165e+01f64,3.48316774383724655e-318f64),(1.68251408217792147e+01f64,1.80348782701430226e-318f64),(1.68184076445259265e+01f64,8.51255345158634146e-319f64),(1.68143443218150530e+01f64,3.03163620944647292e-319f64),(1.68123720470845193e+01f64,2.69112616633268580e-319f64),(1.68083087243736458e+01f64,4.62529435667199777e-319f64),(1.68015755471203576e+01f64,4.34446744357583324e-319f64),(1.67930801008370523e+01f64,3.00668589433148997e-319f64),(1.67839694938689448e+01f64,1.73417041690277537e-319f64),(1.67754740475856394e+01f64,8.97914904751881469e-320f64),(1.67687408703323513e+01f64,4.23809511002621286e-320f64),(1.67646775476214778e+01f64,1.50937054804500819e-320f64),(1.67627052728909440e+01f64,1.33990603152146063e-320f64),(1.67586419501800705e+01f64,2.30283997526605014e-320f64),(1.67519087729267824e+01f64,2.16301939749297737e-320f64),(1.67434133266434806e+01f64,1.49701890689897703e-320f64),(1.67343027196753695e+01f64,8.63626748930498959e-321f64),(1.67258072733920642e+01f64,4.47129409486328122e-321f64),(1.67190740961387760e+01f64,2.10966030774212274e-321f64),(1.67150107734279025e+01f64,7.50979781678694747e-322f64),(1.67130384986973723e+01f64,6.66988621885682835e-322f64),(1.67089751759864953e+01f64,1.14623229835169198e-321f64),(1.67022419987332071e+01f64,1.07706310793391747e-321f64),(1.66937465524499054e+01f64,7.46039125220282282e-322f64),(1.66846359454817943e+01f64,4.29837111881884493e-322f64),(1.66761404991984890e+01f64,2.22329540628560945e-322f64),(1.66694073219452008e+01f64,1.03753785626661774e-322f64),(1.66653439992343273e+01f64,3.95252516672997235e-323f64),(1.66633717245037971e+01f64,3.45845952088872581e-323f64),(1.66593084017929201e+01f64,5.92878775009495853e-323f64),(1.66525752245396355e+01f64,5.43472210425371199e-323f64),(1.66440797782563301e+01f64,3.95252516672997235e-323f64),(1.66349691712882191e+01f64,1.97626258336498618e-323f64),(1.66264737250049137e+01f64,9.88131291682493088e-324f64),(1.66197405477516291e+01f64,4.94065645841246544e-324f64),(1.66156772250407521e+01f64,0.00000000000000000e+00f64),(1.66137049503102219e+01f64,0.00000000000000000e+00f64),(1.66096416275993448e+01f64,4.94065645841246544e-324f64),(1.66029084503460602e+01f64,4.94065645841246544e-324f64),(1.65944130040627549e+01f64,0.00000000000000000e+00f64),(1.65853023970946438e+01f64,0.00000000000000000e+00f64),(1.65768069508113385e+01f64,0.00000000000000000e+00f64),(1.65700737735580539e+01f64,0.00000000000000000e+00f64),(1.65660104508471768e+01f64,0.00000000000000000e+00f64),(1.65640381761166466e+01f64,0.00000000000000000e+00f64),(1.65599748534057731e+01f64,0.00000000000000000e+00f64),(1.65532416761524850e+01f64,0.00000000000000000e+00f64),(1.65447462298691796e+01f64,0.00000000000000000e+00f64),(1.65356356229010686e+01f64,0.00000000000000000e+00f64),(1.65271401766177668e+01f64,0.00000000000000000e+00f64),(1.65204069993644787e+01f64,0.00000000000000000e+00f64),(1.65163436766536051e+01f64,0.00000000000000000e+00f64),(1.65143714019230714e+01f64,0.00000000000000000e+00f64),(1.65103080792121979e+01f64,0.00000000000000000e+00f64),(1.65035749019589097e+01f64,0.00000000000000000e+00f64),(1.64950794556756044e+01f64,0.00000000000000000e+00f64),(1.64859688487074969e+01f64,0.00000000000000000e+00f64),(1.64774734024241916e+01f64,0.00000000000000000e+00f64),(1.64707402251709034e+01f64,0.00000000000000000e+00f64),(1.64666769024600299e+01f64,0.00000000000000000e+00f64),(1.64647046277294962e+01f64,0.00000000000000000e+00f64),(1.64606413050186227e+01f64,0.00000000000000000e+00f64),(1.64539081277653345e+01f64,0.00000000000000000e+00f64),(1.64454126814820327e+01f64,0.00000000000000000e+00f64),(1.64363020745139217e+01f64,0.00000000000000000e+00f64),(1.64278066282306163e+01f64,0.00000000000000000e+00f64),(1.64210734509773282e+01f64,0.00000000000000000e+00f64),(1.64170101282664547e+01f64,0.00000000000000000e+00f64),(1.64150378535359245e+01f64,0.00000000000000000e+00f64),(1.64109745308250474e+01f64,0.00000000000000000e+00f64),(1.64042413535717628e+01f64,0.00000000000000000e+00f64),(1.63957459072884575e+01f64,0.00000000000000000e+00f64),(1.63866353003203464e+01f64,0.00000000000000000e+00f64),(1.63781398540370411e+01f64,0.00000000000000000e+00f64),(1.63714066767837565e+01f64,0.00000000000000000e+00f64),(1.63673433540728794e+01f64,0.00000000000000000e+00f64),(1.63653710793423492e+01f64,0.00000000000000000e+00f64),(1.63613077566314722e+01f64,0.00000000000000000e+00f64),(1.63545745793781876e+01f64,0.00000000000000000e+00f64),(1.63460791330948823e+01f64,0.00000000000000000e+00f64),(1.63369685261267712e+01f64,0.00000000000000000e+00f64),(1.63284730798434659e+01f64,0.00000000000000000e+00f64),(1.63217399025901813e+01f64,0.00000000000000000e+00f64),(1.63176765798793042e+01f64,0.00000000000000000e+00f64),(1.63157043051487740e+01f64,0.00000000000000000e+00f64),(1.63116409824379005e+01f64,0.00000000000000000e+00f64),(1.63049078051846124e+01f64,0.00000000000000000e+00f64),(1.62964123589013070e+01f64,0.00000000000000000e+00f64),(1.62873017519331960e+01f64,0.00000000000000000e+00f64),(1.62788063056498942e+01f64,0.00000000000000000e+00f64),(1.62720731283966060e+01f64,0.00000000000000000e+00f64),(1.62680098056857290e+01f64,0.00000000000000000e+00f64)];
 let n=f64::from_bits(1244638132025);let u=f64::from_bits(21215026808689);
 assert!(trial(n,u,3.4612670487769624,nodes.clone(),false,0.0).is_err());
 let repaired=trial(n,u,3.4612670487769624,nodes.clone(),true,7.28135986364630949e-17).unwrap();
 let metadata=rei_subnormal_pair_candidate(n,u,u,&nodes).unwrap();
 assert_eq!(metadata.pair,Some((24,0)));
 assert_eq!(metadata.count_distance,0);assert_eq!(metadata.l1_ticks,2);
 assert_eq!((sum(repaired.iter().map(|x|x.1))-n).abs().to_bits(),0);
 assert_eq!((sum(repaired.iter().map(|x|x.0*x.1))-u).abs().to_bits(),1);
 for (old,new) in nodes.iter().zip(&repaired) {
  assert_eq!(old.0.to_bits(),new.0.to_bits());
  assert_eq!(old.1>0.0,new.1>0.0);
 }
 // The exact-count base is restored first, then the same pair is checked.
 let mut combined=nodes.clone();combined[1].1=f64::from_bits(combined[1].1.to_bits()+1);
 let metadata=rei_subnormal_pair_candidate(n,u,u,&combined).unwrap();
 assert_eq!(metadata.count_distance,1);assert_eq!(metadata.l1_ticks,3);
 assert_eq!(metadata.pair,Some((24,0)));
 assert_eq!(metadata.after_ticks,n.to_bits() as u128);
 assert!(trial(n,u,3.4612670487769624,nodes.clone(),true,1e-8).is_err());
 // Originally passing normal and subnormal vectors remain byte-identical.
 for (n,u,passing) in [(1.0,1.0,vec![(1.0,1.0)]),
                       (10.0*eta,10.0*eta,vec![(1.0,10.0*eta)])] {
  let got=trial(n,u,1.0,passing.clone(),true,0.0).unwrap();
  assert!(passing.iter().zip(&got).all(|(a,b)|a.0.to_bits()==b.0.to_bits()&&a.1.to_bits()==b.1.to_bits()));
 }
 assert!(trial(1.0,1.0,1.0,vec![(1.0,1.1)],true,0.0).is_err());
 // No eligible positive-support donor; old error remains.
 assert!(trial(2.0*eta,5.0*eta,1.0,vec![(1.0,eta),(2.0,eta)],true,0.0).is_err());
 // Exact count alone cannot bypass the original energy gate.
 assert!(trial(100.0*eta,6045.0*eta,1.0,vec![(100.0,60.0*eta),(1.0,45.0*eta)],true,0.0).is_err());
 assert!(rei_subnormal_pair_candidate(eta,eta,eta,&[(1.0,-eta)]).is_none());
 assert!(rei_subnormal_pair_candidate(eta,eta,eta,&[(f64::NAN,eta)]).is_none());
 assert!(rei_subnormal_pair_candidate(eta,eta,eta,&[(0.0,eta)]).is_none());
 assert!(rei_subnormal_pair_candidate(eta,eta,eta,&[(1.0,f64::MIN_POSITIVE)]).is_none());
 // Every stored zero remains zero; one-tick donors are never removed.
 let no_pair=vec![(1.0,eta),(2.0,0.0)];
 assert!(rei_subnormal_pair_candidate(eta,2.0*eta,2.0*eta,&no_pair).is_none());
 println!("captured_count_energy_ticks=4 later_pair_energy_ticks=1 donor=24 receiver=0 controls=PASS");
}
