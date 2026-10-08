use canonical::{Charge, Ledger, Wide};
use rei_ledger_admission::*;
use std::{
    path::PathBuf,
    sync::atomic::{AtomicUsize, Ordering},
};
static SEQ: AtomicUsize = AtomicUsize::new(0);
fn dir() -> PathBuf {
    loop {
        let p = std::env::temp_dir().join(format!(
            "rei-ledger-test-{}-{}",
            std::process::id(),
            SEQ.fetch_add(1, Ordering::SeqCst)
        ));
        match std::fs::create_dir(&p) {
            Ok(()) => return p,
            Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(e) => panic!("temporary fixture: {e}"),
        }
    }
}

fn w(v: f64) -> Wide {
    Wide::from_f64(v).unwrap()
}
fn context() -> Context {
    Context {
        parent_checkpoint: "accepted-control-checkpoint".into(),
        transition: 0,
        source_pin: SOURCE_PIN.into(),
        bits: vec![
            1e-4f64.to_bits(),
            8.3e-6f64.to_bits(),
            0f64.to_bits(),
            30f64.to_bits(),
        ],
        total_dt_bits: 1f64.to_bits(),
    }
}
fn events(rate: f64) -> Vec<Event> {
    vec![
        Event {
            node: 0,
            species: Species::HI,
            rate,
            energy_ev: 13.7,
            epsilon: canonical::EPS,
        },
        Event {
            node: 0,
            species: Species::HeI,
            rate: 0.,
            energy_ev: 13.7,
            epsilon: canonical::EPS,
        },
        Event {
            node: 0,
            species: Species::HeII,
            rate: 0.,
            energy_ev: 13.7,
            epsilon: canonical::EPS,
        },
    ]
}
fn stages(c: &Context) -> [SealedStage; 2] {
    [
        SealedStage::capture(c.clone(), Stage::Half1, 1, 0.5, events(1e-18)).unwrap(),
        SealedStage::capture(c.clone(), Stage::Half2, 2, 0.5, events(1e-50)).unwrap(),
    ]
}
fn setup(history: Ledger) -> (PathBuf, Allocator, DiagnosticStore, Context) {
    let d = dir();
    let a = Allocator::open(
        d.join("leases"),
        "parent-thread:01a110e6-7e1b-76e9-962b-8a127a814027/ledger-test-branch",
    )
    .unwrap();
    let c = context();
    let s = Snapshot::initial(history, vec![0x1234], &c).unwrap();
    let store = DiagnosticStore::open(d.join("store"), s).unwrap();
    (d, a, store, c)
}
fn proposal(a: &Allocator, s: &DiagnosticStore, c: &Context) -> Proposal {
    Proposal::new(
        a.reserve().unwrap(),
        c.clone(),
        s.snapshot().generation,
        stages(c),
        vec![0x5678],
        [Wide::ZERO; 11],
        true,
        false,
    )
    .unwrap()
}
fn cleanup(d: PathBuf) {
    std::fs::remove_dir_all(d).unwrap()
}
fn historical(v: f64, term: usize) -> Ledger {
    let mut l = Ledger::default();
    l.charge(Charge {
        lane: "accepted-history".into(),
        transition: 0,
        boundary: "already-owned".into(),
        id: "historic-one".into(),
        term,
        bound: w(v),
        coefficient: w(1.),
        units: if term == 0 { "photons/H" } else { "erg/H" },
    })
    .unwrap();
    l
}
#[test]
fn global_identity_replay_coefficients_zero_and_species() {
    let (d, a, s, c) = setup(Ledger::default());
    let p = proposal(&a, &s, &c);
    let q = proposal(&a, &s, &c);
    let mut reg = Registry::default();
    let zero = p.leaves.iter().find(|x| x.raw.is_empty()).unwrap().clone();
    reg.bind(&zero).unwrap();
    assert!(reg.bind(&zero).is_err());
    let positive = p.leaves.iter().find(|x| !x.raw.is_empty()).unwrap().clone();
    reg.bind(&positive).unwrap();
    let mut changed = positive.clone();
    changed.coefficient = w(2.);
    assert!(reg
        .bind(&changed)
        .unwrap_err()
        .contains("conflicting coefficient"));
    assert_ne!(p.leaves[0].edge, q.leaves[0].edge);
    let hi = p
        .leaves
        .iter()
        .find(|x| x.owner == Owner::A(Species::HI))
        .unwrap();
    let he = p
        .leaves
        .iter()
        .find(|x| x.owner == Owner::A(Species::HeI))
        .unwrap();
    assert_ne!(hi.edge, he.edge);
    let h1 = p.leaves.iter().find(|x| x.edge.contains("Half1")).unwrap();
    let h2 = p.leaves.iter().find(|x| x.edge.contains("Half2")).unwrap();
    assert_ne!(h1.edge, h2.edge);
    cleanup(d)
}
#[test]
fn durable_attempts_restart_branch_and_stale_snapshot() {
    let (d, a, mut s, c) = setup(Ledger::default());
    let stale = s.snapshot().clone();
    let p = proposal(&a, &s, &c);
    let identity = p.leaves[0].edge.clone();
    s.apply(&p, FailAt::None).unwrap();
    assert_eq!(s.snapshot().witnesses.len(), 1);
    let restored = s.snapshot().clone();
    assert!(DiagnosticStore::open(d.join("store"), stale).is_err());
    let restarted = Allocator::open(
        d.join("leases"),
        "parent-thread:01a110e6-7e1b-76e9-962b-8a127a814027/ledger-test-branch",
    )
    .unwrap();
    let t = DiagnosticStore::open(d.join("store"), restored).unwrap();
    let q = proposal(&restarted, &t, &c);
    assert_ne!(identity, q.leaves[0].edge);
    let other = Allocator::open(
        d.join("other"),
        "parent-thread:01a110e6-7e1b-76e9-962b-8a127a814027/other-parent-issued-branch",
    )
    .unwrap();
    let o = proposal(&other, &t, &c);
    assert_ne!(q.leaves[0].edge, o.leaves[0].edge);
    assert!(Allocator::open(d.join("leases"), "different-branch").is_err());
    assert!(s.apply(&p, FailAt::None).is_err());
    cleanup(d)
}
#[test]
fn dimensional_mapping_named_terms_dt_epsilon_once() {
    assert_eq!(Owner::A(Species::HI).term(), 7);
    assert_eq!(Owner::A(Species::HeII).term(), 9);
    assert_eq!(Owner::B(Species::HI).term(), 10);
    assert_eq!(Owner::B(Species::HeII).term(), 12);
    assert!(conversion(Unit::PhotonsPerH, Conversion::ProperDt).is_err());
    assert!(conversion(Unit::ErgPerHSecond, Conversion::Epsilon).is_err());
    assert!(conversion(Unit::PhotonsPerHSecond, Conversion::Epsilon).is_err());
    let (d, a, mut s, c) = setup(Ledger::default());
    let p = proposal(&a, &s, &c);
    let v = p.b[0].readout().unwrap().value;
    let expected = (1e-18 * 0.5 + 1e-50 * 0.5) * 13.7 * canonical::EPS;
    assert!((v / expected - 1.).abs() < 1e-14);
    assert!(p.b[1].value.is_empty() && p.b[2].value.is_empty());
    let mut bad = p.clone();
    bad.leaves[0].output = Unit::ErgPerH;
    assert!(s.apply(&bad, FailAt::None).is_err());
    let mut extra = p.clone();
    extra.b[0] = extra.b[0].scale(1e-4).unwrap();
    assert!(s.apply(&extra, FailAt::None).is_err());
    let mut split = p.clone();
    split.b.swap(0, 1);
    assert!(s.apply(&split, FailAt::None).is_err());
    cleanup(d)
}
#[test]
fn leaf_coverage_historical_fresh_and_no_double_charge() {
    let hist = historical(1e-22, 0);
    let old = hist.charges()[0].clone();
    let (d, a, mut s, c) = setup(hist);
    let p = proposal(&a, &s, &c);
    assert!(p
        .leaves
        .iter()
        .any(|x| x.category == Category::FreshSwallowed
            && x.edge.contains("AcceptedHalfAdd")
            && !x.raw.is_empty()));
    let mut missing = p.clone();
    missing.leaves.pop();
    assert!(s.apply(&missing, FailAt::None).is_err());
    let mut doubled = p.clone();
    doubled.leaves.push(doubled.leaves[0].clone());
    assert!(s.apply(&doubled, FailAt::None).is_err());
    let mut cat = p.clone();
    cat.leaves[0].category = Category::ReadoutQuantization;
    assert!(s.apply(&cat, FailAt::None).is_err());
    s.apply(&p, FailAt::None).unwrap();
    assert_eq!(s.snapshot().ledger.charges()[0], old);
    let expected = p
        .leaves
        .iter()
        .filter(|x| {
            matches!(
                x.category,
                Category::FreshSwallowed | Category::ReadoutQuantization
            ) && !x.raw.is_empty()
        })
        .count();
    assert_eq!(s.snapshot().ledger.charges().len(), 1 + expected);
    assert_eq!(s.snapshot().registry.len(), p.leaves.len());
    cleanup(d)
}
#[test]
fn accepted_half_order_full_exclusion_wrong_dt_and_missing_add() {
    let (d, a, s, c) = setup(Ledger::default());
    let h = stages(&c);
    assert!(Proposal::new(
        a.reserve().unwrap(),
        c.clone(),
        0,
        [h[1].clone(), h[0].clone()],
        vec![1],
        [Wide::ZERO; 11],
        true,
        false
    )
    .is_err());
    let full = SealedStage::capture(c.clone(), Stage::FullCostOnly, 3, 1., events(1e-18)).unwrap();
    assert!(Proposal::new(
        a.reserve().unwrap(),
        c.clone(),
        0,
        [full, h[1].clone()],
        vec![1],
        [Wide::ZERO; 11],
        true,
        false
    )
    .is_err());
    assert!(SealedStage::capture(c.clone(), Stage::Half1, 1, 1., events(1e-18)).is_err());
    let mut p = proposal(&a, &s, &c);
    p.leaves.retain(|x| !x.edge.contains("AcceptedHalfAdd"));
    let mut store = s;
    assert!(store.apply(&p, FailAt::None).is_err());
    cleanup(d)
}
#[test]
fn atomic_rollback_all_objects_disk_gate_and_burned_attempts() {
    let (d, a, mut s, c) = setup(historical(1e-22, 0));
    let before = s.snapshot().clone();
    let disk = std::fs::read(d.join("store/HEAD")).unwrap();
    let mut previous = None;
    for fail in [
        FailAt::BeforeWitness,
        FailAt::AfterRegistry,
        FailAt::AfterCanonicalCommit,
        FailAt::BeforePublish,
    ] {
        let p = proposal(&a, &s, &c);
        if let Some(v) = previous {
            assert_ne!(v, p.leaves[0].edge)
        }
        previous = Some(p.leaves[0].edge.clone());
        assert!(s.apply(&p, fail).is_err());
        assert_eq!(*s.snapshot(), before);
        assert_eq!(std::fs::read(d.join("store/HEAD")).unwrap(), disk)
    }
    let mut p = proposal(&a, &s, &c);
    p.original_private_gate = false;
    assert!(s.apply(&p, FailAt::None).is_err());
    assert_eq!(*s.snapshot(), before);
    let mut p = proposal(&a, &s, &c);
    p.leaves[0].coefficient = Wide::ZERO;
    assert!(s.apply(&p, FailAt::None).is_err());
    assert_eq!(*s.snapshot(), before);
    cleanup(d)
}
#[test]
fn original_caps_cumulative_history_and_four_increment_limit() {
    for (term, below, above) in [(0, 1e-21, 2e-20), (1, 1e-31, 2e-30)] {
        let (d, a, mut s, c) = setup(historical(below, term));
        s.apply(&proposal(&a, &s, &c), FailAt::None).unwrap();
        cleanup(d);
        let (d, a, mut s, c) = setup(historical(above, term));
        let before = s.snapshot().clone();
        assert!(s.apply(&proposal(&a, &s, &c), FailAt::None).is_err());
        assert_eq!(*s.snapshot(), before);
        cleanup(d)
    }
    let (d, a, mut s, c) = setup(Ledger::default());
    for _ in 0..4 {
        s.apply(&proposal(&a, &s, &c), FailAt::None).unwrap();
    }
    let before = s.snapshot().clone();
    assert!(s.apply(&proposal(&a, &s, &c), FailAt::None).is_err());
    assert_eq!(*s.snapshot(), before);
    cleanup(d)
}
#[test]
fn original_cap_boundary_matches_unmodified_authority() {
    for (term, cap) in [(0, 1e-20f64), (1, 1e-30f64)] {
        for raw in [cap.next_down(), cap, cap.next_up()] {
            let history = historical(raw, term);
            let (d, a, mut s, c) = setup(history.clone());
            let p = proposal(&a, &s, &c);
            let mut reference = history;
            let fresh: Vec<_> = p
                .leaves
                .iter()
                .filter(|x| {
                    matches!(
                        x.category,
                        Category::FreshSwallowed | Category::ReadoutQuantization
                    )
                })
                .map(|x| Charge {
                    lane: "reference".into(),
                    transition: 0,
                    boundary: "fresh".into(),
                    id: x.edge.clone(),
                    term: x.owner.term(),
                    bound: x.raw,
                    coefficient: x.coefficient,
                    units: if matches!(x.owner, Owner::A(_)) {
                        "photons/H"
                    } else {
                        "erg/H"
                    },
                })
                .collect();
            let expected = reference.commit([Wide::ZERO; 11], fresh, true).is_ok();
            assert_eq!(s.apply(&p, FailAt::None).is_ok(), expected);
            cleanup(d)
        }
    }
}
#[test]
fn unknowns_hold_even_complete_bookkeeping_and_source_context_errors() {
    let (d, a, mut s, c) = setup(Ledger::default());
    let p = proposal(&a, &s, &c);
    let out = s.apply(&p, FailAt::None).unwrap();
    assert_eq!(out.physical_admission, HOLD);
    assert_eq!(s.snapshot().hold, HOLD);
    assert!(s.publish_physical().is_err());
    let mut bad = c.clone();
    bad.source_pin.clear();
    assert!(SealedStage::capture(bad, Stage::Half1, 1, 0.5, events(1e-18)).is_err());
    let mut wrong = c.clone();
    wrong.parent_checkpoint = "different".into();
    let p = Proposal::new(
        a.reserve().unwrap(),
        wrong.clone(),
        s.snapshot().generation,
        stages(&wrong),
        vec![1],
        [Wide::ZERO; 11],
        true,
        false,
    )
    .unwrap();
    assert!(s.apply(&p, FailAt::None).is_err());
    cleanup(d)
}
#[test]
fn performed_export_only_positive_tail_zero_and_overflow() {
    let (d, a, s, c) = setup(Ledger::default());
    let no = proposal(&a, &s, &c);
    assert!(!no
        .leaves
        .iter()
        .any(|x| x.category == Category::ReadoutQuantization));
    let yes = Proposal::new(
        a.reserve().unwrap(),
        c.clone(),
        0,
        stages(&c),
        vec![1],
        [Wide::ZERO; 11],
        true,
        true,
    )
    .unwrap();
    assert_eq!(
        yes.leaves
            .iter()
            .filter(|x| x.category == Category::ReadoutQuantization)
            .count(),
        6
    );
    let tiny = sidecar::Bounded::exact(f64::MIN_POSITIVE)
        .unwrap()
        .scale(f64::MIN_POSITIVE)
        .unwrap();
    let rd = tiny.readout().unwrap();
    assert_eq!(rd.value.to_bits(), 0f64.to_bits());
    assert!(!rd.quantization.is_empty());
    assert!(sidecar::Bounded::exact(f64::MAX)
        .unwrap()
        .scale(f64::MAX)
        .unwrap()
        .readout()
        .is_err());
    cleanup(d)
}
#[test]
fn occurrence_payloads_length_prefix_delimiter_and_context_bits() {
    let (d, a, s, c) = setup(Ledger::default());
    let p = proposal(&a, &s, &c);
    let mut v = c.clone();
    v.bits.push(17);
    let other = Proposal::new(
        a.reserve().unwrap(),
        v.clone(),
        0,
        stages(&v),
        vec![1],
        [Wide::ZERO; 11],
        true,
        false,
    )
    .unwrap();
    assert_ne!(p.leaves[0].edge, other.leaves[0].edge);
    let mut reg = Registry::default();
    let mut one = p.leaves[0].clone();
    one.edge = "1:a2:bc".into();
    let mut two = one.clone();
    two.edge = "2:ab1:c".into();
    reg.bind(&one).unwrap();
    reg.bind(&two).unwrap();
    assert_eq!(reg.len(), 2);
    cleanup(d)
}

