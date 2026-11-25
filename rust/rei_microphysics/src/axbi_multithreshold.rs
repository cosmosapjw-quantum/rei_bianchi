// Included in covariant_transport; same atomic fit edges and quadrature owner.
#[derive(Clone, Debug, PartialEq)]
pub struct ActiveBands {
    pub low: PhotonState,
    pub middle: PhotonState,
    pub high: PhotonState,
}
impl CovariantTransport {
    pub fn empty_bands(&self) -> ActiveBands {
        ActiveBands {
            low: self.empty_state(),
            middle: self.empty_state(),
            high: self.empty_state(),
        }
    }
    pub fn partition_bands(
        &self,
        p: &PhotonState,
        g: &GeometrySnapshot,
    ) -> Result<ActiveBands, ForwardError> {
        let a = self.partition_heii(p, g)?;
        let b = self.partition_edge(&a.below, g, 1)?;
        Ok(ActiveBands {
            low: b.below,
            middle: b.above,
            high: a.above,
        })
    }
    pub fn move_bands(
        &self,
        p: &ActiveBands,
        g: &GeometrySnapshot,
    ) -> Result<ActiveBands, ForwardError> {
        let mut out = self.empty_bands();
        for s in [&p.low, &p.middle, &p.high] {
            let a = self.partition_bands(s, g)?;
            out.low = self.merge_heii_states(&out.low, &a.low)?;
            out.middle = self.merge_heii_states(&out.middle, &a.middle)?;
            out.high = self.merge_heii_states(&out.high, &a.high)?;
        }
        Ok(out)
    }
    pub fn inject_bands(
        &self,
        g: &GeometrySnapshot,
        z: f64,
        dt: f64,
    ) -> Result<(ActiveBands, SourceLedger), ForwardError> {
        if !nonnegative(dt) {
            return Err(bad("AXBI_BANDS_SOURCE_DT"));
        }
        let amount = self.source.at_redshift(z)?.per_h_s * dt;
        if !nonnegative(amount) {
            return Err(bad("AXBI_BANDS_SOURCE_AMOUNT"));
        }
        let rays = self.ray_geometry(g)?;
        let mut p = self.empty_bands();
        let mut l = SourceLedger::default();
        for (j, r) in rays.iter().enumerate() {
            for (s, c) in self.source.spectral_cells.iter().enumerate() {
                if c.lower_ev / r.scale < self.edges[0]
                    || c.upper_ev / r.scale > *self.edges.last().unwrap()
                {
                    return Err(bad("AXBI_COVARIANT_SOURCE_OUTSIDE_GRID"));
                }
                let amp = amount * r.angular_weight * c.photon_fraction / self.source_norms[s];
                if amp == 0. {
                    continue;
                }
                for i in 0..self.n_energy() {
                    let lo = c.lower_ev.max(self.edges[i] * r.scale);
                    let hi = c.upper_ev.min(self.edges[i + 1] * r.scale);
                    if hi <= lo {
                        continue;
                    }
                    let t = FIT_THRESHOLDS_EV[1];
                    let u = FIT_THRESHOLDS_EV[2];
                    for (lower, upper, target) in [
                        (lo, hi.min(t), &mut p.low),
                        (lo.max(t), hi.min(u), &mut p.middle),
                        (lo.max(u), hi, &mut p.high),
                    ] {
                        if upper <= lower {
                            continue;
                        }
                        let (n, en) = source_moments(lower, upper);
                        let n = amp * n;
                        let en = amp * en;
                        let qlo = if lower == self.edges[i] * r.scale {
                            self.edges[i]
                        } else {
                            lower / r.scale
                        };
                        let qhi = if upper == self.edges[i + 1] * r.scale {
                            self.edges[i + 1]
                        } else {
                            upper / r.scale
                        };
                        add_support(target, j * self.n_energy() + i, n, en / r.scale, qlo, qhi);
                        l.added_photons_per_h += n;
                        l.added_energy_ev_per_h += en;
                    }
                }
            }
        }
        for a in [&p.low, &p.middle, &p.high] {
            self.validate_state(a)?
        }
        Ok((p, l))
    }
}
