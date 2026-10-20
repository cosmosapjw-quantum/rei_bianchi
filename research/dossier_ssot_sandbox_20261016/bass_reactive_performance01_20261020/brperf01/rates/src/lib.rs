//! Opt-in compact, positive H/He/D temperature-coefficient receiver.
//! Original Grackle owner, branch semantics, diagnostics and default direct path
//! remain unchanged. Positive PCHIP control points are evaluated in Bernstein
//! form. No rate derivatives, population update, or thermochemistry owner here.
#![forbid(unsafe_code)]

use parent::ForwardError;
use parent::igm_rates::{IgmRateDiagnostics, IgmRates, igm_rates};
use parent::rate_table::{igm_branch_knots, igm_flat};
use sha2::{Digest, Sha256};
use std::sync::Arc;
use wide::f64x4;

const OWNER_BYTES: &[u8] = include_bytes!(
    "../../../repo/research/dossier_ssot_sandbox_20261016/bass_reactive06_vigilode_reference_20261019/parent/crate/owner_src/igm_rates.rs"
);
const OWNER_TABLE_BYTES: &[u8] = include_bytes!(
    "../../../repo/research/dossier_ssot_sandbox_20261016/bass_reactive06_vigilode_reference_20261019/parent/crate/owner_src/rate_table.rs"
);
pub const MIN_NODES: usize = 17;
pub const MAX_NODES: usize = 65_537;
/// Conservative option from the recorded 1025/2049/4097/8193-node scan.
/// This is not a universal error certificate; Direct remains the default backend.
pub const DEFAULT_NODES: usize = 8193;
pub const EVALUATOR_ID: &str = "IGM_GRACKLE_POSITIVE_PCHIP_BERNSTEIN_F64_V1";
const MAGIC: &[u8; 8] = b"RBRATE01";
const HEADER_BYTES: usize = 44;
const CELL_BYTES: usize = 514;

fn bad(message: &'static str) -> ForwardError {
    ForwardError::InvalidInput(message)
}
fn low(t: f64) -> bool {
    t / 11605.0 <= 0.8
}
fn floor_mask(r: &IgmRates) -> [bool; 3] {
    std::array::from_fn(|i| r.diagnostics.ci_floor_cm3_s[i] != 0.0)
}

/// SHA binds the actual compiled source byte strings and numerical schema.
pub fn source_digest() -> [u8; 32] {
    let mut hash = Sha256::new();
    hash.update(EVALUATOR_ID.as_bytes());
    hash.update(OWNER_BYTES);
    hash.update(OWNER_TABLE_BYTES);
    hash.finalize().into()
}

fn harmonic_increment(a: f64, b: f64) -> f64 {
    if a == 0.0 || b == 0.0 || a.is_sign_positive() != b.is_sign_positive() {
        return 0.0;
    }
    let small = a.abs().min(b.abs());
    let large = a.abs().max(b.abs());
    (2.0 * small / (1.0 + small / large)).copysign(a)
}

#[derive(Clone, Debug)]
struct Cell {
    /// Four Bernstein controls, 15 physical channels plus one zero padding lane.
    control: [[f64; 16]; 4],
    floors: [bool; 3],
    blocked: bool,
}

/// Immutable table; node generation calls the original source exactly once per node.
#[derive(Clone, Debug)]
pub struct CompactRateTable {
    cells: Vec<Cell>,
    inv_step: f64,
    source_evaluations: usize,
}

