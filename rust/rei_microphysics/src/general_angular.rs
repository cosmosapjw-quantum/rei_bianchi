//! Fixed, positively weighted general coframe angular registry.
//! This is the source/moment adapter, not the LRS gas driver.
use crate::{general_ray::canonical_ray, ForwardError};
pub type Coframe = [[f64; 3]; 3];
pub struct GeneralAngular {
    reference: Coframe,
    rays: Vec<([f64; 3], f64)>,
}
#[derive(Clone, Debug)]
pub struct SourceAngles {
    pub raw_area: f64,
    pub weights: Vec<f64>,
    pub direction: Vec<[f64; 3]>,
    pub dipole: [f64; 3],
    pub pressure: Coframe,
}
pub struct RadiationMoments {
    pub energy: f64,
    pub flux: [f64; 3],
    pub pressure: Coframe,
}
fn gl(n: usize) -> Result<Vec<(f64, f64)>, ForwardError> {
    let bad = || ForwardError::InvalidInput("GENERAL_ANGULAR_GRID");
    if n < 4 || n > 128 || n % 2 != 0 {
        return Err(bad());
    }
    let mut out = vec![(0., 0.); n];
    for i in 0..n / 2 {
        let mut x = (std::f64::consts::PI * (i as f64 + 0.75) / (n as f64 + 0.5)).cos();
        let eval = |x: f64| {
            let (mut p0, mut p1) = (1., x);
            for k in 2..=n {
                let p = ((2 * k - 1) as f64 * x * p1 - (k - 1) as f64 * p0) / k as f64;
                p0 = p1;
                p1 = p;
            }
            (p1, n as f64 * (x * p1 - p0) / (x * x - 1.))
        };
        for _ in 0..32 {
            let (p, d) = eval(x);
            let y = x - p / d;
            if (y - x).abs() < 2. * f64::EPSILON {
                x = y;
                break;
            }
            x = y;
        }
        let (p, d) = eval(x);
        if p.abs() > 1e-12 {
            return Err(bad());
        }
        let w = 1. / ((1. - x * x) * d * d);
        out[i] = (-x, w);
        out[n - 1 - i] = (x, w);
    }
    Ok(out)
}
impl GeneralAngular {
    pub fn new(
        reference: Coframe,
        center: Coframe,
        nmu: usize,
        nphi: usize,
    ) -> Result<Self, ForwardError> {
        if nphi < 8 || nphi > 256 || nphi % 2 != 0 {
            return Err(ForwardError::InvalidInput("GENERAL_ANGULAR_GRID"));
        }
        let mut rays = Vec::with_capacity(nmu * nphi);
        for (mu, w) in gl(nmu)? {
            let r = (1. - mu * mu).sqrt();
            for k in 0..nphi {
                let p = 2. * std::f64::consts::PI * k as f64 / nphi as f64;
                let d = [r * p.cos(), r * p.sin(), mu];
                let a = canonical_ray(center, reference, d)?;
                rays.push((a.direction, w / nphi as f64 * a.jacobian));
            }
        }
        Ok(Self { reference, rays })
    }
    pub fn len(&self) -> usize {
        self.rays.len()
    }
    pub fn source_at(&self, c: Coframe) -> Result<SourceAngles, ForwardError> {
        let mut weights = Vec::new();
        let mut direction = Vec::new();
        for &(n, w) in &self.rays {
            let a = canonical_ray(self.reference, c, n)?;
            weights.push(w * a.jacobian);
            direction.push(a.direction);
        }
        let raw_area = weights.iter().sum::<f64>();
        if raw_area <= 0. || !raw_area.is_finite() {
            return Err(ForwardError::InvalidInput("GENERAL_ANGULAR_AREA"));
        }
        for w in &mut weights {
            *w /= raw_area;
        }
        let mut dipole = [0.; 3];
        let mut pressure = [[0.; 3]; 3];
        for (n, &w) in direction.iter().zip(&weights) {
            for i in 0..3 {
                dipole[i] += w * n[i];
                for j in 0..3 {
                    pressure[i][j] += w * n[i] * n[j];
                }
            }
        }
        Ok(SourceAngles {
            raw_area,
            weights,
            direction,
            dipole,
            pressure,
        })
    }
    pub fn moments_at(
        &self,
        c: Coframe,
        reference_energy: &[f64],
    ) -> Result<RadiationMoments, ForwardError> {
        if reference_energy.len() != self.len()
            || !reference_energy.iter().all(|x| x.is_finite() && *x >= 0.)
        {
            return Err(ForwardError::InvalidInput("GENERAL_ANGULAR_STOCK"));
        }
        let mut out = RadiationMoments {
            energy: 0.,
            flux: [0.; 3],
            pressure: [[0.; 3]; 3],
        };
        for (&(n, _), &u) in self.rays.iter().zip(reference_energy) {
            let a = canonical_ray(self.reference, c, n)?;
            let u = u * a.energy_scale;
            out.energy += u;
            for i in 0..3 {
                out.flux[i] += u * a.direction[i];
                for j in 0..3 {
                    out.pressure[i][j] += u * a.direction[i] * a.direction[j];
                }
            }
        }
        Ok(out)
    }
}
