//! Source-locked H/He/D finite-volume finite-time, opt-in scientific reference.
//! Source photons are finite *prescribed initial bins*; no cosmic emission history.
//! Uses PR150 Grackle 3.4.1, Verner and DAtomicProvider, one n_e and Cv.
//! Collisional update and photon competition are first order in the joint time
//! splitting. Every attempted step is transactional and fail-closed.
use crate::HHeModel;
use crate::atomic_provider::{Absorber, AtomicProvider};
use crate::deuterium_atomic::{DAtomicProvider, DChargeExchange, d_atomic_rhs};
use crate::deuterium_charge_exchange::Savin2002;
use crate::deuterium_thermal_coupling::CxOwnership;
use crate::igm_rates::igm_rates;
use crate::isotope_state::{IsotopeNumberState, IsotopeSpecies as S};
use crate::mixture_coupling::{CoupleError, MixtureCxComponent, StepControls};
use crate::mixture_eos::{MixtureError, MixtureState};

pub const EV_J: f64 = 1.602_176_634e-19;
pub const SPEED_OF_LIGHT_M_S: f64 = 299_792_458.0;
pub const MAX_PHOTON_BINS: usize = 64;
const CGS_POWER_TO_SI: f64 = 0.1; // erg cm^-3 s^-1 => J m^-3 s^-1

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct PhotonBin {
    pub energy_ev: f64,
    pub number_m3: f64,
}

