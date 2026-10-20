//! Narrow non-CX D collision adapter from the source-locked DAtomicRhs.
//! Only rate-bundle acquisition and unused output construction are removed.
//! Zero-photo input is constructed by this provider at the sole call site, so
//! threshold identity is established by construction; no public photo API is added.
use parent::HHeModel;
use parent::deuterium_atomic::{
    DAtomicError, DAtomicProvider, DAtomicRates, DEnergyLedger, DPhotoInput, GRACKLE_COMMIT,
    MODEL_ID,
};
use parent::igm_rates::IgmRates;
use parent::{IsotopeNumberState, IsotopeSpecies};

pub(crate) struct CollisionRhs {
    pub(crate) d_net: f64,
    pub(crate) ci_events_m3_s: f64,
    pub(crate) rr_events_m3_s: f64,
    pub(crate) energy: DEnergyLedger,
}

fn nonnegative(value: f64) -> Result<f64, DAtomicError> {
    if !value.is_finite() {
        Err(DAtomicError::NonFiniteInput)
    } else if value < 0.0 {
        Err(DAtomicError::InvalidInput)
    } else {
        Ok(value)
    }
}

fn arithmetic(value: f64) -> Result<f64, DAtomicError> {
    if value.is_finite() {
        Ok(value)
    } else {
        Err(DAtomicError::Arithmetic)
    }
}

fn product(factors: &[f64]) -> Result<f64, DAtomicError> {
    for &factor in factors {
        nonnegative(factor)?;
    }
    if factors.contains(&0.0) {
        return Ok(0.0);
    }
    let mut value = 1.0;
    for &factor in factors {
        value = arithmetic(value * factor)?;
        if value == 0.0 {
            return Err(DAtomicError::Arithmetic);
        }
    }
    Ok(value)
}

fn ev_j() -> f64 {
    HHeModel::controlled_fixture().ev_erg * 1e-7
}

pub(crate) fn collision_rhs(
    provider: DAtomicProvider,
    state: &IsotopeNumberState,
    temperature_k: f64,
    photo: &DPhotoInput,
    h: &IgmRates,
) -> Result<CollisionRhs, DAtomicError> {
    if !temperature_k.is_finite() {
        return Err(DAtomicError::NonFiniteInput);
    }
    if !(1.0..=1e6).contains(&temperature_k) {
        return Err(DAtomicError::TemperatureDomain);
    }
    if photo.gamma_s() != 0.0 || photo.heat_j_per_absorber_s() != 0.0 {
        return Err(DAtomicError::InvalidInput);
    }
    let rates = DAtomicRates {
        temperature_k,
        ci_m3_s: h.ci_cm3_s[0] * 1e-6,
        rr_case_a_m3_s: h.rr_cm3_s[0] * 1e-6,
        rr_kinetic_j_m3_s: h.rr_cooling_erg_cm3_s[0] * 1e-13,
        ce_j_m3_s: h.ce_erg[0] * 1e-13,
        ci_floor_m3_s: h.diagnostics.ci_floor_cm3_s[0] * 1e-6,
        ce_cap_j_m3_s: h.diagnostics.ce_cap_erg[0] * 1e-13,
        model_id: MODEL_ID,
        source_commit: GRACKLE_COMMIT,
    };
    let moments = state.moments().map_err(|_| DAtomicError::Arithmetic)?;
    let ne = moments.neutral_free_electron_density_m3;
    let n = |species| state.density_m3(species);
    use IsotopeSpecies::{DIonized, DNeutral};
    let (d0, dp) = (n(DNeutral), n(DIonized));
    let pi = product(&[d0, photo.gamma_s()])?;
    let ci = product(&[ne, d0, rates.ci_m3_s])?;
    let rr = product(&[ne, dp, rates.rr_case_a_m3_s])?;
    let (cxf, cxr) = (0.0, 0.0);
    let chi = provider.chi_d_ev() * ev_j();
    let pi_heat = product(&[d0, photo.heat_j_per_absorber_s()])?;
    let pi_chemical = product(&[chi, pi])?;
    let ci_chemical = product(&[chi, ci])?;
    let rr_chemical_loss = product(&[chi, rr])?;
    let rr_kinetic = product(&[ne, dp, rates.rr_kinetic_j_m3_s])?;
    let ce = product(&[ne, d0, rates.ce_j_m3_s])?;
    let cxf_defect = product(&[provider.defect().delta_chi_j, cxf])?;
    let cxr_defect = product(&[provider.defect().delta_chi_j, cxr])?;
    let channel_energy = [
        DEnergyLedger {
            thermal: pi_heat,
            chemical: pi_chemical,
            escape: 0.0,
            photon_input: product(&[d0, photo.energy_j_per_absorber_s()])?,
        },
        DEnergyLedger {
            thermal: -ci_chemical,
            chemical: ci_chemical,
            ..DEnergyLedger::default()
        },
        DEnergyLedger {
            thermal: -rr_kinetic,
            chemical: -rr_chemical_loss,
            escape: arithmetic(rr_kinetic + rr_chemical_loss)?,
            photon_input: 0.0,
        },
        DEnergyLedger {
            thermal: -ce,
            escape: ce,
            ..DEnergyLedger::default()
        },
        DEnergyLedger {
            thermal: -cxf_defect,
            chemical: cxf_defect,
            ..DEnergyLedger::default()
        },
        DEnergyLedger {
            thermal: cxr_defect,
            chemical: -cxr_defect,
            ..DEnergyLedger::default()
        },
    ];
    let mut energy = DEnergyLedger::default();
    for row in channel_energy {
        energy.thermal = arithmetic(energy.thermal + row.thermal)?;
        energy.chemical = arithmetic(energy.chemical + row.chemical)?;
        energy.escape = arithmetic(energy.escape + row.escape)?;
        energy.photon_input = arithmetic(energy.photon_input + row.photon_input)?;
    }
    let atomic_net = arithmetic(pi + ci - rr)?;
    let cx_net = arithmetic(cxf - cxr)?;
    let d_net = arithmetic(atomic_net + cx_net)?;
    let particles = arithmetic(moments.heavy_particle_density_m3 + ne)?;
    let _temperature_k_s = if particles == 0.0 {
        0.0
    } else {
        arithmetic(
            2.0 * energy.thermal
                / (3.0 * HHeModel::controlled_fixture().kb_erg_k * 1e-7 * particles)
                - temperature_k * atomic_net / particles,
        )?
    };
    let _ci_floor_events = product(&[ne, d0, rates.ci_floor_m3_s])?;
    let _ce_cap_cooling = product(&[ne, d0, rates.ce_cap_j_m3_s])?;
    Ok(CollisionRhs {
        d_net,
        ci_events_m3_s: ci,
        rr_events_m3_s: rr,
        energy,
    })
}
