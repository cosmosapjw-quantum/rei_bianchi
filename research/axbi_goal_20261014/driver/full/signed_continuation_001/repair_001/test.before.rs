#[allow(dead_code)]
#[path = "../examples/axbi_signed_resource_continuation.rs"]
mod wrapper;
use rei_microphysics::axbi_driver::*;
use std::{fs, path::PathBuf};
fn workspace(name: &str) -> PathBuf {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../research/axbi_goal_20261014/driver/full/signed_continuation_001/fixtures")
        .join(format!("{name}-{}", std::process::id()));
    fs::create_dir_all(&root).unwrap();
    root
}
fn component() -> (Driver, DriverState) {
    component_q(-0.01)
}
fn component_q(q: f64) -> (Driver, DriverState) {
    let mut cfg = DriverConfig::baseline();
    cfg.q_ref = q;
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
    for (case, q) in [
        ("SHEAR_MINUS", -0.01),
        ("SHEAR_HALF_PLUS", 0.005),
        ("SHEAR_HALF_MINUS", -0.005),
    ] {
        let root = workspace(case);
        let (driver, mut prefix) = component_q(q);
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
            case,
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
        let (mut h, mut a, mut p, mut l, mut fb) =
            (Vec::new(), Vec::new(), Vec::new(), Vec::new(), Vec::new());
        driver
            .output_row(&prefix, case, &mut h, &mut a, &mut p, &mut l, &mut fb)
            .unwrap();
        for (name, expected) in [
            ("history.csv", h),
            ("abundances.csv", a),
            ("spectra.csv", p),
            ("ledgers.csv", l),
            ("feedback.csv", fb),
        ] {
            let text = fs::read_to_string(segment.join(name)).unwrap();
            assert!(
                text.split_once('\n')
                    .unwrap()
                    .1
                    .starts_with(std::str::from_utf8(&expected).unwrap()),
                "{name} boundary parity"
            );
        }
        let terminal = fs::read_to_string(segment.join("RETURN.txt")).unwrap();
        assert!(terminal.contains(&format!("segment_id={case}_RESOURCE_CONTINUATION_001")));
        assert!(terminal.contains("starting_wall_s=17"));
        assert!(terminal.contains("segment_accepted=2"));
        assert!(fs::read_to_string(segment.join("RETURN.txt"))
            .unwrap()
            .contains("STOPPED_CHECKPOINTED"));
        assert!(wrapper::run_segment(driver, prefix, "fixture", &segment, case).is_err());
    }
}
#[test]
fn strict_templates_and_authority_reject_without_output() {
    for case in ["SHEAR_MINUS", "SHEAR_HALF_PLUS", "SHEAR_HALF_MINUS"] {
        let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../../research/axbi_goal_20261014/driver/full/signed_continuation_001")
            .join(format!("{case}.binding.template"));
        let text = fs::read_to_string(path).unwrap();
        let b = wrapper::parse_binding(&text).unwrap();
        assert!(wrapper::execution_gate(&b).is_err());
        assert!(wrapper::parse_binding(&(text.clone() + "case=ZERO\n")).is_err());
        assert!(wrapper::parse_binding(&(text + "unknown=value\n")).is_err());
        let mut changed = b.clone();
        changed.insert("case".into(), "ZERO".into());
        assert!(wrapper::execution_gate(&changed).is_err());
        changed.insert("execution_authorized".into(), "true".into());
        changed.insert("start_authorized".into(), "true".into());
        assert!(wrapper::execution_gate(&changed).is_err());
        changed = b;
        changed.insert("current_source_sha256".into(), wrapper::OLD.into());
        assert!(wrapper::execution_gate(&changed).is_err());
    }
    let root = workspace("authority");
    let authority = root.join("authority.binding");
    fs::write(&authority, "execution_authorized=true\ncase=SHEAR_MINUS\n").unwrap();
    let mut b =
        wrapper::parse_binding("execution_authorized=true\ncase=SHEAR_HALF_PLUS\n").unwrap();
    b.insert("authority".into(), authority.to_str().unwrap().into());
    b.insert(
        "authority_sha256".into(),
        wrapper::sha256(&authority).unwrap(),
    );
    assert!(wrapper::verify_authority(&b).is_err());
    b.insert("authority_sha256".into(), "0".repeat(64));
    assert!(wrapper::verify_authority(&b).is_err());
}
#[test]
fn resource_changes_are_checked_and_rhs_ceiling_retained() {
    let mut cfg = DriverConfig::baseline();
    let text=format!("additional_steps=1\nadditional_attempts=3\nadditional_wall_s=10\nadditional_output_mib=1792\neffective_max_steps={}\neffective_max_attempts={}\neffective_max_wall_s={}\neffective_output_budget_mib=2048\neffective_max_rhs={}\n",cfg.max_steps+1,cfg.max_attempts+3,cfg.max_wall_s+10.,cfg.max_rhs);
    let b = wrapper::parse_binding(&text).unwrap();
    wrapper::apply_caps(&mut cfg, &b).unwrap();
    let mut bad = b.clone();
    bad.insert("effective_max_rhs".into(), "99999999".into());
    assert!(wrapper::apply_caps(&mut DriverConfig::baseline(), &bad).is_err());
    bad = b;
    bad.insert("additional_wall_s".into(), "NaN".into());
    assert!(wrapper::apply_caps(&mut DriverConfig::baseline(), &bad).is_err());
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
            &state,
            "SHEAR_MINUS",
            &root,
            true,
            &mut h,
            &mut a,
            &mut p,
            &mut l,
            &mut f,
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

#[test]
fn exact_endpoint_is_required_and_resource_wall_is_carried() {
    let root = workspace("endpoint");
    let (mut driver, mut state) = component();
    state.wall_elapsed_s = 17.0;
    driver.config.max_wall_s = 17.0;
    let out = root.join("wallcap");
    assert!(wrapper::run_segment(
        driver.clone(),
        state.clone(),
        "fixture",
        &out,
        "SHEAR_MINUS"
    )
    .is_err());
    let saved = driver.read_checkpoint(&out.join("checkpoint.txt")).unwrap();
    assert_eq!(saved.accepted, state.accepted);
    assert!(saved.wall_elapsed_s >= 17.0);
    driver.config.max_wall_s = 1000.0;
    driver.config.end_zbar = 1.0 / state.a - 1.0;
    let endpoint = 1.0 / (1.0 + driver.config.end_zbar);
    assert_eq!(state.a, endpoint);
    let out = root.join("endpoint");
    wrapper::run_segment(driver, state, "fixture", &out, "SHEAR_MINUS").unwrap();
    assert!(fs::read_to_string(out.join("RETURN.txt"))
        .unwrap()
        .contains("COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT"));
}
