//! RUN04 opt-in BASS source-table geometry + inherited source-native H/He/D event transaction.
//! Same midpoint Lie split, no second gas owner; full EFE/radiation backreaction is not solved.
use crate::axbi_sources::SOURCE_ID;
use crate::bass_source_bridge::BassSourceBridge;
use crate::bianchi_i::GeometrySnapshot;
use crate::deuterium_atomic::{DChargeExchange, d_atomic_rhs};
use crate::full_network::{self, EV_J, EventBudget, FullState, NetworkConfig, NetworkError};
use crate::isotope_state::{IsotopeNumberState, IsotopeSpecies as S};
use crate::mixture_eos::MixtureState;
use crate::positive_birth_clock::photon_slab;
use crate::positive_spectral::expand_births;
use crate::source_age::{AgeHistory, AgeStep};

use crate::retarded_transport::{
    OpacityEventMode, RetardedControls, RetardedDiagnostics, gauss_birth_nodes,
};

pub struct BassRetardedBridge(pub BassSourceBridge, pub RetardedControls);
fn allowed_t(t: f64) -> bool {
    t.is_finite()
        && (crate::deuterium_charge_exchange::Savin2002::MINIMUM_K
            ..=crate::deuterium_charge_exchange::Savin2002::MAXIMUM_K)
            .contains(&t)
}
impl BassRetardedBridge {
    pub fn initial(
        &self,
        full: FullState,
        conf: &NetworkConfig,
        t: f64,
    ) -> Result<AgeHistory, NetworkError> {
        self.0.initial(full, conf, t)
    }

    pub fn emit_births(
        &self,
        t0: f64,
        dt: f64,
        conf: &NetworkConfig,
    ) -> Result<Vec<crate::source_age::Cohort>, NetworkError> {
        if !t0.is_finite() || !dt.is_finite() || dt <= 0.0 || conf.photon_source != SOURCE_ID {
            return Err(NetworkError::InvalidInput);
        }
        let mut births = Vec::new();
        for (u, w) in gauss_birth_nodes(self.1.birth_gauss_nodes)? {
            let tb = t0 + u * dt;
            let batch = self.0.source_births(tb, dt * w)?;
            births.extend(expand_births(
                &self.0.source,
                &batch,
                conf.deuterium.chi_d_ev(),
                self.1.spectrum,
            )?);
        }
        Ok(births)
    }

