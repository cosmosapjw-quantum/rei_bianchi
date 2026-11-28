//! HE29 opt-in C bridge to the pinned VigilODE sequential RODAS5P driver.
//! The caller owns the physical RHS, JVP, partial time derivative and ledgers.
//! This module changes neither the four SciPy references nor their admission.
#![deny(unsafe_op_in_unsafe_fn)]

#[cfg(panic = "abort")]
compile_error!("HE29 bridge requires panic=unwind to contain Rust panics");

use std::ffi::{c_char, c_void};
use std::mem::{align_of, size_of};
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex, TryLockError};

use rodas5p_core::{CoreError, CoreResult, LinearMethod, LinearSolverConfig};
use rodas5p_integrators::{
    AdaptiveStepConfig, OdeProblem, OutputSchedule,
    integrate_sequential_matrix_free_adaptive_observed,
};
use serde_json::{Value, json};

const SOURCE: &str = "a21d573980f66fe02891bd216153443b5352f921";
const ABI_VERSION: u32 = 1;
const RTOL: f64 = 1.0e-10;
const ATOL: f64 = 1.0e-12;
const OK: i32 = 0;
const PARTIAL: i32 = 1;
const INVALID: i32 = 2;
const CALLBACK_ERROR: i32 = 3;
const SOLVER_ERROR: i32 = 4;
const PANIC: i32 = 5;
const BUSY: i32 = 6;
const JSON_BUFFER_SMALL: i32 = 7;
static RUN_LOCK: Mutex<()> = Mutex::new(());

pub type RhsCallback = unsafe extern "C" fn(
    *mut c_void, f64, *const f64, usize, *mut f64,
) -> i32;
pub type JvpCallback = unsafe extern "C" fn(
    *mut c_void, f64, *const f64, *const f64, usize, *mut f64,
) -> i32;

#[repr(C)]
#[derive(Clone, Copy)]
pub struct He29Stats {
    pub abi_version: u32,
    pub status: i32,
    pub dimension: usize,
    pub final_u: f64,
    pub output_samples: usize,
    pub internal_steps: usize,
    pub output_clipped_steps: usize,
    pub attempts: usize,
    pub accepted_macro_steps: usize,
    pub rejected_macro_steps: usize,
    pub rhs_evaluations: u64,
    pub jvp_vectors: u64,
    pub linear_iterations: u64,
    pub direct_factorizations: u64,
    pub callback_rhs_calls: u64,
    pub callback_jvp_calls: u64,
    pub callback_partial_u_calls: u64,
    pub json_required_bytes: usize,
}

impl He29Stats {
    fn empty(n: usize, status: i32) -> Self {
        Self {
            abi_version: ABI_VERSION, status, dimension: n, final_u: 0.0,
            output_samples: 0, internal_steps: 0, output_clipped_steps: 0,
            attempts: 0, accepted_macro_steps: 0, rejected_macro_steps: 0,
            rhs_evaluations: 0, jvp_vectors: 0, linear_iterations: 0,
            direct_factorizations: 0, callback_rhs_calls: 0, callback_jvp_calls: 0,
            callback_partial_u_calls: 0, json_required_bytes: 0,
        }
    }
}

struct CallbackState {
    // An opaque token is stored as usize because OdeProblem callbacks require
    // Send+Sync. Only the sequential driver below can consume these closures;
    // RUN_LOCK prevents concurrent FFI solves. Context lifetime is a C contract.
    context: usize,
    rhs: RhsCallback,
    jvp: JvpCallback,
    partial_u: RhsCallback,
    rhs_calls: AtomicU64,
    jvp_calls: AtomicU64,
    partial_calls: AtomicU64,
    first_error: Mutex<Option<String>>,
}

