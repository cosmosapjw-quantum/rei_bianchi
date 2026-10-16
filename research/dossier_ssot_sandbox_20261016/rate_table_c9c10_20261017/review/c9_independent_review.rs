//! C9 independent, source-identical review: fair parallel baseline and
//! EOS-bound implicit RHS, with separate value-versus-temperature slope tests.
//! This test is additive: original Grackle and PR150 Rust sources are untouched.
use rei_microphysics::{
    axbi_rates::AxbiProvider,
    igm_rates::igm_rates,
    igm_state::IgmGasState,
    igm_thermal::{IgmPhotoInput, IgmPointRhs},
    rate_table::{igm_flat, IgmRateBackend, IgmRateTable},
};
use std::{hint::black_box, sync::Arc, time::Instant};

const TARGET_MAX_COEFF_REL: f64 = 1e-5; // preexisting immutable scientific gate
const RHS_NORM_TOL: f64 = 1e-5;

fn max_abs(xs: impl Iterator<Item = f64>) -> f64 {
    xs.map(f64::abs).fold(0.0_f64, f64::max)
}
fn ledger_residual(r: &IgmPointRhs) -> f64 {
    r.thermal_micro_erg_cm3_s + r.binding_micro_erg_cm3_s + r.escape_erg_cm3_s
        - r.photo_input_erg_cm3_s
        - r.cmb_to_gas_erg_cm3_s
}
fn ledger_scale(r: &IgmPointRhs) -> f64 {
    1e-250
        + r.thermal_micro_erg_cm3_s.abs()
        + r.binding_micro_erg_cm3_s.abs()
        + r.escape_erg_cm3_s.abs()
        + r.photo_input_erg_cm3_s.abs()
        + r.cmb_to_gas_erg_cm3_s.abs()
}
fn event_scale(r: &IgmPointRhs) -> f64 {
    1e-150
        + r.photo_events_cm3_s.iter().sum::<f64>()
        + r.ci_events_cm3_s.iter().sum::<f64>()
        + r.rr_events_cm3_s.iter().sum::<f64>()
        + r.dr_events_cm3_s
}

#[test]
fn c9_implicit_rhs_source_owner_and_ledger() {
    let table = Arc::new(IgmRateTable::build_default().unwrap());
    let direct = IgmRateBackend::Direct;
    let lookup = IgmRateBackend::Table(table);
    let provider = AxbiProvider;
    let nh = 1.5e-3;
    let nhe = 1.2e-4;
    let photo = IgmPhotoInput {
        gamma_s: [1e-13, 2e-14, 3e-15],
        heat_erg_per_absorber_s: [1e-24, 2e-25, 3e-26],
    };
    let states: [[f64; 3]; 4] = [
        [2e-4, 1e-5, 1e-8],
        [0.3, 0.2, 0.1],
        [0.9, 0.09, 0.01],
        [1.0, 0.0, 0.0],
    ];
    let mut num = 0;
    let mut worst_ledger = 0.0_f64;
    let mut worst_event_norm = 0.0_f64;
    let mut worst_energy_norm = 0.0_f64;
    let mut worst_temp_norm = 0.0_f64;
    for frac in states {
        for raw_t in [
            100.0, 5500.0, 5500.001, 9284.0, 9284.001, 1e4, 2e4, 1e5, 9.99e5,
        ] {
            let gas = IgmGasState::from_temperature(frac, nh, nhe, raw_t).unwrap();
            let real_t = gas.eos(nh, nhe).unwrap().temperature_k;
            let prepared = direct.prepare(real_t).unwrap();
            let orig = provider
                .point(&gas, nh, nhe, 1e-16, 57.2355, photo)
                .unwrap();
            let explicit = provider
                .point_with_backend(&direct, &gas, nh, nhe, 1e-16, 57.2355, photo)
                .unwrap();
            let app = provider
                .point_with_backend(&lookup, &gas, nh, nhe, 1e-16, 57.2355, photo)
                .unwrap();
            assert_eq!(
                format!("{:?}", orig.rhs),
                format!("{:?}", explicit.rhs),
                "same direct evaluator physics"
            );
            assert_eq!(
                format!("{:?}", orig.rates),
                format!("{:?}", prepared.rates()),
                "exact-T reuse"
            );
            assert_eq!(
                format!("{:?}", orig.rates),
                format!("{:?}", igm_rates(real_t).unwrap())
            );
            let a = &orig.rhs;
            let b = &app.rhs;
            for r in [a, b] {
                let rs = ledger_residual(r).abs() / ledger_scale(r);
                worst_ledger = worst_ledger.max(rs);
                assert!(
                    rs <= 64.0 * f64::EPSILON,
                    "energy conservation {rs} at T={raw_t}"
                );
                let species = r.species_chemical_cm3_s;
                let p = event_scale(r);
                let nuc_h = (species[0] + species[1]).abs() / p;
                let nuc_he = (species[2] + species[3] + species[4]).abs() / p;
                let charge = (species[1] + species[3] + 2.0 * species[4] - species[5]).abs() / p;
                assert!(nuc_h.max(nuc_he).max(charge) < 64.0 * f64::EPSILON);
            }
            let es = event_scale(a);
            let dev = max_abs(
                b.species_chemical_cm3_s
                    .iter()
                    .zip(&a.species_chemical_cm3_s)
                    .map(|(b, a)| b - a),
            ) / es;
            worst_event_norm = worst_event_norm.max(dev);
            let power = ledger_scale(a);
            let de = max_abs(
                [
                    b.thermal_micro_erg_cm3_s - a.thermal_micro_erg_cm3_s,
                    b.binding_micro_erg_cm3_s - a.binding_micro_erg_cm3_s,
                    b.escape_erg_cm3_s - a.escape_erg_cm3_s,
                ]
                .into_iter(),
            ) / power;
            worst_energy_norm = worst_energy_norm.max(de);
            let particles = nh + nhe + gas.eos(nh, nhe).unwrap().electron_density_cm3;
            let td_scale = 2.0 * power
                / (3.0 * rei_microphysics::HHeModel::controlled_fixture().kb_erg_k * particles)
                + raw_t * es / particles;
            let dt = (b.temperature_dt_k_s - a.temperature_dt_k_s).abs() / td_scale;
            worst_temp_norm = worst_temp_norm.max(dt);
            assert!(
                dev <= RHS_NORM_TOL && de <= RHS_NORM_TOL && dt <= RHS_NORM_TOL,
                "C9 source RHS bound at T={raw_t}: {dev}, {de}, {dt}"
            );
            num += 1;
        }
    }
    println!("C9_RHS {{\"cases\":{num},\"worst_ledger_norm\":{worst_ledger:.16e},\"worst_species_dev_norm\":{worst_event_norm:.16e},\"worst_energy_dev_norm\":{worst_energy_norm:.16e},\"worst_T_rhs_dev_norm\":{worst_temp_norm:.16e}}}");
}

