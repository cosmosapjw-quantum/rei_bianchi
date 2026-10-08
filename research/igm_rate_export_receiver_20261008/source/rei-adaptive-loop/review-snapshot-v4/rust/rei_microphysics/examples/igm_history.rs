//! Manufactured homogeneous FLRW history runner. A new output directory is
//! required. --stop-after counts accepted transactions in this invocation.
use rei_microphysics::{
    coupled_primary::PrimaryPacket,
    igm_checkpoint::{decode_checkpoint, encode_checkpoint, output_coordinate, CheckpointIdentity},
    igm_config::parse_config,
    igm_history::{History, HistoryState},
    igm_photo::igm_photo_rates,
};
use std::{
    fs::{self, File, OpenOptions},
    io::{BufWriter, Write},
    path::{Path, PathBuf},
    process::ExitCode,
};

struct Args {
    config: PathBuf,
    output: PathBuf,
    resume: Option<PathBuf>,
    stop_after: Option<usize>,
}
fn parse_args(args: &[String]) -> Result<Args, String> {
    let mut config = None;
    let mut output = None;
    let mut resume = None;
    let mut stop_after = None;
    let mut i = 0;
    while i < args.len() {
        let value = args
            .get(i + 1)
            .ok_or_else(|| format!("missing value for {}", args[i]))?;
        match args[i].as_str() {
            "--config" if config.is_none() => config = Some(PathBuf::from(value)),
            "--output" if output.is_none() => output = Some(PathBuf::from(value)),
            "--resume" if resume.is_none() => resume = Some(PathBuf::from(value)),
            "--stop-after" if stop_after.is_none() => {
                stop_after = Some(value.parse::<usize>().map_err(|_| "invalid --stop-after")?)
            }
            _ => return Err(format!("unknown or repeated argument: {}", args[i])),
        }
        i += 2;
    }
    Ok(Args {
        config: config.ok_or("--config is required")?,
        output: output.ok_or("--output is required")?,
        resume,
        stop_after,
    })
}
fn json_string(s: &str) -> String {
    let mut out = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 32 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}
