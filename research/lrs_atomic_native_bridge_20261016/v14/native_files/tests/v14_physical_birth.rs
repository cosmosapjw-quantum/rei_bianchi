//! Native tests are executable specifications; execution status is in stage receipts.
use rei_microphysics::{
    axbi_covariant_transport::PhotonAttenuation,
    axbi_driver::{Driver, DriverConfig, DriverState, NativeClockMode,
        SourceClockConfig, SourcePlacement, PhysicalBirthRule},
    igm_state::IgmGasState,
};
fn initial() -> (Driver, DriverState) {
    let mut c=DriverConfig::baseline();
    c.transport_cells=8;c.background_panels=128;c.transport_threads=1;
    let (mut d,mut s)=Driver::new(c).unwrap();
    s.gas=IgmGasState::from_temperature([0.075,0.12,0.03],d.n_h0_cm3/s.a.powi(3),d.n_he0_cm3/s.a.powi(3),15000.).unwrap();
    d.set_source_clocks(&s,SourceClockConfig{microphysics:NativeClockMode::AllMid,
        opacity_midpoint:true,attenuation:PhotonAttenuation::Exponential,
        source:SourcePlacement::Disabled,nonlinear_tolerance:1e-13}).unwrap();
    (d,s)
}
#[test]
fn gauss2_positive_nodes_have_exact_first_four_moments() {
    let nodes=PhysicalBirthRule::Gauss2.nodes();
    assert_eq!(nodes.len(),2);
    for &(c,w) in &nodes {assert!(c>0. && c<1. && w>0.);}
    for k in 0..4 {
        let moment:f64=nodes.iter().map(|&(c,w)|w*c.powi(k)).sum();
        assert!((moment-1./(k+1) as f64).abs()<3e-15);
    }
}
#[test]
fn source_number_is_original_md14_at_each_actual_birth_geometry() {
    let (d,mut s)=initial(); let a0=s.a;let h:f64=1e-5/8.;
    let expected:f64=PhysicalBirthRule::Gauss2.nodes().iter().map(|&(c,w)| {
        let a=a0*(c*h).exp();
        let hubble=d.geometry_point(a).unwrap().h_flrw_per_s;
        d.source.at_redshift(1./a-1.).unwrap().per_h_s*h*w/hubble
    }).sum();
    let report=d.fixed_step_physical_birth(&mut s,h,PhysicalBirthRule::Gauss2).unwrap();
    assert_eq!(report.births.len(),2); assert_eq!(report.segments.len(),3);
    assert!(report.births[0].a < report.births[1].a);
    assert!((s.ledgers.source_n-expected).abs()<1e-12*expected.abs().max(1e-30));
    assert!((s.a-a0*h.exp()).abs()<1e-16);
    assert_eq!(s.accepted,1);assert_eq!(s.attempts,1);
}
#[test]
fn every_microsegment_rhs_is_integrated_with_its_own_clock() {
    let (d,mut s)=initial();let before=s.clone();
    let report=d.fixed_step_physical_birth(&mut s,1e-5/8.,PhysicalBirthRule::Gauss2).unwrap();
    for j in 0..3 {
        let v:f64=report.segments.iter().map(|s|s.photo_events_per_h[j]).sum();
        assert!((v-(s.ledgers.photo_events[j]-before.ledgers.photo_events[j])).abs()<2e-16);
    }
    let cmb:f64=report.segments.iter().map(|s|s.cmb_input_ev_per_h).sum();
    let escape:f64=report.segments.iter().map(|s|s.escaped_ev_per_h).sum();
    assert!((cmb-(s.ledgers.cmb_input-before.ledgers.cmb_input)).abs()<1e-15);
    assert!((escape-(s.ledgers.escaped_u-before.ledgers.escaped_u)).abs()<1e-14);
    assert!(report.segments.iter().all(|s|s.dt_s>0. && s.n_h_cm3>0.));
}
#[test]
fn physical_midpoint_and_gauss2_are_conservative_positive_experiments() {
    for rule in [PhysicalBirthRule::Midpoint,PhysicalBirthRule::Gauss2] {
        let (d,mut s)=initial();
        for _ in 0..8 {d.fixed_step_physical_birth(&mut s,1e-5/8.,rule).unwrap();}
        d.validate(&s,1e-8).unwrap();
        let (n,e)=d.residuals(&s).unwrap();
        assert!(n.abs()<1e-16 && e.abs()<1e-9);
        assert!(s.ledgers.source_n>0. && s.ledgers.absorbed_n>0.);
        assert!(s.photons.iter().all(|&n|n>=0.));
        assert!(s.gas.fractions.iter().all(|&x|(0.0..=1.0).contains(&x)));
    }
}
#[test]
fn disabled_gl2_is_exact_same_three_native_source_off_substeps() {
    let (d,mut a)=initial();let (other,mut b)=initial();let a0=a.a;let h:f64=1e-5/8.;
    let r=d.fixed_step_physical_birth(&mut a,h,PhysicalBirthRule::DisabledGauss2).unwrap();
    let mut right:Vec<f64>=PhysicalBirthRule::Gauss2.nodes().iter().map(|&(c,_)|a0*(c*h).exp()).collect();
    right.push(a0*h.exp());
    for to in right {let step=(to/b.a).ln();other.fixed_step(&mut b,step).unwrap();}
    for j in 0..3 {assert!((a.gas.fractions[j]-b.gas.fractions[j]).abs()<3e-14);}
    assert!((a.gas.w_erg_per_h-b.gas.w_erg_per_h).abs()<1e-24);
    assert!(r.births.iter().all(|s|s.added_photons_per_h==0.));
    assert_eq!(a.ledgers.source_n,0.);
}
#[test]
fn failure_rolls_back_physical_state_and_rhs_but_charges_work() {
    let (mut d,mut s)=initial();d.config.max_rhs=1;
    let before=s.clone();assert!(d.last_clock_rhs().unwrap().is_none());
    assert!(d.fixed_step_physical_birth(&mut s,1e-5,PhysicalBirthRule::Gauss2).is_err());
    assert_eq!(s.photons,before.photons);assert_eq!(s.photon_energy_ref,before.photon_energy_ref);
    assert_eq!(s.gas.fractions,before.gas.fractions);assert_eq!(s.gas.w_erg_per_h,before.gas.w_erg_per_h);
    assert_eq!(s.ledgers.source_n,before.ledgers.source_n);assert_eq!(s.a,before.a);
    assert_eq!(s.accepted,0);assert_eq!(s.attempts,1);assert!(s.rhs_evaluations>0);
    assert!(d.last_clock_rhs().unwrap().is_none());
}
#[test]
fn physical_birth_api_requires_explicit_disabled_native_source() {
    let (d,mut s)=Driver::new(DriverConfig::baseline()).unwrap();
    assert!(d.fixed_step_physical_birth(&mut s,1e-5,PhysicalBirthRule::Gauss2).is_err());
    let (d,mut s)=initial();
    for h in [0.,-1e-5,f64::NAN,0.01] {
        assert!(d.fixed_step_physical_birth(&mut s,h,PhysicalBirthRule::Gauss2).is_err());
    }
}
