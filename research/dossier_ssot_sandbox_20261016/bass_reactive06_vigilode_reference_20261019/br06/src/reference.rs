//! Positive survival/competition reference in optical depth.
use crate::{
    Error, Result,
    fixture::NativeFixture,
    quadrature::{PositiveGauss, gauss_age_nodes},
};
use rei_iso_couple_reference::{
    bass_reactive::split_by_thresholds_from_energies, full_network::EV_J, source_age::Cohort,
};
use std::{collections::HashMap, fs, io::Write, path::Path, time::Instant};

#[derive(Clone, Copy, Debug)]
pub struct PathSample {
    pub energy_ev: f64,
    pub direction: [f64; 3],
    /// Owner equation dE/dt = -E sum_i H_i n_i^2, eV/s.
    pub energy_derivative_ev_s: f64,
    pub rates_per_s: [f64; 4],
}

pub trait PathModel {
    fn sample(&self, time_s: f64) -> Result<PathSample>;
}

pub struct NativePath<'a> {
    pub fixture: &'a NativeFixture,
    pub cohort: &'a Cohort,
}

impl PathModel for NativePath<'_> {
    fn sample(&self, time_s: f64) -> Result<PathSample> {
        let geometry = self.fixture.bridge.0.geometry.snapshot(time_s)?;
        let ray = self.cohort.ray_at(&geometry)?;
        let derivative = -ray.energy_ev
            * (0..3)
                .map(|i| geometry.hubble_per_s[i] * ray.direction[i].powi(2))
                .sum::<f64>();
        Ok(PathSample {
            energy_ev: ray.energy_ev,
            direction: ray.direction,
            energy_derivative_ev_s: derivative,
            rates_per_s: self
                .fixture
                .rates(ray.energy_ev, geometry.volume_factor()?)?,
        })
    }
}

#[derive(Clone, Copy, Debug)]
pub struct PathControls {
    pub slabs: usize,
    pub opacity_degree: usize,
    pub event_degree: usize,
    pub max_samples: usize,
}

impl Default for PathControls {
    fn default() -> Self {
        Self {
            slabs: 4,
            opacity_degree: 4,
            event_degree: 8,
            max_samples: 1_000_000,
        }
    }
}

#[derive(Clone, Debug, Default)]
pub struct PathResult {
    pub survival: f64,
    pub optical_depth: f64,
    pub events: [f64; 4],
    pub heat_ev: [f64; 4],
    pub chemical_ev: f64,
    pub absorbed_energy_ev: f64,
    pub surviving_energy_ev: f64,
    /// Definition from the finite energy ledger. The separately integrated
    /// owner dE/dt below is its independent numerical verification.
    pub geometry_work_ledger_ev: f64,
    pub geometry_work_independent_ev: f64,
    pub end_energy_ev: f64,
    pub end_direction: [f64; 3],
    pub number_residual: f64,
    pub energy_residual_ev: f64,
    pub photo_split_residual_ev: f64,
    pub samples: usize,
    pub inverse_iterations: usize,
    pub slabs: usize,
    pub threshold_crossings: usize,
    pub max_inverse_residual: f64,
    pub opacity_weight_sum: f64,
    pub event_weight_sum: f64,
    /// exp(-finite positive optical depth), or its product, rounded to zero.
    pub represented_survival_underflow: bool,
    /// Positive sampled opacity has an unrepresentable integrated depth.
    pub represented_opacity_underflow: bool,
    pub represented_absorption_underflow: bool,
    pub represented_species_underflow: [bool; 4],
    pub represented_heat_underflow: [bool; 4],
    /// Positive physical-time quadrature is used when total tau <= 1e-8.
    pub thin_time_route: bool,
}

/// Balance positive factors before multiplication. In particular, do not form
/// w*kappa first when kappa is subnormal but the final integral is representable.
fn positive_product<const N: usize>(mut factors: [f64; N]) -> f64 {
    if factors.contains(&0.0) {
        return 0.0;
    }
    factors.sort_by(f64::total_cmp);
    let (mut lower, mut upper) = (0, N);
    let mut value = 1.0;
    while lower < upper {
        if value <= 1.0 {
            upper -= 1;
            value *= factors[upper];
        } else {
            value *= factors[lower];
            lower += 1;
        }
    }
    value
}

#[derive(Clone, Copy)]
struct OpacityIntegral {
    width: f64,
    rate_scale: f64,
    mean_scaled: f64,
}
impl OpacityIntegral {
    fn depth(self) -> f64 {
        positive_product([self.width, self.rate_scale, self.mean_scaled])
    }
}

struct Evaluator<'a, M> {
    model: &'a M,
    samples: usize,
    limit: usize,
}

