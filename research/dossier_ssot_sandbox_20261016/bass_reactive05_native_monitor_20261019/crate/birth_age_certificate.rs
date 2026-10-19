//! A posteriori distribution diagnostics for positive birth-age quadrature.
//!
//! The reference has constant emission and constant opacity over a time span.
//! Its emitted probability density is uniform on x in [0,1]; the survivor
//! density is exp(-tau*x)/phi(tau), where x is age divided by the total span.
//! Actual quadrature nodes are read without moving, merging, or changing them.
//! Input weights integrate emitted photons. A caller may supply nodes from a
//! single fitted rule, GL quadrature, or several timesteps in global age units.
//!
//! Mass defects and normalized shape defects are separate. W1 is the integral
//! of the absolute CDF difference on [0,1], evaluated by positive closed-form
//! interval integrals. Thus, in real arithmetic, |E_d[f]-E_e[f]| <= Lip(f)*W1.
//! Values returned here are f64 evaluations, not directed-rounding intervals.
//! No claim about a variable-opacity or coupled-gas solution follows merely
//! from this constant-opacity reference comparison.

use crate::fitted_birth;
use crate::full_network::NetworkError;

#[derive(Clone, Copy, Debug)]
pub struct ShapeCertificate {
    /// Supremum of the normalized CDF difference, including both sides of jumps.
    pub cdf_sup: f64,
    /// Normalized one-dimensional Wasserstein distance in units of total age.
    pub w1: f64,
    /// First and second moments of normalized age under the exact probability.
    pub exact_moments: [f64; 2],
    /// First and second moments under the normalized positive discrete measure.
    pub discrete_moments: [f64; 2],
    /// Discrete minus exact first and second normalized moments.
    pub signed_moment_defects: [f64; 2],
    /// Positive input atoms whose shifted relative weight rounded to zero.
    pub normalized_weight_underflows: usize,
}

#[derive(Clone, Copy, Debug)]
pub struct MeasureCertificate {
    /// Counts in the same volume convention as `born` supplied by the caller.
    pub exact_mass: f64,
    pub discrete_mass: f64,
    /// (Discrete reference weight - exact weight) / exact weight, independent
    /// of the source amplitude. None when born=0; -1 for an empty quadrature.
    pub relative_mass_defect: Option<f64>,
    /// ln(discrete weight / exact weight), retained even when absolute counts
    /// underflow. None when the source or the discrete measure is empty.
    pub log_mass_ratio: Option<f64>,
    /// True if a mathematically positive exact or discrete count rounded to zero.
    pub absolute_mass_underflow: bool,
    /// None for zero source or an empty discrete measure: shape is undefined.
    pub shape: Option<ShapeCertificate>,
}

#[derive(Clone, Copy, Debug)]
pub struct BirthAgeCertificate {
    pub tau: f64,
    pub born: f64,
    pub input_nodes: usize,
    pub positive_nodes: usize,
    pub emitted: MeasureCertificate,
    pub survivors: MeasureCertificate,
}

#[derive(Default)]
struct PositiveSum {
    sum: f64,
    correction: f64,
}

impl PositiveSum {
    fn add(&mut self, value: f64) {
        let next = self.sum + value;
        self.correction += if self.sum >= value {
            (self.sum - next) + value
        } else {
            (value - next) + self.sum
        };
        self.sum = next;
    }

    fn value(&self) -> f64 {
        self.sum + self.correction
    }
}

fn phi(tau: f64) -> f64 {
    // Every caller has already checked tau >= 0 and finite.
    if tau == 0.0 {
        1.0
    } else {
        -(-tau).exp_m1() / tau
    }
}

/// Integrals of s*exp(-z*s) and (1-s)*exp(-z*s) on [0,1].
fn psi_chi(z: f64) -> (f64, f64) {
    if z < 1e-3 {
        let psi = 0.5
            + z * (-1.0 / 3.0
                + z * (1.0 / 8.0
                    + z * (-1.0 / 30.0 + z * (1.0 / 144.0 + z * (-1.0 / 840.0 + z / 5760.0)))));
        let chi = 0.5
            + z * (-1.0 / 6.0
                + z * (1.0 / 24.0
                    + z * (-1.0 / 120.0 + z * (1.0 / 720.0 + z * (-1.0 / 5040.0 + z / 40320.0)))));
        (psi, chi)
    } else {
        ((phi(z) - (-z).exp()) / z, (1.0 - phi(z)) / z)
    }
}

/// z*psi(z), z*chi(z), without z^2 or an underflowing 1/z^2.
fn scaled_psi_chi(z: f64) -> (f64, f64) {
    if z < 1e-3 {
        let (psi, chi) = psi_chi(z);
        (z * psi, z * chi)
    } else {
        (phi(z) - (-z).exp(), 1.0 - phi(z))
    }
}

fn reference_cdf(tau: f64, x: f64) -> f64 {
    if tau <= 1.0 {
        x * phi(tau * x) / phi(tau)
    } else {
        -(-tau * x).exp_m1() / -(-tau).exp_m1()
    }
}

