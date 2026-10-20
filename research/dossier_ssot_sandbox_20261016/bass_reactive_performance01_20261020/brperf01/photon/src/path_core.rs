// Derived add-only performance copy; see scripts/derive_kernel.py.
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
    opacity_scratch: [f64; 128],
    opacity_integrals: usize,
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
        self.opacity_integrals += 1;
        let mut rate_scale = 0.0_f64;
        for (index, &(u, _w)) in gauss.nodes.iter().enumerate() {
            let t = a + (b - a) * u;
            let rate = self.at(t)?.rates_per_s.iter().sum::<f64>();
            if !rate.is_finite() {
                return Err(Error::InvalidInput("path_optical_depth"));
            }
            rate_scale = rate_scale.max(rate);
            self.opacity_scratch[index] = rate;
        }
        let mean_scaled = if rate_scale == 0.0 {
            0.0
        } else {
            self.opacity_scratch[..gauss.nodes.len()]
                .iter()
                .zip(&gauss.nodes)
                .map(|(r, (_, w))| w * (r / rate_scale))
                .sum()
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
pub fn integrate_path_cached<M: PathModel>(
    model: &M,
    cuts: &[f64],
    thresholds_ev: [f64; 4],
    controls: PathControls,
    rules: &Rules,
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
    if controls.opacity_degree != rules.opacity.nodes.len()
        || controls.event_degree != rules.event.nodes.len()
    {
        return Err(Error::InvalidInput("prepared_rule_mismatch"));
    }
    let opacity = &rules.opacity;
    let event = &rules.event;
    let mut evaluator = Evaluator {
        model,
        samples: 0,
        limit: controls.max_samples,
        opacity_scratch: [0.0; 128],
        opacity_integrals: 0,
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
        let integral = evaluator.opacity_integral(pair[0], pair[1], opacity)?;
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
                let attenuation = (-(tau_before + evaluator.optical_depth(a, t, opacity)?)).exp();
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
                    let (t, iterations, residual) = evaluator.inverse_tau(a, b, tau, z, opacity)?;
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
    let mut work = rules.work.get();
    work.opacity_integrals += evaluator.opacity_integrals;
    work.virtual_samples += evaluator.samples;
    rules.work.set(work);
    Ok(out)
}
