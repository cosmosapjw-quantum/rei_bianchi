//! RUN09: subdivide the original positive graded birth panels, not the ODE grid.
//! Native source, gas, angle/energy support and optical seed remain unchanged.
use crate::{
    bass_optical_birth::BassOpticalBirthBridge,
    birth_layers::{BirthNode, graded_birth_nodes, graded_panels},
    full_network::{NetworkConfig, NetworkError},
    mixture_eos::MixtureState,
    positive_spectral::expand_births,
    retarded_transport::gauss_birth_nodes,
    source_age::Cohort,
};

/// `max_panels` bounds the final subdivided panels as well as the parent count.
pub fn refined_panels(
    tau: f64,
    growth: f64,
    max_panels: usize,
    subdivisions: usize,
) -> Result<Vec<(f64, f64)>, NetworkError> {
    if !(1..=64).contains(&subdivisions) {
        return Err(NetworkError::InvalidInput);
    }
    let base = graded_panels(tau, growth, max_panels)?;
    let total = base
        .len()
        .checked_mul(subdivisions)
        .ok_or(NetworkError::InvalidInput)?;
    if total > max_panels {
        return Err(NetworkError::InputOutsideDomain);
    }
    if subdivisions == 1 {
        return Ok(base);
    }
    let mut result = Vec::with_capacity(total);
    for (a, b) in base {
        for j in 0..subdivisions {
            let left = if j == 0 {
                a
            } else {
                a + (b - a) * (j as f64) / (subdivisions as f64)
            };
            let right = if j + 1 == subdivisions {
                b
            } else {
                a + (b - a) * ((j + 1) as f64) / (subdivisions as f64)
            };
            if !left.is_finite() || !right.is_finite() || right <= left {
                return Err(NetworkError::NoForwardProgress);
            }
            result.push((left, right));
        }
    }
    Ok(result)
}
pub fn refined_birth_nodes(
    tau: f64,
    growth: f64,
    max_panels: usize,
    subdivisions: usize,
) -> Result<Vec<BirthNode>, NetworkError> {
    // Exact parent arithmetic when no refinement was requested.
    if subdivisions == 1 {
        return graded_birth_nodes(tau, growth, max_panels);
    }
    let panels = refined_panels(tau, growth, max_panels, subdivisions)?;
    let gl = gauss_birth_nodes(4)?;
    let mut nodes = Vec::with_capacity(4 * panels.len());
    for (a, b) in panels {
        for &(u, w) in &gl {
            let v = a + (b - a) * u;
            let weight = (b - a) * w;
            if !v.is_finite() || v <= a || v >= b || !weight.is_finite() || weight <= 0. {
                return Err(NetworkError::NoForwardProgress);
            }
            nodes.push(BirthNode {
                remaining_fraction: v,
                weight,
            });
        }
    }
    Ok(nodes)
}
/// Reuse the original source-birth provider on each new quadrature node.
/// No later gas/opacity operation, clipping, or weight renormalization occurs here.
pub fn emit_refined_births(
    bridge: &BassOpticalBirthBridge,
    t0: f64,
    dt: f64,
    config: &NetworkConfig,
    gas_mid: &MixtureState,
    subdivisions: usize,
) -> Result<(Vec<Cohort>, f64, usize), NetworkError> {
    if subdivisions == 1 {
        return bridge.emit_births(t0, dt, config, gas_mid);
    }
    if !t0.is_finite()
        || !dt.is_finite()
        || dt <= 0.
        || config.photon_source != crate::axbi_sources::SOURCE_ID
        || bridge.1.birth_gauss_nodes != 4
        || bridge.2.max_cohorts == 0
    {
        return Err(NetworkError::InvalidInput);
    }
    let tau = bridge.optical_seed(gas_mid, config, t0, dt)?;
    let nodes = refined_birth_nodes(tau, bridge.2.growth, bridge.2.max_panels, subdivisions)?;
    let panel_count = nodes.len() / 4;
    let mut births = Vec::new();
    let t1 = t0 + dt;
    for node in nodes {
        let tb = t1 - node.remaining_fraction * dt;
        if !tb.is_finite() || tb <= t0 || tb >= t1 {
            return Err(NetworkError::NoForwardProgress);
        }
        let batch = bridge.0.source_births(tb, dt * node.weight)?;
        let expanded = expand_births(
            &bridge.0.source,
            &batch,
            config.deuterium.chi_d_ev(),
            bridge.1.spectrum,
        )?;
        if births.len() + expanded.len() > bridge.2.max_cohorts {
            return Err(NetworkError::InputOutsideDomain);
        }
        births.extend(expanded);
    }
    Ok((births, tau, panel_count))
}
