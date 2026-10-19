//! Real Rust affine-H geometry and source-native Verner/D photo event tests.
use rei_iso_couple_reference::HHeModel;
use rei_iso_couple_reference::affine_threshold_events::{
    AffineHubbleBackground, AffinePhotoControls, FrozenPhotoDensities, affine_photo_cohort,
    affine_photo_segments, affine_threshold_cut_times,
};
use rei_iso_couple_reference::axbi_sources::AxbiSource;
use rei_iso_couple_reference::bianchi_i::GeometryBackground;
use rei_iso_couple_reference::deuterium_atomic::DAtomicProvider;
use rei_iso_couple_reference::full_network::NetworkError;
use rei_iso_couple_reference::source_age::Cohort;

const H0: f64 = 1e-12;
const SLOPE: f64 = -1e-21;
const END: f64 = 5e8;
const DEDGE: f64 = 13.602134599702;
fn bg() -> AffineHubbleBackground {
    AffineHubbleBackground::new(
        0.,
        [1., 1., 1.],
        [H0, H0, H0],
        [SLOPE, SLOPE, SLOPE],
        [0., END],
    )
    .unwrap()
}
fn cohort(bg: &AffineHubbleBackground, t: f64, e: f64, dir: [f64; 3]) -> Cohort {
    Cohort {
        birth_time_s: t,
        birth_geometry: bg.snapshot(t).unwrap(),
        energy_at_birth_ev: e,
        direction_at_birth: dir,
        n_comoving_m3: 1.,
        spectral_index: 0,
        angular_index: 0,
    }
}
fn relative_close(a: f64, b: f64, eps: f64) {
    assert!(
        (a - b).abs() <= eps * b.abs().max(1e-30),
        "a={a:.16e}, b={b:.16e}"
    )
}
#[test]
fn affine_hubble_exact_integral_and_dynamic_derivative() {
    let b = bg();
    let t = 350e6;
    let g = b.snapshot(t).unwrap();
    let integral = H0 * t + 0.5 * SLOPE * t * t;
    relative_close(g.scale_factors[0], integral.exp(), 4e-15);
    relative_close(g.hubble_per_s[2], H0 + SLOPE * t, 4e-15);
    b.certify_energy_squared_convex(0., END).unwrap();
    assert!((g.hubble_per_s[2] - H0).abs() > 3e-13);
}
#[test]
fn retarded_birth_h_and_d_edge_roots_match_quadratic() {
    let b = bg();
    let tb = 5e7;
    let co = cohort(&b, tb, 13.604, [0., 0., 1.]);
    let cut = affine_threshold_cut_times(&co, &b, tb, END, DEDGE).unwrap();
    assert_eq!(cut.len(), 2, "{cut:?}");
    for (i, edge) in [DEDGE, 13.60].into_iter().enumerate() {
        let lg = (13.604 / edge).ln();
        let ht = H0 + SLOPE * tb;
        let discriminant = (ht * ht + 2. * SLOPE * lg).sqrt();
        let delta = 2. * lg / (ht + discriminant); // quadratic cancellation-free
        assert!(
            (cut[i] - tb - delta).abs() < 0.006,
            "expected: {}, actual: {}",
            tb + delta,
            cut[i]
        );
        relative_close(
            co.ray_at(&b.snapshot(cut[i]).unwrap()).unwrap().energy_ev,
            edge,
            3e-14,
        );
    }
    let segments = affine_photo_segments(&co, &b, tb, END, DEDGE).unwrap();
    assert_eq!(segments.len(), 3);
    assert!((segments.iter().map(|(a, b)| b - a).sum::<f64>() - (END - tb)).abs() < 1e-7);
}
#[test]
fn two_edge_crossings_in_time_varying_mixed_contraction_and_expansion() {
    let h = 1e-12;
    let b = AffineHubbleBackground::new(0., [1.; 3], [-h, -h, h], [-1e-25; 3], [0., 8e11]).unwrap();
    let co = cohort(
        &b,
        0.,
        27.,
        [(0.1f64).sqrt(), (0.1f64).sqrt(), (0.8f64).sqrt()],
    );
    let cuts = affine_threshold_cut_times(&co, &b, 0., 8e11, DEDGE).unwrap();
    assert_eq!(cuts.len(), 2, "{cuts:?}");
    for t in cuts {
        let e = co.ray_at(&b.snapshot(t).unwrap()).unwrap().energy_ev;
        relative_close(e, 24.59, 6e-15);
    }
}
#[test]
fn no_convexity_certificate_is_not_false_pass() {
    let b = AffineHubbleBackground::new(0., [1.; 3], [0.; 3], [1e-21; 3], [0., END]).unwrap();
    let co = cohort(&b, 0., 20., [0., 0., 1.]);
    assert_eq!(
        b.certify_energy_squared_convex(0., END),
        Err(NetworkError::InputOutsideDomain)
    );
    assert_eq!(
        affine_threshold_cut_times(&co, &b, 0., END, DEDGE),
        Err(NetworkError::InputOutsideDomain)
    );
}
#[test]
fn birth_time_and_source_domain_fail_closed() {
    let b = bg();
    let co = cohort(&b, 5e7, 13.604, [0., 0., 1.]);
    assert_eq!(
        affine_threshold_cut_times(&co, &b, 0., END, DEDGE),
        Err(NetworkError::InvalidInput)
    );
    assert_eq!(
        affine_threshold_cut_times(&co, &b, 5e7, END, 13.6),
        Err(NetworkError::InvalidInput)
    );
    assert_eq!(
        affine_threshold_cut_times(&co, &b, 5e7, END + 1., DEDGE),
        Err(NetworkError::InputOutsideDomain)
    );
}
#[test]
fn photons_single_owner_source_native_competing_hi_and_di() {
    let b = bg();
    let co = cohort(&b, 0., 13.604, [0., 0., 1.]);
    let chi_h = HHeModel::controlled_fixture().threshold_ev[0];
    let provider = DAtomicProvider::new(chi_h, DEDGE, "MANUFACTURED_D_H_DELTA_CHI").unwrap();
    let g = FrozenPhotoDensities {
        proper_reference_time_s: 0.,
        neutral_m3: [8e3, 0., 0., 1.6e3],
    };
    let mut runs = Vec::new();
    for steps in [1, 4, 32] {
        let v = affine_photo_cohort(
            &co,
            &b,
            provider,
            g,
            0.,
            END,
            AffinePhotoControls {
                substeps: steps,
                split_events: true,
            },
        )
        .unwrap();
        assert_eq!(v.event_cuts, 2);
        assert!(v.absorbed_count_com3[0] > 0. && v.absorbed_count_com3[3] > 0.);
        assert!(v.absorbed_count_com3[1] == 0. && v.absorbed_count_com3[2] == 0.);
        assert!(v.count_residual().abs() < 2e-15);
        assert!(v.event_energy_residual().abs() < 5e-31);
        assert!(v.thermal_energy_j_com3 > 0.);
        assert!(v.radiation_geometry_work_j_com3 < 0.);
        runs.push(v);
    }
    let old = affine_photo_cohort(
        &co,
        &b,
        provider,
        g,
        0.,
        END,
        AffinePhotoControls {
            substeps: 1,
            split_events: false,
        },
    )
    .unwrap();
    assert_eq!(old.event_cuts, 0);
    // For this test E(mid) is below D, so unsplit midpoint skips all D events.
    assert_eq!(old.absorbed_count_com3[3], 0.);
    assert!(runs[0].absorbed_count_com3[3] > 1e-3);
    assert!((runs[0].survivor_count_com3 - runs[2].survivor_count_com3).abs() < 1e-6);
}
#[test]
fn source_owned_energy_cell_and_birth_are_retained_without_rebin() {
    let s = AxbiSource::new(1900. / (21_f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
    assert_eq!(s.spectral_cells.len(), 48);
    let b =
        AffineHubbleBackground::new(0., [1. / 21.; 3], [1e-12; 3], [-1e-21; 3], [0., END]).unwrap();
    let cell = &s.spectral_cells[0];
    let birth = 2e7;
    let mut co = cohort(&b, birth, cell.energy_ev, [0., 0., 1.]);
    co.n_comoving_m3 = cell.photon_fraction * s.angular_cells[0].count_fraction;
    let chi_h = HHeModel::controlled_fixture().threshold_ev[0];
    let d = DAtomicProvider::new(chi_h, DEDGE, "MANUFACTURED_D_H_DELTA_CHI").unwrap();
    let g = FrozenPhotoDensities {
        proper_reference_time_s: 0.,
        neutral_m3: [8e3, 0., 0., 1.6e3],
    };
    let p = affine_photo_cohort(
        &co,
        &b,
        d,
        g,
        birth,
        END,
        AffinePhotoControls {
            substeps: 8,
            split_events: true,
        },
    )
    .unwrap();
    assert!(p.initial_count_com3 > 0.);
    assert!(p.count_residual().abs() < 2e-15 * p.initial_count_com3);
    assert!(p.event_energy_residual().abs() < 1e-25 * p.initial_count_com3);
}

#[test]
fn source_native_gl2_age_and_photo_owner_positive_with_varying_hubble() {
    use rei_iso_couple_reference::affine_threshold_events::{
        AffineSourceControls, source_on_affine_photo_pilot,
    };
    use rei_iso_couple_reference::positive_spectral::SpectralMode;
    let s = AxbiSource::new(1900. / (21_f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
    let b =
        AffineHubbleBackground::new(0., [1. / 21.; 3], [1e-10; 3], [-1e-19; 3], [0., END]).unwrap();
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let d = DAtomicProvider::new(chi, DEDGE, "MANUFACTURED_D_H_DELTA_CHI").unwrap();
    let gas = FrozenPhotoDensities {
        proper_reference_time_s: 0.,
        neutral_m3: [8000., 2000., 500., 1600.],
    };
    let v = source_on_affine_photo_pilot(
        &s,
        &b,
        d,
        gas,
        0.,
        END,
        AffineSourceControls {
            gauss_birth: 2,
            photon: AffinePhotoControls {
                substeps: 2,
                split_events: true,
            },
            spectrum: SpectralMode::SplitPositiveGauss3,
        },
    )
    .unwrap();
    assert_eq!(v.true_cohorts, 2352); // 2 births x (48 owner, one D-split) x 8 GL angles
    assert!(v.newborn_count_com3 > 0.);
    assert!(v.survivor_count_com3 > 0.);
    assert!(v.event_cuts > 0);
    assert!(v.number_residual().abs() < 8e-13 * v.newborn_count_com3);
    assert!(v.event_energy_residual().abs() < 8e-13 * v.photo_energy_j_com3);
    assert!(v.heat_j_com3 >= 0. && v.binding_j_com3 >= 0.);
}
