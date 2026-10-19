//! Conditional source-aware *manufactured binding threshold* trajectory probe.
use rei_iso_couple_reference::deuterium_atomic::DAtomicProvider;
use rei_iso_couple_reference::deuterium_thermal_coupling::CxOwnership;
use rei_iso_couple_reference::isotope_state::{IsotopeNumberState, IsotopeSpecies as S};
use rei_iso_couple_reference::mixture_coupling::{MixtureCxComponent, StepControls};
use rei_iso_couple_reference::mixture_eos::{KB_J_K, MixtureState};
const LABEL: &str = "MANUFACTURED_THRESHOLD_0_0037_EV_NOT_ADMITTED";
fn create(he: f64) -> MixtureState {
    let mut d = [0.; 13];
    d[S::H1Neutral as usize] = 1000.0;
    d[S::H1Ionized as usize] = 900.0;
    d[S::DNeutral as usize] = 25.0;
    d[S::DIonized as usize] = 5.0;
    d[S::He4Neutral as usize] = he;
    d[S::He4SinglyIonized as usize] = he / 5.0;
    d[S::He4DoublyIonized as usize] = he / 7.0;
    let nuclei = IsotopeNumberState::new(d).unwrap();
    let nth = nuclei.thermal_particle_density_all_thermal_m3().unwrap();
    MixtureState {
        nuclei,
        thermal_j_m3: 1.5 * KB_J_K * nth * 10000.0,
    }
}
fn main() {
    let p = DAtomicProvider::new(13.598_434_599_702, 13.602_134_599_702, LABEL).unwrap();
    let obj = MixtureCxComponent::new(p, CxOwnership::ThermalSubstep);
    println!(
        "helium_neutral_m3,duration_s,rtol,xi_m3,temperature_K,delta_temperature_K,delta_u_chem_J_m3,delta_u_th_J_m3,baryon_difference_m3,electron_difference_m3,accepted,rejected,rhs_calls,relative_extent_to_strict"
    );
    for he in [0.0, 100.0, 300.0, 600.0] {
        for duration in [1e9, 1e10, 3e10] {
            let s = create(he);
            let strict = obj
                .advance_cx_only(
                    s,
                    duration,
                    StepControls {
                        rtol: 1e-12,
                        atol_normalized: 1e-14,
                        max_attempts: 10000,
                        max_rate_calls: 3_000_000,
                    },
                )
                .unwrap();
            for rtol in [1e-5, 1e-7, 1e-9] {
                let o = obj
                    .advance_cx_only(
                        s,
                        duration,
                        StepControls {
                            rtol,
                            atol_normalized: rtol * 0.001,
                            max_attempts: 10000,
                            max_rate_calls: 3_000_000,
                        },
                    )
                    .unwrap();
                let after = o.final_state.eos().unwrap();
                let before = s.eos().unwrap();
                println!(
                    "{:.1},{:.5e},{:.2e},{:.15e},{:.12e},{:.15e},{:.15e},{:.15e},{:.6e},{:.6e},{},{},{},{:.6e}",
                    he,
                    duration,
                    rtol,
                    o.extent_m3,
                    after.temperature_k,
                    after.temperature_k - before.temperature_k,
                    o.delta_chemical_j_m3,
                    o.delta_thermal_j_m3,
                    o.delta_baryons_m3,
                    o.delta_electron_m3,
                    o.counts.accepted_steps,
                    o.counts.rejected_steps,
                    o.counts.rate_calls,
                    (o.extent_m3 - strict.extent_m3).abs() / strict.extent_m3.abs().max(1e-50)
                );
            }
        }
    }
}
