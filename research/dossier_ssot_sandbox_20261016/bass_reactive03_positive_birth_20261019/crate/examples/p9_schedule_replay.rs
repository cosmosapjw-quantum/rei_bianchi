//! Same accepted time grid for every inner-CX tolerance: no controller feedback.
#[path = "../tests/common/mod.rs"]
mod common;
use common::fixture;
use rei_iso_couple_reference::{
    adaptive_step::{events_comoving, photon_projection},
    isotope_state::IsotopeSpecies as S,
    midpoint_coupled::{Centering, MidpointBridge},
    positive_spectral::SpectralMode,
    reflection_pool::PoolLimits,
};
fn main() {
    let args: Vec<String> = std::env::args().collect();
    assert_eq!(args.len(), 2, "accepted-attempt trace CSV required");
    let text = std::fs::read_to_string(&args[1]).unwrap();
    let mut intervals = vec![];
    for row in text.lines().skip(1) {
        let fields: Vec<_> = row.split(',').collect();
        assert_eq!(fields.len(), 12);
        if fields[3] == "true" {
            intervals.push((
                fields[1].parse::<f64>().unwrap(),
                fields[2].parse::<f64>().unwrap(),
            ));
        }
    }
    assert!(!intervals.is_empty());
    println!(
        "cx_rtol,accepted_intervals,native_substeps,time_s,T_K,DII_m3,photons_com3,HI,HeI,HeII,DI,max_energy_ledger"
    );
    for cx in [1e-8, 1e-10, 1e-12, 1e-14] {
        let (base, ctl, mut conf, gas) =
            fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
        conf.cx_controls.rtol = cx;
        conf.cx_controls.atol_normalized = cx * 1e-3;
        // Explicit, common research work allowance, not an accuracy relaxation.
        conf.cx_controls.max_attempts = 20000;
        conf.cx_controls.max_rate_calls = 2500000;
        let b = MidpointBridge(base, ctl, PoolLimits::default(), Centering::JointCxSplit);
        let mut s = b.initial(gas, &conf, 0.).unwrap();
        let mut events = [0.; 4];
        let mut max_e = 0f64;
        for &(t0, h) in &intervals {
            assert_eq!(s.time_s.to_bits(), t0.to_bits(), "schedule clock changed");
            let end = t0 + h;
            let first = b.advance(&s, &conf, h / 2.).unwrap();
            let e1 = events_comoving(&b, &first, s.time_s).unwrap();
            let last = b
                .advance(&first.state, &conf, end - first.state.time_s)
                .unwrap();
            let e2 = events_comoving(&b, &last, first.state.time_s).unwrap();
            for j in 0..4 {
                events[j] += e1[j] + e2[j];
            }
            max_e = max_e
                .max(first.global_energy_relative_error)
                .max(last.global_energy_relative_error);
            s = last.state;
        }
        let p = photon_projection(&b, &s).unwrap();
        println!(
            "{cx:.17e},{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{max_e:.17e}",
            intervals.len(),
            2 * intervals.len(),
            s.time_s,
            s.full.gas.eos().unwrap().temperature_k,
            s.full.gas.nuclei.density_m3(S::DIonized),
            p.count,
            events[0],
            events[1],
            events[2],
            events[3]
        );
    }
}
