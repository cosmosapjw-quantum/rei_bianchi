//! Source-native MD14/Verner/Grackle/Savin HHeD one-step crossover pilot.
//! Prescribed off-shell H(t)=1e-12, manufactured D and gas; no physical EoR.
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
    source_age::SourceAgeBridge,
};
fn run(optin: bool) {
    let h = 1e-12;
    let source = AxbiSource::new(1900.0 / (21_f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
    let geom = ConstantAxisymmetricBackground::new(
        0.,
        AxisymmetricPoint::new(1. / 21., 0., h, 0.).unwrap(),
        [0., 1.5e14],
    )
    .unwrap();
    let source_owner = SourceAgeBridge::new(source, geom).unwrap();
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let conf = NetworkConfig::source_bound(
        DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        SOURCE_ID,
    );
    let mut n = [0.; 13];
    n[S::H1Neutral as usize] = 1000.;
    n[S::H1Ionized as usize] = 900.;
    n[S::He4Neutral as usize] = 300.;
    n[S::He4SinglyIonized as usize] = 100.;
    n[S::He4DoublyIonized as usize] = 60.;
    n[S::DNeutral as usize] = 25.;
    n[S::DIonized as usize] = 5.;
    let nu = IsotopeNumberState::new(n).unwrap();
    let thermal = 1.5 * KB_J_K * nu.thermal_particle_density_all_thermal_m3().unwrap() * 1e4;
    let full = FullState {
        gas: MixtureState {
            nuclei: nu,
            thermal_j_m3: thermal,
        },
        photon_bins: vec![],
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
        elapsed_s: 0.,
    };
    let mut controls = RetardedControls::new(2, 2, SpectralMode::SplitPositiveGauss3).unwrap();
    if optin {
        controls = controls.with_threshold_events();
    }
    let b = PositiveRetardedBridge(source_owner, controls);
    let initial = b.initial(full, &conf, 0.).unwrap();
    let (step, diag) = b.advance_with_diagnostics(&initial, &conf, 5e8).unwrap();
    println!(
        "{optin},{},{:.16e},{:.16e},{:.16e},{:.16e},{:.16e},{:.16e}",
        diag.provider_threshold_cuts,
        step.state
            .cohorts
            .iter()
            .map(|co| co.n_comoving_m3)
            .sum::<f64>(),
        diag.photon_events_com3[0],
        diag.photon_events_com3[1],
        diag.photon_events_com3[2],
        diag.photon_events_com3[3],
        step.global_energy_relative_error
    );
}
fn main() {
    println!(
        "event_mode,threshold_cuts,survivor_com3,HI_events_com3,HeI_events_com3,HeII_events_com3,DI_events_com3,global_energy_rel_residual"
    );
    run(false);
    run(true);
}
