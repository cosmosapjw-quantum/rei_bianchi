//! Original atomic HH Born ODE as a real-valued, scaled VigilODE client.
//!
//! The authoritative enclosure remains PHYS68 Arb. This independent native
//! path uses num-complex, gauss-quad and a pinned adaptive RODAS5P implementation.
//! The ordinary local error estimate is not an interval or global certificate.

use std::num::NonZeroUsize;
use std::sync::{Arc, Mutex};

use gauss_quad::GaussLegendre;
use num_complex::Complex64 as C;
use rodas5p_core::{CoreError, CoreResult, InitialGuess, LinearMethod, LinearSolverConfig};
use rodas5p_integrators::{
    AdaptiveStepConfig, ControllerKind, MaxStepPolicy, OdeProblem, OutputSchedule,
    Rodas5pMfFastResult, integrate_rodas5p_mf_fast_observed_gmres_into_ls_workspace,
};
use serde::{Deserialize, Serialize};

pub const UPSTREAM_COMMIT: &str = "a21d573980f66fe02891bd216153443b5352f921";
pub const FROZEN_SOURCE_SHA256: &str =
    "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d";
pub const B: f64 = 27.0;
pub const T: f64 = 65.0;
pub const K: f64 = 0.7;
pub const SHIFT: f64 = 0.7;
pub const TARGET_A: usize = 21;
pub const TARGET_B: usize = 20;
// Exactly represented powers of two: z_scale = q_scale squared.
pub const Q_SCALE: f64 = f64::from_bits(1103_u64 << 52); // 2^80
pub const D2_SCALE: f64 = f64::from_bits(1183_u64 << 52); // 2^160

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Request {
    pub schema: String,
    pub lmax: usize,
    pub angular_nodes: usize,
    pub rtol: f64,
    pub atol: f64,
    pub initial_step: f64,
    pub max_step: f64,
    pub max_attempts: usize,
    pub upstream_commit: String,
    pub frozen_source_sha256: String,
    #[serde(rename = "HH_R10")]
    pub hh_r10: String,
}

impl Request {
    pub fn validate(&self) -> CoreResult<()> {
        if self.schema != "PHYS69_VIGILODE_REQUEST_V1"
            || self.upstream_commit != UPSTREAM_COMMIT
            || self.frozen_source_sha256 != FROZEN_SOURCE_SHA256
            || self.hh_r10 != "OFF"
        {
            return Err(CoreError::InvalidInput("request identity mismatch".into()));
        }
        if !(21..=64).contains(&self.lmax)
            || self.angular_nodes < self.lmax + TARGET_A + 8
            || self.angular_nodes > 1024
            || self.max_attempts > 100_000
        {
            return Err(CoreError::InvalidInput("fixed client limits exceeded".into()));
        }
        self.adaptive().validate()
    }

    pub fn adaptive(&self) -> AdaptiveStepConfig {
        AdaptiveStepConfig {
            rtol: self.rtol,
            atol: self.atol,
            initial_step: self.initial_step,
            max_step: self.max_step,
            max_attempts: self.max_attempts,
            controller: ControllerKind::Pi,
            max_step_policy: MaxStepPolicy::StrictRepresentedCap,
            ..Default::default()
        }
    }
}

pub fn get(y: &[f64], i: usize) -> C {
    C::new(y[2 * i], y[2 * i + 1])
}

pub fn put(y: &mut [f64], i: usize, z: C) {
    y[2 * i] = z.re;
    y[2 * i + 1] = z.im;
}

#[derive(Debug)]
struct AngularRows {
    // Actual radial V = 2(1 + 1/d) exp(-2d), its two m=0 rows,
    // and exact analytic derivatives with respect to r of this quadrature.
    a: Vec<f64>,
    b: Vec<f64>,
    dr_a: Vec<f64>,
    dr_b: Vec<f64>,
}

