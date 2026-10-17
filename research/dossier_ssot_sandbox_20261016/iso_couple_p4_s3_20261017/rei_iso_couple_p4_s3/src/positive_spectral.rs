//! Retarded P4/S3 opt-in positive within-cell spectral reference.
//! H/He/D photo threshold-aware quadrature; source photon count per immutable
//! MD14 spectral owner cell is preserved, no replacement of original owners.
//! The manufactured D binding threshold and the Verner H fit threshold differ.
use crate::axbi_sources::AxbiSource;
use crate::full_network::NetworkError;
use crate::source_age::Cohort;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SpectralMode {
    OriginalCellMean,
    SplitPositiveGauss3,
}

#[derive(Clone, Copy, Debug)]
pub struct SpectralNode {
    pub energy_ev: f64,
    /// Fraction of this original source cell's photon number, normalized to one.
    pub fraction: f64,
}

const GL3: [(f64, f64); 3] = [
    (-0.7745966692414834, 5.0 / 9.0),
    (0.0, 8.0 / 9.0),
    (0.7745966692414834, 5.0 / 9.0),
];

fn blackbody_number_shape(energy_ev: f64) -> f64 {
    let constants = crate::HHeModel::controlled_fixture();
    let kt_ev = 50_000.0 * constants.kb_erg_k / constants.ev_erg;
    energy_ev * energy_ev / (energy_ev / kt_ev).exp_m1()
}

/// Positive spectral quadrature, additionally segmented at `chi_D`.
/// The Verner HI fit edge is 13.60 eV, lower endpoint of the source support;
/// original HeI/HeII spectral boundaries are 24.59 and 54.42 eV.
/// Individual photon numbers are renormalized to the exact owner-cell fraction.
pub fn owner_cell_nodes(
    source: &AxbiSource,
    source_cell: usize,
    d_threshold_ev: f64,
    mode: SpectralMode,
) -> Result<Vec<SpectralNode>, NetworkError> {
    let cell = source
        .spectral_cells
        .get(source_cell)
        .ok_or(NetworkError::InvalidInput)?;
    if !d_threshold_ev.is_finite()
        || d_threshold_ev <= 0.0
        || !cell.lower_ev.is_finite()
        || !cell.upper_ev.is_finite()
        || cell.lower_ev >= cell.upper_ev
        || cell.photon_fraction <= 0.0
    {
        return Err(NetworkError::InvalidInput);
    }
    if mode == SpectralMode::OriginalCellMean {
        return Ok(vec![SpectralNode {
            energy_ev: cell.energy_ev,
            fraction: 1.0,
        }]);
    }
    let mut endpoints = vec![cell.lower_ev];
    if d_threshold_ev > cell.lower_ev && d_threshold_ev < cell.upper_ev {
        endpoints.push(d_threshold_ev);
    }
    endpoints.push(cell.upper_ev);
    let mut result = Vec::with_capacity(6);
    let mut normalization = 0.0;
    for seg in endpoints.windows(2) {
        let center = 0.5 * (seg[0] + seg[1]);
        let half = 0.5 * (seg[1] - seg[0]);
        for (node, weight) in GL3 {
            let energy = center + half * node;
            let probability = half * weight * blackbody_number_shape(energy);
            if !probability.is_finite() || probability <= 0.0 {
                return Err(NetworkError::NonFinite);
            }
            normalization += probability;
            result.push(SpectralNode {
                energy_ev: energy,
                fraction: probability,
            });
        }
    }
    if !normalization.is_finite() || normalization <= 0.0 {
        return Err(NetworkError::NonFinite);
    }
    for node in &mut result {
        node.fraction /= normalization;
    }
    Ok(result)
}

/// Split a batch of native owner-cell cohorts into quadrature nodes.
/// No clipping; photon number within each original cell and each angle retained.
pub fn expand_births(
    source: &AxbiSource,
    born: &[Cohort],
    d_threshold_ev: f64,
    mode: SpectralMode,
) -> Result<Vec<Cohort>, NetworkError> {
    if mode == SpectralMode::OriginalCellMean {
        return Ok(born.to_vec());
    }
    let mut nodes_per_cell = Vec::with_capacity(source.spectral_cells.len());
    for i in 0..source.spectral_cells.len() {
        nodes_per_cell.push(owner_cell_nodes(source, i, d_threshold_ev, mode)?);
    }
    let mut out = Vec::with_capacity(born.len() * 4);
    for co in born {
        let nodes = nodes_per_cell
            .get(co.spectral_index)
            .ok_or(NetworkError::InvalidInput)?;
        for node in nodes {
            let mut c = co.clone();
            c.energy_at_birth_ev = node.energy_ev;
            c.n_comoving_m3 *= node.fraction;
            out.push(c);
        }
    }
    Ok(out)
}
