use rei_iso_couple_reference::{
    HHeModel,
    axbi_sources::AxbiSource,
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::NetworkConfig,
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    source_age::SourceAgeBridge,
};
fn main() {
    let mut n = [0.0; 13];
    n[S::H1Neutral as usize] = 1000.0;
    n[S::H1Ionized as usize] = 900.0;
    n[S::He4Neutral as usize] = 300.0;
    n[S::He4SinglyIonized as usize] = 100.0;
    n[S::He4DoublyIonized as usize] = 60.0;
    n[S::DNeutral as usize] = 25.0;
    n[S::DIonized as usize] = 5.0;
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let nth = nuclei.thermal_particle_density_all_thermal_m3().unwrap();
    let gas = MixtureState {
        nuclei,
        thermal_j_m3: 1.5 * KB_J_K * nth * 10000.0,
    };
    let model = HHeModel::controlled_fixture();
    let src = AxbiSource::new(1900.0 / (21f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
    let geo = ConstantAxisymmetricBackground::new(
        0.0,
        AxisymmetricPoint::new(1.0 / 21.0, 0.0, 1.2e-16, 7.2e-18).unwrap(),
        [0.0, 1.5e14],
    )
    .unwrap();
    let conf = NetworkConfig::source_bound(
        DAtomicProvider::new(
            model.threshold_ev[0],
            model.threshold_ev[0] + 0.0037,
            "MANUFACTURED_OFFSET",
        )
        .unwrap(),
        rei_iso_couple_reference::axbi_sources::SOURCE_ID,
    );
    println!(
        "group_H,group_HeI,group_HeII,groups_total,err_total,err_HI,err_HeI,err_HeII,err_D,max_err"
    );
    for a in 1..=6 {
        for b in 1..=6 {
            for c in 1..=6 {
                if a + b + c > 8 {
                    continue;
                }
                let bridge = SourceAgeBridge::with_groups(src.clone(), geo, [a, b, c]).unwrap();
                let g = bridge.geometry.snapshot(5e9).unwrap();
                let cohort = bridge.source_births(5e9, 1e10).unwrap();
                let err = bridge
                    .grey_absorption_error(&cohort, &g, &gas, &conf, 1e10)
                    .unwrap();
                println!(
                    "{a},{b},{c},{},{:.12e},{:.12e},{:.12e},{:.12e},{:.12e},{:.12e}",
                    a + b + c,
                    err.total_relative_error,
                    err.species_relative_error[0],
                    err.species_relative_error[1],
                    err.species_relative_error[2],
                    err.species_relative_error[3],
                    err.species_relative_error
                        .iter()
                        .copied()
                        .fold(0., f64::max)
                );
            }
        }
    }
}
