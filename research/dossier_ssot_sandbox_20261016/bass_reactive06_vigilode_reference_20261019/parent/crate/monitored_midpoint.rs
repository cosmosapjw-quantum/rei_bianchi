//! BASS-REACTIVE-05 generated read-only monitor over the BR03 corrector.
//! Generated with exact reversible edits; physics bodies remain unchanged.
//! BASS-REACTIVE-03 opt-in exponentially fitted birth-age corrector.
//! Derived additively from immutable bound_midpoint.rs; all transport, chemistry,
//! and CX half-flow bodies retain the original formulas and operation order.
//! The first-order predictor uses this same fitted birth rule; its native
//! drift, photo and full_network::step sequencing matches bound_reflection.
//! BirthMode::Off dispatches directly to the original implementation.
//! The original S6 reflection kernel and full_network are left byte unchanged.
//! The predicted half-step is used ONLY to evaluate opacity and gas rates;
//! its photon births, absorptions, thermal changes and ledgers are discarded.
//! Correction updates the original state once. Explicit gas midpoint is not
//! unconditionally positive or stiffly stable: all states are checked/rejected.
use crate::axbi_sources::SOURCE_ID;
use crate::bass_reactive::split_by_thresholds_from_energies;
use crate::bianchi_i::GeometrySnapshot;
use crate::bound_source_age::{AgeHistory, AgeStep, SourceAgeBridge};
use crate::deuterium_atomic::{DChargeExchange, d_atomic_rhs};
use crate::deuterium_thermal_coupling::CxOwnership;
use crate::full_network::{self, EV_J, EventBudget, FullState, NetworkConfig, NetworkError};
use crate::isotope_state::{IsotopeNumberState, IsotopeSpecies as S};
use crate::midpoint_gas;
use crate::mixture_eos::MixtureState;
use crate::native_birth_monitor::{Capture, MonitorError, MonitorMode, MonitoredStep};
use crate::positive_birth_clock::photon_slab;
use crate::positive_spectral::expand_births;
use std::collections::{HashMap, VecDeque};

use crate::retarded_transport::RetardedControls;

pub use crate::reflection_pool::RetardedDiagnostics;

#[derive(Clone, Copy, Debug)]
struct BaseSlab {
    a: f64,
    b: f64,
    ga: GeometrySnapshot,
    gb: GeometrySnapshot,
    gm: GeometrySnapshot,
    vmid: f64,
}

pub use crate::reflection_pool::PoolLimits;

/// All scalar-kernel dependencies that vary between cohorts within ONE step.
/// No rounded/gauge-approximate key. Magnitudes identify sign reflections only.
/// Photon weight is included to reproduce the same floating-point operations.
#[derive(Clone, Copy, Debug, Hash, PartialEq, Eq)]
pub struct ScalarSignature([u64; 13]);
pub fn scalar_signature(
    co: &crate::source_age::Cohort,
    start: f64,
) -> Result<ScalarSignature, NetworkError> {
    if !start.is_finite() || !co.birth_time_s.is_finite() {
        return Err(NetworkError::NonFinite);
    }
    // Retain original owner validation; never reuse an invalid input.
    co.ray_at(&co.birth_geometry)?;
    let mut k = [0u64; 13];
    k[0] = start.to_bits();
    k[1] = co.birth_time_s.to_bits();
    k[2] = co.energy_at_birth_ev.to_bits();
    k[3] = co.n_comoving_m3.to_bits();
    for j in 0..3 {
        k[4 + j] = co.direction_at_birth[j].abs().to_bits();
        k[7 + j] = co.birth_geometry.scale_factors[j].to_bits();
        k[10 + j] = co.birth_geometry.hubble_per_s[j].to_bits();
    }
    Ok(ScalarSignature(k))
}

#[derive(Clone, Debug, Default)]
struct SlabRecord {
    events: [f64; 4],
    heat_j: [f64; 4],
    photon_energy_j: f64,
    geometric_work_j: f64,
    absorbing: bool,
}
#[derive(Clone, Debug)]
struct ScalarTrace {
    slabs: Vec<SlabRecord>,
    surviving: f64,
    geometric_work_j: f64,
    crossings: usize,
}

