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

pub struct PositiveAgeBridge(pub SourceAgeBridge);
fn allowed_t(t: f64) -> bool {
    t.is_finite()
        && (crate::deuterium_charge_exchange::Savin2002::MINIMUM_K
            ..=crate::deuterium_charge_exchange::Savin2002::MAXIMUM_K)
            .contains(&t)
}
impl PositiveAgeBridge {
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
        newborn_start: Option<usize>,
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
        for (index, co) in s.cohorts.iter().enumerate() {
            let energy = co.ray_at(g)?.energy_ev;
            let rates = self.0.opacity_channels(energy, &initial, config)?;
            let opacity = rates.iter().sum::<f64>();
            let (abs, remain) = if opacity == 0.0 || co.n_comoving_m3 == 0.0 {
                (0.0, co.n_comoving_m3)
            } else if newborn_start.is_some_and(|start| index >= start) {
                let p = crate::birth_clock::uniform_partition(0., co.n_comoving_m3, opacity * dt)?;
                (p.absorbed, p.surviving)
            } else {
                (
                    co.n_comoving_m3 * (-(-opacity * dt).exp_m1()),
                    co.n_comoving_m3 * (-opacity * dt).exp(),
                )
            };
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
        self.advance_impl(initial, conf, dt, false)
    }
    /// Opt-in uniform-emission Phi clock at exactly static geometry only.
    /// Midpoint birth labels represent an integrated interval, not age moments.
    /// Existing histories are initial inventories, not certified prior Phi steps.
    /// Mixed continuation through legacy advance is outside this contract.
    pub fn advance_fixed_geometry_phi(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
    ) -> Result<AgeStep, NetworkError> {
        self.advance_impl(initial, conf, dt, true)
    }
    fn advance_impl(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
        phi_births: bool,
    ) -> Result<AgeStep, NetworkError> {
        if conf.photon_source != SOURCE_ID || !conf.use_photo || !dt.is_finite() || dt <= 0.0 {
            return Err(NetworkError::SourceMismatch);
        }
        let t0 = initial.time_s;
        let tm = t0 + 0.5 * dt;
        let t1 = t0 + dt;
        let g0 = self.0.snapshot(t0)?;
        let gm = self.0.snapshot(tm)?;
        let g1 = self.0.snapshot(t1)?;
        if phi_births {
            initial.full.validate(conf)?;
            if !initial.geometry_work_j_com3.is_finite()
                || !initial.max_grey_number_relative_error.is_finite()
                || initial
                    .max_grey_species_relative_error
                    .iter()
                    .any(|x| !x.is_finite())
            {
                return Err(NetworkError::NonFinite);
            }
            initial
                .chemistry_accepted
                .checked_add(1)
                .ok_or(NetworkError::InputOutsideDomain)?;
            let point = self.0.geometry.reference_point;
            if point.mean_hubble_per_s != 0.
                || point.shear_per_s != 0.
                || g0 != gm
                || gm != g1
                || initial.full.elapsed_s != t0
                || !initial.full.photon_bins.is_empty()
                || !t0.is_finite()
                || !tm.is_finite()
                || !t1.is_finite()
                || tm <= t0
                || t1 <= tm
            {
                return Err(NetworkError::InputOutsideDomain);
            }
            let new_count = self
                .0
                .source
                .spectral_cells
                .len()
                .checked_mul(self.0.source.angular_cells.len())
                .ok_or(NetworkError::InputOutsideDomain)?;
            if initial
                .cohorts
                .len()
                .checked_add(new_count)
                .ok_or(NetworkError::InputOutsideDomain)?
                > 65_536
            {
                return Err(NetworkError::InputOutsideDomain);
            }
            if initial.cohorts.iter().any(|c| {
                c.birth_geometry != g0 || !c.birth_time_s.is_finite() || c.birth_time_s > t0
            }) {
                return Err(NetworkError::InputOutsideDomain);
            }
            if [
                initial.source_injected_count_com3,
                initial.source_injected_energy_j_com3,
                initial.photon_absorbed_count_com3,
            ]
            .iter()
            .any(|x| !x.is_finite() || *x < 0.)
            {
                return Err(NetworkError::NonFinite);
            }
        }
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
        let newborn_start = if phi_births {
            Some(s.cohorts.len())
        } else {
            None
        };
        s.cohorts.extend(birth);
        // Source-owned, cohort-exact photons; P2 atomic+CX runs with photons OFF.
        let photo = self.photo(&mut s, &gm, conf, dt, newborn_start)?;
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
        if phi_births {
            s.chemistry_accepted = s
                .chemistry_accepted
                .checked_add(1)
                .ok_or(NetworkError::InputOutsideDomain)?;
        } else {
            s.chemistry_accepted += 1;
        }
        let (wph1, wgas1) = self.0.drift(&mut s, &gm, &g1)?;
        s.time_s = t1;
        let e1 = self.0.total_com_energy(&s, conf, &g1)?;
        let expected = e0 + u_birth + wph0 + wgas0 + wph1 + wgas1;
        let denom = e0.abs().max(e1.abs()).max(expected.abs()).max(1e-50);
        let error = (e1 - expected).abs() / denom;
        if !error.is_finite() || error > 3e-10 {
            return Err(NetworkError::PhysicsLedger);
        }
        if phi_births && !s.geometry_work_j_com3.is_finite() {
            return Err(NetworkError::NonFinite);
        }
        if phi_births
            && [
                s.source_injected_count_com3,
                s.source_injected_energy_j_com3,
                s.photon_absorbed_count_com3,
            ]
            .iter()
            .any(|x| !x.is_finite() || *x < 0.)
        {
            return Err(NetworkError::NonFinite);
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
