//! Specialized HH raw-U RODAS5P driver with the pinned tableau and PI controller.
//!
//! The original eight-stage equations and explicit time derivative are retained.
//! Only the frozen shifted solve is replaced by the analytic block action.
//! This endpoint-only driver owns its represented-clock contract; upstream's
//! private OutputCollector is not claimed to be called here.

use num_complex::Complex64;
use rodas5p_core::{CoreError, CoreResult, Rodas5pCoefficients, rodas5p_coefficients};
use rodas5p_integrators::{
    AdaptiveControllerState, AdaptiveStepConfig, rodas_next_step_after_attempt,
};
use serde::Serialize;
use wu088_hh_phys69_vigilode::{B, Request, T, put};

use crate::block::FrozenJacobian;
use crate::kernel::{Backend, HhKernel, KernelCounters};

const STAGES: usize = 8;
const MAX_STRUCTURED_STEP: f64 = 0.5;

#[derive(Clone, Debug, Serialize)]
pub struct StructuredResult {
    pub complete: bool,
    pub t: f64,
    pub y0: Vec<f64>,
    pub y: Vec<f64>,
    pub attempts: usize,
    pub accepted_steps: usize,
    pub rejected_steps: usize,
    pub state_reuses: usize,
    pub kernel_counts: KernelCounters,
    pub shifted_solves: usize,
    pub max_shifted_residual: f64,
    pub min_shifted_denominator: f64,
    pub workspace_bytes: usize,
    pub message: String,
}

/// Reusable O(n) stage storage. Successful attempts do not allocate heap memory.
///
/// The frozen cache is reused only for identical time/state bits and the same
/// immutable kernel configuration. An h-only retry recomputes the shift while
/// retaining the frozen Jacobian. A failed refresh invalidates all base data.
pub struct StructuredWorkspace {
    dimension: usize,
    coeffs: &'static Rodas5pCoefficients,
    frozen: FrozenJacobian,
    f0: Vec<f64>,
    ft: Vec<f64>,
    u: Vec<f64>,
    stage_state: Vec<f64>,
    stage_rhs: Vec<f64>,
    y_new: Vec<f64>,
    scratch: Vec<f64>,
    cached_y: Vec<f64>,
    cached_t_bits: u64,
    cached_config: Option<(usize, usize, Backend)>,
    valid: bool,
    shifted_solves: usize,
    state_reuses: usize,
    max_shifted_residual: f64,
    min_shifted_denominator: f64,
}

impl StructuredWorkspace {
    pub fn new(dimension: usize) -> CoreResult<Self> {
        if dimension < 2 || (dimension - 2) % 8 != 0 {
            return Err(CoreError::Dimension("HH structured workspace dimension".into()));
        }
        let channels = (dimension - 2) / 8;
        if !(22..=65).contains(&channels) {
            return Err(CoreError::Dimension("HH structured channel range".into()));
        }
        let coeffs = rodas5p_coefficients()?;
        if coeffs.stages() != STAGES {
            return Err(CoreError::Coefficients("HH requires eight RODAS5P stages".into()));
        }
        for i in 0..STAGES {
            if !(0.0..=1.0).contains(&coeffs.c[i]) {
                return Err(CoreError::Coefficients("HH stage outside radial interval".into()));
            }
            for j in i..STAGES {
                if coeffs.a[(i, j)] != 0.0 || coeffs.c_matrix[(i, j)] != 0.0 {
                    return Err(CoreError::Coefficients("nontriangular RODAS5P raw tableau".into()));
                }
            }
        }
        Ok(Self {
            dimension,
            coeffs,
            frozen: FrozenJacobian::new(channels),
            f0: vec![0.0; dimension],
            ft: vec![0.0; dimension],
            u: vec![0.0; STAGES * dimension],
            stage_state: vec![0.0; dimension],
            stage_rhs: vec![0.0; dimension],
            y_new: vec![0.0; dimension],
            scratch: vec![0.0; dimension],
            cached_y: vec![0.0; dimension],
            cached_t_bits: 0,
            cached_config: None,
            valid: false,
            shifted_solves: 0,
            state_reuses: 0,
            max_shifted_residual: 0.0,
            min_shifted_denominator: f64::INFINITY,
        })
    }

    pub fn y_new(&self) -> &[f64] {
        &self.y_new
    }

    /// Raw U stage of the latest successful attempt; stage index must be < 8.
    pub fn stage(&self, index: usize) -> &[f64] {
        &self.u[index * self.dimension..(index + 1) * self.dimension]
    }

    pub fn shifted_solves(&self) -> usize {
        self.shifted_solves
    }

    pub fn state_reuses(&self) -> usize {
        self.state_reuses
    }

