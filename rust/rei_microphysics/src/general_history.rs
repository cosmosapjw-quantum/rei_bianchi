//! Fixed canonical registry on a supplied, expanding Bianchi-I geometry history.
//! Interpolates F=C/a and ln H in ln a; projects the interpolated F to det=1.
use crate::{
    general_angular::{Coframe, GeneralAngular, RadiationMoments},
    ForwardError,
};
const H0: f64 = 2.1842852410855023e-18;
#[derive(Clone, Copy, Debug)]
pub struct HistoryPoint {
    pub a: f64,
    pub h: f64,
    pub f: Coframe,
}
#[derive(Clone, Debug)]
pub struct GeneralHistory {
    p: Vec<HistoryPoint>,
    grid: GeneralAngular,
}
fn bad() -> ForwardError {
    ForwardError::InvalidInput("GENERAL_HISTORY_DOMAIN")
}
fn det(f: Coframe) -> f64 {
    f[0][0] * (f[1][1] * f[2][2] - f[1][2] * f[2][1])
        - f[0][1] * (f[1][0] * f[2][2] - f[1][2] * f[2][0])
        + f[0][2] * (f[1][0] * f[2][1] - f[1][1] * f[2][0])
}
fn coframe(p: HistoryPoint) -> Coframe {
    p.f.map(|r| r.map(|x| p.a * x))
}
impl GeneralHistory {
    pub fn new(p: Vec<HistoryPoint>, nmu: usize, nphi: usize) -> Result<Self, ForwardError> {
        if p.len() < 2
            || p.windows(2).any(|w| w[1].a <= w[0].a)
            || p.iter().any(|x| {
                x.a <= 0.
                    || x.h <= 0.
                    || !x.a.is_finite()
                    || !x.h.is_finite()
                    || !x.f.iter().flatten().all(|v| v.is_finite())
                    || (det(x.f) - 1.).abs() > 1e-7
            })
        {
            return Err(bad());
        }
        let grid = GeneralAngular::new(coframe(p[0]), coframe(p[p.len() / 2]), nmu, nphi)?;
        Ok(Self { p, grid })
    }
    /// Change only the supplied trial clock/coframe, never the canonical registry.
    pub fn replace_interval(&mut self, p: Vec<HistoryPoint>) -> Result<(), ForwardError> {
        if p.len() < 2
            || p.windows(2).any(|w| w[1].a <= w[0].a)
            || p.iter().any(|x| {
                x.a <= 0.
                    || x.h <= 0.
                    || !x.a.is_finite()
                    || !x.h.is_finite()
                    || !x.f.iter().flatten().all(|v| v.is_finite())
                    || (det(x.f) - 1.).abs() > 1e-7
            })
        {
            return Err(bad());
        }
        let old = self.point(p[0].a)?;
        if old.h != p[0].h || old.f != p[0].f {
            return Err(bad());
        }
        self.p = p;
        Ok(())
    }
    pub fn len(&self) -> usize {
        self.grid.len()
    }
    pub fn interval(&self) -> [f64; 2] {
        [self.p[0].a, self.p.last().unwrap().a]
    }
    pub fn point(&self, a: f64) -> Result<HistoryPoint, ForwardError> {
        if !a.is_finite() || a < self.p[0].a || a > self.p.last().unwrap().a {
            return Err(bad());
        }
        let i = self.p.partition_point(|p| p.a <= a);
        let l = self.p[i - 1];
        if a == l.a {
            return Ok(l);
        }
        let r = self.p[i];
        let w = (a / l.a).ln() / (r.a / l.a).ln();
        let mut f: Coframe = std::array::from_fn(|i| {
            std::array::from_fn(|j| l.f[i][j] + w * (r.f[i][j] - l.f[i][j]))
        });
        let d = det(f);
        if d <= 0. || !d.is_finite() {
            return Err(bad());
        }
        f = f.map(|x| x.map(|y| y / d.cbrt()));
        Ok(HistoryPoint {
            a,
            h: l.h * (w * (r.h / l.h).ln()).exp(),
            f,
        })
    }
    pub fn rays(
        &self,
        a: f64,
    ) -> Result<
        (
            Vec<crate::axbi_covariant_transport::RayGeometry>,
            Vec<[f64; 3]>,
        ),
        ForwardError,
    > {
        let c = coframe(self.point(a)?);
        let q = self.grid.source_at(c)?;
        Ok((
            q.weights
                .iter()
                .zip(q.scales.iter().zip(&q.direction))
                .map(|(w, (s, n))| crate::axbi_covariant_transport::RayGeometry {
                    scale: *s,
                    mu: n[2],
                    angular_weight: *w,
                })
                .collect(),
            q.direction,
        ))
    }
    pub fn moments(&self, a: f64, u: &[f64]) -> Result<RadiationMoments, ForwardError> {
        self.grid.moments_at(coframe(self.point(a)?), u)
    }
    pub fn dt(&self, a: f64, b: f64) -> Result<f64, ForwardError> {
        if b <= a {
            return Err(bad());
        }
        let mut l = self.point(a)?;
        let end = self.point(b)?;
        let mut t = 0.;
        for r in self
            .p
            .iter()
            .copied()
            .filter(|p| p.a > a && p.a < b)
            .chain(std::iter::once(end))
        {
            let d = (r.h / l.h).ln();
            let fac = if d == 0. { 1. } else { -(-d).exp_m1() / d };
            t += (r.a / l.a).ln() * fac / (H0 * l.h);
            l = r;
        }
        if !t.is_finite() || t <= 0. {
            return Err(bad());
        }
        Ok(t)
    }
}
