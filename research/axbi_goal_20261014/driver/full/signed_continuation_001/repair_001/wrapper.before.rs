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
    if !CASES.contains(&case) {
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
        format!("{case}_RESOURCE_CONTINUATION_001"),
    )
    .map_err(ioerr)?;
    fs::write(
        out.join("effective_resource_overrides.json"),
        format!("{{\"max_steps\":{},\"max_attempts\":{},\"max_rhs\":{},\"max_wall_s\":{},\"output_budget_mib\":{}}}\n",driver.config.max_steps,driver.config.max_attempts,driver.config.max_rhs,driver.config.max_wall_s,driver.config.output_budget_mib),
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
    writeln!(terminal, "case_id={case}\nsegment_id={case}_RESOURCE_CONTINUATION_001\nstarting_a={}\nstarting_accepted={}\nstarting_attempts={}\nstarting_rhs_evaluations={}\nstarting_comparisons={}\nstarting_rejections={}\nstarting_wall_s={}\nsegment_accepted={}\nsegment_attempts={}\nsegment_rhs_evaluations={}\nsegment_comparisons={}\nsegment_rejections={}\nsegment_wall_s={}\neffective_max_steps={}\neffective_max_attempts={}\neffective_max_rhs={}\neffective_max_wall_s={}\neffective_output_budget_mib={}\nlast_durable_checkpoint={}\nterminal_checkpoint_save={terminal_save_result}\nlast_durable_checkpoint_sha256={durable}\ninitial_energy_reference={initial_energy_reference}",
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
const CASES: [&str; 3] = ["SHEAR_MINUS", "SHEAR_HALF_PLUS", "SHEAR_HALF_MINUS"];
pub const OLD: &str = "d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185";
pub const NEW: &str = "4de69c1e68ebd395fe2d0b5580d901b9a82bde86cadbd11bdd07e5ad2042b4a1";
const KEYS: &[&str] = &[
    "execution_authorized",
    "start_authorized",
    "case",
    "segment",
    "config",
    "config_sha256",
    "q_ref",
    "predecessor",
    "output",
    "raw_output",
    "checkpoint_sha256",
    "terminal_sha256",
    "old_source_sha256",
    "current_source",
    "current_source_sha256",
    "decision",
    "decision_sha256",
    "review",
    "review_sha256",
    "example",
    "example_sha256",
    "binary_sha256",
    "authority",
    "authority_sha256",
    "starting_state_debug",
    "additional_steps",
    "additional_attempts",
    "additional_wall_s",
    "additional_output_mib",
    "effective_max_steps",
    "effective_max_attempts",
    "effective_max_rhs",
    "effective_max_wall_s",
    "effective_output_budget_mib",
];
pub type Binding = std::collections::BTreeMap<String, String>;
pub fn parse_binding(text: &str) -> Result<Binding, ForwardError> {
    let mut values = Binding::new();
    for line in text.lines() {
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let (k, v) = line.split_once('=').ok_or(err("AXBI_BINDING_FORMAT"))?;
        if !KEYS.contains(&k) || v.is_empty() || values.insert(k.into(), v.into()).is_some() {
            return Err(err("AXBI_BINDING_KEY"));
        }
    }
    Ok(values)
}
fn get<'a>(b: &'a Binding, k: &str) -> Result<&'a str, ForwardError> {
    b.get(k)
        .map(String::as_str)
        .ok_or(err("AXBI_BINDING_MISSING"))
}
pub fn execution_gate(b: &Binding) -> Result<(), ForwardError> {
    if get(b, "execution_authorized")? != "true" || get(b, "start_authorized")? != "true" {
        return Err(err("AXBI_EXECUTION_NOT_AUTHORIZED"));
    }
    let case = get(b, "case")?;
    if !CASES.contains(&case) || get(b, "segment")? != format!("{case}_RESOURCE_CONTINUATION_001") {
        return Err(err("AXBI_RESUME_CASE"));
    }
    if get(b, "old_source_sha256")? != OLD || get(b, "current_source_sha256")? != NEW {
        return Err(err("AXBI_SOURCE_EPOCH"));
    }
    for k in KEYS {
        get(b, k)?;
    }
    Ok(())
}
fn hash_check(path: &str, digest: &str) -> Result<(), ForwardError> {
    if sha256(Path::new(path))? != digest {
        Err(err("AXBI_PREDECESSOR_IDENTITY"))
    } else {
        Ok(())
    }
}
pub fn verify_authority(b: &Binding) -> Result<(), ForwardError> {
    hash_check(get(b, "authority")?, get(b, "authority_sha256")?)?;
    let authority = parse_binding(&fs::read_to_string(get(b, "authority")?).map_err(ioerr)?)?;
    for (k, v) in b {
        if !["authority", "authority_sha256"].contains(&k.as_str()) && authority.get(k) != Some(v) {
            return Err(err("AXBI_AUTHORITY_BINDING"));
        }
    }
    Ok(())
}
pub fn apply_caps(cfg: &mut DriverConfig, b: &Binding) -> Result<(), ForwardError> {
    let n = |k| -> Result<usize, ForwardError> {
        get(b, k)?.parse().map_err(|_| err("AXBI_RESOURCE_VALUE"))
    };
    let f = |k| -> Result<f64, ForwardError> {
        let x: f64 = get(b, k)?.parse().map_err(|_| err("AXBI_RESOURCE_VALUE"))?;
        if !x.is_finite() || x <= 0. {
            return Err(err("AXBI_RESOURCE_VALUE"));
        }
        Ok(x)
    };
    let ds = n("additional_steps")?;
    let da = n("additional_attempts")?;
    let dw = f("additional_wall_s")?;
    let dout = n("additional_output_mib")?;
    let steps = n("effective_max_steps")?;
    let attempts = n("effective_max_attempts")?;
    let wall = f("effective_max_wall_s")?;
    let output = n("effective_output_budget_mib")?;
    if ds == 0
        || da == 0
        || dout == 0
        || cfg.max_steps.checked_add(ds) != Some(steps)
        || cfg.max_attempts.checked_add(da) != Some(attempts)
        || cfg.output_budget_mib.checked_add(dout) != Some(output)
        || cfg.max_wall_s + dw != wall
        || wall <= cfg.max_wall_s
        || n("effective_max_rhs")? != cfg.max_rhs
    {
        return Err(err("AXBI_RESOURCE_ARITHMETIC"));
    }
    cfg.max_steps = steps;
    cfg.max_attempts = attempts;
    cfg.max_wall_s = wall;
    cfg.output_budget_mib = output;
    Ok(())
}
fn cli() -> Result<(), ForwardError> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    if args.len() != 4 {
        return Err(err("AXBI_CONTINUATION_USAGE"));
    }
    let mut a = Binding::new();
    for p in args.chunks_exact(2) {
        if !["--binding", "--binding-sha256"].contains(&p[0].as_str())
            || a.insert(p[0].clone(), p[1].clone()).is_some()
        {
            return Err(err("AXBI_CONTINUATION_USAGE"));
        }
    }
    let binding_path = get(&a, "--binding")?;
    let binding_sha = get(&a, "--binding-sha256")?;
    hash_check(binding_path, binding_sha)?;
    let b = parse_binding(&fs::read_to_string(binding_path).map_err(ioerr)?)?;
    execution_gate(&b)?; // Before any output creation or Driver construction.
    verify_authority(&b)?;
    let case = get(&b, "case")?;
    let config = get(&b, "config")?;
    let expected_config = match case {
        "SHEAR_MINUS" => "d5227c1925d27a89e71bf59e1e5abd0557061f910172ea5fa9baacaece46c677",
        "SHEAR_HALF_PLUS" => "a5af5c6e61b2bca228baa8bf71e33e12ebbebb3638425704178badcba6135b81",
        _ => "d0c4d48fdcec402d4e2108d5ac205be00428846156f3613ff6e2e842e168bef2",
    };
    if get(&b, "config_sha256")? != expected_config
        || config != format!("research/axbi_goal_20261014/driver/full/{case}.cfg")
    {
        return Err(err("AXBI_CONFIG_BINDING"));
    }
    let predecessor = Path::new(get(&b, "predecessor")?);
    let out = Path::new(get(&b, "output")?);
    if out.exists() || Path::new(get(&b, "raw_output")?).exists() {
        return Err(err("AXBI_OUTPUT_EXISTS"));
    }
    if fs::read_to_string(predecessor.join("case_id.txt")).map_err(ioerr)? != case {
        return Err(err("AXBI_RESUME_CASE"));
    }
    hash_check(config, expected_config)?;
    for (name, key) in [
        ("config.cfg", "config_sha256"),
        ("checkpoint.txt", "checkpoint_sha256"),
        ("RETURN.txt", "terminal_sha256"),
        ("source_identity.txt", "old_source_sha256"),
    ] {
        hash_check(
            predecessor.join(name).to_str().ok_or(err("AXBI_PATH"))?,
            get(&b, key)?,
        )?;
    }
    for (path, key) in [
        ("current_source", "current_source_sha256"),
        ("decision", "decision_sha256"),
        ("review", "review_sha256"),
        ("example", "example_sha256"),
    ] {
        hash_check(get(&b, path)?, get(&b, key)?)?;
    }
    if get(&b, "decision_sha256")? != DECISION_SHA
        || get(&b, "review_sha256")? != REVIEW_SHA
        || fs::read_to_string(get(&b, "current_source")?).map_err(ioerr)? != compiled_identity()
    {
        return Err(err("AXBI_SOURCE_COMPATIBILITY"));
    }
    let binary = sha256(&std::env::current_exe().map_err(ioerr)?)?;
    if binary != get(&b, "binary_sha256")? {
        return Err(err("AXBI_BINARY_IDENTITY"));
    }
    let text = fs::read_to_string(config).map_err(ioerr)?;
    let mut cfg = DriverConfig::read(&text)?;
    let q = match case {
        "SHEAR_MINUS" => -0.01,
        "SHEAR_HALF_PLUS" => 0.005,
        _ => -0.005,
    };
    if cfg.q_ref != q
        || get(&b, "q_ref")?
            .parse::<f64>()
            .map_err(|_| err("AXBI_Q_REF"))?
            != q
    {
        return Err(err("AXBI_Q_REF"));
    }
    let old = cfg.clone();
    apply_caps(&mut cfg, &b)?;
    let (driver, _) = Driver::new(cfg)?;
    let state = driver.read_checkpoint(&predecessor.join("checkpoint.txt"))?;
    if format!("{state:?}") != get(&b, "starting_state_debug")? || state.photons.len() != 392 {
        return Err(err("AXBI_PREDECESSOR_STATE"));
    }
    driver.validate(&state, 1e-8)?;
    let result = run_segment(driver, state, &text, out, case);
    if out.exists() {
        fs::copy(
            predecessor.join("source_identity.txt"),
            out.join("predecessor_source_identity.txt"),
        )
        .map_err(ioerr)?;
        fs::write(out.join("source_compatibility.json"),format!("{{\"old_source_sha256\":\"{OLD}\",\"current_source_sha256\":\"{NEW}\",\"decision_sha256\":\"{DECISION_SHA}\",\"review_sha256\":\"{REVIEW_SHA}\",\"binding_sha256\":\"{binding_sha}\",\"authority_sha256\":\"{}\",\"checkpoint_sha256\":\"{}\",\"terminal_sha256\":\"{}\",\"new_binary_sha256\":\"{binary}\",\"original_binary_sha256\":\"32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca\",\"relation\":\"REVIEWED_RESOURCE_ONLY\"}}\n",get(&b,"authority_sha256")?,get(&b,"checkpoint_sha256")?,get(&b,"terminal_sha256")?)).map_err(ioerr)?;
        if out.join("RETURN.txt").exists() {
            let mut f = fs::OpenOptions::new()
                .append(true)
                .open(out.join("RETURN.txt"))
                .map_err(ioerr)?;
            writeln!(f,"original_resource_config={old:?}\nexecution_binding_path={binding_path}\nexecution_binding_sha256={binding_sha}\nold_source_sha256={OLD}\ncurrent_source_sha256={NEW}\nnew_binary_sha256={binary}\nexternal_exit=PENDING_CONTROLLER_OBSERVATION\nadditional_steps={}\nadditional_attempts={}\nadditional_wall_s={}\nadditional_output_mib={}",get(&b,"additional_steps")?,get(&b,"additional_attempts")?,get(&b,"additional_wall_s")?,get(&b,"additional_output_mib")?).map_err(ioerr)?;
        }
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

const DECISION_SHA: &str = "80dd0bf70778f82a8bd10e1bb603fa31d270cc0dcfdfd00b9c8ddf07c7855e9a";
const REVIEW_SHA: &str = "03a291a56b9f3b7b22c63f7a7e75ef69ef58e990e6fe4d2e0541c5b2275f3399";
