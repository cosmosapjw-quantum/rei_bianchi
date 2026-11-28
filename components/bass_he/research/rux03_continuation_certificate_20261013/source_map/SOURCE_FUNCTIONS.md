# Exact selected FT03 / Verner source functions

Unit: HERE_RUX03_MOVING_GAS_CONTINUATION_CERTIFICATE_06.

Receiver commit: `a5c958c414dea41216b445c05f58df837f05cacb`. The FT03 rate path supplies CI/RR/two DR and captured kinetic moments. The Verner cross-section function is read from AtomicProvider; its separate raw Grackle coefficient bodies are not substituted for FT03.

## ft03_rates.rs

Source SHA256: `1a97cd7a3555deeb4d8700376cd84580c5102127773bc3a235a29c33b0c1542f`; bytes: 2755.

[rust/rei_microphysics/src/ft03_rates.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/ft03_rates.rs)

Lines 1–76:

```rust
//! Controlled FT03 Case A rates. These analytic fits are distinct from the raw
//! Grackle reference coefficients in `atomic_provider`.
use crate::ForwardError;

const KB: f64 = 1.380_649e-16;
const LAMBDA_K: [f64; 3] = [315_614.0, 570_670.0, 1_263_030.0];
const CI_A: [f64; 3] = [21.11, 32.38, 19.95];
const CI_P: [f64; 3] = [-1.089, -1.146, -1.089];
const CI_C: [f64; 3] = [0.354, 0.416, 0.553];
const CI_R: [f64; 3] = [0.874, 0.987, 0.735];
const CI_D: [f64; 3] = [1.101, 1.056, 1.275];

#[derive(Clone, Copy, Debug)]
pub struct Ft03Coefficients {
    pub alpha_rr_cm3_s: [f64; 3],
    pub log_slope: [f64; 3],
    pub log_slope_derivative: [f64; 3],
    pub rr_kinetic_erg_cm3_s: [f64; 3],
    pub beta_ci_cm3_s: [f64; 3],
    pub alpha_dr_cm3_s: [f64; 2],
    pub dr_energy_erg: [f64; 2],
}

pub fn ft03_coefficients(t: f64) -> Result<Ft03Coefficients, ForwardError> {
    if !t.is_finite() || !(30_000.0..=110_000.0).contains(&t) {
        return Err(ForwardError::InvalidInput("FT03_TEMPERATURE_DOMAIN"));
    }
    let mut alpha_rr = [0.0; 3];
    let mut g = [0.0; 3];
    let mut gp = [0.0; 3];
    let mut beta = [0.0; 3];
    for a in 0..3 {
        let l = LAMBDA_K[a] / t;
        if a == 1 {
            alpha_rr[a] = 3e-14 * l.powf(0.654);
            g[a] = -0.654;
        } else {
            let u = (l / 0.522).powf(0.470);
            let prefactor = if a == 2 { 2.0 } else { 1.0 };
            alpha_rr[a] = prefactor * 1.269e-13 * l.powf(1.503) / (1.0 + u).powf(1.923);
            g[a] = -1.503 + 1.923 * 0.470 * u / (1.0 + u);
            gp[a] = -1.923 * 0.470 * 0.470 * u / (1.0 + u).powi(2);
        }
        beta[a] = CI_A[a] * t.powf(-1.5) * (-l / 2.0).exp() * l.powf(CI_P[a])
            / (1.0 + (l / CI_C[a]).powf(CI_R[a])).powf(CI_D[a]);
    }
    let kinetic = std::array::from_fn(|a| KB * t * alpha_rr[a] * (1.5 + g[a]));
    let dr_a = 1.54e-9 * 11_605.0_f64.powf(1.5);
    let b1 = 40.496_643_948_336_62 * 11_605.0;
    let b2 = 8.099_328_789_667 * 11_605.0;
    let dr = [
        dr_a * t.powf(-1.5) * (-b1 / t).exp(),
        0.3 * dr_a * t.powf(-1.5) * (-(b1 + b2) / t).exp(),
    ];
    let energy = [KB * b1, KB * (b1 + b2)];
    if alpha_rr
        .iter()
        .chain(kinetic.iter())
        .chain(beta.iter())
        .chain(dr.iter())
        .chain(energy.iter())
        .any(|x| !x.is_finite() || *x < 0.0)
        || g.iter().chain(gp.iter()).any(|x| !x.is_finite())
    {
        return Err(ForwardError::InvalidInput("FT03_OVERFLOW"));
    }
    Ok(Ft03Coefficients {
        alpha_rr_cm3_s: alpha_rr,
        log_slope: g,
        log_slope_derivative: gp,
        rr_kinetic_erg_cm3_s: kinetic,
        beta_ci_cm3_s: beta,
        alpha_dr_cm3_s: dr,
        dr_energy_erg: energy,
    })
}
```

