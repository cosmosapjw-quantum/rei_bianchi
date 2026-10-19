//! Additive SSPRK(2,2) absorption of the native reconstructed moment system.
//! Both forward Euler stages use the same frozen gas and physical geometry.
use super::*;

#[derive(Clone, Debug)]
pub struct Ssprk2AbsorptionReport {
    pub absorption: AbsorptionResult,
    pub max_tau_stage1: f64,
    pub max_tau_stage2: f64,
    pub nodes_stage1: usize,
    pub nodes_stage2: usize,
    pub diagnostics_stage1: QuadratureDiagnostics,
    pub diagnostics_stage2: QuadratureDiagnostics,
}
impl PreparedAbsorption {
    /// Largest actual native quadrature-node absorption rate, in proper s^-1.
    pub fn max_node_rate(&self, absorber_cm3: [f64; 3]) -> Result<f64, ForwardError> {
        if !absorber_cm3.iter().all(|&x| nonnegative(x)) {return Err(bad("AXBI_COVARIANT_OPACITY_DOMAIN"));}
        let c=HHeModel::controlled_fixture().c_cm_s;
        let mut max_rate=0.0_f64;
        for node in &self.nodes {
            let rate=c*sum((0..3).map(|j|absorber_cm3[j]*node.sigma[j]));
            if !nonnegative(rate) {return Err(bad("AXBI_SSP_RATE_DOMAIN"));}
            max_rate=max_rate.max(rate);
        }
        Ok(max_rate)
    }
    /// Native-node forward Euler map. Rejects a violated positivity CFL.
    /// No stage clipping, subcycling, or replacement attenuation is performed.
    pub fn evaluate_forward_euler(&self, absorber_cm3:[f64;3], n_h_cm3:f64, dt_s:f64)
        ->Result<AbsorptionResult,ForwardError> {
        if !absorber_cm3.iter().all(|&x| nonnegative(x))
            || !n_h_cm3.is_finite()
            || n_h_cm3 <= 0.0
            || !nonnegative(dt_s)
        {
            return Err(bad("AXBI_COVARIANT_OPACITY_DOMAIN"));
        }
        let model = HHeModel::controlled_fixture();
        let mut state = self.template.clone();
        state.number.fill(0.0);
        state.energy_ref.fill(0.0);
        let mut out = AbsorptionResult {
            state,
            photo: IgmPhotoInput::default(),
            absorbed_per_h: [0.0; 3],
            binding_ev_per_h: 0.0,
            heat_ev_per_h: 0.0,
        };
        let mut count_correction = vec![0.0; out.state.number.len()];
        let mut energy_correction = vec![0.0; out.state.number.len()];
        let upper_anchor: Vec<_> = (0..out.state.number.len())
            .map(|k| {
                self.template.energy_ref[k] - self.template.support_lo[k] * self.template.number[k]
                    > self.template.support_hi[k] * self.template.number[k]
                        - self.template.energy_ref[k]
            })
            .collect();
        let mut absorbed_cell = vec![false; out.state.number.len()];
        for node in &self.nodes {
            let opacity = sum((0..3).map(|j| absorber_cm3[j] * node.sigma[j]));
            let tau = dt_s * model.c_cm_s * opacity;
            if !tau.is_finite() || tau > 1.0 { return Err(bad("AXBI_SSP_CFL")); }
            let surviving = node.number * (1.0 - tau);
            let interval_mean = node.number;
            absorbed_cell[node.cell] |= tau != 0.0;
            compensated_add(
                &mut out.state.number[node.cell],
                &mut count_correction[node.cell],
                surviving,
            );
            let offset = if upper_anchor[node.cell] {
                self.template.support_hi[node.cell] - node.q
            } else {
                node.q - self.template.support_lo[node.cell]
            };
            compensated_add(
                &mut out.state.energy_ref[node.cell],
                &mut energy_correction[node.cell],
                surviving * offset,
            );
            for j in 0..3 {
                let rate = model.c_cm_s * n_h_cm3 * node.sigma[j] * interval_mean;
                out.photo.gamma_s[j] += rate;
                out.photo.heat_erg_per_absorber_s[j] += rate * node.excess_ev[j] * model.ev_erg;
                let event = dt_s * model.c_cm_s * absorber_cm3[j] * node.sigma[j] * interval_mean;
                out.absorbed_per_h[j] += event;
                out.binding_ev_per_h += event * model.threshold_ev[j];
                out.heat_ev_per_h += event * node.excess_ev[j];
            }
        }
        for k in 0..out.state.number.len() {
            if !absorbed_cell[k] {
                out.state.number[k] = self.template.number[k];
                out.state.energy_ref[k] = self.template.energy_ref[k];
            } else if out.state.number[k] == 0.0 {
                out.state.support_lo[k] = 0.0;
                out.state.support_hi[k] = 0.0;
            } else if upper_anchor[k] {
                out.state.energy_ref[k] =
                    out.state.support_hi[k].mul_add(out.state.number[k], -out.state.energy_ref[k]);
            } else {
                out.state.energy_ref[k] =
                    out.state.support_lo[k].mul_add(out.state.number[k], out.state.energy_ref[k]);
            }
        }
        if !out
            .state
            .number
            .iter()
            .chain(&out.state.energy_ref)
            .all(|&x| nonnegative(x))
            || !out
                .photo
                .gamma_s
                .iter()
                .chain(&out.photo.heat_erg_per_absorber_s)
                .chain(&out.absorbed_per_h)
                .all(|&x| nonnegative(x))
            || !nonnegative(out.binding_ev_per_h)
            || !nonnegative(out.heat_ev_per_h)
        {
            return Err(bad("AXBI_SSP_NONFINITE"));
        }
        Ok(out)
    }
}
impl CovariantTransport {
    /// SSPRK(2,2), re-reconstructing native closure at the second stage.
    /// The input is borrowed and is preserved on every failure.
    pub fn absorb_ssprk2(&self, initial:&PhotonState, geometry:&GeometrySnapshot,
        absorber_cm3:[f64;3], n_h_cm3:f64, dt_s:f64)
        ->Result<Ssprk2AbsorptionReport,ForwardError> {
        let p1=self.prepare(initial,geometry)?;
        let max_tau_stage1=dt_s*p1.max_node_rate(absorber_cm3)?;
        let r1=p1.evaluate_forward_euler(absorber_cm3,n_h_cm3,dt_s)?;
        self.validate_state(&r1.state)?;
        let p2=self.prepare(&r1.state,geometry)?;
        let max_tau_stage2=dt_s*p2.max_node_rate(absorber_cm3)?;
        let r2=p2.evaluate_forward_euler(absorber_cm3,n_h_cm3,dt_s)?;
        self.validate_state(&r2.state)?;
        let mut state=initial.clone();
        for k in 0..state.number.len() {
            if dt_s==0.0 || (initial.number[k]==r2.state.number[k] && initial.energy_ref[k]==r2.state.energy_ref[k]) {continue;}
            let n=0.5*initial.number[k]+0.5*r2.state.number[k];
            state.number[k]=n;
            if n==0.0 {
                state.energy_ref[k]=0.0;state.support_lo[k]=0.0;state.support_hi[k]=0.0;
            } else {
                let lo=initial.support_lo[k];let hi=initial.support_hi[k];
                if lo==hi {state.energy_ref[k]=lo*n;}
                else if initial.energy_ref[k]-lo*initial.number[k] <= hi*initial.number[k]-initial.energy_ref[k] {
                    let offset=0.5*(initial.energy_ref[k]-lo*initial.number[k])+0.5*(r2.state.energy_ref[k]-lo*r2.state.number[k]);
                    state.energy_ref[k]=lo.mul_add(n,offset);
                } else {
                    let offset=0.5*(hi*initial.number[k]-initial.energy_ref[k])+0.5*(hi*r2.state.number[k]-r2.state.energy_ref[k]);
                    state.energy_ref[k]=hi.mul_add(n,-offset);
                }
            }
        }
        self.validate_state(&state)?;
        let absorption=AbsorptionResult {
            state,
            photo:IgmPhotoInput {
                gamma_s:std::array::from_fn(|j|0.5*r1.photo.gamma_s[j]+0.5*r2.photo.gamma_s[j]),
                heat_erg_per_absorber_s:std::array::from_fn(|j|0.5*r1.photo.heat_erg_per_absorber_s[j]+0.5*r2.photo.heat_erg_per_absorber_s[j]),
            },
            absorbed_per_h:std::array::from_fn(|j|0.5*r1.absorbed_per_h[j]+0.5*r2.absorbed_per_h[j]),
            binding_ev_per_h:0.5*r1.binding_ev_per_h+0.5*r2.binding_ev_per_h,
            heat_ev_per_h:0.5*r1.heat_ev_per_h+0.5*r2.heat_ev_per_h,
        };
        Ok(Ssprk2AbsorptionReport {absorption,max_tau_stage1,max_tau_stage2,
            nodes_stage1:p1.node_count(),nodes_stage2:p2.node_count(),
            diagnostics_stage1:p1.diagnostics,diagnostics_stage2:p2.diagnostics})
    }
}