#[derive(Debug)]
pub struct HhModel {
    pub channels: usize,
    nodes: Vec<(f64, f64)>,
    basis: Vec<Vec<f64>>,
    // Cache only immutable angular data at exact r bits, never state or JVPs.
    cache: Mutex<Option<(u64, Arc<AngularRows>)>>,
}

impl HhModel {
    pub fn new(lmax: usize, angular_nodes: usize) -> CoreResult<Self> {
        if !(21..=64).contains(&lmax)
            || angular_nodes < lmax + TARGET_A + 8
            || angular_nodes > 1024
        {
            return Err(CoreError::InvalidInput("invalid L or angular order".into()));
        }
        let quadrature = GaussLegendre::new(NonZeroUsize::new(angular_nodes).unwrap());
        let nodes: Vec<(f64, f64)> = quadrature.into_iter().collect();
        let mut basis = Vec::with_capacity(angular_nodes);
        for &(mu, weight) in &nodes {
            if !mu.is_finite() || mu.abs() >= 1.0 || !weight.is_finite() || weight <= 0.0 {
                return Err(CoreError::NonFinite("invalid Gaussian node or weight".into()));
            }
            let mut p = vec![1.0; lmax + 1];
            p[1] = mu;
            for j in 2..=lmax {
                p[j] = ((2 * j - 1) as f64 * mu * p[j - 1]
                    - (j - 1) as f64 * p[j - 2]) / j as f64;
            }
            for (j, pj) in p.iter_mut().enumerate() {
                *pj *= ((2 * j + 1) as f64 / 2.0).sqrt();
            }
            basis.push(p);
        }
        Ok(Self { channels: lmax + 1, nodes, basis, cache: Mutex::new(None) })
    }

    pub fn dimension(&self) -> usize {
        2 * (4 * self.channels + 1)
    }

    fn check(&self, tau: f64, y: &[f64], out: &[f64]) -> CoreResult<f64> {
        let r = T - tau;
        if !tau.is_finite() || !r.is_finite() || r <= SHIFT {
            return Err(CoreError::InvalidInput("radial coordinate outside analytic collar".into()));
        }
        if y.len() != self.dimension() || out.len() != self.dimension() {
            return Err(CoreError::Dimension("HH state dimension mismatch".into()));
        }
        if y.iter().any(|x| !x.is_finite()) {
            return Err(CoreError::NonFinite("nonfinite HH state".into()));
        }
        for j in 0..self.channels {
            if get(y, j).norm() == 0.0 {
                return Err(CoreError::InvalidInput("zero normalized Coulomb denominator".into()));
            }
        }
        Ok(r)
    }

    fn angular_rows(&self, r: f64) -> CoreResult<Arc<AngularRows>> {
        let mut cache = self.cache.lock().map_err(|_| CoreError::InvalidInput("angular cache poisoned".into()))?;
        if let Some((bits, rows)) = &*cache
            && *bits == r.to_bits()
        {
            return Ok(Arc::clone(rows));
        }
        let n = self.channels;
        let mut rows = AngularRows { a: vec![0.0; n], b: vec![0.0; n], dr_a: vec![0.0; n], dr_b: vec![0.0; n] };
        for (q, &(mu, weight)) in self.nodes.iter().enumerate() {
            // This exact formula is the original atomic off-center potential.
            let d = (r * r + SHIFT * SHIFT - 2.0 * r * SHIFT * mu).sqrt();
            let exp = (-2.0 * d).exp();
            let v = 2.0 * (1.0 + d.recip()) * exp * weight;
            let vr = -2.0 * exp * (2.0 + 2.0 / d + 1.0 / (d * d))
                * (r - SHIFT * mu) / d * weight;
            let p = &self.basis[q];
            for j in 0..n {
                rows.a[j] += p[TARGET_A] * p[j] * v;
                rows.b[j] += p[TARGET_B] * p[j] * v;
                rows.dr_a[j] += p[TARGET_A] * p[j] * vr;
                rows.dr_b[j] += p[TARGET_B] * p[j] * vr;
            }
        }
        let rows = Arc::new(rows);
        *cache = Some((r.to_bits(), Arc::clone(&rows)));
        Ok(rows)
    }