impl CompactRateTable {
    pub fn build(nodes: usize) -> Result<Self, ForwardError> {
        if !(MIN_NODES..=MAX_NODES).contains(&nodes) {
            return Err(bad("COMPACT_RATE_GRID"));
        }
        let step = 1e6_f64.ln() / (nodes - 1) as f64;
        let ts = (0..nodes)
            .map(|i| {
                if i == 0 {
                    1.0
                } else if i + 1 == nodes {
                    1e6
                } else {
                    (step * i as f64).exp()
                }
            })
            .collect::<Vec<_>>();
        let rates = ts
            .iter()
            .map(|&t| igm_rates(t))
            .collect::<Result<Vec<_>, _>>()?;
        let values = rates
            .iter()
            .map(|r| {
                let flat = igm_flat(*r);
                std::array::from_fn::<f64, 16, _>(|j| if j < 15 { flat[j] } else { 0.0 })
            })
            .collect::<Vec<_>>();
        let mut slopes = vec![[0.0; 16]; nodes];
        for i in 1..nodes - 1 {
            for j in 0..15 {
                slopes[i][j] = harmonic_increment(
                    values[i][j] - values[i - 1][j],
                    values[i + 1][j] - values[i][j],
                );
            }
        }
        let mut blocked = vec![false; nodes - 1];
        let knots = igm_branch_knots();
        for i in 0..nodes - 1 {
            let seed = i < 2
                || i >= nodes - 3
                || low(ts[i]) != low(ts[i + 1])
                || floor_mask(&rates[i]) != floor_mask(&rates[i + 1])
                || knots.iter().any(|&k| ts[i] <= k && k <= ts[i + 1]);
            if seed {
                for b in blocked
                    .iter_mut()
                    .take((i + 3).min(nodes - 1))
                    .skip(i.saturating_sub(2))
                {
                    *b = true;
                }
            }
        }
        let cells = (0..nodes - 1)
            .map(|i| {
                let control = [
                    values[i],
                    std::array::from_fn(|j| values[i][j] + slopes[i][j] / 3.0),
                    std::array::from_fn(|j| values[i + 1][j] - slopes[i + 1][j] / 3.0),
                    values[i + 1],
                ];
                let invalid = control
                    .iter()
                    .flatten()
                    .any(|&v| v < 0.0 || !(v == 0.0 || v.is_normal()));
                Cell {
                    control,
                    floors: floor_mask(&rates[i]),
                    blocked: blocked[i] || invalid,
                }
            })
            .collect();
        Ok(Self {
            cells,
            inv_step: (nodes - 1) as f64 / 1e6_f64.ln(),
            source_evaluations: nodes,
        })
    }

    pub fn nodes(&self) -> usize {
        self.cells.len() + 1
    }
    pub fn domain(&self) -> [f64; 2] {
        [1.0, 1e6]
    }
    pub fn storage_bytes(&self) -> usize {
        self.cells.len() * std::mem::size_of::<Cell>()
    }
    pub fn blocked_cells(&self) -> usize {
        self.cells.iter().filter(|c| c.blocked).count()
    }
    pub fn source_evaluations(&self) -> usize {
        self.source_evaluations
    }
    pub fn direct_fallback(&self, t: f64) -> bool {
        self.locate(t).is_none()
    }
    pub fn cell_controls(&self, i: usize) -> Option<([[f64; 16]; 4], [bool; 3], bool)> {
        self.cells.get(i).map(|c| (c.control, c.floors, c.blocked))
    }
    fn locate(&self, t: f64) -> Option<(&Cell, [f64; 4])> {
        if !t.is_finite() || !(1.0..=1e6).contains(&t) {
            return None;
        }
        let x = t.ln() * self.inv_step;
        let i = (x.floor() as usize).min(self.cells.len() - 1);
        let cell = &self.cells[i];
        if cell.blocked {
            return None;
        }
        let q = (x - i as f64).clamp(0.0, 1.0);
        let u = 1.0 - q;
        Some((
            cell,
            [u * u * u, 3.0 * u * u * q, 3.0 * u * q * q, q * q * q],
        ))
    }
    pub fn rates(&self, t: f64) -> Result<IgmRates, ForwardError> {
        let Some((cell, w)) = self.locate(t) else {
            return igm_rates(t);
        };
        let v = std::array::from_fn(|j| {
            ((cell.control[0][j] * w[0] + cell.control[1][j] * w[1]) + cell.control[2][j] * w[2])
                + cell.control[3][j] * w[3]
        });
        Ok(unpack(t, v, cell.floors))
    }
    pub fn rates_simd(&self, t: f64) -> Result<IgmRates, ForwardError> {
        let Some((cell, w)) = self.locate(t) else {
            return igm_rates(t);
        };
        let mut values = [0.0; 16];
        let weights = w.map(f64x4::splat);
        for block in 0..4 {
            let base = block * 4;
            let c = cell
                .control
                .map(|row| f64x4::new(std::array::from_fn(|j| row[base + j])));
            let v = (((c[0] * weights[0] + c[1] * weights[1]) + c[2] * weights[2])
                + c[3] * weights[3])
                .to_array();
            values[base..base + 4].copy_from_slice(&v);
        }
        Ok(unpack(t, std::array::from_fn(|j| values[j]), cell.floors))
    }