fn reference_quantile(tau: f64, probability: f64) -> f64 {
    if probability == 0.0 || probability == 1.0 || tau == 0.0 {
        return probability;
    }
    if tau <= 1.0 {
        // Q(p)=p*phi(tau)*[-ln(1-z)/z], z=p*(1-exp(-tau)).
        // The factored form preserves the uniform limit even when z underflows.
        let z = probability * -(-tau).exp_m1();
        let log_ratio = if z == 0.0 { 1.0 } else { -(-z).ln_1p() / z };
        return probability * phi(tau) * log_ratio;
    }
    let log_tail = if probability <= 0.5 {
        (-probability * -(-tau).exp_m1()).ln_1p()
    } else {
        // This form preserves 1-p when exp(-tau) is smaller than an ulp of 1.
        ((1.0 - probability) + probability * (-tau).exp()).ln()
    };
    -log_tail / tau
}

fn reference_moments(tau: f64) -> [f64; 2] {
    if tau <= 1.0 {
        // Integrate the entire convergent Taylor series, including tau=0.
        // At tau<=1, 32 terms leave a truncation far below f64 roundoff.
        let mut integrals = [0.0; 3];
        let mut coefficient = 1.0;
        for n in 0..32 {
            for (p, integral) in integrals.iter_mut().enumerate() {
                *integral += coefficient / (n + p + 1) as f64;
            }
            coefficient *= -tau / (n + 1) as f64;
        }
        [integrals[1] / integrals[0], integrals[2] / integrals[0]]
    } else {
        let tail_ratio = (-tau).exp() / -(-tau).exp_m1();
        let mean = 1.0 / tau - tail_ratio;
        [mean, (2.0 / tau) * mean - tail_ratio]
    }
}

/// Positive area to the left of the CDF/plateau crossing b.
fn left_area(tau: f64, u: f64, v: f64, b: f64) -> f64 {
    let length = v - u;
    if length == 0.0 {
        return 0.0;
    }
    let gap = b - v;
    let t = tau * length;
    let s = tau * gap;
    if tau <= 1.0 {
        let (psi, _) = psi_chi(t);
        (-tau * u).exp() * length * (length * psi + (-t).exp() * gap * phi(s)) / phi(tau)
    } else {
        let (scaled_psi, _) = scaled_psi_chi(t);
        // Algebraically equivalent, but remains representable for tau~1e300.
        (-tau * u).exp() * length * (scaled_psi + (-t).exp() * -(-s).exp_m1()) / -(-tau).exp_m1()
    }
}

/// Positive area to the right of the CDF/plateau crossing b.
fn right_area(tau: f64, u: f64, v: f64, b: f64) -> f64 {
    let length = v - u;
    if length == 0.0 {
        return 0.0;
    }
    let gap = u - b;
    let t = tau * length;
    let s = tau * gap;
    if tau <= 1.0 {
        let (_, chi) = psi_chi(t);
        (-tau * b).exp() * length * (gap * phi(s) + (-s).exp() * length * chi) / phi(tau)
    } else {
        let (_, scaled_chi) = scaled_psi_chi(t);
        (-tau * b).exp() * length * (-(-s).exp_m1() + (-s).exp() * scaled_chi) / -(-tau).exp_m1()
    }
}

fn plateau_area(tau: f64, u: f64, v: f64, probability: f64) -> f64 {
    let crossing = reference_quantile(tau, probability);
    if v <= crossing {
        left_area(tau, u, v, crossing)
    } else if u >= crossing {
        right_area(tau, u, v, crossing)
    } else {
        left_area(tau, u, crossing, crossing) + right_area(tau, crossing, v, crossing)
    }
}

fn empty_measure(born: f64, exact_weight: f64) -> MeasureCertificate {
    MeasureCertificate {
        exact_mass: born * exact_weight,
        discrete_mass: 0.0,
        relative_mass_defect: (born != 0.0).then_some(-1.0),
        log_mass_ratio: None,
        absolute_mass_underflow: born > 0.0 && born * exact_weight == 0.0,
        shape: None,
    }
}

