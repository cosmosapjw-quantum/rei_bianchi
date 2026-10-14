//! Stress-free, density-fixed axisymmetric Bianchi I in elapsed proper seconds.
//! Parameters have no physical defaults; SAME_H is an explicit counterfactual.
use crate::{AxisymmetricPoint, ForwardError, GeometryBackground, GeometrySnapshot};

pub const DEFAULT_PANELS: usize = 4096;
fn invalid(tag: &'static str) -> ForwardError {
    ForwardError::InvalidInput(tag)
}
fn finite(x: f64) -> Result<f64, ForwardError> {
    if x.is_finite() {
        Ok(x)
    } else {
        Err(invalid("AxbiNonFinite"))
    }
}
fn positive(x: f64) -> Result<f64, ForwardError> {
    if finite(x)? > 0.0 {
        Ok(x)
    } else {
        Err(invalid("AxbiPositive"))
    }
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Cosmology {
    pub h0_per_s: f64,
    pub omega_m: f64,
    pub omega_r: f64,
    pub omega_lambda: f64,
}
impl Cosmology {
    pub fn hubble_flrw(&self, a: f64) -> Result<f64, ForwardError> {
        positive(a)?;
        positive(self.h0_per_s)?;
        for density in [self.omega_m, self.omega_r, self.omega_lambda] {
            if finite(density)? < 0.0 {
                return Err(invalid("AxbiDensity"));
            }
        }
        positive(
            self.h0_per_s
                * positive(
                    self.omega_m / a.powi(3) + self.omega_r / a.powi(4) + self.omega_lambda,
                )?
                .sqrt(),
        )
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BackgroundFamily {
    PhysicalDensityFixed,
    SameHDiagnostic,
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct BackgroundPoint {
    pub a: f64,
    pub b: f64,
    pub time_s: f64,
    pub h_flrw_per_s: f64,
    pub h_per_s: f64,
    pub s_per_s: f64,
    /// Instantaneous s/H, distinct from the fixed signed q_ref.
    pub sigma: f64,
}
impl BackgroundPoint {
    pub fn geometry(&self) -> Result<GeometrySnapshot, ForwardError> {
        AxisymmetricPoint::new(self.a, self.b, self.h_per_s, self.s_per_s)?.snapshot()
    }
    pub fn sigma_squared_per_s2(&self) -> f64 {
        3.0 * self.s_per_s * self.s_per_s
    }
}
#[derive(Clone, Debug)]
pub struct AxbiBackground {
    cosmology: Cosmology,
    a_ref: f64,
    a_end: f64,
    b_ref: f64,
    q_ref: f64,
    family: BackgroundFamily,
    panels: usize,
}
impl AxbiBackground {
    pub fn new(
        cosmology: Cosmology,
        a_ref: f64,
        a_end: f64,
        b_ref: f64,
        q_ref: f64,
        family: BackgroundFamily,
        panels: usize,
    ) -> Result<Self, ForwardError> {
        positive(a_ref)?;
        positive(a_end)?;
        finite(b_ref)?;
        finite(q_ref)?;
        if a_end <= a_ref || !(2..=65536).contains(&panels) || panels % 2 != 0 {
            return Err(invalid("AxbiDomainOrPanels"));
        }
        cosmology.hubble_flrw(a_ref)?;
        cosmology.hubble_flrw(a_end)?;
        let result = Self {
            cosmology,
            a_ref,
            a_end,
            b_ref,
            q_ref,
            family,
            panels,
        };
        result.point_at_scale(a_end)?;
        Ok(result)
    }
    pub fn q_ref(&self) -> f64 {
        self.q_ref
    }
    pub fn family(&self) -> BackgroundFamily {
        self.family
    }
    fn rates(&self, a: f64) -> Result<(f64, f64, f64), ForwardError> {
        let hf = self.cosmology.hubble_flrw(a)?;
        let s = finite(
            self.q_ref * self.cosmology.hubble_flrw(self.a_ref)? * (self.a_ref / a).powi(3),
        )?;
        let h = match self.family {
            BackgroundFamily::PhysicalDensityFixed => positive(hf.hypot(s))?,
            BackgroundFamily::SameHDiagnostic => hf,
        };
        Ok((hf, h, s))
    }
    pub fn point_at_scale(&self, a: f64) -> Result<BackgroundPoint, ForwardError> {
        positive(a)?;
        if a < self.a_ref || a > self.a_end {
            return Err(invalid("AxbiScaleDomain"));
        }
        let span = (a / self.a_ref).ln();
        let dx = span / self.panels as f64;
        let (mut clock, mut anisotropy) = (0.0, 0.0);
        for i in 0..=self.panels {
            let ai = self.a_ref * (dx * i as f64).exp();
            let (_, h, s) = self.rates(ai)?;
            let w = if i == 0 || i == self.panels {
                1.0
            } else if i % 2 == 0 {
                2.0
            } else {
                4.0
            };
            clock += w / h;
            anisotropy += w * s / h;
        }
        let (hf, h, s) = self.rates(a)?;
        let point = BackgroundPoint {
            a,
            b: finite(self.b_ref + anisotropy * dx / 3.0)?,
            time_s: finite(clock * dx / 3.0)?,
            h_flrw_per_s: hf,
            h_per_s: h,
            s_per_s: s,
            sigma: finite(s / h)?,
        };
        point.geometry()?;
        Ok(point)
    }
    pub fn point_at_time(&self, time_s: f64) -> Result<BackgroundPoint, ForwardError> {
        finite(time_s)?;
        let end = self.point_at_scale(self.a_end)?;
        if time_s < 0.0 || time_s > end.time_s {
            return Err(invalid("AxbiTimeDomain"));
        }
        if time_s == 0.0 {
            return self.point_at_scale(self.a_ref);
        }
        if time_s == end.time_s {
            return Ok(end);
        }
        let (mut lo, mut hi) = (self.a_ref.ln(), self.a_end.ln());
        for _ in 0..64 {
            let mid = (lo + hi) * 0.5;
            if self.point_at_scale(mid.exp())?.time_s < time_s {
                lo = mid;
            } else {
                hi = mid;
            }
        }
        self.point_at_scale(((lo + hi) * 0.5).exp())
    }
}
impl GeometryBackground for AxbiBackground {
    fn snapshot(&self, t: f64) -> Result<GeometrySnapshot, ForwardError> {
        self.point_at_time(t)?.geometry()
    }
}

/// Actual omitted-stress history: SI pressure/energy, elapsed proper seconds.
#[derive(Clone, Copy, Debug)]
pub struct FeedbackSample {
    pub a: f64,
    pub time_s: f64,
    pub pressure_anisotropy_j_m3: f64,
    pub extra_energy_j_m3: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct FeedbackDiagnostic {
    pub max_abs_delta_s_over_h: f64,
    pub max_extra_energy_over_background: f64,
    /// This is a sampled trapezoidal perturbative estimate, not a rigorous bound.
    pub endpoint_delta_s_per_s: f64,
}
/// No stress history is inferred from q. Include free-streaming CMB stress as
/// well as ionizing photons. G and c must be supplied in SI units.
pub fn omitted_feedback(
    background: &AxbiBackground,
    samples: &[FeedbackSample],
    g_m3_kg_s2: f64,
    c_m_s: f64,
) -> Result<FeedbackDiagnostic, ForwardError> {
    positive(g_m3_kg_s2)?;
    positive(c_m_s)?;
    if samples.len() < 2 {
        return Err(invalid("AxbiFeedbackCoverage"));
    }
    if samples[0].a != background.a_ref || samples[0].time_s != 0.0 {
        return Err(invalid("AxbiFeedbackOrigin"));
    }
    let k = positive(8.0 * std::f64::consts::PI * g_m3_kg_s2 / (3.0 * c_m_s * c_m_s))?;
    let mut integral = 0.0;
    let mut diagnostic = FeedbackDiagnostic {
        max_abs_delta_s_over_h: 0.0,
        max_extra_energy_over_background: 0.0,
        endpoint_delta_s_per_s: 0.0,
    };
    for (i, sample) in samples.iter().enumerate() {
        let point = background.point_at_scale(sample.a)?;
        finite(sample.time_s)?;
        finite(sample.pressure_anisotropy_j_m3)?;
        if finite(sample.extra_energy_j_m3)? < 0.0 {
            return Err(invalid("AxbiFeedbackEnergy"));
        }
        if (sample.time_s - point.time_s).abs() > 1e-7 * point.time_s.max(1.0) {
            return Err(invalid("AxbiFeedbackClock"));
        }
        if i > 0 {
            let prev = &samples[i - 1];
            if sample.a <= prev.a || sample.time_s <= prev.time_s {
                return Err(invalid("AxbiFeedbackOrder"));
            }
            integral = finite(
                integral
                    + 0.5
                        * k
                        * (sample.a.powi(3) * sample.pressure_anisotropy_j_m3
                            + prev.a.powi(3) * prev.pressure_anisotropy_j_m3)
                        * (sample.time_s - prev.time_s),
            )?;
        }
        let ds = finite(integral / sample.a.powi(3))?;
        diagnostic.max_abs_delta_s_over_h = diagnostic
            .max_abs_delta_s_over_h
            .max(finite(ds.abs() / point.h_per_s)?);
        // Total isotropic background including Lambda: H_FLRW²/k.
        diagnostic.max_extra_energy_over_background =
            diagnostic.max_extra_energy_over_background.max(finite(
                sample.extra_energy_j_m3 * k / point.h_flrw_per_s.powi(2),
            )?);
        diagnostic.endpoint_delta_s_per_s = ds;
    }
    Ok(diagnostic)
}

/// Free-streamed initially isotropic massless-radiation moments, SI units.
#[derive(Clone, Copy, Debug)]
pub struct IsotropicRadiationMoments {
    pub energy_j_m3: f64,
    pub pressure_anisotropy_j_m3: f64,
    pub signed_energy_correction_j_m3: f64,
    pub dipole_energy_j_m3: f64,
}
/// Integrate initial directions mu0, not the evolved local angular measure.
/// The full effective Omega_r fluid may be used as a conservative free-stream
/// envelope; this is a perturbative diagnostic rather than coupled evolution.
pub fn isotropic_initial_radiation_moments(
    a: f64,
    b: f64,
    a_ref: f64,
    b_ref: f64,
    epsilon_ref_j_m3: f64,
    panels: usize,
) -> Result<IsotropicRadiationMoments, ForwardError> {
    positive(a)?;
    positive(a_ref)?;
    finite(b)?;
    finite(b_ref)?;
    if finite(epsilon_ref_j_m3)? < 0.0 || !(2..=65536).contains(&panels) || panels % 2 != 0 {
        return Err(invalid("AxbiRadiationDomain"));
    }
    let db = finite(b - b_ref)?;
    let ep = positive((2.0 * db).exp())?;
    let ez = positive((-4.0 * db).exp())?;
    let mut monopole = 0.0;
    let mut quadrupole = 0.0;
    for i in 0..=panels {
        let mu = i as f64 / panels as f64;
        let r = positive(((1.0 - mu * mu) * ep + mu * mu * ez).sqrt())?;
        let local_mu = mu * ez.sqrt() / r;
        let w = if i == 0 || i == panels {
            1.0
        } else if i % 2 == 0 {
            2.0
        } else {
            4.0
        };
        monopole += w * r;
        quadrupole += w * r * (3.0 * local_mu * local_mu - 1.0) / 2.0;
    }
    let eps_iso = finite(epsilon_ref_j_m3 * (a_ref / a).powi(4))?;
    let norm = 3.0 * panels as f64;
    let energy = finite(eps_iso * monopole / norm)?;
    Ok(IsotropicRadiationMoments {
        energy_j_m3: energy,
        pressure_anisotropy_j_m3: finite(eps_iso * quadrupole / norm)?,
        signed_energy_correction_j_m3: finite(energy - eps_iso)?,
        dipole_energy_j_m3: 0.0,
    })
}
