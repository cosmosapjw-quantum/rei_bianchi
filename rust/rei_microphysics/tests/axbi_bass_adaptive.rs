use rei_microphysics::axbi_bass_background::{BassBackground, BassSourceIdentity};
use rei_microphysics::axbi_driver::{run, run_bass_fresh, Driver, DriverConfig};
use std::{
    collections::BTreeMap,
    fs,
    path::{Path, PathBuf},
};
#[path = "../examples/bass_adaptive_trial.rs"]
mod adaptive_cli;
fn fixture() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../research/bass_source007_20261016/inputs")
}
fn scratch(name: &str) -> PathBuf {
    let p = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../research/bass_source009_20261016/raw/test_scratch")
        .join(format!(
            "{}-{}-{:?}",
            std::process::id(),
            name,
            std::thread::current().id()
        ));
    fs::create_dir_all(&p).unwrap();
    p
}
fn bg(case: &str) -> BassBackground {
    BassBackground::from_files(
        &fixture().join("pr164_121.csv"),
        &fixture().join("pr164_121.json"),
        BassSourceIdentity {
            producer_commit: "3c39bbbf46b6663e7c40277e194fd0ef48118472".into(),
            source_csv_sha256: "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133"
                .into(),
            source_manifest_sha256:
                "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed".into(),
            case: case.into(),
            grid_points: 121,
        },
    )
    .unwrap()
}
fn config(end: &str, extra: &str) -> String {
    format!("end_zbar={end}\ninactive_hi_split=true\ntransport_cells=128\nenergy_subdivisions=16\ntransport_threads=1\nparallel_jacobian_columns=false\nspectra_every_accepted=1\nmax_wall_s=10\n{extra}")
}
fn terminal(out: &Path) -> BTreeMap<String, String> {
    fs::read_to_string(out.join("RETURN.txt"))
        .unwrap()
        .lines()
        .filter_map(|line| line.split_once('=').map(|(a, b)| (a.into(), b.into())))
        .collect()
}
fn rows(out: &Path, name: &str) -> Vec<String> {
    fs::read_to_string(out.join(name))
        .unwrap()
        .lines()
        .skip(1)
        .map(str::to_owned)
        .collect()
}
fn check_counts(out: &Path) -> BTreeMap<String, String> {
    let t = terminal(out);
    let n = t["accepted"].parse::<usize>().unwrap();
    assert_eq!(rows(out, "history.csv").len(), n + 1);
    assert_eq!(rows(out, "abundances.csv").len(), 6 * (n + 1));
    assert_eq!(rows(out, "ledgers.csv").len(), 31 * (n + 1));
    assert!(Path::new(&t["last_checkpoint"]).is_file());
    assert!(fs::read_to_string(&t["last_checkpoint"])
        .unwrap()
        .contains("CURRENT_PROVIDER=SOURCE009"));
    t
}
#[test]
fn actual_bass_adaptive_path_has_initial_accepted_terminal_and_bound_six_arrays() {
    let case = "SIGNED_MINUS";
    let cfg = config("19.99999999", "");
    let out = scratch("complete").join("run");
    run_bass_fresh(&cfg, &out, case, bg(case), "component-check").unwrap();
    let t = check_counts(&out);
    assert_eq!(t["status"], "COMPLETE_REPRESENTED_INTERVAL");
    assert!(t["accepted"].parse::<usize>().unwrap() > 0);
    assert!(t["rhs_evaluations"].parse::<usize>().unwrap() > 0);
    let (d, _) = Driver::new_bass(DriverConfig::read(&cfg).unwrap(), bg(case)).unwrap();
    let state = d
        .read_bass_checkpoint(
            Path::new(&t["last_checkpoint"]),
            "component-check",
            &out.join("RUN_BINDING.txt"),
        )
        .unwrap();
    assert_eq!(state.a.to_string(), t["a"]);
    assert_eq!(state.accepted.to_string(), t["accepted"]);
    assert_eq!(state.rhs_evaluations.to_string(), t["rhs_evaluations"]);
    assert_eq!(
        d.geometry_point(state.a).unwrap().time_s.to_string(),
        t["time_s"]
    );
    let saved = fs::read_to_string(&t["last_checkpoint"]).unwrap();
    let (_, body) = saved.split_once("\nAXBI_CHECKPOINT_V4\n").unwrap();
    assert_eq!(body.lines().count(), 10);
    assert!(saved.contains("inactive_hi_split=true"));
    assert!(out.join("checkpoints/initial-00000000.bass-v1").is_file());
    assert!(fs::read_dir(out.join("checkpoints")).unwrap().count() >= 3);
    let mut off = DriverConfig::read(&cfg).unwrap();
    off.inactive_hi_split = false;
    let (off, _) = Driver::new_bass(off, bg(case)).unwrap();
    assert!(off
        .read_bass_checkpoint(
            Path::new(&t["last_checkpoint"]),
            "component-check",
            &out.join("RUN_BINDING.txt")
        )
        .is_err());
    assert!(d
        .read_bass_checkpoint(
            Path::new(&t["last_checkpoint"]),
            "wrong-epoch",
            &out.join("RUN_BINDING.txt")
        )
        .is_err());
    let binding = fs::read(out.join("RUN_BINDING.txt")).unwrap();
    assert!(run_bass_fresh(&cfg, &out, case, bg(case), "component-check").is_err());
    assert_eq!(fs::read(out.join("RUN_BINDING.txt")).unwrap(), binding);
}
#[test]
fn default_axbi_delegation_and_completed_resume_preserve_physics_and_row_counts() {
    let cfg =
        config("19.99999999", "").replace("inactive_hi_split=true", "inactive_hi_split=false");
    let parsed = DriverConfig::read(&cfg).unwrap();
    let (d, mut state) = Driver::new(parsed).unwrap();
    let end = 1.0 / (1.0 + 19.99999999);
    let direct_started = std::time::Instant::now();
    let mut direct_calls = 0usize;
    while state.a < end {
        assert!(direct_started.elapsed().as_secs_f64() <= 10.0);
        assert!(direct_calls < 64);
        direct_calls += 1;
        d.adaptive_step(&mut state).unwrap();
    }
    assert!(direct_started.elapsed().as_secs_f64() <= 10.0);
    fs::write(
        scratch("direct-reference").join("CALLS.txt"),
        format!(
            "actual_adaptive_step_calls={direct_calls}\nwall_s={}\n",
            direct_started.elapsed().as_secs_f64()
        ),
    )
    .unwrap();
    let out = scratch("axbi").join("run");
    run(&cfg, &out, "AXBI_CONTROL", false).unwrap();
    let before = rows(&out, "history.csv");
    let last = before.last().unwrap().split(',').collect::<Vec<_>>();
    assert_eq!(last[4].parse::<f64>().unwrap().to_bits(), state.a.to_bits());
    for j in 0..3 {
        assert_eq!(
            last[9 + j].parse::<f64>().unwrap().to_bits(),
            state.gas.fractions[j].to_bits()
        );
    }
    assert!(fs::read_to_string(out.join("checkpoint.txt"))
        .unwrap()
        .starts_with("AXBI_CHECKPOINT_V4\n"));
    run(&cfg, &out, "AXBI_CONTROL", true).unwrap();
    assert_eq!(rows(&out, "history.csv"), before);
}
#[test]
fn accepted_limit_keeps_last_valid_rows_full_checkpoint_and_charged_costs() {
    let cfg = config("19.99", "max_steps=1\n");
    let out = scratch("accepted-cap").join("run");
    assert!(run_bass_fresh(&cfg, &out, "SIGNED_MINUS", bg("SIGNED_MINUS"), "cap-epoch").is_err());
    let t = check_counts(&out);
    assert_eq!(t["status"], "STOPPED_CHECKPOINTED");
    assert_eq!(t["accepted"], "1");
    assert!(t["attempts"].parse::<usize>().unwrap() >= 3);
    let (d, _) = Driver::new_bass(DriverConfig::read(&cfg).unwrap(), bg("SIGNED_MINUS")).unwrap();
    let state = d
        .read_bass_checkpoint(
            Path::new(&t["last_checkpoint"]),
            "cap-epoch",
            &out.join("RUN_BINDING.txt"),
        )
        .unwrap();
    assert_eq!(state.rhs_evaluations.to_string(), t["rhs_evaluations"]);
    assert_eq!(
        state.a.to_string(),
        rows(&out, "history.csv")
            .last()
            .unwrap()
            .split(',')
            .nth(4)
            .unwrap()
    );
}
#[test]
fn rhs_failure_keeps_initial_physical_state_and_actual_failed_debits() {
    let cfg = config("19.99", "max_rhs=1\n");
    let out = scratch("rhs-cap").join("run");
    assert!(run_bass_fresh(&cfg, &out, "SIGNED_MINUS", bg("SIGNED_MINUS"), "rhs-epoch").is_err());
    let t = check_counts(&out);
    assert_eq!(t["accepted"], "0");
    assert_eq!(t["rhs_evaluations"], "1");
    assert_eq!(t["attempts"], "1");
    let (d, initial) =
        Driver::new_bass(DriverConfig::read(&cfg).unwrap(), bg("SIGNED_MINUS")).unwrap();
    let state = d
        .read_bass_checkpoint(
            Path::new(&t["last_checkpoint"]),
            "rhs-epoch",
            &out.join("RUN_BINDING.txt"),
        )
        .unwrap();
    assert_eq!(state.a, initial.a);
    assert_eq!(state.photons, initial.photons);
    assert_eq!(state.photon_energy_ref, initial.photon_energy_ref);
    assert_eq!(state.photon_support_lo, initial.photon_support_lo);
    assert_eq!(state.photon_support_hi, initial.photon_support_hi);
    assert_eq!(state.photon_inactive_number, initial.photon_inactive_number);
    assert_eq!(
        state.photon_inactive_energy_ref,
        initial.photon_inactive_energy_ref
    );
    assert_eq!(format!("{:?}", state.gas), format!("{:?}", initial.gas));
    assert_eq!(
        format!("{:?}", state.ledgers),
        format!("{:?}", initial.ledgers)
    );
}
#[test]
fn resume_cli_and_existing_legacy_checkpoint_directory_are_rejected() {
    let args = vec!["bass_adaptive_trial".into(), "--resume".into()];
    assert!(adaptive_cli::execute_args(&args)
        .unwrap_err()
        .to_string()
        .contains("FRESH_ONLY"));
    let out = scratch("legacy").join("run");
    fs::create_dir(&out).unwrap();
    let legacy = out.join("checkpoint.txt");
    fs::write(&legacy, "AXBI_CHECKPOINT_V4\nlegacy007008\n").unwrap();
    let original = fs::read(&legacy).unwrap();
    assert!(run_bass_fresh(
        &config("19.9999", ""),
        &out,
        "SIGNED_MINUS",
        bg("SIGNED_MINUS"),
        "fresh"
    )
    .is_err());
    assert_eq!(fs::read(&legacy).unwrap(), original);
    assert!(!out.join("RUN_BINDING.txt").exists());
}
