//! Transactional H/D CX-only finite-time step with frozen PR150 source modules.
//! He and the other 13-state nuclei are *passive* density/charge/heat-capacity
//! contributors. Other reactions/photo/CMB/FF may be evaluated independently,
//! but are never time-integrated by this component.
use crate::deuterium_atomic::{DAtomicError, DAtomicProvider, DPhotoInput};
use crate::deuterium_charge_exchange::Savin2002;
use crate::deuterium_thermal_coupling::{CxOwnership, OwnedAtomicContribution, ThermalCxComponent};
use crate::isotope_state::IsotopeSpecies;
use crate::mixture_eos::{CxOwner, MixtureCxReference, MixtureError, MixtureState};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CoupleError {
    OwnershipConflict,
    InvalidTimeOrControls,
    InvalidComposition,
    ProviderBoundary,
    NoPhysicalRoot,
    LocalAccuracyLimit,
    WorkLimit,
    Arithmetic,
    Reference(MixtureError),
}

#[derive(Clone, Copy, Debug)]
pub struct StepControls {
    pub atol_normalized: f64,
    pub rtol: f64,
    pub max_attempts: usize,
    pub max_rate_calls: usize,
}
impl Default for StepControls {
    fn default() -> Self {
        Self {
            atol_normalized: 1e-11,
            rtol: 1e-8,
            max_attempts: 2000,
            max_rate_calls: 250_000,
        }
    }
}

#[derive(Clone, Copy, Debug, Default)]
pub struct StepCounts {
    pub accepted_steps: usize,
    pub rejected_steps: usize,
    pub attempts: usize,
    pub rate_calls: usize,
}

#[derive(Clone, Copy, Debug)]
pub struct CoupledStep {
    pub original: MixtureState,
    pub final_state: MixtureState,
    pub owner: CxOwnership,
    pub requested_s: f64,
    pub accepted_s: f64,
    pub extent_m3: f64,
    pub delta_chemical_j_m3: f64,
    pub delta_thermal_j_m3: f64,
    pub delta_electron_m3: f64,
    pub delta_baryons_m3: f64,
    pub photon_j_m3: f64,
    pub escaped_j_m3: f64,
    pub cmb_j_m3: f64,
    pub freefree_j_m3: f64,
    pub counts: StepCounts,
    pub defect_source: &'static str,
    pub rate_source: &'static str,
}

