//! Additive C8 study, compiled against source-identical Grackle-owner Rust files.
//! Exactly timed *lookup* experiments. No initial-value thermochemistry history.
use rei_microphysics::{
    igm_rates::igm_rates,
    rate_table::{igm_branch_knots, igm_flat, IgmRateTable},
};
use std::{hint::black_box, time::Instant};

fn temperatures(n: usize, random: bool) -> Vec<f64> {
    let mut state = 0x172942a3d8c56f01_u64;
    let width = 1.0e6_f64.ln();
    (0..n)
        .map(|i| {
            let u = if random {
                state = state
                    .wrapping_mul(6364136223846793005)
                    .wrapping_add(1442695040888963407);
                (state >> 11) as f64 / ((1_u64 << 53) as f64)
            } else {
                (i as f64 + 0.371) / n as f64
            };
            (width * u).exp()
        })
        .collect()
}

fn relative(a: f64, b: f64) -> f64 {
    ((a - b) / b).abs()
}

#[test]
fn c8_source_referenced_pointwise_accuracy_masks_and_fallbacks() {
    let build = Instant::now();
    let table = IgmRateTable::build_default().unwrap();
    let build_s = build.elapsed().as_secs_f64();
    let mut temps = temperatures(16_384, true);
    temps.extend(temperatures(4096, false));
    temps.extend([1.0, 6.137, 20.0, 100.0, 5500.0, 9284.0, 1.0e4, 1.0e5, 1.0e6]);
    for t in igm_branch_knots() {
        if (1.0..=1.0e6).contains(&t) {
            temps.push(t);
            temps.push(f64::from_bits(t.to_bits() - 1));
            temps.push(f64::from_bits(t.to_bits() + 1));
        }
    }
    let mut worst = [0.0_f64; 15];
    let mut worst_t = [0.0_f64; 15];
    let mut exact_zero = 0_u32;
    let mut structural_masks = 0_u32;
    for &t in &temps {
        let ref_rate = igm_rates(t).unwrap();
        let interp = table.rates(t).unwrap();
        let ref_vec = igm_flat(ref_rate);
        let new_vec = igm_flat(interp);
        for j in 0..15 {
            let a = new_vec[j];
            let b = ref_vec[j];
            if b == 0.0 {
                assert_eq!(a, 0.0, "zero mismatch at {t}, j={j}");
                exact_zero += 1;
            } else if !b.is_normal() {
                assert_eq!(a, b, "non-normal must direct-fallback at {t}, j={j}");
            } else {
                assert!(a.is_finite() && a > 0.0, "positivity at {t}, j={j}");
                let e = relative(a, b);
                if e > worst[j] {
                    worst[j] = e;
                    worst_t[j] = t;
                }
            }
        }
        for j in 0..3 {
            assert_eq!(
                interp.diagnostics.ci_floor_cm3_s[j] != 0.0,
                ref_rate.diagnostics.ci_floor_cm3_s[j] != 0.0,
                "CI floor mask mismatch at {t}"
            );
            assert_eq!(
                interp.diagnostics.ce_cap_erg[j] != 0.0,
                ref_rate.diagnostics.ce_cap_erg[j] != 0.0,
                "CE cap mask mismatch at {t}"
            );
        }
        assert_eq!(
            interp.diagnostics.dr_low_branch,
            ref_rate.diagnostics.dr_low_branch
        );
        assert_eq!(
            interp.dr_cooling_erg_cm3_s == 0.0,
            ref_rate.dr_cooling_erg_cm3_s == 0.0
        );
        structural_masks += 1;
    }
    let (channel, error) = worst
        .iter()
        .enumerate()
        .max_by(|a, b| a.1.total_cmp(b.1))
        .unwrap();
    assert!(
        *error < 1.0e-5,
        "frozen acceptance exceeded: channel={channel}, error={error}"
    );
    for t in [0.0, -3.0, 0.9999, 1.0e6 + 1.0, f64::INFINITY, f64::NAN] {
        assert!(table.rates(t).is_err());
    }
    println!("C8_ACCURACY {{\"queries\":{},\"nodes\":{},\"blocked_cells\":{},\"table_bytes\":{},\"build_s\":{:.12},\"max_relative_error\":{:.16e},\"worst_channel\":{},\"worst_t_K\":{:.16e},\"exact_zero_samples\":{},\"exact_masks\":{}}}",
             temps.len(), table.grid().nodes(),table.grid().blocked_cells(),table.storage_bytes(),
             build_s,error,channel,worst_t[channel],exact_zero,structural_masks);
    for j in 0..15 {
        println!(
            "C8_CHANNEL {{\"channel\":{},\"max_relative_error\":{:.16e},\"worst_t_K\":{:.16e}}}",
            j, worst[j], worst_t[j]
        );
    }
}

