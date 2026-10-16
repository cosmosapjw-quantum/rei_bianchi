//! Diagnostic-only pinned suffix. Never resumes or appends a production history.
use rei_microphysics::axbi_bass_background::{sha256_bytes, BassBackground, BassSourceIdentity};
use rei_microphysics::axbi_driver::{
    compiled_identity, ChemicalStageObserver, Driver, DriverConfig,
};
use std::{
    env, fs,
    io::Write,
    path::{Path, PathBuf},
    process::{Command, Stdio},
    time::Instant,
};
fn repository() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}
fn driver_blob() -> Result<String, Box<dyn std::error::Error>> {
    let mut p = Command::new("git")
        .args(["hash-object", "--stdin"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()?;
    p.stdin
        .take()
        .unwrap()
        .write_all(include_bytes!("../src/axbi_driver.rs"))?;
    let result = p.wait_with_output()?;
    if !result.status.success() {
        return Err("GIT_BLOB_ID_FAILED".into());
    };
    Ok(String::from_utf8(result.stdout)?.trim().into())
}
pub fn execute(args: &[String]) -> Result<(), Box<dyn std::error::Error>> {
    if args.len() != 5 || args[1] != "--authority" || args[3] != "--output" {
        return Err(
            "usage: bass_nonlinear_stage_probe --authority AUTHORITY --output FRESH_DIR".into(),
        );
    }
    let repo = repository();
    let authority = fs::read(&args[2])?;
    if sha256_bytes(&authority)?
        != "ceb299fc6335e478d76a7d35c78ccb45695ba368d4e56b786e3e37beded37ee6"
    {
        return Err("AUTHORITY_HASH".into());
    }
    let input = repo.join("research/bass_source011_20261016/inputs");
    let cfg = fs::read_to_string(input.join("config.cfg"))?;
    if sha256_bytes(cfg.as_bytes())?
        != "26a8ce144f65b19f8eec76b79c221aa28500968c2f9f340c251841f00615f13d"
    {
        return Err("CONFIG_HASH".into());
    }
    let bg = BassBackground::from_files(
        &repo.join("research/bass_source007_20261016/inputs/pr164_121.csv"),
        &repo.join("research/bass_source007_20261016/inputs/pr164_121.json"),
        BassSourceIdentity {
            producer_commit: "3c39bbbf46b6663e7c40277e194fd0ef48118472".into(),
            source_csv_sha256: "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133"
                .into(),
            source_manifest_sha256:
                "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed".into(),
            case: "SIGNED_MINUS".into(),
            grid_points: 121,
        },
    )?;
    let (d, _) = Driver::new_bass(DriverConfig::read(&cfg)?, bg)?;
    let mut s = d.read_source011_probe_checkpoint(
        &input.join("accepted-00039600.bass-v1"),
        &input.join("RUN_BINDING.txt"),
    )?;
    let reference = d.read_source011_probe_checkpoint(
        &input.join("terminal-00039624.bass-v1"),
        &input.join("RUN_BINDING.txt"),
    )?;
    let out = Path::new(&args[4]);
    fs::create_dir(out)?;
    let mut obs = ChemicalStageObserver::new(1024);
    let base = (s.accepted, s.attempts, s.rhs_evaluations);
    obs.native_rhs_ceiling = Some(
        base.2
            .checked_add(3000)
            .ok_or("SOURCE011_NATIVE_CAP_OVERFLOW")?,
    );
    let started = Instant::now();
    let end = 1.0 / (1.0 + d.config.end_zbar);
    let outcome = (|| -> Result<(), Box<dyn std::error::Error>> {
        while s.a < end {
            if started.elapsed().as_secs_f64() > 55.0
                || s.accepted - base.0 >= 60
                || s.attempts - base.1 + 3 > 300
                || s.rhs_evaluations - base.2 >= 3000
            {
                return Err("SOURCE011_SUFFIX_CAP".into());
            }
            d.adaptive_step_observed(&mut s, &mut obs)?;
            if s.rhs_evaluations - base.2 > 3000 {
                return Err("SOURCE011_NATIVE_RHS_CAP".into());
            }
        }
        Ok(())
    })();
    let blob = driver_blob()?;
    let head = option_env!("SOURCE011_BUILD_HEAD").unwrap_or("NOT_RECORDED");
    let mut trace = String::from(
        "stage,comparison,branch,chemical_status,adaptive_status,trajectory_role,added_rhs\n",
    );
    for (i, r) in obs.records.iter().enumerate() {
        let context = format!("SOURCE011:{}:{}:{}", r.comparison, r.branch, i);
        let role = match r.branch {
            "FULL" => "FULL_TRIAL_DISCARDED",
            "FIRST_HALF" => "INTERMEDIATE_FIRST_HALF",
            _ => "FINAL_TRAJECTORY_SECOND_HALF",
        };
        trace += &format!(
            "{i},{},{},ACCEPTED_CHEMICAL_STAGE,{},{},{}\n",
            r.comparison, r.branch, r.adaptive_status, role, r.added_rhs
        );
        let packet = format!(
            r#"{{"schema_version":1,"input_kind":"ACTUAL_STAGE","state_order":["x_HII","x_HeII","x_HeIII","w_eV_per_H"],"energy_unit":"eV_per_H","method":"BACKWARD_EULER_PREPARED_ABSORPTION","state":{:?},"old_state":{:?},"residual":{:?},"jacobian":{:?},"residual_evaluation_state":{:?},"jacobian_evaluation_state":{:?},"context_id":"{}","residual_context_id":"{}","jacobian_context_id":"{}","a":{},"dt_s":{},"f_He":{},"k_B_eV_per_K":{},"jacobian_kind":"FINITE_DIFFERENCE","iterate_status":"ACCEPTED_CHEMICAL_STAGE","driver_blob_sha":"{}","source_commit":"{}","stage_id":"{}","execution_receipt":"EXECUTION_RECEIPT.json","cost_owner":"SOURCE011_SEPARATE_OBSERVER","added_rhs_evaluations":{},"adaptive_comparison":{},"branch":"{}","adaptive_status":"{}","trajectory_role":"{}"}}"#,
            r.state,
            r.old_state,
            r.residual,
            r.jacobian,
            r.state,
            r.state,
            context,
            context,
            context,
            r.a,
            r.dt_s,
            r.f_he,
            r.k_b_ev_per_k,
            blob,
            head,
            context,
            r.added_rhs,
            r.comparison,
            r.branch,
            r.adaptive_status,
            role
        );
        fs::write(out.join(format!("stage-{i:03}.json")), packet)?;
    }
    fs::write(out.join("trace.csv"), trace)?;
    fs::write(out.join("terminal_state.txt"), d.source011_state_text(&s)?)?;
    fs::write(
        out.join("reference_state.txt"),
        d.source011_state_text(&reference)?,
    )?;
    let current = d.source011_state_text(&s)?;
    let old = d.source011_state_text(&reference)?;
    let parity = current
        .lines()
        .zip(old.lines())
        .enumerate()
        .all(|(i, (a, b))| {
            if i == 1 {
                a.split_whitespace()
                    .take(10)
                    .eq(b.split_whitespace().take(10))
            } else {
                a == b
            }
        });
    let failure = obs
        .failure
        .as_ref()
        .map(|s| format!("{:?}", s))
        .unwrap_or_else(|| "null".into());
    let json = format!(
        r#"{{"status":"{}","physical_parity_excluding_wall":{},"imported_accepted":{},"imported_attempts":{},"imported_rhs":{},"final_accepted":{},"native_attempt_delta":{},"native_rhs_delta":{},"observer_rhs_delta":{},"total_new_rhs":{},"records":{},"final_comparison":{},"producer_driver_blob":"{}","compiled_source_sha256":"{}","observer_failure":{},"suffix_wall_seconds":{},"scientific_admission":"NOT_ISSUED"}}"#,
        if outcome.is_ok() {
            "SUFFIX_COMPLETE_REVIEW_PENDING"
        } else {
            "SUFFIX_STOPPED_NO_RETRY"
        },
        parity,
        base.0,
        base.1,
        base.2,
        s.accepted,
        s.attempts - base.1,
        s.rhs_evaluations - base.2,
        obs.rhs_evaluations,
        s.rhs_evaluations - base.2 + obs.rhs_evaluations,
        obs.records.len(),
        s.comparisons,
        blob,
        sha256_bytes(compiled_identity().as_bytes())?,
        failure,
        started.elapsed().as_secs_f64()
    );
    fs::write(out.join("EXECUTION_RECEIPT.json"), json)?;
    outcome
}
fn main() {
    if let Err(e) = execute(&env::args().collect::<Vec<_>>()) {
        eprintln!("SOURCE011_PROBE_ERROR: {e:?}");
        std::process::exit(2)
    }
}
