//! Extract exact unmodified Grackle-derived IGM coefficients from rei_microphysics.
//! This is a read-only diagnostic consumer, not a replacement provider.
//! TSV/CSV columns in cgs units, one row per requested T in Kelvin.
//! Usage: cargo run --release --example source07_c11_rates -- --loggrid 10000 24000 129
//!        cargo run --release --example source07_c11_rates -- --points 12000 15000 19000
use rei_microphysics::igm_rates::igm_rates;
use std::env;

fn row(t: f64) -> Result<(), Box<dyn std::error::Error>> {
    let r = igm_rates(t)?;
    // Consistency with the original rate owner: rr HII/HeII/HeIII; dr HeII;
    // RR/DR cooling erg cm^3 s^-1. Outputs preserve scientific native values.
    let v = [
        r.rr_cm3_s[0],
        r.rr_cm3_s[1],
        r.rr_cm3_s[2],
        r.dr_cm3_s,
        r.rr_cooling_erg_cm3_s[0],
        r.rr_cooling_erg_cm3_s[1],
        r.rr_cooling_erg_cm3_s[2],
        r.dr_cooling_erg_cm3_s,
    ];
    if v.iter().any(|x| !x.is_finite() || *x < 0.) {
        return Err("INVALID_PROVIDER_COEFFICIENT".into());
    }
    print!("{t:.17e}");
    for x in v {
        print!(",{x:.17e}");
    }
    println!();
    Ok(())
}
fn real(x: &str) -> Result<f64, Box<dyn std::error::Error>> {
    let v = x.parse::<f64>()?;
    if !v.is_finite() || v <= 0. {
        return Err("NONPOSITIVE_T".into());
    }
    Ok(v)
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let a: Vec<String> = env::args().skip(1).collect();
    println!("T_K,rr_HII_cm3_s,rr_HeII_cm3_s,rr_HeIII_cm3_s,dr_HeII_cm3_s,rr_cool_HII_erg_cm3_s,rr_cool_HeII_erg_cm3_s,rr_cool_HeIII_erg_cm3_s,dr_cool_HeII_erg_cm3_s");
    match a.first().map(String::as_str) {
        Some("--loggrid") if a.len() == 4 => {
            let low = real(&a[1])?;
            let high = real(&a[2])?;
            let n = a[3].parse::<usize>()?;
            if !(high > low && n >= 2 && n <= 4096) {
                return Err("INVALID_GRID".into());
            }
            for i in 0..n {
                row((low.ln() + (high / low).ln() * i as f64 / (n - 1) as f64).exp())?
            }
        }
        Some("--points") if a.len() > 1 => {
            for s in a.iter().skip(1) {
                row(real(s)?)?
            }
        }
        _ => return Err("Usage: --loggrid LOW HIGH N | --points T1 T2 ...".into()),
    }
    Ok(())
}
