//! Isolated manufactured verification kernel for rei_bianchi source-age and diagonal Bianchi I.
//! No source-backed Grackle, global EoR, HyRec, polarised Thomson, or production admission.
//! Proper seconds, photon numbers per H nucleus, eV energy convention.
#![forbid(unsafe_code)]

#[derive(Debug, PartialEq, Clone, Copy)]
pub enum RefError {
    InvalidInput(&'static str),
    OutOfPhysicalDomain(&'static str),
    Overflow(&'static str),
}

fn positive_finite(x: f64, tag: &'static str) -> Result<f64, RefError> {
    if x.is_finite() && x > 0.0 {
        Ok(x)
    } else {
        Err(RefError::InvalidInput(tag))
    }
}
fn nonnegative_finite(x: f64, tag: &'static str) -> Result<f64, RefError> {
    if x.is_finite() && x >= 0.0 {
        Ok(x)
    } else {
        Err(RefError::InvalidInput(tag))
    }
}

/// phi_1(-x) = (1 - exp(-x)) / x, smooth at x=0 for x>=0.
/// Small-x series avoids cancellation; for large x use exp_m1, no clipping.
pub fn phi1_neg(x: f64) -> Result<f64, RefError> {
    nonnegative_finite(x, "optical_depth")?;
    if x < 1.0e-4 {
        let v =
            1.0 - x * (0.5 - x * (1.0 / 6.0 - x * (1.0 / 24.0 - x * (1.0 / 120.0 - x / 720.0))));
        Ok(v)
    } else {
        Ok(-(-x).exp_m1() / x)
    }
}

/// 1 - phi_1(-x) as a separately evaluated positive analytic branch.
fn one_minus_phi1_neg(x: f64) -> Result<f64, RefError> {
    nonnegative_finite(x, "optical_depth")?;
    if x < 1.0e-4 {
        Ok(x * (0.5 - x * (1.0 / 6.0 - x * (1.0 / 24.0 - x * (1.0 / 120.0 - x / 720.0)))))
    } else {
        Ok(1.0 - phi1_neg(x)?)
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct PhotonBox {
    pub old_per_h: f64,
    pub source_per_h_per_s: f64,
    pub hazard_per_s: f64,
    pub dt_s: f64,
    pub photon_energy_ev: f64,
    pub binding_energy_ev: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct PhotonLedger {
    pub next_per_h: f64,
    pub born_per_h: f64,
    pub absorbed_per_h: f64,
    pub photon_number_residual_per_h: f64,
    pub binding_delta_ev_per_h: f64,
    pub heat_delta_ev_per_h: f64,
    pub photon_energy_residual_ev_per_h: f64,
}

impl PhotonBox {
    /// Exact constant-source/constant-hazard collision+birth flow.
    /// Absorption of old photons and of uniformly created photons are calculated separately;
    /// this avoids subtracting two nearly equal large photon inventories.
    pub fn step(self) -> Result<PhotonLedger, RefError> {
        nonnegative_finite(self.old_per_h, "old_photons")?;
        nonnegative_finite(self.source_per_h_per_s, "source")?;
        nonnegative_finite(self.hazard_per_s, "hazard")?;
        nonnegative_finite(self.dt_s, "duration")?;
        positive_finite(self.photon_energy_ev, "photon_energy")?;
        nonnegative_finite(self.binding_energy_ev, "binding")?;
        if self.photon_energy_ev < self.binding_energy_ev {
            return Err(RefError::OutOfPhysicalDomain("below_threshold"));
        }
        let x = self.hazard_per_s * self.dt_s;
        if !x.is_finite() {
            return Err(RefError::Overflow("optical_depth"));
        }
        let birth = self.source_per_h_per_s * self.dt_s;
        if !birth.is_finite() {
            return Err(RefError::Overflow("birth_count"));
        }
        let surviving_old = self.old_per_h * (-x).exp();
        let surviving_birth = birth * phi1_neg(x)?;
        let next = surviving_old + surviving_birth;
        let old_absorbed = self.old_per_h * -(-x).exp_m1();
        let birth_absorbed = birth * one_minus_phi1_neg(x)?;
        let absorbed = old_absorbed + birth_absorbed;
        let bind = self.binding_energy_ev * absorbed;
        let heat = (self.photon_energy_ev - self.binding_energy_ev) * absorbed;
        let result = [next, absorbed, bind, heat, old_absorbed, birth_absorbed];
        if result.iter().any(|y| !y.is_finite() || *y < 0.0) {
            return Err(RefError::Overflow("ledger"));
        }
        let photons_residual = (next + absorbed) - (self.old_per_h + birth);
        let energy_residual = self.photon_energy_ev * (next - self.old_per_h - birth) + bind + heat;
        if !photons_residual.is_finite() || !energy_residual.is_finite() {
            return Err(RefError::Overflow("residual"));
        }
        Ok(PhotonLedger {
            next_per_h: next,
            born_per_h: birth,
            absorbed_per_h: absorbed,
            photon_number_residual_per_h: photons_residual,
            binding_delta_ev_per_h: bind,
            heat_delta_ev_per_h: heat,
            photon_energy_residual_ev_per_h: energy_residual,
        })
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DiagonalGeometry {
    pub a: [f64; 3],
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Ray {
    pub energy_ev: f64,
    pub direction: [f64; 3],
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct RayMap {
    pub ray: Ray,
    pub energy_ratio: f64,
    pub solid_angle_jacobian: f64,
}
impl DiagonalGeometry {
    pub fn transport(&self, dest: DiagonalGeometry, ray: Ray) -> Result<RayMap, RefError> {
        for a in self.a.into_iter().chain(dest.a) {
            positive_finite(a, "scale_factor")?;
        }
        positive_finite(ray.energy_ev, "ray_energy")?;
        if ray.direction.iter().any(|x| !x.is_finite()) {
            return Err(RefError::InvalidInput("direction"));
        }
        let norm = ray.direction.iter().map(|x| x * x).sum::<f64>().sqrt();
        if (norm - 1.0).abs() > 1e-12 {
            return Err(RefError::InvalidInput("direction_norm"));
        }
        let r: [f64; 3] = std::array::from_fn(|i| self.a[i] / dest.a[i]);
        let p: [f64; 3] = std::array::from_fn(|i| ray.direction[i] * r[i]);
        let q = p.iter().map(|v| v * v).sum::<f64>().sqrt();
        let jac = r[0] * r[1] * r[2] / (q * q * q);
        let energy = ray.energy_ev * q;
        if !q.is_finite()
            || q <= 0.0
            || !jac.is_finite()
            || jac <= 0.0
            || !energy.is_finite()
            || energy <= 0.0
        {
            return Err(RefError::Overflow("redshift_jacobian"));
        }
        Ok(RayMap {
            ray: Ray {
                energy_ev: energy,
                direction: p.map(|v| v / q),
            },
            energy_ratio: q,
            solid_angle_jacobian: jac,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn near(a: f64, b: f64, rel: f64) {
        assert!((a - b).abs() <= rel * b.abs().max(1.0), "{a} vs {b}");
    }
    fn base() -> PhotonBox {
        PhotonBox {
            old_per_h: 0.25,
            source_per_h_per_s: 0.05,
            hazard_per_s: 2.0,
            dt_s: 0.7,
            photon_energy_ev: 45.0,
            binding_energy_ev: 24.6,
        }
    }
    #[test]
    fn zero_opacity_limit() {
        let mut b = base();
        b.hazard_per_s = 0.;
        let r = b.step().unwrap();
        near(r.next_per_h, 0.285, 1e-15);
        assert_eq!(r.absorbed_per_h, 0.);
    }
    #[test]
    fn zero_source_exact() {
        let mut b = base();
        b.source_per_h_per_s = 0.;
        let r = b.step().unwrap();
        near(r.next_per_h, b.old_per_h * (-1.4f64).exp(), 1e-15);
    }
    #[test]
    fn optical_depth_very_small() {
        let x = 1e-10;
        near(phi1_neg(x).unwrap(), 1. - x / 2., 1e-15);
        let b = PhotonBox {
            hazard_per_s: x,
            ..base()
        };
        let r = b.step().unwrap();
        assert!(r.absorbed_per_h > 0.);
    }
    #[test]
    fn high_tau_positive() {
        let mut b = base();
        b.hazard_per_s = 1_000.;
        let r = b.step().unwrap();
        assert!(r.next_per_h > 0.);
        assert!(r.absorbed_per_h > 0.);
        near(r.photon_number_residual_per_h, 0., 1e-12);
    }
    #[test]
    fn photon_ledger() {
        let r = base().step().unwrap();
        near(r.photon_number_residual_per_h, 0., 1e-13);
        near(r.photon_energy_residual_ev_per_h, 0., 1e-12);
    }
    #[test]
    fn threshold_energy_ownership() {
        let mut b = base();
        b.binding_energy_ev = b.photon_energy_ev;
        let r = b.step().unwrap();
        assert_eq!(r.heat_delta_ev_per_h, 0.);
    }
    #[test]
    fn below_threshold_fail_closed() {
        let mut b = base();
        b.binding_energy_ev = 100.;
        assert_eq!(
            b.step().unwrap_err(),
            RefError::OutOfPhysicalDomain("below_threshold")
        );
    }
    #[test]
    fn negative_state_rejected() {
        let b = PhotonBox {
            old_per_h: -1.,
            ..base()
        };
        assert!(b.step().is_err());
    }
    #[test]
    fn nonfinite_rejected() {
        let b = PhotonBox {
            dt_s: f64::NAN,
            ..base()
        };
        assert!(b.step().is_err());
    }
    #[test]
    fn exact_flow_semigroup() {
        let b = base();
        let whole = b.step().unwrap();
        let h = b.dt_s / 2.;
        let first = PhotonBox { dt_s: h, ..b }.step().unwrap();
        let second = PhotonBox {
            old_per_h: first.next_per_h,
            dt_s: h,
            ..b
        }
        .step()
        .unwrap();
        near(whole.next_per_h, second.next_per_h, 1e-13);
    }
    #[test]
    fn flrw_redshift() {
        let g0 = DiagonalGeometry { a: [1., 1., 1.] };
        let g1 = DiagonalGeometry { a: [2., 2., 2.] };
        let t = g0
            .transport(
                g1,
                Ray {
                    energy_ev: 80.,
                    direction: [0.6, 0., 0.8],
                },
            )
            .unwrap();
        near(t.ray.energy_ev, 40., 1e-14);
        near(t.solid_angle_jacobian, 1., 1e-14);
    }
    #[test]
    fn signed_bianchi_orientation() {
        let g0 = DiagonalGeometry { a: [1., 1., 1.] };
        let plus = DiagonalGeometry {
            a: [(-0.2f64).exp(), (-0.2f64).exp(), (0.4f64).exp()],
        };
        let r = Ray {
            energy_ev: 80.,
            direction: [0.6, 0., 0.8],
        };
        let t = g0.transport(plus, r).unwrap();
        assert!(t.ray.direction[2] < r.direction[2]);
        assert!(t.ray.energy_ev > 0.);
    }
    #[test]
    fn inverse_energy_direction() {
        let g0 = DiagonalGeometry { a: [1., 1., 1.] };
        let g1 = DiagonalGeometry { a: [0.7, 1.4, 2.1] };
        let r = Ray {
            energy_ev: 100.,
            direction: [0.6, 0., 0.8],
        };
        let mapped = g0.transport(g1, r).unwrap();
        let back = g1.transport(g0, mapped.ray).unwrap();
        near(back.ray.energy_ev, r.energy_ev, 1e-14);
        for i in 0..3 {
            near(back.ray.direction[i], r.direction[i], 1e-14);
        }
    }
    #[test]
    fn zero_scale_rejected() {
        let g = DiagonalGeometry { a: [1., 0., 1.] };
        assert!(
            g.transport(
                DiagonalGeometry { a: [1., 1., 1.] },
                Ray {
                    energy_ev: 1.,
                    direction: [1., 0., 0.]
                }
            )
            .is_err()
        );
    }
}