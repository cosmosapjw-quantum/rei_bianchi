//! Source-bound fixed-proper-volume mixture EOS + one H/D CX event map.
//! This is NOT an expanding Bianchi chemical integrator, and does not alter
//! original `ThermalCxComponent::UnsupportedSpectator` behavior.
use crate::deuterium_charge_exchange::{DhEnergyDefect, DhError, Savin2002};
use crate::isotope_state::{IsotopeNumberState, IsotopeSpecies};

pub const KB_J_K: f64 = 1.380_649e-23;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum MixtureError {
    InvalidThermal,
    Vacuum,
    InvalidElectronOwner,
    UnsupportedOwner,
    MissingSource,
    RateSourceMismatch,
    InvalidDefect,
    ExtentOutsideDomain,
    NegativeThermal,
    NonFiniteArithmetic,
    UnsupportedTemperature,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CxOwner {
    AtomicRhs,
    ThermalSubstep,
}

#[derive(Clone, Copy, Debug)]
pub struct EosSnapshot {
    pub baryons_m3: f64,
    pub heavy_m3: f64,
    pub free_electrons_m3: f64,
    pub thermal_particles_m3: f64,
    pub heat_capacity_j_m3_k: f64,
    pub temperature_k: f64,
    pub pressure_j_m3: f64,
}

#[derive(Clone, Copy, Debug)]
pub struct MixtureState {
    pub nuclei: IsotopeNumberState,
    pub thermal_j_m3: f64,
}

impl MixtureState {
    pub fn eos(self) -> Result<EosSnapshot, MixtureError> {
        let u = self.thermal_j_m3;
        if !u.is_finite() || u < 0.0 {
            return Err(MixtureError::InvalidThermal);
        }
        let m = self
            .nuclei
            .moments()
            .map_err(|_| MixtureError::NonFiniteArithmetic)?;
        let n = self
            .nuclei
            .thermal_particle_density_all_thermal_m3()
            .map_err(|_| MixtureError::NonFiniteArithmetic)?;
        if !n.is_finite() || n <= 0.0 {
            return Err(MixtureError::Vacuum);
        }
        let c_v = 1.5 * KB_J_K * n;
        let temperature = u / c_v;
        let pressure = (2.0 / 3.0) * u;
        if !c_v.is_finite()
            || c_v <= 0.0
            || !temperature.is_finite()
            || !pressure.is_finite()
            || (u > 0.0 && temperature == 0.0)
        {
            return Err(MixtureError::NonFiniteArithmetic);
        }
        Ok(EosSnapshot {
            baryons_m3: m.baryon_density_m3,
            heavy_m3: m.heavy_particle_density_m3,
            free_electrons_m3: m.neutral_free_electron_density_m3,
            thermal_particles_m3: n,
            heat_capacity_j_m3_k: c_v,
            temperature_k: temperature,
            pressure_j_m3: pressure,
        })
    }
    /// Optional cross-check only: charge-state nuclei own free electrons.
    pub fn validate_reported_electrons(self, reported: f64) -> Result<(), MixtureError> {
        if !reported.is_finite() || reported < 0.0 {
            return Err(MixtureError::InvalidElectronOwner);
        }
        let actual = self.eos()?.free_electrons_m3;
        if actual.to_bits() != reported.to_bits() {
            return Err(MixtureError::InvalidElectronOwner);
        }
        Ok(())
    }
}

/// Rates and chemistry are untouched; only the H/D CX owner has authority to
/// change this state. The supplied `defect` MUST be the bound atomic provider's
/// chi_D - chi_H. No default binding energy is manufactured.
#[derive(Clone, Copy, Debug)]
pub struct MixtureCxReference<'a> {
    pub defect: DhEnergyDefect,
    pub owner: CxOwner,
    pub rate_source: &'a str,
}

#[derive(Clone, Copy, Debug)]
pub struct CxEvent {
    pub before: EosSnapshot,
    pub after: EosSnapshot,
    pub state_after: MixtureState,
    pub signed_extent_m3: f64,
    pub chemical_delta_j_m3: f64,
    pub thermal_delta_j_m3: f64,
    pub free_electron_delta_m3: f64,
    pub baryon_delta_m3: f64,
    pub photon_delta_j_m3: f64,
    pub cmb_delta_j_m3: f64,
    pub freefree_delta_j_m3: f64,
}

#[derive(Clone, Copy, Debug)]
pub struct CxInstantaneous {
    pub extent_rate_m3_s: f64,
    pub chemical_power_j_m3_s: f64,
    pub thermal_power_j_m3_s: f64,
    pub temperature_rate_k_s: f64,
    pub rate_source: &'static str,
    pub conserved_electron_rate_m3_s: f64,
}

