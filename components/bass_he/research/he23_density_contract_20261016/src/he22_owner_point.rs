//! HE22 independent native H/He RHS adapter for source-age photon solver.
//! Compile against exactly selected original rei_microphysics source commit.
//! This file does NOT implement new atomic rates or change production code.
//!
//! CLI: he22_owner_point a xHII xHeII xHeIII W_eV/H \
//!       GammaHI GammaHeI GammaHeII HeatHI HeatHeI HeatHeII
//! Output: newline-delimited tab-separated tagged fields HE22_NATIVE_POINT_V1.
//! h=0 on every call because HE21/HE22 owns the external adiabatic half maps.
use rei_microphysics::{
    axbi_driver::{Driver, DriverConfig},
    igm_state::{IgmGasState, w_ev_per_h_to_erg},
    igm_thermal::{igm_point_rhs, IgmPhotoInput},
};
use std::env;

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    if args.len() == 3 && args[1] == "--density" {
        let a: f64 = args[2].parse()?;
        if !a.is_finite() || !(1.0/21.0..=1.0/5.0).contains(&a) {
            return Err("HE23_DENSITY_SCALE_DOMAIN".into());
        }
        let (d, _) = Driver::new(DriverConfig::baseline())?;
        println!("HE23_TOTAL_NUCLEI_V1");
        println!("SOURCE_COMMIT\tf7830e2f55e7a1938bc3c98f61b60651f8dae474");
        println!("A\t{a:.17e}");
        println!("NH_CM3\t{:.17e}", d.n_h0_cm3/a.powi(3));
        println!("NHE_CM3\t{:.17e}", d.n_he0_cm3/a.powi(3));
        return Ok(());
    }
    if args.len() != 12 {
        return Err("usage: he22_owner_point a xHII xHeII xHeIII W_eV_H gammaHI gammaHeI gammaHeII heatHI heatHeI heatHeII".into());
    }
    let read = |i: usize| -> Result<f64, Box<dyn std::error::Error>> {
        let v = args[i].parse::<f64>()?;
        if !v.is_finite() {
            return Err("HE22_NONFINITE_NATIVE_INPUT".into());
        }
        Ok(v)
    };
    let a = read(1)?;
    // Explicit original AXBI calibrated support; never extrapolate silently.
    if !(1.0 / 21.0..=1.0 / 5.0).contains(&a) {
        return Err("HE22_SOURCE_SCALE_FACTOR_OUTSIDE_AXBI_DOMAIN".into());
    }
    let state = IgmGasState::new([read(2)?, read(3)?, read(4)?],
                                 w_ev_per_h_to_erg(read(5)?)?)?;
    let mut photo = IgmPhotoInput::default();
    for i in 0..3 {
        photo.gamma_s[i] = read(6+i)?;
        photo.heat_erg_per_absorber_s[i] = read(9+i)?;
        if photo.gamma_s[i] < 0. || photo.heat_erg_per_absorber_s[i] < 0. {
            return Err("HE22_NEGATIVE_PHOTO_RATE".into());
        }
    }
    let (driver, _) = Driver::new(DriverConfig::baseline())?;
    let nh = driver.n_h0_cm3 / a.powi(3);
    let nhe = driver.n_he0_cm3 / a.powi(3);
    let eos = state.eos(nh, nhe)?;
    let rhs = igm_point_rhs(&state, nh, nhe, 0.0, 2.7255/a, photo)?;
    const EV_ERG: f64 = 1.602176634e-12;
    println!("HE22_NATIVE_POINT_V1");
    println!("NH_CM3\t{nh:.17e}");
    println!("NHE_CM3\t{nhe:.17e}");
    println!("FRACTION_DT\t{:.17e}\t{:.17e}\t{:.17e}",
             rhs.fraction_dt[0], rhs.fraction_dt[1], rhs.fraction_dt[2]);
    println!("W_DT_EV_PER_H_S\t{:.17e}", rhs.w_dt_erg_per_h_s/EV_ERG);
    println!("TEMP_K\t{:.17e}", eos.temperature_k);
    println!("PHOTO_EVENTS\t{:.17e}\t{:.17e}\t{:.17e}",
             rhs.photo_events_cm3_s[0], rhs.photo_events_cm3_s[1], rhs.photo_events_cm3_s[2]);
    println!("THERMAL_MICRO\t{:.17e}",rhs.thermal_micro_erg_cm3_s);
    println!("BINDING_MICRO\t{:.17e}",rhs.binding_micro_erg_cm3_s);
    println!("ESCAPE\t{:.17e}",rhs.escape_erg_cm3_s);
    println!("CMB_TO_GAS\t{:.17e}",rhs.cmb_to_gas_erg_cm3_s);
    println!("PHOTO_INPUT\t{:.17e}",rhs.photo_input_erg_cm3_s);
    println!("CI_EVENTS\t{:.17e}\t{:.17e}\t{:.17e}",
             rhs.ci_events_cm3_s[0], rhs.ci_events_cm3_s[1], rhs.ci_events_cm3_s[2]);
    println!("RR_EVENTS\t{:.17e}\t{:.17e}\t{:.17e}",
             rhs.rr_events_cm3_s[0], rhs.rr_events_cm3_s[1], rhs.rr_events_cm3_s[2]);
    println!("DR_EVENTS\t{:.17e}",rhs.dr_events_cm3_s);
    Ok(())
}
fn main() {
    if let Err(err) = run() {
        eprintln!("HE22_NATIVE_POINT_ERROR: {err}");
        std::process::exit(2);
    }
}
