//! P4/S10 standalone four-corner budget policy prototype.
//! STATUS: AUTHORED_UNCOMPILED. Native sandbox probes returned ServerError.
//! The 20 companion Rust tests were written but NOT executed in this turn.
//! NOT wired into JointCxSplit or adaptive_step.rs. No physical source is changed.
//!
//! Input contract: same immutable initial state, interval, physics/quadrature,
//! and projection schema. Each precision supplies C=one full step and F=two
//! halfsteps. Step event densities must already use each halfstep's own midpoint
//! volume. Project photons by stable labels, never by coarse/fine record index.
//!
//! One frozen positive scale s_i is used for ALL FOUR endpoints. For each i:
//! O_i=|C_tight-F_tight|/s_i;
//! I_i=(|C_loose-C_tight|+|F_loose-F_tight|)/s_i.
//! Require O_i<=1-beta AND I_i<=beta. Tighten the inner tolerance first if its
//! allocation fails; only after it passes may an outer failure request smaller h.
//! A successful result permits the caller to commit F_tight ONCE, not an
//! extrapolated state. This module performs no mutations or trial evaluations.
//!
//! Exact real algebra bounds the tested differences, NOT distance to a true
//! solution. All four endpoints may share an arbitrarily large common bias.
//! Ordinary f64 arithmetic here is not directed-rounding interval arithmetic.
//! Relative/absolute scales must be frozen by the caller for the current ladder;
//! changing scales between pairwise comparisons invalidates the stated norm.
#![forbid(unsafe_code)]
use std::collections::BTreeMap;

