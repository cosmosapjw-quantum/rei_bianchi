//! Read-only evidence for an accepted native AP corrector.
//!
//! The hook receives the actual corrector rate gas and actual emitted cohort
//! slice. Replayed source/rule calculations are checked against every actual
//! birth clock, label and count. They never replace a physics value. The half-
//! step predictor is excluded. Reference certificates use constant source and
//! opacity; native source weights and native retained weights remain separate.
//! A monitor error is returned separately after a successful physics step.

use crate::ap_midpoint::{ApMidpointBridge, BirthMode};
use crate::bianchi_i::GeometrySnapshot;
use crate::birth_age_certificate::{BirthAgeCertificate, compare_nodes};
use crate::bound_source_age::{AgeHistory, AgeStep};
use crate::full_network::{NetworkConfig, NetworkError};
use crate::isotope_state::IsotopeSpecies;
use crate::mixture_eos::MixtureState;
use crate::positive_spectral::expand_births;
use crate::reflection_pool::RetardedDiagnostics;
use crate::source_age::Cohort;
use std::collections::HashMap;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct MonitorControls {
    /// External accepted-step identifier. The fixed-step driver uses 1..=Nt.
    pub step_id: usize,
    /// A diagnostic allocation quota, never a photon cutoff or solver control.
    pub max_newborn_records: usize,
}

