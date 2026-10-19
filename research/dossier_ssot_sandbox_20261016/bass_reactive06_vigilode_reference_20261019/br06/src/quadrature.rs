//! Recovery R1 positive Gauss adapter; previous wrapper bytes were not recovered.
use crate::{Error, Result};
use gauss_quad::GaussLegendre;
use std::num::NonZeroUsize;

#[derive(Clone, Debug)]
pub struct PositiveGauss {
    pub nodes: Vec<(f64, f64)>,
    pub raw_weight_sum: f64,
}
impl PositiveGauss {
    pub fn new(degree: usize) -> Result<Self> {
        if !(1..=128).contains(&degree) {
            return Err(Error::InvalidInput("gauss_degree"));
        }
        let base = GaussLegendre::new(NonZeroUsize::new(degree).unwrap());
        let mut nodes: Vec<(f64, f64)> = base
            .iter()
            .map(|(x, w)| ((1.0 + x) * 0.5, w * 0.5))
            .collect();
        nodes.sort_by(|a, b| a.0.total_cmp(&b.0));
        let raw_weight_sum: f64 = nodes.iter().map(|x| x.1).sum();
        if !raw_weight_sum.is_finite()
            || (raw_weight_sum - 1.0).abs() > 1e-12
            || nodes.iter().any(|(x, w)| {
                !x.is_finite() || *x <= 0.0 || *x >= 1.0 || !w.is_finite() || *w <= 0.0
            })
            || nodes.windows(2).any(|w| w[1].0 <= w[0].0)
        {
            return Err(Error::InvalidInput("gauss_positive_rule"));
        }
        for (_, w) in &mut nodes {
            *w /= raw_weight_sum;
        }
        Ok(Self {
            nodes,
            raw_weight_sum,
        })
    }
}

/// Same positive geometric age panels as the unchanged parent's fitted rule.
/// Degree changes birth quadrature independently of the panel refinement.
pub fn gauss_age_nodes(tau: f64, refinement: usize, degree: usize) -> Result<Vec<(f64, f64)>> {
    if !tau.is_finite() || tau < 0.0 || ![1, 2, 4, 8, 16].contains(&refinement) {
        return Err(Error::InvalidInput("birth_gauss_controls"));
    }
    let gauss = PositiveGauss::new(degree)?;
    let mut out = Vec::new();
    let mut left = 0.0;
    while left < 1.0 {
        let width_target = if tau <= 1.0 {
            1.0 / refinement as f64
        } else {
            (1.0 / tau + left).min(1.0) / refinement as f64
        };
        let right = (left + width_target).min(1.0);
        if right <= left || out.len() > 100_000 {
            return Err(Error::NoForwardProgress("birth_gauss_panels"));
        }
        for &(u, w) in &gauss.nodes {
            let age = left + (right - left) * u;
            let weight = (right - left) * w;
            if age <= left || age >= right || weight <= 0.0 {
                return Err(Error::NoForwardProgress("birth_gauss_clock"));
            }
            out.push((age, weight));
        }
        left = right;
    }
    Ok(out)
}
