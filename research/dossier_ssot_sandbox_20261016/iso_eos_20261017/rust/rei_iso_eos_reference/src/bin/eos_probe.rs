use rei_iso_eos_reference::deuterium_charge_exchange::{DhEnergyDefect, Savin2002};
use rei_iso_eos_reference::mixture_eos::{CxOwner, KB_J_K, MixtureCxReference, MixtureState};
use rei_iso_eos_reference::{IsotopeNumberState, IsotopeSpecies};

fn main() {
    let mut values = [0.0; 13];
    values[IsotopeSpecies::H1Neutral as usize] = 1000.0;
    values[IsotopeSpecies::H1Ionized as usize] = 500.0;
    values[IsotopeSpecies::DNeutral as usize] = 50.0;
    values[IsotopeSpecies::DIonized as usize] = 50.0;
    let pure = IsotopeNumberState::new(values).unwrap();
    let bare = MixtureState {
        nuclei: pure,
        thermal_j_m3: 1.5 * KB_J_K * 2150.0 * 10_000.0,
    };
    values[IsotopeSpecies::He4Neutral as usize] = 200.0;
    values[IsotopeSpecies::He4SinglyIonized as usize] = 200.0;
    values[IsotopeSpecies::He4DoublyIonized as usize] = 100.0;
    let mixed = IsotopeNumberState::new(values).unwrap();
    let he = MixtureState {
        nuclei: mixed,
        thermal_j_m3: 1.5 * KB_J_K * 3050.0 * 10_000.0,
    };
    let c = MixtureCxReference {
        defect: DhEnergyDefect {
            delta_chi_j: 0.0037 * 1.602176634e-19,
            source: "MANUFACTURED_NOT_ATOMIC_THRESHOLD",
        },
        owner: CxOwner::ThermalSubstep,
        rate_source: Savin2002::SOURCE,
    };
    let extent = 10.0;
    let a = c.apply_extent(bare, extent).unwrap();
    let b = c.apply_extent(he, extent).unwrap();
    let rhs_p = c.savin_rhs(bare).unwrap();
    let rhs_h = c.savin_rhs(he).unwrap();
    println!(
        "{{\"scope\":\"MANUFACTURED_FIXED_VOLUME_NO_IONIZATION_RATE_NETWORK\",\"T_initial_k\":10000.0,\"pure_particles_m3\":{},\"helium_particles_m3\":{},\"pure_delta_T_k\":{},\"helium_delta_T_k\":{},\"deltaT_ratio_helium_over_pure\":{},\"savin_extent_rate_pure_m3_s\":{},\"savin_extent_rate_helium_m3_s\":{},\"electron_delta_he_m3\":{},\"baryon_delta_he_m3\":{}}}",
        a.before.thermal_particles_m3,
        b.before.thermal_particles_m3,
        a.after.temperature_k - a.before.temperature_k,
        b.after.temperature_k - b.before.temperature_k,
        (b.after.temperature_k - b.before.temperature_k)
            / (a.after.temperature_k - a.before.temperature_k),
        rhs_p.extent_rate_m3_s,
        rhs_h.extent_rate_m3_s,
        b.free_electron_delta_m3,
        b.baryon_delta_m3
    );
}
