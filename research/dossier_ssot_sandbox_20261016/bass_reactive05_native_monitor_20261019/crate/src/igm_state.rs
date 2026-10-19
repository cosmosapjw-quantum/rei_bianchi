//! Narrow FLRW H/He-only EOS reference adapter for importing PR150's exact
//! igm_thermal.rs point evaluator in P2 *regression tests*. It does not replace
//! the all-isotope `MixtureState` in the coupled reference.
use crate::{ForwardError, HHeModel, HHeState};
#[derive(Clone, Copy, Debug)]
pub struct IgmGasState {
    pub fractions: [f64; 3],
    pub w_erg_per_h: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct IgmEos {
    pub electron_density_cm3: f64,
    pub temperature_k: f64,
    pub u_erg_cm3: f64,
}
impl IgmGasState {
    pub fn eos(&self, n_h: f64, n_he: f64) -> Result<IgmEos, ForwardError> {
        if !n_h.is_normal()
            || n_h <= 0.0
            || !n_he.is_finite()
            || n_he < 0.0
            || !self.w_erg_per_h.is_normal()
            || self.w_erg_per_h <= 0.0
        {
            return Err(ForwardError::InvalidInput("AUDIT_IGM_EOS_DOMAIN"));
        }
        let mut model = HHeModel::controlled_fixture();
        model.n_h_cm3 = n_h;
        model.n_he_cm3 = n_he;
        let s = HHeState {
            fractions: self.fractions,
            u_erg_cm3: self.w_erg_per_h * n_h,
            photon_cm3: [0.0; 3],
            escaped_erg_cm3: 0.0,
        };
        model.validate_state(&s)?;
        let ne = model.electron_density(&s)?;
        let t = model.temperature(&s)?;
        if !t.is_normal() || t <= 0.0 {
            return Err(ForwardError::InvalidInput("AUDIT_IGM_EOS_DOMAIN"));
        }
        Ok(IgmEos {
            electron_density_cm3: ne,
            temperature_k: t,
            u_erg_cm3: s.u_erg_cm3,
        })
    }
}
