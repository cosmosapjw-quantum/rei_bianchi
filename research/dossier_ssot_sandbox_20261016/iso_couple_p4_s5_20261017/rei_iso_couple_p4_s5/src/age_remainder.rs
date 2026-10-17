//! P4/S5 opt-in bounded nonzero photon-age truncation, never implicit absorption.
//!
//! Scoped guarantee: for a *fixed nonnegative opacity history*, direct removed
//! photons contribute at most their removed photon count to all subsequent direct
//! absorption/observer counts, and at most the model-geodesic energy envelope
//! to future direct photo energy. Nonlinear gas feedback is NOT bounded here.
//! A separate numerical remainder owns photons that are no longer transported.
use crate::axbi_sources::SOURCE_ID;
use crate::full_network::{EV_J, NetworkConfig, NetworkError};
use crate::retarded_transport_threshold::{PositiveThresholdBridge, RetardedDiagnostics};
use crate::source_age::{AgeHistory, AgeStep};

#[derive(Clone, Copy, Debug)]
pub struct TailControls {
    /// Cut only nonzero cohorts with represented photon number <= this value.
    pub max_weight_per_cohort_com3: f64,
    /// Cumulative maximum count of photon packets omitted per reference comoving m^3.
    pub max_cumulative_number_com3: f64,
    /// Cumulative upper bound on direct photo energy through horizon, J/comoving m^3.
    pub max_cumulative_energy_j_com3: f64,
    /// Cumulative *direct* event count envelope for each absorber HI/HeI/HeII/DI.
    /// Does NOT bound nonlinear gas-mediated changes in other photon events.
    pub max_direct_species_events_com3: [f64; 4],
    /// A known endpoint of the prescribed geometry; no extrapolation.
    pub horizon_s: f64,
}
impl TailControls {
    fn validate(self, bridge: &PositiveThresholdBridge, t: f64) -> Result<(), NetworkError> {
        if !self.max_weight_per_cohort_com3.is_finite()
            || self.max_weight_per_cohort_com3 < 0.
            || !self.max_cumulative_number_com3.is_finite()
            || self.max_cumulative_number_com3 < 0.
            || !self.max_cumulative_energy_j_com3.is_finite()
            || self.max_cumulative_energy_j_com3 < 0.
            || self
                .max_direct_species_events_com3
                .iter()
                .any(|x| !x.is_finite() || *x < 0.)
            || !self.horizon_s.is_finite()
            || t > self.horizon_s
            || self.horizon_s > bridge.0.geometry.time_domain_s[1]
            || t < bridge.0.geometry.time_domain_s[0]
        {
            return Err(NetworkError::InputOutsideDomain);
        }
        Ok(())
    }
}

/// Direct source photon deletion remainder, NOT an actual atom-photon event.
#[derive(Clone, Copy, Debug, Default)]
pub struct TailRemainder {
    pub cumulative_removed_number_com3: f64,
    pub cumulative_removed_energy_at_cut_j_com3: f64,
    /// Upper model-energy envelope through the registered horizon.
    pub cumulative_future_photo_energy_bound_j_com3: f64,
    pub direct_species_events_upper_com3: [f64; 4],
    pub count_removed_cohorts: usize,
    pub count_removed_nonzero: usize,
}

#[derive(Clone, Debug)]
pub struct BudgetedAgeHistory {
    history: AgeHistory,
    controls: TailControls,
    remainder: TailRemainder,
}
impl BudgetedAgeHistory {
    pub fn history(&self) -> &AgeHistory {
        &self.history
    }
    pub fn controls(&self) -> TailControls {
        self.controls
    }
    pub fn remainder(&self) -> TailRemainder {
        self.remainder
    }
}
#[derive(Clone, Debug)]
pub struct BudgetedStep {
    pub state: BudgetedAgeHistory,
    pub physics: AgeStep,
    pub physics_diagnostics: RetardedDiagnostics,
    pub new_removed_nonzero: usize,
    pub new_removed_exact_zero: usize,
    pub retained_count: usize,
    /// With actual gas coupling this is only a numerical inventory identity.
    pub photon_inventory_relative_residual: f64,
}