    pub fn max_shifted_residual(&self) -> f64 {
        self.max_shifted_residual
    }

    /// If no shift was evaluated, return the neutral identity value 1.
    pub fn min_shifted_denominator(&self) -> f64 {
        if self.min_shifted_denominator.is_finite() {
            self.min_shifted_denominator
        } else {
            1.0
        }
    }

    /// Retained heap capacity, excluding static upstream tableau and result copies.
    pub fn workspace_bytes(&self) -> usize {
        (self.f0.capacity()
            + self.ft.capacity()
            + self.u.capacity()
            + self.stage_state.capacity()
            + self.stage_rhs.capacity()
            + self.y_new.capacity()
            + self.scratch.capacity()
            + self.cached_y.capacity())
            * std::mem::size_of::<f64>()
            + self.frozen.workspace_bytes()
    }

    pub fn invalidate(&mut self) {
        self.valid = false;
        self.cached_config = None;
        self.frozen.invalidate();
    }

    /// Return the existing raw-U embedded error norm. Only y_new/stages are
    /// candidates: this method does not commit an integration state.
    #[allow(clippy::too_many_arguments)]
    pub fn attempt(
        &mut self,
        kernel: &mut HhKernel,
        t: f64,
        y: &[f64],
        h: f64,
        fresh: bool,
        atol: f64,
        rtol: f64,
    ) -> CoreResult<f64> {
        if kernel.dimension() != self.dimension || y.len() != self.dimension {
            self.invalidate();
            return Err(CoreError::Dimension("HH structured attempt shape".into()));
        }
        if !t.is_finite()
            || !(0.0..=T - B).contains(&t)
            || !h.is_finite()
            || h <= 0.0
            || h > MAX_STRUCTURED_STEP
            || t + h > T - B
            || t + h <= t
        {
            return Err(CoreError::InvalidInput("HH structured time/step outside fixed contract".into()));
        }
        if !atol.is_finite() || !rtol.is_finite() || atol < 0.0 || rtol < 0.0 {
            return Err(CoreError::InvalidInput("HH structured invalid error tolerances".into()));
        }
        if y.iter().any(|x| !x.is_finite()) {
            self.invalidate();
            return Err(CoreError::NonFinite("HH structured base state".into()));
        }

        let key = kernel.config_key();
        let same_base = self.valid
            && self.cached_t_bits == t.to_bits()
            && self.cached_config == Some(key)
            && self.cached_y.iter().zip(y).all(|(a, b)| a.to_bits() == b.to_bits());
        if fresh || !same_base {
            // Never leave a partly refreshed f0, ft or Jacobian marked usable.
            self.invalidate();
            kernel.rhs(t, y, &mut self.f0)?;
            kernel.partial_tau(t, y, &mut self.ft)?;
            kernel.freeze(t, y, &mut self.frozen)?;
            self.cached_y.copy_from_slice(y);
            self.cached_t_bits = t.to_bits();
            self.cached_config = Some(key);
            self.valid = true;
        } else {
            self.state_reuses += 1;
        }

        let n = self.dimension;
        let gamma = self.coeffs.gamma;
        let shift = h * gamma;
        let minimum = self.frozen.min_denominator(shift)?;
        self.min_shifted_denominator = self.min_shifted_denominator.min(minimum);
        for i in 0..STAGES {
            if i == 0 {
                self.stage_rhs.copy_from_slice(&self.f0);
            } else {
                self.stage_state.copy_from_slice(y);
                for j in 0..i {
                    let a = self.coeffs.a[(i, j)];
                    if a != 0.0 {
                        for (x, value) in self.stage_state.iter_mut().zip(&self.u[j * n..(j + 1) * n]) {
                            *x += a * value;
                        }
                    }
                }
                kernel.rhs(t + self.coeffs.c[i] * h, &self.stage_state, &mut self.stage_rhs)?;
            }
            // Preserve the parent raw-U coefficient/accumulation order.
            for x in &mut self.stage_rhs {
                *x *= shift;
            }
            for j in 0..i {
                let c = self.coeffs.c_matrix[(i, j)];
                if c != 0.0 {
                    let weight = gamma * c;
                    for (x, value) in self.stage_rhs.iter_mut().zip(&self.u[j * n..(j + 1) * n]) {
                        *x += weight * value;
                    }
                }
            }
            // The original HH system is explicitly nonautonomous.
            let time_weight = shift * h * self.coeffs.gamma_rows[i];
            for (x, value) in self.stage_rhs.iter_mut().zip(&self.ft) {
                *x += time_weight * value;
            }
            self.shifted_solves += 1;
            let residual = self.frozen.solve(
                shift,
                &self.stage_rhs,
                &mut self.u[i * n..(i + 1) * n],
                &mut self.scratch,
            )?;
            self.max_shifted_residual = self.max_shifted_residual.max(residual);
        }

        self.y_new.copy_from_slice(y);
        for i in 0..STAGES {
            let b = self.coeffs.b_code[i];
            if b != 0.0 {
                for (x, value) in self.y_new.iter_mut().zip(&self.u[i * n..(i + 1) * n]) {
                    *x += b * value;
                }
            }
        }
        if self.y_new.iter().any(|x| !x.is_finite()) {
            return Err(CoreError::NonFinite("HH structured candidate state".into()));
        }
        let mut sum = 0.0;
        for ((error, old), new) in self.u[(STAGES - 1) * n..].iter().zip(y).zip(&self.y_new) {
            let scale = atol + rtol * old.abs().max(new.abs());
            if !(scale.is_finite() && scale > 0.0) {
                return Err(CoreError::InvalidInput("HH structured WRMS scale".into()));
            }
            let value = error / scale;
            sum += value * value;
        }
        let norm = (sum / n as f64).sqrt();
        Ok(if norm.is_finite() { norm } else { f64::INFINITY })
    }
}

