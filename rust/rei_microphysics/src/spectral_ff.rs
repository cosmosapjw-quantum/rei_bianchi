//! Isotropic FLRW reference x=E/(k_B T_gamma), signed occupation distortion.
//! Research subflow: no angular transport or implicit general gas coupling.
use crate::{ff_balance::gaunt, ForwardError};
fn bad() -> ForwardError {
    ForwardError::InvalidInput("SPECTRAL_FF_DOMAIN")
}
#[derive(Clone, Debug)]
pub struct SpectralFf {
    x: Vec<f64>,
    delta: Vec<f64>,
    dl: f64,
}
#[derive(Debug, Clone, Copy)]
pub struct Exchange {
    pub net: f64,
    pub emission: f64,
    pub thin_net: f64,
    pub planck_abs: f64,
    pub max_tau: f64,
    pub thick_cells: usize,
    pub absolute_ratio: f64,
}
fn mixed(t: f64, f: f64, u: f64) -> Result<f64, ForwardError> {
    let g2 = 13.605693122994 / (8.617333262145e-5 * t);
    Ok((1. - f) * gaunt(g2, u)? + f * gaunt(4. * g2, u)?)
}
fn norm(t: f64, f: f64) -> Result<f64, ForwardError> {
    let lo = 1e-10_f64.ln();
    let dl = (60_f64.ln() - lo) / 2048.;
    let mut v = 0.;
    for i in 0..=2048 {
        let x = (lo + dl * i as f64).exp();
        let w = if i == 0 || i == 2048 {
            1.
        } else if i % 2 == 0 {
            2.
        } else {
            4.
        };
        v += w * x * (-x).exp() * mixed(t, f, x)?;
    }
    Ok(v * dl / 3.)
}
fn pl(x: f64) -> f64 {
    1. / x.exp_m1()
}
impl SpectralFf {
    pub fn new(xmin: f64, xmax: f64, n: usize) -> Result<Self, ForwardError> {
        if !xmin.is_finite() || !xmax.is_finite() || xmin <= 0. || xmax <= xmin || n < 16 {
            return Err(bad());
        }
        let dl = (xmax / xmin).ln() / n as f64;
        Ok(Self {
            x: (0..n)
                .map(|i| xmin * ((i as f64 + 0.5) * dl).exp())
                .collect(),
            delta: vec![0.; n],
            dl,
        })
    }
    pub fn nodes(&self) -> &[f64] {
        &self.x
    }
    pub fn distortion(&self) -> &[f64] {
        &self.delta
    }
    /// Load a signed distortion only on the same immutable frequency grid.
    /// The caller binds grid identity; invalid payloads leave state unchanged.
    pub fn restore_distortion(&mut self, d: &[f64]) -> Result<(), ForwardError> {
        if d.len() != self.x.len()
            || d.iter()
                .zip(&self.x)
                .any(|(&v, &x)| !v.is_finite() || v + pl(x) < 0. || !(v + pl(x)).is_finite())
        {
            return Err(bad());
        }
        self.delta.copy_from_slice(d);
        Ok(())
    }
    fn phase(&self, x: f64, bb: f64) -> f64 {
        bb * 15. / std::f64::consts::PI.powi(4) * x.powi(4) * self.dl
    }
    pub fn energy(&self, bb: f64) -> Result<f64, ForwardError> {
        if !bb.is_finite() || bb <= 0. || self.x.len() != self.delta.len() {
            return Err(bad());
        }
        Ok(self
            .x
            .iter()
            .zip(&self.delta)
            .map(|(&x, &d)| self.phase(x, bb) * d)
            .sum())
    }
    /// B is the original gross integrated emission per H over the frozen step.
    /// Absolute normalization replaces B only when explicitly selected.
    pub fn advance(
        &mut self,
        t: f64,
        tc: f64,
        frac: f64,
        b: f64,
        bb: f64,
        absolute: bool,
    ) -> Result<Exchange, ForwardError> {
        if ![t, tc, frac, b, bb].iter().all(|x| x.is_finite())
            || t <= 0.
            || tc <= 0.
            || bb <= 0.
            || b < 0.
            || !(0. ..=1.).contains(&frac)
            || self.x.len() != self.delta.len()
        {
            return Err(bad());
        }
        let gnorm = norm(t, frac)?;
        let ratio = 1.4255566872911698e-27 * gnorm
            / (1.43e-27 * (1.1 + 0.34 * (-(5.5 - t.log10()).powi(2) / 3.).exp()));
        let b = if absolute { b * ratio } else { b };
        let r = tc / t;
        let mut q = Exchange {
            net: 0.,
            emission: 0.,
            thin_net: 0.,
            planck_abs: 0.,
            max_tau: 0.,
            thick_cells: 0,
            absolute_ratio: ratio,
        };
        let mut next = self.delta.clone();
        for (i, &x) in self.x.iter().enumerate() {
            let u = r * x;
            let p = self.phase(x, bb);
            let g = mixed(t, frac, u)?;
            let amp = b / gnorm * u * g * self.dl;
            let birth = amp * (-u).exp();
            let tau = amp * (-(-u).exp_m1()) / p;
            let fp = pl(x);
            let fe = pl(u);
            let d = self.delta[i];
            if ![tau, d, fp, fe, p].iter().all(|v| v.is_finite()) || tau < 0. || fp + d < 0. {
                return Err(bad());
            }
            let dd = (fe - fp - d) * (-(-tau).exp_m1());
            // When relaxation rounds to complete thermalization, use exact target
            // distortion rather than subtracting nearly equal large occupations.
            next[i] = if tau > 36. {
                fe - fp + (d - (fe - fp)) * (-tau).exp()
            } else {
                d + dd
            };
            if next[i] + fp < 0. || !next[i].is_finite() {
                return Err(bad());
            }
            q.net += p * (next[i] - d);
            q.emission += birth;
            let abs = p * tau * fp;
            q.planck_abs += abs;
            q.thin_net += birth - abs;
            q.max_tau = q.max_tau.max(tau);
            q.thick_cells += usize::from(tau >= 1.);
        }
        self.delta = next;
        Ok(q)
    }
}

/// Isotropic reference blackbody energy per H in eV, with nH in cm^-3.
pub fn blackbody_per_h(tc: f64, nh: f64) -> Result<f64, ForwardError> {
    let a = 8. * std::f64::consts::PI.powi(5) * 1.380649e-23_f64.powi(4)
        / (15. * 6.62607015e-34_f64.powi(3) * 299792458_f64.powi(3));
    let e = a * tc.powi(4) / (nh * 1e6) / 1.602176634e-19;
    if !e.is_finite() || e <= 0. {
        return Err(bad());
    }
    Ok(e)
}
