// BEGIN RESEARCH_POSITIVE_SOURCE_AGE_ACCESSOR
impl PreparedAbsorption {
    /// Exact prepared-node logarithmic slack loss, with no U-lo*N subtraction.
    pub fn research_positive_log_rhs(
        &self,
        ab: [f64; 3],
        nh: f64,
        first: &[f64],
        second: &[f64],
        log_amplitude: &[f64],
    ) -> Result<(Vec<f64>, IgmPhotoInput), ForwardError> {
        let _validation = self.evaluate(ab, nh, 0.0)?;
        let mut photo = IgmPhotoInput::default();
        let n = self.template.number.len();
        let mut dl = vec![0.0; n];
        let mut dr = vec![0.0; n];
        let mut cl = vec![0.0; n];
        let mut cr = vec![0.0; n];
        for node in &self.nodes {
            let k = node.cell;
            let lambda =
                HHeModel::controlled_fixture().c_cm_s * sum((0..3).map(|j| ab[j] * node.sigma[j]));
            let lo = self.template.support_lo[k];
            let hi = self.template.support_hi[k];
            for j in 0..3 {
                let rate = HHeModel::controlled_fixture().c_cm_s * nh * node.sigma[j] * node.number;
                if rate > 0.0 {
                    photo.gamma_s[j] += (log_amplitude[k] + rate.ln()).exp();
                }
                let heat = rate * node.excess_ev[j] * HHeModel::controlled_fixture().ev_erg;
                if heat > 0.0 {
                    photo.heat_erg_per_absorber_s[j] += (log_amplitude[k] + heat.ln()).exp();
                }
            }
            if hi == lo {
                compensated_add(&mut dl[k], &mut cl[k], lambda * node.number);
            } else {
                compensated_add(&mut dl[k], &mut cl[k], lambda * node.number * (node.q - lo));
                compensated_add(&mut dr[k], &mut cr[k], lambda * node.number * (hi - node.q));
            }
        }
        let mut out = vec![0.0; 2 * n];
        for k in 0..n {
            if self.template.number[k] == 0.0 {
                continue;
            }
            if !first[k].is_finite() || first[k] <= 0.0 {
                return Err(bad("POSITIVE_SLACK_UNDERFLOW_OR_DOMAIN"));
            }
            out[k] = -dl[k] / first[k];
            if self.template.support_hi[k] != self.template.support_lo[k] {
                if !second[k].is_finite() || second[k] <= 0.0 {
                    return Err(bad("POSITIVE_SLACK_UNDERFLOW_OR_DOMAIN"));
                }
                out[n + k] = -dr[k] / second[k];
            }
        }
        Ok((out, photo))
    }
}
// END RESEARCH_POSITIVE_SOURCE_AGE_ACCESSOR
