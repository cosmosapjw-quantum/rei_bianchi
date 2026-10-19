//! Same-input, same-step, complete-bit comparison with timers around advance only.
//! The original cohort inventory/order and source/thermal owners are retained.
#[path = "../tests/common/mod.rs"]
mod common;
use common::{bit_parity, fixture};
use rei_iso_couple_reference::{
    bianchi_i::GeometryBackground,
    positive_spectral::SpectralMode,
    reflection_pool::{PoolLimits, ReflectionPooledBridge},
    retarded_transport_threshold::PositiveThresholdBridge,
};
use std::hint::black_box;
use std::time::Instant;
fn main() {
    let selection = std::env::args().nth(1).unwrap_or_else(|| "all".into());
    println!(
        "case,nsteps,repeat,full_chemistry,fesc,shear_over_H,spectral_mode,birth_GL,opacity_m,old_s,reuse_s,speedup,computed_paths,reused_paths,peak_traces,peak_segments,evictions,bit_equal_steps,cohorts,T_K,photons_com3,absorbed_com3,HI_events_com3,HeI_events_com3,HeII_events_com3,DI_events_com3,max_photon_ledger,max_energy_ledger,RR_events,CX_abs,FF_J,CMB_abs_J"
    );
    // Long-time high-opacity control remains photo-only. Others include explicitly
    // labelled full CI/RR/CX/CE/freefree/CMB, with inherited 20 K test CMB bath.
    let cases = [
        ("photo_low_n16", 16, false, 0.06, 0.2, false, 8e10),
        ("photo_low_n32", 32, false, 0.06, 0.2, false, 8e10),
        ("full_flrw_n16", 16, true, 0., 0.2, false, 8e10),
        ("full_plus_n16", 16, true, 0.06, 0.2, false, 8e10),
        ("full_minus_n16", 16, true, -0.06, 0.2, false, 8e10),
        ("full_plus_n32", 32, true, 0.06, 0.2, false, 8e10),
        ("full_split_n8", 8, true, 0.06, 0.2, true, 8e10),
        ("full_fesc_minus", 16, true, 0.06, 0.1998, false, 8e10),
        ("full_fesc_plus", 16, true, 0.06, 0.2002, false, 8e10),
        ("photo_thick_n12", 12, false, 0.06, 0.2, false, 1.2e14),
    ];
    for (name, nsteps, full, shear, fesc, split, duration) in cases {
        if selection != "all" && selection != name {
            continue;
        }
        let spectrum = if split {
            SpectralMode::SplitPositiveGauss3
        } else {
            SpectralMode::OriginalCellMean
        };
        let gl = if split { 4 } else { 2 };
        let m = if split { 8 } else { 4 };
        for repeat in 0..3 {
            let (base, ctr, conf, gas) = fixture(shear, full, fesc, spectrum, gl, m);
            let old = PositiveThresholdBridge(base.clone(), ctr);
            let new = ReflectionPooledBridge(base.clone(), ctr, PoolLimits::default());
            let mut a = old.initial(gas, &conf, 0.).unwrap();
            let mut b = a.clone();
            let dt = duration / nsteps as f64;
            let (mut old_s, mut reuse_s) = (0., 0.);
            let (mut computed, mut reused, mut peak_t, mut peak_s, mut evictions) = (0, 0, 0, 0, 0);
            let mut photo = [0.; 4];
            let (mut rr, mut cx, mut ff, mut cmb) = (0., 0., 0., 0.);
            let (mut max_n, mut max_e) = (0f64, 0f64);
            for step in 0..nsteps {
                // Alternate order between repeats; no validation/csv formatting
                // or state serialization inside the timed sections.
                let (r, s, d) = if repeat % 2 == 0 {
                    let start = Instant::now();
                    let r = black_box(old.advance(&a, &conf, dt).unwrap());
                    old_s += start.elapsed().as_secs_f64();
                    let start = Instant::now();
                    let (s, d) = black_box(new.advance_with_diagnostics(&b, &conf, dt).unwrap());
                    reuse_s += start.elapsed().as_secs_f64();
                    (r, s, d)
                } else {
                    let start = Instant::now();
                    let (s, d) = black_box(new.advance_with_diagnostics(&b, &conf, dt).unwrap());
                    reuse_s += start.elapsed().as_secs_f64();
                    let start = Instant::now();
                    let r = black_box(old.advance(&a, &conf, dt).unwrap());
                    old_s += start.elapsed().as_secs_f64();
                    (r, s, d)
                };
                bit_parity(&r, &s);
                let v = base
                    .geometry
                    .snapshot(a.time_s + 0.5 * dt)
                    .unwrap()
                    .volume_factor()
                    .unwrap();
                for (p, e) in photo.iter_mut().zip(s.chemistry_budget.photo_events_m3) {
                    *p += e * v;
                }
                rr += s.chemistry_budget.rr_events_m3.iter().sum::<f64>() * v;
                cx += s.chemistry_budget.cx_signed_m3.abs() * v;
                ff += s.chemistry_budget.freefree_integrated_j_m3 * v;
                cmb += s.chemistry_budget.cmb_change_j_m3.abs() * v;
                computed += d.computed_paths;
                reused += d.reused_paths;
                evictions += d.trace_cache_evictions;
                peak_t = peak_t.max(d.peak_cached_traces);
                peak_s = peak_s.max(d.peak_cached_segments);
                max_e = max_e.max(s.global_energy_relative_error);
                let survivors = s
                    .state
                    .cohorts
                    .iter()
                    .map(|co| co.n_comoving_m3)
                    .sum::<f64>();
                let emitted = s.state.source_injected_count_com3;
                max_n = max_n.max(
                    (survivors + s.state.photon_absorbed_count_com3 - emitted).abs() / emitted,
                );
                assert_eq!(
                    d.computed_paths, d.reused_paths,
                    "reflection coverage {name}, step {step}"
                );
                a = r.state;
                b = s.state;
            }
            if full {
                assert!(rr > 0. && cx > 0. && ff > 0. && cmb > 0.);
            }
            assert!(peak_t <= 256 && peak_s <= 8192);
            println!(
                "{name},{nsteps},{repeat},{full},{fesc:.17e},{shear:.17e},{split},{gl},{m},{old_s:.12e},{reuse_s:.12e},{:.12e},{computed},{reused},{peak_t},{peak_s},{evictions},{nsteps},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{max_n:.17e},{max_e:.17e},{rr:.17e},{cx:.17e},{ff:.17e},{cmb:.17e}",
                old_s / reuse_s,
                b.cohorts.len(),
                b.full.gas.eos().unwrap().temperature_k,
                b.cohorts.iter().map(|co| co.n_comoving_m3).sum::<f64>(),
                b.photon_absorbed_count_com3,
                photo[0],
                photo[1],
                photo[2],
                photo[3]
            );
        }
    }
}
