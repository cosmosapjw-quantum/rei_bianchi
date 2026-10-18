#[allow(dead_code)]
#[path = "../examples/axbi_resource_continuation.rs"]
mod wrapper;
use rei_microphysics::axbi_driver::*;
use std::{fs, path::PathBuf};
fn workspace(name: &str) -> PathBuf {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../research/axbi_goal_20261014/driver/full/post_cap_001/rust/fixtures")
        .join(format!("{name}-{}", std::process::id()));
    fs::create_dir_all(&root).unwrap();
    root
}
fn component() -> (Driver, DriverState) {
    let mut cfg = DriverConfig::baseline();
    cfg.end_zbar = 19.8;
    cfg.background_panels = 64;
    cfg.max_steps = 3;
    Driver::new(cfg).unwrap()
}
fn accept(driver: &Driver, state: &mut DriverState) {
    for _ in 0..30 {
        if driver.adaptive_step(state).unwrap() {
            return;
        }
    }
    panic!("manufactured fixture failed bounded accept");
}
#[test]
fn exact_resume_matches_uninterrupted_kernel_and_preserves_prefix() {
    let root = workspace("equivalence");
    let (driver, mut prefix) = component();
    accept(&driver, &mut prefix);
    prefix.wall_elapsed_s = 17.0;
    let checkpoint = root.join("prefix.txt");
    driver.save_checkpoint(&checkpoint, &prefix).unwrap();
    let original = fs::read(&checkpoint).unwrap();
    let mut uninterrupted = prefix.clone();
    accept(&driver, &mut uninterrupted);
    accept(&driver, &mut uninterrupted);
    let restored = driver.read_checkpoint(&checkpoint).unwrap();
    assert_eq!(format!("{prefix:?}"), format!("{restored:?}"));
    let segment = root.join("segment");
    let error = wrapper::run_segment(
        driver.clone(),
        restored,
        "manufactured fixture",
        &segment,
        "ZERO",
    )
    .unwrap_err();
    assert!(format!("{error:?}").contains("AXBI_RUNTIME_CAP"));
    let mut resumed = driver
        .read_checkpoint(&segment.join("checkpoint.txt"))
        .unwrap();
    assert!(resumed.wall_elapsed_s >= 17.0);
    resumed.wall_elapsed_s = uninterrupted.wall_elapsed_s;
    // Includes gas, every photon, every ledger, step policy and cumulative counters.
    assert_eq!(format!("{uninterrupted:?}"), format!("{resumed:?}"));
    assert_eq!(fs::read(&checkpoint).unwrap(), original);
    let history = fs::read_to_string(segment.join("history.csv")).unwrap();
    assert_eq!(history.lines().count(), 4); // header + shared boundary + two new rows
    let boundary = history
        .lines()
        .nth(1)
        .unwrap()
        .split(',')
        .nth(4)
        .unwrap()
        .parse::<f64>()
        .unwrap();
    assert_eq!(boundary, prefix.a);
    assert!(fs::read_to_string(segment.join("RETURN.txt"))
        .unwrap()
        .contains("STOPPED_CHECKPOINTED"));
    assert!(wrapper::run_segment(driver, prefix, "fixture", &segment, "ZERO").is_err());
}
#[test]
fn identity_checks_reject_wrong_config_checkpoint_case_terminal_and_source() {
    let root = workspace("identity");
    let prefix = root.join("prefix");
    fs::create_dir(&prefix).unwrap();
    fs::write(prefix.join("config.cfg"), "fixture").unwrap();
    fs::write(prefix.join("checkpoint.txt"), "checkpoint").unwrap();
    fs::write(prefix.join("RETURN.txt"), "terminal").unwrap();
    fs::write(prefix.join("case_id.txt"), "ZERO").unwrap();
    fs::write(prefix.join("source_identity.txt"), compiled_identity()).unwrap();
    let config = wrapper::sha256(&prefix.join("config.cfg")).unwrap();
    let checkpoint = wrapper::sha256(&prefix.join("checkpoint.txt")).unwrap();
    let terminal = wrapper::sha256(&prefix.join("RETURN.txt")).unwrap();
    let source = wrapper::sha256(&prefix.join("source_identity.txt")).unwrap();
    let expected = wrapper::Expected {
        config: &config,
        checkpoint: &checkpoint,
        terminal: &terminal,
        source: &source,
    };
    let out = root.join("segment");
    let cfg = prefix.join("config.cfg");
    assert!(wrapper::verify_predecessor(&cfg, &prefix, &out, "ZERO", &expected).is_ok());
    assert!(wrapper::verify_predecessor(&cfg, &prefix, &out, "SHEAR_PLUS", &expected).is_err());
    fs::write(prefix.join("case_id.txt"), "OTHER").unwrap();
    assert!(wrapper::verify_predecessor(&cfg, &prefix, &out, "ZERO", &expected).is_err());
    fs::write(prefix.join("case_id.txt"), "ZERO").unwrap();
    for name in [
        "config.cfg",
        "checkpoint.txt",
        "RETURN.txt",
        "source_identity.txt",
    ] {
        let path = prefix.join(name);
        let saved = fs::read(&path).unwrap();
        fs::write(&path, "wrong predecessor").unwrap();
        assert!(
            wrapper::verify_predecessor(&cfg, &prefix, &out, "ZERO", &expected).is_err(),
            "{name}"
        );
        fs::write(path, saved).unwrap();
    }
    fs::create_dir(&out).unwrap();
    assert!(wrapper::verify_predecessor(&cfg, &prefix, &out, "ZERO", &expected).is_err());
}
#[test]
fn cumulative_caps_and_output_failure_rollback_keep_charged_costs() {
    let (mut driver, mut state) = component();
    for cap in 0..4 {
        let mut limited = state.clone();
        match cap {
            0 => limited.accepted = driver.config.max_steps,
            1 => limited.attempts = driver.config.max_attempts,
            2 => limited.rhs_evaluations = driver.config.max_rhs,
            _ => limited.wall_elapsed_s = driver.config.max_wall_s,
        };
        assert!(wrapper::resource_cap(&driver, &limited));
    }
    let previous = state.clone();
    accept(&driver, &mut state);
    let charged = state.clone();
    let root = workspace("outputcap");
    fs::File::create(root.join("large"))
        .unwrap()
        .set_len(224 * 1024 * 1024)
        .unwrap();
    let (mut h, mut a, mut p, mut l, mut f) =
        (Vec::new(), Vec::new(), Vec::new(), Vec::new(), Vec::new());
    let failure = driver
        .output_batch(
            &state, "ZERO", &root, true, &mut h, &mut a, &mut p, &mut l, &mut f,
        )
        .unwrap_err();
    assert!(format!("{failure:?}").contains("AXBI_OUTPUT_CAP"));
    assert!(h.is_empty() && a.is_empty() && p.is_empty() && l.is_empty() && f.is_empty());
    wrapper::rollback_charged(&mut state, previous.clone());
    assert_eq!(state.a, previous.a);
    assert_eq!(state.photons, previous.photons);
    assert_eq!(state.accepted, previous.accepted);
    assert_eq!(state.attempts, charged.attempts);
    assert_eq!(state.rhs_evaluations, charged.rhs_evaluations);
    assert_eq!(state.comparisons, charged.comparisons);
    assert_eq!(state.rejects, charged.rejects);
    driver.config.max_attempts = state.attempts;
    assert!(driver.adaptive_step(&mut state).is_err());
}