## ft03_controlled.rs

Source SHA256: `afcc1c7dd3ad0830552ed1736ff6d96482944d7a3ceac0c5d44b638c15fb01f4`; bytes: 15247.

[rust/rei_microphysics/src/ft03_controlled.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/ft03_controlled.rs)

Lines 93–179:

```rust
pub fn ft03_rhs(model: &Ft03Model, state: &HHeState) -> Result<Ft03Rhs, ForwardError> {
    let t = model.validate_state(state)?;
    let c = ft03_coefficients(t)?;
    let g = &model.gas;
    let [h, he1, he2] = state.fractions;
    let lower = [
        checked_product(&[g.n_h_cm3, 1.0 - h])?,
        checked_product(&[g.n_he_cm3, 1.0 - (he1 + he2)])?,
        checked_product(&[g.n_he_cm3, he1])?,
    ];
    let upper = [
        checked_product(&[g.n_h_cm3, h])?,
        checked_product(&[g.n_he_cm3, he1])?,
        checked_product(&[g.n_he_cm3, he2])?,
    ];
    let ne = g.electron_density(state)?;
    let mut photo = [[0.0; 3]; 3];
    let mut ci = [0.0; 3];
    let mut rr = [0.0; 3];
    let mut rr_kinetic_power = [0.0; 3];
    let mut photon_dot = [0.0; 3];
    let mut j = [0.0; 3];
    let mut du = 0.0;
    let mut escape = 0.0;
    for a in 0..3 {
        ci[a] = checked_product(&[lower[a], ne, c.beta_ci_cm3_s[a]])?;
        rr[a] = checked_product(&[upper[a], ne, c.alpha_rr_cm3_s[a]])?;
        j[a] = ci[a] - rr[a];
        let chi = g.threshold_ev[a] * g.ev_erg;
        let kinetic_rate = checked_product(&[upper[a], ne, c.rr_kinetic_erg_cm3_s[a]])?;
        rr_kinetic_power[a] = kinetic_rate;
        du -= checked_product(&[ci[a], chi])? + kinetic_rate;
        escape += checked_product(&[rr[a], chi])? + kinetic_rate;
        for (k, photon_dot_k) in photon_dot.iter_mut().enumerate() {
            photo[a][k] =
                checked_product(&[g.c_cm_s, lower[a], g.sigma_cm2[a][k], state.photon_cm3[k]])?;
            j[a] += photo[a][k];
            *photon_dot_k -= photo[a][k];
            du += checked_product(&[
                photo[a][k],
                g.photon_energy_ev[k] - g.threshold_ev[a],
                g.ev_erg,
            ])?;
        }
    }
    let dr = [
        checked_product(&[upper[1], ne, c.alpha_dr_cm3_s[0]])?,
        checked_product(&[upper[1], ne, c.alpha_dr_cm3_s[1]])?,
    ];
    let mut dr_kinetic_power = [0.0; 2];
    for (k, event) in dr.iter().enumerate() {
        j[1] -= event;
        dr_kinetic_power[k] = checked_product(&[*event, c.dr_energy_erg[k]])?;
        du -= dr_kinetic_power[k];
        escape += checked_product(&[*event, g.threshold_ev[1] * g.ev_erg + c.dr_energy_erg[k]])?;
    }
    let d = [
        j[0] / g.n_h_cm3,
        (j[1] - j[2]) / g.n_he_cm3,
        j[2] / g.n_he_cm3,
        du,
        photon_dot[0],
        photon_dot[1],
        photon_dot[2],
    ];
    if d.iter().any(|x| !x.is_finite())
        || !escape.is_finite()
        || photo.iter().flatten().any(|x| !x.is_finite() || *x < 0.0)
        || ci
            .iter()
            .chain(rr.iter())
            .chain(dr.iter())
            .any(|x| !x.is_finite() || *x < 0.0)
    {
        return Err(ForwardError::InvalidInput("FT03_OVERFLOW"));
    }
    Ok(Ft03Rhs {
        derivative: d,
        photo_per_cm3_s: photo,
        collision_per_cm3_s: ci,
        recombination_per_cm3_s: rr,
        dr_per_cm3_s: dr,
        rr_kinetic_power_erg_cm3_s: rr_kinetic_power,
        dr_kinetic_power_erg_cm3_s: dr_kinetic_power,
        escaped_energy_rate: escape,
    })
}
```

