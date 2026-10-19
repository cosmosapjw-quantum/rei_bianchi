//! P4/S3 source-native retarded photon characteristics at a frozen gas midpoint.
//! Retains each actual GL2/4 emission proper time, exact Bianchi-I Killing ray,
//! and positive competing HI/HeI/HeII/DI photo events. Gas evolution remains
//! owner P2 Lie-split; no assertion of global second-order accuracy.
use crate::axbi_sources::SOURCE_ID;
use crate::bianchi_i::GeometrySnapshot;
use crate::deuterium_atomic::{DChargeExchange, d_atomic_rhs};
use crate::full_network::{self, EV_J, EventBudget, FullState, NetworkConfig, NetworkError};
use crate::isotope_state::{IsotopeNumberState, IsotopeSpecies as S};
use crate::mixture_eos::MixtureState;
use crate::positive_birth_clock::photon_slab;
use crate::positive_spectral::expand_births;
use crate::source_age::{AgeHistory, AgeStep, SourceAgeBridge};
use crate::threshold_roots::split_by_thresholds_from_energies;
use std::collections::HashMap;

use crate::retarded_transport::{RetardedControls, gauss_birth_nodes};

/// Audit output for a single step with independent gas and photon geometric work.
#[derive(Clone, Copy, Debug, Default)]
pub struct RetardedDiagnostics {
    pub photon_work_ledger_j_com3: f64,
    pub photon_work_independent_j_com3: f64,
    pub newborn_gl_count: usize,
    pub photon_events_com3: [f64; 4],
    pub emitted_photon_energy_j_com3: f64,
    pub threshold_crossings: usize,
    pub unique_geometry_plans: usize,
    /// Only cohorts represented by literal 0.0 photons are removed.
    pub retired_exact_zero_cohorts: usize,
    /// Bit-exact energy keyed immutable opacity lookups on the same gas_mid.
    pub rate_cache_hits: usize,
    pub rate_cache_misses: usize,
}

#[derive(Clone, Copy, Debug)]
struct BaseSlab {
    a: f64,
    b: f64,
    ga: GeometrySnapshot,
    gb: GeometrySnapshot,
    gm: GeometrySnapshot,
    vmid: f64,
}

