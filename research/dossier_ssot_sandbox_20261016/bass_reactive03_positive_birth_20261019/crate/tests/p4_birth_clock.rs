use rei_iso_couple_reference::{
    HHeModel,
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig, NetworkError},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    positive_age::PositiveAgeBridge,
    positive_birth_clock::{PositiveBirthClockBridge, photon_slab},
    source_age::SourceAgeBridge,
};

fn input(h: f64, shear: f64, fesc: f64) -> (PositiveBirthClockBridge, NetworkConfig, FullState) {
    let src = AxbiSource::new(1900. / (21.0f64.powi(3) * 1e6), fesc, 16, 8).unwrap();
    let bg = ConstantAxisymmetricBackground::new(
        0.,
        AxisymmetricPoint::new(1. / 21., 0., h, shear).unwrap(),
        [0., 1.5e14],
    )
    .unwrap();
    let bridge = PositiveBirthClockBridge(SourceAgeBridge::new(src, bg).unwrap());
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
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let nthermal = nuclei.thermal_particle_density_all_thermal_m3().unwrap();
    let state = FullState {
        gas: MixtureState {
            nuclei,
            thermal_j_m3: 1.5 * KB_J_K * nthermal * 10000.,
        },
        photon_bins: vec![],
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
        elapsed_s: 0.,
    };
    (bridge, conf, state)
}
fn rel(a: f64, b: f64) -> f64 {
    (a - b).abs() / a.abs().max(b.abs()).max(1e-50)
}

