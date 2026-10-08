//! A finite escaping E^-2 source and independent positive birth quadrature.
//!
//! The source is photons per H nucleus per proper second. Escape is already
//! included. No proper/comoving density conversion or a^3 factor is applied.
//! Energy weights use the analytic SED normalization, not a discrete adjustment:
//! their number and energy errors converge with energy-panel refinement.
use crate::igm_background::FlatFlrwBackground;
use crate::{verner_cutoff_ev, Absorber, AtomicProvider, ForwardError, HHeModel};

/// Constant escaping production with a photon-number SED proportional to E^-2.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ConstantSource {
    pub photons_per_h_per_s: f64,
    pub energy_min_ev: f64,
    pub energy_max_ev: f64,
}

/// Positive Gauss node for the analytically normalized photon-number SED.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct SourceEnergyNode {
    pub energy_ev: f64,
    pub number_weight: f64,
}

/// One positive packet emitted at an absolute ln(a) epoch.
///
/// Its energy at a later epoch x is `energy_ev * exp(ln_a - x)`; it must not be
/// redshifted from the initial history epoch. A schedule has no gas-step inputs.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Birth {
    pub ln_a: f64,
    pub energy_ev: f64,
    pub per_h: f64,
}

fn invalid() -> ForwardError {
    ForwardError::InvalidInput("IGM_SOURCE_DOMAIN")
}
fn positive(x: f64) -> Result<f64, ForwardError> {
    if x.is_normal() && x > 0.0 {
        Ok(x)
    } else {
        Err(invalid())
    }
}
fn nonnegative(x: f64) -> Result<f64, ForwardError> {
    if x == 0.0 {
        Ok(x)
    } else {
        positive(x)
    }
}
fn resource_error() -> ForwardError {
    ForwardError::InvalidInput("IGM_SOURCE_RESOURCE")
}

/// Two interior Gauss nodes and their common integration weight on [lo, hi].
/// Reject intervals too narrow to represent two ordered interior points rather
/// than silently placing a birth or energy node on an endpoint.
fn gauss_pair(lo: f64, hi: f64) -> Result<([f64; 2], f64), ForwardError> {
    if !lo.is_finite() || !hi.is_finite() {
        return Err(invalid());
    }
    let width = positive(hi - lo)?;
    let half = positive(0.5 * width)?;
    let offset = 1.0 / 3.0_f64.sqrt();
    let nodes = [lo + half * (1.0 - offset), lo + half * (1.0 + offset)];
    if !(lo < nodes[0] && nodes[0] < nodes[1] && nodes[1] < hi) {
        return Err(invalid());
    }
    Ok((nodes, half))
}

fn panel_edges(lo: f64, hi: f64, index: usize, count: usize) -> (f64, f64) {
    let width = hi - lo;
    let left = lo + width * index as f64 / count as f64;
    let right = if index + 1 == count {
        hi
    } else {
        lo + width * (index + 1) as f64 / count as f64
    };
    (left, right)
}

impl ConstantSource {
    /// Frozen synthetic fixture; these are not inferred cosmological sources.
    pub fn manufactured_v1() -> Self {
        Self {
            photons_per_h_per_s: 1e-15,
            energy_min_ev: 13.7,
            energy_max_ev: 100.0,
        }
    }

    fn normalization(&self) -> Result<f64, ForwardError> {
        nonnegative(self.photons_per_h_per_s)?;
        positive(self.energy_min_ev)?;
        positive(self.energy_max_ev)?;
        if self.energy_min_ev >= self.energy_max_ev {
            return Err(invalid());
        }
        // Reuse the provider's supported energy domain, without copying its
        // upper bound or cross-section fit into the source implementation.
        AtomicProvider::reference().cross_section(Absorber::HI, self.energy_max_ev)?;
        positive(positive(1.0 / self.energy_min_ev)? - positive(1.0 / self.energy_max_ev)?)
    }

