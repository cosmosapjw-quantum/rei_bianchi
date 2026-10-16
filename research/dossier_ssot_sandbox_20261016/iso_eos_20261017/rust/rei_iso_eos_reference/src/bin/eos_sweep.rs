//! Deterministic manufactured fixed-volume spectator capacity sweep.
use rei_iso_eos_reference::deuterium_charge_exchange::{DhEnergyDefect, Savin2002};
use rei_iso_eos_reference::mixture_eos::{CxOwner, KB_J_K, MixtureCxReference, MixtureState};
use rei_iso_eos_reference::{IsotopeNumberState, IsotopeSpecies};

fn main() {
    let mut values = [0.0; 13];
    values[IsotopeSpecies::H1Neutral as usize] = 1000.0;
    values[IsotopeSpecies::H1Ionized as usize] = 500.0;
    values[IsotopeSpecies::DNeutral as usize] = 50.0;
    values[IsotopeSpecies::DIonized as usize] = 50.0;
    let c = MixtureCxReference {
        defect: DhEnergyDefect {
            delta_chi_j: 0.0037 * 1.602176634e-19,
            source: "MANUFACTURED_FIXED_DEFECT",
        },
        owner: CxOwner::ThermalSubstep,
        rate_source: Savin2002::SOURCE,
    };
    println!(
        "helium_density_m3,thermal_particles_m3,delta_t_K,predicted_delta_t_K,relative_to_pure_H_D"
    );
    for he in (0..=12).map(|i| i as f64 * 50.0) {
        values[IsotopeSpecies::He4Neutral as usize] = 0.4 * he;
        values[IsotopeSpecies::He4SinglyIonized as usize] = 0.4 * he;
        values[IsotopeSpecies::He4DoublyIonized as usize] = 0.2 * he;
        let nuclei = IsotopeNumberState::new(values).unwrap();
        let nt = nuclei.thermal_particle_density_all_thermal_m3().unwrap();
        let start = MixtureState {
            nuclei,
            thermal_j_m3: 1.5 * KB_J_K * nt * 10_000.0,
        };
        let ev = c.apply_extent(start, 10.0).unwrap();
        let dt = ev.after.temperature_k - ev.before.temperature_k;
        let predicted = -c.defect.delta_chi_j * 10.0 / ev.before.heat_capacity_j_m3_k;
        println!("{he},{nt},{dt:.16e},{predicted:.16e},{:.16e}", 2150.0 / nt);
    }
}
