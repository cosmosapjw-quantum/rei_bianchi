//! Short actual native fixture driver; no cosmological/history campaign.
use canonical::Wide;
use ledger::FailAt;
use native_detailed::{
    cr_off_igm_bridge::{CountPerH, CrMode, DeferredCrAccess, PointContext},
    igm_source_step::{
        trial_source_step, AcceptedSourceStep, NewtonControl, SourceState, SourceStep,
        StepAccuracy, StepLedger,
    },
    igm_state::IgmGasState,
    AtomicProvider, ForwardError,
};
use rei_receiver_restart::*;
use std::{io::Write, path::Path};
struct Off;
impl DeferredCrAccess for Off {
    fn load(&mut self) -> Result<(), ForwardError> {
        panic!("CR must stay OFF")
    }
    fn source_callback(&mut self) -> Result<[f64; 4], ForwardError> {
        panic!("CR must stay OFF")
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
fn ledger_bits(l: &StepLedger) -> Vec<u64> {
    let mut v = Vec::new();
    for a in [&l.photo, &l.collision, &l.recombination] {
        v.extend(a.map(f64::to_bits))
    }
    v.extend(
        [
            l.dielectronic,
            l.escape,
            l.cmb_to_gas,
            l.gas_work,
            l.injected_count,
            l.injected_energy,
        ]
        .map(f64::to_bits),
    );
    v
}
fn step_bits(s: &SourceStep) -> Vec<u64> {
    let mut v = state_bits(&s.state);
    v.extend(ledger_bits(&s.ledger));
    v.extend([
        s.iterations as u64,
        s.rhs_evaluations as u64,
        s.gas_residual_norm.to_bits(),
        s.photon_residual_norm.to_bits(),
    ]);
    v
}
fn accepted_bits(s: &AcceptedSourceStep) -> Vec<u64> {
    let mut v = state_bits(&s.state);
    v.extend(ledger_bits(&s.ledger));
    for stage in &s.stages {
        v.extend(step_bits(stage))
    }
    v.extend([s.error_norm.to_bits(), s.total_rhs_evaluations as u64]);
    v
}
fn go() -> Result<(), String> {
    let a: Vec<String> = std::env::args().collect();
    let mode = &a[1];
    let root = Path::new(&a[2]);
    let report = Path::new(&a[3]);
    let steps: usize = a.get(4).map(|s| s.parse().unwrap()).unwrap_or(0);
    if mode == "schema-check" {
        let mut state = fixture();
        state.photons = vec![state.photons[0]; 1361];
        let err = Receiver::create(root, state, ctx(), &vec![5e-15; 1361], 1e7)
            .err()
            .unwrap();
        assert!(err.contains("schema cap"));
        assert!(!root.exists());
        let accepted_root = root.with_extension("accepted-limit");
        let mut state = fixture();
        state.photons = vec![state.photons[0]; 1360];
        let receiver = Receiver::create(&accepted_root, state, ctx(), &vec![5e-15; 1360], 1e7)?;
        let before = state_bits(receiver.state());
        drop(receiver);
        let restored = Receiver::resume(&accepted_root)?;
        assert_eq!(before, state_bits(restored.state()));
        assert_eq!(restored.generation(), 0);
        println!(
            "ENCODER_DECODER_CONTEXT_LIMIT_REFUSED_BEFORE_FILES_NATIVE_AND_MAX_ACCEPTED_RESTORES"
        );
        return Ok(());
    }
    if mode == "fork-check" {
        unsafe extern "C" {
            fn fork() -> i32;
            fn waitpid(pid: i32, status: *mut i32, options: i32) -> i32;
        }
        let mut r = Receiver::resume(root)?;
        let pid = unsafe { fork() };
        if pid < 0 {
            return Err("fork unavailable".into());
        }
        if pid == 0 {
            let result = r.advance_one(
                r.generation(),
                ctx(),
                &[5e-15],
                1e7,
                &AtomicProvider::reference(),
                &mut Off,
                [Wide::ZERO; 11],
                true,
                FailAt::None,
            );
            assert!(result.err().unwrap().contains("fork handle"));
            println!("INHERITED_FORK_REFUSED_BEFORE_NATIVE");
            std::process::exit(0)
        }
        let mut status = 0;
        assert_eq!(unsafe { waitpid(pid, &mut status, 0) }, pid);
        assert_eq!(status, 0);
        return Ok(());
    }
    if mode == "probe" {
        let r = Receiver::resume(root)?;
        println!(
            "RESTORED generation={} state={:?}",
            r.generation(),
            state_bits(r.state())
        );
        return Ok(());
    }
    let mut receiver = if mode == "resume" {
        Receiver::resume(root)?
    } else if mode == "off" || mode == "baseline" {
        Receiver::legacy(fixture())
    } else {
        Receiver::create(root, fixture(), ctx(), &[5e-15], 1e7)?
    };
    let mut results = Vec::new();
    let mut rhs = 0;
    let mut providers = 0;
    let provider = AtomicProvider::reference();
    // Replay and changed frozen configuration refuse before a single native call.
    if mode == "resume" {
        let before = state_bits(receiver.state());
        let (_, calls) = sidecar::count_only(|| {
            assert!(receiver
                .advance_one(
                    receiver.generation() + 1,
                    ctx(),
                    &[5e-15],
                    1e7,
                    &provider,
                    &mut Off,
                    [Wide::ZERO; 11],
                    true,
                    FailAt::None
                )
                .is_err());
            assert!(receiver
                .advance_one(
                    receiver.generation(),
                    ctx(),
                    &[5e-15],
                    2e7,
                    &provider,
                    &mut Off,
                    [Wide::ZERO; 11],
                    true,
                    FailAt::None
                )
                .is_err());
            Ok::<_, ForwardError>(())
        })
        .unwrap();
        assert_eq!(calls, sidecar::Counters::default());
        assert_eq!(before, state_bits(receiver.state()));
    }
    for _ in 0..steps {
        let generation = receiver.generation();
        let (legacy, counts) = if mode == "baseline" {
            let (t, c) = sidecar::count_only(|| {
                trial_source_step(
                    CrMode::Off,
                    receiver.state(),
                    ctx(),
                    &[5e-15],
                    1e7,
                    &provider,
                    NewtonControl::default(),
                    StepAccuracy::default(),
                    &mut Off,
                )
            })
            .unwrap();
            let accepted = t.accept().unwrap();
            receiver = Receiver::legacy(accepted.state.clone());
            (accepted, c)
        } else {
            let fail = if mode == "crash-pending" {
                FailAt::ProcessStopBeforePublish
            } else {
                FailAt::None
            };
            let r = receiver.advance_one(
                generation,
                ctx(),
                &[5e-15],
                1e7,
                &provider,
                &mut Off,
                [Wide::ZERO; 11],
                true,
                fail,
            )?;
            if let Some(p) = &r.publication {
                assert!(p.directory_synced);
                assert_eq!(p.physical_admission, ledger::HOLD)
            }
            (r.legacy, r.counters)
        };
        rhs += counts.point_calls;
        providers += counts.provider_calls;
        results.push(format!(
            "{{\"rhs\":{},\"provider\":{},\"bits\":{:?}}}",
            counts.point_calls,
            counts.provider_calls,
            accepted_bits(&legacy)
        ));
    }
    let snapshot=receiver.snapshot().map(|s|format!("{{\"generation\":{},\"registry_len\":{},\"witnesses\":{},\"owners\":\"{:?}/{:?}\",\"loss_totals\":\"{:?}\"}}",s.generation,s.registry.len(),s.witnesses.len(),s.a,s.b,s.ledger.totals().unwrap())).unwrap_or("null".into());
    let json=format!("{{\"mode\":\"{}\",\"actual_trials\":{},\"rhs\":{},\"provider\":{},\"steps\":[{}],\"final_state\":{:?},\"snapshot\":{},\"physical_admission\":\"HOLD\"}}\n",mode,steps,rhs,providers,results.join(","),state_bits(receiver.state()),snapshot);
    std::fs::write(report, &json).map_err(|e| e.to_string())?;
    println!("{json}");
    std::io::stdout().flush().unwrap();
    if mode == "stop-committed" {
        std::fs::write(root.join("READY_FOR_KILL"), b"HEAD committed and synced\n").unwrap();
        loop {
            std::thread::sleep(std::time::Duration::from_millis(20))
        }
    }
    Ok(())
}
fn main() {
    if let Err(e) = go() {
        eprintln!("REFUSED: {e}");
        std::process::exit(2)
    }
}