// Fabricated algebraic transaction only: no provider, Newton or RHS evaluation.
fn native_algebraic_trial(error_norm: f64) -> sidecar::DetailedTrial {
    use native_detailed::igm_source_step::{SourceState, SourceStep, SourceTrial, StepLedger};
    let state = SourceState {
        gas: native_detailed::igm_state::IgmGasState::new([0.9, 0.3, 0.05], 1e-12).unwrap(),
        photons: vec![],
    };
    let step = SourceStep {
        state,
        ledger: StepLedger::default(),
        iterations: 0,
        rhs_evaluations: 0,
        gas_residual_norm: 0.,
        photon_residual_norm: 0.,
    };
    let mut stages = Vec::new();
    for (role, dt, rate, point) in [
        (Stage::FullCostOnly, 1., 1e-18, 1),
        (Stage::Half1, 0.5, 1e-18, 2),
        (Stage::Half2, 0.5, 1e-50, 3),
    ] {
        let mut r = sidecar::SpeciesRate::default();
        r.point_ordinal = point;
        r.context_bits = context().bits;
        for e in events(rate) {
            let i = match e.species {
                Species::HI => 0,
                Species::HeI => 1,
                Species::HeII => 2,
            };
            let v = sidecar::Bounded::exact(e.rate).unwrap();
            r.count[i] = r.count[i].add(v).unwrap();
            r.full_energy[i] = r.full_energy[i]
                .add(v.scale(e.energy_ev).unwrap().scale(e.epsilon).unwrap())
                .unwrap();
            r.events.push(sidecar::Event {
                node: e.node,
                species: i,
                event_per_h_s: e.rate,
                energy_ev: e.energy_ev,
                epsilon: e.epsilon,
            });
        }
        let a = std::array::from_fn(|i| r.count[i].scale(dt).unwrap());
        let b = std::array::from_fn(|i| r.full_energy[i].scale(dt).unwrap());
        let expected = SealedStage::capture(context(), role, point, dt, events(rate))
            .unwrap()
            .owners();
        assert_eq!((a, b), expected);
        stages.push(sidecar::SpeciesStage {
            dt_s: dt,
            count: a,
            absorbed_energy: b,
            rate: r,
            errors: vec![],
        });
    }
    sidecar::DetailedTrial {
        legacy: SourceTrial {
            full: step.clone(),
            half1: step.clone(),
            half2: step,
            error_norm,
        },
        stages,
        counters: sidecar::Counters::default(),
    }
}
#[test]
fn native_acceptance_boundary_without_rhs_and_generation_witness() {
    let (d, a, mut s, c) = setup(Ledger::default());
    assert!(Proposal::from_native_trial(
        a.reserve().unwrap(),
        c.clone(),
        0,
        native_algebraic_trial(2.),
        [Wide::ZERO; 11],
        true,
        false
    )
    .is_err());
    let mut mismatch = native_algebraic_trial(0.);
    mismatch.stages[1].rate.context_bits[0] = 2e-4f64.to_bits();
    assert!(Proposal::from_native_trial(
        a.reserve().unwrap(),
        c.clone(),
        0,
        mismatch,
        [Wide::ZERO; 11],
        true,
        false
    )
    .is_err());
    let p = Proposal::from_native_trial(
        a.reserve().unwrap(),
        c.clone(),
        0,
        native_algebraic_trial(0.),
        [Wide::ZERO; 11],
        true,
        false,
    )
    .unwrap();
    assert_eq!(p.native_receipt().unwrap().total_rhs_evaluations, 0);
    s.apply(&p, FailAt::None).unwrap();
    assert_eq!(s.snapshot().witnesses.len(), 1);
    let p1 = proposal(&a, &s, &c);
    let mut wrong = p1.clone();
    wrong.expected_generation = 0;
    assert!(s.apply(&wrong, FailAt::None).is_err());
    s.apply(&p1, FailAt::None).unwrap();
    assert_eq!(s.snapshot().witnesses.len(), 2);
    assert!(s.publish_physical().is_err());
    cleanup(d)
}

