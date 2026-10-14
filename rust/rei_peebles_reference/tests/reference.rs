use rei_peebles_reference::*;

fn close(a: f64, b: f64, rel: f64, abs: f64) {
    assert!((a-b).abs() <= abs + rel*a.abs().max(b.abs()), "{a:.17e} != {b:.17e}");
}

#[test]
fn source_rounded_profile_reaches_real_consumer() {
    let input = ReferenceInput::from_si(3000.0, 3000.0, 250e6, 5e-14, 0.1, 0.0).unwrap();
    let point = evaluate_reference(input).unwrap();
    assert!((point.collapsed.dxp_dt + 3.5862885954445544e-14).abs() < 1e-27);
    close(point.collapsed.source.c_factor, 0.021501337234858833, 2e-14, 0.0);
    close(point.collapsed.source.beta_p_s, 515.5775345899355, 2e-14, 0.0);
    close(point.collapsed.source.alpha_b_m3_s, 6.685412343969989e-19, 2e-14, 0.0);
}

#[test]
fn cgs_boundary_applies_density_conversion_once() {
    let si = ReferenceInput::from_si(3000.0, 3000.0, 250e6, 5e-14, 0.1, 0.3).unwrap();
    let cgs = ReferenceInput::from_cgs(3000.0, 3000.0, 250.0, 5e-14, 0.1, 0.3).unwrap();
    assert_eq!(cgs.n_h_m3(), 250e6);
    assert_eq!(evaluate_reference(si).unwrap().collapsed.dxp_dt,
               evaluate_reference(cgs).unwrap().collapsed.dxp_dt);
}

#[test]
fn actual_ground_and_collapsed_assembly_are_separate() {
    let p = evaluate_reference(ReferenceInput::from_si(3000.0,3000.0,250e6,5e-14,0.1,0.3).unwrap()).unwrap();
    assert_eq!(p.retained.source.x1,(1.0-0.1)-0.3);
    assert_eq!(p.collapsed.source.x1,1.0-0.1);
    close(p.retained.source.r_alpha_s/p.collapsed.source.r_alpha_s,1.5,2e-15,0.0);
    assert!(p.retained.source.c_factor > p.collapsed.source.c_factor);
    assert_ne!(p.source_assembly_contribution,0.0);
}

#[test]
fn shell_defect_and_source_assembly_contributions_close_separately() {
    let p = evaluate_reference(ReferenceInput::from_si(8000.0,8000.0,2e8,8e-14,0.3,0.1).unwrap()).unwrap();
    let d = p.retained.same_rates_closure_defect;
    close(d.direct,d.reconstructed,2e-14,1e-15);
    assert!(d.ground_depletion < 0.0);
    close(p.retained_minus_standard_collapsed,d.direct+p.source_assembly_contribution,2e-14,1e-15);
    close(p.retained.rhs.dxp_dt+p.retained.rhs.dx2_dt+p.retained.rhs.dx1_dt,0.0,0.0,1e-10);
}

#[test]
fn collapsed_evaluation_ignores_valid_retained_shell() {
    let a = ReferenceInput::from_si(3000.0,3000.0,250e6,5e-14,0.1,0.0).unwrap();
    let b = ReferenceInput::from_si(3000.0,3000.0,250e6,5e-14,0.1,0.3).unwrap();
    assert_eq!(evaluate_collapsed(a).unwrap().dxp_dt,evaluate_collapsed(b).unwrap().dxp_dt);
}

#[test]
fn collapsed_redshift_sign_has_no_fraction_dilution_sink() {
    let input = ReferenceInput::from_si(3000.0,3000.0,250e6,5e-14,0.1,0.0).unwrap();
    let dt = evaluate_collapsed(input).unwrap().dxp_dt;
    close(collapsed_redshift_rhs(input,1100.0).unwrap(),-dt/(1101.0*5e-14),2e-15,0.0);
    assert!(collapsed_redshift_rhs(input,1100.0).unwrap()>0.0);
    assert_eq!(collapsed_redshift_rhs(input,-1.0).unwrap_err(),HydrogenError::Domain);
}

#[test]
fn one_temperature_positive_expansion_and_ground_are_required() {
    assert_eq!(ReferenceInput::from_si(2999.0,3000.0,1e8,1e-14,0.5,0.0).unwrap_err(),HydrogenError::UnequalTemperatures);
    assert_eq!(ReferenceInput::from_si(3000.0,3000.0,1e8,0.0,0.5,0.0).unwrap_err(),HydrogenError::Domain);
    assert_eq!(ReferenceInput::from_si(3000.0,3000.0,1e8,1e-14,1.0,0.0).unwrap_err(),HydrogenError::ZeroGroundSobolev);
    assert_eq!(ReferenceInput::from_si(3000.0,3000.0,1e8,1e-14,0.9,0.2).unwrap_err(),HydrogenError::Domain);
}

#[test]
fn invalid_and_overflowing_units_are_errors_without_mutating_valid_input() {
    let input = ReferenceInput::from_si(3000.0,3000.0,250e6,5e-14,0.1,0.0).unwrap();
    let before = evaluate_collapsed(input).unwrap().dxp_dt;
    assert_eq!(ProperHydrogenDensity::from_cm3(f64::MAX).unwrap_err(),HydrogenError::Overflow);
    for bad in [f64::NAN,f64::INFINITY,f64::NEG_INFINITY,-1.0,0.0] {
        assert!(ProperHydrogenDensity::from_m3(bad).is_err());
        assert!(OneTemperature::new(bad,bad).is_err());
        assert!(ExpansionRate::per_second(bad).is_err());
    }
    assert_eq!(evaluate_collapsed(input).unwrap().dxp_dt,before);
}

#[test]
fn shell_weights_and_escape_weight_are_visible_at_consumer() {
    let p = evaluate_reference(ReferenceInput::from_si(3000.0,3000.0,250e6,5e-14,0.1,0.0).unwrap()).unwrap();
    close(p.collapsed.source.beta_p_s,4.0*p.collapsed.source.beta_shell_s,2e-15,0.0);
    close(4.0*p.collapsed.source.d_ground_s,8.2206+3.0*p.collapsed.source.r_alpha_s,2e-15,0.0);
    let c_wrong = p.collapsed.source.d_ground_s/(p.collapsed.source.d_ground_s+p.collapsed.source.beta_p_s);
    assert!((p.collapsed.source.c_factor-c_wrong).abs()>0.01);
}

#[test]
fn pure_h_electron_fraction_and_conservation_are_explicit() {
    let i = ReferenceInput::from_si(3000.0,3000.0,250e6,5e-14,0.2,0.01).unwrap();
    let p = evaluate_retained(i).unwrap();
    let rhs_scale = p.rhs.continuum_flux.abs()+p.rhs.ground_flux.abs();
    assert!((p.rhs.dxp_dt+p.rhs.dx2_dt+p.rhs.dx1_dt).abs()<=2e-15*rhs_scale);
    close(p.rhs.dxp_dt,-p.rhs.continuum_flux,0.0,0.0);
    assert_eq!(i.state().xp,0.2); // Pure H xe=xp; x2 is neutral bound H.
}
