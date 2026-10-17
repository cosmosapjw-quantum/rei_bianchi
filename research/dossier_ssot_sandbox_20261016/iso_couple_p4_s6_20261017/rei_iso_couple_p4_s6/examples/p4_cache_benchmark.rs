//! Matched executable source-native before/after benchmark (no threshold roots)
//! Records real elapsed time and mathematical state parity, never full-EoR speed.
use rei_iso_couple_reference::{
    HHeModel,
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    positive_spectral::SpectralMode,
    retarded_transport::{PositiveRetardedBridge, RetardedControls},
    retarded_transport_threshold::PositiveThresholdBridge,
    source_age::SourceAgeBridge,
};
use std::hint::black_box;
use std::time::Instant;
fn initial() -> FullState {
    let mut n = [0.0; 13];
    n[S::H1Neutral as usize] = 1000.;
    n[S::H1Ionized as usize] = 900.;
    n[S::He4Neutral as usize] = 300.;
    n[S::He4SinglyIonized as usize] = 100.;
    n[S::He4DoublyIonized as usize] = 60.;
    n[S::DNeutral as usize] = 25.;
    n[S::DIonized as usize] = 5.;
    let ni = IsotopeNumberState::new(n).unwrap();
    let th = 1.5 * KB_J_K * ni.thermal_particle_density_all_thermal_m3().unwrap() * 1e4;
    FullState {
        gas: MixtureState {
            nuclei: ni,
            thermal_j_m3: th,
        },
        photon_bins: vec![],
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
        elapsed_s: 0.,
    }
}
fn trial(nsteps: usize, use_cache: bool) -> (f64, f64, f64, f64, usize, usize) {
    let h = 1.2e-16;
    let src = AxbiSource::new(1900.0 / (21f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
    let geometry = ConstantAxisymmetricBackground::new(
        0.,
        AxisymmetricPoint::new(1. / 21., 0., h, 0.06 * h).unwrap(),
        [0., 1.5e14],
    )
    .unwrap();
    let sb = SourceAgeBridge::new(src, geometry).unwrap();
    let ctl = RetardedControls::new(2, 4, SpectralMode::OriginalCellMean).unwrap();
    let p3 = PositiveRetardedBridge(sb.clone(), ctl);
    let s4 = PositiveThresholdBridge(sb, ctl);
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let cfg = NetworkConfig::source_bound(
        DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        SOURCE_ID,
    );
    let mut state = s4.initial(initial(), &cfg, 0.).unwrap();
    let now = Instant::now();
    let mut crossings = 0;
    let mut plans = 0;
    for _ in 0..nsteps {
        if use_cache {
            let (x, diag) = s4
                .advance_with_diagnostics(&state, &cfg, 8e10 / (nsteps as f64))
                .unwrap();
            crossings += diag.threshold_crossings;
            plans += diag.unique_geometry_plans;
            state = black_box(x.state);
        } else {
            let x = p3.advance(&state, &cfg, 8e10 / (nsteps as f64)).unwrap();
            state = black_box(x.state);
        }
    }
    let elapsed = now.elapsed().as_secs_f64();
    let survivors = state.cohorts.iter().map(|x| x.n_comoving_m3).sum::<f64>();
    (
        elapsed,
        survivors,
        state.photon_absorbed_count_com3,
        state.full.gas.eos().unwrap().temperature_k,
        crossings,
        plans,
    )
}
fn main() {
    println!(
        "nsteps,repeat,mode,time_s,survivors_com3,absorbed_com3,T_K,threshold_crossings,unique_geometry_plans"
    );
    for n in [4, 8, 16] {
        for rep in 0..3 {
            let methods = if rep % 2 == 0 {
                [false, true]
            } else {
                [true, false]
            };
            for mode in methods {
                let (t, s, a, temp, roots, plans) = trial(n, mode);
                println!(
                    "{n},{rep},{},{t:.9e},{s:.15e},{a:.15e},{temp:.15e},{roots},{plans}",
                    if mode { "cached_s4" } else { "original_s3" }
                );
            }
        }
    }
}
