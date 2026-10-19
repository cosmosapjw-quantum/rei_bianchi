//! Opt-in binding of unchanged PR159 donor geometry to the original photon trait.
//! No reaction RHS, emissivity, source-age storage or Einstein feedback is changed.
//! The table/source clock owns snapshots; the Hermite cell utility qualifies
//! whole-cell expansion only. The original Killing ray owns photon pullback.
use crate::{
    bass_cell::{Cell, Node},
    bianchi_i::{AxisymmetricPoint, CharacteristicRay, GeometryBackground, GeometrySnapshot},
    donor::{BassBackground, BassSourceIdentity},
    ForwardError,
};
use std::{fs, path::Path};
fn bad(tag: &'static str) -> ForwardError {
    ForwardError::InvalidInput(tag)
}

pub struct QualifiedTable {
    source: BassBackground,
    nodes: Vec<Node>,
    cells: Vec<Cell>,
    a_ref: f64,
    time_domain: [f64; 2],
}
impl QualifiedTable {
    /// Caller supplies immutable, externally approved CSV/manifest hashes.
    /// Never derive an expected hash from the very bytes being admitted.
    pub fn load(csv: &Path, manifest: &Path, id: BassSourceIdentity) -> Result<Self, ForwardError> {
        const CASES: [&str; 8] = [
            "COLD_FLRW",
            "WARM_ISOTROPIC",
            "MASSIVE_A_PLUS",
            "MASSIVE_A_MINUS",
            "MASS3_A_PLUS",
            "MASS300_A_PLUS",
            "SIGNED_PLUS",
            "SIGNED_MINUS",
        ];
        if !CASES.contains(&id.case.as_str())
            || id.producer_commit.len() != 40
            || !id.producer_commit.bytes().all(|c| c.is_ascii_hexdigit())
        {
            return Err(bad("BASS_INTAKE_IDENTITY"));
        }
        // Original loader validates exact bytes, row constraints and proper clock.
        let source = BassBackground::from_files(csv, manifest, id)?;
        let text = fs::read_to_string(csv).map_err(|_| bad("BASS_CSV_IO"))?;
        if crate::donor::sha256_bytes(text.as_bytes())? != source.identity.source_csv_sha256 {
            return Err(bad("BASS_CSV_CHANGED_AFTER_LOAD"));
        }
        let mut lines = text.lines();
        let header = lines
            .next()
            .ok_or(bad("BASS_HEADER"))?
            .split(',')
            .collect::<Vec<_>>();
        let at = |s: &str| {
            header
                .iter()
                .position(|x| *x == s)
                .ok_or(bad("BASS_HEADER"))
        };
        let indices = [
            at("case")?,
            at("x")?,
            at("b")?,
            at("H_mean_per_s")?,
            at("s_per_s")?,
            at("dH_dln_a_per_s")?,
            at("a")?,
        ];
        let mut nodes = Vec::new();
        let mut a_ref = None;
        for line in lines {
            let p = line.split(',').collect::<Vec<_>>();
            if p.len() != header.len() {
                return Err(bad("BASS_ROW_SHAPE"));
            }
            if p[indices[0]] != source.identity.case {
                continue;
            }
            let f = |i: usize| {
                p[indices[i]]
                    .parse::<f64>()
                    .map_err(|_| bad("BASS_ROW_NUMBER"))
            };
            let n = Node {
                x: f(1)?,
                b: f(2)?,
                h_per_s: f(3)?,
                s_per_s: f(4)?,
                dh_dln_a_per_s: f(5)?,
            };
            if a_ref.is_none() {
                a_ref = Some(f(6)? / n.x.exp());
            }
            nodes.push(n);
        }
        if nodes.len() != source.identity.grid_points || nodes.len() < 2 {
            return Err(bad("BASS_NODE_COUNT"));
        }
        let mut cells = Vec::with_capacity(nodes.len() - 1);
        for p in nodes.windows(2) {
            let c = Cell::new(p[0], p[1]).map_err(|_| bad("BASS_HERMITE_CELL"))?;
            c.expansion()
                .map_err(|_| bad("BASS_MONOTONE_ROUTE_UNQUALIFIED"))?;
            cells.push(c);
        }
        let a_ref = a_ref.ok_or(bad("BASS_AREF"))?;
        let t0 = source.point_at_scale(a_ref * nodes[0].x.exp())?.time_s;
        let t1 = source
            .point_at_scale(a_ref * nodes[nodes.len() - 1].x.exp())?
            .time_s;
        if !t0.is_finite() || !t1.is_finite() || t1 <= t0 {
            return Err(bad("BASS_CLOCK_DOMAIN"));
        }
        Ok(Self {
            source,
            nodes,
            cells,
            a_ref,
            time_domain: [t0, t1],
        })
    }
    pub fn cells(&self) -> &[Cell] {
        &self.cells
    }
    pub fn nodes(&self) -> &[Node] {
        &self.nodes
    }
    pub fn donor(&self) -> &BassBackground {
        &self.source
    }
    pub fn domain_x(&self) -> [f64; 2] {
        [self.nodes[0].x, self.nodes[self.nodes.len() - 1].x]
    }
    pub fn domain_s(&self) -> [f64; 2] {
        self.time_domain
    }
    fn check_x(&self, x: f64) -> Result<(), ForwardError> {
        let d = self.domain_x();
        if !x.is_finite() || x < d[0] || x > d[1] {
            return Err(bad("BASS_EXACT_X_DOMAIN"));
        }
        Ok(())
    }
    pub fn point_x(&self, x: f64) -> Result<crate::axbi_background::BackgroundPoint, ForwardError> {
        self.check_x(x)?;
        self.source.point_at_scale(self.a_ref * x.exp())
    }
    pub fn snapshot_x(&self, x: f64) -> Result<GeometrySnapshot, ForwardError> {
        let p = self.point_x(x)?;
        AxisymmetricPoint::new(p.a, p.b, p.h_per_s, p.s_per_s)?.snapshot()
    }
    /// Birth metadata is created by this exact donor, not supplied as arbitrary b.
    /// Immutable lifetime binding prevents mixing independently sourced tables.
    pub fn bind_ray(&self, x: f64, energy: f64, mu: f64) -> Result<BoundRay<'_>, ForwardError> {
        self.check_x(x)?;
        if !mu.is_finite() || mu.abs() > 1.0 {
            return Err(bad("BASS_MU"));
        }
        let ray = CharacteristicRay::new(energy, [(1.0 - mu * mu).sqrt(), 0.0, mu], 1.0)?;
        let birth_geometry = self.snapshot_x(x)?;
        Ok(BoundRay {
            owner: self,
            birth_x: x,
            birth_geometry,
            ray,
        })
    }
}
impl GeometryBackground for QualifiedTable {
    fn snapshot(&self, t: f64) -> Result<GeometrySnapshot, ForwardError> {
        if !t.is_finite() || t < self.time_domain[0] || t > self.time_domain[1] {
            return Err(bad("BASS_EXACT_T_DOMAIN"));
        }
        // Preserve endpoint ownership explicitly rather than invoking an inverse
        // at a representationally shifted last point.
        if t == self.time_domain[0] {
            return self.snapshot_x(self.domain_x()[0]);
        }
        if t == self.time_domain[1] {
            return self.snapshot_x(self.domain_x()[1]);
        }
        let p = self.source.point_at_time(t)?;
        AxisymmetricPoint::new(p.a, p.b, p.h_per_s, p.s_per_s)?.snapshot()
    }
}
pub struct BoundRay<'a> {
    owner: &'a QualifiedTable,
    birth_x: f64,
    birth_geometry: GeometrySnapshot,
    ray: CharacteristicRay,
}
#[derive(Clone, Copy, Debug)]
pub struct Event {
    pub x: f64,
    pub time_s: f64,
    pub energy_ev: f64,
    pub cell_index: usize,
    /// Floating-point bisection result, NOT a directed-rounding enclosure.
    pub x_bracket: [f64; 2],
}
impl BoundRay<'_> {
    pub fn at_x(&self, x: f64) -> Result<CharacteristicRay, ForwardError> {
        if x < self.birth_x {
            return Err(bad("BASS_RAY_BEFORE_BIRTH"));
        }
        self.ray
            .pullback(&self.birth_geometry, &self.owner.snapshot_x(x)?)
    }
    fn event(&self, cell: usize, lo: f64, hi: f64) -> Result<Event, ForwardError> {
        let x = lo + 0.5 * (hi - lo);
        let p = self.owner.point_x(x)?;
        let e = self.at_x(x)?.energy_ev;
        Ok(Event {
            x,
            time_s: p.time_s,
            energy_ev: e,
            cell_index: cell,
            x_bracket: [lo, hi],
        })
    }
    /// Whole-table expansion was checked at construction. Split at donor knots
    /// and seek only forward; record one event for a root on a shared boundary.
    pub fn crossing(&self, edge: f64, xtol: f64) -> Result<Option<Event>, ForwardError> {
        if !edge.is_finite() || edge <= 0.0 || !xtol.is_finite() || xtol <= 0.0 {
            return Err(bad("BASS_EDGE_INPUT"));
        }
        let end = self.owner.domain_x()[1];
        if edge > self.ray.energy_ev {
            return Ok(None);
        }
        if edge == self.ray.energy_ev {
            let i = self
                .owner
                .nodes
                .partition_point(|n| n.x <= self.birth_x)
                .saturating_sub(1)
                .min(self.owner.cells.len() - 1);
            return self.event(i, self.birth_x, self.birth_x).map(Some);
        }
        if self.birth_x >= end {
            return Ok(None);
        }
        for (i, w) in self.owner.nodes.windows(2).enumerate() {
            let mut lo = w[0].x.max(self.birth_x);
            let mut hi = w[1].x;
            if lo >= hi {
                continue;
            }
            let fl = self.at_x(lo)?.energy_ev - edge;
            let fh = self.at_x(hi)?.energy_ev - edge;
            if fl == 0.0 {
                return self.event(i, lo, lo).map(Some);
            }
            if fh == 0.0 {
                return self.event(i, hi, hi).map(Some);
            }
            if fl < 0.0 {
                return Ok(None);
            }
            if fh > 0.0 {
                continue;
            }
            for _ in 0..96 {
                if hi - lo <= xtol {
                    return self.event(i, lo, hi).map(Some);
                }
                let mid = lo + 0.5 * (hi - lo);
                if mid == lo || mid == hi {
                    return Err(bad("BASS_ROOT_NO_PROGRESS"));
                }
                let fm = self.at_x(mid)?.energy_ev - edge;
                if fm == 0.0 {
                    return self.event(i, mid, mid).map(Some);
                }
                if fm > 0.0 {
                    lo = mid;
                } else {
                    hi = mid;
                }
            }
            return Err(bad("BASS_ROOT_ITERATIONS"));
        }
        Ok(None)
    }
}
