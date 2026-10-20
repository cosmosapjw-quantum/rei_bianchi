//! P4/S2 matched source-native H/He/D positive 384-cell cohort comparison.
//! Retains P3 midpoint-full-opacity source as explicit historical control.
//! Does not compare to full native PR150 source-on EoR or Einstein on-shell Bianchi.
use rei_iso_couple_reference::{
    HHeModel,
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    positive_age::PositiveAgeBridge,
    positive_birth_clock::PositiveBirthClockBridge,
    source_age::SourceAgeBridge,
};
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
    let nth = nuclei.thermal_particle_density_all_thermal_m3().unwrap();
    FullState {
        gas: MixtureState {
            nuclei,
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
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let conf = NetworkConfig::source_bound(
        DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        SOURCE_ID,
    );
    println!(
        "case,nsteps,representation,T_final_K,HI_ionized_m3,HeII_m3,HeIII_m3,DII_m3,survivors_com_m3,emitted_com_m3,absorbed_com_m3,max_energy_residual,HI_events_com3,HeI_events_com3,HeII_events_com3,D_events_com3,cohorts"
    );
    for (case, shear, fe) in [
        ("flrw", 0., 0.2),
        ("bi_plus", 0.06 * h, 0.2),
        ("bi_minus", -0.06 * h, 0.2),
        ("bi_plus_fesc025", 0.06 * h, 0.25),
    ] {
        for nsteps in [8usize, 16, 32, 64] {
            let src = AxbiSource::new(1900.0 / (21.0f64.powi(3) * 1e6), fe, 16, 8).unwrap();
            let bg = ConstantAxisymmetricBackground::new(
                0.,
                AxisymmetricPoint::new(1. / 21., 0., h, shear).unwrap(),
                [0., 1.5e14],
            )
            .unwrap();
            let original = SourceAgeBridge::new(src, bg).unwrap();
            for mode in ["p3_full_exposure", "p4_positive_birth_phi"] {
                let mut s = original.initial(initial(), &conf, 0.).unwrap();
                let mut maxerr = 0_f64;
                let mut cumulative = [0.; 4];
                for _ in 0..nsteps {
                    let dt = duration / nsteps as f64;
                    let v = original
                        .geometry
                        .snapshot(s.time_s + 0.5 * dt)
                        .unwrap()
                        .volume_factor()
                        .unwrap();
                    let step = if mode == "p3_full_exposure" {
                        PositiveAgeBridge(original.clone()).advance(&s, &conf, dt)
                    } else {
                        PositiveBirthClockBridge(original.clone()).advance(&s, &conf, dt)
                    }
                    .unwrap();
                    maxerr = maxerr.max(step.global_energy_relative_error);
                    for (j, x) in step.chemistry_budget.photo_events_m3.iter().enumerate() {
                        cumulative[j] += x * v;
                    }
                    s = step.state;
                }
                let nu = s.full.gas.nuclei;
                let survivors = s.cohorts.iter().map(|c| c.n_comoving_m3).sum::<f64>();
                println!(
                    "{case},{nsteps},{mode},{:.16e},{:.16e},{:.16e},{:.16e},{:.16e},{:.16e},{:.16e},{:.16e},{:.16e},{:.16e},{:.16e},{:.16e},{:.16e},{}",
                    s.full.gas.eos().unwrap().temperature_k,
                    nu.density_m3(S::H1Ionized),
                    nu.density_m3(S::He4SinglyIonized),
                    nu.density_m3(S::He4DoublyIonized),
                    nu.density_m3(S::DIonized),
                    survivors,
                    s.source_injected_count_com3,
                    s.photon_absorbed_count_com3,
                    maxerr,
                    cumulative[0],
                    cumulative[1],
                    cumulative[2],
                    cumulative[3],
                    s.cohorts.len()
                );
            }
        }
    }
}
