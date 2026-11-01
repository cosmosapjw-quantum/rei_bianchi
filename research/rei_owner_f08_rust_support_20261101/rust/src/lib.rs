//! Source-resolved F08 Bianchi I photon energy characteristic.
//! Experimental owner adapter: no chemistry, OTS, SDIRK, interval guarantee or production admission.
//! Original reference: rei_microphysics/src/paired_runtime.rs (SHA256 b6c1d2a07ab51ff02318139ae18387b77f61859c08037347f788524df770ebe7).
#![forbid(unsafe_code)]

pub const SOURCE_EV: f64 = 13.7;
pub const H: [f64; 3] = [1.01e-14, 0.99e-14, 1.0e-14];
pub const FIRST_DT_S: f64 = 6.25e8;
pub const LOWER_NODE_EV: f64 = 13.675;
pub const INITIAL_PHOTONS_PER_H: f64 = 0.05;

#[derive(Clone, Copy, Debug)]
pub struct CharacteristicPhoton {
    pub birth_ev: f64,
    pub photons_per_h: f64,
    pub q: [f64; 3],
}

fn valid_unit_q(q: [f64; 3]) -> bool {
    q.iter().all(|a| a.is_finite()) && (q.iter().map(|a| a * a).sum::<f64>() - 1.0).abs() < 2e-12
}
pub fn qhat(n_mu: usize, n_phi: usize, d: usize) -> Result<[f64; 3], &'static str> {
    if n_mu == 0 || n_phi == 0 || d >= n_mu.saturating_mul(n_phi) {
        return Err("GRID");
    }
    let imu = d / n_phi;
    let iphi = d % n_phi;
    let mu = -1.0 + 2.0 * (imu as f64 + 0.5) / n_mu as f64;
    let phi = 2.0 * std::f64::consts::PI * (iphi as f64 + 0.5) / n_phi as f64;
    let r = (1.0 - mu * mu).sqrt();
    let a = [r * phi.cos(), r * phi.sin(), mu];
    let norm = a[0].hypot(a[1]).hypot(a[2]);
    Ok(a.map(|x| x / norm))
}
pub fn energy_after(ph: CharacteristicPhoton, h: [f64; 3], dt_s: f64) -> Result<f64, &'static str> {
    if !valid_unit_q(ph.q)
        || !ph.birth_ev.is_finite()
        || ph.birth_ev <= 0.0
        || !ph.photons_per_h.is_finite()
        || ph.photons_per_h < 0.0
        || !dt_s.is_finite()
        || dt_s < 0.0
        || h.iter().any(|x| !x.is_finite())
    {
        return Err("INPUT_DOMAIN");
    }
    let sum = (0..3)
        .map(|i| ph.q[i] * ph.q[i] * (-2.0 * h[i] * dt_s).exp())
        .sum::<f64>();
    let e = ph.birth_ev * sum.sqrt();
    if !e.is_finite() || e <= 0.0 {
        return Err("ENERGY_UNDERFLOW");
    }
    Ok(e)
}
pub fn native_first_step_witness() -> Result<(f64, f64, f64), &'static str> {
    // Mirrors the ORIGINAL fixed-bin hat allocation, but returns it only as a failure witness.
    // Actual characteristics never deposit into the lower grid node.
    let mut ghost = 0.0;
    let mut min_energy = f64::INFINITY;
    let mut max_energy = f64::NEG_INFINITY;
    let nd = 8 * 16;
    for d in 0..nd {
        let ph = CharacteristicPhoton {
            birth_ev: SOURCE_EV,
            photons_per_h: INITIAL_PHOTONS_PER_H / nd as f64,
            q: qhat(8, 16, d)?,
        };
        let e = energy_after(ph, H, FIRST_DT_S)?;
        min_energy = min_energy.min(e);
        max_energy = max_energy.max(e);
        if e < LOWER_NODE_EV || e > SOURCE_EV {
            return Err("OUTSIDE_NATIVE_HAT_INTERVAL");
        }
        ghost += ph.photons_per_h * (SOURCE_EV - e) / (SOURCE_EV - LOWER_NODE_EV);
    }
    Ok((ghost, min_energy, max_energy))
}
pub fn first_order_leakage() -> f64 {
    let mean_h = (H[0] + H[1] + H[2]) / 3.0;
    INITIAL_PHOTONS_PER_H * SOURCE_EV * mean_h * FIRST_DT_S / (SOURCE_EV - LOWER_NODE_EV)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn reproduces_original_native_128ray_leak() {
        let (ghost, min_e, max_e) = native_first_step_witness().unwrap();
        let original = 0.00017124946478640907_f64;
        assert!(
            (ghost - original).abs() < 1e-14,
            "ghost {ghost} original {original}"
        );
        assert!(min_e > 13.699913519 && max_e < SOURCE_EV && min_e > LOWER_NODE_EV);
        assert!((ghost - first_order_leakage()).abs() < 1e-9);
    }
    #[test]
    fn literal_characteristics_do_not_create_subsupport_photons() {
        for i in 0..128 {
            let ph = CharacteristicPhoton {
                birth_ev: SOURCE_EV,
                photons_per_h: INITIAL_PHOTONS_PER_H / 128.0,
                q: qhat(8, 16, i).unwrap(),
            };
            let e = energy_after(ph, H, FIRST_DT_S).unwrap();
            assert!(e > LOWER_NODE_EV);
        }
    }
    #[test]
    fn isotropic_exact_redshift_and_number_unchanged() {
        let p = CharacteristicPhoton {
            birth_ev: SOURCE_EV,
            photons_per_h: INITIAL_PHOTONS_PER_H,
            q: qhat(8, 16, 0).unwrap(),
        };
        let e = energy_after(p, [1e-14; 3], FIRST_DT_S).unwrap();
        assert!((e - SOURCE_EV * (-1e-14 * FIRST_DT_S).exp()).abs() < 1e-13);
        assert_eq!(p.photons_per_h, INITIAL_PHOTONS_PER_H);
    }
    #[test]
    fn rejected_nonunit_direction_and_negative_photons() {
        let bad = CharacteristicPhoton {
            birth_ev: SOURCE_EV,
            photons_per_h: -0.1,
            q: [1.0, 0.0, 0.0],
        };
        assert!(energy_after(bad, H, FIRST_DT_S).is_err());
        let bad = CharacteristicPhoton {
            birth_ev: SOURCE_EV,
            photons_per_h: 0.1,
            q: [0.3, 0.3, 0.3],
        };
        assert!(energy_after(bad, H, FIRST_DT_S).is_err());
    }
}
