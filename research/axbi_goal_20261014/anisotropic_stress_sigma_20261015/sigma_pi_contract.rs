//! New user-facing Sigma/axis-sign and anisotropic-stress SI contract.
//! This pure Rust module is deliberately isolated from the old native
//! q_ref persisted source, config, checksum and checkpoint machinery.
//! The *only* historical adapter returns the old s_ref/H_FLRW_ref internally.
//! Run: rustc --edition=2021 --test -O sigma_pi_contract.rs -o ... && ...
use std::f64::consts::PI;

const G: f64 = 6.67430e-11;
const C: f64 = 299_792_458.0;
const SQRT3: f64 = 1.732_050_807_568_877_2;
const KAPPA: f64 = 8.0 * PI * G / (3.0 * C * C);

#[derive(Copy, Clone, Debug, PartialEq)]
pub struct SigmaAxis {
    pub sigma_ref: f64,
    pub orientation: i8,
}

impl SigmaAxis {
    pub fn new(sigma_ref: f64, orientation: i8) -> Result<Self, &'static str> {
        if !sigma_ref.is_finite()
            || !(0.0..SQRT3).contains(&sigma_ref)
            || ![-1, 0, 1].contains(&orientation)
            || (sigma_ref == 0.0) != (orientation == 0)
        {
            return Err("SIGMA_AXIS_DOMAIN");
        }
        Ok(Self {
            sigma_ref,
            orientation,
        })
    }
    pub fn signed_s_over_h(&self) -> f64 {
        f64::from(self.orientation) * self.sigma_ref / SQRT3
    }
    pub fn from_stressfree_axis_ratio(
        signed_s_over_h_flrw: f64,
    ) -> Result<Self, &'static str> {
        if !signed_s_over_h_flrw.is_finite() {
            return Err("SIGMA_SOURCE_NONFINITE");
        }
        let branch = if signed_s_over_h_flrw > 0.0 {
            1
        } else if signed_s_over_h_flrw < 0.0 {
            -1
        } else {
            0
        };
        // Old H^2=H_flrw^2+s^2, not a stressed-matter Einstein constraint.
        let sigma = SQRT3 * signed_s_over_h_flrw.abs()
            / signed_s_over_h_flrw.hypot(1.0);
        Self::new(sigma, branch)
    }
    pub fn to_stressfree_axis_ratio(&self) -> f64 {
        f64::from(self.orientation) * self.sigma_ref
            / (3.0 - self.sigma_ref * self.sigma_ref).sqrt()
    }
}

#[derive(Copy, Clone, Debug, PartialEq)]
pub struct PiAxis {
    /// Difference P_parallel - P_perpendicular, in J/m^3 = Pa.
    pub pressure_difference_pa: f64,
}
impl PiAxis {
    pub fn new(pressure_difference_pa: f64) -> Result<Self, &'static str> {
        if !pressure_difference_pa.is_finite() {
            return Err("PI_STRESS_NONFINITE");
        }
        Ok(Self {
            pressure_difference_pa,
        })
    }
    /// Spatial orthonormal mixed tensor diagonal for LRS Bianchi I.
    pub fn diagonal_pa(&self) -> [f64; 3] {
        let pi = self.pressure_difference_pa;
        [-pi / 3.0, -pi / 3.0, 2.0 * pi / 3.0]
    }
    /// pi^ab sigma_ab = 2 s Pi, SI Pa/s.
    pub fn shear_contraction_pa_per_s(&self, signed_s_per_s: f64) -> f64 {
        2.0 * signed_s_per_s * self.pressure_difference_pa
    }
}

pub fn shear_source_per_s2(
    s_per_s: f64,
    h_per_s: f64,
    radiation: PiAxis,
    matter: PiAxis,
) -> Result<f64, &'static str> {
    if !s_per_s.is_finite() || !h_per_s.is_finite() || h_per_s <= 0.0 {
        return Err("SIGMA_SHEAR_DYNAMICS_DOMAIN");
    }
    Ok(-3.0 * h_per_s * s_per_s
        + KAPPA * (radiation.pressure_difference_pa + matter.pressure_difference_pa))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn magnitude_and_orientation_are_independent_and_roundtrip() {
        for old in [0.0, 0.005, -0.005, 0.01, -0.01] {
            let q = SigmaAxis::from_stressfree_axis_ratio(old).unwrap();
            assert!((q.to_stressfree_axis_ratio() - old).abs() < 1e-15);
            assert!((q.signed_s_over_h()
                - old / (1.0 + old * old).sqrt()).abs() < 1e-15);
            assert_eq!(q.orientation.signum(), if old > 0.0 {1}
                  else if old < 0.0 {-1} else {0});
        }
        assert!(SigmaAxis::new(0.1, 0).is_err());
        assert!(SigmaAxis::new(0.0, 1).is_err());
        assert!(SigmaAxis::new(SQRT3, 1).is_err());
    }

    #[test]
    fn tensor_is_tracefree_and_contraction_has_right_sign() {
        for pi in [-1e-13, 0., 2e-13] {
            let tensor = PiAxis::new(pi).unwrap();
            let diag = tensor.diagonal_pa();
            assert!((diag[0] + diag[1] + diag[2]).abs() < 1e-28);
            let s = -1e-18;
            let eigen=[-s,-s,2.*s];
            let direct: f64 = diag.iter().zip(eigen).map(|(p,s)| p*s).sum();
            assert!((direct - tensor.shear_contraction_pa_per_s(s)).abs()
                < 1e-42);
        }
    }

    #[test]
    fn shear_source_obeys_zero_and_restoring_pi_signs() {
        let z=PiAxis::new(0.0).unwrap();
        let a=PiAxis::new(-1e-13).unwrap();
        let s=1e-18;
        let h=1e-16;
        let base=shear_source_per_s2(s,h,z,z).unwrap();
        let stressed=shear_source_per_s2(s,h,a,z).unwrap();
        assert!((base+3.*h*s).abs()<1e-48);
        assert!(stressed<base);
        assert!(shear_source_per_s2(s,0.,a,z).is_err());
    }
}
