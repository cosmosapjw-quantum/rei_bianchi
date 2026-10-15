"""Scoped C7 v2 optional fixed-q support-aware closure.
Patches only experimental axbi_q_grid.rs, retains historical absorb_reconstructed.
"""
from pathlib import Path
p=Path(__file__).resolve().parents[2]/"rust/rei_microphysics/src/axbi_q_grid.rs"
s=p.read_text()
def replace(old,new):
    global s
    n=s.count(old)
    if n!=1:raise RuntimeError(f"Expected exactly one occurrence got {n}: {old[:70]}")
    s=s.replace(old,new,1)

replace("    moment_ref_ev: Vec<f64>,\n    n_energy: usize,",
        "    moment_ref_ev: Vec<f64>,\n    // Envelopes of actual emitted reference-q source support; zero if empty.\n    support_lower_ref_ev: Vec<f64>,\n    support_upper_ref_ev: Vec<f64>,\n    n_energy: usize,")
replace("            moment_ref_ev: vec![0.; n_cells],\n            n_energy,",
        "            moment_ref_ev: vec![0.; n_cells],\n            support_lower_ref_ev: vec![0.; n_cells],\n            support_upper_ref_ev: vec![0.; n_cells],\n            n_energy,")
replace("    pub fn ref_energy_moment(&self) -> &[f64] {\n        &self.moment_ref_ev\n    }\n",
        "    pub fn ref_energy_moment(&self) -> &[f64] {\n        &self.moment_ref_ev\n    }\n    pub fn support_bounds(&self) -> (&[f64], &[f64]) {\n        (&self.support_lower_ref_ev, &self.support_upper_ref_ev)\n    }\n")
replace("            + self.moment_ref_ev.capacity()\n            + self.edges.capacity()",
        "            + self.moment_ref_ev.capacity()\n            + self.support_lower_ref_ev.capacity()\n            + self.support_upper_ref_ev.capacity()\n            + self.edges.capacity()")
# Build support intervals before any state commit.
replace("        let mut ledger = QSourceLedger::default();\n        for j in 0..nmu {",
        "        let mut ledger = QSourceLedger::default();\n        let mut next_lo = self.support_lower_ref_ev.clone();\n        let mut next_hi = self.support_upper_ref_ev.clone();\n        for j in 0..nmu {")
needle="                ledger.added_photons_per_h += n;\n                ledger.added_energy_ev_per_h += r * u;"
replace(needle,
"""                if n > 0.0 {
                    let lo = self.edges[i].max(13.6 / r);
                    let hi = self.edges[i + 1].min(100.0 / r);
                    if !(lo.is_finite() && hi.is_finite() && lo < hi) {
                        return Err(invalid());
                    }
                    if self.number[k] > 0.0 {
                        next_lo[k] = next_lo[k].min(lo);
                        next_hi[k] = next_hi[k].max(hi);
                    } else {
                        next_lo[k] = lo;
                        next_hi[k] = hi;
                    }
                    let after_n = self.number[k] + n;
                    let after_mean = (self.moment_ref_ev[k] + u) / after_n;
                    if after_mean < next_lo[k] * (1.0 - 1e-10)
                       || after_mean > next_hi[k] * (1.0 + 1e-10) {
                        return Err(invalid());
                    }
                }
                ledger.added_photons_per_h += n;
                ledger.added_energy_ev_per_h += r * u;""")
replace("        for k in 0..self.cell_count() {\n            self.number[k] += add_n[k];\n            self.moment_ref_ev[k] += add_u[k];\n        }\n        Ok(ledger)",
        "        for k in 0..self.cell_count() {\n            self.number[k] += add_n[k];\n            self.moment_ref_ev[k] += add_u[k];\n        }\n        self.support_lower_ref_ev = next_lo;\n        self.support_upper_ref_ev = next_hi;\n        Ok(ledger)")
needle="""    pub fn absorb_reconstructed(
        &mut self,
        now: &GeometrySnapshot,
        neutrals: [f64; 3],
        duration_s: f64,
        threads: usize,
    ) -> Result<QReactionLedger, ForwardError> {
        now.volume_factor()?;"""
replacement="""    pub fn absorb_reconstructed(
        &mut self,
        now: &GeometrySnapshot,
        neutrals: [f64; 3],
        duration_s: f64,
        threads: usize,
    ) -> Result<QReactionLedger, ForwardError> {
        self.absorb_reconstructed_impl(now, neutrals, duration_s, threads, false)
    }
    /// Optional C7 support-limited closure. The support envelope is valid
    /// for the original continuously-positive broad MD14 source in the
    /// selected expanding background; no arbitrary spectral hardness bound.
    pub fn absorb_reconstructed_support(
        &mut self,
        now: &GeometrySnapshot,
        neutrals: [f64; 3],
        duration_s: f64,
        threads: usize,
    ) -> Result<QReactionLedger, ForwardError> {
        self.absorb_reconstructed_impl(now, neutrals, duration_s, threads, true)
    }
    fn absorb_reconstructed_impl(
        &mut self,
        now: &GeometrySnapshot,
        neutrals: [f64; 3],
        duration_s: f64,
        threads: usize,
        restricted: bool,
    ) -> Result<QReactionLedger, ForwardError> {
        now.volume_factor()?;"""
replace(needle,replacement)
needle="""        let edges = &self.edges;
        let chunks = std::thread::scope(|scope| -> Result<Vec<QReactionLedger>, ForwardError> {"""
replace(needle,"""        let edges = &self.edges;
        let lows = &self.support_lower_ref_ev;
        let highs = &self.support_upper_ref_ev;
        let chunks = std::thread::scope(|scope| -> Result<Vec<QReactionLedger>, ForwardError> {""")
needle="""            for ((n, u), a) in new_n
                .chunks_mut(span)
                .zip(new_u.chunks_mut(span))
                .zip(self.source.angular_cells.chunks(per_group))
            {"""
replace(needle,"""            for ((((n, u), low), high), a) in new_n
                .chunks_mut(span)
                .zip(new_u.chunks_mut(span))
                .zip(lows.chunks(span))
                .zip(highs.chunks(span))
                .zip(self.source.angular_cells.chunks(per_group))
            {""")
needle="""                                let loss = absorb_positive_bin(
                                    edges[i],
                                    edges[i + 1],
                                    n[k],"""
replace(needle,"""                                let left = if restricted { low[k] } else { edges[i] };
                                let right = if restricted { high[k] } else { edges[i + 1] };
                                if !(left > 0.0 && right > left) {
                                    return Err(invalid());
                                }
                                let loss = absorb_positive_bin(
                                    left,
                                    right,
                                    n[k],""")
p.write_text(s)
print(f"PATCHED {p}, bytes {len(s)}")
