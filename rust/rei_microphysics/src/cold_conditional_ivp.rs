//! Finite conditional cold FLRW IVP; prescribed CMB, neutral helium spectator.
use crate::{
    axisym_coupled_derivative, cold_hii_rr, cold_stage_composition, AxisymCoupledState,
    AxisymLocalSources, AxisymmetricPoint, ForwardError, IsotopeNumberState,
};
pub type State = [f64; 19]; // a, 13 species, u, Rc, Eesc, Ebath, W
pub fn hubble(a: f64) -> f64 {
    let g = 4.48162687719e-7 * 2.728_f64.powi(4);
    3.2407792896393e-18
        * (0.13 * a.powi(-3) + 0.343 + g * a.powi(-4) * (1.0 + 0.227107317660239 * 3.04)).sqrt()
}
pub fn initial(a: f64, nh: f64, nhe: f64, xe: f64, t: f64) -> State {
    let mut y = [0.; 19];
    y[0] = a;
    y[2] = nh * (1. - xe);
    y[3] = nh * xe;
    y[11] = nhe;
    y[14] = 1.5 * cold_hii_rr::KB * t * (nh + nhe + nh * xe);
    y
}
pub fn physical(y: &State) -> Result<AxisymCoupledState, ForwardError> {
    let mut n = [0.; 13];
    n.copy_from_slice(&y[1..14]);
    Ok(AxisymCoupledState {
        isotopes: IsotopeNumberState::new(n)?,
        thermal_energy_j_m3: y[14],
        photon_number_m3: 0.,
        photon_energy_j_m3: 0.,
        photon_delta_pressure_j_m3: 0.,
    })
}
pub fn rhs(
    tau: f64,
    y: &State,
    ai: f64,
    tgi: f64,
    free: bool,
) -> Result<(State, [f64; 6]), ForwardError> {
    let h = hubble(y[0]);
    let g = AxisymmetricPoint::new(y[0], 0., h, 0.)?;
    let s = physical(y)?;
    let a3 = y[0].powi(3);
    let mut dy = [0.; 19];
    dy[0] = y[0] * h;
    let mut sources = [0.; 6];
    let d = if free {
        axisym_coupled_derivative(tau, g, &s, cold_hii_rr::KB, |_, _| {
            Ok(AxisymLocalSources {
                species_m3_s: [0.; 13],
                electron_m3_s: 0.,
                photon_number_m3_s: 0.,
                photon_power_j_m3_s: 0.,
                thermal_power_j_m3_s: 0.,
                internal_power_j_m3_s: 0.,
                escape_power_j_m3_s: 0.,
                external_power_j_m3_s: 0.,
            })
        })?
    } else {
        let o = cold_stage_composition::stage(tau, g, &s, tgi * ai / y[0])?;
        let p = o.derivative.sources;
        sources = [
            p.species_m3_s[1],
            p.species_m3_s[2],
            p.thermal_power_j_m3_s,
            p.internal_power_j_m3_s,
            p.escape_power_j_m3_s,
            p.external_power_j_m3_s,
        ];
        dy[15] = a3 * o.recombinations_m3_s;
        dy[16] = a3 * (cold_hii_rr::CHI_J * o.recombinations_m3_s + o.cooling_w_m3);
        dy[17] = a3 * o.cmb_bath_w_m3;
        o.derivative
    };
    dy[1..14].copy_from_slice(&d.species_m3_s);
    dy[14] = d.thermal_energy_j_m3_s;
    dy[18] = 2. * h * a3 * y[14];
    if !dy.iter().all(|x| x.is_finite()) {
        return Err(ForwardError::InvalidInput("COLD_IVP_NONFINITE"));
    }
    Ok((dy, sources))
}
pub fn integrate<F: FnMut(f64, &State, &State, &[f64; 6])>(
    y0: State,
    tgi: f64,
    n: usize,
    free: bool,
    mut observe: F,
) -> Result<Vec<State>, ForwardError> {
    let ai = y0[0];
    let dt = 1e14 / n as f64;
    let mut y = y0;
    let mut epochs = vec![y];
    for i in 0..n {
        let t = i as f64 * dt;
        let mut eval = |t: f64, z: &State| {
            let (d, s) = rhs(t, z, ai, tgi, free)?;
            observe(t, z, &d, &s);
            Ok::<_, ForwardError>(d)
        };
        let k1 = eval(t, &y)?;
        let shift = |k: &State, f: f64| {
            let mut z = y;
            for j in 0..19 {
                z[j] += f * dt * k[j];
            }
            z
        };
        let k2 = eval(t + dt / 2., &shift(&k1, 0.5))?;
        let k3 = eval(t + dt / 2., &shift(&k2, 0.5))?;
        let k4 = eval(t + dt, &shift(&k3, 1.))?;
        for j in 0..19 {
            y[j] += dt * (k1[j] + 2. * k2[j] + 2. * k3[j] + k4[j]) / 6.;
        }
        physical(&y)?;
        if (i + 1) % (n / 4) == 0 {
            epochs.push(y);
        }
    }
    Ok(epochs)
}