#[test]
fn generation_is_part_of_occurrence_even_same_attempt() {
    let (d, a, s, c) = setup(Ledger::default());
    let attempt = a.reserve().unwrap();
    let p0 = Proposal::new(
        attempt.clone(),
        c.clone(),
        0,
        stages(&c),
        vec![1],
        [Wide::ZERO; 11],
        true,
        false,
    )
    .unwrap();
    let p1 = Proposal::new(
        attempt,
        c.clone(),
        1,
        stages(&c),
        vec![1],
        [Wide::ZERO; 11],
        true,
        false,
    )
    .unwrap();
    assert_ne!(p0.leaves[0].edge, p1.leaves[0].edge);
    assert_eq!(s.snapshot().generation, 0);
    cleanup(d)
}
#[test]
fn inherited_rate_leaf_propagates_once_and_actual_readout_q() {
    let (d, a, mut s, c) = setup(Ledger::default());
    let mut ev = events(1e-18);
    ev.push(Event {
        node: 1,
        species: Species::HI,
        rate: 1e-50,
        energy_ev: 13.7,
        epsilon: canonical::EPS,
    });
    let h1 = SealedStage::capture(c.clone(), Stage::Half1, 1, 0.5, ev).unwrap();
    let h2 = SealedStage::capture(c.clone(), Stage::Half2, 2, 0.5, events(1e-50)).unwrap();
    let p = Proposal::new(
        a.reserve().unwrap(),
        c.clone(),
        0,
        [h1, h2],
        vec![1],
        [Wide::ZERO; 11],
        true,
        false,
    )
    .unwrap();
    assert!(p
        .leaves
        .iter()
        .any(|x| x.category == Category::FreshSwallowed
            && x.edge.contains("Half1")
            && !x.raw.is_empty()));
    s.apply(&p, FailAt::None).unwrap();
    let (n, e) = s.snapshot().ledger.totals().unwrap();
    assert!(p.a[0].swallowed.le(n) && p.b[0].swallowed.le(e));
    let (d2, a2, mut t, c2) = setup(Ledger::default());
    let ev = vec![Event {
        node: 0,
        species: Species::HI,
        rate: f64::MIN_POSITIVE,
        energy_ev: f64::MIN_POSITIVE,
        epsilon: canonical::EPS,
    }];
    let h = [
        SealedStage::capture(c2.clone(), Stage::Half1, 1, 0.5, ev.clone()).unwrap(),
        SealedStage::capture(c2.clone(), Stage::Half2, 2, 0.5, ev).unwrap(),
    ];
    let p = Proposal::new(
        a2.reserve().unwrap(),
        c2.clone(),
        0,
        h,
        vec![1],
        [Wide::ZERO; 11],
        true,
        true,
    )
    .unwrap();
    assert!(p
        .leaves
        .iter()
        .any(|x| x.category == Category::ReadoutQuantization && !x.raw.is_empty()));
    assert_eq!(p.b[0].readout().unwrap().value.to_bits(), 0f64.to_bits());
    t.apply(&p, FailAt::None).unwrap();
    assert!(t
        .snapshot()
        .ledger
        .charges()
        .iter()
        .any(|x| x.boundary == "ReadoutQuantization" && !x.bound.is_empty()));
    cleanup(d);
    cleanup(d2)
}

#[test]
fn cloned_allocator_root_cannot_reuse_global_namespace() {
    let d = dir();
    let ns = "parent-issued-fork-lease";
    let a = Allocator::open(d.join("first"), ns).unwrap();
    let b = Allocator::open(d.join("second"), ns).unwrap();
    assert_ne!(
        a.reserve().unwrap().identity(),
        b.reserve().unwrap().identity()
    );
    std::fs::create_dir(d.join("cloned")).unwrap();
    std::fs::copy(d.join("first/NAMESPACE"), d.join("cloned/NAMESPACE")).unwrap();
    assert!(Allocator::open(d.join("cloned"), ns).is_err());
    cleanup(d)
}
