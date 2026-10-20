//! P4/S2 opt-in positive birth-opacity clock with exact 1-step emission
//! convolution under frozen midpoint opacity. Original owner_src and original
//! P3 positive_age.rs remain unchanged. Model still uses midpoint birth
//! geometry, finite discrete energy/angle cells, Lie-split H/He/D chemistry.
//!
//! Prior cohorts: N_old * exp(-tau); new cohorts: B * phi(tau)
//! where phi(tau) = (1-exp(-tau))/tau and B = midpoint_j * dt.
//! Photo events are computed once from N_old*(1-exp(-tau)) + B*(1-phi).
//! Noncompressed cohort-by-cohort positive source-age transport, independent
//! from the P2 MAX_PHOTON_BINS grey bridge. Frozen-opacity exact per stage;
//! P2 owns only gas collisional/CX/FF/CMB, never duplicate photo reactions.
use crate::axbi_sources::SOURCE_ID;
use crate::bianchi_i::GeometrySnapshot;
use crate::deuterium_atomic::{DChargeExchange, d_atomic_rhs};
use crate::full_network::{self, EV_J, EventBudget, FullState, NetworkConfig, NetworkError};
use crate::isotope_state::{IsotopeNumberState, IsotopeSpecies as S};
use crate::mixture_eos::MixtureState;
use crate::source_age::{AgeHistory, AgeStep, SourceAgeBridge};

/// Nonnegative, photon-conserving integrated source/absorption fractions.
/// `tau` is the dimensionless total optical depth (kappa s^-1 * dt s).
#[derive(Debug, Clone, Copy)]
pub struct SlabFractions {
    pub old_surviving: f64,
    pub old_absorbed: f64,
    pub new_surviving: f64,
    pub new_absorbed: f64,
}

/// Evaluate phi(-tau) and (1-phi) without cancellation for tau -> 0.
/// The positive branch is exact under a constant source and fixed opacity.
pub fn photon_slab(tau: f64) -> Result<SlabFractions, NetworkError> {
    if !tau.is_finite() || tau < 0.0 {
        return Err(NetworkError::InvalidInput);
    }
    if tau == 0.0 {
        return Ok(SlabFractions {
            old_surviving: 1.0,
            old_absorbed: 0.0,
            new_surviving: 1.0,
            new_absorbed: 0.0,
        });
    }
    let old_surviving = (-tau).exp();
    let old_absorbed = -(-tau).exp_m1();
    let new_absorbed = if tau < 1.0e-3 {
        // tau/2 - tau^2/6 + tau^3/24 - tau^4/120 + tau^5/720 - tau^6/5040
        tau * (0.5
            + tau
                * (-1.0 / 6.0
                    + tau
                        * (1.0 / 24.0 + tau * (-1.0 / 120.0 + tau * (1.0 / 720.0 - tau / 5040.0)))))
    } else {
        1.0 - old_absorbed / tau
    };
    let new_surviving = 1.0 - new_absorbed;
    let result = SlabFractions {
        old_surviving,
        old_absorbed,
        new_surviving,
        new_absorbed,
    };
    if ![old_surviving, old_absorbed, new_surviving, new_absorbed]
        .into_iter()
        .all(|x| x.is_finite() && (0.0..=1.0).contains(&x))
    {
        return Err(NetworkError::NonFinite);
    }
    Ok(result)
}

