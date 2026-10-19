//! Physically source-model-conditional finite H/He/D+Bianchi-I history;
//! explicitly fails the per-species spectral compression science gate.
use rei_iso_couple_reference::{
    HHeModel,
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
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
    let nu = IsotopeNumberState::new(n).unwrap();
    let particles = nu.thermal_particle_density_all_thermal_m3().unwrap();
    FullState {
        gas: MixtureState {
            nuclei: nu,
            thermal_j_m3: 1.5 * KB_J_K * particles * 10000.,
        },
        photon_bins: vec![],
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
        elapsed_s: 0.,
    }
}
fn main() {
    let h = 1.2e-16;
    let total_s = 8.0e10;
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let config = NetworkConfig::source_bound(
        DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        SOURCE_ID,
    );
    println!(
        "case,nsteps,T_final_K,HII_m3,HeII_m3,HeIII_m3,DII_m3,photons_com_m3,emitted_com_m3,absorbed_com_m3,cohorts,source_tail_omitted,source_normalization_residual,max_grey_total,max_grey_HI,max_grey_HeI,max_grey_HeII,max_grey_DI,max_step_energy_residual,zfinal,geom_work_com_j_m3"
    );
    for (case, shear, fe, groups) in [("flrw_233", 0., 0.2, [2, 3, 3])] {
        for nsteps in [32, 64, 128, 256] {
            let src = AxbiSource::new(1900.0 / (21.0f64.powi(3) * 1e6), fe, 16, 8).unwrap();
            let norm = src.normalization_relative_residual;
            let tail = src.omitted_blackbody_tail_photon_fraction;
            let point = AxisymmetricPoint::new(1.0 / 21.0, 0.0, h, shear).unwrap();
            let bg = ConstantAxisymmetricBackground::new(0.0, point, [0., 1.5e14]).unwrap();
            let b = SourceAgeBridge::with_groups(src, bg, groups).unwrap();
            let mut state = b.initial(initial(), &config, 0.).unwrap();
            let mut max_e = 0.0f64;
            for _ in 0..nsteps {
                let result = b
                    .advance(&state, &config, total_s / (nsteps as f64))
                    .unwrap();
                max_e = max_e.max(result.global_energy_relative_error);
                state = result.state;
            }
            let g = b.geometry.snapshot(total_s).unwrap();
            let z = 1.0 / g.volume_factor().unwrap().cbrt() - 1.0;
            let pho = state.cohorts.iter().map(|c| c.n_comoving_m3).sum::<f64>();
            let nuc = state.full.gas.nuclei;
            println!(
                "{case},{nsteps},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e},{:.15e}",
                state.full.gas.eos().unwrap().temperature_k,
                nuc.density_m3(S::H1Ionized),
                nuc.density_m3(S::He4SinglyIonized),
                nuc.density_m3(S::He4DoublyIonized),
                nuc.density_m3(S::DIonized),
                pho,
                state.source_injected_count_com3,
                state.photon_absorbed_count_com3,
                state.cohorts.len(),
                tail,
                norm,
                state.max_grey_number_relative_error,
                state.max_grey_species_relative_error[0],
                state.max_grey_species_relative_error[1],
                state.max_grey_species_relative_error[2],
                state.max_grey_species_relative_error[3],
                max_e,
                z,
                state.geometry_work_j_com3
            );
        }
    }
}
