//! RUN04 opt-in receiver of immutable BASS164/165 source-only EFE tables.
//! This numerical Hermite geometry is not a fresh EFE+reacting-gas solution.
use crate::ForwardError;
use crate::bianchi_i::{AxisymmetricPoint, GeometryBackground, GeometrySnapshot};
use crate::full_network::NetworkError;
use crate::source_age::Cohort;
use std::{
    fs,
    io::Write,
    path::Path,
    process::{Command, Stdio},
};

pub const A_REF: f64 = 1.0 / 21.0;
pub const BASS_COMMIT: &str = "3c39bbbf46b6663e7c40277e194fd0ef48118472";
const EPS_MARGIN: f64 = 64.0 * f64::EPSILON;
const GL8: [(f64, f64); 4] = [
    (0.1834346424956498, 0.362683783378362),
    (0.525532409916329, 0.3137066458778873),
    (0.7966664774136267, 0.2223810344533745),
    (0.9602898564975363, 0.1012285362903763),
];

/// Exact extrema of the quadratic b_x of the specified cubic Hermite interval.
/// The accepted -1/2 < b_x < 1 condition makes all three axes expanding.
/// Binary64 evaluation is guarded, not an outward-rounded interval certificate.
pub fn monotone_lrs_bounds(
    b0: f64,
    b1: f64,
    p0: f64,
    p1: f64,
    dx: f64,
) -> Result<(f64, f64), NetworkError> {
    if ![b0, b1, p0, p1, dx].iter().all(|x| x.is_finite()) || dx <= 0.0 {
        return Err(NetworkError::InvalidInput);
    }
    let a = 3.0 * (p0 + p1) + 6.0 * (b0 - b1) / dx;
    let b = -4.0 * p0 - 2.0 * p1 + 6.0 * (b1 - b0) / dx;
    let mut lo = p0.min(p1);
    let mut hi = p0.max(p1);
    if a != 0.0 {
        let u = -b / (2.0 * a);
        if u > 0.0 && u < 1.0 {
            let v = (a * u + b) * u + p0;
            lo = lo.min(v);
            hi = hi.max(v);
        }
    }
    if !lo.is_finite() || !hi.is_finite() || lo <= -0.5 + EPS_MARGIN || hi >= 1.0 - EPS_MARGIN {
        return Err(NetworkError::InputOutsideDomain);
    }
    Ok((lo, hi))
}

