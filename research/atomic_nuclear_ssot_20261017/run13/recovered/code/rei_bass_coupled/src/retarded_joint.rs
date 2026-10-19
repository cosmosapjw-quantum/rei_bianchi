//! RUN08 comoving retarded joint reference, positive finite birth packets.
use crate::full_network::{NetworkConfig, NetworkError};
use crate::{bass_geometry::BassPoint, source_age::Cohort};
pub struct RetardedContext<'a> {
    pub point: BassPoint,
    pub a_ref: f64,
    pub cohorts: &'a [Cohort],
    pub active: usize,
    pub config: &'a NetworkConfig,
    pub gas_mask: u8,
    pub photo: bool,
    pub expansion: bool,
}
/// First14 are densities/energy per initial proper volume. Output: parent27,
/// one optical depth per cohort, photo events4, photo heats4, gas/photon work.
pub fn rhs_x(
    comoving: &[f64; 14],
    depth: &[f64],
    ctx: &RetardedContext<'_>,
) -> Result<Vec<f64>, NetworkError> {
    use crate::{
        full_network::{EV_J, FullState, SPEED_OF_LIGHT_M_S},
        gas_reference_rhs::gas_rates,
        isotope_state::IsotopeNumberState,
        joint_slab::{LOWER, SlabSpectrum, UPPER},
        mixture_eos::MixtureState,
    };
    let m = ctx.cohorts.len();
    if depth.len() != m
        || ctx.active > m
        || !ctx.a_ref.is_finite()
        || ctx.a_ref <= 0.
        || !ctx.point.h.is_finite()
        || ctx.point.h <= 0.
        || !ctx.point.a.is_finite()
        || ctx.point.a <= 0.
        || !ctx.point.s.is_finite()
        || depth.iter().any(|v| !v.is_finite())
        || comoving.iter().any(|v| !v.is_finite())
    {
        return Err(NetworkError::InvalidInput);
    }
    let d = (ctx.point.a / ctx.a_ref).powi(3);
    let mut n = [0.; 13];
    for i in 0..13 {
        n[i] = comoving[i] / d;
    }
    let s = FullState {
        gas: MixtureState {
            nuclei: IsotopeNumberState::new(n).map_err(|_| NetworkError::NegativePopulation)?,
            thermal_j_m3: comoving[13] / d,
        },
        photon_bins: vec![],
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
        elapsed_s: ctx.point.time_s,
    };
    let mut c = *ctx.config;
    c.cmb_temperature_k = 2.7255 / ctx.point.a;
    let mut out = vec![0.; 37 + m];
    for (dst, src) in out[..27]
        .iter_mut()
        .zip(gas_rates(&s, &c, ctx.gas_mask)?.vector())
    {
        *dst = src * d / ctx.point.h;
    }
    let p = 27 + m;
    if ctx.expansion {
        out[13] -= 2. * comoving[13];
        out[p + 8] = 2. * comoving[13];
    }
    let snapshot = ctx.point.snapshot()?;
    for (i, co) in ctx.cohorts.iter().take(ctx.active).enumerate() {
        if ctx.point.time_s < co.birth_time_s {
            return Err(NetworkError::InvalidInput);
        }
        let ray = co.ray_at(&snapshot)?;
        let e = ray.energy_ev;
        let count = co.n_comoving_m3 / ctx.a_ref.powi(3) * (-depth[i]).exp();
        let bprime = ctx.point.s / ctx.point.h;
        let mu2 = ray.direction[2].powi(2);
        if ctx.expansion {
            out[p + 9] +=
                count * e * ((1. - bprime) * (1. - mu2) + (1. + 2. * bprime) * mu2) * EV_J;
        }
        if ctx.photo {
            let spec = SlabSpectrum::native(vec![e], vec![0.], &c)?;
            for a in 0..4 {
                let k =
                    SPEED_OF_LIGHT_M_S * n[LOWER[a]] * spec.cross_sections()[0][a] / ctx.point.h;
                let event = k * count;
                let heat = event * (e - spec.thresholds()[a]) * EV_J;
                out[27 + i] += k;
                out[LOWER[a]] -= event;
                out[UPPER[a]] += event;
                out[13] += heat;
                out[p + a] += event;
                out[p + 4 + a] += heat;
            }
        }
    }
    if out.iter().any(|v| !v.is_finite()) {
        return Err(NetworkError::NonFinite);
    }
    Ok(out)
}
