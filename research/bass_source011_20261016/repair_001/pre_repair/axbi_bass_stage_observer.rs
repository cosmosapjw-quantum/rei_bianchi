use rei_microphysics::axbi_bass_background::{BassBackground, BassSourceIdentity};
use rei_microphysics::axbi_driver::{ChemicalStageObserver, Driver, DriverConfig};
use std::{
    fs,
    path::{Path, PathBuf},
};
fn repo() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}
fn driver() -> Driver {
    let root = repo();
    let bg = BassBackground::from_files(
        &root.join("research/bass_source007_20261016/inputs/pr164_121.csv"),
        &root.join("research/bass_source007_20261016/inputs/pr164_121.json"),
        BassSourceIdentity {
            producer_commit: "3c39bbbf46b6663e7c40277e194fd0ef48118472".into(),
            source_csv_sha256: "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133"
                .into(),
            source_manifest_sha256:
                "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed".into(),
            case: "SIGNED_MINUS".into(),
            grid_points: 121,
        },
    )
    .unwrap();
    Driver::new_bass(
        DriverConfig::read(
            &fs::read_to_string(root.join("research/bass_source011_20261016/inputs/config.cfg"))
                .unwrap(),
        )
        .unwrap(),
        bg,
    )
    .unwrap()
    .0
}
#[test]
fn observer_parity_context_and_separate_costs() {
    let d = driver();
    let input = repo().join("research/bass_source011_20261016/inputs");
    let mut a = d
        .read_source011_probe_checkpoint(
            &input.join("accepted-00039600.bass-v1"),
            &input.join("RUN_BINDING.txt"),
        )
        .unwrap();
    let mut b = a.clone();
    let mut obs = ChemicalStageObserver::new(1024);
    assert_eq!(
        d.adaptive_step(&mut a).unwrap(),
        d.adaptive_step_observed(&mut b, &mut obs).unwrap()
    );
    assert_eq!(
        d.source011_state_text(&a).unwrap(),
        d.source011_state_text(&b).unwrap()
    );
    assert_eq!(obs.records.len(), 3);
    assert!(obs.rhs_evaluations >= 12);
    for r in &obs.records {
        assert_eq!(r.adaptive_status, "ADAPTIVE_ACCEPTED");
        assert_eq!(r.jacobian.len(), 4);
        assert!(r.residual.iter().all(|x| x.is_finite()));
        assert!(r.added_rhs >= 4)
    }
}
#[test]
fn observer_cap_failure_retains_actual_debits_without_physical_commit() {
    let d = driver();
    let input = repo().join("research/bass_source011_20261016/inputs");
    let mut s = d
        .read_source011_probe_checkpoint(
            &input.join("accepted-00039600.bass-v1"),
            &input.join("RUN_BINDING.txt"),
        )
        .unwrap();
    let old = s.clone();
    let mut obs = ChemicalStageObserver::new(2);
    assert!(d.adaptive_step_observed(&mut s, &mut obs).is_err());
    assert_eq!(obs.rhs_evaluations, 2);
    assert!(obs.failure.is_some());
    assert_eq!(s.a, old.a);
    assert_eq!(s.gas.fractions, old.gas.fractions);
    assert_eq!(s.gas.w_erg_per_h, old.gas.w_erg_per_h);
    assert_eq!(format!("{:?}", s.ledgers), format!("{:?}", old.ledgers));
    assert_eq!(s.photon_energy_ref, old.photon_energy_ref);
    assert_eq!(s.photon_support_lo, old.photon_support_lo);
    assert_eq!(s.photon_support_hi, old.photon_support_hi);
    assert_eq!(s.photon_inactive_number, old.photon_inactive_number);
    assert_eq!(s.photon_inactive_energy_ref, old.photon_inactive_energy_ref);
    assert_eq!(s.photons, old.photons);
    assert!(s.rhs_evaluations > old.rhs_evaluations);
    assert_eq!(s.attempts, old.attempts + 1);
}
#[test]
fn bridge_pinned_inputs_and_production_source_rejection() {
    let d = driver();
    let input = repo().join("research/bass_source011_20261016/inputs");
    let cp = input.join("accepted-00039600.bass-v1");
    assert!(d
        .read_bass_checkpoint(
            &cp,
            "source010-half-target-001-SIGNED_MINUS",
            &input.join("RUN_BINDING.txt")
        )
        .is_err());
    assert!(d
        .read_source011_probe_checkpoint(&cp, &input.join("config.cfg"))
        .is_err());
    let scratch = repo().join("research/bass_source011_20261016/raw/wrong-checkpoint");
    fs::write(&scratch, "AXBI_CHECKPOINT_V4\n").unwrap();
    assert!(d
        .read_source011_probe_checkpoint(&scratch, &input.join("RUN_BINDING.txt"))
        .is_err());
    let mut cfg = d.config.clone();
    cfg.local_target *= 2.0;
    let mut wrong = d.clone();
    wrong.config = cfg;
    assert!(wrong
        .read_source011_probe_checkpoint(&cp, &input.join("RUN_BINDING.txt"))
        .is_err());
}