pub struct PositiveBirthClockBridge(pub SourceAgeBridge);
fn allowed_t(t: f64) -> bool {
    t.is_finite()
        && (crate::deuterium_charge_exchange::Savin2002::MINIMUM_K
            ..=crate::deuterium_charge_exchange::Savin2002::MAXIMUM_K)
            .contains(&t)
}
impl PositiveBirthClockBridge {
    pub fn initial(
        &self,
        full: FullState,
        config: &NetworkConfig,
        t: f64,
    ) -> Result<AgeHistory, NetworkError> {
        self.0.initial(full, config, t)
    }
    fn photo(
        &self,
        s: &mut AgeHistory,
        g: &GeometrySnapshot,
        config: &NetworkConfig,
        dt: f64,
        prior_cohorts: usize,
    ) -> Result<EventBudget, NetworkError> {
        let vol = g
            .volume_factor()
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        let initial = s.full.gas;
        let initial_nuclei = initial.nuclei;
        let base = crate::HHeModel::controlled_fixture().threshold_ev;
        let chi = [base[0], base[1], base[2], config.deuterium.chi_d_ev()];
        let mut delta = [0.0; 4];
        let (mut photon_energy, mut thermal, mut d_heat) = (0.0, 0.0, 0.0);
        let mut residuals = Vec::with_capacity(s.cohorts.len());
        if prior_cohorts > s.cohorts.len() {
            return Err(NetworkError::InvalidInput);
        }
        for (idx, co) in s.cohorts.iter().enumerate() {
            let energy = co.ray_at(g)?.energy_ev;
            let rates = self.0.opacity_channels(energy, &initial, config)?;
            let opacity = rates.iter().sum::<f64>();
            if !opacity.is_finite()
                || opacity < 0.0
                || !co.n_comoving_m3.is_finite()
                || co.n_comoving_m3 < 0.0
            {
                return Err(NetworkError::NonFinite);
            }
            let frac = photon_slab(opacity * dt)?;
            // Previously existing photon cohorts see the complete step.
            // Fresh midpoint-represented birth cohorts see a positive
            // integral over all emission times within this step.
            let (absorbed_fraction, survivor_fraction) = if idx < prior_cohorts {
                (frac.old_absorbed, frac.old_surviving)
            } else {
                (frac.new_absorbed, frac.new_surviving)
            };
            let abs = co.n_comoving_m3 * absorbed_fraction;
            let remain = co.n_comoving_m3 * survivor_fraction;
            if !remain.is_finite() || remain < 0.0 {
                return Err(NetworkError::NonFinite);
            }
            residuals.push(remain);
            if opacity > 0.0 {
                let number = abs / vol;
                photon_energy += number * energy * EV_J;
                for j in 0..4 {
                    let x = number * rates[j] / opacity;
                    delta[j] += x;
                    let heat = x * (energy - chi[j]) * EV_J;
                    thermal += heat;
                    if j == 3 {
                        d_heat += heat
                    }
                }
            }
        }
        if delta[3] > 0.0 {
            let neutral = initial_nuclei.density_m3(S::DNeutral);
            if neutral <= 0.0 {
                return Err(NetworkError::PhysicsLedger);
            }
            let input = config
                .deuterium
                .photo_input_from_bound_rates(
                    delta[3] / (neutral * dt),
                    d_heat / (neutral * dt),
                    config.photon_source,
                )
                .map_err(|_| NetworkError::SourceMismatch)?;
            let r = d_atomic_rhs(
                config.deuterium,
                &initial_nuclei,
                initial.eos()?.temperature_k,
                &input,
                DChargeExchange::Disabled,
            )
            .map_err(|_| NetworkError::InputOutsideDomain)?;
            if (r.photo_events_m3_s * dt - delta[3]).abs() > 4e-12 * delta[3].max(1e-40)
                || (r.channel_energy[0].thermal * dt - d_heat).abs()
                    > 4e-12 * d_heat.abs().max(1e-40)
            {
                return Err(NetworkError::PhysicsLedger);
            }
        }
        let mut vals = [0.0; 13];
        for sp in S::ALL {
            vals[sp as usize] = initial_nuclei.density_m3(sp);
        }
        for (j, (from, to)) in [
            (S::H1Neutral, S::H1Ionized),
            (S::He4Neutral, S::He4SinglyIonized),
            (S::He4SinglyIonized, S::He4DoublyIonized),
            (S::DNeutral, S::DIonized),
        ]
        .into_iter()
        .enumerate()
        {
            vals[from as usize] -= delta[j];
            vals[to as usize] += delta[j];
        }
        let nuclei = IsotopeNumberState::new(vals).map_err(|_| NetworkError::NegativePopulation)?;
        let gas = MixtureState {
            nuclei,
            thermal_j_m3: initial.thermal_j_m3 + thermal,
        };
        let eos = gas.eos()?;
        if !allowed_t(eos.temperature_k) {
            return Err(NetworkError::TemperatureOutsideSource);
        }
        let chem = delta
            .iter()
            .zip(chi)
            .map(|(x, e)| x * e * EV_J)
            .sum::<f64>();
        let u0 = s.full.binding_j_m3(config);
        let u1 = FullState {
            gas,
            photon_bins: vec![],
            escaped_j_m3: 0.0,
            cmb_reservoir_j_m3: 0.0,
            elapsed_s: 0.0,
        }
        .binding_j_m3(config);
        if (u1 - u0 - chem).abs() > 3e-12 * u1.abs().max(u0.abs()).max(1e-40) {
            return Err(NetworkError::PhysicsLedger);
        }
        // Transaction commit only after all physical checks passed.
        for (co, r) in s.cohorts.iter_mut().zip(residuals) {
            co.n_comoving_m3 = r
        }
        s.full.gas = gas;
        s.photon_absorbed_count_com3 += delta.iter().sum::<f64>() * vol;
        Ok(EventBudget {
            photo_events_m3: delta,
            photo_energy_j_m3: photon_energy,
            thermal_change_j_m3: thermal,
            chemical_change_j_m3: chem,
            ..EventBudget::default()
        })
    }
    pub fn advance(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
    ) -> Result<AgeStep, NetworkError> {
        if conf.photon_source != SOURCE_ID || !conf.use_photo || !dt.is_finite() || dt <= 0.0 {
            return Err(NetworkError::SourceMismatch);
        }
        let t0 = initial.time_s;
        let tm = t0 + 0.5 * dt;
        let t1 = t0 + dt;
        if !t1.is_finite() || t1 <= t0 {
            return Err(NetworkError::NoForwardProgress);
        }
        let g0 = self.0.snapshot(t0)?;
        let gm = self.0.snapshot(tm)?;
        let g1 = self.0.snapshot(t1)?;
        let e0 = self.0.total_com_energy(initial, conf, &g0)?;
        let mut s = initial.clone();
        let (wph0, wgas0) = self.0.drift(&mut s, &g0, &gm)?;
        let birth = self.0.source_births(tm, dt)?;
        let n_birth = birth.iter().map(|c| c.n_comoving_m3).sum::<f64>();
        let u_birth = birth
            .iter()
            .map(|c| c.n_comoving_m3 * c.energy_at_birth_ev * EV_J)
            .sum::<f64>();
        s.source_injected_count_com3 += n_birth;
        s.source_injected_energy_j_com3 += u_birth;
        let prior_cohorts = s.cohorts.len();
        s.cohorts.extend(birth);
        // P4: exact constant-midpoint-opacity source exposure for newborns.
        // Frozen P3 PositiveAgeBridge::advance remains separately available.
        let photo = self.photo(&mut s, &gm, conf, dt, prior_cohorts)?;
        s.full.photon_bins.clear();
        let mut local = *conf;
        local.use_photo = false;
        let chemistry = full_network::step(&s.full, &local, dt)?;
        let mut events = chemistry.budget;
        events.photo_events_m3 = photo.photo_events_m3;
        events.photo_energy_j_m3 = photo.photo_energy_j_m3;
        events.thermal_change_j_m3 += photo.thermal_change_j_m3;
        events.chemical_change_j_m3 += photo.chemical_change_j_m3;
        s.full = chemistry.state;
        s.chemistry_accepted += 1;
        let (wph1, wgas1) = self.0.drift(&mut s, &gm, &g1)?;
        s.time_s = t1;
        let e1 = self.0.total_com_energy(&s, conf, &g1)?;
        let expected = e0 + u_birth + wph0 + wgas0 + wph1 + wgas1;
        let denom = e0.abs().max(e1.abs()).max(expected.abs()).max(1e-50);
        let error = (e1 - expected).abs() / denom;
        if !error.is_finite() || error > 3e-10 {
            return Err(NetworkError::PhysicsLedger);
        }
        Ok(AgeStep {
            state: s,
            source_birth_com3: n_birth,
            radiation_redshift_work_j_com3: wph0 + wph1,
            adiabatic_gas_work_j_com3: wgas0 + wgas1,
            projected_grey_absorption_relative_error: 0.0,
            projected_grey_species_relative_error: [0.0; 4],
            global_energy_relative_error: error,
            chemistry_budget: events,
        })
    }
}