/// Fitted controls only numerical birth-age quadrature. No physical source scaling.
pub use crate::ap_midpoint::BirthMode;
pub use crate::midpoint_coupled::Centering;

pub struct MonitoredMidpointBridge(
    pub SourceAgeBridge,
    pub RetardedControls,
    pub PoolLimits,
    pub Centering,
    pub BirthMode,
);
fn allowed_t(t: f64) -> bool {
    t.is_finite()
        && (crate::deuterium_charge_exchange::Savin2002::MINIMUM_K
            ..=crate::deuterium_charge_exchange::Savin2002::MAXIMUM_K)
            .contains(&t)
}
impl MonitoredMidpointBridge {
    /// Read-only adapter to immutable projections and the exact legacy dispatcher.
    pub fn original(&self) -> crate::bound_midpoint::MidpointBridge {
        crate::bound_midpoint::MidpointBridge(self.0.clone(), self.1, self.2, self.3)
    }

    pub fn from_original(bridge: crate::bound_midpoint::MidpointBridge, mode: BirthMode) -> Self {
        Self(bridge.0, bridge.1, bridge.2, bridge.3, mode)
    }

    /// Exact source-native competing absorption rates in s^-1, using physical
    /// midpoint gas densities. This is a public audit seam, not another owner.
    pub fn opacity_channels(
        &self,
        energy_ev: f64,
        gas: &MixtureState,
        conf: &NetworkConfig,
    ) -> Result<[f64; 4], NetworkError> {
        gas.eos()?;
        let rates = self.0.opacity_channels(energy_ev, gas, conf)?;
        if rates.iter().any(|x| !x.is_finite() || *x < 0.0) {
            return Err(NetworkError::InvalidInput);
        }
        Ok(rates)
    }

    fn validate_source(&self) -> Result<(), NetworkError> {
        let source = &self.0.source;
        if source.spectral_cells.is_empty() || source.angular_cells.is_empty() {
            return Err(NetworkError::InvalidInput);
        }
        for c in &source.spectral_cells {
            if ![c.lower_ev, c.upper_ev, c.energy_ev, c.photon_fraction]
                .iter()
                .all(|x| x.is_finite())
                || c.lower_ev <= 0.0
                || c.upper_ev <= c.lower_ev
                || c.energy_ev < c.lower_ev
                || c.energy_ev > c.upper_ev
                || c.photon_fraction <= 0.0
            {
                return Err(NetworkError::InvalidInput);
            }
        }
        for a in &source.angular_cells {
            if !a.mu.is_finite()
                || !a.count_fraction.is_finite()
                || a.mu.abs() > 1.0
                || a.count_fraction <= 0.0
            {
                return Err(NetworkError::InvalidInput);
            }
        }
        let spectral: f64 = source
            .spectral_cells
            .iter()
            .map(|x| x.photon_fraction)
            .sum();
        let angular: f64 = source.angular_cells.iter().map(|x| x.count_fraction).sum();
        if !spectral.is_finite()
            || !angular.is_finite()
            || (spectral - 1.0).abs() > 1e-12
            || (angular - 1.0).abs() > 1e-12
        {
            return Err(NetworkError::InvalidInput);
        }
        Ok(())
    }

    /// Source-native comoving emission amplitude, photons m^-3 s^-1.
    fn emission_amplitude(&self, geometry: &GeometrySnapshot) -> Result<f64, NetworkError> {
        let volume = geometry
            .volume_factor()
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        let z = 1.0 / volume.cbrt() - 1.0;
        let source = self
            .0
            .source
            .at_redshift(z)
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        let amplitude = source.proper_photons_cm3_s * 1e6 * volume;
        if !amplitude.is_finite() || amplitude <= 0.0 {
            return Err(NetworkError::NonFinite);
        }
        Ok(amplitude)
    }

    pub fn initial(
        &self,
        full: FullState,
        conf: &NetworkConfig,
        t: f64,
    ) -> Result<AgeHistory, NetworkError> {
        self.0.initial(full, conf, t)
    }

