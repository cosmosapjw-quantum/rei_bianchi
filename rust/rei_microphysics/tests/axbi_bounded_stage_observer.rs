//! Synthetic changed-seam controls; no owner checkpoint, history, or telemetry.
use rei_microphysics::axbi_driver::{ChemicalStageObserver, Driver, DriverConfig, DriverState};
use rei_microphysics::ForwardError;
use std::{fs, path::Path, process::Command};

const PIN: &str = "eb2abcac4f44b7bc4ff532286953fcb4e353c7bb";
fn observer(packets: usize, rhs: usize) -> ChemicalStageObserver {
    ChemicalStageObserver::new_bounded_with_limits(
        "SYNTHETIC_CHANGED_SEAM", PIN, "LOCAL_FOCUSED_TEST_ONLY", packets, rhs,
    ).unwrap()
}
fn fixture() -> (Driver, DriverState) {
    let mut c = DriverConfig::baseline();
    c.end_zbar = 19.8;
    c.background_panels = 64;
    c.transport_cells = 8;
    c.transport_threads = 2;
    c.parallel_jacobian_columns = true;
    c.n_mu = 8;
    c.escape_fraction = 1e-20;
    c.initial_dln_a = 1e-10;
    Driver::new(c).unwrap()
}
fn failure() -> ForwardError { ForwardError::InvalidInput("SYNTHETIC_INJECTED_FAILURE") }

#[test]
fn disabled_parity_initial_residual_pass_and_actual_branch_capture() {
    let (driver, mut plain) = fixture();
    let mut measured = plain.clone();
    let mut obs = observer(6, 48);
    // The new policy must not reuse legacy diagnostic native-budget overrides.
    obs.native_rhs_ceiling = Some(0);
    let before = plain.rhs_evaluations;
    assert_eq!(driver.adaptive_step(&mut plain).unwrap(),
        driver.adaptive_step_observed(&mut measured, &mut obs).unwrap());
    assert_eq!(format!("{plain:?}"), format!("{measured:?}"));
    // Exactly one native R call per branch proves the initial residual passed.
    assert_eq!(plain.rhs_evaluations-before, 3);
    let packets = obs.bounded_packets().unwrap();
    assert_eq!(packets.len(), 3);
    assert_eq!(packets.iter().map(|p|p.branch).collect::<Vec<_>>(),
        vec!["FULL", "HALF_FIRST", "HALF_SECOND"]);
    for packet in packets {
        assert_eq!(packet.state, packet.old_state);
        assert_eq!(packet.adaptive_status, "ACCEPTED");
        assert!(packet.native_scaled_residual_inf <= 1e-11);
        assert!(packet.jacobian.is_some());
        assert_eq!(packet.added_rhs_attempts, 4);
        assert_eq!(packet.added_rhs_successes, 4);
        assert_eq!(packet.parent_step_id, 1);
    }
    assert_ne!(packets[0].context_id, packets[1].context_id);
    assert_eq!(obs.bounded_summary().unwrap().attempts, 12);
    assert!(obs.records.is_empty());
    assert!(obs.bounded_evaluations().unwrap().iter().all(|e|e.direction==1));
    let mut terminal=plain.clone();
    terminal.a=1.0/(1.0+driver.config.end_zbar);
    let count=obs.bounded_packets().unwrap().len();
    assert!(driver.adaptive_step_observed(&mut terminal,&mut obs).unwrap());
    assert_eq!(obs.bounded_packets().unwrap().len(),count);
}

#[test]
fn failed_plus_fallback_and_failed_jacobian_are_counted_and_finalized() {
    let mut obs = observer(6,48);
    let x = [0.2,0.1,0.1,0.02];
    obs.current_branch = "FIRST_HALF";
    obs.bounded_capture_control(x,[0.0;4],|y| {
        if y[0] > x[0] { Err(failure()) }
        else { Ok(std::array::from_fn(|i|y[i]-x[i])) }
    });
    obs.bounded_finalize_control(0,"REJECTED");
    let summary = obs.bounded_summary().unwrap();
    assert_eq!((summary.attempts,summary.successes),(5,4));
    let evaluations = obs.bounded_evaluations().unwrap();
    assert!(evaluations[0].outcome.starts_with("FAILED:"));
    assert_eq!(evaluations[1].direction,-1);
    assert_eq!(evaluations[1].column,0);
    assert!(obs.bounded_packets().unwrap()[0].jacobian.is_some());
    obs.current_branch = "SECOND_HALF";
    obs.bounded_capture_control(x,[0.0;4],|_|Err(failure()));
    obs.bounded_finalize_control(1,"ABORTED");
    let packets = obs.bounded_packets().unwrap();
    assert_eq!(packets[0].adaptive_status,"REJECTED");
    assert_eq!(packets[1].adaptive_status,"ABORTED");
    assert!(packets[1].jacobian.is_none());
    assert!(packets[1].unavailable_reason.as_ref().unwrap().contains("HOLD_"));
    assert_eq!(obs.bounded_summary().unwrap().attempts,7);
    assert_eq!(obs.bounded_summary().unwrap().successes,4);
}

