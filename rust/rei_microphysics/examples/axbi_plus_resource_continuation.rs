//! One resource-only continuation. The numerical library and original source identity stay frozen.
use rei_microphysics::{axbi_driver::*, ForwardError};
use std::{
    fs,
    io::{BufWriter, Write},
    path::Path,
    process::{Command, Stdio},
    time::Instant,
};
fn err(s: &'static str) -> ForwardError {
    ForwardError::InvalidInput(s)
}
fn ioerr(_: std::io::Error) -> ForwardError {
    err("AXBI_CONTINUATION_IO")
}
pub fn sha256(path: &Path) -> Result<String, ForwardError> {
    let result = Command::new("sha256sum")
        .arg("--")
        .arg(path)
        .stdin(Stdio::null())
        .output()
        .map_err(ioerr)?;
    if !result.status.success() {
        return Err(err("AXBI_IDENTITY_HASH_IO"));
    }
    let text = String::from_utf8(result.stdout).map_err(|_| err("AXBI_IDENTITY_HASH_FORMAT"))?;
    let digest = text
        .split_whitespace()
        .next()
        .ok_or(err("AXBI_IDENTITY_HASH_FORMAT"))?;
    if digest.len() != 64 || !digest.bytes().all(|b| b.is_ascii_hexdigit()) {
        return Err(err("AXBI_IDENTITY_HASH_FORMAT"));
    }
    Ok(digest.to_string())
}
pub struct Expected<'a> {
    pub config: &'a str,
    pub checkpoint: &'a str,
    pub terminal: &'a str,
    pub source: &'a str,
}
pub fn verify_predecessor(
    config: &Path,
    predecessor: &Path,
    out: &Path,
    case: &str,
    expected: &Expected<'_>,
) -> Result<String, ForwardError> {
    if out.exists() {
        return Err(err("AXBI_OUTPUT_EXISTS"));
    }
    if case != "SHEAR_PLUS"
        || fs::read_to_string(predecessor.join("case_id.txt")).map_err(ioerr)? != case
    {
        return Err(err("AXBI_RESUME_CASE"));
    }
    for (path, digest) in [
        (config.to_path_buf(), expected.config),
        (predecessor.join("config.cfg"), expected.config),
        (predecessor.join("checkpoint.txt"), expected.checkpoint),
        (predecessor.join("RETURN.txt"), expected.terminal),
        (predecessor.join("source_identity.txt"), expected.source),
    ] {
        if sha256(&path)? != digest {
            return Err(err("AXBI_PREDECESSOR_IDENTITY"));
        }
    }
    if fs::read_to_string(predecessor.join("source_identity.txt")).map_err(ioerr)?
        != compiled_identity()
    {
        return Err(err("AXBI_RESUME_IDENTITY"));
    }
    fs::read_to_string(config).map_err(ioerr)
}
pub fn resource_cap(driver: &Driver, state: &DriverState) -> bool {
    state.wall_elapsed_s >= driver.config.max_wall_s
        || state.accepted >= driver.config.max_steps
        || state.attempts >= driver.config.max_attempts
        || state.rhs_evaluations >= driver.config.max_rhs
}
pub fn rollback_charged(state: &mut DriverState, previous: DriverState) {
    let failed = state.clone();
    *state = previous;
    state.attempts = failed.attempts;
    state.comparisons = failed.comparisons;
    state.rhs_evaluations = failed.rhs_evaluations;
    state.rejects = failed.rejects;
    state.wall_elapsed_s = failed.wall_elapsed_s;
}
pub fn run_segment(
    driver: Driver,
    mut state: DriverState,
    config_text: &str,
    out: &Path,
    case: &str,
) -> Result<(), ForwardError> {
    if case != "SHEAR_PLUS" {
        return Err(err("AXBI_RESUME_CASE"));
    }
    if out.exists() {
        return Err(err("AXBI_OUTPUT_EXISTS"));
    }
    let starting = state.clone();
    fs::create_dir(out).map_err(ioerr)?;
    fs::create_dir(out.join("raw")).map_err(ioerr)?;
    fs::create_dir(out.join("checkpoints")).map_err(ioerr)?;
    fs::write(out.join("config.cfg"), config_text).map_err(ioerr)?;
    fs::write(out.join("source_identity.txt"), compiled_identity()).map_err(ioerr)?;
    fs::write(out.join("case_id.txt"), case).map_err(ioerr)?;
    fs::write(
        out.join("segment_id.txt"),
        "SHEAR_PLUS_RESOURCE_CONTINUATION_001",
    )
    .map_err(ioerr)?;
    fs::write(
        out.join("effective_resource_overrides.json"),
        "{\"max_steps\":500000,\"max_attempts\":1550054,\"max_wall_s\":16976.389416854}\n",
    )
    .map_err(ioerr)?;
    fs::write(out.join("metadata.txt"),"boundary=first row exactly duplicates predecessor terminal checkpoint; composed history counts once\nclock=original proper seconds since zbar20; no rebasing\nfull_history_feedback=PENDING_original_prefix_plus_segment_composition\nscientific_admission=NOT_ISSUED\n").map_err(ioerr)?;
    pub fn open_output(
        path: &Path,
        resume: bool,
        header: &str,
    ) -> Result<BufWriter<fs::File>, ForwardError> {
        let exists = path.exists();
        let mut f = BufWriter::new(
            fs::OpenOptions::new()
                .create(true)
                .write(true)
                .append(resume)
                .truncate(!resume)
                .open(path)
                .map_err(ioerr)?,
        );
        if !resume || !exists {
            writeln!(f, "{header}").map_err(ioerr)?;
        }
        Ok(f)
    }
    let mut h=open_output(&out.join("history.csv"),false,"case_id,q_ref,Sigma,time_s,a,zbar,b,H_per_s,s_per_s,x_HII,x_HeII,x_HeIII,nH_proper_cm3,ne_proper_cm3,temperature_K,Gamma_HI_per_s,Gamma_HeI_per_s,Gamma_HeII_per_s,photon_n_per_H,photon_u_eV_per_H,J0_photon_u_eV_per_H,J1_photon_u_eV_per_H,J2_photon_u_eV_per_H,x_HI,x_HeI")?;
    let mut a=open_output(&out.join("abundances.csv"),false,"run_id,time_s,zbar,Tgas_K,background_Tref_K,species_id,A,Z,charge,nproper,element_fraction,Ybaryon,electron_xe,normalization_registry")?;
    let mut p=open_output(&out.join("spectra.csv"),false,"case_id,q_ref,Sigma,time_s,a,zbar,energy_low_eV,energy_high_eV,mu_center,solid_angle_weight_sr,photon_n_per_H,photon_u_eV_per_H")?;
    let mut l = open_output(
        &out.join("ledgers.csv"),
        false,
        "case_id,time_s,ledger_name,residual,tolerance,status",
    )?;
    let mut fb=open_output(&out.join("feedback.csv"),false,"case_id,time_s,a,H_per_s,effective_radiation_DeltaP_J_m3,ionizing_DeltaP_J_m3,effective_radiation_signed_deltaepsilon_J_m3,extra_energy_J_m3,extra_energy_ratio,total_DeltaP_J_m3")?;
    let mut rejects = open_output(
        &out.join("raw/rejections.csv"),
        true,
        "attempt,a,dln_a,error",
    )?;
    let mut last_spectrum_time = Some(driver.background.point_at_scale(state.a)?.time_s);
    driver.output_batch(
        &state, case, out, true, &mut h, &mut a, &mut p, &mut l, &mut fb,
    )?;
    for writer in [&mut h, &mut a, &mut p, &mut l, &mut fb, &mut rejects] {
        writer.flush().map_err(ioerr)?;
    }
    driver.save_checkpoint_budget(out, &out.join("checkpoint.txt"), &state)?;
    let started = Instant::now();
    let prior_wall = state.wall_elapsed_s;
    let mut last_save = Instant::now();
    let end = 1.0 / (1.0 + driver.config.end_zbar);
    let mut outcome = (|| {
        while state.a < end {
            state.wall_elapsed_s = prior_wall + started.elapsed().as_secs_f64();
            if resource_cap(&driver, &state) {
                return Err(err("AXBI_RUNTIME_CAP"));
            }
            let previous = state.clone();
            let accepted = match driver.adaptive_step(&mut state) {
                Ok(value) => value,
                Err(e) => {
                    writeln!(
                        rejects,
                        "{},{},{},{e:?}",
                        state.attempts, state.a, state.next_dln_a
                    )
                    .map_err(ioerr)?;
                    rejects.flush().map_err(ioerr)?;
                    if state.consecutive_rejects >= 30
                        || state.next_dln_a < 1e-10
                        || state.rhs_evaluations >= driver.config.max_rhs
                    {
                        return Err(e);
                    }
                    false
                }
            };
            if !accepted {
                writeln!(
                    rejects,
                    "{},{},{},local_metric={}",
                    state.attempts, state.a, state.next_dln_a, state.last_error
                )
                .map_err(ioerr)?;
                if state.consecutive_rejects >= 30 || state.next_dln_a < 1e-10 {
                    return Err(err("AXBI_REJECT_CAP"));
                }
                continue;
            }
            let checkpoint_due = driver.spectrum_due(
                state.accepted,
                last_save.elapsed().as_secs_f64(),
                state.a == end,
            );
            if let Err(error) = driver.output_batch(
                &state,
                case,
                out,
                checkpoint_due,
                &mut h,
                &mut a,
                &mut p,
                &mut l,
                &mut fb,
            ) {
                rollback_charged(&mut state, previous);
                return Err(error);
            }
            if checkpoint_due {
                last_spectrum_time = Some(driver.background.point_at_scale(state.a)?.time_s);
                for writer in [&mut h, &mut a, &mut p, &mut l, &mut fb, &mut rejects] {
                    writer.flush().map_err(ioerr)?;
                }
                state.wall_elapsed_s = prior_wall + started.elapsed().as_secs_f64();
                driver.save_checkpoint_budget(
                    out,
                    &out.join(format!("checkpoints/{:08}.txt", state.accepted)),
                    &state,
                )?;
                driver.save_checkpoint_budget(out, &out.join("checkpoint.txt"), &state)?;
                check_resources(out, driver.config.output_budget_mib as u64 * 1024 * 1024)?;
                last_save = Instant::now();
            }
        }
        if state.a != end {
            return Err(err("AXBI_ENDPOINT_ABSENT"));
        }
        driver.validate(&state, 1e-8)?;
        Ok(())
    })();
    state.wall_elapsed_s = prior_wall + started.elapsed().as_secs_f64();
    for writer in [&mut h, &mut a, &mut p, &mut l, &mut fb, &mut rejects] {
        writer.flush().map_err(ioerr)?;
    }
    let terminal_save = (|| {
        driver.ensure_spectrum_snapshot(&state, case, out, &mut last_spectrum_time, &mut p)?;
        p.flush().map_err(ioerr)?;
        driver.save_checkpoint_budget(out, &out.join("checkpoint.txt"), &state)
    })();
    let terminal_save_result = format!("{terminal_save:?}");
    if outcome.is_ok() {
        outcome = terminal_save;
    }
    let residuals = driver.residuals(&state)?;
    let durable = sha256(&out.join("checkpoint.txt"))?;
    let saved_text = fs::read_to_string(out.join("checkpoint.txt")).map_err(ioerr)?;
    let initial_energy_reference = saved_text
        .lines()
        .nth(5)
        .ok_or(err("AXBI_CHECKPOINT_SHAPE_OR_INITIAL"))?;
    fs::write(out.join("RETURN.txt"),format!("status={}\na={}\naccepted={}\nattempts={}\ncomparisons={}\nrejections={}\nrhs_evaluations={}\nwall_s={}\nmax_newton_residual={}\nlast_error={}\nresiduals={residuals:?}\nresult={outcome:?}\nfull_history_feedback=PENDING\nscientific_admission=NOT_ISSUED\n",if outcome.is_ok() && state.a==end {"COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT"} else {"STOPPED_CHECKPOINTED"},state.a,state.accepted,state.attempts,state.comparisons,state.rejects,state.rhs_evaluations,state.wall_elapsed_s,state.max_newton_residual,state.last_error)).map_err(ioerr)?;
    let mut terminal = fs::OpenOptions::new()
        .append(true)
        .open(out.join("RETURN.txt"))
        .map_err(ioerr)?;
    writeln!(terminal, "case_id={case}\nsegment_id=SHEAR_PLUS_RESOURCE_CONTINUATION_001\nstarting_a={}\nstarting_accepted={}\nstarting_attempts={}\nstarting_rhs_evaluations={}\nstarting_comparisons={}\nstarting_rejections={}\nstarting_wall_s={}\nsegment_accepted={}\nsegment_attempts={}\nsegment_rhs_evaluations={}\nsegment_comparisons={}\nsegment_rejections={}\nsegment_wall_s={}\neffective_max_steps={}\neffective_max_attempts={}\neffective_max_rhs={}\neffective_max_wall_s={}\neffective_output_budget_mib={}\nlast_durable_checkpoint={}\nterminal_checkpoint_save={terminal_save_result}\nlast_durable_checkpoint_sha256={durable}\ninitial_energy_reference={initial_energy_reference}",
        starting.a, starting.accepted, starting.attempts, starting.rhs_evaluations, starting.comparisons, starting.rejects, starting.wall_elapsed_s,
        state.accepted-starting.accepted, state.attempts-starting.attempts, state.rhs_evaluations-starting.rhs_evaluations, state.comparisons-starting.comparisons, state.rejects-starting.rejects, state.wall_elapsed_s-starting.wall_elapsed_s,
        driver.config.max_steps, driver.config.max_attempts, driver.config.max_rhs, driver.config.max_wall_s, driver.config.output_budget_mib, out.join("checkpoint.txt").display()).map_err(ioerr)?;
    outcome
}
fn main() {
    let result = cli();
    if let Err(error) = result {
        eprintln!("{error:?}");
        std::process::exit(1);
    }
}
fn cli() -> Result<(), ForwardError> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    let mut values = std::collections::BTreeMap::new();
    if args.len() != 8 {
        return Err(err("AXBI_CONTINUATION_USAGE"));
    }
    for pair in args.chunks_exact(2) {
        if !["--config", "--predecessor", "--output", "--case"].contains(&pair[0].as_str())
            || values.insert(pair[0].as_str(), pair[1].as_str()).is_some()
        {
            return Err(err("AXBI_CONTINUATION_USAGE"));
        }
    }
    let get = |key| {
        values
            .get(key)
            .copied()
            .ok_or(err("AXBI_CONTINUATION_USAGE"))
    };
    let config = Path::new(get("--config")?);
    let predecessor = Path::new(get("--predecessor")?);
    let out = Path::new(get("--output")?);
    let case = get("--case")?;
    let expected = Expected {
        config: "b9a8bdeaf61a68839e23486fa8ad0740fe1318c55cbc7f522e11cacbb4ff21c0",
        checkpoint: "00c74753d79b80c9f3fc73a3703d0f6b3f9d08fe003bf7bd816d570a9f37f831",
        terminal: "d7e028dca87141f54ac2a653b4657781d679dde8e5a8de0a1bca43865a745862",
        source: "d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185",
    };
    let text = verify_predecessor(config, predecessor, out, case, &expected)?;
    let mut cfg = DriverConfig::read(&text)?;
    cfg.max_steps = 500000;
    cfg.max_attempts = 1550054;
    cfg.max_wall_s = 16976.389416854;
    let (driver, _) = Driver::new(cfg)?;
    let state = driver.read_checkpoint(&predecessor.join("checkpoint.txt"))?;
    if state.accepted != 200000
        || state.attempts != 600054
        || state.rhs_evaluations != 4200402
        || state.comparisons != 200018
        || state.consecutive_rejects != 0
        || state.rejects != 18
        || state.a != 0.08873654701704167
        || state.wall_elapsed_s != 6176.389416854
    {
        return Err(err("AXBI_PREDECESSOR_STATE"));
    }
    let binary = sha256(&std::env::current_exe().map_err(ioerr)?)?;
    // Wrapper identity is execution provenance, never the original binary identity.
    let source = sha256(Path::new(
        "rust/rei_microphysics/examples/axbi_plus_resource_continuation.rs",
    ))?;
    let binding_path = Path::new(
        "research/axbi_goal_20261014/driver/full/post_plus_001/PLUS_CONTINUATION_BINDING.json",
    );
    let binding_sha256 = sha256(binding_path)?;
    let result = run_segment(driver, state, &text, out, case);
    if out.exists() {
        fs::write(out.join("execution_wrapper_identity.json"),format!("{{\"new_binary_sha256\":\"{binary}\",\"new_example_source_sha256\":\"{source}\",\"original_binary_sha256\":\"32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca\"}}\n")).map_err(ioerr)?;
    }
    if out.join("RETURN.txt").exists() {
        let mut terminal = fs::OpenOptions::new()
            .append(true)
            .open(out.join("RETURN.txt"))
            .map_err(ioerr)?;
        writeln!(terminal, "predecessor={}\npredecessor_config_path={}\npredecessor_config_sha256={}\npredecessor_checkpoint_path={}\npredecessor_checkpoint_sha256={}\npredecessor_RETURN_path={}\npredecessor_RETURN_sha256={}\npredecessor_source_identity_path={}\npredecessor_source_identity_sha256={}\nexecution_binding_path={}\nexecution_binding_sha256={}\nnew_binary_sha256={}\nnew_example_source_sha256={}\noriginal_max_steps=200000\noriginal_max_attempts=650000\noriginal_max_rhs=20000000\noriginal_max_wall_s=10800\noriginal_output_budget_mib=2048",
            predecessor.display(), predecessor.join("config.cfg").display(), expected.config,
            predecessor.join("checkpoint.txt").display(), expected.checkpoint,
            predecessor.join("RETURN.txt").display(), expected.terminal,
            predecessor.join("source_identity.txt").display(), expected.source,
            binding_path.display(), binding_sha256, binary, source).map_err(ioerr)?;
    }
    result
}
fn check_resources(out: &Path, total_output_bytes: u64) -> Result<(), ForwardError> {
    guard_output_bytes_with_limit(out, 0, total_output_bytes)?;
    if let Ok(status) = fs::read_to_string("/proc/self/status") {
        if let Some(line) = status.lines().find(|s| s.starts_with("VmHWM:")) {
            if line
                .split_whitespace()
                .nth(1)
                .and_then(|s| s.parse::<u64>().ok())
                .unwrap_or(0)
                > 2 * 1024 * 1024
            {
                return Err(err("AXBI_RSS_CAP"));
            }
        }
    }
    Ok(())
}