## atomic_provider.rs

Source SHA256: `b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3`; bytes: 12939.

[rust/rei_microphysics/src/atomic_provider.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/atomic_provider.rs)

Lines 327–354:

```rust
    /// Verner ground-state outer-shell fit. Fit thresholds differ from binding energies.
    pub fn cross_section(&self, absorber: Absorber, energy_ev: f64) -> Result<f64, ForwardError> {
        if !energy_ev.is_finite() || energy_ev < 0.0 {
            return Err(ForwardError::InvalidInput("PHOTON_ENERGY_INVALID"));
        }
        if energy_ev > 50000.0 {
            return Err(ForwardError::InvalidInput("VERNER_ENERGY_DOMAIN"));
        }
        let (eth, e0, sigma0, ya, p, yw, y0, y1) = match absorber {
            Absorber::HI => (13.60, 0.4298, 5.475e4, 32.88, 2.963, 0.0, 0.0, 0.0),
            Absorber::HeI => (24.59, 13.61, 949.2, 1.469, 3.188, 2.039, 0.4434, 2.136),
            Absorber::HeII => (54.42, 1.720, 1.369e4, 32.88, 2.963, 0.0, 0.0, 0.0),
        };
        if energy_ev < eth {
            return Ok(0.0);
        }
        let x = energy_ev / e0 - y0;
        let y = (x * x + y1 * y1).sqrt();
        let sigma = sigma0
            * ((x - 1.0).powi(2) + yw * yw)
            * y.powf(p / 2.0 - 5.5)
            * (1.0 + (y / ya).sqrt()).powf(-p)
            * 1e-18;
        if !sigma.is_finite() || sigma < 0.0 {
            return Err(ForwardError::InvalidInput("VERNER_RESULT_INVALID"));
        }
        Ok(sigma)
    }
```

## hhe_events.rs

Source SHA256: `c100b08e034089c2d67b2102769ccdd51f1d29a2f388d6bb2dfe7984af93b290`; bytes: 9447.

[rust/rei_microphysics/src/hhe_events.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/hhe_events.rs)

Lines 59–74:

```rust

impl HHeModel {
    pub fn controlled_fixture() -> Self {
        Self {
            n_h_cm3: 1e-4,
            n_he_cm3: 8.3e-6,
            c_cm_s: 29_979_245_800.0,
            kb_erg_k: 1.380_649e-16,
            ev_erg: 1.602_176_634e-12,
            threshold_ev: [13.598_434_599_702, 24.587_389_011, 54.417_76],
            photon_energy_ev: [13.7, 24.7, 54.5],
            sigma_cm2: [
                [6e-18, 1e-18, 1e-19],
                [0.0, 7e-18, 1e-18],
                [0.0, 0.0, 1.5e-18],
            ],
```
