//! S10 native same-interval inner/outer budget adapter.
//! No production-source edits, extrapolation, photon pruning or silent clipping.
//! All pairs in one attempt borrow the SAME immutable initial state and physics.
//! The loose pair defines ONE scale vector frozen throughout its inner ladder.
//! Differences between precisions are sensitivity diagnostics, not rigorous error bounds.
use crate::bound_adaptive::LocalTolerances;
use crate::bound_midpoint::MidpointBridge;
use crate::budget_kernel::{Action, BudgetError, Precision, Report, Scale};
use crate::full_network::{NetworkConfig, NetworkError};
use crate::source_age::AgeHistory;
#[derive(Clone, Debug)]
pub struct NativeBudgetControls {
    pub beta: f64,
    pub ladder: Vec<Precision>,
    pub pair_budget: usize,
}
impl Default for NativeBudgetControls {
    fn default() -> Self {
        Self {
            beta: 0.25,
            ladder: [1e-8, 1e-10, 1e-12, 1e-14]
                .map(|x| Precision {
                    relative: x,
                    absolute: x * 1e-3,
                })
                .to_vec(),
            pair_budget: 4,
        }
    }
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum AdapterError {
    Network(NetworkError),
    Policy(BudgetError),
    InvalidControls,
    ProjectionMismatch,
}
impl From<NetworkError> for AdapterError {
    fn from(e: NetworkError) -> Self {
        Self::Network(e)
    }
}
impl From<BudgetError> for AdapterError {
    fn from(e: BudgetError) -> Self {
        Self::Policy(e)
    }
}
#[derive(Clone, Debug)]
pub struct Comparison {
    pub loose: Precision,
    pub tight: Precision,
    pub report: Report,
    /// Raw four-corner observations, retained for independent policy readback.
    pub four: [Vec<Datum>; 4],
}
#[derive(Clone, Debug)]
pub struct Accepted {
    pub state: AgeHistory,
    pub photo_events_com3: [f64; 4],
    pub precision: Precision,
    pub max_energy_ledger: f64,
}
#[derive(Clone, Debug)]
pub struct BudgetTrial {
    pub action: Action,
    pub accepted: Option<Box<Accepted>>,
    pub comparisons: Vec<Comparison>,
    pub scales: Vec<Scale>,
    pub pairs_evaluated: usize,
    pub next_h_s: f64,
    pub reason: Option<NetworkError>,
}

use crate::bound_adaptive::{events_comoving, next_step, photon_projection};
use crate::bound_midpoint::Centering;
use crate::budget_kernel::{self, Context, Datum, Pair};
use crate::isotope_state::IsotopeSpecies as S;
use std::collections::{BTreeMap, BTreeSet};

struct Evaluation {
    policy: Pair,
    fine: AgeHistory,
    events: [f64; 4],
    ledger: f64,
}
fn config_at(c: &NetworkConfig, p: Precision) -> NetworkConfig {
    let mut x = *c;
    x.cx_controls.rtol = p.relative;
    x.cx_controls.atol_normalized = p.absolute;
    x
}
fn projection(
    b: &MidpointBridge,
    s: &AgeHistory,
    e: [f64; 4],
) -> Result<BTreeMap<String, Datum>, AdapterError> {
    let mut out = BTreeMap::new();
    let mut add = |key: String, unit: &str, value: f64| {
        out.insert(
            key.clone(),
            Datum {
                key,
                unit: unit.into(),
                value,
            },
        );
    };
    for sp in S::ALL {
        add(
            format!("nucleus_{}", sp as usize),
            "proper_m^-3",
            s.full.gas.nuclei.density_m3(sp),
        );
    }
    for (k, v) in [
        ("thermal", s.full.gas.thermal_j_m3),
        ("escape", s.full.escaped_j_m3),
        ("cmb", s.full.cmb_reservoir_j_m3),
    ] {
        add(k.into(), "J/proper_m^3", v);
    }
    let p = photon_projection(b, s)?;
    add("photons".into(), "comoving_m^-3", p.count);
    add("photon_energy".into(), "J/comoving_m^3", p.energy_j);
    add("energy_P2".into(), "dimensionless", p.q2_energy);
    add(
        "source_count".into(),
        "comoving_m^-3",
        s.source_injected_count_com3,
    );
    add(
        "source_energy".into(),
        "J/comoving_m^3",
        s.source_injected_energy_j_com3,
    );
    for (j, v) in e.iter().enumerate() {
        add(format!("photo_event_{j}"), "comoving_m^-3", *v);
    }
    for ((spectral, angular), v) in p.groups {
        add(
            format!("photon_group_{spectral}_{angular}"),
            "comoving_m^-3",
            v,
        );
    }
    Ok(out)
}
fn evaluate(
    b: &MidpointBridge,
    s: &AgeHistory,
    c: &NetworkConfig,
    h: f64,
    p: Precision,
    context: &Context,
) -> Result<Evaluation, AdapterError> {
    let config = config_at(c, p);
    let end = s.time_s + h;
    let coarse = b.advance(s, &config, h)?;
    let f = b.advance(s, &config, h / 2.)?;
    let z = b.advance(&f.state, &config, end - f.state.time_s)?;
    if coarse.state.time_s.to_bits() != end.to_bits() || z.state.time_s.to_bits() != end.to_bits() {
        return Err(AdapterError::ProjectionMismatch);
    }
    let ce = events_comoving(b, &coarse, s.time_s)?;
    let f1 = events_comoving(b, &f, s.time_s)?;
    let f2 = events_comoving(b, &z, f.state.time_s)?;
    let fe = std::array::from_fn(|j| f1[j] + f2[j]);
    let mut cp = projection(b, &coarse.state, ce)?;
    let mut fp = projection(b, &z.state, fe)?;
    let keys: BTreeSet<_> = cp.keys().chain(fp.keys()).cloned().collect();
    // Only an absent photon group may mean zero. Fixed gas/event fields may not
    // silently disappear; a new group at a later precision fails assess labels.
    for k in keys {
        if !cp.contains_key(&k) || !fp.contains_key(&k) {
            if !k.starts_with("photon_group_") {
                return Err(AdapterError::ProjectionMismatch);
            }
            let zero = Datum {
                key: k.clone(),
                unit: "comoving_m^-3".into(),
                value: 0.,
            };
            cp.entry(k.clone()).or_insert_with(|| zero.clone());
            fp.entry(k).or_insert(zero);
        }
    }
    Ok(Evaluation {
        policy: Pair {
            context: context.clone(),
            precision: p,
            coarse: cp.into_values().collect(),
            fine: fp.into_values().collect(),
        },
        fine: z.state,
        events: fe,
        ledger: f
            .global_energy_relative_error
            .max(z.global_energy_relative_error),
    })
}
fn absolute_tolerance(key: &str, t: &LocalTolerances) -> Result<f64, AdapterError> {
    if let Some(x) = key.strip_prefix("nucleus_") {
        return x
            .parse::<usize>()
            .ok()
            .and_then(|j| t.nuclei_m3.get(j).copied())
            .ok_or(AdapterError::ProjectionMismatch);
    }
    if let Some(x) = key.strip_prefix("photo_event_") {
        return x
            .parse::<usize>()
            .ok()
            .and_then(|j| t.photo_events_com3.get(j).copied())
            .ok_or(AdapterError::ProjectionMismatch);
    }
    if key.starts_with("photon_group_") {
        return Ok(t.photon_number_com3);
    }
    match key {
        "thermal" | "escape" | "cmb" => Ok(t.gas_energy_j_m3),
        "photons" | "source_count" => Ok(t.photon_number_com3),
        "photon_energy" | "source_energy" => Ok(t.photon_energy_j_com3),
        "energy_P2" => Ok(t.angular_p2_energy),
        _ => Err(AdapterError::ProjectionMismatch),
    }
}
fn freeze(p: &Pair, t: &LocalTolerances) -> Result<Vec<Scale>, AdapterError> {
    if p.coarse.len() != p.fine.len() {
        return Err(AdapterError::ProjectionMismatch);
    }
    p.coarse
        .iter()
        .zip(&p.fine)
        .map(|(a, b)| {
            if a.key != b.key || a.unit != b.unit {
                return Err(AdapterError::ProjectionMismatch);
            }
            let value = absolute_tolerance(&a.key, t)? + t.rtol * a.value.abs().max(b.value.abs());
            if !value.is_finite() || value <= 0. {
                return Err(AdapterError::Policy(BudgetError::InvalidScale));
            }
            Ok(Scale {
                key: a.key.clone(),
                unit: a.unit.clone(),
                value,
            })
        })
        .collect()
}
fn validate_controls(v: &NativeBudgetControls) -> Result<(), AdapterError> {
    if !v.beta.is_finite()
        || v.beta <= 0.
        || v.beta >= 1.
        || !(2..=64).contains(&v.pair_budget)
        || !(2..=64).contains(&v.ladder.len())
    {
        return Err(AdapterError::InvalidControls);
    }
    for p in &v.ladder {
        if !p.relative.is_finite()
            || !p.absolute.is_finite()
            || p.relative <= 0.
            || p.absolute <= 0.
        {
            return Err(AdapterError::InvalidControls);
        }
    }
    for w in v.ladder.windows(2) {
        if w[1].relative >= w[0].relative || w[1].absolute >= w[0].absolute {
            return Err(AdapterError::InvalidControls);
        }
    }
    Ok(())
}
fn recoverable(e: NetworkError) -> bool {
    matches!(
        e,
        NetworkError::NegativePopulation
            | NetworkError::NegativeEnergy
            | NetworkError::TemperatureOutsideSource
    )
}
fn physical_rejection(
    e: NetworkError,
    h: f64,
    pairs: usize,
    comparisons: Vec<Comparison>,
    scales: Vec<Scale>,
) -> BudgetTrial {
    BudgetTrial {
        action: Action::RetrySmallerOuterInterval,
        accepted: None,
        comparisons,
        scales,
        pairs_evaluated: pairs,
        next_h_s: h / 2.,
        reason: Some(e),
    }
}
/// A single immutable-input attempt with a bounded inner ladder. No outer retry
/// or caller-state mutation happens here. Stop outcomes never masquerade as an
/// accepted solution. The context identity is intra-call borrowing, not a hash
/// or a transferable proof of scientific/source identity.
pub fn attempt(
    b: &MidpointBridge,
    s: &AgeHistory,
    c: &NetworkConfig,
    h: f64,
    tol: &LocalTolerances,
    controls: &NativeBudgetControls,
) -> Result<BudgetTrial, AdapterError> {
    tol.validate()?;
    validate_controls(controls)?;
    if b.3 != Centering::JointCxSplit || !h.is_finite() || h <= 0. {
        return Err(AdapterError::InvalidControls);
    }
    let mid = s.time_s + 0.5 * h;
    let end = s.time_s + h;
    if !mid.is_finite() || !end.is_finite() || mid <= s.time_s || end <= mid {
        return Err(NetworkError::NoForwardProgress.into());
    }
    let mut fixed = *c;
    fixed.cx_controls.rtol = 0.;
    fixed.cx_controls.atol_normalized = 0.;
    let context = Context {
        initial_identity: format!("immutable-borrow:{s:p}"),
        physics_identity: format!(
            "P9-original:{:?}:{:?}:{:?}:{:?}:{fixed:?}",
            b.0, b.1, b.2, b.3
        ),
        projection_identity: "P9-labelled-projection-units-v1".into(),
        start_s: s.time_s,
        end_s: end,
    };
    let mut pairs = 1;
    let mut lo = match evaluate(b, s, c, h, controls.ladder[0], &context) {
        Ok(v) => v,
        Err(AdapterError::Network(e)) if recoverable(e) => {
            return Ok(physical_rejection(e, h, pairs, vec![], vec![]));
        }
        Err(e) => return Err(e),
    };
    let scales = freeze(&lo.policy, tol)?; // IMMUTABLE for every comparison below.
    let mut comparisons = Vec::new();
    for level in 1..controls.ladder.len() {
        pairs += 1;
        let hi = match evaluate(b, s, c, h, controls.ladder[level], &context) {
            Ok(v) => v,
            Err(AdapterError::Network(e)) if recoverable(e) => {
                return Ok(physical_rejection(e, h, pairs, comparisons, scales));
            }
            Err(e) => return Err(e),
        };
        let report = budget_kernel::assess(&lo.policy, &hi.policy, &scales, controls.beta)?;
        let action = budget_kernel::plan_next(
            &report,
            level + 1 < controls.ladder.len(),
            pairs,
            controls.pair_budget,
        )?;
        let outer = report.outer_max / (1. - controls.beta);
        comparisons.push(Comparison {
            loose: lo.policy.precision,
            tight: hi.policy.precision,
            report,
            four: [
                lo.policy.coarse.clone(),
                lo.policy.fine.clone(),
                hi.policy.coarse.clone(),
                hi.policy.fine.clone(),
            ],
        });
        if action == Action::RefineAtSameInterval {
            lo = hi;
            continue;
        }
        let next_h_s = match action {
            Action::CommitTightFine => next_step(h, outer, true),
            Action::RetrySmallerOuterInterval => next_step(h, outer, false),
            _ => h,
        };
        let accepted = if action == Action::CommitTightFine {
            Some(Box::new(Accepted {
                state: hi.fine,
                photo_events_com3: hi.events,
                precision: hi.policy.precision,
                max_energy_ledger: hi.ledger,
            }))
        } else {
            None
        };
        return Ok(BudgetTrial {
            action,
            accepted,
            comparisons,
            scales,
            pairs_evaluated: pairs,
            next_h_s,
            reason: None,
        });
    }
    Err(AdapterError::InvalidControls)
}