impl MixtureCxReference<'_> {
    fn validate(self) -> Result<(), MixtureError> {
        if self.owner != CxOwner::ThermalSubstep {
            return Err(MixtureError::UnsupportedOwner);
        }
        if self.defect.source.is_empty() || self.rate_source.is_empty() {
            return Err(MixtureError::MissingSource);
        }
        if self.rate_source != Savin2002::SOURCE {
            return Err(MixtureError::RateSourceMismatch);
        }
        if !self.defect.delta_chi_j.is_finite() {
            return Err(MixtureError::InvalidDefect);
        }
        Ok(())
    }
    pub fn signed_extent_bounds(self, state: MixtureState) -> Result<[f64; 2], MixtureError> {
        self.validate()?;
        state.eos()?;
        let h0 = state.nuclei.density_m3(IsotopeSpecies::H1Neutral);
        let hp = state.nuclei.density_m3(IsotopeSpecies::H1Ionized);
        let d0 = state.nuclei.density_m3(IsotopeSpecies::DNeutral);
        let dp = state.nuclei.density_m3(IsotopeSpecies::DIonized);
        Ok([-h0.min(dp), hp.min(d0)])
    }
    /// Exactly one signed CX event extent at fixed proper volume [m^-3].
    /// An invalid candidate returns Err and never mutates the original state.
    pub fn apply_extent(self, state: MixtureState, extent: f64) -> Result<CxEvent, MixtureError> {
        let [lo, hi] = self.signed_extent_bounds(state)?;
        if !extent.is_finite() || extent < lo || extent > hi {
            return Err(MixtureError::ExtentOutsideDomain);
        }
        let before = state.eos()?;
        let chemical = self.defect.delta_chi_j * extent;
        let thermal = -chemical;
        let next_u = state.thermal_j_m3 + thermal;
        if !chemical.is_finite() || !next_u.is_finite() {
            return Err(MixtureError::NonFiniteArithmetic);
        }
        if next_u < 0.0 {
            return Err(MixtureError::NegativeThermal);
        }
        let mut data = [0.0; 13];
        for s in IsotopeSpecies::ALL {
            data[s as usize] = state.nuclei.density_m3(s);
        }
        data[IsotopeSpecies::H1Neutral as usize] += extent;
        data[IsotopeSpecies::H1Ionized as usize] -= extent;
        data[IsotopeSpecies::DNeutral as usize] -= extent;
        data[IsotopeSpecies::DIonized as usize] += extent;
        let nuclei =
            IsotopeNumberState::new(data).map_err(|_| MixtureError::NonFiniteArithmetic)?;
        let state_after = MixtureState {
            nuclei,
            thermal_j_m3: next_u,
        };
        let after = state_after.eos()?;
        if extent != 0.0
            && ([before.temperature_k, after.temperature_k]
                .into_iter()
                .any(|t| !(Savin2002::MINIMUM_K..=Savin2002::MAXIMUM_K).contains(&t)))
        {
            return Err(MixtureError::UnsupportedTemperature);
        }
        let free_electron_delta = after.free_electrons_m3 - before.free_electrons_m3;
        let baryon_delta = after.baryons_m3 - before.baryons_m3;
        // The event-level algebraic invariants hold exactly. Floating evaluation
        // may leave sub-ulp roundoff, and must not be silently clipped.
        Ok(CxEvent {
            before,
            after,
            state_after,
            signed_extent_m3: extent,
            chemical_delta_j_m3: chemical,
            thermal_delta_j_m3: thermal,
            free_electron_delta_m3: free_electron_delta,
            baryon_delta_m3: baryon_delta,
            photon_delta_j_m3: 0.0,
            cmb_delta_j_m3: 0.0,
            freefree_delta_j_m3: 0.0,
        })
    }

    /// Instantaneous Savin (2002) CX RHS [m^-3 s^-1], excluding every other
    /// chemical, photon, ff or CMB channel. Not a time-integrator.
    pub fn savin_rhs(self, state: MixtureState) -> Result<CxInstantaneous, MixtureError> {
        self.validate()?;
        let before = state.eos()?;
        let rates = Savin2002::rates(before.temperature_k).map_err(|e| match e {
            DhError::OutsideTemperatureDomain => MixtureError::UnsupportedTemperature,
            _ => MixtureError::NonFiniteArithmetic,
        })?;
        let n = &state.nuclei;
        let r = rates.forward_m3_s
            * n.density_m3(IsotopeSpecies::H1Ionized)
            * n.density_m3(IsotopeSpecies::DNeutral)
            - rates.reverse_m3_s
                * n.density_m3(IsotopeSpecies::H1Neutral)
                * n.density_m3(IsotopeSpecies::DIonized);
        let power = self.defect.delta_chi_j * r;
        let t_dot = -power / before.heat_capacity_j_m3_k;
        if !r.is_finite() || !power.is_finite() || !t_dot.is_finite() {
            return Err(MixtureError::NonFiniteArithmetic);
        }
        Ok(CxInstantaneous {
            extent_rate_m3_s: r,
            chemical_power_j_m3_s: power,
            thermal_power_j_m3_s: -power,
            temperature_rate_k_s: t_dot,
            rate_source: Savin2002::SOURCE,
            conserved_electron_rate_m3_s: 0.0,
        })
    }
}

/// Homogeneous nonrelativistic ideal-gas temperature equation for a comoving
/// common-temperature gas, with Theta = expansion scalar [s^-1].
/// `external_thermal_j_m3_s` excludes CX energy (already owned here).
/// `other_particle_creation_m3_s` is the chemistry-induced change in n_th,
/// not the dilution -Theta*n_th. Both channels are caller-owned inputs.
pub fn temperature_derivative(
    eos: &EosSnapshot,
    expansion_theta_s: f64,
    external_thermal_j_m3_s: f64,
    other_particle_creation_m3_s: f64,
    cx_extent_rate_m3_s: f64,
    defect_j_per_event: f64,
) -> Result<f64, MixtureError> {
    if [
        expansion_theta_s,
        external_thermal_j_m3_s,
        other_particle_creation_m3_s,
        cx_extent_rate_m3_s,
        defect_j_per_event,
    ]
    .iter()
    .any(|x| !x.is_finite())
    {
        return Err(MixtureError::NonFiniteArithmetic);
    }
    let thermal_source = external_thermal_j_m3_s - defect_j_per_event * cx_extent_rate_m3_s;
    let t_dot = -(2.0 / 3.0) * expansion_theta_s * eos.temperature_k
        + thermal_source / eos.heat_capacity_j_m3_k
        - eos.temperature_k * other_particle_creation_m3_s / eos.thermal_particles_m3;
    if !t_dot.is_finite() {
        return Err(MixtureError::NonFiniteArithmetic);
    }
    Ok(t_dot)
}