impl<M: PathModel> Evaluator<'_, M> {
    fn at(&mut self, time_s: f64) -> Result<PathSample> {
        if self.samples >= self.limit {
            return Err(Error::WorkLimit("path_samples"));
        }
        self.samples += 1;
        let value = self.model.sample(time_s)?;
        if !value.energy_ev.is_finite()
            || value.energy_ev <= 0.0
            || !value.energy_derivative_ev_s.is_finite()
            || value.rates_per_s.iter().any(|v| !v.is_finite() || *v < 0.0)
            || value.direction.iter().any(|v| !v.is_finite())
            || (value.direction.iter().map(|x| x * x).sum::<f64>() - 1.0).abs() > 1e-12
        {
            return Err(Error::InvalidInput("path_sample"));
        }
        Ok(value)
    }

    fn opacity_integral(
        &mut self,
        a: f64,
        b: f64,
        gauss: &PositiveGauss,
    ) -> Result<OpacityIntegral> {
        let mut rates = Vec::with_capacity(gauss.nodes.len());
        let mut rate_scale = 0.0_f64;
        for &(u, w) in &gauss.nodes {
            let t = a + (b - a) * u;
            let rate = self.at(t)?.rates_per_s.iter().sum::<f64>();
            if !rate.is_finite() {
                return Err(Error::InvalidInput("path_optical_depth"));
            }
            rate_scale = rate_scale.max(rate);
            rates.push((rate, w));
        }
        let mean_scaled = if rate_scale == 0.0 {
            0.0
        } else {
            rates.iter().map(|(r, w)| w * (r / rate_scale)).sum()
        };
        let integral = OpacityIntegral {
            width: b - a,
            rate_scale,
            mean_scaled,
        };
        let value = integral.depth();
        if !value.is_finite() || value < 0.0 {
            return Err(Error::InvalidInput("path_optical_depth"));
        }
        Ok(integral)
    }

    fn optical_depth(&mut self, a: f64, b: f64, gauss: &PositiveGauss) -> Result<f64> {
        if a == b {
            return Ok(0.0);
        }
        Ok(self.opacity_integral(a, b, gauss)?.depth())
    }

    fn inverse_tau(
        &mut self,
        a: f64,
        b: f64,
        total: f64,
        target: f64,
        gauss: &PositiveGauss,
    ) -> Result<(f64, usize, f64)> {
        let fraction = target / total;
        if !fraction.is_finite() || fraction <= 0.0 || fraction >= 1.0 {
            return Err(Error::InvalidInput("inverse_optical_fraction"));
        }
        let mut lower = a;
        let mut upper = b;
        let mut t = a + (b - a) * fraction;
        let mut residual = f64::INFINITY;
        for iteration in 1..=48 {
            if t <= a || t >= b || !t.is_finite() {
                return Err(Error::NoForwardProgress("inverse_physical_clock"));
            }
            let value = self.optical_depth(a, t, gauss)? / total;
            residual = value - fraction;
            if residual.abs() <= 64.0 * f64::EPSILON
                || upper - lower <= 64.0 * f64::EPSILON * (b - a)
            {
                return Ok((t, iteration, residual.abs()));
            }
            if residual < 0.0 {
                lower = t;
            } else {
                upper = t;
            }
            let rate = self.at(t)?.rates_per_s.iter().sum::<f64>();
            let proposed = t - residual * total / rate;
            let next = if proposed.is_finite() && proposed > lower && proposed < upper {
                proposed
            } else {
                lower + 0.5 * (upper - lower)
            };
            if next == t || next <= lower || next >= upper {
                // A represented clock has reached its adjacent-f64 enclosure.
                // Return the actual residual rather than altering a birth time.
                return Ok((t, iteration, residual.abs()));
            }
            t = next;
        }
        let _ = residual;
        Err(Error::WorkLimit("inverse_optical_iterations"))
    }
}

