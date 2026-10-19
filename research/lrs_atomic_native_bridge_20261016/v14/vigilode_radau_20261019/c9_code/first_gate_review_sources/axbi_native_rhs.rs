//! Direct native reconstructed-node derivatives for opt-in external ODE adapters.
use super::*;
#[derive(Clone, Debug)]
pub struct NativeAbsorptionRates {
    pub number_dt: Vec<f64>,
    pub energy_ref_dt: Vec<f64>,
    /// Derivative of Uref - support_lo*N, accumulated directly at nodes.
    pub energy_offset_dt: Vec<f64>,
    pub photo: IgmPhotoInput,
    pub absorbed_per_h_s: [f64; 3],
    pub binding_ev_per_h_s: f64,
    pub heat_ev_per_h_s: f64,
}
impl PreparedAbsorption {
    /// No finite-step subtraction, attenuation, CFL, or state projection.
    pub fn native_rates(
        &self,
        absorber_cm3: [f64; 3],
        n_h_cm3: f64,
    ) -> Result<NativeAbsorptionRates, ForwardError> {
        if !absorber_cm3.iter().all(|&x| nonnegative(x)) || !n_h_cm3.is_finite() || n_h_cm3 <= 0.0 {
            return Err(bad("AXBI_COVARIANT_OPACITY_DOMAIN"));
        }
        let m = HHeModel::controlled_fixture();
        let cells = self.template.number.len();
        let mut r = NativeAbsorptionRates {
            number_dt: vec![0.; cells],
            energy_ref_dt: vec![0.; cells],
            energy_offset_dt: vec![0.; cells],
            photo: IgmPhotoInput::default(),
            absorbed_per_h_s: [0.; 3],
            binding_ev_per_h_s: 0.,
            heat_ev_per_h_s: 0.,
        };
        let mut cn = vec![0.; cells];
        let mut cu = vec![0.; cells];
        let mut co = vec![0.; cells];
        for node in &self.nodes {
            let mut total = 0.;
            for j in 0..3 {
                let photo = m.c_cm_s * n_h_cm3 * node.sigma[j] * node.number;
                r.photo.gamma_s[j] += photo;
                r.photo.heat_erg_per_absorber_s[j] += photo * node.excess_ev[j] * m.ev_erg;
                let event = m.c_cm_s * absorber_cm3[j] * node.sigma[j] * node.number;
                r.absorbed_per_h_s[j] += event;
                r.binding_ev_per_h_s += event * m.threshold_ev[j];
                r.heat_ev_per_h_s += event * node.excess_ev[j];
                total += event;
            }
            compensated_add(&mut r.number_dt[node.cell], &mut cn[node.cell], -total);
            compensated_add(
                &mut r.energy_ref_dt[node.cell],
                &mut cu[node.cell],
                -node.q * total,
            );
            compensated_add(
                &mut r.energy_offset_dt[node.cell],
                &mut co[node.cell],
                -(node.q - self.template.support_lo[node.cell]) * total,
            );
        }
        if !r
            .number_dt
            .iter()
            .chain(&r.energy_ref_dt)
            .chain(&r.energy_offset_dt)
            .all(|v| v.is_finite())
            || !r
                .photo
                .gamma_s
                .iter()
                .chain(&r.photo.heat_erg_per_absorber_s)
                .chain(&r.absorbed_per_h_s)
                .all(|&v| nonnegative(v))
            || !nonnegative(r.binding_ev_per_h_s)
            || !nonnegative(r.heat_ev_per_h_s)
        {
            return Err(bad("AXBI_NATIVE_RHS_NONFINITE"));
        }
        Ok(r)
    }
}
