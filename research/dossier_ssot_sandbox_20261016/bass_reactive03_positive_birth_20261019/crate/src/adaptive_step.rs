//! P4/S9 opt-in, observable-projected local step-doubling control.
//! The underlying JointCxSplit and all source owners are unchanged.
//! Accept the TWO HALF STEPS, never extrapolate states or budgets.
//! Coarse/rejected trials cannot mutate the input or contribute events.
//! This controls a computed local defect, NOT a certified global error.
use crate::bianchi_i::GeometryBackground;
use crate::full_network::{EV_J, NetworkConfig, NetworkError};
use crate::isotope_state::IsotopeSpecies as S;
use crate::midpoint_coupled::{Centering, MidpointBridge};
use crate::source_age::{AgeHistory, AgeStep};
use std::collections::BTreeMap;

/// Absolute tolerances retain their physical units. Defaults are NOT an EoR
/// acceptance policy: the experiment must record its chosen values.
#[derive(Clone, Copy, Debug)]
pub struct LocalTolerances {
    pub rtol: f64,
    pub nuclei_m3: [f64; 13],
    pub gas_energy_j_m3: f64,
    pub photon_number_com3: f64,
    pub photon_energy_j_com3: f64,
    pub photo_events_com3: [f64; 4],
    pub angular_p2_energy: f64,
}
impl Default for LocalTolerances {
    fn default() -> Self {
        Self {
            rtol: 1e-3,
            nuclei_m3: [1e-10; 13],
            gas_energy_j_m3: 1e-25,
            photon_number_com3: 1e-22,
            photon_energy_j_com3: 1e-37,
            photo_events_com3: [1e-22, 1e-23, 1e-28, 1e-25],
            angular_p2_energy: 1e-12,
        }
    }
}
impl LocalTolerances {
    pub fn validate(&self) -> Result<(), NetworkError> {
        if !self.rtol.is_finite() || self.rtol < 0. {
            return Err(NetworkError::InvalidInput);
        }
        let a = self
            .nuclei_m3
            .iter()
            .copied()
            .chain(self.photo_events_com3)
            .chain([
                self.gas_energy_j_m3,
                self.photon_number_com3,
                self.photon_energy_j_com3,
                self.angular_p2_energy,
            ]);
        if a.into_iter().any(|v| !v.is_finite() || v <= 0.) {
            return Err(NetworkError::InvalidInput);
        }
        Ok(())
    }
}
pub fn scaled_defect(coarse: f64, fine: f64, atol: f64, rtol: f64) -> Result<f64, NetworkError> {
    if [coarse, fine, atol, rtol].iter().any(|v| !v.is_finite()) || atol <= 0. || rtol < 0. {
        return Err(NetworkError::InvalidInput);
    }
    let scale = atol + rtol * coarse.abs().max(fine.abs());
    let d = (coarse - fine).abs();
    if !scale.is_finite() || !d.is_finite() {
        return Err(NetworkError::NonFinite);
    }
    // No /3: observed global order is not uniform across channels.
    Ok(d / scale)
}
#[derive(Clone, Debug)]
pub struct Defect {
    pub label: String,
    pub coarse: f64,
    pub fine: f64,
    pub absolute: f64,
    pub ratio: f64,
}
#[derive(Clone, Debug, Default)]
pub struct ErrorReport {
    pub components: Vec<Defect>,
    pub maximum: f64,
    pub worst: String,
}
impl ErrorReport {
    fn add(
        &mut self,
        label: impl Into<String>,
        coarse: f64,
        fine: f64,
        atol: f64,
        rtol: f64,
    ) -> Result<(), NetworkError> {
        let ratio = scaled_defect(coarse, fine, atol, rtol)?;
        let label = label.into();
        if ratio > self.maximum {
            self.maximum = ratio;
            self.worst = label.clone();
        }
        self.components.push(Defect {
            label,
            coarse,
            fine,
            absolute: (coarse - fine).abs(),
            ratio,
        });
        Ok(())
    }
}
#[derive(Clone, Debug)]
pub struct PhotonProjection {
    pub count: f64,
    pub energy_j: f64,
    pub q2_energy: f64,
    /// Birth-time resolution differs across coarse/fine. Compare conserved
    /// source spectral/angular labels, NOT zip-by-index newborn records.
    pub groups: BTreeMap<(usize, usize), f64>,
}
pub fn photon_projection(
    b: &MidpointBridge,
    s: &AgeHistory,
) -> Result<PhotonProjection, NetworkError> {
    let g =
        b.0.geometry
            .snapshot(s.time_s)
            .map_err(|_| NetworkError::InputOutsideDomain)?;
    let mut p = PhotonProjection {
        count: 0.,
        energy_j: 0.,
        q2_energy: 0.,
        groups: BTreeMap::new(),
    };
    let mut q2 = 0.;
    for c in &s.cohorts {
        let ray = c.ray_at(&g)?;
        let e = c.n_comoving_m3 * ray.energy_ev * EV_J;
        p.count += c.n_comoving_m3;
        p.energy_j += e;
        q2 += e * (3. * ray.direction[2].powi(2) - 1.) / 2.;
        *p.groups
            .entry((c.spectral_index, c.angular_index))
            .or_default() += c.n_comoving_m3;
    }
    p.q2_energy = if p.energy_j > 0. { q2 / p.energy_j } else { 0. };
    if [p.count, p.energy_j, p.q2_energy]
        .iter()
        .any(|v| !v.is_finite())
    {
        return Err(NetworkError::NonFinite);
    }
    Ok(p)
}
pub fn events_comoving(
    b: &MidpointBridge,
    step: &AgeStep,
    t0: f64,
) -> Result<[f64; 4], NetworkError> {
    let g =
        b.0.geometry
            .snapshot(t0 + 0.5 * (step.state.time_s - t0))
            .map_err(|_| NetworkError::InputOutsideDomain)?;
    let volume = g
        .volume_factor()
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    Ok(step.chemistry_budget.photo_events_m3.map(|v| v * volume))
}
fn compare(
    b: &MidpointBridge,
    a: &AgeStep,
    z: &AgeStep,
    ae: [f64; 4],
    ze: [f64; 4],
    tol: &LocalTolerances,
) -> Result<ErrorReport, NetworkError> {
    let mut report = ErrorReport::default();
    for sp in S::ALL {
        report.add(
            format!("nucleus_{}", sp as usize),
            a.state.full.gas.nuclei.density_m3(sp),
            z.state.full.gas.nuclei.density_m3(sp),
            tol.nuclei_m3[sp as usize],
            tol.rtol,
        )?;
    }
    for (label, x, y) in [
        (
            "thermal",
            a.state.full.gas.thermal_j_m3,
            z.state.full.gas.thermal_j_m3,
        ),
        (
            "escape",
            a.state.full.escaped_j_m3,
            z.state.full.escaped_j_m3,
        ),
        (
            "cmb",
            a.state.full.cmb_reservoir_j_m3,
            z.state.full.cmb_reservoir_j_m3,
        ),
    ] {
        report.add(label, x, y, tol.gas_energy_j_m3, tol.rtol)?;
    }
    let pa = photon_projection(b, &a.state)?;
    let pz = photon_projection(b, &z.state)?;
    report.add(
        "photons",
        pa.count,
        pz.count,
        tol.photon_number_com3,
        tol.rtol,
    )?;
    report.add(
        "photon_energy",
        pa.energy_j,
        pz.energy_j,
        tol.photon_energy_j_com3,
        tol.rtol,
    )?;
    report.add(
        "energy_P2",
        pa.q2_energy,
        pz.q2_energy,
        tol.angular_p2_energy,
        tol.rtol,
    )?;
    report.add(
        "source_count",
        a.state.source_injected_count_com3,
        z.state.source_injected_count_com3,
        tol.photon_number_com3,
        tol.rtol,
    )?;
    report.add(
        "source_energy",
        a.state.source_injected_energy_j_com3,
        z.state.source_injected_energy_j_com3,
        tol.photon_energy_j_com3,
        tol.rtol,
    )?;
    for j in 0..4 {
        report.add(
            format!("photo_event_{j}"),
            ae[j],
            ze[j],
            tol.photo_events_com3[j],
            tol.rtol,
        )?;
    }
    // Stable union: a completely missing/zero source label is not ignored.
    let mut keys = BTreeMap::new();
    for k in pa.groups.keys().chain(pz.groups.keys()) {
        keys.insert(*k, ());
    }
    for k in keys.keys() {
        report.add(
            format!("photon_group_{}_{}", k.0, k.1),
            *pa.groups.get(k).unwrap_or(&0.),
            *pz.groups.get(k).unwrap_or(&0.),
            tol.photon_number_com3,
            tol.rtol,
        )?;
    }
    Ok(report)
}
#[derive(Clone, Debug)]
pub struct AcceptedStep {
    pub state: AgeHistory,
    pub photo_events_com3: [f64; 4],
    pub report: ErrorReport,
    pub attempted_h_s: f64,
    pub next_h_s: f64,
    pub max_energy_ledger: f64,
}
#[derive(Clone, Debug)]
pub enum Trial {
    Accepted(Box<AcceptedStep>),
    Rejected {
        report: Option<ErrorReport>,
        reason: Option<NetworkError>,
        next_h_s: f64,
    },
}
pub fn next_step(h: f64, error: f64, accepted: bool) -> f64 {
    let f = if error == 0. {
        2.
    } else {
        (0.8 * error.powf(-1. / 3.)).clamp(0.2, 2.)
    };
    h * if accepted { f } else { f.min(0.5) }
}
fn recoverable(e: NetworkError) -> bool {
    matches!(
        e,
        NetworkError::NegativePopulation
            | NetworkError::NegativeEnergy
            | NetworkError::TemperatureOutsideSource
    )
}
/// Exactly one attempt; no recursive retries, hidden tolerance changes or input mutation.
pub fn attempt(
    b: &MidpointBridge,
    initial: &AgeHistory,
    c: &NetworkConfig,
    h: f64,
    tol: &LocalTolerances,
) -> Result<Trial, NetworkError> {
    tol.validate()?;
    if b.3 != Centering::JointCxSplit || !h.is_finite() || h <= 0. {
        return Err(NetworkError::InvalidInput);
    }
    let mid = initial.time_s + 0.5 * h;
    let end = initial.time_s + h;
    if !mid.is_finite() || !end.is_finite() || mid <= initial.time_s || end <= mid {
        return Err(NetworkError::NoForwardProgress);
    }
    type ComparedPaths = (AgeStep, AgeStep, [f64; 4], [f64; 4], f64);
    let calculate = || -> Result<ComparedPaths, NetworkError> {
        let a = b.advance(initial, c, h)?;
        let f = b.advance(initial, c, h / 2.)?;
        let z = b.advance(&f.state, c, end - f.state.time_s)?;
        let ae = events_comoving(b, &a, initial.time_s)?;
        let f1 = events_comoving(b, &f, initial.time_s)?;
        let f2 = events_comoving(b, &z, f.state.time_s)?;
        let ze = std::array::from_fn(|j| f1[j] + f2[j]);
        let ledger = f
            .global_energy_relative_error
            .max(z.global_energy_relative_error);
        Ok((a, z, ae, ze, ledger))
    };
    let (a, z, ae, ze, ledger) = match calculate() {
        Ok(v) => v,
        Err(e) if recoverable(e) => {
            return Ok(Trial::Rejected {
                report: None,
                reason: Some(e),
                next_h_s: h / 2.,
            });
        }
        Err(e) => return Err(e), // provenance, ownership, ledger and inner work errors are fatal
    };
    let report = compare(b, &a, &z, ae, ze, tol)?;
    let accept = report.maximum <= 1.;
    let next = next_step(h, report.maximum, accept);
    if accept {
        Ok(Trial::Accepted(Box::new(AcceptedStep {
            state: z.state,
            photo_events_com3: ze,
            report,
            attempted_h_s: h,
            next_h_s: next,
            max_energy_ledger: ledger,
        })))
    } else {
        Ok(Trial::Rejected {
            report: Some(report),
            reason: None,
            next_h_s: next,
        })
    }
}