/// Round upward at each nonnegative floating-point operation. IEEE-754 rounding
/// is covered; uncertainty in input cross-section / geometry isn't.
fn upper_add(a: f64, b: f64) -> Result<f64, NetworkError> {
    if !(a.is_finite() && b.is_finite()) || a < 0. || b < 0. {
        return Err(NetworkError::NonFinite);
    }
    let z = a + b;
    if !z.is_finite() {
        return Err(NetworkError::NonFinite);
    }
    if b == 0. { Ok(z) } else { Ok(z.next_up()) }
}
fn upper_mul(a: f64, b: f64) -> Result<f64, NetworkError> {
    if !(a.is_finite() && b.is_finite()) || a < 0. || b < 0. {
        return Err(NetworkError::NonFinite);
    }
    if a == 0. || b == 0. {
        return Ok(0.);
    }
    let z = a * b;
    if !z.is_finite() {
        return Err(NetworkError::NonFinite);
    }
    // A positive subnormal product that rounds to zero is bounded above by
    // the least positive representable float, not a fatal physics failure.
    if z == 0. {
        return Ok(f64::from_bits(1));
    }
    Ok(z.next_up())
}

/// For axisymmetric constant directional rates, d ln E/dt is a convex mixture
/// of -H_i, hence E_future <= E_now exp(max(0,-min H_i) * horizon_duration).
fn energy_growth_upper(
    bridge: &PositiveThresholdBridge,
    now: f64,
    horizon: f64,
) -> Result<f64, NetworkError> {
    let snapshot = bridge.0.snapshot(now)?;
    let hmin = snapshot
        .hubble_per_s
        .into_iter()
        .fold(f64::INFINITY, f64::min);
    if !hmin.is_finite() || now > horizon {
        return Err(NetworkError::InputOutsideDomain);
    }
    // Bound the represented rate*time product from above, including rounding.
    let positive_rate = (-hmin).max(0.);
    if positive_rate == 0. {
        return Ok(1.0_f64.next_up());
    }
    let duration_upper = (horizon - now).next_up();
    let exponent_upper = upper_mul(positive_rate, duration_upper)?;
    let value = exponent_upper.exp();
    if !value.is_finite() || value <= 0. {
        return Err(NetworkError::NonFinite);
    }
    Ok(value.next_up())
}

#[derive(Clone, Copy, Debug)]
struct Candidate {
    idx: usize,
    weight: f64,
    energy_cut_j: f64,
    energy_bound_j: f64,
    species_possible: [bool; 4],
}

impl PositiveThresholdBridge {
    pub fn with_tail_budget(
        &self,
        initial: AgeHistory,
        conf: &NetworkConfig,
        controls: TailControls,
    ) -> Result<BudgetedAgeHistory, NetworkError> {
        controls.validate(self, initial.time_s)?;
        if conf.photon_source != SOURCE_ID || !conf.use_photo {
            return Err(NetworkError::SourceMismatch);
        }
        if initial
            .cohorts
            .iter()
            .any(|c| !c.n_comoving_m3.is_finite() || c.n_comoving_m3 < 0.)
        {
            return Err(NetworkError::NonFinite);
        }
        Ok(BudgetedAgeHistory {
            history: initial,
            controls,
            remainder: TailRemainder::default(),
        })
    }

