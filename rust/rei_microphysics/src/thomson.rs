//! Thomson loss given a material history and a future-directed photon.
//! Time is normal-observer proper time in seconds. No collision gain or
//! velocity/chemistry backreaction is evolved by this transport operation.
use crate::{
    axbi_driver::{Driver, DriverState},
    igm_thermal::SIGMA_T_CM2,
    AxisymmetricPoint, CharacteristicRay, ForwardError, GeometrySnapshot, C_LIGHT,
};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum DensityConstraint {
    /// Keep the supplied proper density when prescribing a tilt.
    FixedRest,
    /// Keep the original normal-frame number density, n_rest = n_normal / gamma.
    FixedNormalInventory,
}

#[derive(Clone, Copy, Debug)]
pub struct MaterialKnot {
    pub normal_t_s: f64,
    pub a: f64,
    pub b: f64,
    /// Input total reference density (SI), interpreted by density_constraint.
    pub n_reference_m3: f64,
    /// Total free electrons per reference particle. REI uses H nuclei as reference.
    pub electrons_per_reference: f64,
    pub beta: [f64; 3],
}

/// Input beta is external to the homogeneous AXBI chemistry.
impl Driver {
    pub fn thomson_material_knot(
        &self,
        state: &DriverState,
        beta: [f64; 3],
    ) -> Result<MaterialKnot, ForwardError> {
        let p = self.background.point_at_scale(state.a)?;
        let nh = self.n_h0_cm3 / p.a.powi(3);
        let nhe = self.n_he0_cm3 / p.a.powi(3);
        let eos = state.gas.eos(nh, nhe)?;
        Ok(MaterialKnot {
            normal_t_s: p.time_s,
            a: p.a,
            b: p.b,
            n_reference_m3: nh * 1e6,
            electrons_per_reference: eos.electron_density_cm3 / nh,
            beta,
        })
    }
}

#[derive(Clone, Copy, Debug)]
pub struct ThomsonSample {
    pub material: MaterialKnot,
    pub n_reference_rest_m3: f64,
    pub direction: [f64; 3],
    pub rate_per_s: f64,
    pub tau_to_receiver: f64,
    /// Probability mass of this knot's following (future) cell; zero at receiver.
    pub next_cell_mass: f64,
}

#[derive(Clone, Copy, Debug)]
struct ElectronBoost {
    speed: f64,
    unit_velocity: [f64; 3],
    inverse_gamma: f64,
}
impl ElectronBoost {
    fn new(beta: [f64; 3]) -> Result<Self, ForwardError> {
        let speed = beta[0].hypot(beta[1]).hypot(beta[2]);
        if !speed.is_finite() || speed >= 1.0 {
            return Err(ForwardError::InvalidInput("THOMSON_BETA"));
        }
        // (1-v)(1+v) and the chord expression below preserve the
        // co-propagating limit D ~ sqrt((1-v)/(1+v)) at large gamma.
        Ok(Self {
            speed,
            unit_velocity: if speed == 0.0 {
                [0.0; 3]
            } else {
                beta.map(|v| v / speed)
            },
            inverse_gamma: ((1.0 - speed) * (1.0 + speed)).sqrt(),
        })
    }

    fn doppler(&self, unit_direction: [f64; 3]) -> f64 {
        let chord_squared: f64 = self
            .unit_velocity
            .iter()
            .zip(unit_direction)
            .map(|(v, e)| (v - e).powi(2))
            .sum();
        ((1.0 - self.speed) + 0.5 * self.speed * chord_squared) / self.inverse_gamma
    }
}

fn geometry(k: &MaterialKnot) -> Result<GeometrySnapshot, ForwardError> {
    // Characteristic pullback needs only the three scale factors at its endpoints.
    AxisymmetricPoint::new(k.a, k.b, 0.0, 0.0)?.snapshot()
}

/// On each native proper-time interval the sampled rate is interpolated linearly.
/// The terminal direction follows photon propagation (opposite the apparent sky
/// direction). Each ray direction is pulled from that *same* terminal tetrad.
pub fn thomson_history(
    knots: &[MaterialKnot],
    density_constraint: DensityConstraint,
    receiver_direction: [f64; 3],
) -> Result<Vec<ThomsonSample>, ForwardError> {
    if knots.len() < 2
        || knots
            .windows(2)
            .any(|pair| pair[1].normal_t_s <= pair[0].normal_t_s)
    {
        return Err(ForwardError::InvalidInput("THOMSON_CLOCK"));
    }
    let terminal = geometry(knots.last().unwrap())?;
    let photon = CharacteristicRay::new(1.0, receiver_direction, 0.0)?;
    let mut samples = Vec::with_capacity(knots.len());
    for knot in knots {
        if !knot.normal_t_s.is_finite()
            || !knot.n_reference_m3.is_finite()
            || knot.n_reference_m3 < 0.0
            || !knot.electrons_per_reference.is_finite()
            || knot.electrons_per_reference < 0.0
        {
            return Err(ForwardError::InvalidInput("THOMSON_MATERIAL"));
        }
        let direction = photon.pullback(&terminal, &geometry(knot)?)?.direction;
        let boost = ElectronBoost::new(knot.beta)?;
        let rest = match density_constraint {
            DensityConstraint::FixedRest => knot.n_reference_m3,
            DensityConstraint::FixedNormalInventory => knot.n_reference_m3 * boost.inverse_gamma,
        };
        let rate = (C_LIGHT * SIGMA_T_CM2 * 1e-6)
            * rest
            * knot.electrons_per_reference
            * boost.doppler(direction);
        if !rate.is_finite() {
            return Err(ForwardError::InvalidInput("THOMSON_RATE"));
        }
        samples.push(ThomsonSample {
            material: *knot,
            direction,
            n_reference_rest_m3: rest,
            rate_per_s: rate,
            tau_to_receiver: 0.0,
            next_cell_mass: 0.0,
        });
    }
    for i in (0..samples.len() - 1).rev() {
        let near = samples[i + 1];
        let far = &mut samples[i];
        let dt = near.material.normal_t_s - far.material.normal_t_s;
        let delta = dt * (0.5 * near.rate_per_s + 0.5 * far.rate_per_s);
        far.tau_to_receiver = near.tau_to_receiver + delta;
        if !far.tau_to_receiver.is_finite() {
            return Err(ForwardError::InvalidInput("THOMSON_INTEGRAL"));
        }
        far.next_cell_mass = (-near.tau_to_receiver).exp() * -(-delta).exp_m1();
    }
    Ok(samples)
}