fn median(mut v: Vec<f64>) -> f64 {
    v.sort_by(|a, b| a.total_cmp(b));
    v[v.len() / 2]
}
fn accumulate_direct(ts: &[f64], scales: &[f64; 15]) -> f64 {
    let mut s = 0.0;
    for &t in ts {
        let r = black_box(igm_rates(black_box(t)).unwrap());
        let vals = igm_flat(r);
        for j in 0..15 {
            s += vals[j] / scales[j];
        }
    }
    black_box(s)
}
fn accumulate_scalar(ts: &[f64], table: &IgmRateTable, scales: &[f64; 15]) -> f64 {
    let mut s = 0.0;
    for &t in ts {
        let r = black_box(table.rates(black_box(t)).unwrap());
        let vals = igm_flat(r);
        for j in 0..15 {
            s += vals[j] / scales[j];
        }
    }
    black_box(s)
}
fn accumulate_batch(ts: &[f64], table: &IgmRateTable, scales: &[f64; 15], workers: usize) -> f64 {
    let rows = if workers == 0 {
        table.batch_soa(black_box(ts)).unwrap()
    } else {
        table.batch_parallel(black_box(ts), workers).unwrap()
    };
    let mut s = 0.0;
    for (i, _) in ts.iter().enumerate() {
        for (j, column) in rows.iter().enumerate() {
            s += black_box(column[i]) / scales[j];
        }
    }
    black_box(s)
}

#[test]
fn c8_matched_accuracy_and_amortization_benchmark() {
    let start = Instant::now();
    let table = IgmRateTable::build_default().unwrap();
    let build_s = start.elapsed().as_secs_f64();
    let scales = igm_flat(igm_rates(1e4).unwrap());
    assert!(scales.iter().all(|s| s.is_finite() && *s > 0.0));
    for &n in &[4096_usize, 32_768] {
        for random in [false, true] {
            let ts = temperatures(n, random);
            let scenario = if random {
                "random_logT"
            } else {
                "ordered_logT"
            };
            // warming avoids comparing initialization with hot lookup time.
            let warm = &ts[..ts.len().min(16)];
            black_box(accumulate_direct(warm, &scales));
            black_box(accumulate_scalar(warm, &table, &scales));
            black_box(accumulate_batch(warm, &table, &scales, 0));
            black_box(accumulate_batch(warm, &table, &scales, 4));
            let mut records: [Vec<f64>; 4] = std::array::from_fn(|_| Vec::new());
            let mut checks = [0.0_f64; 4];
            // Rotate modes to reduce fixed first-position and cache bias.
            for sample in 0..3 {
                for shift in 0..4 {
                    let method = (shift + sample) % 4;
                    let tick = Instant::now();
                    let checksum = match method {
                        0 => accumulate_direct(&ts, &scales),
                        1 => accumulate_scalar(&ts, &table, &scales),
                        2 => accumulate_batch(&ts, &table, &scales, 0),
                        _ => accumulate_batch(&ts, &table, &scales, 4),
                    };
                    records[method].push(tick.elapsed().as_secs_f64());
                    checks[method] = checksum;
                }
            }
            for sum in &checks[1..] {
                assert!(
                    ((sum - checks[0]) / checks[0]).abs() < 1e-5,
                    "benchmark only valid for matched sampled accuracy"
                );
            }
            for (j, method) in ["direct", "table_scalar", "table_soa", "table_parallel4"]
                .into_iter()
                .enumerate()
            {
                let med = median(records[j].clone());
                let per_query = med / n as f64;
                let direct_med = median(records[0].clone());
                let gain = (direct_med - med) / n as f64;
                let break_even = if gain > 0.0 {
                    build_s / gain
                } else {
                    f64::INFINITY
                };
                let breakeven_text = if break_even.is_finite() {
                    format!("{break_even:.4}")
                } else {
                    "null".into()
                };
                println!("C8_BENCH {{\"distribution\":\"{scenario}\",\"n\":{n},\"method\":\"{method}\",\"samples\":3,\"median_s\":{med:.12},\"per_query_s\":{per_query:.14},\"speedup_vs_direct\":{:.9},\"break_even_queries\":{breakeven_text},\"checksum_relative_difference\":{:.4e},\"build_s\":{build_s:.12},\"table_bytes\":{}}}",
                   direct_med/med,(checks[j]-checks[0]).abs()/checks[0].abs(),table.storage_bytes());
            }
        }
    }
}
