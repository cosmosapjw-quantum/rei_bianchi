//! Collisionless prescribed-axisymmetric packet ledger; no source or absorber is coupled here.
use crate::{ForwardError, GeometrySnapshot, PhotonBins, PhotonGrid, RadiationState};
#[derive(Clone, Debug, PartialEq)]
pub struct AxisymPhotonLedgerContract {
    pub grid: PhotonGrid,
}
#[derive(Clone, Debug, PartialEq)]
pub struct AxisymPhotonStep {
    pub before: PhotonBins,
    pub after: PhotonBins,
    pub transported: RadiationState,
    pub number_change_cm3: f64,
    /// Difference induced by finite bin deposition only; not a transport loss.
    pub remap_count_residual_cm3: f64,
    pub energy_change_ev_cm3: f64,
}
fn finite(x: f64) -> Result<f64, ForwardError> {
    if x.is_finite() {
        Ok(x)
    } else {
        Err(ForwardError::InvalidInput("AXISYM_RADIATION_OVERFLOW"))
    }
}
impl AxisymPhotonLedgerContract {
    pub fn new(energy_edges_ev: Vec<f64>, mu_edges: Vec<f64>) -> Result<Self, ForwardError> {
        Ok(Self {
            grid: PhotonGrid::new(energy_edges_ev, mu_edges, 1)?,
        })
    }
    pub fn collisionless_step(
        &self,
        state: &RadiationState,
        to: GeometrySnapshot,
    ) -> Result<AxisymPhotonStep, ForwardError> {
        let before = state.remap(&self.grid)?;
        let transported = state.transport(to)?;
        let after = transported.remap(&self.grid)?;
        let packet_n0 = state.comoving_photon_count()?;
        let packet_n1 = transported.comoving_photon_count()?;
        if packet_n0.to_bits() != packet_n1.to_bits() {
            return Err(ForwardError::InvalidInput("AXISYM_PHOTON_NUMBER"));
        }
        let n0 = before.total_count()?;
        let n1 = after.total_count()?;
        let e0 = before.total_energy_ev_cm3()?;
        let e1 = after.total_energy_ev_cm3()?;
        Ok(AxisymPhotonStep {
            before,
            after,
            transported,
            number_change_cm3: finite(packet_n1 - packet_n0)?,
            remap_count_residual_cm3: finite(n1 - n0)?,
            energy_change_ev_cm3: finite(e1 - e0)?,
        })
    }
}
