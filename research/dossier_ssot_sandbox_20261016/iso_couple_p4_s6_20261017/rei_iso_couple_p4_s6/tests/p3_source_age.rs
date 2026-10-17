//! Source-bound geometric/clock/photo bridge with exact imported MD14 and Bianchi-I owners.
use rei_iso_couple_reference::{
    HHeModel,
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{
        AxisymmetricPoint, CharacteristicRay, ConstantAxisymmetricBackground, GeometryBackground,
    },
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    source_age::SourceAgeBridge,
};
const THRESHOLD: &str = "MANUFACTURED_P3_TEST_D_BINDING";
fn initial_neutrals(he: f64, fully_ionized: bool) -> FullState {
    let mut n = [0.0; 13];
    if fully_ionized {
        n[S::H1Ionized as usize] = 1900.0;
        n[S::He4DoublyIonized as usize] = he;
        n[S::DIonized as usize] = 30.0;
    } else {
        n[S::H1Neutral as usize] = 1000.0;
        n[S::H1Ionized as usize] = 900.0;
        n[S::He4Neutral as usize] = he;
        n[S::He4SinglyIonized as usize] = he / 3.0;
        n[S::He4DoublyIonized as usize] = he / 5.0;
        n[S::DNeutral as usize] = 25.0;
        n[S::DIonized as usize] = 5.0;
    }
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let nth = nuclei.thermal_particle_density_all_thermal_m3().unwrap();
    FullState {
        gas: MixtureState {
            nuclei,
            thermal_j_m3: 1.5 * KB_J_K * nth * 1e4,
        },
        photon_bins: vec![],
        escaped_j_m3: 0.0,
        cmb_reservoir_j_m3: 0.0,
        elapsed_s: 0.0,
    }
}
fn config() -> NetworkConfig {
    let h = HHeModel::controlled_fixture().threshold_ev[0];
    NetworkConfig::source_bound(
        DAtomicProvider::new(h, h + 0.0037, THRESHOLD).unwrap(),
        SOURCE_ID,
    )
}
fn bridge(h: f64, s: f64, n_segment: usize, mu: usize) -> SourceAgeBridge {
    let nh0 = 1900.0 / (21.0f64.powi(3) * 1e6);
    let source = AxbiSource::new(nh0, 0.2, n_segment, mu).unwrap();
    let point = AxisymmetricPoint::new(1.0 / 21.0, 0.0, h, s).unwrap();
    let geo = ConstantAxisymmetricBackground::new(0.0, point, [0.0, 1.5e14]).unwrap();
    SourceAgeBridge::new(source, geo).unwrap()
}
fn approx(x: f64, y: f64, tol: f64) {
    assert!(
        (x - y).abs() <= tol * x.abs().max(y.abs()).max(1e-40),
        "x={x:.15e} y={y:.15e} tol={tol}"
    );
}
#[test]
fn actual_source_positive_normalized() {
    let b = bridge(1.2e-16, 0.0, 16, 8);
    assert_eq!(b.source.spectral_cells.len(), 48);
    assert_eq!(b.source.angular_cells.len(), 8);
    approx(
        b.source
            .spectral_cells
            .iter()
            .map(|s| s.photon_fraction)
            .sum(),
        1.0,
        2e-14,
    );
    approx(
        b.source
            .angular_cells
            .iter()
            .map(|s| s.count_fraction)
            .sum(),
        1.0,
        2e-14,
    );
    let o = b.source.at_redshift(19.8).unwrap();
    let n_h0 = 1900.0 / (21.0f64.powi(3) * 1e6);
    approx(
        o.proper_photons_cm3_s / o.per_h_s,
        n_h0 * 20.8f64.powi(3),
        3e-15,
    );
    assert!(b.source.at_redshift(20.1).is_err());
}
#[test]
fn exact_native_anisotropic_killing_ray() {
    let b = bridge(1.2e-16, 2.4e-17, 16, 8);
    let t = 9.0e13;
    let g0 = b.geometry.snapshot(0.0).unwrap();
    let g1 = b.geometry.snapshot(t).unwrap();
    for (direction, rate) in [
        ([1.0, 0.0, 0.0], 1.2e-16 - 2.4e-17),
        ([0.0, 0.0, 1.0], 1.2e-16 + 2.0 * 2.4e-17),
    ] {
        let v = CharacteristicRay::new(70.0, direction, 0.0)
            .unwrap()
            .pullback(&g0, &g1)
            .unwrap();
        approx(v.energy_ev, 70.0 * (-rate * t).exp(), 2e-14);
    }
    approx(
        g1.volume_factor().unwrap() / g0.volume_factor().unwrap(),
        (3.0 * 1.2e-16 * t).exp(),
        3e-14,
    );
}
#[test]
fn first_burst_chemistry_source_and_ledgers() {
    let b = bridge(1.2e-16, 0.06 * 1.2e-16, 16, 8);
    let s = b
        .initial(initial_neutrals(300.0, false), &config(), 0.0)
        .unwrap();
    let out = b.advance(&s, &config(), 1e10).unwrap();
    assert_eq!(out.state.cohorts.len(), 384);
    assert!(out.source_birth_com3 > 0.0);
    assert!(out.global_energy_relative_error < 3e-10);
    assert!(out.state.photon_absorbed_count_com3 > 0.0);
    assert!(out.state.time_s == 1e10);
    eprintln!(
        "grey error 8-group={}",
        out.projected_grey_absorption_relative_error
    );
    eprintln!(
        "species grey {:?}",
        out.projected_grey_species_relative_error
    );
    assert!(out.projected_grey_absorption_relative_error < 5e-3);
}
#[test]
fn birth_cohorts_retain_age_and_photon_number() {
    let b = bridge(1.2e-16, 0.1 * 1.2e-16, 16, 8);
    let s = b
        .initial(initial_neutrals(300.0, false), &config(), 0.0)
        .unwrap();
    let a = b.advance(&s, &config(), 3e10).unwrap();
    let q = b.advance(&a.state, &config(), 3e10).unwrap();
    assert_eq!(q.state.cohorts.len(), 768);
    assert_ne!(
        q.state.cohorts[0].birth_time_s,
        q.state.cohorts[384].birth_time_s
    );
    let remain = q.state.cohorts.iter().map(|x| x.n_comoving_m3).sum::<f64>();
    approx(
        q.state.source_injected_count_com3,
        remain + q.state.photon_absorbed_count_com3,
        2e-11,
    );
    assert!(q.global_energy_relative_error < 3e-10);
}
#[test]
fn no_absorption_constant_source_exact_birth_count() {
    let b = bridge(0.0, 0.0, 16, 8);
    let mut c = config();
    c.use_collisions = false;
    c.use_cmb = false;
    c.use_cx = false;
    let x = b.initial(initial_neutrals(300.0, true), &c, 0.0).unwrap();
    let src = b.source.at_redshift(20.0).unwrap();
    let expected = src.proper_photons_cm3_s * 1e6 * 3.0e10 * (1.0 / 21.0f64).powi(3);
    let mut s = x;
    for _ in 0..8 {
        s = b.advance(&s, &c, 3.0e10 / 8.0).unwrap().state;
    }
    approx(s.source_injected_count_com3, expected, 4e-14);
    approx(
        s.cohorts.iter().map(|q| q.n_comoving_m3).sum(),
        expected,
        4e-14,
    );
    approx(s.photon_absorbed_count_com3, 0.0, 0.0);
}
#[test]
fn frozen_original_p2_domain_and_source_identity_guards() {
    let b = bridge(1.2e-16, 0.0, 16, 8);
    let s = b
        .initial(initial_neutrals(300.0, false), &config(), 0.0)
        .unwrap();
    assert!(b.advance(&s, &config(), -1.0).is_err());
    assert!(b.source_births(2.0e14, 1.0).is_err());
    let mut c = config();
    c.photon_source = "NOT_MD14";
    assert!(b.advance(&s, &c, 1e10).is_err());
}
#[test]
fn p2_64_bin_representation_gate() {
    let nh0 = 1900.0 / (21.0f64.powi(3) * 1e6);
    let src = AxbiSource::new(nh0, 0.2, 16, 32).unwrap();
    let geo = bridge(1.2e-16, 0.0, 16, 8).geometry;
    assert!(SourceAgeBridge::new(src, geo).is_err());
}
#[test]
fn source_births_not_equal_number_weighted_energy_at_different_ages() {
    let b = bridge(1.2e-16, 0.08 * 1.2e-16, 16, 8);
    let a = b.source_births(5e12, 1e12).unwrap();
    let q = b.source_births(6e12, 1e12).unwrap();
    let g = b.geometry.snapshot(8e12).unwrap();
    let xa = a[0].ray_at(&g).unwrap().energy_ev;
    let xb = q[0].ray_at(&g).unwrap().energy_ev;
    assert!(xa < xb);
    let p = b.project(&[a[0].clone(), q[0].clone()], &g).unwrap();
    let expected = (a[0].n_comoving_m3 * xa + q[0].n_comoving_m3 * xb)
        / (a[0].n_comoving_m3 + q[0].n_comoving_m3);
    approx(p[0].energy_ev, expected, 3e-15);
}