    pub fn rhs(&self, tau: f64, y: &[f64], out: &mut [f64]) -> CoreResult<()> {
        let r = self.check(tau, y, out)?;
        let n = self.channels;
        let rows = self.angular_rows(r)?;
        let (fa, fb) = (get(y, TARGET_A), get(y, TARGET_B));
        let mut dz = C::default();
        for j in 0..n {
            let f = get(y, j);
            let q = K * K + 2.0 / r - (j * (j + 1)) as f64 / (r * r);
            put(out, j, -get(y, n + j));
            put(out, n + j, f * q);
            put(out, 2 * n + j, fa * f * (Q_SCALE * rows.a[j]));
            put(out, 3 * n + j, fb * f * (Q_SCALE * rows.b[j]));
            // Bilinear, with no conjugation and no second-derivative factor 2.
            dz += (get(y, 2 * n + j) / f) * (get(y, 3 * n + j) / f);
        }
        put(out, 4 * n, dz);
        finite_output(out)
    }

    pub fn jvp(&self, tau: f64, y: &[f64], v: &[f64], out: &mut [f64]) -> CoreResult<()> {
        let r = self.check(tau, y, out)?;
        if v.len() != self.dimension() || v.iter().any(|x| !x.is_finite()) {
            return Err(CoreError::InvalidInput("invalid HH JVP direction".into()));
        }
        let n = self.channels;
        let rows = self.angular_rows(r)?;
        let (fa, fb) = (get(y, TARGET_A), get(y, TARGET_B));
        let (va, vb) = (get(v, TARGET_A), get(v, TARGET_B));
        let mut dz = C::default();
        for j in 0..n {
            let (f, df) = (get(y, j), get(v, j));
            let q = K * K + 2.0 / r - (j * (j + 1)) as f64 / (r * r);
            put(out, j, -get(v, n + j));
            put(out, n + j, df * q);
            put(out, 2 * n + j, (va * f + fa * df) * (Q_SCALE * rows.a[j]));
            put(out, 3 * n + j, (vb * f + fb * df) * (Q_SCALE * rows.b[j]));
            let (a, b) = (get(y, 2 * n + j) / f, get(y, 3 * n + j) / f);
            dz += (get(v, 2 * n + j) / f) * b
                + a * (get(v, 3 * n + j) / f) - 2.0 * a * b * (df / f);
        }
        put(out, 4 * n, dz);
        finite_output(out)
    }

    pub fn partial_tau(&self, tau: f64, y: &[f64], out: &mut [f64]) -> CoreResult<()> {
        let r = self.check(tau, y, out)?;
        out.fill(0.0);
        let n = self.channels;
        let rows = self.angular_rows(r)?;
        let (fa, fb) = (get(y, TARGET_A), get(y, TARGET_B));
        for j in 0..n {
            let f = get(y, j);
            let qt = 2.0 / (r * r) - 2.0 * (j * (j + 1)) as f64 / (r * r * r);
            put(out, n + j, f * qt);
            put(out, 2 * n + j, fa * f * (-Q_SCALE * rows.dr_a[j]));
            put(out, 3 * n + j, fb * f * (-Q_SCALE * rows.dr_b[j]));
        }
        finite_output(out)
    }

    pub fn ode(self: &Arc<Self>) -> CoreResult<OdeProblem> {
        let (rhs, jvp, dt) = (Arc::clone(self), Arc::clone(self), Arc::clone(self));
        OdeProblem::new(
            "WU088-HH-original-m0-two-Born-rows",
            self.dimension(),
            Arc::new(move |t, y, out| rhs.rhs(t, y, out)),
            None, None,
            Some(Arc::new(move |t, y, v, out| jvp.jvp(t, y, v, out))),
            Some(Arc::new(move |t, y, out| dt.partial_tau(t, y, out))),
            false, None, None,
        )
    }
}