fn new_file(path: &Path, bytes: &[u8]) -> Result<(), String> {
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .map_err(|e| format!("{}: {e}", path.display()))?;
    file.write_all(bytes)
        .and_then(|()| file.sync_all())
        .map_err(|e| format!("{}: {e}", path.display()))
}
/// Atomic replacement is restricted to files inside the directory this run
/// exclusively created. A failed write leaves the preceding checkpoint intact.
fn replace_file(dir: &Path, name: &str, bytes: &[u8]) -> Result<(), String> {
    let temporary = dir.join(format!(".{name}.pending"));
    new_file(&temporary, bytes)?;
    fs::rename(&temporary, dir.join(name)).map_err(|e| format!("checkpoint/status rename: {e}"))?;
    File::open(dir)
        .and_then(|file| file.sync_all())
        .map_err(|e| format!("directory sync: {e}"))
}
fn checkpoint(
    dir: &Path,
    id: &CheckpointIdentity,
    h: &History,
    s: &HistoryState,
    complete: bool,
) -> Result<(), String> {
    replace_file(
        dir,
        "checkpoint.txt",
        encode_checkpoint(id, h, s, complete)?.as_bytes(),
    )
}
fn status(
    dir: &Path,
    s: &HistoryState,
    kind: &str,
    complete: bool,
    error: Option<&str>,
) -> Result<(), String> {
    let text = format!("{{\"schema\":\"igm_history_status_v1\",\"status\":{},\"complete\":{},\"ln_a\":{},\"z\":{},\"accepted_steps\":{},\"rejected_steps\":{},\"max_residual\":{},\"error\":{}}}\n", json_string(kind), complete, s.ln_a, (-s.ln_a).exp() - 1.0, s.accepted_steps, s.rejected_steps, s.max_residual, error.map(json_string).unwrap_or_else(|| "null".into()));
    replace_file(dir, "status.json", text.as_bytes())
}
const CSV_HEADER: &str = "ln_a,z,x_hii,x_heii,x_heiii,w,T,Tcmb,ne_per_h,Gamma_hi,Gamma_hei,Gamma_heii,Nactive,Eactive,emitted_N,emitted_E,abs_HI,abs_HeI,abs_HeII,out_N,out_E,redshift_E,escape_E,work_E,cmb_reservoir_E,number_residual,energy_residual,ci_HI,ci_HeI,ci_HeII,rr_HII,rr_HeII,rr_HeIII,dr_HeII,ci_floor_HI,ci_floor_HeI,ci_floor_HeII,ce_cap_HI_E,ce_cap_HeI_E,ce_cap_HeII_E,excluded_dr_E,underflow_N_bound,underflow_E_bound,cmb_absolute_exchange_E,accepted_steps,rejected_steps,max_residual,packet_count\n";
fn csv_row(h: &History, s: &HistoryState) -> Result<String, String> {
    let point = h
        .config
        .background
        .at_ln_a(s.ln_a)
        .map_err(|e| e.to_string())?;
    let eos = s
        .gas
        .eos(point.n_h_cm3, point.n_he_cm3)
        .map_err(|e| e.to_string())?;
    let packets: Vec<_> = s
        .packets
        .iter()
        .map(|p| PrimaryPacket {
            energy_ev: h.energy(p, s.ln_a),
            per_h: p.per_h,
        })
        .collect();
    let photo = igm_photo_rates(&s.gas, &packets, point.n_h_cm3, point.n_he_cm3)
        .map_err(|e| e.to_string())?;
    let r = h.radiation(s);
    let b = h.balances(s).map_err(|e| e.to_string())?;
    let l = &s.ledger;
    let values = [
        s.ln_a,
        (-s.ln_a).exp() - 1.0,
        s.gas.fractions[0],
        s.gas.fractions[1],
        s.gas.fractions[2],
        s.gas.w_erg_per_h,
        eos.temperature_k,
        point.tcmb_k,
        eos.electron_density_cm3 / point.n_h_cm3,
        photo.input.gamma_s[0],
        photo.input.gamma_s[1],
        photo.input.gamma_s[2],
        r[0],
        r[1],
        l.emitted_n,
        l.emitted_e,
        l.absorption[0],
        l.absorption[1],
        l.absorption[2],
        l.out_n,
        l.out_e,
        l.redshift_e,
        l.escape_e,
        l.work_e,
        l.cmb_e,
        b[0],
        b[1],
        l.ci[0],
        l.ci[1],
        l.ci[2],
        l.rr[0],
        l.rr[1],
        l.rr[2],
        l.dr,
        l.floor[0],
        l.floor[1],
        l.floor[2],
        l.cap_e[0],
        l.cap_e[1],
        l.cap_e[2],
        l.excluded_dr_e,
        l.underflow_n_bound,
        l.underflow_e_bound,
        l.cmb_abs_e,
    ];
    if !values.iter().all(|v| v.is_finite()) {
        return Err("IGM_CSV_NONFINITE".into());
    }
    let mut row = values
        .iter()
        .map(f64::to_string)
        .collect::<Vec<_>>()
        .join(",");
    row.push_str(&format!(
        ",{},{},{},{}\n",
        s.accepted_steps,
        s.rejected_steps,
        s.max_residual,
        s.packets.len()
    ));
    Ok(row)
}
fn run(args: &[String]) -> Result<(), String> {
    let args = parse_args(args)?;
    let config_bytes = fs::read(&args.config).map_err(|e| format!("config: {e}"))?;
    let config_text =
        std::str::from_utf8(&config_bytes).map_err(|e| format!("config UTF-8: {e}"))?;
    let (h, mut state) = History::new(parse_config(config_text).map_err(|e| e.to_string())?)
        .map_err(|e| e.to_string())?;
    let identity = CheckpointIdentity::new(&config_bytes, &h)?;
    if let Some(path) = &args.resume {
        let text = fs::read_to_string(path).map_err(|e| format!("resume: {e}"))?;
        state = decode_checkpoint(&text, &identity, &h)?.state;
    }
    // Validate and load the resume fully before creating or mutating any output.
    fs::create_dir(&args.output).map_err(|e| {
        if e.kind() == std::io::ErrorKind::AlreadyExists {
            "IGM_OUTPUT_EXISTS: choose a new directory".into()
        } else {
            format!("output directory: {e}")
        }
    })?;
    let start_steps = state.accepted_steps;
    let result = (|| -> Result<(), String> {
        checkpoint(&args.output, &identity, &h, &state, false)?;
        status(&args.output, &state, "running", false, None)?;
        new_file(&args.output.join("config.cfg"), &config_bytes)?;
        let manifest = format!("{{\"schema\":\"igm_history_manifest_v1\",\"model_id\":{},\"provider_id\":{},\"closure_id\":{},\"solver_id\":{},\"checkpoint_schema\":{},\"config_sha256\":{},\"source_sha256\":{},\"resume_checkpoint\":{},\"resume_ln_a\":{},\"source_hash_definition\":\"source model, binary parameters, quadrature controls and complete birth schedule\",\"coordinates\":\"ln(a); dt_eff=delta_ln_a/H_endpoint\",\"output_cursor_definition\":\"number of scheduled output rows already emitted\",\"units\":\"erg/H and photons/H; Gamma in s^-1\",\"claim\":\"Manufactured point-solver numerical history, conditional on Case-A escape, C=1 and primary-only heating; not observed EoR or interval certification\"}}\n", json_string(&h.config.model_id), json_string(&identity.provider_id), json_string(&identity.closure_id), json_string(&identity.solver_id), json_string(&identity.schema_id), json_string(&identity.config_sha256), json_string(&identity.source_sha256), args.resume.as_ref().map(|p| json_string(&p.display().to_string())).unwrap_or_else(|| "null".into()), state.ln_a);
        new_file(&args.output.join("manifest.json"), manifest.as_bytes())?;
        let mut births = String::from("birth_index,ln_a,energy_ev,per_h\n");
        for (index, b) in h.births.iter().enumerate() {
            births.push_str(&format!("{index},{},{},{}\n", b.ln_a, b.energy_ev, b.per_h));
        }
        new_file(&args.output.join("birth_schedule.csv"), births.as_bytes())?;
        let file = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(args.output.join("history.csv"))
            .map_err(|e| e.to_string())?;
        let mut csv = BufWriter::new(file);
        csv.write_all(CSV_HEADER.as_bytes())
            .map_err(|e| e.to_string())?;
        // Every output file begins at its own invocation's restored/initial state.
        csv.write_all(csv_row(&h, &state)?.as_bytes())
            .and_then(|()| csv.flush())
            .map_err(|e| e.to_string())?;
        if state.output_cursor <= h.config.output_panels
            && output_coordinate(&h, state.output_cursor)? == state.ln_a
        {
            state.output_cursor += 1;
        }
        checkpoint(&args.output, &identity, &h, &state, false)?;
        loop {
            if state.ln_a == h.config.end {
                checkpoint(&args.output, &identity, &h, &state, true)?;
                status(&args.output, &state, "complete", true, None)?;
                return Ok(());
            }
            if args
                .stop_after
                .is_some_and(|limit| state.accepted_steps - start_steps >= limit)
            {
                status(&args.output, &state, "stopped", false, None)?;
                return Ok(());
            }
            let endpoint = if state.output_cursor <= h.config.output_panels {
                output_coordinate(&h, state.output_cursor)?
            } else {
                h.config.end
            };
            if endpoint <= state.ln_a {
                return Err("IGM_OUTPUT_CURSOR_INVALID".into());
            }
            state = h.advance_one(&state, endpoint).map_err(|e| e.to_string())?;
            if state.ln_a == endpoint {
                csv.write_all(csv_row(&h, &state)?.as_bytes())
                    .and_then(|()| csv.flush())
                    .map_err(|e| e.to_string())?;
                state.output_cursor += 1;
            }
            checkpoint(&args.output, &identity, &h, &state, false)?;
        }
    })();
    if let Err(error) = result {
        let cp_error = checkpoint(&args.output, &identity, &h, &state, false).err();
        let status_error = status(&args.output, &state, "failed", false, Some(&error)).err();
        return Err(format!(
            "{error}{}{}",
            cp_error
                .map(|e| format!("; checkpoint persistence failed: {e}"))
                .unwrap_or_default(),
            status_error
                .map(|e| format!("; status persistence failed: {e}"))
                .unwrap_or_default()
        ));
    }
    Ok(())
}
fn main() -> ExitCode {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args == ["--help"] {
        println!("Usage: igm_history --config FILE --output NEW_DIRECTORY [--resume CHECKPOINT] [--stop-after N]\n--stop-after counts newly accepted transactions; a deliberate stop returns success with complete=false.\nThe exact config bytes and deterministic source identity must match on resume. Existing output directories are never overwritten.");
        return ExitCode::SUCCESS;
    }
    match run(&args) {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!(
                "{{\"status\":\"failed\",\"complete\":false,\"error\":{}}}",
                json_string(&error)
            );
            ExitCode::FAILURE
        }
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    use rei_microphysics::{
        igm_checkpoint::{decode_checkpoint, CheckpointIdentity},
        igm_config::parse_config,
        igm_history::History,
    };
    use std::sync::atomic::{AtomicUsize, Ordering};
    static COUNTER: AtomicUsize = AtomicUsize::new(0);
    const CONFIG: &str = include_str!("../../../configs/igm_manufactured_v1.cfg");
    fn fixture(extra: &str) -> (PathBuf, PathBuf) {
        let root = std::env::temp_dir().join(format!(
            "rei-igm-cli-{}-{}",
            std::process::id(),
            COUNTER.fetch_add(1, Ordering::SeqCst)
        ));
        fs::create_dir(&root).unwrap();
        let text = CONFIG
            .replace("source_rate=1e-15", "source_rate=0")
            .replace("x_hii=2e-4", "x_hii=0")
            .replace("max_steps=200000", extra);
        let config = root.join("input.cfg");
        fs::write(&config, text).unwrap();
        (root, config)
    }
    fn args(config: &Path, out: &Path) -> Vec<String> {
        vec![
            "--config".into(),
            config.display().to_string(),
            "--output".into(),
            out.display().to_string(),
        ]
    }
    #[test]
    fn existing_directory_is_never_overwritten() {
        let (root, config) = fixture("max_steps=200000");
        let out = root.join("occupied");
        fs::create_dir(&out).unwrap();
        fs::write(out.join("marker"), "keep").unwrap();
        let error = run(&args(&config, &out)).unwrap_err();
        assert!(error.contains("OUTPUT_EXISTS"), "{error}");
        assert_eq!(fs::read_to_string(out.join("marker")).unwrap(), "keep");
        fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn split_cli_restart_matches_continuous_checkpoint_exactly() {
        let (root, config) = fixture("max_steps=200000");
        let split = root.join("split");
        let full = root.join("full");
        let resume = root.join("resume");
        run(&args(&config, &full)).unwrap();
        let mut part = args(&config, &split);
        part.extend(["--stop-after".into(), "2".into()]);
        run(&part).unwrap();
        assert!(fs::read_to_string(split.join("status.json"))
            .unwrap()
            .contains("\"complete\":false"));
        let mut continued = args(&config, &resume);
        continued.extend([
            "--resume".into(),
            split.join("checkpoint.txt").display().to_string(),
        ]);
        run(&continued).unwrap();
        assert_eq!(
            fs::read(full.join("checkpoint.txt")).unwrap(),
            fs::read(resume.join("checkpoint.txt")).unwrap()
        );
        let csv = fs::read_to_string(full.join("history.csv")).unwrap();
        assert!(csv.starts_with("ln_a,z,x_hii,x_heii,x_heiii,w,T,Tcmb,ne_per_h,Gamma_hi,Gamma_hei,Gamma_heii,Nactive,Eactive,"));
        assert_eq!(csv.lines().count(), 22);
        assert_eq!(
            fs::read(config).unwrap(),
            fs::read(full.join("config.cfg")).unwrap()
        );
        fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn runtime_failure_records_last_accepted_checkpoint_and_incomplete_status() {
        let (root, config) = fixture("max_steps=1");
        let out = root.join("failed");
        assert!(run(&args(&config, &out)).is_err());
        let bytes = fs::read(&config).unwrap();
        let (h, _) =
            History::new(parse_config(std::str::from_utf8(&bytes).unwrap()).unwrap()).unwrap();
        let id = CheckpointIdentity::new(&bytes, &h).unwrap();
        let cp = decode_checkpoint(
            &fs::read_to_string(out.join("checkpoint.txt")).unwrap(),
            &id,
            &h,
        )
        .unwrap();
        assert!(!cp.complete);
        assert_eq!(cp.state.accepted_steps, 1);
        assert!(cp.state.ln_a > h.config.start);
        let status = fs::read_to_string(out.join("status.json")).unwrap();
        assert!(status.contains("\"status\":\"failed\""));
        assert!(status.contains("\"complete\":false"));
        fs::remove_dir_all(root).unwrap();
    }
}
