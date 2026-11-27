//! Persistent HE25 point bridge to the pinned original rei_microphysics rlib.
//! One request performs exactly one igm_point_rhs evaluation; h=0 by contract.
use rei_microphysics::{
    axbi_driver::{Driver, DriverConfig},
    igm_state::{IgmGasState, w_ev_per_h_to_erg},
    igm_thermal::{igm_point_rhs, IgmPhotoInput},
};
use std::io::{self, BufRead, Write};
const SOURCE: &str = "f7830e2f55e7a1938bc3c98f61b60651f8dae474";
const EV_ERG: f64 = 1.602176634e-12;

fn evaluate(line: &str, driver: &Driver) -> Result<String, Box<dyn std::error::Error>> {
    let words: Vec<&str> = line.split_whitespace().collect();
    if words.len() != 11 { return Err("HE25_REQUEST_ARITY".into()); }
    let mut v = [0.0f64; 11];
    for (i, word) in words.iter().enumerate() {
        v[i] = word.parse()?;
        if !v[i].is_finite() { return Err("HE25_NONFINITE_INPUT".into()); }
    }
    let a = v[0];
    if !(1.0 / 21.0..=1.0 / 5.0).contains(&a) { return Err("HE25_SCALE_DOMAIN".into()); }
    let gas = IgmGasState::new([v[1], v[2], v[3]], w_ev_per_h_to_erg(v[4])?)?;
    let mut photo = IgmPhotoInput::default();
    for i in 0..3 {
        if v[5+i] < 0.0 || v[8+i] < 0.0 { return Err("HE25_NEGATIVE_PHOTO_INPUT".into()); }
        photo.gamma_s[i] = v[5+i];
        photo.heat_erg_per_absorber_s[i] = v[8+i];
    }
    let nh = driver.n_h0_cm3 / a.powi(3);
    let nhe = driver.n_he0_cm3 / a.powi(3);
    let eos = gas.eos(nh, nhe)?;
    let rhs = igm_point_rhs(&gas, nh, nhe, 0.0, 2.7255/a, photo)?;
    let mut out = vec!["POINT".to_owned()];
    let values = [
        nh, nhe, rhs.fraction_dt[0], rhs.fraction_dt[1], rhs.fraction_dt[2],
        rhs.w_dt_erg_per_h_s/EV_ERG, eos.temperature_k,
        rhs.photo_events_cm3_s[0], rhs.photo_events_cm3_s[1], rhs.photo_events_cm3_s[2],
        rhs.thermal_micro_erg_cm3_s, rhs.binding_micro_erg_cm3_s,
        rhs.escape_erg_cm3_s, rhs.cmb_to_gas_erg_cm3_s, rhs.photo_input_erg_cm3_s,
        rhs.ci_events_cm3_s[0], rhs.ci_events_cm3_s[1], rhs.ci_events_cm3_s[2],
        rhs.rr_events_cm3_s[0], rhs.rr_events_cm3_s[1], rhs.rr_events_cm3_s[2],
        rhs.dr_events_cm3_s,
    ];
    out.extend(values.iter().map(|x| format!("{x:.17e}")));
    Ok(out.join("\t"))
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let (driver, _) = Driver::new(DriverConfig::baseline())?;
    let stdout = io::stdout();
    let mut output = stdout.lock();
    writeln!(output, "HE25_OWNER_V1\t{SOURCE}\t{:.17e}\t{:.17e}", driver.n_h0_cm3, driver.n_he0_cm3)?;
    output.flush()?;
    for line in io::stdin().lock().lines() {
        let response = match evaluate(&line?, &driver) {
            Ok(s) => s,
            Err(e) => format!("ERROR\t{e}"),
        };
        writeln!(output, "{response}")?;
        output.flush()?;
    }
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("HE25_OWNER_FATAL: {e}");
        std::process::exit(2);
    }
}