#[test]
fn slab_small_large_and_reject_nonfinite() {
    for tau in [
        0., 1e-300, 1e-20, 1e-12, 1e-7, 0.0009999, 0.001, 0.5, 2., 60., 1e5,
    ] {
        let x = photon_slab(tau).unwrap();
        for f in [
            x.old_surviving,
            x.old_absorbed,
            x.new_surviving,
            x.new_absorbed,
        ] {
            assert!(f.is_finite() && (0. ..=1.).contains(&f), "tau {tau}, f {f}");
        }
        assert!((x.old_surviving + x.old_absorbed - 1.).abs() < 3e-16);
        assert!((x.new_surviving + x.new_absorbed - 1.).abs() < 3e-16);
        assert!(x.new_surviving >= x.old_surviving);
        assert!(x.new_absorbed <= x.old_absorbed);
    }
    for x in [-1.0, f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
        assert_eq!(photon_slab(x).unwrap_err(), NetworkError::InvalidInput);
    }
}
#[test]
fn kernel_matches_independent_simpson_convolution() {
    let n = 5000;
    for tau in [0.001, 0.05, 0.3, 1., 3., 10.] {
        let mut s = 0.0;
        for i in 0..=n {
            let u = i as f64 / n as f64;
            let weight = if i == 0 || i == n {
                1.
            } else if i % 2 == 0 {
                2.
            } else {
                4.
            };
            s += weight * (-tau * (1. - u)).exp();
        }
        let simpson = s / (3. * n as f64);
        let kernel = photon_slab(tau).unwrap();
        assert!(
            rel(kernel.new_surviving, simpson) < 3e-11,
            "tau {tau}: {simpson} vs {}",
            kernel.new_surviving
        );
    }
}
#[test]
fn asymptotic_first_order_old_vs_second_order_slab() {
    // Exact constant J, k frozen physical slab. Old midpoint-j photons
    // are artificially exposed for a full step; new are emitted throughout.
    let j: f64 = 2.0;
    let k: f64 = 1.3;
    let total: f64 = 2.0;
    let exact = j / k * (1. - (-k * total).exp());
    let mut err_old = vec![];
    let mut err_new = vec![];
    for n in [8, 16, 32, 64, 128] {
        let dt = total / n as f64;
        let x = photon_slab(k * dt).unwrap();
        let (mut a, mut b) = (0., 0.);
        for _ in 0..n {
            a = a * x.old_surviving + j * dt * x.old_surviving;
            b = b * x.old_surviving + j * dt * x.new_surviving;
        }
        err_old.push((a - exact).abs());
        err_new.push((b - exact).abs());
    }
    assert!(err_new.iter().all(|e| *e < 1.5e-14));
    assert!(
        err_old
            .windows(2)
            .all(|w| w[0] > 1.85 * w[1] && w[0] < 2.15 * w[1])
    );
}
#[test]
fn native_owner_first_birth_improves_exposure_without_double_photons() {
    let (new, conf, full) = input(1.2e-16, 0., 0.2);
    let initial = new.initial(full, &conf, 0.).unwrap();
    let old = PositiveAgeBridge(new.0.clone());
    let a = old.advance(&initial, &conf, 1e10).unwrap();
    let b = new.advance(&initial, &conf, 1e10).unwrap();
    assert_eq!(a.state.cohorts.len(), 384);
    assert_eq!(b.state.cohorts.len(), 384);
    assert!(
        b.state
            .cohorts
            .iter()
            .zip(&a.state.cohorts)
            .all(|(new, old)| new.n_comoving_m3 >= old.n_comoving_m3)
    );
    let sum_old = a.chemistry_budget.photo_events_m3.iter().sum::<f64>();
    let sum_new = b.chemistry_budget.photo_events_m3.iter().sum::<f64>();
    assert!(sum_new < sum_old, "{sum_old:e} vs {sum_new:e}");
    assert!(b.global_energy_relative_error < 3e-10);
    assert!(
        rel(
            b.state.source_injected_count_com3,
            b.state.cohorts.iter().map(|x| x.n_comoving_m3).sum::<f64>()
                + b.state.photon_absorbed_count_com3
        ) < 1e-11
    );
}
#[test]
fn double_age_with_native_chemistry_and_single_owner() {
    for shear in [-0.06 * 1.2e-16, 0., 0.06 * 1.2e-16] {
        let (b, conf, full) = input(1.2e-16, shear, 0.2);
        let s0 = b.initial(full, &conf, 0.).unwrap();
        let s1 = b.advance(&s0, &conf, 3e10).unwrap();
        let s2 = b.advance(&s1.state, &conf, 3e10).unwrap();
        assert_eq!(s2.state.cohorts.len(), 768);
        assert_eq!(s2.state.chemistry_accepted, 2);
        assert!(s1.global_energy_relative_error < 3e-10);
        assert!(s2.global_energy_relative_error < 3e-10);
        assert!(s2.chemistry_budget.cx_signed_m3.is_finite());
        assert!(
            rel(
                s2.state.source_injected_count_com3,
                s2.state
                    .cohorts
                    .iter()
                    .map(|x| x.n_comoving_m3)
                    .sum::<f64>()
                    + s2.state.photon_absorbed_count_com3
            ) < 1e-10
        );
    }
}
#[test]
fn preserved_state_on_invalid_dt_source_and_domain() {
    let (b, conf, full) = input(1.2e-16, 0., 0.2);
    let initial = b.initial(full, &conf, 0.).unwrap();
    let initial_n = b.0.source.spectral_cells.len();
    for dt in [-1.0, 0., f64::NAN, 1e17] {
        assert!(b.advance(&initial, &conf, dt).is_err());
        assert_eq!(initial.cohorts.len(), 0);
        assert_eq!(b.0.source.spectral_cells.len(), initial_n);
    }
    let mut invalid = conf;
    invalid.photon_source = "NOT_MD14";
    assert_eq!(
        b.advance(&initial, &invalid, 1e10).unwrap_err(),
        NetworkError::SourceMismatch
    );
}
#[test]
fn no_photo_when_opacity_zero_has_exact_birth_conservation() {
    // Source still injects photons, but only ionized H/D and He III are present.
    // This verifies the zero-total-kappa branch without changing any owner code.
    let (b, mut conf, mut full) = input(0., 0., 0.2);
    let mut n = [0.; 13];
    n[S::H1Ionized as usize] = 1900.;
    n[S::He4DoublyIonized as usize] = 460.;
    n[S::DIonized as usize] = 30.;
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let nth = nuclei.thermal_particle_density_all_thermal_m3().unwrap();
    full.gas = MixtureState {
        nuclei,
        thermal_j_m3: 1.5 * KB_J_K * nth * 10000.,
    };
    conf.use_cx = false;
    conf.use_collisions = false;
    conf.use_cmb = false;
    let s = b.initial(full, &conf, 0.).unwrap();
    let a = b.advance(&s, &conf, 1e9).unwrap();
    assert!(a.chemistry_budget.photo_events_m3.iter().all(|x| *x == 0.));
    assert!(
        rel(
            a.state.source_injected_count_com3,
            a.state.cohorts.iter().map(|x| x.n_comoving_m3).sum::<f64>()
        ) < 1e-13
    );
}