    /// Composite two-point Gauss quadrature on every threshold-split segment.
    ///
    /// Binding energies and Verner fit cutoffs are separate segment boundaries.
    /// `panels_per_segment` refines only the energy quadrature. The returned
    /// weights approximate integral 1; they are deliberately not renormalized.
    pub fn energy_quadrature(
        &self,
        panels_per_segment: usize,
    ) -> Result<Vec<SourceEnergyNode>, ForwardError> {
        let normalization = self.normalization()?;
        if panels_per_segment == 0 {
            return Err(invalid());
        }
        let mut boundaries = vec![self.energy_min_ev, self.energy_max_ev];
        let binding = HHeModel::controlled_fixture().threshold_ev;
        let cutoffs = [Absorber::HI, Absorber::HeI, Absorber::HeII].map(verner_cutoff_ev);
        for edge in binding.into_iter().chain(cutoffs) {
            if edge > self.energy_min_ev && edge < self.energy_max_ev {
                boundaries.push(edge);
            }
        }
        boundaries.sort_by(f64::total_cmp);
        boundaries.dedup();
        let node_count = panels_per_segment
            .checked_mul(boundaries.len() - 1)
            .and_then(|count| count.checked_mul(2))
            .ok_or_else(resource_error)?;
        let mut nodes = Vec::new();
        nodes
            .try_reserve_exact(node_count)
            .map_err(|_| resource_error())?;
        for edges in boundaries.windows(2) {
            for panel in 0..panels_per_segment {
                let (left, right) = panel_edges(edges[0], edges[1], panel, panels_per_segment);
                let (energies, half_width) = gauss_pair(left, right)?;
                for energy_ev in energies {
                    let number_weight = positive(
                        positive(positive(half_width / normalization)? / energy_ev)? / energy_ev,
                    )?;
                    nodes.push(SourceEnergyNode {
                        energy_ev,
                        number_weight,
                    });
                }
            }
        }
        Ok(nodes)
    }
}

/// Build births from positive Gauss2 quadrature of j/H on fixed ln(a) panels.
///
/// This schedule depends only on the given endpoints and quadrature controls,
/// never on adaptive gas timesteps. Each epoch contains the same sorted energy
/// nodes. Insert births once at their stored epoch and evolve them only later.
/// Zero production yields no births, including no zero-weight packets.
///
/// Nonzero subnormal intermediates and unrepresentable interior nodes are
/// outside this numerical contract. Checked allocation errors are reported;
/// callers must additionally impose their configured packet-count limit.
#[allow(clippy::too_many_arguments)]
pub fn build_birth_schedule(
    background: &FlatFlrwBackground,
    source: &ConstantSource,
    ln_a_start: f64,
    ln_a_end: f64,
    birth_panels: usize,
    energy_panels_per_segment: usize,
) -> Result<Vec<Birth>, ForwardError> {
    if birth_panels == 0 || !ln_a_start.is_finite() || !ln_a_end.is_finite() {
        return Err(invalid());
    }
    positive(ln_a_end - ln_a_start)?;
    background.at_ln_a(ln_a_start)?;
    background.at_ln_a(ln_a_end)?;
    let energy_nodes = source.energy_quadrature(energy_panels_per_segment)?;
    let birth_count = birth_panels
        .checked_mul(2)
        .and_then(|count| count.checked_mul(energy_nodes.len()))
        .ok_or_else(resource_error)?;
    if source.photons_per_h_per_s == 0.0 {
        return Ok(Vec::new());
    }
    let mut births = Vec::new();
    births
        .try_reserve_exact(birth_count)
        .map_err(|_| resource_error())?;
    for panel in 0..birth_panels {
        let (left, right) = panel_edges(ln_a_start, ln_a_end, panel, birth_panels);
        let (epochs, half_width) = gauss_pair(left, right)?;
        for ln_a in epochs {
            let point = background.at_ln_a(ln_a)?;
            let proper_time_weight = positive(half_width / point.hubble_per_s)?;
            let emitted_per_h = positive(source.photons_per_h_per_s * proper_time_weight)?;
            for node in &energy_nodes {
                births.push(Birth {
                    ln_a,
                    energy_ev: node.energy_ev,
                    per_h: positive(emitted_per_h * node.number_weight)?,
                });
            }
        }
    }
    Ok(births)
}