    /// Forward transport each cohort from t0 or its physical birth time.
    /// Optical depth is partitioned into positive exact-frozen local segments.
    /// Time-varying opacity is evaluated using source-native sigma(E(t)),
    /// comoving-frozen gas density n_s(t)=n_s(t_mid) V_mid/V(t), and exact rays.
    fn photo(
        &self,
        s: &mut AgeHistory,
        gm: &GeometrySnapshot,
        conf: &NetworkConfig,
        t0: f64,
        t1: f64,
        prior: usize,
    ) -> Result<(EventBudget, RetardedDiagnostics), NetworkError> {
        let vm = gm
            .volume_factor()
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        let gas_mid = s.full.gas;
        let old_nuclei = gas_mid.nuclei;
        let chi = crate::HHeModel::controlled_fixture().threshold_ev;
        let chis = [chi[0], chi[1], chi[2], conf.deuterium.chi_d_ev()];
        let mut delta_com = [0.; 4];
        let mut photo_e_com = 0.;
        let mut thermal_com = 0.;
        let mut d_heat_com = 0.;
        let mut geom_work = 0.;
        let mut geom_work_ind = 0.;
        let mut provider_threshold_cuts = 0_usize;
        let mut residuals = Vec::with_capacity(s.cohorts.len());
        if prior > s.cohorts.len() {
            return Err(NetworkError::InvalidInput);
        }
        for (index, co) in s.cohorts.iter().enumerate() {
            let ta = if index < prior { t0 } else { co.birth_time_s };
            if !ta.is_finite() || ta < t0 || ta >= t1 {
                return Err(NetworkError::InvalidInput);
            }
            let initial_n = co.n_comoving_m3;
            if !initial_n.is_finite() || initial_n < 0. {
                return Err(NetworkError::NonFinite);
            }
            let ga = self.0.snapshot(ta)?;
            let e_initial = co.ray_at(&ga)?.energy_ev;
            let mut n = initial_n;
            let m = self.1.opacity_substeps;
            let dt = (t1 - ta) / m as f64;
            let mut absorption_energy_ev = 0.;
            for j in 0..m {
                let aa = ta + j as f64 * dt;
                let bb = if j + 1 == m {
                    t1
                } else {
                    ta + (j + 1) as f64 * dt
                };
                let partitions = match self.1.opacity_event_mode {
                    OpacityEventMode::FrozenMidpoint => vec![(aa, bb)],
                    OpacityEventMode::SplitProviderThresholds => {
                        crate::bass_geometry::partition_at_photo_events(
                            co,
                            &self.0.geometry,
                            aa,
                            bb,
                            conf.deuterium.chi_d_ev(),
                        )?
                    }
                };
                provider_threshold_cuts += partitions.len() - 1;
                for (aa, bb) in partitions {
                    let mid = 0.5 * (aa + bb);
                    let g = self.0.snapshot(mid)?;
                    let vmid = g
                        .volume_factor()
                        .map_err(|_| NetworkError::InputOutsideDomain)?;
                    let en = co.ray_at(&g)?.energy_ev;
                    let mut rates = self.0.opacity_channels(en, &gas_mid, conf)?;
                    let denscale = vm / vmid;
                    if !denscale.is_finite() || denscale <= 0. {
                        return Err(NetworkError::NonFinite);
                    }
                    for r in &mut rates {
                        *r *= denscale;
                    }
                    let k: f64 = rates.iter().sum();
                    if !k.is_finite() || k < 0. {
                        return Err(NetworkError::NonFinite);
                    }
                    let tau = k * (bb - aa);
                    let frac = photon_slab(tau)?;
                    let absorbed = n * frac.old_absorbed;
                    let remain = n * frac.old_surviving;
                    if !absorbed.is_finite() || !remain.is_finite() || remain < 0. {
                        return Err(NetworkError::NonFinite);
                    }
                    let qa = self.0.snapshot(aa)?;
                    let qb = self.0.snapshot(bb)?;
                    let e_a = co.ray_at(&qa)?.energy_ev;
                    let e_b = co.ray_at(&qb)?.energy_ev;
                    geom_work_ind += n * frac.new_surviving * (e_b - e_a) * EV_J;
                    if k > 0. {
                        absorption_energy_ev += absorbed * en;
                        for sp in 0..4 {
                            let a = absorbed * rates[sp] / k;
                            if a > 0. && en < chis[sp] {
                                return Err(NetworkError::PhysicsLedger);
                            }
                            delta_com[sp] += a;
                            thermal_com += a * (en - chis[sp]) * EV_J;
                            if sp == 3 {
                                d_heat_com += a * (en - chis[sp]) * EV_J;
                            }
                        }
                        photo_e_com += absorbed * en * EV_J;
                    }
                    n = remain;
                }
            }
            let g1 = self.0.snapshot(t1)?;
            let e1 = co.ray_at(&g1)?.energy_ev;
            geom_work += (n * e1 - initial_n * e_initial + absorption_energy_ev) * EV_J;
            residuals.push(n);
        }
        let mut delta = [0.; 4];
        for j in 0..4 {
            delta[j] = delta_com[j] / vm;
        }
        let thermal = thermal_com / vm;
        let d_heat = d_heat_com / vm;
        let photon_energy = photo_e_com / vm;
        if delta[3] > 0. {
            let dn = old_nuclei.density_m3(S::DNeutral);
            if dn <= 0. {
                return Err(NetworkError::PhysicsLedger);
            }
            let input = conf
                .deuterium
                .photo_input_from_bound_rates(
                    delta[3] / (dn * (t1 - t0)),
                    d_heat / (dn * (t1 - t0)),
                    conf.photon_source,
                )
                .map_err(|_| NetworkError::SourceMismatch)?;
            let r = d_atomic_rhs(
                conf.deuterium,
                &old_nuclei,
                gas_mid.eos()?.temperature_k,
                &input,
                DChargeExchange::Disabled,
            )
            .map_err(|_| NetworkError::InputOutsideDomain)?;
            if (r.photo_events_m3_s * (t1 - t0) - delta[3]).abs() > 4e-12 * delta[3].max(1e-40)
                || (r.channel_energy[0].thermal * (t1 - t0) - d_heat).abs()
                    > 4e-12 * d_heat.abs().max(1e-40)
            {
                return Err(NetworkError::PhysicsLedger);
            }
        }
        let mut vals = [0.; 13];
        for sp in S::ALL {
            vals[sp as usize] = old_nuclei.density_m3(sp);
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
            thermal_j_m3: gas_mid.thermal_j_m3 + thermal,
        };
        if !allowed_t(gas.eos()?.temperature_k) {
            return Err(NetworkError::TemperatureOutsideSource);
        }
        let chem = delta
            .iter()
            .zip(chis)
            .map(|(x, e)| x * e * EV_J)
            .sum::<f64>();
        let u0 = s.full.binding_j_m3(conf);
        let u1 = FullState {
            gas,
            photon_bins: vec![],
            escaped_j_m3: 0.,
            cmb_reservoir_j_m3: 0.,
            elapsed_s: 0.,
        }
        .binding_j_m3(conf);
        if (u1 - u0 - chem).abs() > 3e-12 * u1.abs().max(u0.abs()).max(1e-40) {
            return Err(NetworkError::PhysicsLedger);
        }
        // Commit photons and gas simultaneously after all checks.
        for (co, r) in s.cohorts.iter_mut().zip(residuals) {
            co.n_comoving_m3 = r;
        }
        s.full.gas = gas;
        s.photon_absorbed_count_com3 += delta_com.iter().sum::<f64>();
        if !geom_work.is_finite() || !geom_work_ind.is_finite() {
            return Err(NetworkError::NonFinite);
        }
        Ok((
            EventBudget {
                photo_events_m3: delta,
                photo_energy_j_m3: photon_energy,
                thermal_change_j_m3: thermal,
                chemical_change_j_m3: chem,
                ..EventBudget::default()
            },
            RetardedDiagnostics {
                photon_work_ledger_j_com3: geom_work,
                photon_work_independent_j_com3: geom_work_ind,
                photon_events_com3: delta_com,
                provider_threshold_cuts,
                ..RetardedDiagnostics::default()
            },
        ))
    }

