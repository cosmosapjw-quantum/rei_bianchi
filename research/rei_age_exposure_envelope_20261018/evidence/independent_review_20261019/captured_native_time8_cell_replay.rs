#![allow(dead_code)]
#[derive(Debug)] enum ForwardError { InvalidInput(&'static str) }
mod closure { use super::ForwardError;
fn bad() -> ForwardError {
    ForwardError::InvalidInput("AXBI_Q_EXPONENTIAL_CLOSURE_DOMAIN")
}
fn valid(v: f64) -> bool {
    v.is_finite() && v >= 0.0
}
fn mean_x(beta: f64) -> f64 {
    let b = beta.abs();
    if b < 1e-3 {
        let b2 = beta * beta;
        beta * (1.0 / 3.0 - b2 / 45.0 + 2.0 * b2 * b2 / 945.0 - b2 * b2 * b2 / 4725.0)
    } else {
        beta.signum() * (1.0 + 2.0 / (2.0 * b).exp_m1() - 1.0 / b)
    }
}
fn variance_x(beta: f64) -> f64 {
    let b = beta.abs();
    if b < 1e-3 {
        let b2 = b * b;
        1.0 / 3.0 - b2 / 15.0 + 2.0 * b2 * b2 / 189.0
    } else if b > 30.0 {
        1.0 / (b * b)
    } else {
        1.0 / (b * b) - 1.0 / b.sinh().powi(2)
    }
}
#[derive(Clone, Copy, Debug)]
pub struct PositiveReconstruction {
    pub lower_ev: f64,
    pub upper_ev: f64,
    pub beta: f64,
    pub normalizer: f64,
}
impl PositiveReconstruction {
    pub fn mean_ev(&self) -> f64 {
        (self.lower_ev + self.upper_ev) * 0.5
            + (self.upper_ev - self.lower_ev) * 0.5 * mean_x(self.beta)
    }
}
pub fn positive_reconstruct(
    lo: f64,
    hi: f64,
    mean: f64,
) -> Result<PositiveReconstruction, ForwardError> {
    if !(lo.is_finite()
        && hi.is_finite()
        && mean.is_finite()
        && hi > lo
        && lo > 0.0
        && mean > lo
        && mean < hi)
    {
        return Err(bad());
    }
    let eta = (2.0 * mean - lo - hi) / (hi - lo);
    if eta.abs() >= 1.0 {
        return Err(bad());
    }
    let beta = if eta == 0.0 {
        0.0
    } else {
        let mut left = 0.0;
        let mut right = (2.0 / (1.0 - eta.abs())).max(2.0);
        if right > 25000.0 {
            return Err(bad());
        }
        let mut guess = if eta.abs() < 0.4 {
            3.0 * eta.abs()
        } else {
            1.0 / (1.0 - eta.abs())
        };
        guess = guess.clamp(left, right);
        for _ in 0..64 {
            let m = mean_x(guess);
            if m < eta.abs() {
                left = guess;
            } else {
                right = guess;
            }
            if (m - eta.abs()).abs() <= 2e-14 {
                break;
            }
            let deriv = variance_x(guess);
            let candidate = guess - (m - eta.abs()) / deriv;
            guess = if candidate.is_finite() && candidate > left && candidate < right {
                candidate
            } else {
                0.5 * (left + right)
            };
        }
        eta.signum() * guess
    };
    if (mean_x(beta) - eta).abs() > 2e-10 {
        return Err(bad());
    }
    let ab = beta.abs();
    let normalizer = if ab < 1e-5 {
        2.0 * (1.0 + beta * beta / 6.0 + beta.powi(4) / 120.0) * (-ab).exp()
    } else {
        -(-2.0 * ab).exp_m1() / ab
    };
    if !(normalizer.is_finite() && normalizer > 0.0) {
        return Err(bad());
    }
    Ok(PositiveReconstruction {
        lower_ev: lo,
        upper_ev: hi,
        beta,
        normalizer,
    })
}

}
use closure::positive_reconstruct;
pub const FIT_THRESHOLDS_EV: [f64; 3] = [13.60, 24.59, 54.42];
pub const MAX_NODES_PER_CELL: usize = 1024;
const X8: [f64; 8] = [
    -0.9602898564975363,
    -0.7966664774136267,
    -0.5255324099163290,
    -0.1834346424956498,
    0.1834346424956498,
    0.5255324099163290,
    0.7966664774136267,
    0.9602898564975363,
];
const W8: [f64; 8] = [
    0.1012285362903763,
    0.2223810344533745,
    0.3137066458778873,
    0.3626837833783619,
    0.3626837833783619,
    0.3137066458778873,
    0.2223810344533745,
    0.1012285362903763,
];
fn bad(tag: &'static str) -> ForwardError {
    ForwardError::InvalidInput(tag)
}
fn nonnegative(x: f64) -> bool {
    x.is_finite() && x >= 0.0
}
fn sum(xs: impl Iterator<Item = f64>) -> f64 {
    let (mut total, mut correction) = (0.0, 0.0);
    for x in xs {
        let y = x - correction;
        let next = total + y;
        correction = (next - total) - y;
        total = next;
    }
    total
}
fn compensated_add(total: &mut f64, correction: &mut f64, x: f64) {
    let y = x - *correction;
    let next = *total + y;
    *correction = (next - *total) - y;
    *total = next;
}
/// Evaluate the represented first moment relative to its nearer support end.
/// U == end*N forces an endpoint delta at binary64 moment resolution; this is
/// an exact equality branch, never a tolerance-based broad-support fallback.
fn support_mean(lo: f64, hi: f64, n: f64, u: f64) -> f64 {
    let lower_distance = u - lo * n;
    let upper_distance = hi * n - u;
    if lower_distance <= upper_distance {
        lo + lower_distance / n
    } else {
        hi - upper_distance / n
    }
}

