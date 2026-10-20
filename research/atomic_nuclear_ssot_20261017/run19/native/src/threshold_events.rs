//! Opt-in P4/S4a spectral event timing for *constant directional Hubble rates*.
//! This module finds every Verner/D photo-edge passage on a finite Bianchi-I
//! photon segment, including two passages when some axes expand and others
//! contract. It makes no claim for time-dependent H_i(t) or smooth-rate error.
use crate::bianchi_i::{
    ConstantAxisymmetricBackground, ConstantHubbleBackground, GeometryBackground,
};

// Only the two actual source-owned constant-H_i background types may call the
// convexity-based event locator. Arbitrary time-varying callbacks are excluded
// at compile time, rather than merely checked at a few sample times.
mod sealed {
    pub trait Sealed {}
    impl Sealed for super::ConstantHubbleBackground {}
    impl Sealed for super::ConstantAxisymmetricBackground {}
}
pub trait ConstantHubbleGeometry: GeometryBackground + sealed::Sealed {}
impl ConstantHubbleGeometry for ConstantHubbleBackground {}
impl ConstantHubbleGeometry for ConstantAxisymmetricBackground {}

use crate::full_network::NetworkError;
use crate::source_age::Cohort;

/// Source-locked Verner outer-shell fit turn-on edges (eV), distinct from
/// the `HHeModel` chemical binding thresholds and from the D binding edge.
pub const VERNER_FIT_EDGES_EV: [f64; 3] = [13.60, 24.59, 54.42];

fn e_and_d_e2(
    co: &Cohort,
    bg: &impl ConstantHubbleGeometry,
    t: f64,
) -> Result<(f64, f64), NetworkError> {
    let g = bg
        .snapshot(t)
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    let ray = co.ray_at(&g)?;
    let energy = ray.energy_ev;
    let de2 = -2.0
        * energy
        * energy
        * ray
            .direction
            .iter()
            .zip(g.hubble_per_s.iter())
            .map(|(n, h)| n * n * h)
            .sum::<f64>();
    if !energy.is_finite() || energy <= 0.0 || !de2.is_finite() {
        return Err(NetworkError::NonFinite);
    }
    Ok((energy, de2))
}

fn crossing_root(
    co: &Cohort,
    bg: &impl ConstantHubbleGeometry,
    mut left: f64,
    mut right: f64,
    edge: f64,
) -> Result<Option<f64>, NetworkError> {
    let fl = e_and_d_e2(co, bg, left)?.0 - edge;
    let fr = e_and_d_e2(co, bg, right)?.0 - edge;
    if fl == 0.0 || fr == 0.0 || (fl < 0.0) == (fr < 0.0) {
        return Ok(None);
    }
    let side = fl < 0.0;
    for _ in 0..80 {
        let middle = 0.5 * left + 0.5 * right;
        if middle <= left || middle >= right {
            break;
        }
        let f = e_and_d_e2(co, bg, middle)?.0 - edge;
        if f == 0.0 {
            return Ok(Some(middle));
        }
        if (f < 0.0) == side {
            left = middle;
        } else {
            right = middle;
        }
    }
    Ok(Some(0.5 * left + 0.5 * right))
}

/// Ascending internal crossing times, not interval endpoints.
/// For constant H_i, E² = Σ C_i exp(-2H_i t) is convex; its derivative is
/// monotone, so the energy has at most one interior minimum. We locate that
/// minimum and bracket all threshold crossings on each monotone part.
/// Only provider photo *fit* edges are used here, not chemical binding energy.
pub fn threshold_cut_times(
    co: &Cohort,
    bg: &impl ConstantHubbleGeometry,
    t0: f64,
    t1: f64,
    d_binding_ev: f64,
) -> Result<Vec<f64>, NetworkError> {
    if !t0.is_finite()
        || !t1.is_finite()
        || t1 <= t0
        || !d_binding_ev.is_finite()
        || d_binding_ev <= VERNER_FIT_EDGES_EV[0]
    {
        return Err(NetworkError::InvalidInput);
    }
    let g0 = bg
        .snapshot(t0)
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    let g1 = bg
        .snapshot(t1)
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    let gm = bg
        .snapshot(t0 + 0.5 * (t1 - t0))
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    // Do not pretend the constant-H convexity proof applies to an arbitrary
    // callback supplying changing H(t). Native S3 background satisfies this.
    for i in 0..3 {
        let h = g0.hubble_per_s[i];
        let hscale = h
            .abs()
            .max(g1.hubble_per_s[i].abs())
            .max(gm.hubble_per_s[i].abs())
            .max(1e-40);
        if (h - g1.hubble_per_s[i]).abs() > 1e-13 * hscale
            || (h - gm.hubble_per_s[i]).abs() > 1e-13 * hscale
        {
            return Err(NetworkError::InputOutsideDomain);
        }
    }
    let (_, da) = e_and_d_e2(co, bg, t0)?;
    let (_, db) = e_and_d_e2(co, bg, t1)?;
    let mut intervals = vec![(t0, t1)];
    if da < 0. && db > 0. {
        let (mut left, mut right) = (t0, t1);
        for _ in 0..80 {
            let middle = 0.5 * left + 0.5 * right;
            if middle <= left || middle >= right {
                break;
            }
            let d = e_and_d_e2(co, bg, middle)?.1;
            if d <= 0. {
                left = middle;
            } else {
                right = middle;
            }
        }
        let min_t = 0.5 * left + 0.5 * right;
        if min_t > t0 && min_t < t1 {
            intervals = vec![(t0, min_t), (min_t, t1)];
        }
    }
    let edges = [
        VERNER_FIT_EDGES_EV[0],
        VERNER_FIT_EDGES_EV[1],
        VERNER_FIT_EDGES_EV[2],
        d_binding_ev,
    ];
    let mut cuts = Vec::new();
    for edge in edges {
        for &(left, right) in &intervals {
            if let Some(t) = crossing_root(co, bg, left, right, edge)?
                && t > t0
                && t < t1
            {
                cuts.push(t);
            }
        }
    }
    cuts.sort_by(f64::total_cmp);
    let resolution = 16.0 * f64::EPSILON * t0.abs().max(t1.abs()).max(1.);
    cuts.dedup_by(|a, b| (*a - *b).abs() <= resolution);
    Ok(cuts)
}

/// Complete subintervals from an existing opacity segment. Every returned
/// interior endpoint is a photo turn-on/off event; optional no-cut segments
/// retain the exact original midpoint path. All widths must be positive.
pub fn partition_at_photo_events(
    co: &Cohort,
    bg: &impl ConstantHubbleGeometry,
    t0: f64,
    t1: f64,
    d_binding_ev: f64,
) -> Result<Vec<(f64, f64)>, NetworkError> {
    let cuts = threshold_cut_times(co, bg, t0, t1, d_binding_ev)?;
    let mut start = t0;
    let mut segments = Vec::with_capacity(cuts.len() + 1);
    for t in cuts.into_iter().chain(std::iter::once(t1)) {
        if t <= start {
            return Err(NetworkError::NoForwardProgress);
        }
        segments.push((start, t));
        start = t;
    }
    Ok(segments)
}