    /// Cache transport includes schema, source SHA and payload SHA. It detects
    /// accidental corruption/source mismatch, not adversarial authenticity.
    pub fn to_bytes(&self) -> Vec<u8> {
        let mut out = Vec::with_capacity(HEADER_BYTES + CELL_BYTES * self.cells.len() + 32);
        out.extend(MAGIC);
        out.extend(source_digest());
        out.extend((self.nodes() as u32).to_le_bytes());
        for c in &self.cells {
            out.push(u8::from(c.blocked));
            out.push(
                c.floors
                    .iter()
                    .enumerate()
                    .fold(0_u8, |m, (j, &v)| m | (u8::from(v) << j)),
            );
            for v in c.control.iter().flatten() {
                out.extend(v.to_le_bytes());
            }
        }
        let digest = Sha256::digest(&out);
        out.extend(digest);
        out
    }
    pub fn from_bytes(bytes: &[u8]) -> Result<Self, ForwardError> {
        if bytes.len() < HEADER_BYTES + 32 || &bytes[..8] != MAGIC {
            return Err(bad("COMPACT_CACHE_HEADER"));
        }
        if bytes[8..40] != source_digest() {
            return Err(bad("COMPACT_CACHE_SOURCE"));
        }
        let nodes = u32::from_le_bytes(bytes[40..44].try_into().unwrap()) as usize;
        if !(MIN_NODES..=MAX_NODES).contains(&nodes)
            || bytes.len() != HEADER_BYTES + CELL_BYTES * (nodes - 1) + 32
        {
            return Err(bad("COMPACT_CACHE_LENGTH"));
        }
        let body_len = bytes.len() - 32;
        if Sha256::digest(&bytes[..body_len])[..] != bytes[body_len..] {
            return Err(bad("COMPACT_CACHE_HASH"));
        }
        let mut cells = Vec::with_capacity(nodes - 1);
        let mut offset = HEADER_BYTES;
        for _ in 0..nodes - 1 {
            let blocked = bytes[offset];
            let mask = bytes[offset + 1];
            offset += 2;
            if blocked > 1 || mask > 7 {
                return Err(bad("COMPACT_CACHE_MASK"));
            }
            let mut control = [[0.0; 16]; 4];
            for v in control.iter_mut().flatten() {
                *v = f64::from_le_bytes(bytes[offset..offset + 8].try_into().unwrap());
                offset += 8;
                if *v < 0.0 || !(*v == 0.0 || v.is_normal()) {
                    return Err(bad("COMPACT_CACHE_COEFFICIENT"));
                }
            }
            cells.push(Cell {
                control,
                floors: std::array::from_fn(|j| mask & (1 << j) != 0),
                blocked: blocked != 0,
            });
        }
        Ok(Self {
            cells,
            inv_step: (nodes - 1) as f64 / 1e6_f64.ln(),
            source_evaluations: 0,
        })
    }
}

fn unpack(t: f64, mut v: [f64; 15], floors: [bool; 3]) -> IgmRates {
    for j in 0..3 {
        if floors[j] {
            v[j] = 1e-20;
        }
    }
    let ce = [v[7], v[8], v[9]];
    IgmRates {
        ci_cm3_s: [v[0], v[1], v[2]],
        rr_cm3_s: [v[3], v[4], v[5]],
        dr_cm3_s: v[6],
        ce_erg: ce,
        rr_cooling_erg_cm3_s: [v[10], v[11], v[12]],
        dr_cooling_erg_cm3_s: if low(t) { 0.0 } else { v[13] },
        dr_raw_cooling_erg_cm3_s: v[13],
        freefree_erg_cm3_s: v[14],
        diagnostics: IgmRateDiagnostics {
            ci_floor_cm3_s: std::array::from_fn(|j| if floors[j] { v[j] } else { 0.0 }),
            ce_cap_erg: std::array::from_fn(|j| {
                if [118348.0, 13179.0, 473638.0][j] / t > 69.07755278982137 {
                    ce[j]
                } else {
                    0.0
                }
            }),
            dr_excluded_erg_cm3_s: if low(t) { v[13] } else { 0.0 },
            dr_low_branch: low(t),
        },
    }
}