/// A single immutable owner, bound to the *real* original DAtomicProvider.
/// AtomicRhs: native owner handles CX instantaneous terms, thermal step denied.
/// ThermalSubstep: native non-CX instantaneous terms, new CX step owns extent.
#[derive(Clone, Copy, Debug)]
pub struct MixtureCxComponent {
    provider: DAtomicProvider,
    owner: CxOwnership,
}
impl MixtureCxComponent {
    pub fn new(provider: DAtomicProvider, owner: CxOwnership) -> Self {
        Self { provider, owner }
    }
    pub fn owner(&self) -> CxOwnership {
        self.owner
    }
    pub fn provider(&self) -> DAtomicProvider {
        self.provider
    }
    pub fn atomic_rhs(
        &self,
        state: &MixtureState,
        photo: &DPhotoInput,
    ) -> Result<OwnedAtomicContribution, DAtomicError> {
        let t = state
            .eos()
            .map_err(|_| DAtomicError::Arithmetic)?
            .temperature_k;
        ThermalCxComponent::new(self.provider, self.owner).rhs(&state.nuclei, t, photo)
    }
    /// Implemented source-off / CX-only temperature-dependent evolution.
    /// Rejected steps return Err without mutating the by-value initial state.
    /// Neither atomic RHS nor H/He or ionizing photon fields are stepped here.
    pub fn advance_cx_only(
        &self,
        initial: MixtureState,
        duration_s: f64,
        controls: StepControls,
    ) -> Result<CoupledStep, CoupleError> {
        if self.owner != CxOwnership::ThermalSubstep {
            return Err(CoupleError::OwnershipConflict);
        }
        if !duration_s.is_finite()
            || duration_s < 0.0
            || !controls.atol_normalized.is_finite()
            || controls.atol_normalized <= 0.0
            || !controls.rtol.is_finite()
            || controls.rtol < 0.0
            || controls.max_attempts == 0
            || controls.max_rate_calls == 0
        {
            return Err(CoupleError::InvalidTimeOrControls);
        }
        let reference = MixtureCxReference {
            defect: self.provider.defect(),
            owner: CxOwner::ThermalSubstep,
            rate_source: Savin2002::SOURCE,
        };
        let initial_eos = initial.eos().map_err(CoupleError::Reference)?;
        if !(Savin2002::MINIMUM_K..=Savin2002::MAXIMUM_K).contains(&initial_eos.temperature_k) {
            return Err(CoupleError::ProviderBoundary);
        }
        let [physical_lo, physical_hi] = reference
            .signed_extent_bounds(initial)
            .map_err(CoupleError::Reference)?;
        let scale = [
            IsotopeSpecies::H1Neutral,
            IsotopeSpecies::H1Ionized,
            IsotopeSpecies::DNeutral,
            IsotopeSpecies::DIonized,
        ]
        .into_iter()
        .map(|sp| initial.nuclei.density_m3(sp))
        .fold(0.0_f64, f64::max);
        if !scale.is_finite() {
            return Err(CoupleError::Arithmetic);
        }
        let mut counts = StepCounts::default();
        let mut z = 0.0;
        if scale > 0.0 && duration_s > 0.0 {
            let energy_per_extent = self.provider.defect().delta_chi_j * scale;
            let cv = initial_eos.heat_capacity_j_m3_k;
            let mut a = physical_lo / scale;
            let mut b = physical_hi / scale;
            // Restrict mathematical solve to the exact *declared* provider domain;
            // do not clamp a chemical state or extrapolate Savin coefficients.
            if energy_per_extent != 0.0 {
                let xlo = (initial.thermal_j_m3 - cv * Savin2002::MINIMUM_K) / energy_per_extent;
                let xhi = (initial.thermal_j_m3 - cv * Savin2002::MAXIMUM_K) / energy_per_extent;
                a = a.max(xlo.min(xhi));
                b = b.min(xlo.max(xhi));
            }
            if !a.is_finite() || !b.is_finite() || a > 0.0 || b < 0.0 {
                return Err(CoupleError::InvalidComposition);
            }
            let stage = StageSpec {
                initial,
                reference,
                scale,
                bounds: [a, b],
                max_rate_calls: controls.max_rate_calls,
            };
            let mut t = 0.0;
            let mut h = duration_s / 16.0;
            while t < duration_s {
                if counts.attempts >= controls.max_attempts {
                    return Err(CoupleError::WorkLimit);
                }
                h = h.min(duration_s - t);
                if t + h <= t || h <= 0.0 || !h.is_finite() {
                    return Err(CoupleError::LocalAccuracyLimit);
                }
                counts.attempts += 1;
                let coarse = heun_stage(&stage, z, h, &mut counts);
                let fine = (|| {
                    let halfway = heun_stage(&stage, z, h / 2.0, &mut counts)?;
                    heun_stage(&stage, halfway, h / 2.0, &mut counts)
                })();
                match (coarse, fine) {
                    (Ok(zcoarse), Ok(zfine)) => {
                        let err = (zcoarse - zfine).abs() / 3.0;
                        let tolerance =
                            controls.atol_normalized + controls.rtol * zfine.abs().max(z.abs());
                        if !err.is_finite() || !tolerance.is_finite() {
                            return Err(CoupleError::Arithmetic);
                        }
                        let factor = if err == 0.0 {
                            2.0
                        } else {
                            (0.85 * (tolerance / err).powf(1.0 / 3.0)).clamp(0.2, 2.0)
                        };
                        if err <= tolerance {
                            z = zfine;
                            t += h;
                            counts.accepted_steps += 1;
                            h *= factor;
                        } else {
                            counts.rejected_steps += 1;
                            h *= factor.min(0.75);
                        }
                    }
                    (Err(CoupleError::ProviderBoundary | CoupleError::NoPhysicalRoot), _)
                    | (_, Err(CoupleError::ProviderBoundary | CoupleError::NoPhysicalRoot)) => {
                        counts.rejected_steps += 1;
                        h *= 0.5;
                    }
                    (Err(e), _) | (_, Err(e)) => return Err(e),
                }
            }
        }
        let event = reference
            .apply_extent(initial, scale * z)
            .map_err(CoupleError::Reference)?;
        Ok(CoupledStep {
            original: initial,
            final_state: event.state_after,
            owner: self.owner,
            requested_s: duration_s,
            accepted_s: duration_s,
            extent_m3: event.signed_extent_m3,
            delta_chemical_j_m3: event.chemical_delta_j_m3,
            delta_thermal_j_m3: event.thermal_delta_j_m3,
            delta_electron_m3: event.free_electron_delta_m3,
            delta_baryons_m3: event.baryon_delta_m3,
            photon_j_m3: 0.0,
            escaped_j_m3: 0.0,
            cmb_j_m3: 0.0,
            freefree_j_m3: 0.0,
            counts,
            defect_source: self.provider.defect().source,
            rate_source: Savin2002::SOURCE,
        })
    }
}

