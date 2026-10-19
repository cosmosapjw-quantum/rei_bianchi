//! Opt-in reactive bridge over an immutable, fully-qualified BASS table.
//! Constant background delegates exact old formulas. Table snapshots retain
//! original donor clock/inversion, with exact-f64 memoization, no new interpolation.
//! Scalar absorption only, non-tilted gas; no gas feedback into donor Einstein data.
use crate::bianchi_i::{ConstantAxisymmetricBackground, GeometryBackground, GeometrySnapshot};
pub use crate::bound_midpoint::MidpointBridge as BindingBridge;
pub use crate::bound_source_age::SourceAgeBridge as BoundSourceAgeBridge;
use crate::source_age::Cohort;
use crate::{ForwardError, full_network::NetworkError, qualified_table::QualifiedTable};
use std::{
    cell::RefCell,
    collections::{HashMap, VecDeque},
    rc::Rc,
};
#[derive(Default)]
struct Memo {
    map: HashMap<u64, GeometrySnapshot>,
    fifo: VecDeque<u64>,
    hits: usize,
    misses: usize,
}
struct TableState {
    table: QualifiedTable,
    knots: Vec<f64>,
    memo: RefCell<Memo>,
    capacity: usize,
}
#[derive(Clone)]
pub struct GeometryChoice {
    inner: Choice,
}
#[derive(Clone)]
enum Choice {
    Constant(ConstantAxisymmetricBackground),
    Table(Rc<TableState>),
}
impl std::fmt::Debug for GeometryChoice {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("GeometryChoice")
            .field("domain_s", &self.domain_s())
            .field("identity", &self.identity())
            .finish()
    }
}
impl GeometryChoice {
    pub fn constant(g: ConstantAxisymmetricBackground) -> Self {
        Self {
            inner: Choice::Constant(g),
        }
    }
    pub fn table(t: QualifiedTable, capacity: usize) -> Result<Self, ForwardError> {
        if capacity > 65536 {
            return Err(ForwardError::InvalidInput("BASS_CACHE_LIMIT"));
        }
        let knots = t
            .nodes()
            .iter()
            .map(|n| t.point_x(n.x).map(|p| p.time_s))
            .collect::<Result<Vec<_>, _>>()?;
        Ok(Self {
            inner: Choice::Table(Rc::new(TableState {
                table: t,
                knots,
                memo: RefCell::new(Memo::default()),
                capacity,
            })),
        })
    }
    pub fn domain_s(&self) -> [f64; 2] {
        match &self.inner {
            Choice::Constant(g) => g.time_domain_s,
            Choice::Table(t) => t.table.domain_s(),
        }
    }
    pub fn identity(&self) -> String {
        match &self.inner {
            Choice::Constant(g) => format!("CONSTANT:{g:?}"),
            Choice::Table(t) => format!("BASS:{:?}", t.table.donor().identity),
        }
    }
    pub fn cache_stats(&self) -> (usize, usize, usize) {
        match &self.inner {
            Choice::Constant(_) => (0, 0, 0),
            Choice::Table(t) => {
                let m = t.memo.borrow();
                (m.hits, m.misses, m.map.len())
            }
        }
    }
    pub fn clear_cache(&self) {
        if let Choice::Table(t) = &self.inner {
            let mut m = t.memo.borrow_mut();
            m.map.clear();
            m.fifo.clear();
        }
    }
    pub fn snapshot(&self, time: f64) -> Result<GeometrySnapshot, ForwardError> {
        <Self as GeometryBackground>::snapshot(self, time)
    }
    pub fn edge_count(&self, e0: f64, e1: f64, d: f64, old_count: usize) -> usize {
        match self.inner {
            Choice::Constant(_) => old_count,
            _ => [13.60, 24.59, 54.42, d]
                .iter()
                .filter(|e| e0 > **e && e1 < **e)
                .count(),
        }
    }
    pub fn validate_history(
        &self,
        history: &crate::source_age::AgeHistory,
    ) -> Result<(), NetworkError> {
        if let Choice::Table(_) = &self.inner {
            self.snapshot(history.time_s)
                .map_err(|_| NetworkError::InputOutsideDomain)?;
            if history.full.elapsed_s.to_bits() != history.time_s.to_bits() {
                return Err(NetworkError::SourceMismatch);
            }
            for co in &history.cohorts {
                if co.birth_time_s > history.time_s {
                    return Err(NetworkError::SourceMismatch);
                }
                self.validate_birth(co)?;
            }
        }
        Ok(())
    }
    /// Validate original cohort fields before crossing. No arbitrary birth-b adapter.
    pub fn validate_birth(&self, co: &Cohort) -> Result<(), NetworkError> {
        if !co.birth_time_s.is_finite() {
            return Err(NetworkError::InvalidInput);
        }
        let g = self
            .snapshot(co.birth_time_s)
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        let equal = g
            .scale_factors
            .iter()
            .chain(g.hubble_per_s.iter())
            .zip(
                co.birth_geometry
                    .scale_factors
                    .iter()
                    .chain(co.birth_geometry.hubble_per_s.iter()),
            )
            .all(|(a, b)| a.to_bits() == b.to_bits());
        if !equal {
            return Err(NetworkError::SourceMismatch);
        }
        co.ray_at(&g)?;
        Ok(())
    }
}
impl GeometryBackground for GeometryChoice {
    fn snapshot(&self, time: f64) -> Result<GeometrySnapshot, ForwardError> {
        match &self.inner {
            Choice::Constant(g) => g.snapshot(time),
            Choice::Table(t) => {
                let d = t.table.domain_s();
                if !time.is_finite() || time < d[0] || time > d[1] {
                    return Err(ForwardError::InvalidInput("BASS_EXACT_T_DOMAIN"));
                }
                let key = time.to_bits();
                {
                    let mut m = t.memo.borrow_mut();
                    if let Some(g) = m.map.get(&key).copied() {
                        m.hits += 1;
                        return Ok(g);
                    }
                }
                let g = t.table.snapshot(time)?;
                let mut m = t.memo.borrow_mut();
                m.misses += 1;
                if t.capacity > 0 {
                    while m.map.len() >= t.capacity {
                        let key = m
                            .fifo
                            .pop_front()
                            .ok_or(ForwardError::InvalidInput("BASS_CACHE_INVARIANT"))?;
                        m.map.remove(&key);
                    }
                    m.map.insert(key, g);
                    m.fifo.push_back(key);
                }
                Ok(g)
            }
        }
    }
}
/// Constant branch stays byte-for-byte on original root evaluator. BASS tables
/// were admitted for strictly positive directional expansion over EVERY cell.
/// Thus no hidden turns; split at provider knots and all actual interior edges.
#[allow(clippy::too_many_arguments)]
pub fn split_by_thresholds_from_energies(
    g: &GeometryChoice,
    co: &Cohort,
    ta: f64,
    tb: f64,
    e0: f64,
    e1: f64,
    d_edge: f64,
) -> Result<Vec<f64>, NetworkError> {
    if let Choice::Constant(old) = &g.inner {
        return crate::threshold_roots::split_by_thresholds_from_energies(
            old, co, ta, tb, e0, e1, d_edge,
        );
    }
    if ![ta, tb, e0, e1, d_edge].iter().all(|x| x.is_finite())
        || tb <= ta
        || ta < co.birth_time_s
        || e0 <= 0.
        || e1 <= 0.
        || d_edge <= 0.
    {
        return Err(NetworkError::InvalidInput);
    }
    let Choice::Table(t) = &g.inner else {
        unreachable!()
    };
    let domain = g.domain_s();
    if ta < domain[0] || tb > domain[1] {
        return Err(NetworkError::InputOutsideDomain);
    }
    if e1 > e0 * (1. + 128. * f64::EPSILON) {
        return Err(NetworkError::PhysicsLedger);
    }
    let first = t.knots.partition_point(|x| *x <= ta);
    let last = t.knots.partition_point(|x| *x < tb);
    let mut result = t.knots[first..last].to_vec();
    for edge in [13.60, 24.59, 54.42, d_edge] {
        if e0 > edge && e1 < edge {
            let (mut lo, mut hi) = (ta, tb);
            for _ in 0..96 {
                let mid = lo + 0.5 * (hi - lo);
                if mid == lo || mid == hi {
                    break;
                }
                let en = co
                    .ray_at(
                        &g.snapshot(mid)
                            .map_err(|_| NetworkError::InputOutsideDomain)?,
                    )?
                    .energy_ev;
                if en == edge {
                    lo = mid;
                    hi = mid;
                    break;
                }
                if en > edge {
                    lo = mid;
                } else {
                    hi = mid;
                }
            }
            let x = lo + 0.5 * (hi - lo);
            if x > ta && x < tb {
                result.push(x);
            }
        }
    }
    result.sort_by(f64::total_cmp);
    result.dedup_by(|x, y| x.to_bits() == y.to_bits());
    result.insert(0, ta);
    result.push(tb);
    Ok(result)
}