#[derive(Clone, Debug)]
pub struct FullState {
    pub gas: MixtureState,
    pub photon_bins: Vec<PhotonBin>,
    pub escaped_j_m3: f64,
    pub cmb_reservoir_j_m3: f64,
    pub elapsed_s: f64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum NetworkError {
    InvalidInput,
    InputOutsideDomain,
    SpeciesOutsideDomain,
    NonFinite,
    NegativePopulation,
    NegativeEnergy,
    TemperatureOutsideSource,
    SourceMismatch,
    OwnershipConflict,
    NoForwardProgress,
    PhysicsLedger,
    Cx(CoupleError),
}
impl From<MixtureError> for NetworkError {
    fn from(e: MixtureError) -> Self {
        if e == MixtureError::UnsupportedTemperature {
            Self::TemperatureOutsideSource
        } else {
            Self::InputOutsideDomain
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct NetworkConfig {
    pub deuterium: DAtomicProvider,
    pub owner: CxOwnership,
    pub photon_source: &'static str,
    pub cmb_temperature_k: f64,
    pub use_photo: bool,
    pub use_collisions: bool,
    pub use_cx: bool,
    pub use_cmb: bool,
    pub cx_controls: StepControls,
}
impl NetworkConfig {
    pub fn source_bound(deuterium: DAtomicProvider, photon_source: &'static str) -> Self {
        Self {
            deuterium,
            owner: CxOwnership::ThermalSubstep,
            photon_source,
            cmb_temperature_k: 20.0,
            use_photo: true,
            use_collisions: true,
            use_cx: true,
            use_cmb: true,
            cx_controls: StepControls::default(),
        }
    }
}

#[derive(Clone, Copy, Debug, Default)]
pub struct EventBudget {
    pub photo_events_m3: [f64; 4], // HI, HeI, HeII, DI
    pub ci_events_m3: [f64; 4],
    pub rr_events_m3: [f64; 4],
    pub dr_hei_m3: f64,
    pub cx_signed_m3: f64,
    pub photo_energy_j_m3: f64,
    pub thermal_change_j_m3: f64,
    pub chemical_change_j_m3: f64,
    pub escape_change_j_m3: f64,
    pub cmb_change_j_m3: f64,
    pub freefree_integrated_j_m3: f64,
    pub d_electron_integrated_m3: f64,
}
impl EventBudget {
    fn add(&mut self, other: Self) {
        for (a, b) in self.photo_events_m3.iter_mut().zip(other.photo_events_m3) {
            *a += b;
        }
        for (a, b) in self.ci_events_m3.iter_mut().zip(other.ci_events_m3) {
            *a += b;
        }
        for (a, b) in self.rr_events_m3.iter_mut().zip(other.rr_events_m3) {
            *a += b;
        }
        self.dr_hei_m3 += other.dr_hei_m3;
        self.cx_signed_m3 += other.cx_signed_m3;
        self.photo_energy_j_m3 += other.photo_energy_j_m3;
        self.thermal_change_j_m3 += other.thermal_change_j_m3;
        self.chemical_change_j_m3 += other.chemical_change_j_m3;
        self.escape_change_j_m3 += other.escape_change_j_m3;
        self.cmb_change_j_m3 += other.cmb_change_j_m3;
        self.d_electron_integrated_m3 += other.d_electron_integrated_m3;
        self.freefree_integrated_j_m3 += other.freefree_integrated_j_m3;
    }
}
#[derive(Clone, Debug)]
pub struct NetworkResult {
    pub state: FullState,
    pub budget: EventBudget,
    pub attempts: usize,
    pub accepted: usize,
    pub rejected: usize,
}

fn all_finite(x: &[f64]) -> bool {
    x.iter().all(|x| x.is_finite())
}
fn nonnegative(v: f64) -> Result<f64, NetworkError> {
    if !v.is_finite() {
        Err(NetworkError::NonFinite)
    } else if v < 0.0 {
        Err(NetworkError::NegativePopulation)
    } else {
        Ok(v)
    }
}
fn atomic_values(state: &MixtureState) -> [f64; 13] {
    let mut a = [0.0; 13];
    for s in S::ALL {
        a[s as usize] = state.nuclei.density_m3(s);
    }
    a
}
fn new_gas(v: [f64; 13], thermal: f64) -> Result<MixtureState, NetworkError> {
    if !thermal.is_finite() {
        return Err(NetworkError::NonFinite);
    }
    if thermal < 0.0 {
        return Err(NetworkError::NegativeEnergy);
    }
    let nuclei = IsotopeNumberState::new(v).map_err(|_| NetworkError::NegativePopulation)?;
    let gas = MixtureState {
        nuclei,
        thermal_j_m3: thermal,
    };
    gas.eos()?;
    Ok(gas)
}
impl FullState {
    pub fn validate(&self, config: &NetworkConfig) -> Result<(), NetworkError> {
        if config.photon_source.is_empty() || config.deuterium.threshold_source().is_empty() {
            return Err(NetworkError::SourceMismatch);
        }
        if !self.elapsed_s.is_finite()
            || self.elapsed_s < 0.0
            || !self.escaped_j_m3.is_finite()
            || self.escaped_j_m3 < 0.0
            || !self.cmb_reservoir_j_m3.is_finite()
            || !config.cmb_temperature_k.is_finite()
            || config.cmb_temperature_k <= 0.0
        {
            return Err(NetworkError::InvalidInput);
        }
        let t = self.gas.eos()?.temperature_k;
        if !(Savin2002::MINIMUM_K..=Savin2002::MAXIMUM_K).contains(&t) {
            return Err(NetworkError::TemperatureOutsideSource);
        }
        if self.photon_bins.len() > MAX_PHOTON_BINS {
            return Err(NetworkError::InputOutsideDomain);
        }
        for b in &self.photon_bins {
            if !b.energy_ev.is_finite()
                || b.energy_ev <= 0.0
                || b.energy_ev > 50_000.0
                || !b.number_m3.is_finite()
                || b.number_m3 < 0.0
            {
                return Err(NetworkError::InputOutsideDomain);
            }
        }
        Ok(())
    }
    pub fn photon_number(&self) -> f64 {
        self.photon_bins.iter().map(|p| p.number_m3).sum()
    }
    pub fn binding_j_m3(&self, config: &NetworkConfig) -> f64 {
        let h = HHeModel::controlled_fixture().threshold_ev;
        let n = &self.gas.nuclei;
        EV_J * (h[0] * n.density_m3(S::H1Ionized)
            + h[1] * n.density_m3(S::He4SinglyIonized)
            + (h[1] + h[2]) * n.density_m3(S::He4DoublyIonized)
            + config.deuterium.chi_d_ev() * n.density_m3(S::DIonized))
    }
    /// Invariant for dynamic H1, He4, D. Other 13-state spectator charge-state
    /// chemical reservoirs are constant and therefore omitted from this baseline.
    pub fn energy_j_m3(&self, config: &NetworkConfig) -> f64 {
        self.gas.thermal_j_m3
            + self.binding_j_m3(config)
            + self
                .photon_bins
                .iter()
                .map(|p| p.number_m3 * p.energy_ev * EV_J)
                .sum::<f64>()
            + self.escaped_j_m3
            + self.cmb_reservoir_j_m3
    }
}
fn chemistry_deltas(a: &mut [f64; 13], channel: usize, value: f64) {
    match channel {
        0 => {
            a[S::H1Neutral as usize] -= value;
            a[S::H1Ionized as usize] += value;
        }
        1 => {
            a[S::He4Neutral as usize] -= value;
            a[S::He4SinglyIonized as usize] += value;
        }
        2 => {
            a[S::He4SinglyIonized as usize] -= value;
            a[S::He4DoublyIonized as usize] += value;
        }
        3 => {
            a[S::DNeutral as usize] -= value;
            a[S::DIonized as usize] += value;
        }
        _ => unreachable!(),
    }
}
fn photo_step(s: &mut FullState, c: &NetworkConfig, dt: f64) -> Result<EventBudget, NetworkError> {
    photo_step_births(s, c, dt, None)
}
fn photo_step_births(
    s: &mut FullState,
    c: &NetworkConfig,
    dt: f64,
    births: Option<(&[f64], &[PhotonBin])>,
) -> Result<EventBudget, NetworkError> {
    if !c.use_photo {
        return Ok(EventBudget::default());
    }
    let initial = s.gas.eos()?;
    let a = atomic_values(&s.gas);
    let absorber = [
        a[S::H1Neutral as usize],
        a[S::He4Neutral as usize],
        a[S::He4SinglyIonized as usize],
        a[S::DNeutral as usize],
    ];
    let refprovider = AtomicProvider::reference();
    let binding = HHeModel::controlled_fixture().threshold_ev;
    let chis = [binding[0], binding[1], binding[2], c.deuterium.chi_d_ev()];
    let mut delta = [0.0; 4];
    let mut d_heat = 0.0;
    let mut photons = s.photon_bins.clone();
    let mut photo_energy = 0.0;
    let mut heat = 0.0;
    for (index, (b, p)) in s.photon_bins.iter().zip(photons.iter_mut()).enumerate() {
        let mut opac = [0.0; 4];
        for j in 0..4 {
            let sigma = if j == 3 {
                c.deuterium
                    .cross_section_m2(b.energy_ev)
                    .map_err(|_| NetworkError::InputOutsideDomain)?
            } else if b.energy_ev < chis[j] {
                0.0
            } else {
                refprovider
                    .cross_section(
                        [Absorber::HI, Absorber::HeI, Absorber::HeII][j],
                        b.energy_ev,
                    )
                    .map_err(|_| NetworkError::InputOutsideDomain)?
                    * 1e-4
            };
            opac[j] = sigma * absorber[j];
        }
        let lambda = opac.iter().sum::<f64>() * SPEED_OF_LIGHT_M_S;
        if !lambda.is_finite() || lambda < 0.0 {
            return Err(NetworkError::NonFinite);
        }
        if lambda == 0.0 || b.number_m3 == 0.0 {
            continue;
        }
        let partition = if let Some((born, old)) = births {
            Some(crate::birth_clock::uniform_partition(
                old[index].number_m3,
                born[index],
                lambda * dt,
            )?)
        } else {
            None
        };
        let absorbed =
            partition.map_or_else(|| b.number_m3 * (-(-lambda * dt).exp_m1()), |v| v.absorbed);
        let mut pieces = [0.0; 4];
        for j in 0..4 {
            pieces[j] = absorbed * (opac[j] * SPEED_OF_LIGHT_M_S / lambda);
            delta[j] += pieces[j];
        }
        let done = pieces.iter().sum::<f64>();
        p.number_m3 = partition.map_or(b.number_m3 - done, |v| v.surviving);
        // A genuinely tiny negative photon residual is a rejected trial, never clipped.
        nonnegative(p.number_m3)?;
        photo_energy += done * b.energy_ev * EV_J;
        heat += pieces
            .iter()
            .zip(chis)
            .map(|(x, chi)| x * (b.energy_ev - chi) * EV_J)
            .sum::<f64>();
        d_heat += pieces[3] * (b.energy_ev - chis[3]) * EV_J;
    }
    // D PI is *derived from the identical shared photon events*, then checked
    // against the immutable DAtomicRhs photo transaction. Never apply it twice.
    if absorber[3] > 0.0 && delta[3] > 0.0 {
        let phot = c
            .deuterium
            .photo_input_from_bound_rates(
                delta[3] / (absorber[3] * dt),
                d_heat / (absorber[3] * dt),
                c.photon_source,
            )
            .map_err(|_| NetworkError::SourceMismatch)?;
        let owner = d_atomic_rhs(
            c.deuterium,
            &s.gas.nuclei,
            initial.temperature_k,
            &phot,
            DChargeExchange::Disabled,
        )
        .map_err(|_| NetworkError::InputOutsideDomain)?;
        let pi = owner.channel_energy[0];
        let compare = |v: f64, w: f64| (v - w).abs() <= 4e-12 * v.abs().max(w.abs()).max(1e-40);
        if !compare(owner.photo_events_m3_s * dt, delta[3])
            || !compare(pi.thermal * dt, d_heat)
            || !compare(pi.chemical * dt, delta[3] * chis[3] * EV_J)
            || !compare(
                pi.photon_input * dt,
                photo_energy_if_d(&delta, chis[3], d_heat),
            )
        {
            return Err(NetworkError::PhysicsLedger);
        }
    }
    let mut values = a;
    for (j, &v) in delta.iter().enumerate() {
        chemistry_deltas(&mut values, j, v);
    }
    let oldchem = s.binding_j_m3(c);
    let newgas = new_gas(values, s.gas.thermal_j_m3 + heat)?;
    let newchem = FullState {
        gas: newgas,
        photon_bins: vec![],
        escaped_j_m3: 0.0,
        cmb_reservoir_j_m3: 0.0,
        elapsed_s: 0.0,
    }
    .binding_j_m3(c);
    // Ownership identity: only the shared finite photon pool drives all PI.
    // Compare reconstructed binding against event chemistry with a floating
    // inventory-scale roundoff bound, not a relative bound on tiny deltas.
    if !all_finite(&[photo_energy, heat, newchem, initial.temperature_k]) {
        return Err(NetworkError::NonFinite);
    }
    let chem_by_events = photo_energy - heat;
    if ((newchem - oldchem) - chem_by_events).abs()
        > 3e-12 * newchem.abs().max(oldchem.abs()).max(1e-40)
    {
        return Err(NetworkError::PhysicsLedger);
    }
    s.gas = newgas;
    s.photon_bins = photons;
    Ok(EventBudget {
        photo_events_m3: delta,
        photo_energy_j_m3: photo_energy,
        thermal_change_j_m3: heat,
        chemical_change_j_m3: photo_energy - heat,
        ..EventBudget::default()
    })
}

fn photo_energy_if_d(delta: &[f64; 4], chi_d: f64, d_heat: f64) -> f64 {
    d_heat + delta[3] * chi_d * EV_J
}
fn coefficient_rates_m3s(ne: f64, absorber: f64, ion: f64, ci: f64, rr: f64) -> (f64, f64) {
    let ne_cm = ne * 1e-6;
    (ne_cm * absorber * ci, ne_cm * ion * rr) // cm^3/s times cm^-3 electron => 1/s; output m^-3 s^-1
}

fn collision_step(
    s: &mut FullState,
    c: &NetworkConfig,
    dt: f64,
) -> Result<EventBudget, NetworkError> {
    if !c.use_collisions && !c.use_cmb {
        return Ok(EventBudget::default());
    }
    let eos = s.gas.eos()?;
    let t = eos.temperature_k;
    let n = atomic_values(&s.gas);
    let ne = eos.free_electrons_m3;
    let mut d_net = 0.0;
    let mut d_ci = 0.0;
    let mut d_rr = 0.0;
    let mut ci = [0.0; 4];
    let mut rr = [0.0; 4];
    let mut dr = 0.0;
    let mut heat = 0.0;
    let mut chem = 0.0;
    let mut esc = 0.0;
    let mut ff = 0.0;
    let kbase = HHeModel::controlled_fixture().threshold_ev;
    let r = igm_rates(t).map_err(|_| NetworkError::TemperatureOutsideSource)?;
    if c.use_collisions {
        // The original D RHS sees the entire mixture n_e; CX disabled here.
        let no_d_photo = c
            .deuterium
            .photo_input_from_bound_rates(0.0, 0.0, c.photon_source)
            .map_err(|_| NetworkError::SourceMismatch)?;
        let d = d_atomic_rhs(
            c.deuterium,
            &s.gas.nuclei,
            t,
            &no_d_photo,
            DChargeExchange::Disabled,
        )
        .map_err(|_| NetworkError::InputOutsideDomain)?;
        d_net = d.species_m3_s[S::DIonized as usize];
        d_ci = d.ci_events_m3_s;
        d_rr = d.rr_events_m3_s;
        let d_ledger = d.energy;
        if d.energy.residual().abs()
            > 1e-13
                * d.energy
                    .thermal
                    .abs()
                    .max(d.energy.chemical.abs())
                    .max(d.energy.escape.abs())
                    .max(1e-30)
        {
            return Err(NetworkError::PhysicsLedger);
        }
        let low = [
            n[S::H1Neutral as usize],
            n[S::He4Neutral as usize],
            n[S::He4SinglyIonized as usize],
        ];
        let high = [
            n[S::H1Ionized as usize],
            n[S::He4SinglyIonized as usize],
            n[S::He4DoublyIonized as usize],
        ];
        for j in 0..3 {
            let (cij, rrj) =
                coefficient_rates_m3s(ne, low[j], high[j], r.ci_cm3_s[j], r.rr_cm3_s[j]);
            ci[j] = cij;
            rr[j] = rrj;
            let chi = kbase[j] * EV_J;
            chem += (cij - rrj) * chi * dt;
            heat -= cij * chi * dt;
            esc += rrj * chi * dt;
            // Kinetic recombination cooling only, not the binding energy again.
            let rr_kin = ne * 1e-6 * high[j] * 1e-6 * r.rr_cooling_erg_cm3_s[j] * CGS_POWER_TO_SI;
            heat -= rr_kin * dt;
            esc += rr_kin * dt;
        }
        // HeII -> HeI dielectronic branch from original Grackle, once.
        dr = coefficient_rates_m3s(ne, 0.0, n[S::He4SinglyIonized as usize], 0.0, r.dr_cm3_s).1;
        let chi1 = kbase[1] * EV_J;
        chem -= dr * chi1 * dt;
        esc += dr * chi1 * dt;
        let dr_kin = ne
            * 1e-6
            * n[S::He4SinglyIonized as usize]
            * 1e-6
            * r.dr_cooling_erg_cm3_s
            * CGS_POWER_TO_SI;
        heat -= dr_kin * dt;
        esc += dr_kin * dt;
        // Three CE channels, original HeI metastable has ne^2*n(HeII).
        let ne_cm = ne * 1e-6;
        let ce0 = ne_cm * (low[0] * 1e-6) * r.ce_erg[0] * CGS_POWER_TO_SI;
        let ce1 = ne_cm.powi(2)
            * (n[S::He4SinglyIonized as usize] * 1e-6)
            * r.ce_erg[1]
            * CGS_POWER_TO_SI;
        let ce2 = ne_cm * (n[S::He4SinglyIonized as usize] * 1e-6) * r.ce_erg[2] * CGS_POWER_TO_SI;
        let ces = ce0 + ce1 + ce2;
        heat -= ces * dt;
        esc += ces * dt;
        // Free-free global owner. Include all charged spectator ions, not only D/H/He4.
        let z2: f64 = S::ALL
            .into_iter()
            .map(|sp| {
                let q = f64::from(sp.charge());
                q * q * n[sp as usize]
            })
            .sum();
        ff = ne_cm * (z2 * 1e-6) * r.freefree_erg_cm3_s * CGS_POWER_TO_SI;
        heat -= ff * dt;
        esc += ff * dt;
        // D provider independently owns its CI/RR/CE binding and escape.
        heat += d_ledger.thermal * dt;
        chem += d_ledger.chemical * dt;
        esc += d_ledger.escape * dt;
    }
    // Exactly one global CMB owner based on *total* electrons, including D and spectators.
    let mut cmb = 0.0;
    if c.use_cmb {
        const SIGMA_T_CM2: f64 = 6.652_458_705_1e-25;
        const ME_G: f64 = 9.109_383_713_9e-28;
        const PLANCK_ERG_S: f64 = 6.626_070_15e-27;
        let hc = HHeModel::controlled_fixture();
        let arad = 8.0 * std::f64::consts::PI.powi(5) * hc.kb_erg_k.powi(4)
            / (15.0 * PLANCK_ERG_S.powi(3) * hc.c_cm_s.powi(3));
        let coeff = 4.0 * SIGMA_T_CM2 * arad * hc.kb_erg_k / (ME_G * hc.c_cm_s);
        cmb = coeff
            * (ne * 1e-6)
            * c.cmb_temperature_k.powi(4)
            * (c.cmb_temperature_k - t)
            * CGS_POWER_TO_SI;
        heat += cmb * dt;
    }
    let mut values = n;
    for j in 0..3 {
        chemistry_deltas(&mut values, j, (ci[j] - rr[j]) * dt);
    }
    chemistry_deltas(&mut values, 1, -dr * dt);
    chemistry_deltas(&mut values, 3, d_net * dt);
    // Fail before mutation: the formula owns no clipping nor partially accepted trial.
    let newgas = new_gas(values, s.gas.thermal_j_m3 + heat)?;
    let oldchem = s.binding_j_m3(c);
    let newchem = FullState {
        gas: newgas,
        photon_bins: vec![],
        escaped_j_m3: 0.0,
        cmb_reservoir_j_m3: 0.0,
        elapsed_s: 0.0,
    }
    .binding_j_m3(c);
    let expected = chem;
    let scale = newchem
        .abs()
        .max(oldchem.abs())
        .max(expected.abs())
        .max(1e-40);
    if ((newchem - oldchem) - chem).abs() > 3e-12 * scale {
        return Err(NetworkError::PhysicsLedger);
    }
    s.gas = newgas;
    s.escaped_j_m3 += esc;
    s.cmb_reservoir_j_m3 -= cmb * dt;
    if !all_finite(&[
        heat,
        chem,
        esc,
        cmb,
        ff,
        s.escaped_j_m3,
        s.cmb_reservoir_j_m3,
    ]) {
        return Err(NetworkError::NonFinite);
    }
    let mut rbudget = EventBudget {
        ci_events_m3: ci.map(|x| x * dt),
        rr_events_m3: rr.map(|x| x * dt),
        dr_hei_m3: dr * dt,
        thermal_change_j_m3: heat,
        chemical_change_j_m3: chem,
        escape_change_j_m3: esc,
        cmb_change_j_m3: -cmb * dt,
        freefree_integrated_j_m3: ff * dt,
        d_electron_integrated_m3: d_net * dt,
        ..EventBudget::default()
    };
    rbudget.ci_events_m3[3] = d_ci * dt;
    rbudget.rr_events_m3[3] = d_rr * dt;
    Ok(rbudget)
}

fn cx_step(s: &mut FullState, c: &NetworkConfig, dt: f64) -> Result<EventBudget, NetworkError> {
    if !c.use_cx {
        return Ok(EventBudget::default());
    }
    if c.owner != CxOwnership::ThermalSubstep {
        return Err(NetworkError::OwnershipConflict);
    }
    let component = MixtureCxComponent::new(c.deuterium, c.owner);
    let q = component
        .advance_cx_only(s.gas, dt, c.cx_controls)
        .map_err(NetworkError::Cx)?;
    s.gas = q.final_state;
    Ok(EventBudget {
        cx_signed_m3: q.extent_m3,
        thermal_change_j_m3: q.delta_thermal_j_m3,
        chemical_change_j_m3: q.delta_chemical_j_m3,
        ..EventBudget::default()
    })
}

/// First-order operator-split step; finite photons are shared across H/He/D.
/// dt is proper seconds and no expansion, no external photon births, no atomic source restarts.
/// A failed trial leaves the input bit-identical.
pub fn step(
    source: &FullState,
    config: &NetworkConfig,
    dt_s: f64,
) -> Result<NetworkResult, NetworkError> {
    source.validate(config)?;
    if !dt_s.is_finite() || dt_s < 0.0 {
        return Err(NetworkError::InvalidInput);
    }
    if config.use_cx && config.owner != CxOwnership::ThermalSubstep {
        return Err(NetworkError::OwnershipConflict);
    }
    let mut out = source.clone();
    let mut events = EventBudget::default();
    if dt_s == 0.0 {
        return Ok(NetworkResult {
            state: out,
            budget: events,
            attempts: 1,
            accepted: 1,
            rejected: 0,
        });
    }
    events.add(photo_step(&mut out, config, dt_s)?);
    events.add(collision_step(&mut out, config, dt_s)?);
    events.add(cx_step(&mut out, config, dt_s)?);
    out.elapsed_s += dt_s;
    out.validate(config)?;
    let initial = source.energy_j_m3(config);
    let final_e = out.energy_j_m3(config);
    let den = initial.abs().max(final_e.abs()).max(1e-50);
    if !all_finite(&[initial, final_e]) || (final_e - initial).abs() > 3e-11 * den {
        return Err(NetworkError::PhysicsLedger);
    }
    Ok(NetworkResult {
        state: out,
        budget: events,
        attempts: 1,
        accepted: 1,
        rejected: 0,
    })
}

/// Fixed global interval subdivided on every trial; no post-hoc clipping.
/// This is a bounded reference, not a certified stiff production integrator.
pub fn run_substeps(
    initial: &FullState,
    config: &NetworkConfig,
    dt_s: f64,
    steps: usize,
) -> Result<NetworkResult, NetworkError> {
    if !(1..=65_536).contains(&steps) || !dt_s.is_finite() || dt_s < 0.0 {
        return Err(NetworkError::InvalidInput);
    }
    let mut s = initial.clone();
    let mut b = EventBudget::default();
    for _ in 0..steps {
        let r = step(&s, config, dt_s / (steps as f64))?;
        s = r.state;
        b.add(r.budget)
    }
    Ok(NetworkResult {
        state: s,
        budget: b,
        attempts: steps,
        accepted: steps,
        rejected: 0,
    })
}

/// Restricted opt-in fixed-proper-volume uniform-emission transaction.
/// Each births[i] is integrated number/m^3 over this actual dt, at the unchanged
/// energy of source.photon_bins[i]. Beginning-of-step gas opacity stays frozen;
/// the coupled chemistry remains FIRST ORDER. Do not route Bianchi histories here.
#[derive(Clone, Debug)]
pub struct BirthNetworkResult {
    pub network: NetworkResult,
    pub injected_number_m3: f64,
    pub injected_energy_j_m3: f64,
}
pub fn step_fixed_volume_uniform_births(
    source: &FullState,
    config: &NetworkConfig,
    dt_s: f64,
    births: &[f64],
) -> Result<BirthNetworkResult, NetworkError> {
    source.validate(config)?;
    if births.len() != source.photon_bins.len()
        || !dt_s.is_finite()
        || dt_s < 0.
        || births.iter().any(|x| !x.is_finite() || *x < 0.)
    {
        return Err(NetworkError::InvalidInput);
    }
    if dt_s == 0. && births.iter().any(|x| *x != 0.) {
        return Err(NetworkError::InvalidInput);
    }
    // Exact legacy route, including its numerical choices and ownership guards.
    if births.iter().all(|x| *x == 0.) {
        return Ok(BirthNetworkResult {
            network: step(source, config, dt_s)?,
            injected_number_m3: 0.,
            injected_energy_j_m3: 0.,
        });
    }
    if config.use_cx && config.owner != CxOwnership::ThermalSubstep {
        return Err(NetworkError::OwnershipConflict);
    }
    let mut out = source.clone();
    let mut injected_number_m3 = 0.;
    let mut injected_energy_j_m3 = 0.;
    for (bin, born) in out.photon_bins.iter_mut().zip(births) {
        bin.number_m3 += born;
        injected_number_m3 += born;
        injected_energy_j_m3 += born * bin.energy_ev * EV_J;
    }
    if !all_finite(&[injected_number_m3, injected_energy_j_m3]) {
        return Err(NetworkError::NonFinite);
    }
    out.validate(config)?;
    let mut events =
        photo_step_births(&mut out, config, dt_s, Some((births, &source.photon_bins)))?;
    events.add(collision_step(&mut out, config, dt_s)?);
    events.add(cx_step(&mut out, config, dt_s)?);
    out.elapsed_s += dt_s;
    out.validate(config)?;
    let e0 = source.energy_j_m3(config);
    let e1 = out.energy_j_m3(config);
    let scale = e0
        .abs()
        .max(e1.abs())
        .max(injected_energy_j_m3.abs())
        .max(1e-50);
    if !all_finite(&[e0, e1]) || (e1 - e0 - injected_energy_j_m3).abs() > 3e-11 * scale {
        return Err(NetworkError::PhysicsLedger);
    }
    Ok(BirthNetworkResult {
        network: NetworkResult {
            state: out,
            budget: events,
            attempts: 1,
            accepted: 1,
            rejected: 0,
        },
        injected_number_m3,
        injected_energy_j_m3,
    })
}