#[derive(Clone, Debug, Default)]
pub enum RateBackend {
    #[default]
    Direct,
    CompactScalar(Arc<CompactRateTable>),
    CompactSimd(Arc<CompactRateTable>),
}
impl RateBackend {
    pub fn rates(&self, t: f64) -> Result<IgmRates, ForwardError> {
        match self {
            Self::Direct => igm_rates(t),
            Self::CompactScalar(tab) => tab.rates(t),
            Self::CompactSimd(tab) => tab.rates_simd(t),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn diagnostic_bits(r: IgmRates) -> Vec<u64> {
        igm_flat(r)
            .into_iter()
            .chain(r.diagnostics.ci_floor_cm3_s)
            .chain(r.diagnostics.ce_cap_erg)
            .chain([
                r.dr_cooling_erg_cm3_s,
                r.diagnostics.dr_excluded_erg_cm3_s,
                f64::from(r.diagnostics.dr_low_branch),
            ])
            .map(f64::to_bits)
            .collect()
    }
    #[test]
    fn source_once_per_node_and_nonnegative_controls() {
        let tab = CompactRateTable::build(1025).unwrap();
        assert_eq!(tab.source_evaluations(), 1025);
        for c in &tab.cells {
            assert!(
                c.control
                    .iter()
                    .flatten()
                    .all(|v| *v >= 0.0 && v.is_finite())
            );
        }
        assert!(tab.blocked_cells() >= 20);
    }
    #[test]
    fn default_direct_and_invalid_input_contract() {
        for t in [1.0, 100.0, 5500.0, 9284.0, 1e6] {
            assert_eq!(
                diagnostic_bits(RateBackend::default().rates(t).unwrap()),
                diagnostic_bits(igm_rates(t).unwrap())
            );
        }
        let tab = CompactRateTable::build(1025).unwrap();
        for t in [f64::NAN, f64::INFINITY, -1.0, 0.0, 0.9, 1e6_f64.next_up()] {
            assert!(tab.rates(t).is_err());
            assert!(tab.rates_simd(t).is_err());
        }
        assert!(CompactRateTable::build(3).is_err());
    }
    #[test]
    fn branch_neighborhoods_and_diagnostics_preserved() {
        let tab = CompactRateTable::build(4097).unwrap();
        for t in igm_branch_knots().into_iter().chain([1.0, 1e6]) {
            for q in [t.next_down(), t, t.next_up()] {
                if !(1.0..=1e6).contains(&q) {
                    continue;
                }
                assert!(tab.direct_fallback(q));
                assert_eq!(
                    diagnostic_bits(tab.rates(q).unwrap()),
                    diagnostic_bits(igm_rates(q).unwrap())
                );
            }
        }
    }
    #[test]
    fn scalar_simd_all_fields_bitwise() {
        let tab = CompactRateTable::build(4097).unwrap();
        for i in 0..10001 {
            let t = (1e6_f64.ln() * i as f64 / 10001.0).exp();
            let a = tab.rates(t).unwrap();
            let b = tab.rates_simd(t).unwrap();
            assert_eq!(diagnostic_bits(a), diagnostic_bits(b));
            assert!(igm_flat(a).into_iter().all(|x| x >= 0.0 && x.is_finite()));
            if low(t) {
                assert_eq!(a.dr_cm3_s, 0.0);
                assert_eq!(a.dr_cooling_erg_cm3_s, 0.0);
            }
        }
    }
    #[test]
    fn serialization_readback_and_rejection() {
        // Non-power-of-two intervals also exercise exact inverse-grid metadata.
        let tab = CompactRateTable::build(1026).unwrap();
        let mut bytes = tab.to_bytes();
        let restored = CompactRateTable::from_bytes(&bytes).unwrap();
        assert_eq!(restored.source_evaluations(), 0);
        for i in 0..1000 {
            let t = (1e6_f64.ln() * (i as f64 + 0.17) / 1000.0).exp();
            assert_eq!(
                diagnostic_bits(tab.rates(t).unwrap()),
                diagnostic_bits(restored.rates(t).unwrap())
            );
        }
        bytes[80] ^= 1;
        assert!(CompactRateTable::from_bytes(&bytes).is_err());
        bytes = tab.to_bytes();
        bytes[8] ^= 1;
        assert!(CompactRateTable::from_bytes(&bytes).is_err());
        assert!(CompactRateTable::from_bytes(&bytes[..40]).is_err());
    }
}