impl Default for MonitorControls {
    fn default() -> Self {
        Self {
            step_id: 1,
            max_newborn_records: 1_000_000,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum MonitorMode {
    Off,
    On(MonitorControls),
}

#[derive(Clone, Debug, PartialEq)]
pub enum MonitorError {
    InvalidControls,
    UnsupportedBirthMode,
    RecordQuota { requested: usize, limit: usize },
    Reference(NetworkError),
    InputMismatch(&'static str),
    NonFinite(&'static str),
    NegativePopulation,
    IncompleteCapture,
}

impl From<NetworkError> for MonitorError {
    fn from(value: NetworkError) -> Self {
        Self::Reference(value)
    }
}

#[derive(Debug)]
pub struct MonitoredStep {
    pub step: AgeStep,
    pub diagnostics: RetardedDiagnostics,
    /// None means monitor OFF; Some(Err) leaves successful physics intact.
    pub monitor: Option<Result<StepMonitor, MonitorError>>,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct PopulationMoments {
    pub count: f64,
    pub age_sum_s: f64,
    pub age2_sum_s2: f64,
    pub positive_cohorts: usize,
    pub zero_cohorts: usize,
    pub first_moment_underflows: usize,
    pub second_moment_underflows: usize,
}

/// Raw native moments; an empty/zero measure has zero raw moments and no mean.
/// An exact zero in f64 is reported as zero, without inventing its cause.
pub fn population_moments(
    values: impl IntoIterator<Item = (f64, f64)>,
) -> Result<PopulationMoments, MonitorError> {
    let mut out = PopulationMoments::default();
    for (count, age) in values {
        if !count.is_finite() || !age.is_finite() || age < 0.0 {
            return Err(MonitorError::NonFinite("population_or_age"));
        }
        if count < 0.0 {
            return Err(MonitorError::NegativePopulation);
        }
        if count == 0.0 {
            out.zero_cohorts += 1;
        } else {
            out.positive_cohorts += 1;
        }
        let first = count * age;
        let second = count * age.powi(2);
        if count > 0.0 && age > 0.0 {
            out.first_moment_underflows += usize::from(first == 0.0);
            out.second_moment_underflows += usize::from(second == 0.0);
        }
        out.count += count;
        out.age_sum_s += first;
        out.age2_sum_s2 += second;
    }
    if ![out.count, out.age_sum_s, out.age2_sum_s2]
        .iter()
        .all(|x| x.is_finite())
    {
        return Err(MonitorError::NonFinite("population_moments"));
    }
    Ok(out)
}

#[derive(Clone, Debug)]
pub struct PanelRecord {
    pub panel_id: usize,
    pub left: f64,
    pub right: f64,
    pub width_from_weights: f64,
    pub width_bits_match: bool,
    pub nominal_width_s: f64,
    pub optical_width: f64,
    pub represented_birth_left_s: f64,
    pub represented_birth_right_s: f64,
    pub represented_width_s: f64,
    pub represented_width_defect_s: f64,
    pub physical_bound_excess_s: f64,
    pub optical_bound_excess: f64,
    pub exact_survival_per_unit_born: f64,
    pub reference_underflow: bool,
    pub local_reference: BirthAgeCertificate,
}

/// Reconstruct the original recurrence, verifying every actual rule pair.
/// Bounds are real-arithmetic statements; exported f64 excesses expose rounding.
pub fn rule_panels(
    tau: f64,
    refinement: usize,
    nodes: &[(f64, f64)],
    t0: f64,
    dt: f64,
) -> Result<Vec<PanelRecord>, MonitorError> {
    if !tau.is_finite()
        || tau < 0.0
        || !t0.is_finite()
        || !dt.is_finite()
        || dt <= 0.0
        || ![1, 2, 4, 8, 16].contains(&refinement)
        || nodes.is_empty()
        || !nodes.len().is_multiple_of(2)
    {
        return Err(MonitorError::InputMismatch("panel_inputs"));
    }
    let t1 = t0 + dt;
    if !t1.is_finite() || t1 <= t0 {
        return Err(MonitorError::InputMismatch("panel_clock"));
    }
    let r = refinement as f64;
    let mut left = 0.0;
    let mut out = Vec::new();
    for (panel_id, pair) in nodes.chunks_exact(2).enumerate() {
        let width_target = if tau <= 1.0 {
            1.0 / r
        } else {
            (1.0 / tau + left).min(1.0) / r
        };
        let right = (left + width_target).min(1.0);
        let width = right - left;
        let weight_width = pair[0].1 * 2.0;
        if right <= left
            || pair[0].1.to_bits() != pair[1].1.to_bits()
            || weight_width.to_bits() != width.to_bits()
            || !pair
                .iter()
                .all(|&(x, w)| x.is_finite() && w.is_finite() && x > left && x < right && w > 0.0)
            || pair[0].0 >= pair[1].0
        {
            return Err(MonitorError::InputMismatch("actual_rule_panel"));
        }
        let theta = tau * width;
        let local_nodes = [
            ((pair[0].0 - left) / width, pair[0].1 / width),
            ((pair[1].0 - left) / width, pair[1].1 / width),
        ];
        let local_reference = compare_nodes(theta, 1.0, &local_nodes)?;
        let survival = (-tau * left).exp() * width * crate::fitted_birth::phi(theta)?;
        let birth_left = t1 - dt * right;
        let birth_right = t1 - dt * left;
        let nominal = dt * width;
        let represented = birth_right - birth_left;
        out.push(PanelRecord {
            panel_id,
            left,
            right,
            width_from_weights: weight_width,
            width_bits_match: true,
            nominal_width_s: nominal,
            optical_width: theta,
            represented_birth_left_s: birth_left,
            represented_birth_right_s: birth_right,
            represented_width_s: represented,
            represented_width_defect_s: represented - nominal,
            physical_bound_excess_s: (nominal - dt / r).max(0.0),
            optical_bound_excess: (theta - (1.0 + tau * left) / r).max(0.0),
            exact_survival_per_unit_born: survival,
            reference_underflow: survival == 0.0,
            local_reference,
        });
        left = right;
    }
    if left != 1.0 {
        return Err(MonitorError::InputMismatch("incomplete_panel_cover"));
    }
    Ok(out)
}

#[derive(Clone, Debug)]
pub struct RuleRecord {
    pub rule_id: usize,
    pub energy_ev: f64,
    pub rates_per_s: [f64; 4],
    pub tau: f64,
    pub refinement: usize,
    pub nodes: Vec<(f64, f64)>,
    pub panels: Vec<PanelRecord>,
    /// Unit-born constant-j, constant-kappa reference. This is not native error.
    pub frozen_kernel_reference: BirthAgeCertificate,
}

#[derive(Clone, Debug)]
pub struct TemplateRecord {
    pub template_id: usize,
    pub rule_id: usize,
    pub spectral_index: usize,
    pub angular_index: usize,
    pub energy_ev: f64,
    pub direction: [f64; 3],
    pub midpoint_rate_com3_s: f64,
    pub constant_j_born_com3: f64,
    pub first_birth_row: usize,
    pub birth_count: usize,
    pub native_born_com3: f64,
    pub native_after_photo: PopulationMoments,
    pub native_accepted: PopulationMoments,
    /// Actual source weights and represented clocks, propagated with the
    /// frozen selector opacity. Discrepancy is not a pure quadrature error.
    pub native_source_frozen_reference: BirthAgeCertificate,
}

#[derive(Clone, Debug)]
pub struct BirthRecord {
    /// Persistent append index in a noncompact native history.
    pub cohort_index: usize,
    pub template_id: usize,
    pub rule_id: usize,
    pub node_id: usize,
    pub target_age: f64,
    pub emission_weight: f64,
    pub clock_age: f64,
    pub clock_age_defect: f64,
    pub clock_age_defect_s: f64,
    pub source_amplitude_ratio: f64,
    pub born_count_underflow: bool,
    pub frozen_source_survivor_com3: f64,
    pub frozen_source_underflow: bool,
    pub birth: Cohort,
    pub killing_ev_scale: [f64; 3],
    pub after_photo_com3: Option<f64>,
    pub accepted_com3: Option<f64>,
    pub end_energy_ev: Option<f64>,
    pub end_direction: Option<[f64; 3]>,
}

#[derive(Clone, Debug)]
pub struct AcceptedInventory {
    pub populations_m3: [f64; 13],
    pub thermal_j_m3: f64,
    pub binding_j_m3: f64,
    pub escaped_j_m3: f64,
    pub cmb_reservoir_j_m3: f64,
    pub source_count_com3: f64,
    pub source_energy_j_com3: f64,
    pub absorbed_count_com3: f64,
    pub geometry_work_j_com3: f64,
    pub photons: PopulationMoments,
}

#[derive(Clone, Debug)]
pub struct StepMonitor {
    pub step_id: usize,
    pub t0: f64,
    pub tm: f64,
    pub t1: f64,
    pub dt: f64,
    pub prior_cohorts: usize,
    pub rate_gas: MixtureState,
    pub midpoint_geometry: GeometrySnapshot,
    pub end_geometry: GeometrySnapshot,
    pub rules: Vec<RuleRecord>,
    pub templates: Vec<TemplateRecord>,
    pub births: Vec<BirthRecord>,
    pub accepted: Option<AcceptedInventory>,
}

fn amplitude(bridge: &ApMidpointBridge, geometry: &GeometrySnapshot) -> Result<f64, MonitorError> {
    let volume = geometry
        .volume_factor()
        .map_err(|_| MonitorError::InputMismatch("source_volume"))?;
    let z = 1.0 / volume.cbrt() - 1.0;
    let source = bridge
        .0
        .source
        .at_redshift(z)
        .map_err(|_| MonitorError::InputMismatch("source_redshift"))?;
    let value = source.proper_photons_cm3_s * 1e6 * volume;
    if !value.is_finite() || value <= 0.0 {
        return Err(MonitorError::NonFinite("source_amplitude"));
    }
    Ok(value)
}

fn same_identity(a: &Cohort, b: &Cohort) -> bool {
    a.birth_time_s.to_bits() == b.birth_time_s.to_bits()
        && a.energy_at_birth_ev.to_bits() == b.energy_at_birth_ev.to_bits()
        && a.spectral_index == b.spectral_index
        && a.angular_index == b.angular_index
        && a.direction_at_birth.map(f64::to_bits) == b.direction_at_birth.map(f64::to_bits)
        && a.birth_geometry.scale_factors.map(f64::to_bits)
            == b.birth_geometry.scale_factors.map(f64::to_bits)
        && a.birth_geometry.hubble_per_s.map(f64::to_bits)
            == b.birth_geometry.hubble_per_s.map(f64::to_bits)
}

/// Internal observer. Its failures are stored, never propagated to the solver.
pub(crate) struct Capture {
    controls: MonitorControls,
    data: Option<StepMonitor>,
    error: Option<MonitorError>,
}

impl Capture {
    pub(crate) fn new(controls: MonitorControls) -> Self {
        Self {
            controls,
            data: None,
            error: None,
        }
    }

    pub(crate) fn finish(self) -> Result<StepMonitor, MonitorError> {
        if let Some(error) = self.error {
            return Err(error);
        }
        self.data
            .filter(|data| data.accepted.is_some())
            .ok_or(MonitorError::IncompleteCapture)
    }

    #[allow(clippy::too_many_arguments)]
    pub(crate) fn observe_births(
        &mut self,
        bridge: &ApMidpointBridge,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
        rate_gas: &MixtureState,
        births: &[Cohort],
        midpoint_geometry: &GeometrySnapshot,
        end_geometry: &GeometrySnapshot,
    ) {
        if self.error.is_some() {
            return;
        }
        let result = build_birth_capture(
            self.controls,
            bridge,
            initial,
            conf,
            dt,
            rate_gas,
            births,
            midpoint_geometry,
            end_geometry,
        );
        match result {
            Ok(data) => self.data = Some(data),
            Err(error) => self.error = Some(error),
        }
    }

    pub(crate) fn observe_after_photo(&mut self, cohorts: &[Cohort]) {
        if self.error.is_some() {
            return;
        }
        if let Err(error) = self.fill_weights(cohorts, false) {
            self.error = Some(error);
        }
    }

    fn fill_weights(&mut self, cohorts: &[Cohort], accepted: bool) -> Result<(), MonitorError> {
        let data = self.data.as_mut().ok_or(MonitorError::IncompleteCapture)?;
        if cohorts.len() != data.prior_cohorts + data.births.len() {
            return Err(MonitorError::InputMismatch("cohort_cardinality"));
        }
        for record in &mut data.births {
            let actual = &cohorts[record.cohort_index];
            if !same_identity(actual, &record.birth) {
                return Err(MonitorError::InputMismatch("retained_cohort_identity"));
            }
            if !actual.n_comoving_m3.is_finite() {
                return Err(MonitorError::NonFinite("retained_population"));
            }
            if actual.n_comoving_m3 < 0.0 {
                return Err(MonitorError::NegativePopulation);
            }
            if accepted {
                if record.after_photo_com3.map(f64::to_bits) != Some(actual.n_comoving_m3.to_bits())
                {
                    return Err(MonitorError::InputMismatch("post_photo_population_changed"));
                }
                record.accepted_com3 = Some(actual.n_comoving_m3);
                let ray = actual.ray_at(&data.end_geometry)?;
                record.end_energy_ev = Some(ray.energy_ev);
                record.end_direction = Some(ray.direction);
            } else {
                record.after_photo_com3 = Some(actual.n_comoving_m3);
            }
        }
        for template in &mut data.templates {
            let slice = &data.births
                [template.first_birth_row..template.first_birth_row + template.birth_count];
            let values = slice.iter().map(|record| {
                (
                    if accepted {
                        record.accepted_com3.unwrap_or(f64::NAN)
                    } else {
                        record.after_photo_com3.unwrap_or(f64::NAN)
                    },
                    data.t1 - record.birth.birth_time_s,
                )
            });
            let moments = population_moments(values)?;
            if accepted {
                template.native_accepted = moments;
            } else {
                template.native_after_photo = moments;
            }
        }
        Ok(())
    }

    pub(crate) fn observe_accepted(&mut self, state: &AgeHistory, conf: &NetworkConfig) {
        if self.error.is_some() {
            return;
        }
        if let Err(error) = self.capture_accepted(state, conf) {
            self.error = Some(error);
        }
    }

    fn capture_accepted(
        &mut self,
        state: &AgeHistory,
        conf: &NetworkConfig,
    ) -> Result<(), MonitorError> {
        self.fill_weights(&state.cohorts, true)?;
        let data = self.data.as_mut().ok_or(MonitorError::IncompleteCapture)?;
        if state.time_s.to_bits() != data.t1.to_bits() {
            return Err(MonitorError::InputMismatch("accepted_clock"));
        }
        let mut populations = [0.0; 13];
        for species in IsotopeSpecies::ALL {
            let value = state.full.gas.nuclei.density_m3(species);
            if !value.is_finite() {
                return Err(MonitorError::NonFinite("accepted_population"));
            }
            if value < 0.0 {
                return Err(MonitorError::NegativePopulation);
            }
            populations[species as usize] = value;
        }
        data.accepted = Some(AcceptedInventory {
            populations_m3: populations,
            thermal_j_m3: state.full.gas.thermal_j_m3,
            binding_j_m3: state.full.binding_j_m3(conf),
            escaped_j_m3: state.full.escaped_j_m3,
            cmb_reservoir_j_m3: state.full.cmb_reservoir_j_m3,
            source_count_com3: state.source_injected_count_com3,
            source_energy_j_com3: state.source_injected_energy_j_com3,
            absorbed_count_com3: state.photon_absorbed_count_com3,
            geometry_work_j_com3: state.geometry_work_j_com3,
            photons: population_moments(
                state
                    .cohorts
                    .iter()
                    .map(|co| (co.n_comoving_m3, state.time_s - co.birth_time_s)),
            )?,
        });
        Ok(())
    }
}

#[allow(clippy::too_many_arguments)]
fn build_birth_capture(
    controls: MonitorControls,
    bridge: &ApMidpointBridge,
    initial: &AgeHistory,
    conf: &NetworkConfig,
    dt: f64,
    rate_gas: &MixtureState,
    births: &[Cohort],
    midpoint_geometry: &GeometrySnapshot,
    end_geometry: &GeometrySnapshot,
) -> Result<StepMonitor, MonitorError> {
    if controls.step_id == 0 {
        return Err(MonitorError::InvalidControls);
    }
    if births.len() > controls.max_newborn_records {
        return Err(MonitorError::RecordQuota {
            requested: births.len(),
            limit: controls.max_newborn_records,
        });
    }
    let BirthMode::Fitted { refinement } = bridge.4 else {
        return Err(MonitorError::UnsupportedBirthMode);
    };
    let t0 = initial.time_s;
    let tm = t0 + dt / 2.0;
    let t1 = t0 + dt;
    let templates = expand_births(
        &bridge.0.source,
        &bridge.0.source_births(tm, 1.0)?,
        conf.deuterium.chi_d_ev(),
        bridge.1.spectrum,
    )?;
    let mid_amplitude = amplitude(bridge, midpoint_geometry)?;
    let mut out = StepMonitor {
        step_id: controls.step_id,
        t0,
        tm,
        t1,
        dt,
        prior_cohorts: initial.cohorts.len(),
        rate_gas: *rate_gas,
        midpoint_geometry: *midpoint_geometry,
        end_geometry: *end_geometry,
        rules: Vec::new(),
        templates: Vec::new(),
        births: Vec::with_capacity(births.len()),
        accepted: None,
    };
    let mut rule_ids = HashMap::new();
    let mut cursor = 0;
    for (template_id, template) in templates.iter().enumerate() {
        let energy_bits = template.energy_at_birth_ev.to_bits();
        let rule_id = match rule_ids.get(&energy_bits) {
            Some(&index) => index,
            None => {
                let rates = bridge.opacity_channels(template.energy_at_birth_ev, rate_gas, conf)?;
                let tau = rates.iter().sum::<f64>() * dt;
                let nodes = crate::fitted_birth::rule(tau, refinement)?;
                let index = out.rules.len();
                let panels = rule_panels(tau, refinement, &nodes, t0, dt)?;
                let reference = compare_nodes(tau, 1.0, &nodes)?;
                out.rules.push(RuleRecord {
                    rule_id: index,
                    energy_ev: template.energy_at_birth_ev,
                    rates_per_s: rates,
                    tau,
                    refinement,
                    nodes,
                    panels,
                    frozen_kernel_reference: reference,
                });
                rule_ids.insert(energy_bits, index);
                index
            }
        };
        let rule = &out.rules[rule_id];
        let constant_born = template.n_comoving_m3 * dt;
        let first = cursor;
        let mut source_nodes = Vec::with_capacity(rule.nodes.len());
        let mut native_born = 0.0;
        for (node_id, &(target_age, weight)) in rule.nodes.iter().enumerate() {
            let actual = births
                .get(cursor)
                .ok_or(MonitorError::InputMismatch("missing_actual_birth"))?;
            let target_birth = t1 - dt * target_age;
            if actual.birth_time_s.to_bits() != target_birth.to_bits()
                || actual.energy_at_birth_ev.to_bits() != energy_bits
                || actual.spectral_index != template.spectral_index
                || actual.angular_index != template.angular_index
                || actual.direction_at_birth.map(f64::to_bits)
                    != template.direction_at_birth.map(f64::to_bits)
            {
                return Err(MonitorError::InputMismatch("actual_birth_rule_join"));
            }
            let ratio = amplitude(bridge, &actual.birth_geometry)? / mid_amplitude;
            let expected_count = template.n_comoving_m3 * dt * weight * ratio;
            if actual.n_comoving_m3.to_bits() != expected_count.to_bits() {
                return Err(MonitorError::InputMismatch("actual_birth_source_weight"));
            }
            let age_s = t1 - actual.birth_time_s;
            let clock_age = age_s / dt;
            if !clock_age.is_finite() || !(0.0..=1.0).contains(&clock_age) {
                return Err(MonitorError::InputMismatch("represented_age_support"));
            }
            let kappa = rule.rates_per_s.iter().sum::<f64>();
            let native_source_survivor = actual.n_comoving_m3 * (-kappa * age_s).exp();
            let birth_ray = crate::bianchi_i::CharacteristicRay::new(
                actual.energy_at_birth_ev,
                actual.direction_at_birth,
                0.0,
            )
            .map_err(|_| MonitorError::InputMismatch("birth_ray_normalization"))?;
            let killing = std::array::from_fn(|i| {
                actual.birth_geometry.scale_factors[i]
                    * actual.energy_at_birth_ev
                    * birth_ray.direction[i]
            });
            source_nodes.push((
                clock_age,
                if constant_born == 0.0 {
                    0.0
                } else {
                    actual.n_comoving_m3 / constant_born
                },
            ));
            native_born += actual.n_comoving_m3;
            out.births.push(BirthRecord {
                cohort_index: initial.cohorts.len() + cursor,
                template_id,
                rule_id,
                node_id,
                target_age,
                emission_weight: weight,
                clock_age,
                clock_age_defect: clock_age - target_age,
                clock_age_defect_s: age_s - dt * target_age,
                source_amplitude_ratio: ratio,
                born_count_underflow: template.n_comoving_m3 > 0.0 && actual.n_comoving_m3 == 0.0,
                frozen_source_survivor_com3: native_source_survivor,
                frozen_source_underflow: actual.n_comoving_m3 > 0.0
                    && native_source_survivor == 0.0,
                birth: actual.clone(),
                killing_ev_scale: killing,
                after_photo_com3: None,
                accepted_com3: None,
                end_energy_ev: None,
                end_direction: None,
            });
            cursor += 1;
        }
        out.templates.push(TemplateRecord {
            template_id,
            rule_id,
            spectral_index: template.spectral_index,
            angular_index: template.angular_index,
            energy_ev: template.energy_at_birth_ev,
            direction: template.direction_at_birth,
            midpoint_rate_com3_s: template.n_comoving_m3,
            constant_j_born_com3: constant_born,
            first_birth_row: first,
            birth_count: cursor - first,
            native_born_com3: native_born,
            native_after_photo: PopulationMoments::default(),
            native_accepted: PopulationMoments::default(),
            native_source_frozen_reference: compare_nodes(rule.tau, constant_born, &source_nodes)?,
        });
    }
    if cursor != births.len() {
        return Err(MonitorError::InputMismatch("unmatched_actual_birth"));
    }
    Ok(out)
}