#[derive(Clone, Debug)]
pub struct SourceIdentity {
    pub csv_sha256: String,
    pub manifest_sha256: String,
    pub case: String,
    pub points: usize,
}
#[derive(Clone, Copy, Debug)]
struct Node {
    x: f64,
    b: f64,
    h: f64,
    s: f64,
    hx: f64,
    t: f64,
}
#[derive(Clone, Debug)]
struct Segment {
    x0: f64,
    dx: f64,
    b: [f64; 4],
    lh: [f64; 4],
}
fn coefficients(y0: f64, y1: f64, p0: f64, p1: f64, dx: f64) -> [f64; 4] {
    [
        y0,
        dx * p0,
        3.0 * (y1 - y0) - dx * (2.0 * p0 + p1),
        2.0 * (y0 - y1) + dx * (p0 + p1),
    ]
}
fn poly(c: [f64; 4], u: f64) -> (f64, f64) {
    (
        ((c[3] * u + c[2]) * u + c[1]) * u + c[0],
        (3.0 * c[3] * u + 2.0 * c[2]) * u + c[1],
    )
}
impl Segment {
    fn state(&self, x: f64) -> (f64, f64, f64) {
        let u = (x - self.x0) / self.dx;
        let (b, db) = poly(self.b, u);
        let h = poly(self.lh, u).0.exp();
        (b, h, h * db / self.dx)
    }
    fn clock(&self, x: f64) -> f64 {
        if x == self.x0 {
            return 0.0;
        }
        let half = (x - self.x0) * 0.5;
        let mid = self.x0 + half;
        GL8.iter()
            .map(|(v, w)| {
                w * half * (1.0 / self.state(mid - half * v).1 + 1.0 / self.state(mid + half * v).1)
            })
            .sum()
    }
}
#[derive(Clone, Copy, Debug)]
pub struct BassPoint {
    pub x: f64,
    pub a: f64,
    pub b: f64,
    pub h: f64,
    pub s: f64,
    pub time_s: f64,
}
impl BassPoint {
    pub fn snapshot(self) -> Result<GeometrySnapshot, NetworkError> {
        AxisymmetricPoint::new(self.a, self.b, self.h, self.s)
            .and_then(|p| p.snapshot())
            .map_err(|_| NetworkError::InputOutsideDomain)
    }
}
#[derive(Clone, Debug)]
pub struct BassGeometry {
    pub identity: SourceIdentity,
    nodes: Vec<Node>,
    segments: Vec<Segment>,
    times: Vec<f64>,
    pub slope_min: f64,
    pub slope_max: f64,
    pub hamiltonian_max: f64,
    pub raychaudhuri_max: f64,
    pub producer_clock_max_rel: f64,
}
fn sha256(bytes: &[u8]) -> Result<String, NetworkError> {
    let mut c = Command::new("sha256sum")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .map_err(|_| NetworkError::InvalidInput)?;
    c.stdin
        .take()
        .ok_or(NetworkError::InvalidInput)?
        .write_all(bytes)
        .map_err(|_| NetworkError::InvalidInput)?;
    let o = c
        .wait_with_output()
        .map_err(|_| NetworkError::InvalidInput)?;
    let text = String::from_utf8(o.stdout).map_err(|_| NetworkError::InvalidInput)?;
    if !o.status.success() {
        return Err(NetworkError::InvalidInput);
    }
    Ok(text
        .split_whitespace()
        .next()
        .ok_or(NetworkError::InvalidInput)?
        .to_string())
}
impl BassGeometry {
    pub fn from_files(
        csv: &Path,
        manifest: &Path,
        identity: SourceIdentity,
    ) -> Result<Self, NetworkError> {
        let raw = fs::read(csv).map_err(|_| NetworkError::InvalidInput)?;
        let mr = fs::read(manifest).map_err(|_| NetworkError::InvalidInput)?;
        if sha256(&raw)? != identity.csv_sha256 || sha256(&mr)? != identity.manifest_sha256 {
            return Err(NetworkError::SourceMismatch);
        }
        let mt = std::str::from_utf8(&mr).map_err(|_| NetworkError::InvalidInput)?;
        if !mt.contains("bass.rei.proposed_background_point_tangent.v1")
            || !mt.contains(&identity.csv_sha256)
        {
            return Err(NetworkError::SourceMismatch);
        }
        if ![
            "COLD_FLRW",
            "WARM_ISOTROPIC",
            "MASSIVE_A_PLUS",
            "MASSIVE_A_MINUS",
            "MASS3_A_PLUS",
            "MASS300_A_PLUS",
            "SIGNED_PLUS",
            "SIGNED_MINUS",
        ]
        .contains(&identity.case.as_str())
        {
            return Err(NetworkError::SourceMismatch);
        }
        let text = std::str::from_utf8(&raw).map_err(|_| NetworkError::InvalidInput)?;
        let mut lines = text.lines();
        let hdr: Vec<_> = lines
            .next()
            .ok_or(NetworkError::InvalidInput)?
            .split(',')
            .collect();
        let column = |n: &str| {
            hdr.iter()
                .position(|v| *v == n)
                .ok_or(NetworkError::SourceMismatch)
        };
        let cx = column("case")?;
        let names = [
            "x",
            "b",
            "H_mean_per_s",
            "s_per_s",
            "dH_dln_a_per_s",
            "proper_elapsed_s",
            "a",
            "Sigma",
            "signed_s_over_H",
            "massive_rho_norm",
            "massive_pbar_norm",
        ];
        let ids = names
            .iter()
            .map(|n| column(n))
            .collect::<Result<Vec<_>, _>>()?;
        let mut nodes: Vec<Node> = Vec::new();
        let mut ham = 0.0_f64;
        let mut ray = 0.0_f64;
        let fm = if identity.case == "COLD_FLRW" {
            0.0
        } else {
            0.1
        };
        for line in lines {
            let v: Vec<_> = line.split(',').collect();
            if v.len() != hdr.len() {
                return Err(NetworkError::SourceMismatch);
            }
            if v[cx] != identity.case {
                continue;
            }
            let n = ids
                .iter()
                .map(|i| v[*i].parse::<f64>().map_err(|_| NetworkError::InvalidInput))
                .collect::<Result<Vec<_>, _>>()?;
            if !n.iter().all(|f| f.is_finite()) {
                return Err(NetworkError::NonFinite);
            }
            let (x, b, h, s, hx, t, a, sigma, signed, rho, p) = (
                n[0], n[1], n[2], n[3], n[4], n[5], n[6], n[7], n[8], n[9], n[10],
            );
            if h <= 0.0
                || a <= 0.0
                || rho < 0.0
                || p < 0.0
                || p > rho / 3.0 + 1e-19
                || (a / (A_REF * x.exp()) - 1.0).abs() > 3e-12
                || (signed - s / h).abs() > 3e-12
                || (sigma - 3.0_f64.sqrt() * (s / h).abs()).abs() > 3e-12
            {
                return Err(NetworkError::InputOutsideDomain);
            }
            let h0 = 2.1842852410855026e-18_f64;
            let h2 = h0
                * h0
                * (0.315 * (1.0 - fm) / a.powi(3)
                    + 0.000092 / a.powi(4)
                    + 0.6849080000000001
                    + rho)
                + s * s;
            let he = (h * h - h2).abs() / (h * h).max(h2);
            ham = ham.max(he);
            let hp = (h0
                * h0
                * (-3.0 * 0.315 * (1.0 - fm) / a.powi(3)
                    - 4.0 * 0.000092 / a.powi(4)
                    - 3.0 * (rho + p))
                - 6.0 * s * s)
                / (2.0 * h);
            let re = (hp - hx).abs() / hp.abs().max(1e-300);
            ray = ray.max(re);
            if he > 3e-12 || re > 3e-12 {
                return Err(NetworkError::InputOutsideDomain);
            }
            if let Some(prev) = nodes.last()
                && (x <= prev.x || t <= prev.t)
            {
                return Err(NetworkError::InputOutsideDomain);
            }
            nodes.push(Node { x, b, h, s, hx, t });
        }
        if nodes.len() != identity.points
            || nodes.len() < 2
            || nodes[0].x != 0.0
            || nodes[0].t != 0.0
        {
            return Err(NetworkError::SourceMismatch);
        }
        let mut segments = Vec::new();
        let mut times = vec![0.0];
        let mut lo = f64::INFINITY;
        let mut hi = f64::NEG_INFINITY;
        let mut clock_error = 0.0_f64;
        for w in nodes.windows(2) {
            let l = w[0];
            let r = w[1];
            let dx = r.x - l.x;
            let (a, b) = monotone_lrs_bounds(l.b, r.b, l.s / l.h, r.s / r.h, dx)?;
            lo = lo.min(a);
            hi = hi.max(b);
            let seg = Segment {
                x0: l.x,
                dx,
                b: coefficients(l.b, r.b, l.s / l.h, r.s / r.h, dx),
                lh: coefficients(l.h.ln(), r.h.ln(), l.hx / l.h, r.hx / r.h, dx),
            };
            let t = times.last().copied().unwrap_or(0.0) + seg.clock(r.x);
            if !t.is_finite() || t <= *times.last().unwrap_or(&0.0) {
                return Err(NetworkError::NoForwardProgress);
            }
            clock_error = clock_error.max((t - r.t).abs() / r.t.abs().max(1.0));
            times.push(t);
            segments.push(seg);
        }
        Ok(Self {
            identity,
            nodes,
            segments,
            times,
            slope_min: lo,
            slope_max: hi,
            hamiltonian_max: ham,
            raychaudhuri_max: ray,
            producer_clock_max_rel: clock_error,
        })
    }
    pub fn x_max(&self) -> f64 {
        self.nodes[self.nodes.len() - 1].x
    }
    pub fn time_max(&self) -> f64 {
        self.times[self.times.len() - 1]
    }
    pub fn point_at_x(&self, x: f64) -> Result<BassPoint, NetworkError> {
        if !x.is_finite() || x < 0.0 || x > self.x_max() {
            return Err(NetworkError::InputOutsideDomain);
        }
        let k = self
            .nodes
            .partition_point(|n| n.x < x)
            .clamp(1, self.nodes.len() - 1)
            - 1;
        let (b, h, s) = self.segments[k].state(x);
        let t = self.times[k] + self.segments[k].clock(x);
        if ![b, h, s, t].iter().all(|v| v.is_finite()) || h <= 0.0 {
            return Err(NetworkError::NonFinite);
        }
        Ok(BassPoint {
            x,
            a: A_REF * x.exp(),
            b,
            h,
            s,
            time_s: t,
        })
    }
    /// Safeguarded Newton inverse of the original positive GL8 proper-time chart.
    pub fn x_at_time(&self, t: f64) -> Result<f64, NetworkError> {
        if !t.is_finite() || t < 0.0 || t > self.time_max() {
            return Err(NetworkError::InputOutsideDomain);
        }
        if t == 0.0 {
            return Ok(0.0);
        }
        if t == self.time_max() {
            return Ok(self.x_max());
        }
        let k = self
            .times
            .partition_point(|u| *u < t)
            .clamp(1, self.times.len() - 1)
            - 1;
        let seg = &self.segments[k];
        let mut lo = seg.x0;
        let mut hi = self.nodes[k + 1].x;
        let mut x = lo + (hi - lo) * (t - self.times[k]) / (self.times[k + 1] - self.times[k]);
        for iter in 0..76 {
            let r = self.times[k] + seg.clock(x) - t;
            if r.abs() <= 8.0 * f64::EPSILON * t.max(1.0) {
                return Ok(x);
            }
            if r > 0.0 {
                hi = x;
            } else {
                lo = x;
            }
            let candidate = x - r * seg.state(x).1;
            let next = if iter < 12 && candidate > lo && candidate < hi {
                candidate
            } else {
                0.5 * lo + 0.5 * hi
            };
            if next == x || next <= lo || next >= hi {
                return Ok(x);
            }
            x = next;
        }
        Err(NetworkError::NoForwardProgress)
    }
    pub fn point_at_time(&self, t: f64) -> Result<BassPoint, NetworkError> {
        self.point_at_x(self.x_at_time(t)?)
    }
}
impl GeometryBackground for BassGeometry {
    fn snapshot(&self, t: f64) -> Result<GeometrySnapshot, ForwardError> {
        self.point_at_time(t)
            .and_then(BassPoint::snapshot)
            .map_err(|_| ForwardError::InvalidInput("BASS_POINT_DOMAIN"))
    }
}
/// Strictly internal provider crossings; the all-axis expansion condition was
/// tested on each complete Hermite interval when the source was loaded.
pub fn partition_at_photo_events(
    co: &Cohort,
    bg: &BassGeometry,
    t0: f64,
    t1: f64,
    d_ev: f64,
) -> Result<Vec<(f64, f64)>, NetworkError> {
    if !t0.is_finite()
        || !t1.is_finite()
        || t1 <= t0
        || t0 < co.birth_time_s
        || !d_ev.is_finite()
        || d_ev <= 13.60
    {
        return Err(NetworkError::InvalidInput);
    }
    let x0 = bg.x_at_time(t0)?;
    let x1 = bg.x_at_time(t1)?;
    let energy = |x: f64| -> Result<f64, NetworkError> {
        Ok(co.ray_at(&bg.point_at_x(x)?.snapshot()?)?.energy_ev)
    };
    let e0 = energy(x0)?;
    let e1 = energy(x1)?;
    let mut cuts = vec![t0, t1];
    let binding = crate::HHeModel::controlled_fixture().threshold_ev;
    let fits = crate::threshold_events::VERNER_FIT_EDGES_EV;
    for edge in [
        binding[0].max(fits[0]),
        binding[1].max(fits[1]),
        binding[2].max(fits[2]),
        d_ev,
    ] {
        if e0 <= edge || e1 >= edge {
            continue;
        }
        let mut lo = x0;
        let mut hi = x1;
        for _ in 0..72 {
            let mid = 0.5 * lo + 0.5 * hi;
            if mid <= lo || mid >= hi {
                break;
            }
            if energy(mid)? > edge {
                lo = mid;
            } else {
                hi = mid;
            }
        }
        let t = bg.point_at_x(0.5 * lo + 0.5 * hi)?.time_s;
        if t > t0 && t < t1 {
            cuts.push(t);
        }
    }
    cuts.sort_by(f64::total_cmp);
    cuts.dedup_by(|a, b| *a == *b);
    Ok(cuts.windows(2).map(|p| (p[0], p[1])).collect())
}
