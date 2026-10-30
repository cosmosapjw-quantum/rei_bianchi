//! Read-only native AXBI source export for a time-dependent short-interval pilot.
//! Inputs: cells per threshold segment, n_mu and source-locked nH0 in cm^-3.
//! No production run, no modifications to AxbiSource or original channels.
use rei_microphysics::axbi_sources::{AxbiSource, SOURCE_ID};
use std::env;
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let a: Vec<String> = env::args().skip(1).collect();
    if a.len() != 3 {
        return Err("usage: SEGMENT_CELLS N_MU NH0_CM3".into());
    }
    let n = a[0].parse::<usize>()?;
    let m = a[1].parse::<usize>()?;
    let nh0 = a[2].parse::<f64>()?;
    if !nh0.is_finite() || nh0 <= 0. || !matches!(m, 8 | 16 | 32) || !(1..=1024).contains(&n) {
        return Err("BAD_SOURCE_INPUT".into());
    }
    let src = AxbiSource::new(nh0, 0.2, n, m)?;
    println!(
        "META,{SOURCE_ID},{nh0:.17e},2.00000000000000011e-1,{n},{m},{:.17e},{:.17e}",
        src.normalization_relative_residual, src.omitted_blackbody_tail_photon_fraction
    );
    for (i, x) in src.spectral_cells.iter().enumerate() {
        println!(
            "SPECTRUM,{i},{:.17e},{:.17e},{:.17e},{:.17e}",
            x.lower_ev, x.upper_ev, x.energy_ev, x.photon_fraction
        );
    }
    for (i, x) in src.angular_cells.iter().enumerate() {
        println!("ANGLE,{i},{:.17e},{:.17e}", x.mu, x.count_fraction);
    }
    for z in (4..=20).map(|k| k as f64) {
        let r = src.at_redshift(z)?;
        println!(
            "RATE,{z:.17e},{:.17e},{:.17e},{:.17e}",
            r.per_h_s, r.proper_photons_cm3_s, r.comoving_photons_per_s_cmpc3
        );
    }
    Ok(())
}