#[derive(Clone, Debug)]
pub struct Datum { pub key: String, pub unit: String, pub value: f64 }
#[derive(Clone, Debug)]
pub struct Scale { pub key: String, pub unit: String, pub value: f64 }
#[derive(Clone, Debug)]
pub struct Context {
    pub initial_identity: String,
    pub physics_identity: String,
    pub projection_identity: String,
    pub start_s: f64,
    pub end_s: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct Precision { pub relative: f64, pub absolute: f64 }
#[derive(Clone, Debug)]
pub struct Pair {
    pub context: Context,
    pub precision: Precision,
    pub coarse: Vec<Datum>,
    pub fine: Vec<Datum>,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Decision { AcceptTightFine, TightenInner, ReduceOuter }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Action {
    CommitTightFine,
    RefineAtSameInterval,
    RetrySmallerOuterInterval,
    StopInnerUnresolved,
    StopWorkLimit,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BudgetError {
    InvalidConfig, InvalidContext, ContextMismatch, InvalidPrecision,
    PrecisionNotTighter, EmptyProjection, DuplicateLabel, LabelMismatch,
    UnitMismatch, InvalidScale, NonFinite, NonFiniteArithmetic,
    NormalizedUnderflow,
}
#[derive(Clone, Debug)]
pub struct ComponentReport {
    pub key: String,
    pub outer: f64,
    pub inner: f64,
    pub loose_defect: f64,
    pub mixed_change: f64,
    pub triangle_upper: f64,
}
#[derive(Clone, Debug)]
pub struct Report {
    pub decision: Decision,
    pub beta: f64,
    pub outer_max: f64,
    pub inner_max: f64,
    pub loose_defect_max: f64,
    pub mixed_change_max: f64,
    pub triangle_upper_max: f64,
    pub components: Vec<ComponentReport>,
}
fn valid_context(c: &Context) -> bool {
    !c.initial_identity.is_empty() && !c.physics_identity.is_empty()
        && !c.projection_identity.is_empty() && c.start_s.is_finite()
        && c.end_s.is_finite() && c.end_s > c.start_s
}
fn same_context(a: &Context, b: &Context) -> bool {
    a.initial_identity == b.initial_identity && a.physics_identity == b.physics_identity
        && a.projection_identity == b.projection_identity
        && a.start_s.to_bits() == b.start_s.to_bits()
        && a.end_s.to_bits() == b.end_s.to_bits()
}
fn valid_precision(p: Precision) -> bool {
    p.relative.is_finite() && p.absolute.is_finite()
        && p.relative > 0.0 && p.absolute > 0.0
}
fn index(rows: &[Datum]) -> Result<BTreeMap<&str, &Datum>, BudgetError> {
    if rows.is_empty() { return Err(BudgetError::EmptyProjection); }
    let mut map = BTreeMap::new();
    for row in rows {
        if row.key.is_empty() { return Err(BudgetError::LabelMismatch); }
        if row.unit.is_empty() { return Err(BudgetError::UnitMismatch); }
        if !row.value.is_finite() { return Err(BudgetError::NonFinite); }
        if map.insert(row.key.as_str(), row).is_some() {
            return Err(BudgetError::DuplicateLabel);
        }
    }
    Ok(map)
}
fn distance(a: f64, b: f64, scale: f64) -> Result<f64, BudgetError> {
    let difference = (a - b).abs();
    let normalized = difference / scale;
    if !difference.is_finite() || !normalized.is_finite() {
        return Err(BudgetError::NonFiniteArithmetic);
    }
    if a != b && normalized == 0.0 {
        return Err(BudgetError::NormalizedUnderflow);
    }
    Ok(normalized)
}
fn finite_sum(a: f64, b: f64) -> Result<f64, BudgetError> {
    let x = a + b;
    if x.is_finite() { Ok(x) } else { Err(BudgetError::NonFiniteArithmetic) }
}

/// Labels, units and exact trial context are validated before arithmetic.
/// An identity string is a provenance contract, not a proof that a caller really
/// ran its claimed physics. The missing P9 adapter must bind these identities.
pub fn assess(lo: &Pair, hi: &Pair, scales: &[Scale], beta: f64)
    -> Result<Report, BudgetError>
{
    if !beta.is_finite() || beta <= 0.0 || beta >= 1.0 || scales.is_empty() {
        return Err(BudgetError::InvalidConfig);
    }
    if !valid_context(&lo.context) || !valid_context(&hi.context) {
        return Err(BudgetError::InvalidContext);
    }
    if !same_context(&lo.context, &hi.context) { return Err(BudgetError::ContextMismatch); }
    if !valid_precision(lo.precision) || !valid_precision(hi.precision) {
        return Err(BudgetError::InvalidPrecision);
    }
    if hi.precision.relative >= lo.precision.relative
        || hi.precision.absolute >= lo.precision.absolute {
        return Err(BudgetError::PrecisionNotTighter);
    }
    let mut weights = BTreeMap::new();
    for s in scales {
        if s.key.is_empty() || s.unit.is_empty() || !s.value.is_finite() || s.value <= 0.0 {
            return Err(BudgetError::InvalidScale);
        }
        if weights.insert(s.key.as_str(), s).is_some() { return Err(BudgetError::DuplicateLabel); }
    }
    let maps = [index(&lo.coarse)?, index(&lo.fine)?, index(&hi.coarse)?, index(&hi.fine)?];
    if maps.iter().any(|m| m.len() != weights.len()) { return Err(BudgetError::LabelMismatch); }
    let mut report = Report {
        decision: Decision::AcceptTightFine, beta, outer_max: 0.0, inner_max: 0.0,
        loose_defect_max: 0.0, mixed_change_max: 0.0, triangle_upper_max: 0.0,
        components: Vec::with_capacity(weights.len()),
    };
    for (key, scale) in weights {
        let mut q = [0.0; 4];
        for (k, map) in maps.iter().enumerate() {
            let row = map.get(key).ok_or(BudgetError::LabelMismatch)?;
            if row.unit != scale.unit { return Err(BudgetError::UnitMismatch); }
            q[k] = row.value;
        }
        let outer = distance(q[2], q[3], scale.value)?;
        let inner = finite_sum(distance(q[0], q[2], scale.value)?, distance(q[1], q[3], scale.value)?)?;
        let loose_defect = distance(q[0], q[1], scale.value)?;
        let mixed_change = distance(q[0] - q[1], q[2] - q[3], scale.value)?;
        let triangle_upper = finite_sum(outer, inner)?;
        report.outer_max = report.outer_max.max(outer);
        report.inner_max = report.inner_max.max(inner);
        report.loose_defect_max = report.loose_defect_max.max(loose_defect);
        report.mixed_change_max = report.mixed_change_max.max(mixed_change);
        report.triangle_upper_max = report.triangle_upper_max.max(triangle_upper);
        report.components.push(ComponentReport {
            key: key.into(), outer, inner, loose_defect, mixed_change, triangle_upper,
        });
    }
    report.decision = if report.inner_max > beta {
        Decision::TightenInner
    } else if report.outer_max > 1.0 - beta {
        Decision::ReduceOuter
    } else { Decision::AcceptTightFine };
    Ok(report)
}

/// A pair evaluation means C and F at ONE inner precision (three native macro
/// calls in the P9 contract). Reuse the previous tight pair as the next loose
/// pair, so an inner refinement needs one additional pair evaluation, not two.
/// Underlying per-CX work limits must remain independent and fatal to the adapter.
/// This function schedules nothing; it returns a bounded action for the caller.
pub fn plan_next(r: &Report, another_inner_level: bool, pairs_used: usize, pair_budget: usize)
    -> Result<Action, BudgetError>
{
    if pair_budget < 2 || pair_budget > 64 || pairs_used < 2 || pairs_used > pair_budget {
        return Err(BudgetError::InvalidConfig);
    }
    Ok(match r.decision {
        Decision::AcceptTightFine => Action::CommitTightFine,
        Decision::ReduceOuter => Action::RetrySmallerOuterInterval,
        Decision::TightenInner if !another_inner_level => Action::StopInnerUnresolved,
        Decision::TightenInner if pairs_used == pair_budget => Action::StopWorkLimit,
        Decision::TightenInner => Action::RefineAtSameInterval,
    })
}