fn field(
    initial: MixtureState,
    reference: MixtureCxReference<'_>,
    scale: f64,
    z: f64,
    counts: &mut StepCounts,
    max_rate_calls: usize,
) -> Result<f64, CoupleError> {
    if counts.rate_calls >= max_rate_calls {
        return Err(CoupleError::WorkLimit);
    }
    counts.rate_calls += 1;
    let candidate = reference
        .apply_extent(initial, scale * z)
        .map_err(|e| match e {
            MixtureError::UnsupportedTemperature => CoupleError::ProviderBoundary,
            MixtureError::ExtentOutsideDomain => CoupleError::NoPhysicalRoot,
            other => CoupleError::Reference(other),
        })?;
    reference
        .savin_rhs(candidate.state_after)
        .map(|rhs| rhs.extent_rate_m3_s / scale)
        .map_err(|e| match e {
            MixtureError::UnsupportedTemperature => CoupleError::ProviderBoundary,
            other => CoupleError::Reference(other),
        })
}

struct StageSpec<'a> {
    initial: MixtureState,
    reference: MixtureCxReference<'a>,
    scale: f64,
    bounds: [f64; 2],
    max_rate_calls: usize,
}

/// Full/half Heun construction reuses the original owner integration order.
/// Every Euler and Heun stage is validated before it can affect an endpoint.
fn heun_stage(
    stage: &StageSpec<'_>,
    z0: f64,
    dt: f64,
    counts: &mut StepCounts,
) -> Result<f64, CoupleError> {
    let g0 = field(
        stage.initial,
        stage.reference,
        stage.scale,
        z0,
        counts,
        stage.max_rate_calls,
    )?;
    let euler = z0 + dt * g0;
    if !euler.is_finite() || euler < stage.bounds[0] || euler > stage.bounds[1] {
        return Err(CoupleError::NoPhysicalRoot);
    }
    let g1 = field(
        stage.initial,
        stage.reference,
        stage.scale,
        euler,
        counts,
        stage.max_rate_calls,
    )?;
    let second_euler = euler + dt * g1;
    if !second_euler.is_finite() || second_euler < stage.bounds[0] || second_euler > stage.bounds[1]
    {
        return Err(CoupleError::NoPhysicalRoot);
    }
    field(
        stage.initial,
        stage.reference,
        stage.scale,
        second_euler,
        counts,
        stage.max_rate_calls,
    )?;
    let endpoint = (z0 + second_euler) / 2.0;
    if !endpoint.is_finite() || endpoint < stage.bounds[0] || endpoint > stage.bounds[1] {
        return Err(CoupleError::NoPhysicalRoot);
    }
    field(
        stage.initial,
        stage.reference,
        stage.scale,
        endpoint,
        counts,
        stage.max_rate_calls,
    )?;
    Ok(endpoint)
}