fn finite_output(out: &[f64]) -> CoreResult<()> {
    if out.iter().any(|x| !x.is_finite()) {
        Err(CoreError::NonFinite("nonfinite HH callback output".into()))
    } else {
        Ok(())
    }
}

pub fn parse_seed(text: &str, lmax: usize) -> CoreResult<Vec<(C, C)>> {
    let mut rows = Vec::new();
    for line in text.lines().filter(|s| !s.trim().is_empty() && !s.trim_start().starts_with('#')) {
        let parts: Vec<_> = line.split_whitespace().collect();
        if parts.len() != 5 || parts[0].parse::<usize>().ok() != Some(rows.len()) {
            return Err(CoreError::InvalidInput("seed requires consecutive ell and four numbers".into()));
        }
        let numbers: Result<Vec<f64>, _> = parts[1..].iter().map(|s| s.parse()).collect();
        let numbers = numbers.map_err(|_| CoreError::InvalidInput("invalid seed float".into()))?;
        if numbers.iter().any(|x| !x.is_finite()) {
            return Err(CoreError::NonFinite("nonfinite seed".into()));
        }
        let f = C::new(numbers[0], numbers[1]);
        if f.norm() == 0.0 {
            return Err(CoreError::InvalidInput("zero seed denominator".into()));
        }
        rows.push((f, C::new(numbers[2], numbers[3])));
    }
    if !(21..=64).contains(&lmax) || rows.len() != lmax + 1 {
        return Err(CoreError::Dimension("seed does not match requested L".into()));
    }
    Ok(rows)
}