impl CallbackState {
    fn fail(&self, text: String) -> CoreError {
        if let Ok(mut error) = self.first_error.lock() {
            if error.is_none() { *error = Some(text.clone()); }
        }
        // InvalidInput is fatal to this driver; a failed foreign callback must
        // not become a retryable nonlinear/linear-error attempt.
        CoreError::InvalidInput(text)
    }

    fn eval(&self, kind: &str, u: f64, z: &[f64], v: Option<&[f64]>, out: &mut [f64])
        -> CoreResult<()> {
        if let Ok(error) = self.first_error.lock() {
            if let Some(text) = error.as_ref() {
                return Err(CoreError::InvalidInput(text.clone()));
            }
        }
        if !u.is_finite() || z.len() != out.len()
            || !z.iter().all(|x| x.is_finite())
            || v.is_some_and(|x| x.len() != z.len() || !x.iter().all(|q| q.is_finite())) {
            return Err(self.fail(format!("HE29_FFI_{kind}_INPUT")));
        }
        out.fill(f64::NAN); // Detect a callback that leaves an output unwritten.
        let context = self.context as *mut c_void;
        let rc = match v {
            Some(direction) => {
                self.jvp_calls.fetch_add(1, Ordering::Relaxed);
                // SAFETY: the foreign caller supplied a valid synchronous
                // callback/context. Rust slices remain alive for this call.
                unsafe { (self.jvp)(context, u, z.as_ptr(), direction.as_ptr(), z.len(), out.as_mut_ptr()) }
            }
            None => {
                let callback = if kind == "RHS" {
                    self.rhs_calls.fetch_add(1, Ordering::Relaxed); self.rhs
                } else {
                    self.partial_calls.fetch_add(1, Ordering::Relaxed); self.partial_u
                };
                unsafe { callback(context, u, z.as_ptr(), z.len(), out.as_mut_ptr()) }
            }
        };
        if rc != 0 { return Err(self.fail(format!("HE29_FFI_{kind}_CALLBACK_STATUS={rc}"))); }
        if !out.iter().all(|x| x.is_finite()) {
            return Err(self.fail(format!("HE29_FFI_{kind}_NONFINITE_OR_UNWRITTEN_OUTPUT")));
        }
        Ok(())
    }

    fn fill_counts(&self, stats: &mut He29Stats) {
        stats.callback_rhs_calls = self.rhs_calls.load(Ordering::Relaxed);
        stats.callback_jvp_calls = self.jvp_calls.load(Ordering::Relaxed);
        stats.callback_partial_u_calls = self.partial_calls.load(Ordering::Relaxed);
    }
}

struct Outcome { stats: He29Stats, state: Option<Vec<f64>>, telemetry: Value }

fn failure(n: usize, status: i32, message: impl Into<String>) -> Outcome {
    Outcome {
        stats: He29Stats::empty(n, status), state: None,
        telemetry: json!({"schema":"he29.vigilode.segment.v1", "status":status,
            "success":false, "message":message.into(), "vigilode_source":SOURCE,
            "new_scientific_admission":false}),
    }
}