    /// Advance the unchanged native Rust transport and chemistry first; only
    /// afterwards apply an error-budgeted approximation to the accepted state.
    /// All pruning is transactional, one explicit operation in the shadow lane.
    pub fn advance_budgeted(
        &self,
        current: &BudgetedAgeHistory,
        conf: &NetworkConfig,
        dt: f64,
    ) -> Result<BudgetedStep, NetworkError> {
        current.controls.validate(self, current.history.time_s)?;
        if !dt.is_finite() || dt <= 0. || current.history.time_s + dt > current.controls.horizon_s {
            return Err(NetworkError::InputOutsideDomain);
        }
        let (mut physics, diagnostics) =
            self.advance_with_diagnostics(&current.history, conf, dt)?;
        let now = physics.state.time_s;
        current.controls.validate(self, now)?;
        let controls = current.controls;
        let growth = energy_growth_upper(self, now, controls.horizon_s)?;
        let g = self.0.snapshot(now)?;
        let edges = [13.60, 24.59, 54.42, conf.deuterium.chi_d_ev()];
        let mut candidates = Vec::new();
        let mut zeros = 0usize;
        for (i, co) in physics.state.cohorts.iter().enumerate() {
            let weight = co.n_comoving_m3;
            if !weight.is_finite() || weight < 0. {
                return Err(NetworkError::NonFinite);
            }
            if weight == 0. {
                zeros += 1;
                continue;
            }
            if weight > controls.max_weight_per_cohort_com3 {
                continue;
            }
            let en = co.ray_at(&g)?.energy_ev;
            if !en.is_finite() || en <= 0. {
                return Err(NetworkError::NonFinite);
            }
            let e_cut = upper_mul(upper_mul(weight, en)?, EV_J)?;
            let e_bound = upper_mul(e_cut, growth)?;
            let e_future = upper_mul(en, growth)?;
            candidates.push(Candidate {
                idx: i,
                weight,
                energy_cut_j: e_cut,
                energy_bound_j: e_bound,
                species_possible: edges.map(|edge| e_future >= edge),
            });
        }
        // Maximize cohort deletion count under fixed budgets, deterministic for ties.
        candidates.sort_by(|a, b| a.weight.total_cmp(&b.weight).then(a.idx.cmp(&b.idx)));
        let mut new_rem = current.remainder;
        let mut mask = vec![false; physics.state.cohorts.len()];
        let mut new_removed = 0usize;
        for x in candidates {
            let next_n = upper_add(new_rem.cumulative_removed_number_com3, x.weight)?;
            let next_e = upper_add(
                new_rem.cumulative_future_photo_energy_bound_j_com3,
                x.energy_bound_j,
            )?;
            if next_n > controls.max_cumulative_number_com3
                || next_e > controls.max_cumulative_energy_j_com3
            {
                continue;
            }
            let cut_e = upper_add(
                new_rem.cumulative_removed_energy_at_cut_j_com3,
                x.energy_cut_j,
            )?;
            let mut species = new_rem.direct_species_events_upper_com3;
            for (i, yes) in x.species_possible.into_iter().enumerate() {
                if yes {
                    species[i] = upper_add(species[i], x.weight)?;
                }
            }
            if species
                .iter()
                .zip(controls.max_direct_species_events_com3)
                .any(|(value, cap)| *value > cap)
            {
                continue;
            }
            new_rem.cumulative_removed_number_com3 = next_n;
            new_rem.cumulative_future_photo_energy_bound_j_com3 = next_e;
            new_rem.cumulative_removed_energy_at_cut_j_com3 = cut_e;
            new_rem.direct_species_events_upper_com3 = species;
            mask[x.idx] = true;
            new_removed += 1;
        }
        let before = physics.state.cohorts.len();
        let mut i = 0usize;
        physics.state.cohorts.retain(|x| {
            let keep = x.n_comoving_m3 != 0. && !mask[i];
            i += 1;
            keep
        });
        new_rem.count_removed_cohorts += before - physics.state.cohorts.len();
        new_rem.count_removed_nonzero += new_removed;
        // Source count = absorbed + retained + numerical remainder. A removed
        // photon is never reclassified as an absorbed photon or thermal heating.
        let remaining = physics
            .state
            .cohorts
            .iter()
            .map(|x| x.n_comoving_m3)
            .sum::<f64>();
        let total = physics.state.source_injected_count_com3;
        if total <= 0. || !total.is_finite() {
            return Err(NetworkError::PhysicsLedger);
        }
        let rhs = (physics.state.photon_absorbed_count_com3 + remaining)
            + new_rem.cumulative_removed_number_com3;
        let residual = (rhs - total).abs() / total;
        if !residual.is_finite() || residual > 1e-10 {
            return Err(NetworkError::PhysicsLedger);
        }
        let history = BudgetedAgeHistory {
            history: physics.state.clone(),
            controls,
            remainder: new_rem,
        };
        Ok(BudgetedStep {
            state: history,
            physics,
            physics_diagnostics: diagnostics,
            new_removed_nonzero: new_removed,
            new_removed_exact_zero: zeros,
            retained_count: before - new_removed - zeros,
            photon_inventory_relative_residual: residual,
        })
    }
}
