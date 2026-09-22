use rei_microphysics::*;

fn close(a: f64, b: f64) {
    assert!((a - b).abs() <= 5e-13 * b.abs(), "{a:e} != {b:e}");
}
fn table() -> PchipTable {
    PchipTable::new(vec![-2.0, 0.0, 2.0], [vec![0.0; 2], vec![0.0; 2], vec![0.25; 2], vec![-3.0, -2.5]]).unwrap()
}
fn state() -> State {
    State { n_comoving_per_cmpc3: [1.0, 2.0, 3.0, 4.0], x_hii: 0.8,
        helium: [0.6, 0.3, 0.1], u_erg_per_cm3: 1e-12, gamma_hi_per_s: 1e-12 }
}
fn params() -> GroupParams {
    GroupParams { redshift: 3.0, n_h_proper_per_cm3: 1.2e-5, n_he_proper_per_cm3: 1e-6,
        hubble_per_s: 1e-16, sigma_hi_cm2: [6e-18, 2e-18, 1e-18, 2e-19],
        sigma_hei_cm2: [0.0, 7e-18, 3e-18, 5e-19], sigma_heii_cm2: [0.0, 0.0, 0.0, 1e-18],
        redshift_coeff: [1.0, 2.0, 3.0, 4.0], source_fraction: [0.4, 0.3, 0.2, 0.1],
        lowgroup_log_opacity: [table(), table()] }
}
#[test]
fn specified_mass_and_signed_examples() {
    assert_eq!(positive_mass_projection(&[1.0, 3.0], 8.0).unwrap(), vec![2.0, 6.0]);
    let s = signed_transfer_lift(-4.0, &[1.0, 3.0]).unwrap();
    assert_eq!(s.positive, vec![0.0, 0.0]);
    assert_eq!(s.negative, vec![1.0, 3.0]);
    assert_eq!(s.signed, vec![-1.0, -3.0]);
}
#[test]
fn zero_support_is_function_specific() {
    assert_eq!(positive_mass_projection(&[0.0, 0.0], 0.0).unwrap(), vec![0.0, 0.0]);
    assert_eq!(positive_mass_projection(&[], 0.0).unwrap(), Vec::<f64>::new());
    assert!(positive_mass_projection(&[], 1.0).is_err());
    assert!(signed_transfer_lift(0.0, &[0.0, 0.0]).is_err());
    assert!(signed_transfer_lift(0.0, &[]).is_err());
}
#[test]
fn error_precedence_and_nonfinite_inputs() {
    assert_eq!(positive_mass_projection(&[f64::NAN], -1.0).unwrap_err().code(), "PRIOR_NOT_FINITE");
    assert_eq!(positive_mass_projection(&[-1.0], -1.0).unwrap_err().code(), "INVALID_TOTAL");
    assert_eq!(positive_mass_projection(&[-1.0], 0.0).unwrap_err().code(), "NEGATIVE_PRIOR");
    assert_eq!(signed_transfer_lift(f64::NAN, &[0.0]).unwrap_err().code(), "INVALID_CONDITIONAL_MASS_PRIOR");
    assert_eq!(signed_transfer_lift(f64::INFINITY, &[1.0]).unwrap_err().code(), "NONFINITE_RATE");
    assert!(positive_mass_projection(&[f64::INFINITY], 0.0).is_err());
}
#[test]
fn overflow_is_not_silently_renormalized() {
    assert_eq!(positive_mass_projection(&[1e308, 1e308], 1.0).unwrap(), vec![0.0, 0.0]);
    assert_eq!(signed_transfer_lift(-4.0, &[1e308, 1e308]).unwrap().signed, vec![0.0, 0.0]);
}
#[test]
fn pchip_knots_interior_and_domain() {
    let t = table();
    for (x, y) in [(-2.0, -3.0), (0.0, -2.5), (2.0, -2.0), (0.5, -2.375)] {
        assert_eq!(pchip_eval(&t, x).unwrap(), y);
    }
    assert!(matches!(pchip_eval(&t, 2.0 + f64::EPSILON * 2.0), Err(ForwardError::OutsideTableDomain { .. })));
    assert!(pchip_eval(&t, -2.0 - f64::EPSILON * 2.0).is_err());
    assert!(pchip_eval(&t, f64::NAN).is_err());
    assert!(PchipTable::new(vec![0.0, 0.0], [vec![0.0], vec![0.0], vec![0.0], vec![0.0]]).is_err());
}
#[test]
fn pchip_uses_right_interval_at_interior_knot() {
    let t = PchipTable::new(vec![-2.0, 0.0, 2.0], [vec![0.0; 2], vec![0.0; 2], vec![0.0; 2], vec![17.0, 29.0]]).unwrap();
    assert_eq!(pchip_eval(&t, 0.0).unwrap(), 29.0);
}
#[test]
fn transform_is_max_shifted_without_floors() {
    let mut z = [0.0; 9]; z[5] = 1000.0; z[6] = 999.0;
    let s = transform_z_to_y(&z);
    assert_eq!(s.n_comoving_per_cmpc3, [1.0; 4]);
    assert_eq!(s.x_hii, 0.5);
    close(s.helium.iter().sum(), 1.0);
    z[5] = f64::NAN;
    assert!(transform_z_to_y(&z).helium.iter().all(|x| x.is_nan()));
}
#[test]
fn opacity_ownership_and_proper_units() {
    let s = state(); let mut p = params();
    let a = opacity_cMpc_inv(&s, &p).unwrap();
    p.sigma_hi_cm2[0] *= 1e6; p.sigma_hi_cm2[1] *= 1e6;
    let b = opacity_cMpc_inv(&s, &p).unwrap(); assert_eq!(a, b);
    p.sigma_hei_cm2[1] *= 2.0;
    let c = opacity_cMpc_inv(&s, &p).unwrap();
    close(c[1] - b[1], p.n_he_proper_per_cm3 * s.helium[0] * 7e-18 * MPC_CM / 4.0);
    let alpha_si = (p.n_h_proper_per_cm3 * 1e6) * (1.0 - s.x_hii) * (p.sigma_hi_cm2[2] / 1e4);
    let he_si = (p.n_he_proper_per_cm3 * 1e6) * s.helium[0] * (p.sigma_hei_cm2[2] / 1e4);
    close(a[2], (alpha_si + he_si) * (MPC_CM / 100.0) / 4.0);
}
#[test]
fn gamma_has_one_comoving_factor_and_no_table_dependency() {
    let mut s = state(); let mut p = params();
    let a = gamma_species(&s, &p);
    p.redshift = 0.0; let b = gamma_species(&s, &p); close(a.hi_per_s / b.hi_per_s, 64.0);
    s.gamma_hi_per_s = 1e-200;
    assert_eq!(gamma_species(&s, &p).hi_per_s, b.hi_per_s);
    let si = (C_LIGHT / 100.0) / (MPC_CM / 100.0).powi(3)
        * p.sigma_hi_cm2.iter().zip(s.n_comoving_per_cmpc3).map(|(sig, n)| sig / 1e4 * n).sum::<f64>();
    close(b.hi_per_s, si);
}
#[test]
fn isolated_groups_and_no_emissivity() {
    let mut s = state(); let p = params();
    for g in 0..4 {
        s.n_comoving_per_cmpc3 = [0.0; 4]; s.n_comoving_per_cmpc3[g] = 1.0;
        let rhs = photon_rates(&s, &[0.0; 4], &p).unwrap();
        for i in 0..4 {
            if i == g { assert!(rhs[i] < 0.0); }
            else if i + 1 == g { close(rhs[i], p.hubble_per_s * p.redshift_coeff[g]); }
            else { assert_eq!(rhs[i], 0.0); }
        }
    }
    s.n_comoving_per_cmpc3 = [0.0; 4];
    assert_eq!(photon_rates(&s, &[10.0; 4], &p).unwrap(), [4.0, 3.0, 2.0, 1.0]);
}
#[test]
fn redshift_internal_transfer_telescopes() {
    let s = state(); let mut p = params(); p.hubble_per_s = 0.1;
    let rhs = photon_rates(&s, &[0.0; 4], &p).unwrap();
    let k = opacity_cMpc_inv(&s, &p).unwrap();
    let total: f64 = (0..4).map(|g| rhs[g] + C_LIGHT * 4.0 / MPC_CM * k[g] * s.n_comoving_per_cmpc3[g]).sum();
    close(total, -0.1);
}
#[test]
fn four_site_calls_do_not_share_state() {
    let p = params(); let mut sites = Vec::new();
    for i in 0..4 { let mut s = state(); s.x_hii = 0.1 + 0.2 * i as f64; sites.push(s); }
    let first: Vec<_> = sites.iter().map(|s| opacity_cMpc_inv(s, &p).unwrap()).collect();
    for i in (0..4).rev() { assert_eq!(opacity_cMpc_inv(&sites[i], &p).unwrap(), first[i]); }
    assert_ne!(first[0][2], first[3][2]);
}
#[test]
fn registry_does_not_admit_missing_physical_sources() {
    assert_eq!(coverage::PORTED_FUNCTIONS.len(), 7);
    for key in ["P0_C8", "C9_CP0", "HOST4_H19", "HH_R10"] {
        assert!(matches!(coverage::require_physical_source(key), Err(ForwardError::MissingAuthority(_))));
    }
}
