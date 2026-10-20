//! One bounded native row per process; input/physics labels explicit.
#[path = "../tests/common/mod.rs"]
mod common;
use common::fixture;
use rei_iso_couple_reference::{
    bianchi_i::GeometryBackground,
    deuterium_thermal_coupling::CxOwnership,
    isotope_state::IsotopeSpecies as S,
    midpoint_coupled::{Centering, MidpointBridge},
    positive_spectral::SpectralMode,
    reflection_pool::PoolLimits,
};
use std::time::Instant;
fn main() {
    let a: Vec<String> = std::env::args().collect();
    assert_eq!(a.len(), 4, "mode nsteps scenario");
    let mode = match a[1].as_str() {
        "legacy" => Centering::Legacy,
        "opacity" => Centering::OpacityOnly,
        "gas" => Centering::GasOnly,
        "joint" => Centering::Joint,
        "joint_cx" => Centering::JointCxSplit,
        _ => panic!("mode"),
    };
    let n: usize = a[2].parse().unwrap();
    assert!((1..=1024).contains(&n));
    let (shear, full, split) = match a[3].as_str() {
        "plus" => (0.06, true, false),
        "zero" => (0., true, false),
        "minus" => (-0.06, true, false),
        "photo" => (0.06, false, false),
        "split" => (0.06, true, true),
        _ => panic!("scenario"),
    };
    let spectrum = if split {
        SpectralMode::SplitPositiveGauss3
    } else {
        SpectralMode::OriginalCellMean
    };
    let (base, ctl, mut cfg, gas) = fixture(shear, full, 0.2, spectrum, 2, 4);
    cfg.owner = if mode == Centering::JointCxSplit {
        CxOwnership::ThermalSubstep
    } else {
        CxOwnership::AtomicRhs
    };
    // Fixed inner tolerance across ALL modes to isolate outer temporal error.
    cfg.cx_controls.rtol = 1e-12;
    cfg.cx_controls.atol_normalized = 1e-15;
    let bridge = MidpointBridge(base, ctl, PoolLimits::default(), mode);
    let mut state = bridge.initial(gas, &cfg, 0.).unwrap();
    let span = 8e10;
    let h = span / n as f64;
    let mut species = [0.; 4];
    let mut photoe = 0.;
    let mut rr = 0.;
    let mut cx = 0.;
    let mut ff = 0.;
    let mut cmb = 0.;
    let mut maxn = 0f64;
    let mut maxe = 0f64;
    let timer = Instant::now();
    for _ in 0..n {
        let vm = bridge
            .0
            .geometry
            .snapshot(state.time_s + h / 2.)
            .unwrap()
            .volume_factor()
            .unwrap();
        let out = bridge.advance(&state, &cfg, h).unwrap();
        let b = &out.chemistry_budget;
        for (x, db) in species.iter_mut().zip(b.photo_events_m3) {
            *x += db * vm;
        }
        photoe += b.photo_energy_j_m3 * vm;
        rr += b.rr_events_m3.iter().sum::<f64>() * vm;
        cx += b.cx_signed_m3.abs() * vm;
        ff += b.freefree_integrated_j_m3 * vm;
        cmb += b.cmb_change_j_m3.abs() * vm;
        maxe = maxe.max(out.global_energy_relative_error);
        state = out.state;
        let photons = state.cohorts.iter().map(|q| q.n_comoving_m3).sum::<f64>();
        maxn = maxn.max(
            (photons + state.photon_absorbed_count_com3 - state.source_injected_count_com3).abs()
                / state.source_injected_count_com3,
        );
    }
    let elapsed = timer.elapsed().as_secs_f64();
    let eos = state.full.gas.eos().unwrap();
    assert!(
        state
            .cohorts
            .iter()
            .all(|q| q.n_comoving_m3.is_finite() && q.n_comoving_m3 >= 0.)
    );
    println!(
        "mode,nsteps,scenario,full_chemistry,shear_over_H,split_spectrum,span_s,wall_s,temp_K,photons_com3,absorbed_com3,HI_events,HeI_events,HeII_events,DI_events,photo_energy_j_com3,RR_events,CX_abs,FF_J,CMB_abs_J,photon_ledger,energy_ledger,cohorts,n_HII,n_HeII,n_HeIII,n_DII,thermal_J_m3,escaped_J_m3,cmb_J_m3"
    );
    println!(
        "{},{},{},{},{:.17e},{},{:.17e},{:.12e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
        a[1],
        n,
        a[3],
        full,
        shear,
        split,
        span,
        elapsed,
        eos.temperature_k,
        state.cohorts.iter().map(|q| q.n_comoving_m3).sum::<f64>(),
        state.photon_absorbed_count_com3,
        species[0],
        species[1],
        species[2],
        species[3],
        photoe,
        rr,
        cx,
        ff,
        cmb,
        maxn,
        maxe,
        state.cohorts.len(),
        state.full.gas.nuclei.density_m3(S::H1Ionized),
        state.full.gas.nuclei.density_m3(S::He4SinglyIonized),
        state.full.gas.nuclei.density_m3(S::He4DoublyIonized),
        state.full.gas.nuclei.density_m3(S::DIonized),
        state.full.gas.thermal_j_m3,
        state.full.escaped_j_m3,
        state.full.cmb_reservoir_j_m3
    );
}
