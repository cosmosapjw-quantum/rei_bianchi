//! Homogeneous diagonal Bianchi-I geometry and collisionless photon characteristics.
use crate::ForwardError;

fn invalid(tag: &'static str) -> ForwardError {
    ForwardError::InvalidInput(tag)
}

fn positive_finite(x: f64, tag: &'static str) -> Result<f64, ForwardError> {
    if x.is_finite() && x > 0.0 {
        Ok(x)
    } else {
        Err(invalid(tag))
    }
}

fn finite(x: f64, tag: &'static str) -> Result<f64, ForwardError> {
    if x.is_finite() {
        Ok(x)
    } else {
        Err(invalid(tag))
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct GeometrySnapshot {
    pub scale_factors: [f64; 3],
    pub hubble_per_s: [f64; 3],
}

impl GeometrySnapshot {
    pub fn new(scale_factors: [f64; 3], hubble_per_s: [f64; 3]) -> Result<Self, ForwardError> {
        let snapshot = Self {
            scale_factors,
            hubble_per_s,
        };
        snapshot.validate()?;
        Ok(snapshot)
    }

    fn validate(&self) -> Result<(), ForwardError> {
        for a in self.scale_factors {
            positive_finite(a, "BianchiScale")?;
        }
        for h in self.hubble_per_s {
            finite(h, "BianchiHubble")?;
        }
        self.volume_factor()?;
        Ok(())
    }

    pub fn volume_factor(&self) -> Result<f64, ForwardError> {
        for a in self.scale_factors {
            positive_finite(a, "BianchiScale")?;
        }
        for h in self.hubble_per_s {
            finite(h, "BianchiHubble")?;
        }
        let v = self.scale_factors.iter().product();
        positive_finite(v, "BianchiVolume")
    }
}

pub trait GeometryBackground {
    fn snapshot(&self, t: f64) -> Result<GeometrySnapshot, ForwardError>;
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ConstantHubbleBackground {
    pub initial_scale_factors: [f64; 3],
    pub hubble_per_s: [f64; 3],
}

impl ConstantHubbleBackground {
    pub fn new(
        initial_scale_factors: [f64; 3],
        hubble_per_s: [f64; 3],
    ) -> Result<Self, ForwardError> {
        GeometrySnapshot::new(initial_scale_factors, hubble_per_s)?;
        Ok(Self {
            initial_scale_factors,
            hubble_per_s,
        })
    }
}

impl GeometryBackground for ConstantHubbleBackground {
    fn snapshot(&self, t: f64) -> Result<GeometrySnapshot, ForwardError> {
        finite(t, "BianchiTime")?;
        GeometrySnapshot::new(self.initial_scale_factors, self.hubble_per_s)?;
        let mut a = [0.0; 3];
        for (i, output) in a.iter_mut().enumerate() {
            let ht = finite(self.hubble_per_s[i] * t, "BianchiExponent")?;
            *output = positive_finite(self.initial_scale_factors[i] * ht.exp(), "BianchiScale")?;
        }
        GeometrySnapshot::new(a, self.hubble_per_s)
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CharacteristicRay {
    pub energy_ev: f64,
    pub direction: [f64; 3],
    pub occupation: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct RayDerivative {
    pub energy_dot_ev_s: f64,
    pub direction_dot_per_s: [f64; 3],
}

impl CharacteristicRay {
    pub fn new(energy_ev: f64, direction: [f64; 3], occupation: f64) -> Result<Self, ForwardError> {
        positive_finite(energy_ev, "RayEnergy")?;
        if !occupation.is_finite() || occupation < 0.0 {
            return Err(invalid("RayOccupation"));
        }
        for component in direction {
            finite(component, "RayDirection")?;
        }
        let norm = direction[0].hypot(direction[1]).hypot(direction[2]);
        if !norm.is_finite() || (norm - 1.0).abs() > 1e-12 {
            return Err(invalid("RayUnitDirection"));
        }
        let normalized = direction.map(|component| component / norm);
        Ok(Self {
            energy_ev,
            direction: normalized,
            occupation,
        })
    }

    fn validate(&self) -> Result<(), ForwardError> {
        Self::new(self.energy_ev, self.direction, self.occupation)?;
        Ok(())
    }

    fn scaled_components(
        &self,
        g0: &GeometrySnapshot,
        g1: &GeometrySnapshot,
    ) -> Result<([f64; 3], f64), ForwardError> {
        self.validate()?;
        g0.validate()?;
        g1.validate()?;
        let mut q = [0.0; 3];
        for (i, component) in q.iter_mut().enumerate() {
            let ratio = finite(g0.scale_factors[i] / g1.scale_factors[i], "RayScaleRatio")?;
            *component = finite(self.direction[i] * ratio, "RayScaledDirection")?;
        }
        let r = positive_finite(q[0].hypot(q[1]).hypot(q[2]), "RayRedshift")?;
        Ok((q, r))
    }

    pub fn pullback(
        &self,
        g0: &GeometrySnapshot,
        g1: &GeometrySnapshot,
    ) -> Result<Self, ForwardError> {
        let (q, r) = self.scaled_components(g0, g1)?;
        let energy = positive_finite(self.energy_ev * r, "RayTransportEnergy")?;
        Self::new(energy, q.map(|component| component / r), self.occupation)
    }

    pub fn solid_angle_jacobian(
        &self,
        g0: &GeometrySnapshot,
        g1: &GeometrySnapshot,
    ) -> Result<f64, ForwardError> {
        let (_, r) = self.scaled_components(g0, g1)?;
        let log_j = g0
            .scale_factors
            .iter()
            .zip(g1.scale_factors)
            .map(|(a, b)| a.ln() - b.ln())
            .sum::<f64>()
            - 3.0 * r.ln();
        positive_finite(log_j.exp(), "RaySolidAngleJacobian")
    }

    pub fn derivative(&self, g: &GeometrySnapshot) -> Result<RayDerivative, ForwardError> {
        self.validate()?;
        g.validate()?;
        let mut hd = 0.0;
        for i in 0..3 {
            hd = finite(
                self.direction[i].mul_add(self.direction[i] * g.hubble_per_s[i], hd),
                "RayHubbleProjection",
            )?;
        }
        let energy_dot_ev_s = finite(-self.energy_ev * hd, "RayEnergyDerivative")?;
        let mut direction_dot_per_s = [0.0; 3];
        for (i, derivative) in direction_dot_per_s.iter_mut().enumerate() {
            let difference = hd - g.hubble_per_s[i];
            // A canceled projection is zero to working precision (the middle
            // component of the frozen rational direction is one such case).
            let scale = hd.abs().max(g.hubble_per_s[i].abs());
            let difference = if difference.abs() <= 4.0 * f64::EPSILON * scale {
                0.0
            } else {
                difference
            };
            *derivative = finite(self.direction[i] * difference, "RayDirectionDerivative")?;
        }
        Ok(RayDerivative {
            energy_dot_ev_s,
            direction_dot_per_s,
        })
    }
}