/// Each supplied cut is a true discontinuity or geometry knot. Uniform slabs
/// provide an independent path control; no opacity or source weights are clipped.
pub fn integrate_path<M: PathModel>(
    model: &M,
    cuts: &[f64],
    thresholds_ev: [f64; 4],
    controls: PathControls,
) -> Result<PathResult> {
    if cuts.len() < 2
        || cuts.iter().any(|v| !v.is_finite())
        || cuts.windows(2).any(|v| v[1] <= v[0])
        || controls.slabs == 0
        || controls.slabs > 4096
        || controls.max_samples == 0
        || thresholds_ev.iter().any(|v| !v.is_finite() || *v < 0.0)
    {
        return Err(Error::InvalidInput("path_controls_or_cuts"));
    }
    let opacity = PositiveGauss::new(controls.opacity_degree)?;
    let event = PositiveGauss::new(controls.event_degree)?;
    let mut evaluator = Evaluator {
        model,
        samples: 0,
        limit: controls.max_samples,
    };
    let start = evaluator.at(cuts[0])?;
    let end = evaluator.at(*cuts.last().unwrap())?;
    let mut out = PathResult {
        survival: 1.0,
        end_energy_ev: end.energy_ev,
        end_direction: end.direction,
        opacity_weight_sum: opacity.raw_weight_sum,
        event_weight_sum: event.raw_weight_sum,
        ..PathResult::default()
    };
    let t0 = cuts[0];
    let t1 = *cuts.last().unwrap();
    if !(t1 - t0).is_finite() {
        return Err(Error::InvalidInput("path_clock_difference"));
    }
    let mut divisions = cuts.to_vec();
    for i in 1..controls.slabs {
        divisions.push(t0 + (t1 - t0) * i as f64 / controls.slabs as f64);
    }
    divisions.sort_by(f64::total_cmp);
    divisions.dedup_by(|a, b| a.to_bits() == b.to_bits());
    let mut slabs = Vec::with_capacity(divisions.len() - 1);
    let mut path_rate_scale = 0.0_f64;
    for pair in divisions.windows(2) {
        let integral = evaluator.opacity_integral(pair[0], pair[1], &opacity)?;
        path_rate_scale = path_rate_scale.max(integral.rate_scale);
        slabs.push((pair[0], pair[1], integral));
    }
    let path_mean_scaled = if path_rate_scale == 0.0 {
        0.0
    } else {
        slabs
            .iter()
            .map(|(_, _, x)| {
                (x.width / (t1 - t0)) * (x.rate_scale / path_rate_scale) * x.mean_scaled
            })
            .sum::<f64>()
    };
    let path_integral = OpacityIntegral {
        width: t1 - t0,
        rate_scale: path_rate_scale,
        mean_scaled: path_mean_scaled,
    };
    let path_tau = path_integral.depth();
    if !path_tau.is_finite() {
        return Err(Error::InvalidInput("path_optical_depth"));
    }
    if path_tau <= 1e-8 {
        // In the thin limit, inverse optical fractions and P/kappa lose
        // information for subnormal hazards. Integrate the positive event
        // distribution in physical time, normalize its shape, and multiply
        // complete moments by the full absorption only after summation.
        // All supplied cuts and independent path/event quadrature remain used.
        out.thin_time_route = true;
        out.optical_depth = path_tau;
        out.represented_opacity_underflow = path_rate_scale > 0.0 && path_tau == 0.0;
        let mut event_samples = Vec::with_capacity(slabs.len() * event.nodes.len());
        let mut event_rate_scale = 0.0_f64;
        let mut tau_before = 0.0;
        for &(a, b, integral) in &slabs {
            for &(u, w) in &event.nodes {
                let t = a + (b - a) * u;
                let sample = evaluator.at(t)?;
                let rate = sample.rates_per_s.iter().sum::<f64>();
                if !rate.is_finite() {
                    return Err(Error::InvalidInput("path_optical_depth"));
                }
                event_rate_scale = event_rate_scale.max(rate);
                let attenuation = (-(tau_before + evaluator.optical_depth(a, t, &opacity)?)).exp();
                out.geometry_work_independent_ev +=
                    positive_product([b - a, w, attenuation, sample.energy_derivative_ev_s.abs()])
                        * sample.energy_derivative_ev_s.signum();
                event_samples.push(((b - a) / (t1 - t0) * w, attenuation, sample));
            }
            tau_before += integral.depth();
        }
        if (path_rate_scale == 0.0) != (event_rate_scale == 0.0) {
            return Err(Error::InvalidInput("opacity_event_quadrature_disagreement"));
        }
        if path_rate_scale > 0.0 {
            let mut event_shape = [0.0; 4];
            let mut heat_shape = [0.0; 4];
            let mut energy_shape = 0.0;
            for (w, attenuation, sample) in event_samples {
                for (species, &threshold) in thresholds_ev.iter().enumerate() {
                    if sample.rates_per_s[species] > 0.0 && sample.energy_ev < threshold {
                        return Err(Error::InvalidInput("absorption_below_binding_threshold"));
                    }
                    let mass = w * attenuation * (sample.rates_per_s[species] / event_rate_scale);
                    event_shape[species] += mass;
                    heat_shape[species] += mass * (sample.energy_ev - threshold).max(0.0);
                    energy_shape += mass * sample.energy_ev;
                }
            }
            let norm = event_shape.iter().sum::<f64>();
            if !norm.is_finite() || norm <= 0.0 {
                return Err(Error::InvalidInput("positive_event_shape"));
            }
            let phi = if path_tau == 0.0 {
                1.0
            } else {
                -(-path_tau).exp_m1() / path_tau
            };
            let quantity = |moment: f64| {
                positive_product([
                    path_integral.width,
                    path_integral.rate_scale,
                    path_integral.mean_scaled,
                    phi,
                    moment,
                ])
            };
            out.represented_absorption_underflow = quantity(1.0) == 0.0;
            for species in 0..4 {
                out.events[species] = quantity(event_shape[species] / norm);
                out.heat_ev[species] = quantity(heat_shape[species] / norm);
                out.represented_species_underflow[species] =
                    event_shape[species] > 0.0 && out.events[species] == 0.0;
                out.represented_heat_underflow[species] =
                    heat_shape[species] > 0.0 && out.heat_ev[species] == 0.0;
            }
            out.absorbed_energy_ev = quantity(energy_shape / norm);
        }
        out.survival = (-path_tau).exp();
        out.slabs = slabs.len();
    } else {
        for &(a, b, integral) in &slabs {
            let tau = integral.depth();
            out.optical_depth += tau;
            let survival_start = out.survival;
            let absorbed_fraction = -(-tau).exp_m1();
            let absorbed = survival_start * absorbed_fraction;
            out.represented_opacity_underflow |= integral.rate_scale > 0.0 && tau == 0.0;
            out.represented_absorption_underflow |=
                survival_start > 0.0 && integral.rate_scale > 0.0 && absorbed == 0.0;
            if tau == 0.0 {
                for &(u, w) in &event.nodes {
                    out.geometry_work_independent_ev += survival_start
                        * (b - a)
                        * w
                        * evaluator.at(a + (b - a) * u)?.energy_derivative_ev_s;
                }
            } else {
                for &(u, w) in &event.nodes {
                    let z = -(-u * absorbed_fraction).ln_1p();
                    let (t, iterations, residual) =
                        evaluator.inverse_tau(a, b, tau, z, &opacity)?;
                    out.inverse_iterations += iterations;
                    out.max_inverse_residual = out.max_inverse_residual.max(residual);
                    let sample = evaluator.at(t)?;
                    let total: f64 = sample.rates_per_s.iter().sum();
                    if total <= 0.0 {
                        return Err(Error::InvalidInput("positive_hazard_inverse"));
                    }
                    let probability = absorbed * w;
                    out.absorbed_energy_ev += probability * sample.energy_ev;
                    out.geometry_work_independent_ev +=
                        probability / total * sample.energy_derivative_ev_s;
                    for (species, &threshold) in thresholds_ev.iter().enumerate() {
                        let amount = probability * (sample.rates_per_s[species] / total);
                        if sample.rates_per_s[species] > 0.0 && sample.energy_ev < threshold {
                            return Err(Error::InvalidInput("absorption_below_binding_threshold"));
                        }
                        out.represented_species_underflow[species] |=
                            absorbed > 0.0 && sample.rates_per_s[species] > 0.0 && amount == 0.0;
                        out.events[species] += amount;
                        let heat = amount * (sample.energy_ev - threshold).max(0.0);
                        out.represented_heat_underflow[species] |=
                            amount > 0.0 && sample.energy_ev > threshold && heat == 0.0;
                        out.heat_ev[species] += heat;
                    }
                }
            }
            out.survival = survival_start * (-tau).exp();
            if survival_start > 0.0 && tau > 0.0 && out.survival == 0.0 {
                out.represented_survival_underflow = true;
            }
            out.slabs += 1;
        }
    }
    out.surviving_energy_ev = out.survival * end.energy_ev;
    out.chemical_ev = out
        .events
        .iter()
        .zip(thresholds_ev)
        .map(|(n, chi)| n * chi)
        .sum();
    out.geometry_work_ledger_ev =
        out.surviving_energy_ev + out.absorbed_energy_ev - start.energy_ev;
    out.number_residual = out.survival + out.events.iter().sum::<f64>() - 1.0;
    out.energy_residual_ev = out.surviving_energy_ev + out.absorbed_energy_ev
        - start.energy_ev
        - out.geometry_work_independent_ev;
    out.photo_split_residual_ev =
        out.heat_ev.iter().sum::<f64>() + out.chemical_ev - out.absorbed_energy_ev;
    out.samples = evaluator.samples;
    if [
        out.survival,
        out.optical_depth,
        out.chemical_ev,
        out.absorbed_energy_ev,
        out.surviving_energy_ev,
        out.geometry_work_ledger_ev,
        out.geometry_work_independent_ev,
        out.number_residual,
        out.energy_residual_ev,
        out.photo_split_residual_ev,
        out.max_inverse_residual,
    ]
    .iter()
    .chain(out.events.iter())
    .chain(out.heat_ev.iter())
    .any(|x| !x.is_finite())
        || out
            .events
            .iter()
            .chain(out.heat_ev.iter())
            .any(|x| *x < 0.0)
        || out.survival < 0.0
        || out.survival > 1.0
    {
        return Err(Error::InvalidInput("path_accumulator_finite_positive"));
    }
    Ok(out)
}

