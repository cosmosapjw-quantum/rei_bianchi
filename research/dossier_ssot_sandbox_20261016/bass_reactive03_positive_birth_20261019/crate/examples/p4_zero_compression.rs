//! Photon-state EXACT-ZERO retirement only; no unquantified numerical cutoff.
use rei_iso_couple_reference::{
    HHeModel,
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    positive_spectral::SpectralMode,
    retarded_transport::RetardedControls,
    retarded_transport_threshold::PositiveThresholdBridge,
    source_age::SourceAgeBridge,
};
use std::time::Instant;
fn initial() -> FullState {
    let mut n = [0.; 13];
    n[S::H1Neutral as usize] = 1000.;
    n[S::H1Ionized as usize] = 900.;
    n[S::He4Neutral as usize] = 300.;
    n[S::He4SinglyIonized as usize] = 100.;
    n[S::He4DoublyIonized as usize] = 60.;
    n[S::DNeutral as usize] = 25.;
    n[S::DIonized as usize] = 5.;
    let nuclei = IsotopeNumberState::new(n).unwrap();
    FullState {
        gas: MixtureState {
            nuclei,
            thermal_j_m3: 1.5
                * KB_J_K
                * nuclei.thermal_particle_density_all_thermal_m3().unwrap()
                * 1e4,
        },
        photon_bins: vec![],
        elapsed_s: 0.,
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
    }
}
fn main() {
    println!(
        "mode,step,elapsed_s,cohorts,removed_exact_zeros,photon_absorbed,photons_surviving,temp_K,photon_ledger_rel"
    );
    for compressed in [false, true] {
        let h = 1.2e-16;
        let src = AxbiSource::new(1900. / (21f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
        let bg = ConstantAxisymmetricBackground::new(
            0.,
            AxisymmetricPoint::new(1. / 21., 0., h, 0.).unwrap(),
            [0., 1.5e14],
        )
        .unwrap();
        let bridge = PositiveThresholdBridge(
            SourceAgeBridge::new(src, bg).unwrap(),
            RetardedControls::new(2, 4, SpectralMode::OriginalCellMean).unwrap(),
        );
        let chi = HHeModel::controlled_fixture().threshold_ev[0];
        let mut cfg = NetworkConfig::source_bound(
            DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
            SOURCE_ID,
        );
        cfg.use_collisions = false;
        cfg.use_cx = false;
        cfg.use_cmb = false;
        let mut state = bridge.initial(initial(), &cfg, 0.).unwrap();
        for step in 1..=12 {
            let start = Instant::now();
            let (out, diag) = if compressed {
                bridge
                    .advance_compact_exact_zeros(&state, &cfg, 1e13)
                    .unwrap()
            } else {
                bridge.advance_with_diagnostics(&state, &cfg, 1e13).unwrap()
            };
            state = out.state;
            let photons = state.cohorts.iter().map(|x| x.n_comoving_m3).sum::<f64>();
            let balance = (photons + state.photon_absorbed_count_com3
                - state.source_injected_count_com3)
                .abs()
                / state.source_injected_count_com3;
            println!(
                "{}, {step},{:.9e},{},{},{:.15e},{:.15e},{:.15e},{:.15e}",
                if compressed {
                    "exact_zero_only"
                } else {
                    "retain_all"
                },
                start.elapsed().as_secs_f64(),
                state.cohorts.len(),
                diag.retired_exact_zero_cohorts,
                state.photon_absorbed_count_com3,
                photons,
                state.full.gas.eos().unwrap().temperature_k,
                balance
            );
        }
    }
}
