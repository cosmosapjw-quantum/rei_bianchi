//! Label-preserving batching with ordered floating-point reduction.
use crate::{
    Error, Mode, Result,
    kernel::{NativeKernel, Work},
};
use rei_br06_reference::{
    fixture::NativeFixture,
    reference::{self, PathControls, PathResult, RunControls},
};
use rei_iso_couple_reference::{full_network::EV_J, source_age::Cohort};
use std::{
    collections::HashMap,
    path::Path,
    sync::{Arc, mpsc},
    thread,
};

#[derive(Clone, Debug)]
pub struct LabelledBirth {
    pub template: usize,
    pub node: usize,
    pub target_age: f64,
    pub emission_weight: f64,
    pub cohort: Cohort,
    unique_path: usize,
}

/// No birth record is discarded. Unique work is only the exact reflection
/// equivalence already used by BR06; this object has no mutation API.
pub struct PreparedBatch<'a> {
    fixture: &'a NativeFixture,
    fixture_identity: FixtureIdentity,
    births: Vec<LabelledBirth>,
    unique: Arc<Vec<Cohort>>,
    pub templates: usize,
}
impl<'a> PreparedBatch<'a> {
    pub fn build(fixture: &'a NativeFixture, controls: RunControls) -> Result<Self> {
        let templates = fixture.templates(controls.split_spectrum)?;
        let limit = if controls.template_limit == 0 {
            templates.len()
        } else {
            controls.template_limit.min(templates.len())
        };
        let mut births = Vec::new();
        let mut unique = Vec::new();
        let mut map = HashMap::new();
        for (template_id, template) in templates.iter().take(limit).enumerate() {
            for (node, (target_age, emission_weight, cohort)) in
                reference::emit_births(fixture, template, controls)?
                    .into_iter()
                    .enumerate()
            {
                // Original run validates the ray before forming its reflection key.
                cohort.ray_at(&cohort.birth_geometry)?;
                let key = [
                    cohort.birth_time_s.to_bits(),
                    cohort.energy_at_birth_ev.to_bits(),
                    cohort.direction_at_birth[0].abs().to_bits(),
                    cohort.direction_at_birth[1].abs().to_bits(),
                    cohort.direction_at_birth[2].abs().to_bits(),
                    cohort.birth_geometry.scale_factors[0].to_bits(),
                    cohort.birth_geometry.scale_factors[2].to_bits(),
                ];
                let unique_path = *map.entry(key).or_insert_with(|| {
                    unique.push(cohort.clone());
                    unique.len() - 1
                });
                births.push(LabelledBirth {
                    template: template_id,
                    node,
                    target_age,
                    emission_weight,
                    cohort,
                    unique_path,
                });
            }
        }
        Ok(Self {
            fixture,
            fixture_identity: FixtureIdentity::of(fixture)?,
            births,
            unique: Arc::new(unique),
            templates: limit,
        })
    }
    pub fn births(&self) -> &[LabelledBirth] {
        &self.births
    }
    pub fn unique_cohorts(&self) -> &[Cohort] {
        &self.unique
    }
    pub fn result_for_birth(&self, index: usize, paths: &[PathResult]) -> PathResult {
        let birth = &self.births[index];
        let mut path = paths[birth.unique_path].clone();
        for i in 0..3 {
            path.end_direction[i] = path.end_direction[i]
                .abs()
                .copysign(birth.cohort.direction_at_birth[i]);
        }
        path
    }
    pub fn reduce(&self, fixture: &NativeFixture, paths: &[PathResult]) -> Result<Ledger> {
        self.check_fixture(fixture)?;
        if paths.len() != self.unique.len() {
            return Err(Error::InvalidInput("batch_path_cardinality"));
        }
        let mut ledger = Ledger::default();
        // Exactly BR06 template-major, node-minor order. Never a parallel sum.
        for (index, birth) in self.births.iter().enumerate() {
            ledger.add_birth(fixture, &birth.cohort, &self.result_for_birth(index, paths));
        }
        ledger.validate()?;
        Ok(ledger)
    }
    fn check_fixture(&self, fixture: &NativeFixture) -> Result<()> {
        if !std::ptr::eq(self.fixture, fixture) {
            return Err(Error::InvalidInput("batch_fixture_identity"));
        }
        Ok(())
    }
}