/// Endpoint-only represented clock, bounded by both tf and a strict max_step.
/// The accepted solver step is always end - t, never the unrepresented request.
/// A rejected trial is strictly shortened even when rounding erases shrinkage.
fn represented_trial(
    t: f64,
    requested: f64,
    tf: f64,
    maximum: f64,
    rejected: Option<f64>,
) -> CoreResult<Option<f64>> {
    if !t.is_finite() || !tf.is_finite() || tf < t
        || !maximum.is_finite() || maximum <= 0.0
    {
        return Err(CoreError::InvalidInput("HH represented-clock input".into()));
    }
    let proposed = requested.min(maximum);
    if proposed.is_nan() || proposed <= 0.0 || t + proposed <= t {
        return Ok(None);
    }
    let mut end = (t + proposed).min(tf);
    if let Some(previous) = rejected {
        if end - t >= previous {
            end = (t + previous).next_down().min(tf);
        }
    }
    if end - t > maximum {
        end = end.next_down();
    }
    let h = end - t;
    if !(end.is_finite() && end > t && h > 0.0 && h <= maximum && end <= tf && t + h == end) {
        return Err(CoreError::InvalidInput("HH represented clock cannot advance within cap".into()));
    }
    Ok(Some(h))
}

pub fn solve_structured(
    request: &Request,
    seed: &[(Complex64, Complex64)],
    backend: Backend,
) -> CoreResult<StructuredResult> {
    request.validate()?;
    if request.max_step > MAX_STRUCTURED_STEP {
        return Err(CoreError::InvalidInput("HH structured max_step must be <= 0.5".into()));
    }
    let adaptive: AdaptiveStepConfig = request.adaptive();
    let mut kernel = HhKernel::new(request.lmax, request.angular_nodes, backend)?;
    let dimension = kernel.dimension();
    let channels = request.lmax + 1;
    if seed.len() != channels {
        return Err(CoreError::Dimension("HH structured seed channel count".into()));
    }
    let mut y0 = vec![0.0; dimension];
    for (j, &(f, g)) in seed.iter().enumerate() {
        if !f.re.is_finite() || !f.im.is_finite()
            || !g.re.is_finite() || !g.im.is_finite() || f.norm() == 0.0
        {
            return Err(CoreError::InvalidInput("HH structured invalid seed".into()));
        }
        put(&mut y0, j, f);
        put(&mut y0, channels + j, g);
    }
    let mut y = y0.clone();
    let mut workspace = StructuredWorkspace::new(dimension)?;
    let mut controller = AdaptiveControllerState::default();
    let (mut t, tf) = (0.0, T - B);
    let mut requested_h = adaptive.initial_step.min(tf);
    let (mut attempts, mut accepted_steps, mut rejected_steps) = (0, 0, 0);
    let mut fresh = true;
    let mut message = String::from("maximum attempts reached");
    let mut failed_attempt_messages = Vec::new();

    while t < tf && attempts < adaptive.max_attempts {
        let trial = represented_trial(
            t, requested_h, tf, adaptive.max_step, controller.last_rejected_trial(),
        );
        let trial_h = match trial {
            Ok(Some(h)) => h,
            Ok(None) => {
                message = "proposed step does not advance represented time".into();
                break;
            }
            Err(error) => {
                message = format!("represented-clock failure: {error}");
                break;
            }
        };
        // Compare represented endpoints, including an admissible final short step.
        if t + trial_h < t + adaptive.min_step && t + trial_h < tf {
            message = "minimum represented step reached".into();
            break;
        }
        let requested_for_controller = requested_h.min(adaptive.max_step);
        let clipped = trial_h < requested_for_controller && t + trial_h == tf;
        attempts += 1;
        let outcome = workspace.attempt(
            &mut kernel, t, &y, trial_h, fresh, adaptive.atol, adaptive.rtol,
        );
        let mut retryable = true;
        let error = match outcome {
            Ok(error) => error,
            Err(error) => {
                retryable = matches!(&error, CoreError::LinearSolve(_) | CoreError::NonFinite(_));
                failed_attempt_messages.push(format!(
                    "attempt {attempts}, tau {t:.17e}, h {trial_h:.17e}: {error}"
                ));
                f64::INFINITY
            }
        };
        let accepted = error.is_finite() && error <= 1.0;
        if accepted {
            t += trial_h;
            y.copy_from_slice(workspace.y_new());
            accepted_steps += 1;
            fresh = true;
        } else {
            rejected_steps += 1;
            fresh = false;
        }
        if !retryable {
            message = "nonretryable attempted step failure".into();
            break;
        }
        if t == tf {
            message = "success".into();
            break;
        }
        requested_h = match rodas_next_step_after_attempt(
            &mut controller, &adaptive, requested_for_controller, trial_h,
            error, accepted, clipped,
        ) {
            Ok(h) => h,
            Err(error) => {
                message = format!("controller failure: {error}");
                break;
            }
        };
    }
    let complete = t == tf;
    if complete {
        message = "success".into();
    }
    if !failed_attempt_messages.is_empty() {
        message.push_str("; preserved failed attempts: ");
        message.push_str(&failed_attempt_messages.join(" | "));
    }
    Ok(StructuredResult {
        complete,
        t,
        y0,
        y,
        attempts,
        accepted_steps,
        rejected_steps,
        state_reuses: workspace.state_reuses(),
        kernel_counts: kernel.counts.clone(),
        shifted_solves: workspace.shifted_solves(),
        max_shifted_residual: workspace.max_shifted_residual(),
        min_shifted_denominator: workspace.min_shifted_denominator(),
        workspace_bytes: workspace.workspace_bytes() + kernel.workspace_bytes(),
        message,
    })
}

