//! Independent resolution controls for a study, not a new physical integrator.
use rei_iso_couple_reference::{
    full_network::NetworkError, positive_spectral::SpectralMode,
    retarded_transport::RetardedControls,
};
pub fn controls(
    split: bool,
    birth: usize,
    opacity: usize,
) -> Result<RetardedControls, NetworkError> {
    RetardedControls::new(
        birth,
        opacity,
        if split {
            SpectralMode::SplitPositiveGauss3
        } else {
            SpectralMode::OriginalCellMean
        },
    )
}