#[test]
fn execution_wide_caps_include_failed_fallbacks_incomplete_slots_and_skips() {
    let mut obs = observer(999,999);
    let x = [0.2,0.1,0.1,0.02];
    let mut calls = 0;
    for comparison in 1..=10 {
        obs.current_comparison = comparison;
        obs.bounded_capture_control(x,[0.0;4],|y| {
            calls += 1;
            if calls%2==1 { Err(failure()) }
            else { Ok(std::array::from_fn(|i|y[i]-x[i])) }
        });
    }
    let summary=obs.bounded_summary().unwrap();
    assert_eq!((summary.packets,summary.attempts,summary.successes),(6,48,24));
    assert_eq!(calls,48);
    assert_eq!(summary.skipped_stages,4);
    assert_eq!(obs.bounded_evaluations().unwrap().len(),48);
    for (i,e) in obs.bounded_evaluations().unwrap().iter().enumerate() {
        assert_eq!(e.evaluation_id,i+1);
    }
    let mut exhausted=observer(3,2);
    for _ in 0..5 { exhausted.bounded_capture_control(x,[0.0;4],|y|Ok(y)); }
    let summary=exhausted.bounded_summary().unwrap();
    assert_eq!((summary.packets,summary.attempts,summary.cap_denied),(3,2,3));
    assert_eq!(summary.failed_packets,3);
    assert_eq!(summary.skipped_stages,2);
    assert!(exhausted.bounded_packets().unwrap().iter().all(|p|p.jacobian.is_none()));
}

#[test]
fn null_jacobian_never_changes_physics_and_abort_retains_prior_packets() {
    let (driver, mut plain) = fixture();
    let mut measured=plain.clone();
    let mut obs=observer(6,0);
    for _ in 0..3 {
        assert_eq!(driver.adaptive_step(&mut plain).unwrap(),
            driver.adaptive_step_observed(&mut measured,&mut obs).unwrap());
        assert_eq!(format!("{plain:?}"),format!("{measured:?}"));
    }
    assert_eq!(obs.bounded_summary().unwrap().packets,6);
    assert_eq!(obs.bounded_summary().unwrap().attempts,0);
    assert_eq!(obs.bounded_summary().unwrap().skipped_stages,3);
    assert!(obs.bounded_packets().unwrap().iter().all(|p|p.jacobian.is_none()));
    let (mut limited, mut plain)=fixture();
    limited.config.max_rhs=1;
    let mut measured=plain.clone();
    let mut obs=observer(6,48);
    assert!(limited.adaptive_step(&mut plain).is_err());
    assert!(limited.adaptive_step_observed(&mut measured,&mut obs).is_err());
    assert_eq!(format!("{plain:?}"),format!("{measured:?}"));
    let packets=obs.bounded_packets().unwrap();
    assert_eq!(packets.len(),1);
    assert_eq!(packets[0].branch,"FULL");
    assert_eq!(packets[0].adaptive_status,"ABORTED");
    assert_eq!(obs.bounded_summary().unwrap().attempts,4);
}

#[test]
fn finite_synthetic_flush_is_outer_once_fresh_and_adapter_binding_is_explicit() {
    let mut obs=observer(6,48);
    let x=[0.2,0.1,0.1,0.02];
    obs.current_branch="SECOND_HALF";
    obs.bounded_capture_control(x,[0.0;4],|y|Ok(std::array::from_fn(|i|y[i]-x[i])));
    obs.bounded_finalize_control(0,"ACCEPTED");
    obs.bounded_capture_control(x,[0.0;4],|_|Err(failure()));
    obs.bounded_finalize_control(1,"ABORTED");
    let unit=Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../research/flrw_native_bounded_observer_20261016");
    let out=unit.join(format!("synthetic_flush_{}",std::process::id()));
    assert!(!out.exists());
    obs.flush_bounded(&out).unwrap();
    assert!(obs.flush_bounded(&out).is_err());
    assert_eq!(fs::read_dir(&out).unwrap().count(),3);
    let result=Command::new("python3").arg(unit.join("tests/check_binding_and_flush.py"))
        .arg(&out).output().unwrap();
    assert!(result.status.success(),"{}",String::from_utf8_lossy(&result.stderr));
    println!("SYNTHETIC_CHANGED_SEAM_FLUSH={} {}",out.display(),String::from_utf8_lossy(&result.stdout));
}
