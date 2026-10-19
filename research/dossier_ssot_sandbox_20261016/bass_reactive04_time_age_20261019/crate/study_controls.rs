//! Research-only orthogonal controls; leaves source, IC and physics kernels intact.
use rei_iso_couple_reference::{
    bass_reactive::BindingBridge,
    full_network::{NetworkConfig, NetworkError},
    positive_spectral::SpectralMode,
    retarded_transport::RetardedControls,
};
#[derive(Clone, Copy, Debug)]
pub struct AxisControls {
    pub birth_gl: usize,
    pub opacity: usize,
    pub spectrum: SpectralMode,
    pub cx_rtol: f64,
}
impl AxisControls {
    /// Validate completely before changing either receiver. CX absolute tolerance
    /// follows the declared 0.01*rtol ladder; work limits are never changed here.
    pub fn apply(
        self,
        bridge: &mut BindingBridge,
        config: &mut NetworkConfig,
    ) -> Result<(), NetworkError> {
        let retarded = RetardedControls::new(self.birth_gl, self.opacity, self.spectrum)?;
        let atol = 0.01 * self.cx_rtol;
        if !self.cx_rtol.is_finite()
            || self.cx_rtol <= 0.0
            || self.cx_rtol >= 1.0
            || !atol.is_finite()
            || atol <= 0.0
        {
            return Err(NetworkError::InvalidInput);
        }
        bridge.1 = retarded;
        config.cx_controls.rtol = self.cx_rtol;
        config.cx_controls.atol_normalized = atol;
        Ok(())
    }
}
