//! RUN11 opt-in first-cell replacement; original source providers stay immutable.
use crate::{
    HHeModel,
    axbi_sources::SpectralCell,
    bass_geometry::BassGeometry,
    full_network::NetworkError,
    source_age::Cohort,
    spectral_edge_support::{Cell, Rule, refine_cell},
};
use std::collections::HashMap;
/// BassGeometry admission checks H>0 and -1/2<b_X<1 on all Hermite intervals.
/// Therefore actual Killing rays decrease; no endpoint-only monotonicity claim.
/// Each parent ray keeps birth clock/direction and all nonzero-cell tuples.
pub fn refine_first_cell(
    cohorts: &[Cohort],
    cell: SpectralCell,
    g: &BassGeometry,
    end_s: f64,
    d_ev: f64,
    m: usize,
) -> Result<Vec<Cohort>, NetworkError> {
    if !(1..=64).contains(&m) || !d_ev.is_finite() || d_ev <= 13.6 {
        return Err(NetworkError::InvalidInput);
    }
    let end = g.point_at_time(end_s)?.snapshot()?;
    let model = HHeModel::controlled_fixture();
    let kt = model.kb_erg_k / model.ev_erg * 50000.;
    let c = Cell {
        lower_ev: cell.lower_ev,
        upper_ev: cell.upper_ev,
        owner_mean_ev: cell.energy_ev,
        photon_fraction: cell.photon_fraction,
    };
    let mut cache: HashMap<(u64, u64), Rule> = HashMap::new();
    let mut out = Vec::new();
    for co in cohorts {
        if co.spectral_index != 0 {
            out.push(co.clone());
            continue;
        }
        if co.birth_time_s >= end_s || co.energy_at_birth_ev.to_bits() != cell.energy_ev.to_bits() {
            return Err(NetworkError::SourceMismatch);
        }
        let eta = co.ray_at(&end)?.energy_ev / co.energy_at_birth_ev;
        let key = (co.birth_time_s.to_bits(), eta.to_bits());
        if let std::collections::hash_map::Entry::Vacant(e) = cache.entry(key) {
            e.insert(
                refine_cell(c, eta, &[13.6, d_ev], m, kt)
                    .map_err(|_| NetworkError::InputOutsideDomain)?,
            );
        }
        for node in &cache[&key].nodes {
            let mut q = co.clone();
            q.energy_at_birth_ev = node.energy_ev;
            q.n_comoving_m3 = co.n_comoving_m3 * (node.photon_fraction / cell.photon_fraction);
            if !q.n_comoving_m3.is_finite() || q.n_comoving_m3 <= 0. {
                return Err(NetworkError::NonFinite);
            }
            out.push(q);
        }
    }
    Ok(out)
}