pub fn solve(request: &Request, seed: &[(C, C)]) -> CoreResult<Rodas5pMfFastResult> {
    request.validate()?;
    let model = Arc::new(HhModel::new(request.lmax, request.angular_nodes)?);
    if seed.len() != model.channels {
        return Err(CoreError::Dimension("seed count mismatch".into()));
    }
    let n = model.channels;
    let mut y0 = vec![0.0; model.dimension()];
    for (j, &(f, g)) in seed.iter().enumerate() {
        put(&mut y0, j, f);
        put(&mut y0, n + j, g);
    }
    let linear = LinearSolverConfig {
        method: LinearMethod::Gmres,
        rtol: 1.0e-12,
        atol: 1.0e-14,
        restart: 40,
        maxiter: 200,
        x0_strategy: InitialGuess::Zero,
        ..Default::default()
    };
    integrate_rodas5p_mf_fast_observed_gmres_into_ls_workspace(
        &model.ode()?, (0.0, T - B), &y0, &linear, &request.adaptive(),
        &OutputSchedule::new(vec![0.0, T - B])?,
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    fn state(model: &HhModel) -> Vec<f64> {
        let mut y = vec![0.0; model.dimension()];
        for j in 0..model.channels {
            put(&mut y, j, C::new(0.8 + 0.002 * j as f64, 0.2 - 0.001 * j as f64));
            put(&mut y, model.channels + j, C::new(0.1, -0.4));
            put(&mut y, 2 * model.channels + j, C::new(0.03, 0.004 * j as f64));
            put(&mut y, 3 * model.channels + j, C::new(-0.01, 0.007 * j as f64));
        }
        y
    }

    #[test]
    fn exact_power_of_two_scaling_preserves_bilinear_relation() {
        assert_eq!(Q_SCALE * Q_SCALE, D2_SCALE);
        assert_eq!((C::new(3.0, 4.0) * Q_SCALE) / Q_SCALE, C::new(3.0, 4.0));
    }

    #[test]
    fn crate_gaussian_moments_and_harmonic_orthonormality() {
        let m = HhModel::new(28, 96).unwrap();
        for power in [0_i32, 2, 4, 40, 56, 100, 190] {
            let sum: f64 = m.nodes.iter().map(|&(x, w)| w * x.powi(power)).sum();
            assert!((sum - 2.0 / (power as f64 + 1.0)).abs() < 3.0e-14);
        }
        for a in [0, 20, 21, 28] {
            for b in [0, 20, 21, 28] {
                let sum: f64 = m.nodes.iter().enumerate().map(|(i, &(_, w))| w * m.basis[i][a] * m.basis[i][b]).sum();
                assert!((sum - if a == b { 1.0 } else { 0.0 }).abs() < 3.0e-13);
            }
        }
    }

    #[test]
    fn analytic_jvp_matches_independent_centered_difference() {
        let m = HhModel::new(28, 96).unwrap();
        let y = state(&m);
        let v: Vec<f64> = (0..y.len()).map(|i| ((i * 7 % 31) as f64 - 15.0) / 30.0).collect();
        let eps = 2.0e-5;
        let (mut analytic, mut plus, mut minus) = (vec![0.0; y.len()], vec![0.0; y.len()], vec![0.0; y.len()]);
        m.jvp(37.3, &y, &v, &mut analytic).unwrap();
        m.rhs(37.3, &y.iter().zip(&v).map(|(a,b)| a + eps*b).collect::<Vec<_>>(), &mut plus).unwrap();
        m.rhs(37.3, &y.iter().zip(&v).map(|(a,b)| a - eps*b).collect::<Vec<_>>(), &mut minus).unwrap();
        for i in 0..y.len() {
            let finite = (plus[i] - minus[i]) / (2.0 * eps);
            assert!((analytic[i] - finite).abs() <= 2.0e-8 * analytic[i].abs().max(1.0), "component {i}: {} vs {finite}", analytic[i]);
        }
    }

    #[test]
    fn analytic_time_partial_matches_centered_difference() {
        let m = HhModel::new(28, 96).unwrap();
        let y = state(&m);
        let (mut analytic, mut plus, mut minus) = (vec![0.0; y.len()], vec![0.0; y.len()], vec![0.0; y.len()]);
        let eps = 2.0e-5;
        m.partial_tau(37.3, &y, &mut analytic).unwrap();
        m.rhs(37.3 + eps, &y, &mut plus).unwrap();
        m.rhs(37.3 - eps, &y, &mut minus).unwrap();
        for i in 0..y.len() {
            let finite = (plus[i] - minus[i]) / (2.0 * eps);
            assert!((analytic[i] - finite).abs() <= 2.0e-8 * analytic[i].abs().max(1.0), "component {i}: {} vs {finite}", analytic[i]);
        }
    }

    #[test]
    fn time_reversal_and_bilinear_d2_sign() {
        let m = HhModel::new(28, 96).unwrap();
        let n = m.channels;
        let mut y = state(&m);
        for j in 0..n { put(&mut y, j, C::new(1.0, 0.0)); put(&mut y, 2*n+j, C::default()); put(&mut y, 3*n+j, C::default()); }
        put(&mut y, 2*n+5, C::new(0.0, 2.0));
        put(&mut y, 3*n+5, C::new(0.0, 3.0));
        let mut out = vec![0.0; y.len()];
        m.rhs(0.0, &y, &mut out).unwrap();
        assert_eq!(get(&out, 4*n), C::new(-6.0, 0.0));
        assert_eq!(get(&out, 0), -get(&y, n));
    }

    #[test]
    fn zero_denominator_and_bad_shapes_are_rejected() {
        let m = HhModel::new(28, 96).unwrap();
        let mut y = state(&m);
        let mut out = vec![0.0; y.len()];
        put(&mut y, 3, C::default());
        assert!(m.rhs(1.0, &y, &mut out).is_err());
        assert!(m.rhs(1.0, &[], &mut out).is_err());
        assert!(HhModel::new(64, 32).is_err());
    }

    #[test]
    fn quadrature_cache_is_bitwise_radial_and_state_independent() {
        let m = HhModel::new(28, 96).unwrap();
        let rows = m.angular_rows(30.0).unwrap();
        assert!(Arc::ptr_eq(&rows, &m.angular_rows(30.0).unwrap()));
        assert!(!Arc::ptr_eq(&rows, &m.angular_rows(31.0).unwrap()));
        assert_eq!(rows.a, m.angular_rows(30.0).unwrap().a);
    }
}
