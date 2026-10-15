//! Real native cold H/He/MD14-BB50K origin tests for a frozen HyRec donor.
//! The donor is a conditional candidate; no old q-signed snapshots are reused.
use rei_microphysics::axbi_driver::{compiled_identity, Driver, DriverConfig};
use rei_microphysics::axbi_rates::{AxbiProvider, AXBI_PROVIDER_ID};
use rei_microphysics::igm_state::IgmGasState;
use rei_microphysics::igm_thermal::IgmPhotoInput;

const DONOR_XHII: f64 = 0.000210349192936;
const DONOR_T: f64 = 9.306042400380866;

fn short_config(x: f64, temp: f64, q: f64) -> DriverConfig {
    let mut cfg = DriverConfig::baseline();
    cfg.initial_hii_fraction = x;
    cfg.initial_temperature_k = temp;
    cfg.q_ref = q;
    cfg.end_zbar = 19.985;
    cfg.background_panels = 64;
    cfg.max_steps = 250;
    cfg.max_attempts = 500;
    cfg.max_rhs = 50000;
    cfg.max_wall_s = 40.0;
    cfg.local_target = 1e-5;
    cfg
}

#[test]
fn unchanged_baseline_and_source_derived_donor_both_start_fresh() {
    let baseline = DriverConfig::baseline();
    assert_eq!(baseline.initial_hii_fraction, 2.0e-4);
    let (db, sb) = Driver::new(short_config(
        baseline.initial_hii_fraction,
        baseline.initial_temperature_k, 0.0,
    )).unwrap();
    let (dd, sd) = Driver::new(short_config(DONOR_XHII, DONOR_T, 0.0)).unwrap();
    assert_eq!(sb.gas.fractions, [2.0e-4,0.0,0.0]);
    assert_eq!(sd.gas.fractions, [DONOR_XHII,0.0,0.0]);
    assert!(sb.photons.iter().all(|&v| v==0.0));
    assert!(sd.photons.iter().all(|&v| v==0.0));
    assert_eq!(sb.ledgers.source_n, 0.0);
    assert_eq!(sd.ledgers.source_u, 0.0);
    assert_eq!(db.residuals(&sb).unwrap(), (0.0,0.0));
    assert_eq!(dd.residuals(&sd).unwrap(), (0.0,0.0));
    let nh = dd.n_h0_cm3 / sd.a.powi(3);
    let nhe = dd.n_he0_cm3 / sd.a.powi(3);
    let eb = sb.gas.eos(nh,nhe).unwrap();
    let ed = sd.gas.eos(nh,nhe).unwrap();
    assert!((ed.temperature_k/DONOR_T-1.0).abs()<1e-14);
    assert!((ed.electron_density_cm3/eb.electron_density_cm3
        -DONOR_XHII/2.0e-4).abs()<1e-13);
    assert!((ed.temperature_k/eb.temperature_k-1.0)>0.1);
    // The donor is a source-conditioned q=0 comparison, not a primordial
    // anisotropic recombination solution. The native signed background at
    // zbar20 remains a fresh REI construction.
    assert!(compiled_identity().contains("initial_hii_fraction"));
}

#[test]
fn configuration_change_or_unphysical_xhii_is_rejected_without_projection() {
    let conf = DriverConfig::baseline();
    let serialized = format!(
        "initial_hii_fraction={DONOR_XHII:.15}\ninitial_temperature_k={DONOR_T:.15}\nend_zbar=19.985\nbackground_panels=64\n"
    );
    let parsed = DriverConfig::read(&serialized).unwrap();
    assert_eq!(parsed.initial_hii_fraction,DONOR_XHII);
    assert!((parsed.initial_temperature_k-DONOR_T).abs()<1e-13);
    assert_eq!(parsed.q_ref,conf.q_ref);
    for bad in ["NaN","-0.1","1.1","inf"] {
        assert!(DriverConfig::read(&format!("initial_hii_fraction={bad}\n")).is_err());
    }
}

#[test]
fn initial_actual_rei_photo_free_chemistry_and_thermal_rhs_differ() {
    let (driver, baseline) = Driver::new(short_config(0.0002,
        DriverConfig::baseline().initial_temperature_k,0.0)).unwrap();
    let (_,donor) = Driver::new(short_config(DONOR_XHII,DONOR_T,0.0)).unwrap();
    let n_h=driver.n_h0_cm3/baseline.a.powi(3);
    let n_he=driver.n_he0_cm3/baseline.a.powi(3);
    let p=driver.background.point_at_scale(baseline.a).unwrap();
    let cmbrad=2.7255 *21.0;
    let b=AxbiProvider.point(&baseline.gas,n_h,n_he,p.h_per_s,
        cmbrad,IgmPhotoInput::default()).unwrap();
    let d=AxbiProvider.point(&donor.gas,n_h,n_he,p.h_per_s,
        cmbrad,IgmPhotoInput::default()).unwrap();
    assert_eq!(b.provider_id,AXBI_PROVIDER_ID);
    assert_eq!(d.provider_id,AXBI_PROVIDER_ID);
    assert_eq!(b.rhs.photo_events_cm3_s,[0.0;3]);
    assert_eq!(d.rhs.photo_events_cm3_s,[0.0;3]);
    assert!(d.rhs.fraction_dt[0].is_finite());
    assert!(b.rhs.fraction_dt[0].is_finite());
    assert!(d.rhs.temperature_dt_k_s.is_finite());
    assert!(b.rhs.temperature_dt_k_s.is_finite());
    assert_ne!(d.rhs.fraction_dt[0],b.rhs.fraction_dt[0]);
    assert_ne!(d.rhs.temperature_dt_k_s,b.rhs.temperature_dt_k_s);
}