fn flat_rates(t: f64, table: &IgmRateTable) -> ([f64; 15], [f64; 15]) {
    (
        igm_flat(igm_rates(t).unwrap()),
        igm_flat(table.rates(t).unwrap()),
    )
}
#[test]
fn c9_independent_log_derivative_scan_no_derivative_admission() {
    let table = IgmRateTable::build_default().unwrap();
    let mut max_val = 0.0_f64;
    let mut max_slope = 0.0_f64;
    let mut worst_t = 0.0;
    let mut worst_channel = 0;
    let dx = 1e-6_f64;
    let mut counted = 0usize;
    // Interior temperatures in 1 K..1e6 K and exact original branch neighbors.
    for i in 0..2048 {
        let x = 1e6_f64.ln() * ((i as f64 + 0.1235) / 2048.0);
        let t = x.exp();
        let tm = (x - dx).exp();
        let tp = (x + dx).exp();
        let (d0, t0) = flat_rates(t, &table);
        let (dm, tmv) = flat_rates(tm, &table);
        let (dp, tpv) = flat_rates(tp, &table);
        for c in 0..15 {
            let a = d0[c];
            let b = t0[c];
            if a > 0.0 && a.is_normal() && b > 0.0 {
                let e = ((b - a) / a).abs();
                max_val = max_val.max(e);
            }
            // This is diagnostic only: structural zeros and source kinks do
            // not have a single differentiable log rate.
            if [a, dm[c], dp[c], b, tmv[c], tpv[c]]
                .iter()
                .all(|v| *v > 0.0 && v.is_normal())
            {
                let src = (dp[c].ln() - dm[c].ln()) / (2.0 * dx);
                let tab = (tpv[c].ln() - tmv[c].ln()) / (2.0 * dx);
                let diff = (src - tab).abs();
                if diff > max_slope {
                    max_slope = diff;
                    worst_t = t;
                    worst_channel = c;
                }
                counted += 1;
            }
        }
    }
    assert!(max_val < TARGET_MAX_COEFF_REL);
    println!("C9_LOG_DERIVATIVE {{\"samples\":{counted},\"max_rate_value_rel\":{max_val:.16e},\"max_log_slope_abs_diff\":{max_slope:.16e},\"worst_temperature_K\":{worst_t:.16e},\"worst_channel\":{worst_channel},\"eps_logT\":{dx}}}");
}