    pub fn advance_with_diagnostics(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
    ) -> Result<(AgeStep, RetardedDiagnostics), NetworkError> {
        if conf.photon_source != SOURCE_ID || !conf.use_photo || !dt.is_finite() || dt <= 0. {
            return Err(NetworkError::SourceMismatch);
        }
        let t0 = initial.time_s;
        let tm = t0 + dt / 2.;
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
        s.geometry_work_j_com3 -= wph0;
        let births = self.emit_births(t0, dt, conf)?;
        let n_birth = births.iter().map(|c| c.n_comoving_m3).sum::<f64>();
        let e_birth = births
            .iter()
            .map(|c| c.n_comoving_m3 * c.energy_at_birth_ev * EV_J)
            .sum::<f64>();
        s.source_injected_count_com3 += n_birth;
        s.source_injected_energy_j_com3 += e_birth;
        let prior = s.cohorts.len();
        s.cohorts.extend(births);
        let (photo, mut diag) = self.photo(&mut s, &gm, conf, t0, t1, prior)?;
        s.full.photon_bins.clear();
        let mut local = *conf;
        local.use_photo = false;
        // Cosmic CMB bath at the same proper midpoint; not the legacy fixed 20 K fixture.
        local.cmb_temperature_k = self.0.cmb_t0_k
            / gm.volume_factor()
                .map_err(|_| NetworkError::InputOutsideDomain)?
                .cbrt();
        let chemistry = full_network::step(&s.full, &local, dt)?;
        let mut events = chemistry.budget;
        events.photo_events_m3 = photo.photo_events_m3;
        events.photo_energy_j_m3 = photo.photo_energy_j_m3;
        events.thermal_change_j_m3 += photo.thermal_change_j_m3;
        events.chemical_change_j_m3 += photo.chemical_change_j_m3;
        s.full = chemistry.state;
        s.chemistry_accepted += 1;
        let (wph1, wgas1) = self.0.drift(&mut s, &gm, &g1)?;
        s.geometry_work_j_com3 -= wph1;
        s.geometry_work_j_com3 += diag.photon_work_ledger_j_com3;
        s.time_s = t1;
        let e1 = self.0.total_com_energy(&s, conf, &g1)?;
        let expected = e0 + e_birth + wgas0 + wgas1 + diag.photon_work_ledger_j_com3;
        let denom = e1.abs().max(e0.abs()).max(expected.abs()).max(1e-50);
        let error = (e1 - expected).abs() / denom;
        if !error.is_finite() || error > 3e-10 {
            return Err(NetworkError::PhysicsLedger);
        }
        diag.newborn_gl_count = s.cohorts.len() - prior;
        diag.emitted_photon_energy_j_com3 = e_birth;
        Ok((
            AgeStep {
                state: s,
                source_birth_com3: n_birth,
                radiation_redshift_work_j_com3: diag.photon_work_ledger_j_com3,
                adiabatic_gas_work_j_com3: wgas0 + wgas1,
                projected_grey_absorption_relative_error: 0.,
                projected_grey_species_relative_error: [0.; 4],
                global_energy_relative_error: error,
                chemistry_budget: events,
            },
            diag,
        ))
    }
    pub fn advance(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
    ) -> Result<AgeStep, NetworkError> {
        self.advance_with_diagnostics(initial, conf, dt)
            .map(|x| x.0)
    }
}