#[test]
fn first_accepted_native_chemistry_photon_step_and_ledger() {
    for (q,x,temp) in [
        (0.0,0.0002,DriverConfig::baseline().initial_temperature_k),
        (0.0,DONOR_XHII,DONOR_T),
        (-0.01,DONOR_XHII,DONOR_T),
        (0.01,DONOR_XHII,DONOR_T),
    ] {
        let (d, mut s)=Driver::new(short_config(x,temp,q)).unwrap();
        let mut accepted=false;
        for _ in 0..30 {
            if d.adaptive_step(&mut s).unwrap() {
                accepted=true;
                break;
            }
        }
        assert!(accepted, "q={q} x={x} T={temp} step={} rejects={} error={} attempts={}",s.next_dln_a,s.rejects,s.last_error,s.attempts);
        assert_eq!(s.accepted,1);
        assert!(s.a>1.0/21.0);
        assert!(s.gas.fractions[0].is_finite());
        assert!(s.gas.eos(d.n_h0_cm3/s.a.powi(3),
                         d.n_he0_cm3/s.a.powi(3)).unwrap().temperature_k>1.0);
        d.validate(&s,1e-8).unwrap();
        let (count,energy)=d.residuals(&s).unwrap();
        assert!(count.abs()<1e-10);
        assert!(energy.abs()<1e-10);
    }
}

#[test]
fn fresh_initial_state_cannot_consume_different_initial_energy_checkpoint() {
    let (d0,s0)=Driver::new(short_config(0.0002,
        DriverConfig::baseline().initial_temperature_k,0.0)).unwrap();
    let (d1,_)=Driver::new(short_config(DONOR_XHII,DONOR_T,0.0)).unwrap();
    let path=std::env::temp_dir().join(format!("rei_rec_donor_ckpt_{}.txt",
            std::process::id()));
    d0.save_checkpoint(&path,&s0).unwrap();
    let err=d1.read_checkpoint(&path).unwrap_err();
    assert!(format!("{err:?}").contains("AXBI_CHECKPOINT_SHAPE_OR_INITIAL"));
    std::fs::remove_file(&path).unwrap();
}


#[test]
fn actual_photo_free_hydrogen_rhs_matches_source_analytic_reaction_owner() {
    for &(x,temp) in &[
        (2e-4,DriverConfig::baseline().initial_temperature_k),
        (DONOR_XHII,DONOR_T),
        (DONOR_XHII,DriverConfig::baseline().initial_temperature_k),
        (2e-4,DONOR_T),
    ] {
        let (d,s)=Driver::new(short_config(x,temp,0.0)).unwrap();
        let nh=d.n_h0_cm3/s.a.powi(3);
        let nhe=d.n_he0_cm3/s.a.powi(3);
        let h=d.background.point_at_scale(s.a).unwrap().h_per_s;
        let state=IgmGasState::from_temperature([x,0.0,0.0],nh,nhe,temp).unwrap();
        let point=AxbiProvider.point(&state,nh,nhe,h,2.7255/s.a,
                                     IgmPhotoInput::default()).unwrap();
        // Exact source formula at neutral helium and zero incoming ionizing
        // photons. The source's CI floor remains INCLUDED, not clipped.
        let ci=point.rates.ci_cm3_s[0];
        let rr=point.rates.rr_cm3_s[0];
        let native=nh*x*((1.0-x)*ci-x*rr);
        let expected=point.rhs.fraction_dt[0];
        assert!((native-expected).abs() <= 3e-15*expected.abs().max(1e-35));
        let r=&point.rhs;
        let energy=r.thermal_micro_erg_cm3_s+r.binding_micro_erg_cm3_s
                 +r.escape_erg_cm3_s-r.photo_input_erg_cm3_s-r.cmb_to_gas_erg_cm3_s;
        assert!(energy.abs()<=1e-14*r.escape_erg_cm3_s.max(
                 r.cmb_to_gas_erg_cm3_s.abs()).max(1e-90));
    }
}

#[test]
fn identical_q_signed_magnitude_has_equal_initial_scalar_atomic_rhs() {
    let mut values=Vec::new();
    for q in [-0.01,0.01] {
        let (d,s)=Driver::new(short_config(DONOR_XHII,DONOR_T,q)).unwrap();
        let nh=d.n_h0_cm3/s.a.powi(3);
        let nhe=d.n_he0_cm3/s.a.powi(3);
        let h=d.background.point_at_scale(s.a).unwrap().h_per_s;
        let r=AxbiProvider.point(&s.gas,nh,nhe,h,
                  2.7255/s.a,IgmPhotoInput::default()).unwrap();
        values.push((h,r.rhs.fraction_dt[0],r.rhs.temperature_dt_k_s));
    }
    assert_eq!(values[0],values[1]);
}