fn temperatures(n: usize, random: bool) -> Vec<f64> {
    let mut seed = 0x172942a3d8c56f01_u64;
    let width = 1e6_f64.ln();
    (0..n)
        .map(|i| {
            let x = if random {
                seed = seed
                    .wrapping_mul(6364136223846793005)
                    .wrapping_add(1442695040888963407);
                (seed >> 11) as f64 / ((1_u64 << 53) as f64)
            } else {
                (i as f64 + 0.371) / n as f64
            };
            (width * x).exp()
        })
        .collect()
}
fn direct_batch_parallel(ts: &[f64], workers: usize) -> [Vec<f64>; 15] {
    assert!((1..=4).contains(&workers));
    if ts.is_empty() {
        return std::array::from_fn(|_| Vec::new());
    }
    let chunk = ts.len().div_ceil(workers);
    let blocks = std::thread::scope(|scope| {
        let handles: Vec<_> = ts
            .chunks(chunk)
            .map(|piece| {
                scope.spawn(move || -> [Vec<f64>; 15] {
                    let mut block: [Vec<f64>; 15] =
                        std::array::from_fn(|_| Vec::with_capacity(piece.len()));
                    for &t in piece {
                        let rate = igm_flat(igm_rates(black_box(t)).unwrap());
                        for (v, x) in block.iter_mut().zip(rate) {
                            v.push(x);
                        }
                    }
                    block
                })
            })
            .collect();
        handles
            .into_iter()
            .map(|h| h.join().expect("worker panic"))
            .collect::<Vec<_>>()
    });
    let mut result: [Vec<f64>; 15] = std::array::from_fn(|_| Vec::with_capacity(ts.len()));
    for block in blocks {
        for (col, data) in result.iter_mut().zip(block) {
            col.extend(data);
        }
    }
    result
}
fn column_sum(cols: &[Vec<f64>; 15], scale: &[f64; 15]) -> f64 {
    let mut result = 0.0_f64;
    for i in 0..cols[0].len() {
        for j in 0..15 {
            result += cols[j][i] / scale[j];
        }
    }
    black_box(result)
}
fn median(mut x: Vec<f64>) -> f64 {
    x.sort_by(|a, b| a.total_cmp(b));
    x[x.len() / 2]
}
#[test]
fn c9_equal_workers_direct_vs_table_benchmark() {
    let now = Instant::now();
    let table = IgmRateTable::build_default().unwrap();
    let build_s = now.elapsed().as_secs_f64();
    let s = igm_flat(igm_rates(1e4).unwrap());
    for random in [false, true] {
        for &n in &[32768usize, 262144usize] {
            let ts = temperatures(n, random);
            let control = direct_batch_parallel(&ts, 4);
            let tcheck = table.batch_parallel(&ts, 4).unwrap();
            let gold = column_sum(&control, &s);
            let got = column_sum(&tcheck, &s);
            assert!(((got - gold) / gold).abs() < TARGET_MAX_COEFF_REL);
            let methods = ["direct_parallel4", "table_parallel4"];
            let mut samples: [Vec<f64>; 2] = std::array::from_fn(|_| Vec::new());
            for round in 0..7 {
                for idx in 0..2 {
                    let j = (idx + round) % 2;
                    let start = Instant::now();
                    let a = if j == 0 {
                        direct_batch_parallel(&ts, 4)
                    } else {
                        table.batch_parallel(&ts, 4).unwrap()
                    };
                    black_box(column_sum(&a, &s));
                    samples[j].push(start.elapsed().as_secs_f64());
                }
            }
            let direct_med = median(samples[0].clone());
            let table_med = median(samples[1].clone());
            let speed = direct_med / table_med;
            let gain = (direct_med - table_med) / ts.len() as f64;
            let break_even = if gain > 0.0 {
                Some(build_s / gain)
            } else {
                None
            };
            println!("C9_FAIR_BENCH {{\"distribution\":\"{}\",\"N\":{},\"workers\":4,\"direct4_median_s\":{direct_med:.12},\"table4_median_s\":{table_med:.12},\"ratio\":{speed:.9},\"build_s\":{build_s:.9},\"break_even\":{:?},\"checksum_relative_diff\":{:.9e},\"methods\":\"{} vs {}\"}}",
            if random{"random"}else{"ordered"},ts.len(),break_even,((got-gold)/gold).abs(),methods[0],methods[1]);
        }
    }
}

#[test]
fn c9_prepared_temperature_binding_rejects_stale_eos_without_clipping() {
    let nh = 1.0e-3;
    let nhe = 8.0e-5;
    let fractions = [0.12, 0.08, 0.01];
    let gas0 = IgmGasState::from_temperature(fractions, nh, nhe, 10_000.0).unwrap();
    let gas1 = IgmGasState::from_temperature(fractions, nh, nhe, 10_001.0).unwrap();
    let t0 = gas0.eos(nh, nhe).unwrap().temperature_k;
    let table = Arc::new(IgmRateTable::build_default().unwrap());
    let cached = IgmRateBackend::Table(table).prepare(t0).unwrap();
    let valid = rei_microphysics::igm_thermal::igm_point_rhs_with_prepared(
        &gas0,
        nh,
        nhe,
        1e-16,
        57.2355,
        IgmPhotoInput::default(),
        &cached,
    );
    assert!(valid.is_ok());
    let invalid = rei_microphysics::igm_thermal::igm_point_rhs_with_prepared(
        &gas1,
        nh,
        nhe,
        1e-16,
        57.2355,
        IgmPhotoInput::default(),
        &cached,
    )
    .unwrap_err();
    assert_eq!(invalid.code(), "IGM_PREPARED_TEMPERATURE_MISMATCH");
    // Same degrees of freedom but slightly changed EOS temperature cannot
    // silently inherit a stale bundle or rebind the gas temperature.
    println!("C9_TEMPERATURE_BIND {{\"prepared_K\":{t0:.15e},\"reuse_unchanged\":\"PASS\",\"changed_EOS_error\":\"{}\"}}", invalid.code());
}