fn measure_certificate(
    sorted: &[(f64, f64)],
    tau: f64,
    born: f64,
) -> Result<MeasureCertificate, NetworkError> {
    let exact_weight = phi(tau);
    if born == 0.0 || sorted.is_empty() {
        return Ok(empty_measure(born, exact_weight));
    }
    let logs: Vec<_> = sorted
        .iter()
        .map(|(x, weight)| weight.ln() - tau * x)
        .collect();
    let shift = logs.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    let weights: Vec<_> = logs.iter().map(|log| (log - shift).exp()).collect();
    let mut total = PositiveSum::default();
    let mut direct_mass = PositiveSum::default();
    for ((x, emitted), weight) in sorted.iter().zip(&weights) {
        total.add(*weight);
        direct_mass.add(emitted * (-tau * x).exp());
    }
    let total = total.value();
    let log_weight = shift + total.ln();
    let log_ratio = log_weight - exact_weight.ln();
    let direct_weight = direct_mass.value();
    let relative_mass_defect = if direct_weight.is_finite() && direct_weight > 0.0 {
        (direct_weight - exact_weight) / exact_weight
    } else {
        log_ratio.exp_m1()
    };
    let direct_count = born * direct_weight;
    let discrete_mass = if direct_count.is_finite() && direct_count > 0.0 {
        direct_count
    } else {
        (born.ln() + log_weight).exp()
    };
    let exact_mass = born * exact_weight;
    if ![exact_mass, discrete_mass, relative_mass_defect, log_ratio]
        .iter()
        .all(|v| v.is_finite())
    {
        return Err(NetworkError::NonFinite);
    }

    // Prefix/(prefix+suffix) evaluates each discrete CDF partition directly.
    // This keeps probabilities within [0,1] without clipping any population.
    let mut suffix = vec![0.0; weights.len() + 1];
    let mut reverse_sum = PositiveSum::default();
    for i in (0..weights.len()).rev() {
        reverse_sum.add(weights[i]);
        suffix[i] = reverse_sum.value();
    }
    let mut prefix = PositiveSum::default();
    let mut cdf = 0.0;
    let mut previous_age = 0.0;
    let mut cdf_sup: f64 = 0.0;
    let mut w1 = PositiveSum::default();
    let mut moments = [PositiveSum::default(), PositiveSum::default()];
    for (i, ((age, _), weight)) in sorted.iter().zip(&weights).enumerate() {
        w1.add(plateau_area(tau, previous_age, *age, cdf));
        let exact_cdf = reference_cdf(tau, *age);
        cdf_sup = cdf_sup.max((exact_cdf - cdf).abs());
        prefix.add(*weight);
        let left_mass = prefix.value();
        cdf = left_mass / (left_mass + suffix[i + 1]);
        cdf_sup = cdf_sup.max((exact_cdf - cdf).abs());
        moments[0].add((weight / total) * age);
        moments[1].add((weight / total) * age * age);
        previous_age = *age;
    }
    w1.add(plateau_area(tau, previous_age, 1.0, 1.0));
    let exact_moments = reference_moments(tau);
    let discrete_moments = [moments[0].value(), moments[1].value()];
    let w1 = w1.value();
    if ![cdf_sup, w1, discrete_moments[0], discrete_moments[1]]
        .iter()
        .all(|v| v.is_finite() && *v >= 0.0)
    {
        return Err(NetworkError::NonFinite);
    }
    Ok(MeasureCertificate {
        exact_mass,
        discrete_mass,
        relative_mass_defect: Some(relative_mass_defect),
        log_mass_ratio: Some(log_ratio),
        absolute_mass_underflow: exact_mass == 0.0 || discrete_mass == 0.0,
        shape: Some(ShapeCertificate {
            cdf_sup,
            w1,
            exact_moments,
            discrete_moments,
            signed_moment_defects: [
                discrete_moments[0] - exact_moments[0],
                discrete_moments[1] - exact_moments[1],
            ],
            normalized_weight_underflows: weights.iter().filter(|w| **w == 0.0).count(),
        }),
    })
}

/// Compare actual nonnegative emitted weights with the constant-source exact
/// measure. Ages may include endpoints and repeated values and need not be
/// sorted. Zero weights are admitted; negative or nonfinite inputs are rejected.
/// Empty nodes with born>0 report complete mass loss and undefined shape.
/// With born=0, both mass and shape follow the empty-measure convention.
pub fn compare_nodes(
    tau: f64,
    born: f64,
    nodes: &[(f64, f64)],
) -> Result<BirthAgeCertificate, NetworkError> {
    if !tau.is_finite()
        || tau < 0.0
        || !born.is_finite()
        || born < 0.0
        || nodes.iter().any(|(age, weight)| {
            !age.is_finite() || !(0.0..=1.0).contains(age) || !weight.is_finite() || *weight < 0.0
        })
    {
        return Err(NetworkError::InvalidInput);
    }
    let mut sorted: Vec<_> = nodes.iter().copied().filter(|(_, w)| *w > 0.0).collect();
    sorted.sort_by(|a, b| a.0.total_cmp(&b.0));
    Ok(BirthAgeCertificate {
        tau,
        born,
        input_nodes: nodes.len(),
        positive_nodes: sorted.len(),
        emitted: measure_certificate(&sorted, 0.0, born)?,
        survivors: measure_certificate(&sorted, tau, born)?,
    })
}

/// Diagnose the unchanged BR03 fitted rule. Its representational-resolution
/// errors propagate unchanged; no fallback node or replacement rule is used.
pub fn compare_fitted(
    tau: f64,
    born: f64,
    refinement: usize,
) -> Result<BirthAgeCertificate, NetworkError> {
    compare_nodes(tau, born, &fitted_birth::rule(tau, refinement)?)
}