#[derive(Clone, Copy, Debug, Default)]
pub struct QuadratureDiagnostics {
    pub max_count_relative_defect: f64,
    pub max_energy_relative_defect: f64,
    /// Explicit normalized exponential-tail bound for y > 48 (beta > 30).
    pub omitted_tail_number_bound_per_h: f64,
    pub omitted_tail_energy_bound_ev_per_h: f64,
    pub omitted_tail_endpoint_moment_bound_ev_per_h: f64,
    pub max_asymptotic_mean_defect_ev: f64,
}
fn cell_quadrature(
    lo: f64,
    hi: f64,
    n: f64,
    u: f64,
    r: f64,
    diagnostics: &mut QuadratureDiagnostics,
) -> Result<Vec<(f64, f64)>, ForwardError> {
    let mean = support_mean(lo, hi, n, u);
    if lo == hi {
        if u != lo * n {
            return Err(bad("AXBI_COVARIANT_DELTA_MOMENT"));
        }
        return Ok(vec![(lo, n)]);
    }
    if mean == lo || mean == hi {
        if mean < lo || mean > hi {
            return Err(bad("AXBI_COVARIANT_DELTA_MOMENT"));
        }
        return Ok(vec![(mean, n)]);
    }
    let width = hi - lo;
    let gap = (mean - lo).min(hi - mean);
    let beta = match positive_reconstruct(lo, hi, mean) {
        Ok(fit) => fit.beta,
        Err(_) => {
            // For |beta|>30, coth(beta)-1 differs from one by <1.76e-26.
            let b = width / (2.0 * gap);
            if !b.is_finite() || b <= 30.0 {
                return Err(bad("AXBI_COVARIANT_RECONSTRUCTION_DOMAIN"));
            }
            diagnostics.max_asymptotic_mean_defect_ev = diagnostics
                .max_asymptotic_mean_defect_ev
                .max(width * (-2.0 * b).exp() / -(-2.0 * b).exp_m1());
            if mean < 0.5 * (lo + hi) {
                -b
            } else {
                b
            }
        }
    };
    let steep = beta.abs();
    let mut points = Vec::new();
    points.push(lo);
    for cut in FIT_THRESHOLDS_EV {
        let q = cut / r;
        if q > lo && q < hi {
            points.push(q);
        }
    }
    points.push(hi);
    points.sort_by(f64::total_cmp);
    let mut base = Vec::new();
    if steep <= 30.0 {
        for pair in points.windows(2) {
            let panels = ((pair[1] - pair[0]) / width * 2.0 * steep / 3.0)
                .ceil()
                .max(1.0) as usize;
            for p in 0..panels {
                let a = pair[0] + (pair[1] - pair[0]) * p as f64 / panels as f64;
                let b = pair[0] + (pair[1] - pair[0]) * (p + 1) as f64 / panels as f64;
                let half = (b - a) * 0.5;
                for i in 0..8 {
                    let q = (a + b) * 0.5 + half * X8[i];
                    let x = 2.0 * (q - lo) / width - 1.0;
                    let weight = W8[i] * half / width * (beta * x - steep).exp();
                    if weight > 0.0 {
                        base.push((q, weight));
                    }
                }
            }
        }
    } else {
        let endpoint = if beta > 0.0 { hi } else { lo };
        let distance = width / (2.0 * steep);
        let ymax = (2.0 * steep).min(48.0);
        let mut ypoints = vec![0.0, ymax];
        for q in points {
            let y = (endpoint - q) * beta.signum() / distance;
            if y > 0.0 && y < ymax {
                ypoints.push(y);
            }
        }
        for p in 1..16 {
            let y = 3.0 * p as f64;
            if y < ymax {
                ypoints.push(y);
            }
        }
        ypoints.sort_by(f64::total_cmp);
        for pair in ypoints.windows(2) {
            let half = 0.5 * (pair[1] - pair[0]);
            for i in 0..8 {
                let y = 0.5 * (pair[0] + pair[1]) + half * X8[i];
                let q = endpoint - beta.signum() * distance * y;
                let weight = W8[i] * half * (-y).exp();
                if weight > 0.0 {
                    base.push((q, weight));
                }
            }
        }
        let tail = (-48.0_f64).exp() / -(-2.0 * steep).exp_m1();
        diagnostics.omitted_tail_number_bound_per_h += n * tail;
        diagnostics.omitted_tail_energy_bound_ev_per_h += n * hi * tail;
        diagnostics.omitted_tail_endpoint_moment_bound_ev_per_h += n * distance * 49.0 * tail;
    }
    if base.len() > MAX_NODES_PER_CELL || base.is_empty() {
        return Err(bad("AXBI_COVARIANT_QUADRATURE_CAP"));
    }
    let node_lo = base.iter().map(|x| x.0).fold(f64::INFINITY, f64::min);
    let node_hi = base.iter().map(|x| x.0).fold(f64::NEG_INFINITY, f64::max);
    if mean < node_lo || mean > node_hi {
        return Err(bad("AXBI_COVARIANT_QUADRATURE_CAP"));
    }
    let scale = gap;
    let eval = |lambda: f64| -> (Vec<f64>, f64, f64) {
        let logs: Vec<_> = base
            .iter()
            .map(|&(q, w)| w.ln() + lambda * (q - mean) / scale)
            .collect();
        let max = logs.iter().copied().fold(f64::NEG_INFINITY, f64::max);
        let weights: Vec<_> = logs.iter().map(|l| (l - max).exp()).collect();
        let total = sum(weights.iter().copied());
        let m = sum(base
            .iter()
            .zip(&weights)
            .map(|(&(q, _), w)| w * ((q - mean) / scale)))
            / total;
        let second = sum(base
            .iter()
            .zip(&weights)
            .map(|(&(q, _), w)| w * ((q - mean) / scale).powi(2)))
            / total;
        (weights, m, (second - m * m).max(0.0))
    };
    let (mut lower, mut upper) = (-1.0, 1.0);
    for _ in 0..32 {
        if eval(lower).1 <= 0.0 {
            break;
        }
        lower *= 2.0;
    }
    for _ in 0..32 {
        if eval(upper).1 >= 0.0 {
            break;
        }
        upper *= 2.0;
    }
    if eval(lower).1 > 0.0 || eval(upper).1 < 0.0 {
        return Err(bad("AXBI_COVARIANT_TILT_BRACKET"));
    }
    let mut lambda = 0.0;
    for _ in 0..80 {
        let (_, m, variance) = eval(lambda);
        if m.abs() < 8.0 * f64::EPSILON {
            break;
        }
        if m < 0.0 {
            lower = lambda;
        } else {
            upper = lambda;
        }
        let candidate = lambda - m / variance;
        lambda = if candidate.is_finite() && candidate > lower && candidate < upper {
            candidate
        } else {
            0.5 * (lower + upper)
        };
    }
    let (weights, _, _) = eval(lambda);
    let norm = sum(weights.iter().copied());
    let result: Vec<_> = base
        .iter()
        .zip(weights)
        .map(|(&(q, _), w)| (q, n * (w / norm)))
        .collect();
    let count_defect = (sum(result.iter().map(|x| x.1)) - n).abs();
    let energy_defect = (sum(result.iter().map(|x| x.0 * x.1)) - u).abs();
    let energy_scale = u.abs().max(n * width);
    println!("DETAIL,{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{},{}", mean, beta, lambda, eval(lambda).1, count_defect, 64.0*f64::EPSILON*n, energy_defect, 128.0*f64::EPSILON*energy_scale, energy_scale, scale, result.len(), result.iter().filter(|x| x.1==0.0).count());
    if count_defect > 64.0 * f64::EPSILON * n || energy_defect > 128.0 * f64::EPSILON * energy_scale
    {
        return Err(bad("AXBI_COVARIANT_MOMENT_FIT"));
    }
    diagnostics.max_count_relative_defect =
        diagnostics.max_count_relative_defect.max(count_defect / n);
    diagnostics.max_energy_relative_defect = diagnostics
        .max_energy_relative_defect
        .max(energy_defect / energy_scale);
    Ok(result)
}


fn main() {
 let lo=f64::from_bits(4623845976678756827u64);
 let hi=f64::from_bits(4625495657056071966u64);
 let n=f64::from_bits(240243477644326u64);
 let u=f64::from_bits(4094958919588752u64);
 let r=f64::from_bits(4607172967961653718u64);
 let mut d=QuadratureDiagnostics::default();
 let answer=cell_quadrature(lo,hi,n,u,r,&mut d);
 match answer { Ok(v)=>println!("RESULT,OK,{}",v.len()),Err(e)=>println!("RESULT,{:?},0",e), }
}