    /// Fit birth ages separately for every native spectral energy. A cohort is
    /// evaluated at its own physical birth time and retains spectral/angular
    /// labels, source energy, direction and exact donor birth geometry. Opacity
    /// at emitted energy in the predicted midpoint gas selects the rule only;
    /// the unchanged transport below evaluates actual Killing energies E(t).
    pub fn emit_births(
        &self,
        t0: f64,
        dt: f64,
        conf: &NetworkConfig,
        rate_gas: &MixtureState,
    ) -> Result<Vec<crate::source_age::Cohort>, NetworkError> {
        if self.4 == BirthMode::Off {
            return self.original().emit_births(t0, dt, conf);
        }
        if !t0.is_finite() || !dt.is_finite() || dt <= 0.0 || conf.photon_source != SOURCE_ID {
            return Err(NetworkError::InvalidInput);
        }
        let BirthMode::Fitted { refinement } = self.4 else {
            unreachable!()
        };
        // Validate the rule control even if a future source batch is empty.
        crate::fitted_birth::rule(0.0, refinement)?;
        self.validate_source()?;
        rate_gas.eos()?;
        let t1 = t0 + dt;
        let tm = t0 + 0.5 * dt;
        if !t1.is_finite() || t1 <= tm || tm <= t0 {
            return Err(NetworkError::NoForwardProgress);
        }
        let gm = self.0.snapshot(tm)?;
        let midpoint_amplitude = self.emission_amplitude(&gm)?;
        let template = expand_births(
            &self.0.source,
            &self.0.source_births(tm, 1.0)?,
            conf.deuterium.chi_d_ev(),
            self.1.spectrum,
        )?;
        let mut births = Vec::new();
        let mut rules: HashMap<u64, Vec<(f64, f64)>> = HashMap::new();
        let mut geometry_rate: HashMap<u64, (GeometrySnapshot, f64)> = HashMap::new();
        for co in template {
            if !co.n_comoving_m3.is_finite() || co.n_comoving_m3 < 0.0 {
                return Err(NetworkError::InvalidInput);
            }
            let rule = match rules.entry(co.energy_at_birth_ev.to_bits()) {
                std::collections::hash_map::Entry::Occupied(entry) => entry.into_mut(),
                std::collections::hash_map::Entry::Vacant(entry) => {
                    let opacity: f64 = self
                        .opacity_channels(co.energy_at_birth_ev, rate_gas, conf)?
                        .iter()
                        .sum();
                    entry.insert(crate::fitted_birth::rule(opacity * dt, refinement)?)
                }
            };
            for &(age, weight) in rule.iter() {
                let tb = t1 - dt * age;
                // An unrepresentable physical birth clock is an execution
                // precision limit; never snap it to an arbitrary endpoint.
                if !tb.is_finite() || tb < t0 || tb >= t1 {
                    return Err(NetworkError::NoForwardProgress);
                }
                let (geometry, amplitude) = match geometry_rate.entry(tb.to_bits()) {
                    std::collections::hash_map::Entry::Occupied(entry) => *entry.get(),
                    std::collections::hash_map::Entry::Vacant(entry) => {
                        let geometry = self.0.snapshot(tb)?;
                        let amplitude = self.emission_amplitude(&geometry)?;
                        *entry.insert((geometry, amplitude))
                    }
                };
                let count = co.n_comoving_m3 * dt * weight * (amplitude / midpoint_amplitude);
                if !count.is_finite() || count < 0.0 {
                    return Err(NetworkError::NonFinite);
                }
                let mut born = co.clone();
                born.birth_time_s = tb;
                born.birth_geometry = geometry;
                born.n_comoving_m3 = count;
                births.push(born);
            }
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
        interval: (f64, f64),
        prior: usize,
        predicted_gas: Option<MixtureState>,
    ) -> Result<(EventBudget, RetardedDiagnostics), NetworkError> {
        let (t0, t1) = interval;
        let vm = gm
            .volume_factor()
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        let gas_mid = s.full.gas; // original state drifted to midpoint volume
        let rate_gas = predicted_gas.unwrap_or(gas_mid); // separate evaluation state
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
        let mut traces: HashMap<ScalarSignature, ScalarTrace> = HashMap::new();
        let mut trace_order: VecDeque<ScalarSignature> = VecDeque::new();
        let mut cached_segments = 0usize;
        let (
            mut computed_paths,
            mut reused_paths,
            mut peak_cached_traces,
            mut peak_cached_segments,
            mut trace_cache_evictions,
            mut replayed_segments,
        ) = (0usize, 0usize, 0usize, 0usize, 0usize, 0usize);
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
            let signature = scalar_signature(co, ta)?;
            if let Some(trace) = traces.get(&signature) {
                // Replay individual slab contributions in ORIGINAL order.
                // Do not pre-sum a ray or multiply an orbit weight.
                for rec in &trace.slabs {
                    geom_work_ind += rec.geometric_work_j;
                    if rec.absorbing {
                        for (sp, out) in delta_com.iter_mut().enumerate() {
                            *out += rec.events[sp];
                            thermal_com += rec.heat_j[sp];
                            if sp == 3 {
                                d_heat_com += rec.heat_j[sp];
                            }
                        }
                        photo_e_com += rec.photon_energy_j;
                    }
                }
                geom_work += trace.geometric_work_j;
                residuals.push(trace.surviving);
                threshold_crossings += trace.crossings;
                reused_paths += 1;
                replayed_segments += trace.slabs.len();
                continue;
            }
            computed_paths += 1;
            let crossings_before = threshold_crossings;
            let mut records = Vec::new();
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
                threshold_crossings += self.0.geometry.edge_count(
                    endpoint_energies.0,
                    endpoint_energies.1,
                    conf.deuterium.chi_d_ev(),
                    splits.len() - 2,
                );
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
                        let values = self.0.opacity_channels(en, &rate_gas, conf)?;
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
                    let mut rec = SlabRecord {
                        geometric_work_j: n * frac.new_surviving * (e_b - e_a) * EV_J,
                        absorbing: k > 0.,
                        ..SlabRecord::default()
                    };
                    geom_work_ind += rec.geometric_work_j;
                    if k > 0. {
                        absorption_energy_ev += absorbed * en;
                        for sp in 0..4 {
                            let a = absorbed * rates[sp] / k;
                            if a > 0. && en < chis[sp] {
                                return Err(NetworkError::PhysicsLedger);
                            }
                            rec.events[sp] = a;
                            rec.heat_j[sp] = a * (en - chis[sp]) * EV_J;
                            delta_com[sp] += a;
                            thermal_com += rec.heat_j[sp];
                            if sp == 3 {
                                d_heat_com += rec.heat_j[sp];
                            }
                        }
                        rec.photon_energy_j = absorbed * en * EV_J;
                        photo_e_com += rec.photon_energy_j;
                    }
                    n = remain;
                    records.push(rec);
                }
            }
            let g1 = self.0.snapshot(t1)?;
            let e1 = co.ray_at(&g1)?.energy_ev;
            let final_work = (n * e1 - initial_n * e_initial + absorption_energy_ev) * EV_J;
            geom_work += final_work;
            residuals.push(n);
            if self.2.max_entries > 0 && records.len() <= self.2.max_segments {
                while traces.len() >= self.2.max_entries
                    || cached_segments + records.len() > self.2.max_segments
                {
                    // Evict oldest one at a time, not an entire recent orbit.
                    // The cache is optional: eviction changes work, never data.
                    let oldest = trace_order.pop_front().ok_or(NetworkError::InvalidInput)?;
                    let removed = traces.remove(&oldest).ok_or(NetworkError::InvalidInput)?;
                    cached_segments -= removed.slabs.len();
                    trace_cache_evictions += 1;
                }
                cached_segments += records.len();
                trace_order.push_back(signature);
                traces.insert(
                    signature,
                    ScalarTrace {
                        slabs: records,
                        surviving: n,
                        geometric_work_j: final_work,
                        crossings: threshold_crossings - crossings_before,
                    },
                );
                peak_cached_traces = peak_cached_traces.max(traces.len());
                peak_cached_segments = peak_cached_segments.max(cached_segments);
            }
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
                computed_paths,
                reused_paths,
                peak_cached_traces,
                peak_cached_segments,
                trace_cache_evictions,
                replayed_segments,
                ..RetardedDiagnostics::default()
            },
        ))
    }

    /// No monitoring: dispatch directly to the unchanged parent AP implementation.
    pub fn advance_with_diagnostics(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
    ) -> Result<(AgeStep, RetardedDiagnostics), NetworkError> {
        self.parent().advance_with_diagnostics(initial, conf, dt)
    }

    pub fn from_parent(parent: crate::ap_midpoint::ApMidpointBridge) -> Self {
        Self(parent.0, parent.1, parent.2, parent.3, parent.4)
    }

    pub fn parent(&self) -> crate::ap_midpoint::ApMidpointBridge {
        crate::ap_midpoint::ApMidpointBridge(self.0.clone(), self.1, self.2, self.3, self.4)
    }

    /// Monitoring errors are diagnostics; they cannot turn accepted physics
    /// into a rejected step. Legacy birth mode is run by the original owner.
    pub fn advance_with_monitor(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
        mode: MonitorMode,
    ) -> Result<MonitoredStep, NetworkError> {
        let MonitorMode::On(controls) = mode else {
            let (step, diagnostics) = self.parent().advance_with_diagnostics(initial, conf, dt)?;
            return Ok(MonitoredStep {
                step,
                diagnostics,
                monitor: None,
            });
        };
        if self.4 == BirthMode::Off {
            let (step, diagnostics) = self.parent().advance_with_diagnostics(initial, conf, dt)?;
            return Ok(MonitoredStep {
                step,
                diagnostics,
                monitor: Some(Err(MonitorError::UnsupportedBirthMode)),
            });
        }
        let mut capture = Capture::new(controls);
        let (step, diagnostics) = self.advance_core(initial, conf, dt, true, Some(&mut capture))?;
        Ok(MonitoredStep {
            step,
            diagnostics,
            monitor: Some(capture.finish()),
        })
    }

    // With predict=false and OpacityOnly centering this is the original first-
    // order ReflectionPooledBridge sequence with fitted births. Its result is
    // temporary in the half-step predictor; no predictor ledger is committed.
    fn advance_core(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
        predict: bool,
        mut monitor: Option<&mut Capture>,
    ) -> Result<(AgeStep, RetardedDiagnostics), NetworkError> {
        initial.full.validate(conf)?;
        self.validate_source()?;
        for co in &initial.cohorts {
            if !co.n_comoving_m3.is_finite() {
                return Err(NetworkError::NonFinite);
            }
            if co.n_comoving_m3 < 0.0 {
                return Err(NetworkError::NegativePopulation);
            }
            if !co.birth_time_s.is_finite()
                || co.birth_time_s > initial.time_s
                || co.spectral_index >= self.0.source.spectral_cells.len()
                || co.angular_index >= self.0.source.angular_cells.len()
            {
                return Err(NetworkError::SourceMismatch);
            }
            self.0.geometry.validate_birth(co)?;
        }
        self.0.geometry.validate_history(initial)?;
        if conf.photon_source != SOURCE_ID || !conf.use_photo || !dt.is_finite() || dt <= 0. {
            return Err(NetworkError::SourceMismatch);
        }
        if self.3 == Centering::Legacy {
            return Err(NetworkError::InvalidInput);
        }
        if matches!(self.3, Centering::Joint | Centering::GasOnly)
            && conf.use_cx
            && conf.owner != CxOwnership::AtomicRhs
        {
            return Err(NetworkError::OwnershipConflict);
        }
        if self.3 == Centering::JointCxSplit
            && conf.use_cx
            && conf.owner != CxOwnership::ThermalSubstep
        {
            return Err(NetworkError::OwnershipConflict);
        }
        if self.2.max_entries > 4096 || self.2.max_segments > 262144 {
            return Err(NetworkError::InvalidInput);
        }
        RetardedControls::new(
            self.1.birth_gauss_nodes,
            self.1.opacity_substeps,
            self.1.spectrum,
        )?;
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
        // A consistent first-order h/2 predictor has O(h^2) midpoint-state error.
        // It includes the same source/geometry and all selected gas channels.
        // Its complete output is temporary: not one of its ledger entries is committed.
        let predicted = if predict
            && matches!(
                self.3,
                Centering::Joint | Centering::OpacityOnly | Centering::JointCxSplit
            ) {
            let mut pc = *conf;
            pc.owner = CxOwnership::ThermalSubstep;
            let first_order = Self(
                self.0.clone(),
                self.1,
                self.2,
                Centering::OpacityOnly,
                self.4,
            );
            Some(
                first_order
                    .advance_core(initial, &pc, 0.5 * dt, false, None)?
                    .0,
            )
        } else {
            None
        };
        let mut s = initial.clone();
        let (wph0, wgas0) = self.0.drift(&mut s, &g0, &gm)?;
        s.geometry_work_j_com3 -= wph0;
        // Symmetric native CX exposures surround the photon+non-CX corrector.
        let cx_first = if self.3 == Centering::JointCxSplit {
            let mut cc = *conf;
            cc.use_photo = false;
            let out = midpoint_gas::cx_flow(&s.full, &cc, 0.5 * dt)?;
            s.full = out.state;
            out.budget
        } else {
            EventBudget::default()
        };
        let rate_gas = predicted
            .as_ref()
            .map(|p| p.state.full.gas)
            .unwrap_or(s.full.gas);
        let births = self.emit_births(t0, dt, conf, &rate_gas)?;
        // BR05 read-only corrector hook; the predictor receives None.
        if let Some(observer) = monitor.as_deref_mut() {
            observer.observe_births(
                &self.parent(),
                initial,
                conf,
                dt,
                &rate_gas,
                &births,
                &gm,
                &g1,
            );
        }
        let n_birth = births.iter().map(|c| c.n_comoving_m3).sum::<f64>();
        let e_birth = births
            .iter()
            .map(|c| c.n_comoving_m3 * c.energy_at_birth_ev * EV_J)
            .sum::<f64>();
        s.source_injected_count_com3 += n_birth;
        s.source_injected_energy_j_com3 += e_birth;
        let prior = s.cohorts.len();
        s.cohorts.extend(births);
        let (photo, mut diag) = self.photo(
            &mut s,
            &gm,
            conf,
            (t0, t1),
            prior,
            predicted.as_ref().map(|p| p.state.full.gas),
        )?;
        if let Some(observer) = monitor.as_deref_mut() {
            observer.observe_after_photo(&s.cohorts);
        }
        s.full.photon_bins.clear();
        let mut local = *conf;
        local.use_photo = false;
        let chemistry = match self.3 {
            Centering::JointCxSplit => {
                local.use_cx = false;
                let p = &predicted
                    .as_ref()
                    .ok_or(NetworkError::InvalidInput)?
                    .state
                    .full;
                let rates = midpoint_gas::rhs(p, &local)?;
                midpoint_gas::apply(&s.full, &local, &rates, dt)?
            }
            Centering::Joint => {
                local.owner = CxOwnership::AtomicRhs;
                let p = &predicted
                    .as_ref()
                    .ok_or(NetworkError::InvalidInput)?
                    .state
                    .full;
                let rates = midpoint_gas::rhs(p, &local)?;
                midpoint_gas::apply(&s.full, &local, &rates, dt)?
            }
            Centering::GasOnly => {
                local.owner = CxOwnership::AtomicRhs;
                midpoint_gas::step(&s.full, &local, dt)?
            }
            Centering::OpacityOnly => {
                local.owner = CxOwnership::ThermalSubstep;
                full_network::step(&s.full, &local, dt)?
            }
            Centering::Legacy => unreachable!("delegated to original before mutation"),
        };
        let mut events = chemistry.budget;
        events.photo_events_m3 = photo.photo_events_m3;
        events.photo_energy_j_m3 = photo.photo_energy_j_m3;
        events.thermal_change_j_m3 += photo.thermal_change_j_m3;
        events.chemical_change_j_m3 += photo.chemical_change_j_m3;
        s.full = chemistry.state;
        if self.3 == Centering::JointCxSplit {
            let mut cc = *conf;
            cc.use_photo = false;
            let second = midpoint_gas::cx_flow(&s.full, &cc, 0.5 * dt)?;
            s.full = second.state;
            events =
                midpoint_gas::add_budget(midpoint_gas::add_budget(cx_first, events), second.budget);
        }
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
        if let Some(observer) = monitor {
            observer.observe_accepted(&s, conf);
        }
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
