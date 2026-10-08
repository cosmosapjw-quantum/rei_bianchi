use canonical::{Ledger, Wide};
use ledger::{Allocator, Context, DiagnosticStore, FailAt, Snapshot, HOLD, SOURCE_PIN};
use native_detailed::{
    cr_off_igm_bridge::{CountPerH, CrMode, DeferredCrAccess, PointContext},
    igm_source_step::{
        trial_source_step, NewtonControl, SourceState, SourceStep, SourceTrial, StepAccuracy,
    },
    igm_state::IgmGasState,
    AtomicProvider, ForwardError,
};
use rei_ledger_real_caller::*;
use std::path::PathBuf;
struct Off;
impl DeferredCrAccess for Off {
    fn load(&mut self) -> Result<(), ForwardError> {
        panic!("CR must remain OFF")
    }
    fn source_callback(&mut self) -> Result<[f64; 4], ForwardError> {
        panic!("CR must remain OFF")
    }
}
fn ctx() -> PointContext {
    PointContext {
        n_h_cm3: 1e-4,
        n_he_cm3: 8.3e-6,
        hubble_s: 0.,
        t_cmb_k: 30.,
    }
}
fn fixture() -> SourceState {
    let c = ctx();
    SourceState {
        gas: IgmGasState::from_temperature([0.9, 0.3, 0.05], c.n_h_cm3, c.n_he_cm3, 1e4).unwrap(),
        photons: vec![CountPerH {
            energy_ev: 13.7,
            photons_per_h: 0.05,
        }],
    }
}
fn statebits(s: &SourceState) -> Vec<u64> {
    let mut out = s.gas.fractions.map(f64::to_bits).to_vec();
    out.push(s.gas.w_erg_per_h.to_bits());
    for n in &s.photons {
        out.extend([n.energy_ev.to_bits(), n.photons_per_h.to_bits()]);
    }
    out
}
fn stagebits(s: &SourceStep) -> Vec<u64> {
    let mut v = statebits(&s.state);
    let l = &s.ledger;
    for a in [&l.photo[..], &l.collision[..], &l.recombination[..]] {
        v.extend(a.iter().map(|x| x.to_bits()));
    }
    v.extend(
        [
            l.dielectronic,
            l.escape,
            l.cmb_to_gas,
            l.gas_work,
            l.injected_count,
            l.injected_energy,
            s.gas_residual_norm,
            s.photon_residual_norm,
        ]
        .map(f64::to_bits),
    );
    v.extend([s.iterations as u64, s.rhs_evaluations as u64]);
    v
}
fn trialbits(s: &SourceTrial) -> Vec<u64> {
    let mut v = stagebits(&s.full);
    v.extend(stagebits(&s.half1));
    v.extend(stagebits(&s.half2));
    v.push(s.error_norm.to_bits());
    v
}
fn clone_actual(t: &sidecar::DetailedTrial) -> sidecar::DetailedTrial {
    sidecar::DetailedTrial {
        legacy: t.legacy.clone(),
        stages: t.stages.clone(),
        counters: t.counters,
    }
}
fn fresh_local_root() -> PathBuf {
    let parent = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("evidence/local-real-runs");
    std::fs::create_dir_all(&parent).unwrap();
    for i in 0..1024 {
        let p = parent.join(format!("receiver-{i}"));
        match std::fs::create_dir(&p) {
            Ok(()) => return p,
            Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(e) => panic!("local test root: {e}"),
        }
    }
    panic!("local namespace allocation exhausted")
}
#[test]
fn real_native_trial_enters_opt_in_receiver_and_rolls_back() {
    let old = fixture();
    let before_old = statebits(&old);
    let src = [5e-15];
    let dt = 1e7;
    let provider = AtomicProvider::reference();
    // Exactly the source-fed normal fixture used by the accepted species slice.
    // These are the only two actual native solver trials in this added test.
    let detailed = sidecar::trial_detailed(
        CrMode::Off,
        &old,
        ctx(),
        &src,
        dt,
        &provider,
        NewtonControl::default(),
        StepAccuracy::default(),
        &mut Off,
    )
    .unwrap();
    let (reference, baseline_counts) = sidecar::count_only(|| {
        trial_source_step(
            CrMode::Off,
            &old,
            ctx(),
            &src,
            dt,
            &provider,
            NewtonControl::default(),
            StepAccuracy::default(),
            &mut Off,
        )
    })
    .unwrap();
    assert_eq!(trialbits(&detailed.legacy), trialbits(&reference));
    assert_eq!(detailed.counters, baseline_counts);
    let rhs = detailed.legacy.full.rhs_evaluations
        + detailed.legacy.half1.rhs_evaluations
        + detailed.legacy.half2.rhs_evaluations;
    assert_eq!(detailed.counters.point_calls, rhs);
    assert_eq!(
        detailed.counters.provider_calls,
        (rhs + 3) * 3 * old.photons.len()
    );
    assert!(rhs > 0);
    assert_eq!(
        detailed
            .stages
            .iter()
            .map(|s| s.dt_s.to_bits())
            .collect::<Vec<_>>(),
        vec![dt.to_bits(), (dt * 0.5).to_bits(), (dt * 0.5).to_bits()]
    );
    let expected_a: [sidecar::Bounded; 3] = std::array::from_fn(|i| {
        detailed.stages[1].count[i]
            .add(detailed.stages[2].count[i])
            .unwrap()
    });
    let expected_b: [sidecar::Bounded; 3] = std::array::from_fn(|i| {
        detailed.stages[1].absorbed_energy[i]
            .add(detailed.stages[2].absorbed_energy[i])
            .unwrap()
    });
    assert!(!detailed.stages[0].absorbed_energy[0].value.is_empty());
    assert_ne!(
        expected_b[0],
        expected_b[0]
            .add(detailed.stages[0].absorbed_energy[0])
            .unwrap()
    );
    let expected_accepted = reference.clone().accept().unwrap();
    let mut bits = vec![
        ctx().n_h_cm3.to_bits(),
        ctx().n_he_cm3.to_bits(),
        ctx().hubble_s.to_bits(),
        ctx().t_cmb_k.to_bits(),
    ];
    bits.extend(before_old.clone());
    bits.extend(src.map(f64::to_bits));
    bits.push(dt.to_bits());
    let context = Context {
        parent_checkpoint: "LOCAL_REAL_NATIVE_DIAGNOSTIC_FIXTURE_NOT_PHYSICAL_CHECKPOINT".into(),
        transition: 0,
        source_pin: SOURCE_PIN.into(),
        bits,
        total_dt_bits: dt.to_bits(),
    };
    let root = fresh_local_root();
    let namespace = format!(
        "LOCAL_TEST_ONLY/normal-source-fed-fixture/{}",
        root.display()
    );
    let allocator = Allocator::open(root.join("leases"), &namespace).unwrap();
    let initial = Snapshot::initial(Ledger::default(), before_old.clone(), &context).unwrap();
    let mut store = DiagnosticStore::open(root.join("store"), initial).unwrap();
    let before = store.snapshot().clone();
    let head = std::fs::read(root.join("store/HEAD")).unwrap();
    // Empty increment is an explicitly declared diagnostic control request; it is
    // not inferred from the six species owners or admitted as a physical update.
    let request = || DiagnosticRequest {
        context: context.clone(),
        original_increment: [Wide::ZERO; 11],
        original_private_gate: true,
    };
    assert!(receive_native_trial(
        DiagnosticOptIn::default(),
        clone_actual(&detailed),
        &allocator,
        &mut store,
        request(),
        FailAt::None
    )
    .unwrap_err()
    .contains("DISABLED"));
    assert_eq!(*store.snapshot(), before);
    assert_eq!(std::fs::read(root.join("store/HEAD")).unwrap(), head);
    let mut rejected = clone_actual(&detailed);
    rejected.legacy.error_norm = 2.;
    assert!(receive_native_trial(
        DiagnosticOptIn::Enabled,
        rejected,
        &allocator,
        &mut store,
        request(),
        FailAt::None
    )
    .is_err());
    assert_eq!(*store.snapshot(), before);
    assert!(receive_native_trial(
        DiagnosticOptIn::Enabled,
        clone_actual(&detailed),
        &allocator,
        &mut store,
        request(),
        FailAt::BeforePublish
    )
    .is_err());
    assert_eq!(*store.snapshot(), before);
    assert_eq!(std::fs::read(root.join("store/HEAD")).unwrap(), head);
    // Count around the added caller itself: acceptance/replay/publication must add
    // no provider call or native point/RHS evaluation to the already computed trial.
    let (receipt, caller_counts) = sidecar::count_only(|| {
        receive_native_trial(
            DiagnosticOptIn::Enabled,
            clone_actual(&detailed),
            &allocator,
            &mut store,
            request(),
            FailAt::None,
        )
        .map_err(|_| ForwardError::InvalidInput("DIAGNOSTIC_RECEIVER_FAILED"))
    })
    .unwrap();
    assert_eq!(caller_counts, sidecar::Counters::default());
    assert_eq!(receipt.additional_rhs_evaluations, 0);
    assert_eq!(receipt.observed_native_calls, detailed.counters);
    assert_eq!(trialbits(&receipt.legacy_trial), trialbits(&reference));
    assert_eq!(
        receipt.native.total_rhs_evaluations,
        expected_accepted.total_rhs_evaluations
    );
    assert_eq!(receipt.native.total_rhs_evaluations, rhs);
    assert_eq!(
        receipt.native.error_norm_bits,
        expected_accepted.error_norm.to_bits()
    );
    assert_eq!(
        receipt.native.accepted_stage_rhs,
        [
            reference.half1.rhs_evaluations,
            reference.half2.rhs_evaluations
        ]
    );
    assert_eq!(store.snapshot().state, statebits(&expected_accepted.state));
    assert_eq!(store.snapshot().a, expected_a);
    assert_eq!(store.snapshot().b, expected_b);
    assert_eq!(store.snapshot().generation, 1);
    assert_eq!(store.snapshot().witnesses.len(), 1);
    assert_eq!(receipt.publication.physical_admission, HOLD);
    assert!(store.publish_physical().is_err());
    assert_eq!(statebits(&old), before_old);
    let report=format!("{{\n  \"fixture\":\"prior_source_fed_normal_fixture\",\n  \"real_native_trials\":2,\n  \"detail_rhs\":{},\n  \"baseline_rhs\":{},\n  \"total_actual_rhs\":{},\n  \"detail_provider_calls\":{},\n  \"baseline_provider_calls\":{},\n  \"total_actual_provider_calls\":{},\n  \"added_caller_rhs\":{},\n  \"added_caller_provider_calls\":{},\n  \"legacy_bitwise_equal\":true,\n  \"accepted_half_owners_equal\":true,\n  \"full_stage_cost_included_owners_excluded\":true,\n  \"native_rejection_and_pre_publish_rollback\":true,\n  \"namespace_scope\":\"fresh_local_test_only\",\n  \"directory_synced\":{},\n  \"physical_admission\":\"HOLD\",\n  \"global_cross_host_namespace_proven\":false,\n  \"disk_only_restore_proven\":false\n}}\n",detailed.counters.point_calls,baseline_counts.point_calls,detailed.counters.point_calls+baseline_counts.point_calls,detailed.counters.provider_calls,baseline_counts.provider_calls,detailed.counters.provider_calls+baseline_counts.provider_calls,caller_counts.point_calls,caller_counts.provider_calls,receipt.publication.directory_synced);
    std::fs::write(root.join("REAL_NATIVE_RECEIVER_REPORT.json"), &report).unwrap();
    std::fs::write(
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("evidence/REAL_NATIVE_RECEIVER_REPORT.json"),
        &report,
    )
    .unwrap();
    println!("{report}");
}
