//! Positive-only resolution adapter; no grey projection is exposed.
//! All physical source/kernel modules remain unchanged. The inherited grey
//! constructor retains its64-bin guard; positive rays are not that representation.
use crate::axbi_sources::AxbiSource;
use crate::bianchi_i::{ConstantAxisymmetricBackground, GeometryBackground};
use crate::full_network::{FullState, NetworkConfig, NetworkError};
use crate::reflection_pool::{PoolLimits, ReflectionPooledBridge, RetardedDiagnostics};
use crate::retarded_transport::RetardedControls;
use crate::source_age::{AgeHistory, AgeStep, SourceAgeBridge};
pub struct PositiveStudyBridge {
    inner: ReflectionPooledBridge,
}
impl PositiveStudyBridge {
    pub fn new(
        nh0: f64,
        fesc: f64,
        cells: usize,
        angles: usize,
        geometry: ConstantAxisymmetricBackground,
        controls: RetardedControls,
    ) -> Result<Self, NetworkError> {
        let source = AxbiSource::new(nh0, fesc, cells, angles)
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        RetardedControls::new(
            controls.birth_gauss_nodes,
            controls.opacity_substeps,
            controls.spectrum,
        )?;
        let g = geometry
            .snapshot(geometry.time_domain_s[0])
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        let v = g
            .volume_factor()
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        source
            .at_redshift(1.0 / v.cbrt() - 1.0)
            .map_err(|_| NetworkError::InputOutsideDomain)?;
        // This private bridge is used ONLY by the positive-cohort operator.
        // All numerical/physical input validation is retained. The grey grouping
        // field is never read by this path; no MAX_PHOTON_BINS guard is changed.
        let base = SourceAgeBridge {
            source,
            geometry,
            spectral_groups_per_segment: [1, 1, 1],
        };
        Ok(Self {
            inner: ReflectionPooledBridge(base, controls, PoolLimits::default()),
        })
    }
    pub fn source(&self) -> &AxbiSource {
        &self.inner.0.source
    }
    pub fn geometry(&self) -> &ConstantAxisymmetricBackground {
        &self.inner.0.geometry
    }
    /// Exact constant-opacity continuous-source reference for this discrete
    /// spectrum, not a new gas-evolution algorithm. Total injected photons=1.
    pub fn frozen_spectrum(
        &self,
        gas: &crate::mixture_eos::MixtureState,
        conf: &NetworkConfig,
        duration_s: f64,
    ) -> Result<FrozenSpectralBudget, NetworkError> {
        if !duration_s.is_finite()
            || duration_s <= 0.0
            || conf.photon_source != crate::axbi_sources::SOURCE_ID
        {
            return Err(NetworkError::InvalidInput);
        }
        let mut out = FrozenSpectralBudget::default();
        let h = crate::HHeModel::controlled_fixture().threshold_ev;
        let chi = [h[0], h[1], h[2], conf.deuterium.chi_d_ev()];
        for (i, c) in self.source().spectral_cells.iter().enumerate() {
            for node in crate::positive_spectral::owner_cell_nodes(
                self.source(),
                i,
                chi[3],
                self.inner.1.spectrum,
            )? {
                let w = c.photon_fraction * node.fraction;
                let rates = self.inner.0.opacity_channels(node.energy_ev, gas, conf)?;
                let k: f64 = rates.iter().sum();
                let phi = crate::positive_birth_clock::photon_slab(k * duration_s)?;
                let survive = w * phi.new_surviving;
                let absorb = w * phi.new_absorbed;
                out.surviving_fraction += survive;
                out.injected_mean_energy_ev += w * node.energy_ev;
                out.surviving_energy_ev += survive * node.energy_ev;
                out.absorbed_energy_ev += absorb * node.energy_ev;
                if k > 0.0 {
                    for j in 0..4 {
                        let a = absorb * rates[j] / k;
                        out.events_per_injected_photon[j] += a;
                        out.heat_ev += a * (node.energy_ev - chi[j]);
                        out.binding_ev += a * chi[j];
                    }
                }
            }
        }
        Ok(out)
    }
    pub fn initial(
        &self,
        gas: FullState,
        conf: &NetworkConfig,
        t: f64,
    ) -> Result<AgeHistory, NetworkError> {
        self.inner.initial(gas, conf, t)
    }
    pub fn advance(
        &self,
        initial: &AgeHistory,
        conf: &NetworkConfig,
        dt: f64,
    ) -> Result<(AgeStep, RetardedDiagnostics), NetworkError> {
        self.inner.advance_with_diagnostics(initial, conf, dt)
    }
}

/// Energy quantities in eV per initially injected photon; number fractions
/// dimensionless. Fixed physical gas and no redshifting for this oracle only.
#[derive(Clone, Copy, Debug, Default)]
pub struct FrozenSpectralBudget {
    pub surviving_fraction: f64,
    pub events_per_injected_photon: [f64; 4],
    pub injected_mean_energy_ev: f64,
    pub surviving_energy_ev: f64,
    pub absorbed_energy_ev: f64,
    pub heat_ev: f64,
    pub binding_ev: f64,
}

/// Observer diagnostics over the complete live cohort inventory. No pruning,
/// remapping, or replacement of directional information is performed.
#[derive(Clone, Copy, Debug, Default)]
pub struct ObserverMoments {
    pub photons_com3: f64,
    pub energy_j_com3: f64,
    pub energy_p2_j_com3: f64,
    pub mean_age_s: f64,
}
pub fn observer_moments(
    state: &AgeHistory,
    geometry: &ConstantAxisymmetricBackground,
) -> Result<ObserverMoments, NetworkError> {
    let g = geometry
        .snapshot(state.time_s)
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    let mut out = ObserverMoments::default();
    let mut age_moment = 0.0;
    for co in &state.cohorts {
        let age = state.time_s - co.birth_time_s;
        if !age.is_finite() || age < 0.0 {
            return Err(NetworkError::InvalidInput);
        }
        let ray = co.ray_at(&g)?;
        let e = co.n_comoving_m3 * ray.energy_ev * crate::full_network::EV_J;
        out.photons_com3 += co.n_comoving_m3;
        out.energy_j_com3 += e;
        out.energy_p2_j_com3 += e * (3.0 * ray.direction[2] * ray.direction[2] - 1.0) * 0.5;
        age_moment += co.n_comoving_m3 * age;
    }
    if out.photons_com3 > 0.0 {
        out.mean_age_s = age_moment / out.photons_com3;
    }
    if [
        out.photons_com3,
        out.energy_j_com3,
        out.energy_p2_j_com3,
        out.mean_age_s,
    ]
    .iter()
    .any(|v| !v.is_finite())
    {
        return Err(NetworkError::NonFinite);
    }
    Ok(out)
}
