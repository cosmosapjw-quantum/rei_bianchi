//! Live CR-off point/BE receiver with optional durable conditional bookkeeping.
mod connection;
pub use connection::*;
mod run;
use canonical::{Ledger, Wide};
use ledger::{Allocator, Context, DiagnosticStore, FailAt, Snapshot, R, SOURCE_PIN};
use native_detailed::{
    cr_off_igm_bridge::{CountPerH, CrMode, DeferredCrAccess, PointContext},
    igm_source_step::{
        trial_source_step, AcceptedSourceStep, NewtonControl, SourceState, StepAccuracy,
    },
    igm_state::IgmGasState,
    AtomicProvider,
};
use std::path::Path;
pub struct Receiver {
    state: SourceState,
    generation: u64,
    durable: Option<Durable>,
}
struct Durable {
    run: run::Run,
    allocator: Allocator,
    store: DiagnosticStore,
}
pub struct StepReceipt {
    pub legacy: AcceptedSourceStep,
    pub counters: sidecar::Counters,
    pub publication: Option<ledger::Publication>,
}
pub fn state_bits(s: &SourceState) -> Vec<u64> {
    let mut v = s.gas.fractions.map(f64::to_bits).to_vec();
    v.push(s.gas.w_erg_per_h.to_bits());
    for p in &s.photons {
        v.extend([p.energy_ev.to_bits(), p.photons_per_h.to_bits()])
    }
    v
}
fn from_bits(v: &[u64]) -> R<SourceState> {
    if v.len() < 4 || (v.len() - 4) % 2 != 0 || v.len() > 4096 {
        return Err("native checkpoint state shape".into());
    }
    let f = |i| f64::from_bits(v[i]);
    let gas = IgmGasState::new([f(0), f(1), f(2)], f(3)).map_err(|e| format!("{e:?}"))?;
    let mut photons = Vec::new();
    for pair in v[4..].chunks_exact(2) {
        let energy = f64::from_bits(pair[0]);
        let count = f64::from_bits(pair[1]);
        if !energy.is_normal() || energy <= 0. || !(count == 0. || count.is_normal()) || count < 0.
        {
            return Err("normal-domain photon checkpoint".into());
        }
        photons.push(CountPerH {
            energy_ev: energy,
            photons_per_h: count,
        })
    }
    Ok(SourceState { gas, photons })
}
fn context(
    namespace: &str,
    generation: u64,
    s: &SourceState,
    c: PointContext,
    source: &[f64],
    dt: f64,
) -> Context {
    let mut bits = vec![
        c.n_h_cm3.to_bits(),
        c.n_he_cm3.to_bits(),
        c.hubble_s.to_bits(),
        c.t_cmb_k.to_bits(),
    ];
    bits.extend(state_bits(s));
    bits.extend(source.iter().map(|x| x.to_bits()));
    bits.push(dt.to_bits());
    let n = NewtonControl::default();
    let a = StepAccuracy::default();
    bits.extend([
        n.max_iterations as u64,
        n.tolerance.to_bits(),
        a.relative.to_bits(),
        a.fraction_absolute.to_bits(),
        a.photon_absolute.to_bits(),
        a.thermal_absolute_erg_per_h.to_bits(),
    ]);
    Context {
        parent_checkpoint: namespace.into(),
        transition: generation as usize,
        source_pin: SOURCE_PIN.into(),
        bits,
        total_dt_bits: dt.to_bits(),
    }
}
impl Receiver {
    /// Default/off executes the unchanged native trial+accept path and creates no files.
    pub fn legacy(state: SourceState) -> Self {
        Self {
            state,
            generation: 0,
            durable: None,
        }
    }
    pub fn create(
        root: impl AsRef<Path>,
        state: SourceState,
        c: PointContext,
        source: &[f64],
        dt: f64,
    ) -> R<Self> {
        from_bits(&state_bits(&state))?;
        if 4 + state_bits(&state).len() + source.len() + 7 > 4096 {
            return Err("receiver context schema cap".into());
        }
        if source.len() != state.photons.len() {
            return Err("source shape".into());
        }
        let run = run::Run::create(root.as_ref())?;
        let ctx = context(&run.namespace, 0, &state, c, source, dt);
        let allocator = Allocator::open(run.root.join("leases"), &run.namespace)?;
        let store = DiagnosticStore::open(
            run.root.join("store"),
            Snapshot::initial(Ledger::default(), state_bits(&state), &ctx)?,
        )?;
        Ok(Self {
            state,
            generation: 0,
            durable: Some(Durable {
                run,
                allocator,
                store,
            }),
        })
    }
    /// Only disk and bound local identity are required; no caller Snapshot is accepted.
    pub fn resume(root: impl AsRef<Path>) -> R<Self> {
        let run = run::Run::resume(root.as_ref())?;
        for path in [
            run.root.join("leases/NAMESPACE"),
            run.root.join("store/HEAD"),
        ] {
            if !std::fs::symlink_metadata(&path)
                .map_err(|e| e.to_string())?
                .file_type()
                .is_file()
            {
                return Err("incomplete/symlink run checkpoint".into());
            }
        }
        let allocator = Allocator::open(run.root.join("leases"), &run.namespace)?;
        let store = DiagnosticStore::restore(run.root.join("store"))?;
        store.validate_allocator(&allocator)?;
        let state = from_bits(&store.snapshot().state)?;
        let generation = store.snapshot().generation;
        Ok(Self {
            state,
            generation,
            durable: Some(Durable {
                run,
                allocator,
                store,
            }),
        })
    }
    pub fn state(&self) -> &SourceState {
        &self.state
    }
    pub fn generation(&self) -> u64 {
        self.generation
    }
    pub fn snapshot(&self) -> Option<&Snapshot> {
        self.durable.as_ref().map(|d| d.store.snapshot())
    }
    /// Real solve -> native accept -> Proposal -> canonical commit -> durable HEAD.
    /// Original canonical request remains explicit. Physical/history/full-Wide stay HOLD.
    pub fn advance_one(
        &mut self,
        expected_generation: u64,
        c: PointContext,
        source: &[f64],
        dt: f64,
        provider: &AtomicProvider,
        cr: &mut impl DeferredCrAccess,
        increment: [Wide; 11],
        private_gate: bool,
        fail: FailAt,
    ) -> R<StepReceipt> {
        if expected_generation != self.generation {
            return Err("receiver replay/stale generation".into());
        }
        if let Some(d) = &mut self.durable {
            d.run.check_owner()?;
            let ctx = context(
                &d.run.namespace,
                self.generation,
                &self.state,
                c,
                source,
                dt,
            );
            // Fail before any native call on changed frozen input/configuration or replay.
            d.store.check_native_input(&ctx)?;
            let trial = sidecar::trial_detailed(
                CrMode::Off,
                &self.state,
                c,
                source,
                dt,
                provider,
                NewtonControl::default(),
                StepAccuracy::default(),
                cr,
            )
            .map_err(|e| format!("{e:?}"))?;
            let receipt = receive_native_trial(
                DiagnosticOptIn::Enabled,
                trial,
                &d.allocator,
                &mut d.store,
                DiagnosticRequest {
                    context: ctx,
                    original_increment: increment,
                    original_private_gate: private_gate,
                },
                fail,
            )?;
            let legacy = receipt
                .legacy_trial
                .accept()
                .map_err(|e| format!("{e:?}"))?;
            self.state = legacy.state.clone();
            self.generation = receipt.publication.generation;
            Ok(StepReceipt {
                legacy,
                counters: receipt.observed_native_calls,
                publication: Some(receipt.publication),
            })
        } else {
            let (trial, counters) = sidecar::count_only(|| {
                trial_source_step(
                    CrMode::Off,
                    &self.state,
                    c,
                    source,
                    dt,
                    provider,
                    NewtonControl::default(),
                    StepAccuracy::default(),
                    cr,
                )
            })
            .map_err(|e| format!("{e:?}"))?;
            let legacy = trial.accept().map_err(|e| format!("{e:?}"))?;
            self.state = legacy.state.clone();
            self.generation += 1;
            Ok(StepReceipt {
                legacy,
                counters,
                publication: None,
            })
        }
    }
}