fn solve(n: usize, z0: &[f64], callbacks: Arc<CallbackState>, initial_step: f64,
         max_step: f64, max_attempts: usize) -> Outcome {
    let cfg = AdaptiveStepConfig {
        rtol: RTOL, atol: ATOL, initial_step, max_step, max_attempts,
        ..Default::default()
    };
    if let Err(e) = cfg.validate() { return failure(n, INVALID, e.to_string()); }
    if max_step > 1.0 { return failure(n, INVALID, "normalized max_step must be <=1"); }
    let rhs_ctx = callbacks.clone();
    let jvp_ctx = callbacks.clone();
    let ft_ctx = callbacks.clone();
    let problem = match OdeProblem::new(
        "HE29-opt-in-scaled-segment", n,
        Arc::new(move |u,z,out| rhs_ctx.eval("RHS",u,z,None,out)),
        None, None,
        Some(Arc::new(move |u,z,v,out| jvp_ctx.eval("JVP",u,z,Some(v),out))),
        Some(Arc::new(move |u,z,out| ft_ctx.eval("PARTIAL_U",u,z,None,out))),
        false, None, None,
    ) {
        Ok(p) => p, Err(e) => return failure(n, INVALID, e.to_string()),
    };
    let output = match OutputSchedule::new(vec![0.0,1.0]) {
        Ok(o) => o, Err(e) => return failure(n, INVALID, e.to_string()),
    };
    let linear = LinearSolverConfig { method: LinearMethod::Gmres, ..Default::default() };
    let result = match integrate_sequential_matrix_free_adaptive_observed(
        &problem, (0.0,1.0), z0, &linear, &cfg, &output,
    ) {
        Ok(r) => r,
        Err(e) => {
            let mut o = failure(n, SOLVER_ERROR, e.to_string());
            callbacks.fill_counts(&mut o.stats);
            if callbacks.first_error.lock().ok().is_some_and(|e| e.is_some()) {
                o.stats.status = CALLBACK_ERROR; o.telemetry["status"] = json!(CALLBACK_ERROR);
            }
            return o;
        }
    };
    let complete = result.observed.success && result.observed.t.as_slice() == [0.0,1.0]
        && result.observed.y.len() == 2
        && result.observed.y.iter().all(|z| z.len() == n && z.iter().all(|x| x.is_finite()));
    let callback_error = callbacks.first_error.lock().ok().and_then(|e| e.clone());
    let status = if callback_error.is_some() { CALLBACK_ERROR }
        else if complete { OK } else { PARTIAL };
    let state = result.observed.y.last().filter(|z|
        z.len() == n && z.iter().all(|x| x.is_finite())).cloned();
    let mut stats = He29Stats::empty(n,status);
    stats.final_u = result.observed.t.last().copied().unwrap_or(0.0);
    stats.output_samples = result.observed.t.len();
    stats.internal_steps = result.observed.internal_steps;
    stats.output_clipped_steps = result.observed.output_clipped_steps;
    stats.attempts = result.diagnostics.attempts;
    stats.accepted_macro_steps = result.diagnostics.accepted_macro_steps;
    stats.rejected_macro_steps = result.diagnostics.rejected_macro_steps;
    stats.rhs_evaluations = result.observed.counters.rhs_evaluations;
    stats.jvp_vectors = result.observed.counters.jvp_vectors;
    stats.linear_iterations = result.observed.counters.linear_iterations;
    stats.direct_factorizations = result.observed.counters.direct_factorizations;
    callbacks.fill_counts(&mut stats);
    let finite_estimator = result.diagnostics.error_norms.last().copied().filter(|x| x.is_finite());
    let telemetry = json!({
        "schema":"he29.vigilode.segment.v1", "status":status, "success":status == OK,
        "complete_output":complete,
        "message":result.observed.message, "callback_error":callback_error,
        "vigilode_source":SOURCE, "method":"sequential-matrix-free-RODAS5P-GMRES",
        "independent_variable":"normalized segment u in [0,1]", "rtol":RTOL,"atol_scaled":ATOL,
        "initial_step":initial_step,"max_step":max_step,"max_attempts":max_attempts,
        "dense_output_used":false,"requested_output":[0.0,1.0],"returned_u":result.observed.t,
        "attempts":stats.attempts,"accepted_macro_steps":stats.accepted_macro_steps,
        "rejected_macro_steps":stats.rejected_macro_steps,"internal_steps":stats.internal_steps,
        "output_clipped_steps":stats.output_clipped_steps,"counters":result.observed.counters,
        "callback_rhs_calls":stats.callback_rhs_calls,"callback_jvp_calls":stats.callback_jvp_calls,
        "callback_partial_u_calls":stats.callback_partial_u_calls,
        "last_internal_error_estimate":finite_estimator,"error_estimate_is_global_bound":false,
        "new_scientific_admission":false,
    });
    Outcome { stats, state, telemetry }
}

