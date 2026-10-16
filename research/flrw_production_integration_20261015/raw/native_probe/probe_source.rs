//! Finite q=0 integration probe; fresh output only, no history resume.
use rei_microphysics::axbi_driver::{compiled_identity, Driver, DriverConfig};
use std::{error::Error, fs, path::Path, time::Instant};

fn run_case(root: &Path, name: &str, donor: bool) -> Result<(), Box<dyn Error>> {
    let out = root.join(name);
    fs::create_dir(&out)?;
    let mut config = DriverConfig::baseline();
    config.end_zbar = 19.8;
    config.max_steps = 2;
    config.max_attempts = 120;
    config.max_rhs = 100000;
    config.max_wall_s = 120.0;
    if donor {
        // Explicit opt-in donor H residual and temperature; existing nH/fHe.
        config.initial_x_hii = 0.000210349192936;
        config.initial_temperature_k = 9.306042400380866;
    }
    fs::write(out.join("config.txt"), format!("{config:#?}\n"))?;
    let started = Instant::now();
    let (driver, mut state) = Driver::new(config)?;
    let initial = state.clone();
    let mut trials = String::from("comparison,accepted,a,next_dln_a,last_error,wall_s\n");
    let mut failure = None;
    for _ in 0..40 {
        if state.accepted == 2 {
            break;
        }
        if started.elapsed().as_secs_f64() >= driver.config.max_wall_s {
            failure = Some("probe wall cap".to_string());
            break;
        }
        match driver.adaptive_step(&mut state) {
            Ok(accepted) => trials.push_str(&format!(
                "{},{accepted},{},{},{},{}\n",
                state.comparisons,
                state.a,
                state.next_dln_a,
                state.last_error,
                started.elapsed().as_secs_f64()
            )),
            Err(error) => {
                failure = Some(format!("{error:?}"));
                break;
            }
        }
    }
    if state.accepted != 2 && failure.is_none() {
        failure = Some("probe comparison cap".to_string());
    }
    fs::write(out.join("trials.csv"), trials)?;
    driver.save_checkpoint(&out.join("checkpoint.txt"), &state)?;
    let restored = driver.read_checkpoint(&out.join("checkpoint.txt"))?;
    if restored.a != state.a
        || restored.gas.fractions != state.gas.fractions
        || restored.gas.w_erg_per_h != state.gas.w_erg_per_h
        || restored.photons != state.photons
    {
        return Err("probe checkpoint mismatch".into());
    }
    let (mut history, mut abundances, mut spectra, mut ledgers, mut feedback) =
        (Vec::new(), Vec::new(), Vec::new(), Vec::new(), Vec::new());
    for s in [&initial, &state] {
        driver.output_row(
            s,
            name,
            &mut history,
            &mut abundances,
            &mut spectra,
            &mut ledgers,
            &mut feedback,
        )?;
    }
    for (file, bytes) in [
        ("history_rows.csv", history),
        ("abundance_rows.csv", abundances),
        ("spectrum_rows.csv", spectra),
        ("ledger_rows.csv", ledgers),
        ("feedback_rows.csv", feedback),
    ] {
        fs::write(out.join(file), bytes)?;
    }
    driver.validate(&state, 1e-8)?;
    let eos = state.gas.eos(
        driver.n_h0_cm3 / state.a.powi(3),
        driver.n_he0_cm3 / state.a.powi(3),
    )?;
    let (number, energy) = driver.residuals(&state)?;
    let status = if failure.is_none() { "PASS" } else { "FAIL" };
    let error_json = failure
        .as_ref()
        .map(|s| format!("{s:?}"))
        .unwrap_or_else(|| "null".into());
    fs::write(
        out.join("summary.json"),
        format!(
            "{{\n  \"status\": \"{status}\",\n  \"error\": {error_json},\n  \"q_ref\": 0,\n  \"initial_x_hii\": {},\n  \"initial_temperature_k\": {},\n  \"n_h0_cm3\": {},\n  \"n_he0_cm3\": {},\n  \"accepted\": {},\n  \"comparisons\": {},\n  \"attempts\": {},\n  \"rejects\": {},\n  \"rhs_evaluations\": {},\n  \"a\": {},\n  \"x_hii\": {},\n  \"temperature_k\": {},\n  \"number_residual\": {number},\n  \"energy_residual_ev_per_h\": {energy},\n  \"last_error\": {},\n  \"checkpoint_roundtrip\": true,\n  \"wall_s\": {}\n}}\n",
            driver.config.initial_x_hii,
            driver.config.initial_temperature_k,
            driver.n_h0_cm3,
            driver.n_he0_cm3,
            state.accepted,
            state.comparisons,
            state.attempts,
            state.rejects,
            state.rhs_evaluations,
            state.a,
            state.gas.fractions[0],
            eos.temperature_k,
            state.last_error,
            started.elapsed().as_secs_f64()
        ),
    )?;
    if let Some(error) = failure {
        return Err(error.into());
    }
    Ok(())
}

fn main() -> Result<(), Box<dyn Error>> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    if args.len() != 2 || args[0] != "--output" {
        return Err("usage: flrw_integration_probe --output FRESH_DIRECTORY".into());
    }
    let root = Path::new(&args[1]);
    if root.exists() {
        return Err("probe requires a fresh output directory".into());
    }
    fs::create_dir_all(root)?;
    fs::write(root.join("source_identity.txt"), compiled_identity())?;
    fs::write(
        root.join("probe_source.rs"),
        include_str!("flrw_integration_probe.rs"),
    )?;
    let (clock_driver, _) = Driver::new(DriverConfig::baseline())?;
    let a0 = 0.19_f64;
    let a1 = a0 * (1.0 + 1e-10);
    let before = Instant::now();
    let increment = clock_driver.background.interval_increment(a0, a1)?;
    let local_wall = before.elapsed().as_secs_f64();
    let before = Instant::now();
    let accumulated = clock_driver.background.point_at_scale(a1)?.time_s
        - clock_driver.background.point_at_scale(a0)?.time_s;
    let accumulated_wall = before.elapsed().as_secs_f64();
    fs::write(
        root.join("clock_comparison.json"),
        format!(
            "{{\n  \"a0\": {a0},\n  \"a1\": {a1},\n  \"stable_dt_s\": {},\n  \"accumulated_difference_s\": {accumulated},\n  \"gl4_minus_gl8_s\": {},\n  \"stable_wall_s\": {local_wall},\n  \"accumulated_wall_s\": {accumulated_wall}\n}}\n",
            increment.proper_time_s, increment.gl4_time_difference_s
        ),
    )?;
    run_case(root, "baseline_ic", false)?;
    run_case(root, "donor_ic", true)?;
    println!("two finite q=0 probes complete: {}", root.display());
    Ok(())
}
