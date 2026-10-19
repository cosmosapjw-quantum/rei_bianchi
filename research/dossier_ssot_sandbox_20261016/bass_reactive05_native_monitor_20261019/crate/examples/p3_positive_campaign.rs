//! Matched direct-positive and 64-bin projected source-age + source-native HHeD gas.
//! This is an explicit conditional comparison, not an EoR production history.
use rei_iso_couple_reference::{
    HHeModel,
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    positive_age::PositiveAgeBridge,
    source_age::SourceAgeBridge,
};
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
    let nth = ni.thermal_particle_density_all_thermal_m3().unwrap();
    FullState {
        gas: MixtureState {
            nuclei: ni,
            thermal_j_m3: 1.5 * KB_J_K * nth * 10000.,
        },
        photon_bins: vec![],
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
        elapsed_s: 0.,
    }
}
fn main() {
    let h = 1.2e-16;
    let duration = 8.0e10;
    let c = HHeModel::controlled_fixture().threshold_ev[0];
    let conf = NetworkConfig::source_bound(
        DAtomicProvider::new(c, c + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        SOURCE_ID,
    );
    println!(
        "case,nsteps,representation,T_final_K,HII_m3,HeII_m3,HeIII_m3,DII_m3,photons_com_m3,emitted_com_m3,absorbed_com_m3,cohorts,max_step_energy_error,HI_photo_m3,HeI_photo_m3,HeII_photo_m3,D_photo_m3,source_normalization,source_tail"
    );
    for (case, shear, fe) in [
        ("flrw", 0., 0.2),
        ("bi_plus", 0.06 * h, 0.2),
        ("bi_minus", -0.06 * h, 0.2),
        ("bi_fesc025", 0.06 * h, 0.25),
    ] {
        for nsteps in [8usize, 16, 32, 64] {
            let src = AxbiSource::new(1900.0 / (21.0f64.powi(3) * 1e6), fe, 16, 8).unwrap();
            let norm = src.normalization_relative_residual;
            let tail = src.omitted_blackbody_tail_photon_fraction;
            let bg = ConstantAxisymmetricBackground::new(
                0.,
                AxisymmetricPoint::new(1. / 21., 0., h, shear).unwrap(),
                [0., 1.5e14],
            )
            .unwrap();
            let base = SourceAgeBridge::new(src, bg).unwrap();
            for representation in ["positive_384", "projected_64"] {
                let mut state = base.initial(initial(), &conf, 0.).unwrap();
                let mut max_e = 0.0f64;
                let mut cumulative = [0.; 4];
                for _ in 0..nsteps {
                    let result = if representation == "positive_384" {
                        PositiveAgeBridge(base.clone()).advance(
                            &state,
                            &conf,
                            duration / nsteps as f64,
                        )
                    } else {
                        base.advance(&state, &conf, duration / nsteps as f64)
                    }
                    .unwrap();
                    max_e = max_e.max(result.global_energy_relative_error);
                    let v = base
                        .geometry
                        .snapshot(state.time_s + 0.5 * duration / nsteps as f64)
                        .unwrap()
                        .volume_factor()
                        .unwrap();
                    for (j, x) in result.chemistry_budget.photo_events_m3.iter().enumerate() {
                        cumulative[j] += x * v;
                    }
                    state = result.state;
                }
                let nu = state.full.gas.nuclei;
                let n = state.cohorts.iter().map(|x| x.n_comoving_m3).sum::<f64>();
                println!(
                    "{case},{nsteps},{representation},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e}",
                    state.full.gas.eos().unwrap().temperature_k,
                    nu.density_m3(S::H1Ionized),
                    nu.density_m3(S::He4SinglyIonized),
                    nu.density_m3(S::He4DoublyIonized),
                    nu.density_m3(S::DIonized),
                    n,
                    state.source_injected_count_com3,
                    state.photon_absorbed_count_com3,
                    state.cohorts.len(),
                    max_e,
                    cumulative[0],
                    cumulative[1],
                    cumulative[2],
                    cumulative[3],
                    norm,
                    tail
                );
            }
        }
    }
}