#[unsafe(no_mangle)]
pub extern "C" fn he29_vigilode_abi_version() -> u32 { ABI_VERSION }

/// # Safety
/// The header specifies valid pointer lengths, non-overlap and callback lifetime.
/// Foreign exceptions, invalid addresses and process aborts cannot be contained.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn he29_vigilode_segment(
    n: usize, z0: *const f64, rhs: Option<RhsCallback>, jvp: Option<JvpCallback>,
    partial_u: Option<RhsCallback>, context: *mut c_void, initial_step: f64,
    max_step: f64, max_attempts: usize, z_out: *mut f64, stats: *mut He29Stats,
    json_out: *mut c_char, json_capacity: usize,
) -> i32 {
    if stats.is_null() || (stats as usize) % align_of::<He29Stats>() != 0 { return INVALID; }
    // Initialize the status before any operation that may fail.
    unsafe { stats.write(He29Stats::empty(n,INVALID)); }
    if json_out.is_null() || json_capacity == 0 || json_capacity > isize::MAX as usize {
        return INVALID;
    }
    unsafe { json_out.write(0); }
    let outcome = catch_unwind(AssertUnwindSafe(|| {
        if n == 0 || n > isize::MAX as usize / size_of::<f64>()
            || z0.is_null() || z_out.is_null()
            || (z0 as usize) % align_of::<f64>() != 0
            || (z_out as usize) % align_of::<f64>() != 0 {
            return failure(n,INVALID,"invalid state pointer, length or alignment");
        }
        let (Some(rhs),Some(jvp),Some(partial_u)) = (rhs,jvp,partial_u) else {
            return failure(n,INVALID,"RHS, JVP and partial_u callbacks are all required");
        };
        let initial = unsafe { std::slice::from_raw_parts(z0,n) };
        if !initial.iter().all(|x| x.is_finite()) {
            return failure(n,INVALID,"initial state must be finite");
        }
        let _guard = match RUN_LOCK.try_lock() {
            Ok(g) => g,
            Err(TryLockError::WouldBlock) => return failure(n,BUSY,"another bridge solve is active"),
            Err(TryLockError::Poisoned(e)) => e.into_inner(),
        };
        let callbacks = Arc::new(CallbackState {
            context:context as usize,rhs,jvp,partial_u,
            rhs_calls:AtomicU64::new(0),jvp_calls:AtomicU64::new(0),partial_calls:AtomicU64::new(0),
            first_error:Mutex::new(None),
        });
        solve(n,initial,callbacks,initial_step,max_step,max_attempts)
    }));
    let mut outcome = match outcome {
        Ok(o) => o,
        Err(_) => failure(n,PANIC,"Rust panic caught inside HE29 bridge; no endpoint admission"),
    };
    if let Some(state) = outcome.state.as_ref() {
        // No foreign call can occur during this copy. Non-overlap is required.
        unsafe { std::ptr::copy_nonoverlapping(state.as_ptr(),z_out,n); }
    }
    // Serialization is also contained; this path has only built-in JSON values.
    let encoded = catch_unwind(AssertUnwindSafe(|| serde_json::to_vec(&outcome.telemetry)));
    let bytes = match encoded {
        Ok(Ok(b)) => b,
        _ => {
            outcome.stats.status = PANIC;
            b"{\"status\":5,\"success\":false,\"message\":\"telemetry serialization failure\"}".to_vec()
        }
    };
    outcome.stats.json_required_bytes = bytes.len()+1;
    let status = if bytes.len() >= json_capacity { JSON_BUFFER_SMALL } else { outcome.stats.status };
    let count = bytes.len().min(json_capacity-1);
    unsafe {
        std::ptr::copy_nonoverlapping(bytes.as_ptr(),json_out.cast::<u8>(),count);
        json_out.add(count).write(0);
        outcome.stats.status = status;
        stats.write(outcome.stats);
    }
    status
}
