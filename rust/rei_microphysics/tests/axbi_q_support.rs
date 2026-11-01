//! C7: scientific support provenance for a positive MD14 fixed-q source.
use rei_microphysics::axbi_background::{AxbiBackground, BackgroundFamily, Cosmology};
use rei_microphysics::axbi_q_grid::QFixedGrid;
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::AxisymmetricPoint;

fn owner_source() -> AxbiSource {
    use rei_microphysics::igm_background::{FlatFlrwBackground, FlatFlrwConfig};
    let a: f64 = 1.0 / 21.0;
    let h0 = 67.4e5 / 3.085_677_581_491_367e24;
    let bg = FlatFlrwBackground::new(FlatFlrwConfig {
        h0_per_s: h0,
        omega_m: 0.315,
        omega_r: 0.000092,
        omega_lambda: 0.684908,
        omega_b: 0.0224 / 0.674_f64.powi(2),
        helium_mass_fraction: 0.2454,
        tcmb0_k: 2.7255,
        ln_a_min: a.ln(),
        ln_a_max: (0.2_f64).ln(),
        parameter_source: "C7 actual chosen scenario".to_string(),
    })
    .unwrap();
    AxbiSource::new(bg.n_h_comoving_cm3(), 0.2, 16, 32).unwrap()
}
fn geometries(
    q: f64,
) -> (
    rei_microphysics::GeometrySnapshot,
    rei_microphysics::GeometrySnapshot,
) {
    let c = Cosmology {
        h0_per_s: 67.4e5 / 3.085_677_581_491_367e24,
        omega_m: 0.315,
        omega_r: 0.000092,
        omega_lambda: 0.684908,
    };
    let bg = AxbiBackground::new(
        c,
        1.0 / 21.0,
        1.0 / 5.0,
        0.0,
        q,
        BackgroundFamily::PhysicalDensityFixed,
        4096,
    )
    .unwrap();
    (
        bg.point_at_scale(1.0 / 21.0).unwrap().geometry().unwrap(),
        bg.point_at_scale(1.0 / 5.0).unwrap().geometry().unwrap(),
    )
}
#[test]
fn real_md14_new_source_support_is_subcell_clipped() {
    let (g0, gend) = geometries(0.01);
    let src = owner_source();
    let mut early = QFixedGrid::new(&src, g0, 64, 433.0).unwrap();
    early.inject(&g0, 20., 1e10, 1).unwrap();
    let mut late = QFixedGrid::new(&src, g0, 64, 433.0).unwrap();
    late.inject(&gend, 4., 1e10, 1).unwrap();
    for grid in [&early, &late] {
        let (lo, hi) = grid.support_bounds();
        assert_eq!(lo.len(), grid.number().len());
        for (idx, n) in grid.number().iter().enumerate() {
            if *n > 0.0 {
                assert!(lo[idx] > 0.0 && hi[idx] > lo[idx]);
                assert!(lo[idx] <= grid.ref_energy_moment()[idx] / n * (1. + 1e-10));
                assert!(hi[idx] >= grid.ref_energy_moment()[idx] / n * (1. - 1e-10));
            } else {
                assert_eq!(lo[idx], 0.0);
                assert_eq!(hi[idx], 0.0);
            }
        }
    }
    assert!(late
        .support_bounds()
        .0
        .iter()
        .any(|x| *x > 55.0 && *x < 59.0));
}
#[test]
fn two_ages_same_selected_source_have_connected_common_support() {
    let src = owner_source();
    for q in [-0.01, 0.0, 0.01] {
        let (g0, gf) = geometries(q);
        let mut total = QFixedGrid::new(&src, g0, 128, 433.0).unwrap();
        let a = total.inject(&g0, 20.0, 1e10, 1).unwrap();
        let b = total.inject(&gf, 4.0, 1e10, 4).unwrap();
        let mom = total.observe(&gf).unwrap();
        assert!(
            (mom.photon_number_per_h - a.added_photons_per_h - b.added_photons_per_h).abs() < 4e-18
        );
        let (lo, hi) = total.support_bounds();
        for (k, n) in total.number().iter().enumerate() {
            if *n > 0.0 {
                assert!(lo[k] < hi[k] && hi[k] <= 433.0);
            }
        }
    }
}
#[test]
fn support_bounded_absorption_preserves_photon_energy_and_thread_equivalence() {
    let src = owner_source();
    let (g0, gf) = geometries(0.01);
    let mut one = QFixedGrid::new(&src, g0, 256, 433.0).unwrap();
    one.inject(&g0, 20.0, 1e10, 1).unwrap();
    one.inject(&gf, 4.0, 1e10, 1).unwrap();
    let mut four = one.clone();
    let before = one.observe(&gf).unwrap();
    let gas = [2e-6, 3e-7, 1e-8];
    let dt = 1e9;
    let a = one.absorb_reconstructed_support(&gf, gas, dt, 1).unwrap();
    let b = four.absorb_reconstructed_support(&gf, gas, dt, 4).unwrap();
    for (x, y) in one.number().iter().zip(four.number()) {
        assert_eq!(x.to_bits(), y.to_bits());
    }
    for (x, y) in one.ref_energy_moment().iter().zip(four.ref_energy_moment()) {
        assert_eq!(x.to_bits(), y.to_bits());
    }
    let after = one.observe(&gf).unwrap();
    let nerr = before.photon_number_per_h
        - after.photon_number_per_h
        - a.absorbed_per_h.iter().sum::<f64>();
    let eerr = before.photon_energy_ev_per_h
        - after.photon_energy_ev_per_h
        - a.binding_ev_per_h
        - a.heat_ev_per_h;
    assert!(nerr.abs() <= 2e-11 * before.photon_number_per_h);
    assert!(eerr.abs() <= 2e-11 * before.photon_energy_ev_per_h);
    for i in 0..3 {
        assert!((a.absorbed_per_h[i] - b.absorbed_per_h[i]).abs() < 1e-17);
    }
}
#[test]
fn out_of_domain_source_rejects_without_support_mutation() {
    let src = owner_source();
    let (g0, _) = geometries(0.0);
    let mut grid = QFixedGrid::new(&src, g0, 64, 433.0).unwrap();
    grid.inject(&g0, 20.0, 1e10, 1).unwrap();
    let lo = grid.support_bounds().0.to_vec();
    let hi = grid.support_bounds().1.to_vec();
    let contracted = AxisymmetricPoint::new(1.0 / 42.0, 0.0, 1e-16, 0.0)
        .unwrap()
        .snapshot()
        .unwrap();
    assert!(grid.inject(&contracted, 20.0, 1e10, 1).is_err());
    assert_eq!(lo, grid.support_bounds().0);
    assert_eq!(hi, grid.support_bounds().1);
}