/// Exact frozen-context receipt for worker fixtures reconstructed in another
/// thread. Floating state/clock bits are explicit. Debug strings retain all
/// private immutable source and D-provider fields through their existing APIs.
#[derive(Clone, Debug, PartialEq, Eq)]
struct FixtureIdentity {
    bits: Vec<u64>,
    case: String,
    geometry: String,
    source: String,
    config: String,
}
impl FixtureIdentity {
    fn of(f: &NativeFixture) -> Result<Self> {
        f.validate_source()?;
        let mut bits = vec![
            f.t0,
            f.tm,
            f.t1,
            f.recorded_mid_volume,
            f.source_midpoint_amplitude,
            f.rate_gas.thermal_j_m3,
        ]
        .into_iter()
        .map(f64::to_bits)
        .collect::<Vec<_>>();
        bits.extend(f.recorded_mid_geometry.scale_factors.map(f64::to_bits));
        bits.extend(f.recorded_mid_geometry.hubble_per_s.map(f64::to_bits));
        bits.extend(f.thresholds_ev.map(f64::to_bits));
        bits.extend(
            rei_iso_couple_reference::isotope_state::IsotopeSpecies::ALL
                .map(|species| f.rate_gas.nuclei.density_m3(species).to_bits()),
        );
        Ok(Self {
            bits,
            case: f.case.clone(),
            geometry: f.bridge.0.geometry.identity(),
            source: format!("{:?}", f.bridge.0.source),
            config: format!("{:?}", f.conf),
        })
    }
}

pub struct BatchResult {
    pub paths: Vec<PathResult>,
    pub work: Work,
}

/// OFF dispatch calls the original native_path with unchanged arguments.
pub fn evaluate_serial(
    fixture: &NativeFixture,
    batch: &PreparedBatch<'_>,
    controls: PathControls,
    mode: Mode,
) -> Result<BatchResult> {
    batch.check_fixture(fixture)?;
    fixture.bridge.0.geometry.clear_cache();
    let mut paths = Vec::with_capacity(batch.unique.len());
    let work = match mode {
        Mode::Baseline => {
            for cohort in batch.unique.iter() {
                paths.push(reference::native_path(fixture, cohort, controls)?);
            }
            Work {
                virtual_samples: paths.iter().map(|p| p.samples).sum(),
                ..Work::default()
            }
        }
        Mode::Cached => {
            let kernel = NativeKernel::new(fixture, controls)?;
            for cohort in batch.unique.iter() {
                paths.push(kernel.native_path(cohort)?);
            }
            kernel.work()
        }
    };
    Ok(BatchResult { paths, work })
}

struct Job {
    cohorts: Arc<Vec<Cohort>>,
    indices: Vec<usize>,
    controls: PathControls,
}
struct Reply {
    results: Vec<(usize, Result<PathResult>)>,
    work: Work,
}
struct Worker {
    send: mpsc::Sender<Option<Job>>,
    receive: mpsc::Receiver<Result<Reply>>,
    handle: Option<thread::JoinHandle<()>>,
}