pub fn native_path(
    fixture: &NativeFixture,
    cohort: &Cohort,
    controls: PathControls,
) -> Result<PathResult> {
    if cohort.n_comoving_m3 < 0.0 || !cohort.n_comoving_m3.is_finite() {
        return Err(Error::InvalidInput("cohort_population"));
    }
    fixture.bridge.0.geometry.validate_birth(cohort)?;
    let end = fixture.bridge.0.geometry.snapshot(fixture.t1)?;
    let e0 = cohort.ray_at(&cohort.birth_geometry)?.energy_ev;
    let e1 = cohort.ray_at(&end)?.energy_ev;
    let cuts = split_by_thresholds_from_energies(
        &fixture.bridge.0.geometry,
        cohort,
        cohort.birth_time_s,
        fixture.t1,
        e0,
        e1,
        fixture.thresholds_ev[3],
    )?;
    let mut result = integrate_path(
        &NativePath { fixture, cohort },
        &cuts,
        fixture.thresholds_ev,
        controls,
    )?;
    result.threshold_crossings = [13.60, 24.59, 54.42, fixture.thresholds_ev[3]]
        .iter()
        .filter(|edge| e0 > **edge && e1 < **edge)
        .count();
    Ok(result)
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BirthMethod {
    Fitted,
    Gauss,
}

#[derive(Clone, Copy, Debug)]
pub struct RunControls {
    pub birth: BirthMethod,
    pub refinement: usize,
    pub birth_degree: usize,
    pub path: PathControls,
    pub split_spectrum: bool,
    /// A declared template-prefix control for inexpensive smoke tests.
    /// Zero means all templates; this is never called a full-source result.
    pub template_limit: usize,
    pub source_scale: f64,
}

pub fn emit_births(
    fixture: &NativeFixture,
    template: &Cohort,
    controls: RunControls,
) -> Result<Vec<(f64, f64, Cohort)>> {
    fixture.validate_source()?;
    if !controls.source_scale.is_finite()
        || controls.source_scale < 0.0
        || !template.n_comoving_m3.is_finite()
        || template.n_comoving_m3 < 0.0
    {
        return Err(Error::InvalidInput("source_weight"));
    }
    let cell = fixture
        .bridge
        .0
        .source
        .spectral_cells
        .get(template.spectral_index)
        .ok_or(Error::InvalidInput("template_spectral_label"))?;
    if template.angular_index >= fixture.bridge.0.source.angular_cells.len()
        || !template.energy_at_birth_ev.is_finite()
        || template.energy_at_birth_ev < cell.lower_ev
        || template.energy_at_birth_ev > cell.upper_ev
    {
        return Err(Error::InvalidInput("template_source_label_or_energy"));
    }
    template.ray_at(&template.birth_geometry)?;
    let rates = fixture.bridge.opacity_channels(
        template.energy_at_birth_ev,
        &fixture.rate_gas,
        &fixture.conf,
    )?;
    let dt = fixture.t1 - fixture.t0;
    let tau = rates.iter().sum::<f64>() * dt;
    let nodes = match controls.birth {
        BirthMethod::Fitted => {
            rei_iso_couple_reference::fitted_birth::rule(tau, controls.refinement)?
        }
        BirthMethod::Gauss => gauss_age_nodes(tau, controls.refinement, controls.birth_degree)?,
    };
    let mut out = Vec::with_capacity(nodes.len());
    for (age, weight) in nodes {
        let t = fixture.t1 - dt * age;
        if !t.is_finite() || t < fixture.t0 || t >= fixture.t1 {
            return Err(Error::NoForwardProgress("birth_clock"));
        }
        let geometry = fixture.bridge.0.geometry.snapshot(t)?;
        let amplitude = fixture.emission_amplitude(&geometry)?;
        let mut cohort = template.clone();
        cohort.birth_time_s = t;
        cohort.birth_geometry = geometry;
        cohort.n_comoving_m3 = template.n_comoving_m3
            * dt
            * weight
            * (amplitude / fixture.source_midpoint_amplitude)
            * controls.source_scale;
        if !cohort.n_comoving_m3.is_finite() || cohort.n_comoving_m3 < 0.0 {
            return Err(Error::InvalidInput("born_population"));
        }
        out.push((age, weight, cohort));
    }
    Ok(out)
}

#[derive(Clone, Debug, Default)]
pub struct Totals {
    pub born: f64,
    pub surviving: f64,
    pub age_sum_s: f64,
    pub age2_sum_s2: f64,
    pub events: [f64; 4],
    pub heat_j: [f64; 4],
    pub chemical_j: f64,
    pub source_energy_j: f64,
    pub surviving_energy_j: f64,
    pub absorbed_energy_j: f64,
    pub work_ledger_j: f64,
    pub work_independent_j: f64,
    pub q2_numerator_j: f64,
    pub cohorts: usize,
    pub samples: usize,
    pub inversions: usize,
    pub threshold_crossings: usize,
    pub max_path_number_residual: f64,
    pub max_path_energy_relative_residual: f64,
    pub max_inverse_residual: f64,
    pub zero_born_cohorts: usize,
    pub represented_survival_underflows: usize,
    pub represented_opacity_underflows: usize,
    pub represented_absorption_underflows: usize,
    pub represented_species_underflows: usize,
    pub represented_heat_underflows: usize,
    pub thin_time_paths: usize,
}

impl Totals {
    fn add_birth(&mut self, fixture: &NativeFixture, co: &Cohort, path: &PathResult) {
        let n = co.n_comoving_m3;
        let retained = n * path.survival;
        let age = fixture.t1 - co.birth_time_s;
        self.born += n;
        self.surviving += retained;
        self.age_sum_s += retained * age;
        self.age2_sum_s2 += retained * age * age;
        self.source_energy_j += n * co.energy_at_birth_ev * EV_J;
        self.surviving_energy_j += n * path.surviving_energy_ev * EV_J;
        self.absorbed_energy_j += n * path.absorbed_energy_ev * EV_J;
        self.chemical_j += n * path.chemical_ev * EV_J;
        self.work_ledger_j += n * path.geometry_work_ledger_ev * EV_J;
        self.work_independent_j += n * path.geometry_work_independent_ev * EV_J;
        self.q2_numerator_j +=
            n * path.surviving_energy_ev * EV_J * 0.5 * (3.0 * path.end_direction[2].powi(2) - 1.0);
        for i in 0..4 {
            self.events[i] += n * path.events[i];
            self.heat_j[i] += n * path.heat_ev[i] * EV_J;
        }
        self.cohorts += 1;
        self.zero_born_cohorts += usize::from(n == 0.0);
        self.represented_survival_underflows += usize::from(path.represented_survival_underflow);
        self.represented_opacity_underflows += usize::from(path.represented_opacity_underflow);
        self.represented_absorption_underflows +=
            usize::from(path.represented_absorption_underflow);
        self.represented_species_underflows += path
            .represented_species_underflow
            .iter()
            .filter(|&&x| x)
            .count();
        self.represented_heat_underflows += path
            .represented_heat_underflow
            .iter()
            .filter(|&&x| x)
            .count();
        self.thin_time_paths += usize::from(path.thin_time_route);
        self.samples += path.samples;
        self.inversions += path.inverse_iterations;
        self.threshold_crossings += path.threshold_crossings;
        self.max_path_number_residual = self
            .max_path_number_residual
            .max(path.number_residual.abs());
        self.max_path_energy_relative_residual = self
            .max_path_energy_relative_residual
            .max((path.energy_residual_ev / co.energy_at_birth_ev).abs());
        self.max_inverse_residual = self.max_inverse_residual.max(path.max_inverse_residual);
    }
    pub fn number_residual(&self) -> f64 {
        self.surviving + self.events.iter().sum::<f64>() - self.born
    }
    pub fn energy_residual(&self) -> f64 {
        self.surviving_energy_j + self.absorbed_energy_j
            - self.source_energy_j
            - self.work_independent_j
    }
    fn validate(&self) -> Result<()> {
        if [
            self.born,
            self.surviving,
            self.age_sum_s,
            self.age2_sum_s2,
            self.chemical_j,
            self.source_energy_j,
            self.surviving_energy_j,
            self.absorbed_energy_j,
            self.work_ledger_j,
            self.work_independent_j,
            self.q2_numerator_j,
        ]
        .iter()
        .chain(self.events.iter())
        .chain(self.heat_j.iter())
        .any(|x| !x.is_finite())
        {
            return Err(Error::InvalidInput("source_integral_accumulator"));
        }
        Ok(())
    }
}

/// Full output retains every labelled birth. Scalar reuse is allowed only for
/// exact reflection-equivalent paths; all labels/weights remain separate rows.
pub fn run(fixture: &NativeFixture, controls: RunControls, directory: &Path) -> Result<Totals> {
    fs::create_dir_all(directory)?;
    let start = Instant::now();
    let templates = fixture.templates(controls.split_spectrum)?;
    let limit = if controls.template_limit == 0 {
        templates.len()
    } else {
        controls.template_limit.min(templates.len())
    };
    let mut births_file = std::io::BufWriter::new(fs::File::create(directory.join("BIRTHS.csv"))?);
    let mut flags_file =
        std::io::BufWriter::new(fs::File::create(directory.join("PATH_FLAGS.csv"))?);
    writeln!(
        flags_file,
        "template,node,zero_born,represented_survival_underflow,represented_retained_product_underflow,thin_time_route,represented_opacity_underflow,represented_absorption_underflow,HI_underflow,HeI_underflow,HeII_underflow,DI_underflow,HI_heat_underflow,HeI_heat_underflow,HeII_heat_underflow,DI_heat_underflow"
    )?;
    writeln!(
        births_file,
        "template,spectral,angular,node,target_age,emission_weight,birth_time_s,birth_a1,birth_a2,birth_a3,birth_H1,birth_H2,birth_H3,birth_energy_ev,birth_n1,birth_n2,birth_n3,K1,K2,K3,born_com3,tau,survival,retained_com3,end_energy_ev,end_n1,end_n2,end_n3,HI,HeI,HeII,DI,heat_j,chemical_j,absorption_j,work_ledger_j,work_independent_j,path_samples,inverse_iterations,threshold_crossings,max_inverse_residual"
    )?;
    let mut template_file =
        std::io::BufWriter::new(fs::File::create(directory.join("TEMPLATES_RESULT.csv"))?);
    writeln!(
        template_file,
        "template,spectral,angular,energy_ev,born_com3,survivor_com3,age_sum_com_s,age2_sum_com_s2,HI,HeI,HeII,DI,thermal_j,chemical_j,source_j,surviving_j,absorbed_j,work_ledger_j,work_independent_j,q2_numerator_j,cohorts"
    )?;
    let mut totals = Totals::default();
    let mut cache: HashMap<[u64; 7], PathResult> = HashMap::new();
    let mut actual_path_samples = 0usize;
    for (id, template) in templates.iter().take(limit).enumerate() {
        let mut subtotal = Totals::default();
        for (node, (target_age, weight, co)) in
            emit_births(fixture, template, controls)?.iter().enumerate()
        {
            let ray = co.ray_at(&co.birth_geometry)?;
            let k = std::array::from_fn::<_, 3, _>(|i| {
                co.birth_geometry.scale_factors[i] * ray.energy_ev * ray.direction[i]
            });
            let key = [
                co.birth_time_s.to_bits(),
                co.energy_at_birth_ev.to_bits(),
                co.direction_at_birth[0].abs().to_bits(),
                co.direction_at_birth[1].abs().to_bits(),
                co.direction_at_birth[2].abs().to_bits(),
                co.birth_geometry.scale_factors[0].to_bits(),
                co.birth_geometry.scale_factors[2].to_bits(),
            ];
            let mut path = if let Some(value) = cache.get(&key) {
                value.clone()
            } else {
                let value = native_path(fixture, co, controls.path)?;
                actual_path_samples += value.samples;
                cache.insert(key, value.clone());
                value
            };
            // Reflection changes the labelled final direction, not scalar opacity.
            for i in 0..3 {
                path.end_direction[i] = path.end_direction[i]
                    .abs()
                    .copysign(co.direction_at_birth[i]);
            }
            subtotal.add_birth(fixture, co, &path);
            totals.add_birth(fixture, co, &path);
            let n = co.n_comoving_m3;
            writeln!(
                flags_file,
                "{id},{node},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
                n == 0.0,
                path.represented_survival_underflow,
                n > 0.0 && path.survival > 0.0 && n * path.survival == 0.0,
                path.thin_time_route,
                path.represented_opacity_underflow,
                path.represented_absorption_underflow,
                path.represented_species_underflow[0],
                path.represented_species_underflow[1],
                path.represented_species_underflow[2],
                path.represented_species_underflow[3],
                path.represented_heat_underflow[0],
                path.represented_heat_underflow[1],
                path.represented_heat_underflow[2],
                path.represented_heat_underflow[3]
            )?;
            writeln!(
                births_file,
                "{id},{},{},{node},{target_age:.17e},{weight:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{n:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{},{},{},{:.17e}",
                co.spectral_index,
                co.angular_index,
                co.birth_time_s,
                co.birth_geometry.scale_factors[0],
                co.birth_geometry.scale_factors[1],
                co.birth_geometry.scale_factors[2],
                co.birth_geometry.hubble_per_s[0],
                co.birth_geometry.hubble_per_s[1],
                co.birth_geometry.hubble_per_s[2],
                co.energy_at_birth_ev,
                co.direction_at_birth[0],
                co.direction_at_birth[1],
                co.direction_at_birth[2],
                k[0],
                k[1],
                k[2],
                path.optical_depth,
                path.survival,
                n * path.survival,
                path.end_energy_ev,
                path.end_direction[0],
                path.end_direction[1],
                path.end_direction[2],
                n * path.events[0],
                n * path.events[1],
                n * path.events[2],
                n * path.events[3],
                n * path.heat_ev.iter().sum::<f64>() * EV_J,
                n * path.chemical_ev * EV_J,
                n * path.absorbed_energy_ev * EV_J,
                n * path.geometry_work_ledger_ev * EV_J,
                n * path.geometry_work_independent_ev * EV_J,
                path.samples,
                path.inverse_iterations,
                path.threshold_crossings,
                path.max_inverse_residual
            )?;
        }
        writeln!(
            template_file,
            "{id},{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{}",
            template.spectral_index,
            template.angular_index,
            template.energy_at_birth_ev,
            subtotal.born,
            subtotal.surviving,
            subtotal.age_sum_s,
            subtotal.age2_sum_s2,
            subtotal.events[0],
            subtotal.events[1],
            subtotal.events[2],
            subtotal.events[3],
            subtotal.heat_j.iter().sum::<f64>(),
            subtotal.chemical_j,
            subtotal.source_energy_j,
            subtotal.surviving_energy_j,
            subtotal.absorbed_energy_j,
            subtotal.work_ledger_j,
            subtotal.work_independent_j,
            subtotal.q2_numerator_j,
            subtotal.cohorts
        )?;
        subtotal.validate()?;
    }
    totals.validate()?;
    births_file.flush()?;
    flags_file.flush()?;
    template_file.flush()?;
    let mut file = fs::File::create(directory.join("SUMMARY.csv"))?;
    writeln!(
        file,
        "case,birth,refinement,birth_degree,path_slabs,opacity_degree,event_degree,split,templates,available_templates,cohorts,unique_paths,actual_path_samples,wall_s,born_com3,survivor_com3,age_sum_com_s,age2_sum_com_s2,HI,HeI,HeII,DI,thermal_j,chemical_j,source_j,surviving_j,absorbed_j,work_ledger_j,work_independent_j,q2_numerator_j,number_residual,energy_residual_j,max_path_number_residual,max_path_energy_relative_residual,max_inverse_residual,threshold_crossings"
    )?;
    writeln!(
        file,
        "{},{:?},{},{},{},{},{},{},{limit},{},{},{},{actual_path_samples},{:.9e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{}",
        fixture.case,
        controls.birth,
        controls.refinement,
        controls.birth_degree,
        controls.path.slabs,
        controls.path.opacity_degree,
        controls.path.event_degree,
        controls.split_spectrum,
        templates.len(),
        totals.cohorts,
        cache.len(),
        start.elapsed().as_secs_f64(),
        totals.born,
        totals.surviving,
        totals.age_sum_s,
        totals.age2_sum_s2,
        totals.events[0],
        totals.events[1],
        totals.events[2],
        totals.events[3],
        totals.heat_j.iter().sum::<f64>(),
        totals.chemical_j,
        totals.source_energy_j,
        totals.surviving_energy_j,
        totals.absorbed_energy_j,
        totals.work_ledger_j,
        totals.work_independent_j,
        totals.q2_numerator_j,
        totals.number_residual(),
        totals.energy_residual(),
        totals.max_path_number_residual,
        totals.max_path_energy_relative_residual,
        totals.max_inverse_residual,
        totals.threshold_crossings
    )?;
    let mut diagnostic = fs::File::create(directory.join("DIAGNOSTICS.json"))?;
    writeln!(
        diagnostic,
        "{{\n  \"zero_born_cohorts\": {},\n  \"represented_survival_underflows\": {},\n  \"thin_time_paths\": {},\n  \"represented_opacity_underflows\": {},\n  \"represented_absorption_underflows\": {},\n  \"represented_species_underflows\": {},\n  \"represented_heat_underflows\": {},\n  \"per_path_sample_limit\": {},\n  \"actual_path_samples\": {},\n  \"opacity_raw_weight_sum\": {:.17e},\n  \"event_raw_weight_sum\": {:.17e},\n  \"max_inverse_normalized_residual\": {:.17e},\n  \"inventory_owner\": \"recorded_SIGNED_MINUS_step1_comoving\",\n  \"geometry_work_independent\": \"integral_survival_times_owner_dE_dt\",\n  \"gas_evolved\": false\n}}",
        totals.zero_born_cohorts,
        totals.represented_survival_underflows,
        totals.thin_time_paths,
        totals.represented_opacity_underflows,
        totals.represented_absorption_underflows,
        totals.represented_species_underflows,
        totals.represented_heat_underflows,
        controls.path.max_samples,
        actual_path_samples,
        PositiveGauss::new(controls.path.opacity_degree)?.raw_weight_sum,
        PositiveGauss::new(controls.path.event_degree)?.raw_weight_sum,
        totals.max_inverse_residual
    )?;
    Ok(totals)
}
