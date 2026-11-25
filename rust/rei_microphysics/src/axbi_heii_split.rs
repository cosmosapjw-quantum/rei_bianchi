// Included in axbi_covariant_transport: reuse its exact moment and source owner.
// Opt-in spectral owner; the coupled DriverState and checkpoint schema are unchanged.
#[derive(Clone, Debug, PartialEq)]
pub struct HeiiPools {
    pub below: PhotonState,
    pub above: PhotonState,
}
#[derive(Clone, Debug)]
pub struct HeiiAbsorption {
    pub state: HeiiPools,
    pub photo: IgmPhotoInput,
    pub absorbed_per_h: [f64; 3],
    pub binding_ev_per_h: f64,
    pub heat_ev_per_h: f64,
}
impl CovariantTransport {
    pub fn empty_heii(&self) -> HeiiPools {
        HeiiPools {
            below: self.empty_state(),
            above: self.empty_state(),
        }
    }
    fn merge_heii_states(
        &self,
        a: &PhotonState,
        b: &PhotonState,
    ) -> Result<PhotonState, ForwardError> {
        self.validate_state(a)?;
        self.validate_state(b)?;
        let mut out = a.clone();
        for k in 0..self.cell_count() {
            let n0 = a.number[k];
            let n1 = b.number[k];
            if n1 == 0. {
                continue;
            }
            if n0 == 0. {
                add_support(
                    &mut out,
                    k,
                    n1,
                    b.energy_ref[k],
                    b.support_lo[k],
                    b.support_hi[k],
                );
                continue;
            }
            let lo = a.support_lo[k].min(b.support_lo[k]);
            let hi = a.support_hi[k].max(b.support_hi[k]);
            let n = n0 + n1;
            let u0 = a.energy_ref[k];
            let u1 = b.energy_ref[k];
            let l = (u0 - lo * n0) + (u1 - lo * n1);
            let h = (hi * n0 - u0) + (hi * n1 - u1);
            let u = if l <= h {
                lo.mul_add(n, l)
            } else {
                hi.mul_add(n, -h)
            };
            if (u - u0 - u1).abs() > 128. * f64::EPSILON * (u0 + u1).abs() {
                return Err(bad("AXBI_HEII_MERGE_DEFECT"));
            }
            out.number[k] = n;
            out.energy_ref[k] = u;
            out.support_lo[k] = lo;
            out.support_hi[k] = hi;
        }
        self.validate_state(&out)?;
        Ok(out)
    }
    pub fn partition_heii(
        &self,
        p: &PhotonState,
        g: &GeometrySnapshot,
    ) -> Result<HeiiPools, ForwardError> {
        self.validate_state(p)?;
        let rays = self.ray_geometry(g)?;
        let mut out = self.empty_heii();
        for k in 0..self.cell_count() {
            let (n, u, lo, hi) = (
                p.number[k],
                p.energy_ref[k],
                p.support_lo[k],
                p.support_hi[k],
            );
            if n == 0. {
                continue;
            }
            let r = rays[k / self.n_energy()].scale;
            let t = FIT_THRESHOLDS_EV[2];
            let cut = t / r;
            if hi * r < t {
                add_support(&mut out.below, k, n, u, lo, hi);
                continue;
            }
            if lo * r >= t {
                add_support(&mut out.above, k, n, u, lo, hi);
                continue;
            }
            // A delta at the boundary belongs above; a non-delta support ending
            // there has no atom unless its moments force the endpoint.
            let q = cell_quadrature(lo, hi, n, u, r, &mut QuadratureDiagnostics::default())?;
            let a: Vec<_> = q.iter().copied().filter(|(v, _)| v * r < t).collect();
            let b: Vec<_> = q.iter().copied().filter(|(v, _)| v * r >= t).collect();
            let al = lo;
            let ah = hi.min(cut);
            let bl = lo.max(cut);
            let bh = hi;
            let (an, au) = restricted_moments(&a, al, ah);
            let (bn, bu) = restricted_moments(&b, bl, bh);
            if (an + bn - n).abs() > 64. * f64::EPSILON * n
                || (au + bu - u).abs() > 128. * f64::EPSILON * u
            {
                return Err(bad("AXBI_HEII_SPLIT_DEFECT"));
            }
            if an > 0. {
                add_support(&mut out.below, k, an, au, al, ah)
            }
            if bn > 0. {
                add_support(&mut out.above, k, bn, bu, bl, bh)
            }
        }
        self.validate_state(&out.below)?;
        self.validate_state(&out.above)?;
        Ok(out)
    }
    /// Move both pools independently; never reconstruct a merged cross-threshold cell.
    /// Works in either direction provided the original ray geometry is valid.
    pub fn move_heii(
        &self,
        p: &HeiiPools,
        g: &GeometrySnapshot,
    ) -> Result<HeiiPools, ForwardError> {
        let a = self.partition_heii(&p.below, g)?;
        let b = self.partition_heii(&p.above, g)?;
        Ok(HeiiPools {
            below: self.merge_heii_states(&a.below, &b.below)?,
            above: self.merge_heii_states(&a.above, &b.above)?,
        })
    }
    pub fn heii_inventory(
        &self,
        p: &HeiiPools,
        g: &GeometrySnapshot,
    ) -> Result<(f64, f64), ForwardError> {
        let a = self.inventory(&p.below, g)?;
        let b = self.inventory(&p.above, g)?;
        Ok((a.0 + b.0, a.1 + b.1))
    }
    /// Birth moments are integrated separately on both sides of the physical
    /// HeII edge using the original source law, before any N/U compression.
    pub fn inject_heii(
        &self,
        g: &GeometrySnapshot,
        z: f64,
        dt: f64,
    ) -> Result<(HeiiPools, SourceLedger), ForwardError> {
        if !nonnegative(dt) {
            return Err(bad("AXBI_HEII_SOURCE_DT"));
        }
        let amount = self.source.at_redshift(z)?.per_h_s * dt;
        if !nonnegative(amount) {
            return Err(bad("AXBI_HEII_SOURCE_AMOUNT"));
        }
        let rays = self.ray_geometry(g)?;
        let mut p = self.empty_heii();
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
                    let t = FIT_THRESHOLDS_EV[2];
                    for (lower, upper, target) in
                        [(lo, hi.min(t), &mut p.below), (lo.max(t), hi, &mut p.above)]
                    {
                        if upper <= lower {
                            continue;
                        }
                        let (n, u) = source_moments(lower, upper);
                        let n = amp * n;
                        let u = amp * u;
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
                        add_support(target, j * self.n_energy() + i, n, u / r.scale, qlo, qhi);
                        l.added_photons_per_h += n;
                        l.added_energy_ev_per_h += u;
                    }
                }
            }
        }
        self.validate_state(&p.below)?;
        self.validate_state(&p.above)?;
        Ok((p, l))
    }
    /// Same frozen-coefficient continuous-birth owner as the unsplit driver.
    /// All three absorbers operate in both pools; below-HeII is not passive.
    pub fn advance_heii(
        &self,
        p: &HeiiPools,
        birth: &HeiiPools,
        g: &GeometrySnapshot,
        absorbers: [f64; 3],
        nh: f64,
        dt: f64,
    ) -> Result<HeiiAbsorption, ForwardError> {
        let a = self.prepare(&p.below, g)?.evaluate_continuous_birth(
            &self.prepare(&birth.below, g)?,
            absorbers,
            nh,
            dt,
        )?;
        let b = self.prepare(&p.above, g)?.evaluate_continuous_birth(
            &self.prepare(&birth.above, g)?,
            absorbers,
            nh,
            dt,
        )?;
        self.validate_state(&a.state)?;
        self.validate_state(&b.state)?;
        let mut photo = a.photo;
        for k in 0..3 {
            photo.gamma_s[k] += b.photo.gamma_s[k];
            photo.heat_erg_per_absorber_s[k] += b.photo.heat_erg_per_absorber_s[k];
        }
        Ok(HeiiAbsorption {
            state: HeiiPools {
                below: a.state,
                above: b.state,
            },
            photo,
            absorbed_per_h: std::array::from_fn(|k| a.absorbed_per_h[k] + b.absorbed_per_h[k]),
            binding_ev_per_h: a.binding_ev_per_h + b.binding_ev_per_h,
            heat_ev_per_h: a.heat_ev_per_h + b.heat_ev_per_h,
        })
    }
    pub fn heii_endpoint_photo(
        &self,
        p: &HeiiPools,
        g: &GeometrySnapshot,
        nh: f64,
    ) -> Result<IgmPhotoInput, ForwardError> {
        let mut a = self.prepare(&p.below, g)?.evaluate([0.; 3], nh, 0.)?.photo;
        let b = self.prepare(&p.above, g)?.evaluate([0.; 3], nh, 0.)?.photo;
        for k in 0..3 {
            a.gamma_s[k] += b.gamma_s[k];
            a.heat_erg_per_absorber_s[k] += b.heat_erg_per_absorber_s[k];
        }
        Ok(a)
    }
}