/// The original GeometryChoice contains Rc<RefCell> and is intentionally not
/// Send/Sync. Each persistent worker loads and owns its own immutable fixture;
/// only data records cross threads. No unsafe trait implementation is used.
pub struct ParallelPool {
    workers: Vec<Worker>,
    fixture_identity: Option<FixtureIdentity>,
}
impl ParallelPool {
    pub fn new(root: &Path, case: &str, threads: usize) -> Result<Self> {
        if threads == 0 || threads > 16 {
            return Err(Error::InvalidInput("parallel_thread_count"));
        }
        let mut pool = Self {
            workers: Vec::new(),
            fixture_identity: None,
        };
        for _ in 0..threads {
            let root = root.to_path_buf();
            let case = case.to_owned();
            let (send, jobs) = mpsc::channel::<Option<Job>>();
            let (responses, receive) = mpsc::channel();
            let (ready_send, ready) = mpsc::channel();
            let handle = thread::spawn(move || {
                let fixture = match NativeFixture::load(&root, &case) {
                    Ok(fixture) => fixture,
                    Err(error) => {
                        let _ = ready_send.send(Err(error));
                        return;
                    }
                };
                let identity = match FixtureIdentity::of(&fixture) {
                    Ok(identity) => identity,
                    Err(error) => {
                        let _ = ready_send.send(Err(error));
                        return;
                    }
                };
                if ready_send.send(Ok(identity)).is_err() {
                    return;
                }
                while let Ok(Some(job)) = jobs.recv() {
                    fixture.bridge.0.geometry.clear_cache();
                    let result = (|| {
                        let kernel = NativeKernel::new(&fixture, job.controls)?;
                        let mut results = Vec::with_capacity(job.indices.len());
                        for index in job.indices {
                            results.push((index, kernel.native_path(&job.cohorts[index])));
                        }
                        Ok(Reply {
                            results,
                            work: kernel.work(),
                        })
                    })();
                    if responses.send(result).is_err() {
                        return;
                    }
                }
            });
            pool.workers.push(Worker {
                send,
                receive,
                handle: Some(handle),
            });
            let identity = ready
                .recv()
                .map_err(|_| worker_error("worker_initialization"))??;
            if let Some(expected) = &pool.fixture_identity {
                if expected != &identity {
                    return Err(Error::InvalidInput("worker_fixture_identity"));
                }
            } else {
                pool.fixture_identity = Some(identity);
            }
        }
        Ok(pool)
    }
    pub fn evaluate(
        &self,
        batch: &PreparedBatch<'_>,
        controls: PathControls,
    ) -> Result<BatchResult> {
        if self.fixture_identity.as_ref() != Some(&batch.fixture_identity) {
            return Err(Error::InvalidInput("parallel_fixture_identity"));
        }
        for (worker_id, worker) in self.workers.iter().enumerate() {
            worker
                .send
                .send(Some(Job {
                    cohorts: Arc::clone(&batch.unique),
                    // Round-robin jobs balance varying opacities without a parallel
                    // accumulation. Row order is reconstructed only after joining.
                    indices: (worker_id..batch.unique.len())
                        .step_by(self.workers.len())
                        .collect(),
                    controls,
                }))
                .map_err(|_| worker_error("worker_job_send"))?;
        }
        let mut unordered = Vec::with_capacity(batch.unique.len());
        let mut work = Work::default();
        let mut first_pool_error = None;
        for worker in &self.workers {
            match worker
                .receive
                .recv()
                .map_err(|_| worker_error("worker_result_receive"))?
            {
                Ok(reply) => {
                    unordered.extend(reply.results);
                    work.opacity_integrals += reply.work.opacity_integrals;
                    work.virtual_samples += reply.work.virtual_samples;
                }
                Err(error) => {
                    if first_pool_error.is_none() {
                        first_pool_error = Some(error);
                    }
                }
            }
        }
        if let Some(error) = first_pool_error {
            return Err(error);
        }
        unordered.sort_by_key(|item| item.0);
        // The lowest failing original cohort index determines the returned error.
        let paths = unordered
            .into_iter()
            .map(|(_, result)| result)
            .collect::<Result<Vec<_>>>()?;
        if paths.len() != batch.unique.len() {
            return Err(worker_error("worker_cardinality"));
        }
        Ok(BatchResult { paths, work })
    }
}
impl Drop for ParallelPool {
    fn drop(&mut self) {
        for worker in &self.workers {
            let _ = worker.send.send(None);
        }
        for worker in &mut self.workers {
            if let Some(handle) = worker.handle.take() {
                let _ = handle.join();
            }
        }
    }
}
fn worker_error(tag: &'static str) -> Error {
    Error::Io(std::io::Error::other(tag))
}

include!("ledger.rs");