#[cfg(test)]
mod clock_tests {
    use super::represented_trial;

    #[test]
    fn strict_cap_and_exact_quarter_boundary_near_38() {
        let t = 37.7_f64;
        let maximum = 0.1_f64;
        // Rounding this time sum makes its represented interval exceed 0.1.
        let natural_end = t + maximum;
        assert!(natural_end - t > maximum);
        let h = represented_trial(t, maximum, 38.0, maximum, None)
            .unwrap().unwrap();
        assert!(h > 0.0 && h <= maximum);
        assert_eq!(t + h, natural_end.next_down());

        let boundary = represented_trial(37.75, 0.25, 38.0, 0.25, None)
            .unwrap().unwrap();
        assert_eq!(boundary, 0.25);
        assert_eq!(37.75 + boundary, 38.0);
    }

    #[test]
    fn adjacent_clock_requires_a_cap_that_can_reach_it() {
        let end = 38.0_f64;
        let t = end.next_down();
        let ulp = end - t;
        assert_eq!(represented_trial(t, 0.25 * ulp, end, 0.25, None).unwrap(), None);
        // Here the half-ULP tie rounds upward, but the hard cap must still win.
        assert!(represented_trial(t, ulp, end, 0.5 * ulp, None).is_err());
        let h = represented_trial(t, ulp, end, ulp, None).unwrap().unwrap();
        assert_eq!(h, ulp);
        assert_eq!(t + h, end);
    }

    #[test]
    fn rejection_strictly_shortens_even_when_nominal_shrink_rounds_away() {
        let t = 37.0_f64;
        let ulp = t.next_up() - t;
        let rejected = 3.0 * ulp;
        let proposal = 2.55 * ulp;
        assert_eq!(t + proposal, t + rejected);
        let h = represented_trial(t, proposal, 38.0, 0.25, Some(rejected))
            .unwrap().unwrap();
        assert_eq!(h, 2.0 * ulp);
        assert!(h < rejected);
        // A one-ULP rejected step cannot be silently retried at the same end.
        assert!(represented_trial(t, 0.75 * ulp, 38.0, 0.25, Some(ulp)).is_err());
    }

    #[test]
    fn final_two_ulp_landing_integrates_only_the_remaining_interval() {
        let tf = 38.0_f64;
        let t = tf.next_down().next_down();
        let remaining = tf - t;
        let h = represented_trial(t, 0.25, tf, 0.25, None).unwrap().unwrap();
        assert_eq!(h, remaining);
        assert!(h < 0.25);
        assert_eq!(t + h, tf);
    }
}