#[test]
fn actual_two_age_hi_bias_is_closed_by_two_fixed_age_lanes() {
    let src = owner_source();
    let (g0, gf) = geometries(0.0);
    let ngas = [2.37e-5, 2.0e-6, 0.0];
    // Use the exact selected FlatFlrwBackground proper density rather than
    // guessed numbers: at z4 nH0*(1+z)^3 and fHe=nHe/nH.
    let h0 = 67.4e5 / 3.085_677_581_491_367e24;
    let omega_b = 0.0224 / 0.674_f64.powi(2);
    let rho = 3.0 * h0 * h0 / (8.0 * std::f64::consts::PI * 6.67430e-8);
    let nh0 = (1.0 - 0.2454) * omega_b * rho / 1.67262192595e-24;
    let n_hi = nh0 * 125.0 * (1.0 - 0.0002);
    let n_he_i = nh0 * 125.0 * 0.2454 / (4.0 * (1.0 - 0.2454));
    let gas = [n_hi, n_he_i, ngas[2]];
    let d0 = 1e10;
    let d4 = d0 * src.at_redshift(20.0).unwrap().per_h_s / src.at_redshift(4.0).unwrap().per_h_s;
    let mut pooled = QFixedGrid::new(&src, g0, 256, 433.0).unwrap();
    pooled.inject(&g0, 20.0, d0, 1).unwrap();
    pooled.inject(&gf, 4.0, d4, 1).unwrap();
    let mut early = QFixedGrid::new(&src, g0, 256, 433.0).unwrap();
    let mut late = early.clone();
    early.inject(&g0, 20.0, d0, 1).unwrap();
    late.inject(&gf, 4.0, d4, 1).unwrap();
    let pooled_reaction = pooled
        .absorb_reconstructed_support(&gf, gas, 1e10, 1)
        .unwrap();
    let early_reaction = early
        .absorb_reconstructed_support(&gf, gas, 1e10, 1)
        .unwrap();
    let late_reaction = late
        .absorb_reconstructed_support(&gf, gas, 1e10, 1)
        .unwrap();
    let split_hi = early_reaction.absorbed_per_h[0] + late_reaction.absorbed_per_h[0];
    let independent_scipy = 8.84106359389859e-10;
    let mixed_err = (pooled_reaction.absorbed_per_h[0] / independent_scipy - 1.0).abs();
    let split_err = (split_hi / independent_scipy - 1.0).abs();
    assert!(
        mixed_err > 2e-3,
        "mixed error unexpectedly small {}",
        mixed_err
    );
    assert!(split_err < 1e-6, "two-lane HI error {}", split_err);
    assert!(split_err * 100.0 < mixed_err);
}
#[test]
fn selected_source_epoch_q_intervals_have_common_positive_overlap() {
    use rei_microphysics::CharacteristicRay;
    let src = owner_source();
    for q in [-0.01, 0.0, 0.01] {
        let (g0, gf) = geometries(q);
        for ang in &src.angular_cells {
            let mu = ang.mu;
            let r = CharacteristicRay::new(1.0, [(1.0 - mu * mu).sqrt(), 0.0, mu], 0.0)
                .unwrap()
                .pullback(&g0, &gf)
                .unwrap()
                .energy_ev;
            let max_lower = (13.6 / r).max(13.6);
            let min_upper = (100.0 / r).min(100.0);
            assert!(max_lower < min_upper);
            assert!(
                max_lower < 60.0,
                "actual source q support unexpectedly disjoint"
            );
        }
    }
}