pub struct PositiveThresholdBridge(pub SourceAgeBridge, pub RetardedControls);
fn allowed_t(t: f64) -> bool {
    t.is_finite()
        && (crate::deuterium_charge_exchange::Savin2002::MINIMUM_K
            ..=crate::deuterium_charge_exchange::Savin2002::MAXIMUM_K)
            .contains(&t)
}
impl PositiveThresholdBridge {
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
        let mut residuals = Vec::with_capacity(s.cohorts.len());
        let mut plans: HashMap<u64, Vec<BaseSlab>> = HashMap::new();
        let mut threshold_crossings = 0usize;
        let mut unique_geometry_plans = 0usize;
        // One gas midpoint owns rate evaluation. Never reuse across gas steps.
        let mut rate_cache: HashMap<u64, [f64; 4]> = HashMap::new();
        let (mut rate_cache_hits, mut rate_cache_misses) = (0usize, 0usize);
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
            if initial_n == 0.0 {
                residuals.push(0.0);
                continue;
            }
            let ga = self.0.snapshot(ta)?;
            let e_initial = co.ray_at(&ga)?.energy_ev;
            let mut n = initial_n;
            // Reuse the immutable geometry snapshots for all cohorts sharing
            // the same physical start time (old t0, or GL birth times).
            // No approximation/age merging: distinct Killing momenta are retained.
            if let std::collections::hash_map::Entry::Vacant(vacant) = plans.entry(ta.to_bits()) {
                let m = self.1.opacity_substeps;
                let dt = (t1 - ta) / m as f64;
                let mut slabs = Vec::with_capacity(m);
                for j in 0..m {
                    let aa = ta + j as f64 * dt;
                    let bb = if j + 1 == m {
                        t1
                    } else {
                        ta + (j + 1) as f64 * dt
                    };
                    let mid = 0.5 * (aa + bb);
                    let ga = self.0.snapshot(aa)?;
                    let gb = self.0.snapshot(bb)?;
                    let gm = self.0.snapshot(mid)?;
                    let vmid = gm
                        .volume_factor()
                        .map_err(|_| NetworkError::InputOutsideDomain)?;
                    slabs.push(BaseSlab {
                        a: aa,
                        b: bb,
                        ga,
                        gb,
                        gm,
                        vmid,
                    });
                }
                vacant.insert(slabs);
                unique_geometry_plans += 1;
            }
            let mut absorption_energy_ev = 0.;
            let coarse = plans.get(&ta.to_bits()).ok_or(NetworkError::InvalidInput)?;
            for slab in coarse {
                let endpoint_energies = (
                    co.ray_at(&slab.ga)?.energy_ev,
                    co.ray_at(&slab.gb)?.energy_ev,
                );
                let splits = split_by_thresholds_from_energies(
                    &self.0.geometry,
                    co,
                    slab.a,
                    slab.b,
                    endpoint_energies.0,
                    endpoint_energies.1,
                    conf.deuterium.chi_d_ev(),
                )?;
                threshold_crossings += splits.len() - 2;
                // Use cached geometry on non-crossing cells and evaluate extra
                // geometry snapshots only at actual discontinuity roots.
                for (sidx, window) in splits.windows(2).enumerate() {
                    let aa = window[0];
                    let bb = window[1];
                    let (ga, gb, g, vmid) = if splits.len() == 2 {
                        (slab.ga, slab.gb, slab.gm, slab.vmid)
                    } else {
                        let ga = if sidx == 0 {
                            slab.ga
                        } else {
                            self.0.snapshot(aa)?
                        };
                        let gb = if sidx + 2 == splits.len() {
                            slab.gb
                        } else {
                            self.0.snapshot(bb)?
                        };
                        let g = self.0.snapshot(0.5 * (aa + bb))?;
                        let vmid = g
                            .volume_factor()
                            .map_err(|_| NetworkError::InputOutsideDomain)?;
                        (ga, gb, g, vmid)
                    };
                    let en = co.ray_at(&g)?.energy_ev;
                    let mut rates = if let Some(values) = rate_cache.get(&en.to_bits()) {
                        rate_cache_hits += 1;
                        *values
                    } else {
                        let values = self.0.opacity_channels(en, &gas_mid, conf)?;
                        rate_cache_misses += 1;
                        if rate_cache.len() < 8192 {
                            rate_cache.insert(en.to_bits(), values);
                        }
                        values
                    };
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
                    let frac = photon_slab(k * (bb - aa))?;
                    let absorbed = n * frac.old_absorbed;
                    let remain = n * frac.old_surviving;
                    if !absorbed.is_finite() || !remain.is_finite() || remain < 0. {
                        return Err(NetworkError::NonFinite);
                    }
                    let e_a = if splits.len() == 2 {
                        endpoint_energies.0
                    } else {
                        co.ray_at(&ga)?.energy_ev
                    };
                    let e_b = if splits.len() == 2 {
                        endpoint_energies.1
                    } else {
                        co.ray_at(&gb)?.energy_ev
                    };
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
                threshold_crossings,
                unique_geometry_plans,
                rate_cache_hits,
                rate_cache_misses,
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

    /// Lossless under the represented f64 state: remove only exact-zero photon
    /// cohorts after an accepted transaction. There is no relative cutoff,
    /// approximate phase-space merging, or hidden photon/energy reassignment.
    /// This option cannot compress nonzero long-lived age populations.
    pub fn advance_compact_exact_zeros(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
    ) -> Result<(AgeStep, RetardedDiagnostics), NetworkError> {
        let (mut out, mut diagnostics) = self.advance_with_diagnostics(initial, conf, dt)?;
        let previous = out.state.cohorts.len();
        out.state.cohorts.retain(|c| c.n_comoving_m3 != 0.0);
        diagnostics.retired_exact_zero_cohorts = previous - out.state.cohorts.len();
        Ok((out, diagnostics))
    }
}

/// Independent *manufactured scalar* retarded Duhamel reference. It exercises
/// the same positive birth quadrature and piecewise-constant optical-depth
/// approximation without importing external chemistry or claiming native EoR.
#[derive(Clone, Copy, Debug)]
pub struct ScalarDuhamelStep {
    pub emitted: f64,
    pub survivors: f64,
    pub absorbed: f64,
}
pub fn scalar_duhamel<F, G>(
    t0: f64,
    dt: f64,
    initial_n: f64,
    birth_gl: usize,
    substeps: usize,
    source: F,
    opacity: G,
) -> Result<ScalarDuhamelStep, NetworkError>
where
    F: Fn(f64) -> f64,
    G: Fn(f64) -> f64,
{
    if !t0.is_finite()
        || !dt.is_finite()
        || dt <= 0.
        || !initial_n.is_finite()
        || initial_n < 0.
        || ![1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024].contains(&substeps)
    {
        return Err(NetworkError::InvalidInput);
    }
    let t1 = t0 + dt;
    if !t1.is_finite() || t1 <= t0 {
        return Err(NetworkError::NoForwardProgress);
    }
    let mut born = vec![(t0, initial_n)];
    let mut emitted = 0.;
    for (x, w) in gauss_birth_nodes(birth_gl)? {
        let tb = t0 + dt * x;
        let j = source(tb);
        if !j.is_finite() || j < 0. {
            return Err(NetworkError::InvalidInput);
        }
        let b = j * dt * w;
        if !b.is_finite() {
            return Err(NetworkError::NonFinite);
        }
        emitted += b;
        born.push((tb, b));
    }
    let mut survivors = 0.;
    for (ta, n) in born {
        let mut nleft = n;
        for step in 0..substeps {
            let a = ta + (t1 - ta) * (step as f64) / (substeps as f64);
            let b = ta + (t1 - ta) * ((step + 1) as f64) / (substeps as f64);
            let k = opacity(0.5 * (a + b));
            if !k.is_finite() || k < 0. {
                return Err(NetworkError::InvalidInput);
            }
            nleft *= photon_slab(k * (b - a))?.old_surviving;
        }
        survivors += nleft;
    }
    let absorbed = initial_n + emitted - survivors;
    if !survivors.is_finite() || !absorbed.is_finite() || absorbed < -1e-13 * (initial_n + emitted)
    {
        return Err(NetworkError::NonFinite);
    }
    Ok(ScalarDuhamelStep {
        emitted,
        survivors,
        absorbed,
    })
}
