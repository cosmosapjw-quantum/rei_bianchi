#![allow(dead_code)]
use rei_iso_couple_reference::{
    HHeModel,
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    positive_spectral::SpectralMode,
    retarded_transport::RetardedControls,
    source_age::{AgeStep, Cohort, SourceAgeBridge},
};
pub fn fixture(
    shear: f64,
    full: bool,
    fe: f64,
    spectrum: SpectralMode,
    gl: usize,
    m: usize,
) -> (SourceAgeBridge, RetardedControls, NetworkConfig, FullState) {
    let mut n = [0.; 13];
    for (sp, v) in [
        (S::H1Neutral, 1000.),
        (S::H1Ionized, 900.),
        (S::DNeutral, 25.),
        (S::DIonized, 5.),
        (S::He4Neutral, 300.),
        (S::He4SinglyIonized, 100.),
        (S::He4DoublyIonized, 60.),
    ] {
        n[sp as usize] = v;
    }
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let gas = FullState {
        gas: MixtureState {
            nuclei,
            thermal_j_m3: 1.5
                * KB_J_K
                * nuclei.thermal_particle_density_all_thermal_m3().unwrap()
                * 10000.,
        },
        photon_bins: vec![],
        elapsed_s: 0.,
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
    };
    let src = AxbiSource::new(1900. / (21f64.powi(3) * 1e6), fe, 16, 8).unwrap();
    let geom = ConstantAxisymmetricBackground::new(
        0.,
        AxisymmetricPoint::new(1. / 21., 0., 1.2e-16, shear * 1.2e-16).unwrap(),
        [0., 1.5e14],
    )
    .unwrap();
    let base = SourceAgeBridge::new(src, geom).unwrap();
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let mut conf = NetworkConfig::source_bound(
        DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        SOURCE_ID,
    );
    conf.use_collisions = full;
    conf.use_cx = full;
    conf.use_cmb = full;
    (
        base,
        RetardedControls::new(gl, m, spectrum).unwrap(),
        conf,
        gas,
    )
}
pub fn pulse(base: &SourceAgeBridge, e: f64, mu: f64, n: f64) -> Cohort {
    Cohort {
        birth_time_s: 0.,
        birth_geometry: base.geometry.snapshot(0.).unwrap(),
        energy_at_birth_ev: e,
        direction_at_birth: [(1. - mu * mu).sqrt(), 0., mu],
        n_comoving_m3: n,
        spectral_index: 0,
        angular_index: 0,
    }
}
/// Complete explicit bit serialization. Includes *every* current AgeStep/History,
/// FullState, MixtureState, Cohort and EventBudget field; no float tolerance.
pub fn step_bits(r: &AgeStep) -> Vec<u64> {
    let s = &r.state;
    let f = &s.full;
    let mut v = Vec::with_capacity(128 + s.cohorts.len() * 15);
    macro_rules! floats{($($x:expr),* $(,)?)=>{$(v.push(($x).to_bits());)*};}
    for sp in S::ALL {
        floats!(f.gas.nuclei.density_m3(sp));
    }
    floats!(
        f.gas.thermal_j_m3,
        f.escaped_j_m3,
        f.cmb_reservoir_j_m3,
        f.elapsed_s
    );
    v.push(f.photon_bins.len() as u64);
    for b in &f.photon_bins {
        floats!(b.energy_ev, b.number_m3);
    }
    floats!(
        s.time_s,
        s.geometry_work_j_com3,
        s.source_injected_count_com3,
        s.source_injected_energy_j_com3,
        s.photon_absorbed_count_com3,
        s.max_grey_number_relative_error
    );
    for x in s.max_grey_species_relative_error {
        floats!(x);
    }
    v.push(s.chemistry_accepted as u64);
    v.push(s.cohorts.len() as u64);
    for c in &s.cohorts {
        floats!(c.birth_time_s, c.energy_at_birth_ev, c.n_comoving_m3);
        for x in c.birth_geometry.scale_factors {
            floats!(x);
        }
        for x in c.birth_geometry.hubble_per_s {
            floats!(x);
        }
        for x in c.direction_at_birth {
            floats!(x);
        }
        v.push(c.spectral_index as u64);
        v.push(c.angular_index as u64);
    }
    floats!(
        r.source_birth_com3,
        r.radiation_redshift_work_j_com3,
        r.adiabatic_gas_work_j_com3,
        r.projected_grey_absorption_relative_error,
        r.global_energy_relative_error
    );
    for x in r.projected_grey_species_relative_error {
        floats!(x);
    }
    let b = &r.chemistry_budget;
    for arr in [b.photo_events_m3, b.ci_events_m3, b.rr_events_m3] {
        for x in arr {
            floats!(x);
        }
    }
    floats!(
        b.dr_hei_m3,
        b.cx_signed_m3,
        b.photo_energy_j_m3,
        b.thermal_change_j_m3,
        b.chemical_change_j_m3,
        b.escape_change_j_m3,
        b.cmb_change_j_m3,
        b.freefree_integrated_j_m3,
        b.d_electron_integrated_m3
    );
    v
}
pub fn bit_parity(a: &AgeStep, b: &AgeStep) {
    let aa = step_bits(a);
    let bb = step_bits(b);
    assert_eq!(aa.len(), bb.len());
    for (i, (x, y)) in aa.iter().zip(&bb).enumerate() {
        assert_eq!(x, y, "bit-level state mismatch field {i}");
    }
}
