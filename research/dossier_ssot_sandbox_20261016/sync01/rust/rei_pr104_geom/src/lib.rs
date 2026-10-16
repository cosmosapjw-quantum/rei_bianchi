//! Sampled PR104 RUN002 geometry interface, not a native EoR solver.
#![forbid(unsafe_code)]
use rei_ssot_reference::{DiagonalGeometry, Ray, RefError};

pub const HEADER: &str = "x,z,Q,Nrec,Nemit,Nexcess,tau,t_s,b,ne_cm3,nH_cm3,H_s,ledger";
pub const RP01_SAMPLES: &str = include_str!("../../../fixtures/pr104_rp01_sample.csv");
pub const FLRW_SAMPLES: &str = include_str!("../../../fixtures/pr104_flrw_sample.csv");

#[derive(Clone, Copy, Debug)]
pub struct ReducedRow {
    pub x: f64,
    pub z: f64,
    pub q: f64,
    pub nrec: f64,
    pub nemit: f64,
    pub nexcess: f64,
    pub tau: f64,
    pub t_s: f64,
    pub b: f64,
    pub ne_cm3: f64,
    pub nh_cm3: f64,
    pub h_s: f64,
    pub ledger: f64,
}

impl ReducedRow {
    fn from_csv(line: &str) -> Result<Self, &'static str> {
        let fields: Vec<_> = line.split(',').collect();
        if fields.len() != 13 {
            return Err("expected_13_fields");
        }
        let mut v = [0.0; 13];
        for (dest, src) in v.iter_mut().zip(fields) {
            *dest = src.parse().map_err(|_| "invalid_number")?;
        }
        if v.iter().any(|x: &f64| !x.is_finite()) {
            return Err("nonfinite");
        }
        let out = Self {
            x: v[0],
            z: v[1],
            q: v[2],
            nrec: v[3],
            nemit: v[4],
            nexcess: v[5],
            tau: v[6],
            t_s: v[7],
            b: v[8],
            ne_cm3: v[9],
            nh_cm3: v[10],
            h_s: v[11],
            ledger: v[12],
        };
        out.validate()?;
        Ok(out)
    }
    pub fn validate(&self) -> Result<(), &'static str> {
        if self.x < 0.0
            || self.z < 0.0
            || !(0.0..=1.0).contains(&self.q)
            || self.nrec < 0.0
            || self.nemit < 0.0
            || self.nexcess < 0.0
            || self.tau < 0.0
            || self.t_s < 0.0
            || self.ne_cm3 < 0.0
            || self.nh_cm3 <= 0.0
            || self.h_s <= 0.0
        {
            return Err("row_outside_physical_domain");
        }
        let expected_z = 21.0 * (-self.x).exp() - 1.0;
        if (expected_z - self.z).abs() > 2.0e-11 {
            return Err("mean_redshift_inconsistent");
        }
        let counter = self.q + self.nrec + self.nexcess - self.nemit;
        if (counter - self.ledger).abs() > 3.0e-13 {
            return Err("reduced_photon_counter_inconsistent");
        }
        Ok(())
    }
    pub fn geometry(&self, b: f64) -> Result<DiagonalGeometry, RefError> {
        let a = self.x.exp();
        let transverse = a * (-b).exp();
        let longitudinal = a * (2.0 * b).exp();
        if !transverse.is_finite()
            || !longitudinal.is_finite()
            || transverse <= 0.0
            || longitudinal <= 0.0
        {
            return Err(RefError::Overflow("scale_factor"));
        }
        Ok(DiagonalGeometry {
            a: [transverse, transverse, longitudinal],
        })
    }
}

pub fn parse_samples(csv: &str) -> Result<Vec<ReducedRow>, &'static str> {
    let mut lines = csv.lines();
    if lines.next() != Some(HEADER) {
        return Err("wrong_header");
    }
    let rows: Vec<_> = lines.map(ReducedRow::from_csv).collect::<Result<_, _>>()?;
    if rows.len() != 3 {
        return Err("expected_three_sampled_rows");
    }
    for w in rows.windows(2) {
        if w[0].x >= w[1].x || w[0].t_s >= w[1].t_s || w[0].tau > w[1].tau {
            return Err("nonmonotonic_sample_order");
        }
    }
    Ok(rows)
}

/// Exact LRS Killing map: E_emit/E_observed for an observer-tetrad direction.
/// The second result is the angular-only isotropized reference at matched mean-a.
/// A common mean-a is not the same as a common proper-time epoch.
pub fn energy_ratio(emit: ReducedRow, obs: ReducedRow, mu: f64) -> Result<(f64, f64), RefError> {
    if !mu.is_finite() || !(-1.0..=1.0).contains(&mu) || emit.x > obs.x {
        return Err(RefError::InvalidInput("mu_or_order"));
    }
    let direction = [(1.0 - mu * mu).sqrt(), 0.0, mu];
    let ray = Ray {
        energy_ev: 1.0,
        direction,
    };
    let physical = obs
        .geometry(obs.b)?
        .transport(emit.geometry(emit.b)?, ray)?;
    let iso = obs.geometry(0.0)?.transport(emit.geometry(0.0)?, ray)?;
    Ok((physical.energy_ratio, iso.energy_ratio))
}

pub fn delta_ln_energy(emit: ReducedRow, obs: ReducedRow, mu: f64) -> Result<f64, RefError> {
    let (actual, iso) = energy_ratio(emit, obs, mu)?;
    Ok((actual / iso).ln())
}

/// a_2 = 5/2 integral_{-1}^{1} delta ln(E_emit/E_obs) P2(mu) dmu.
/// Simpson quadrature; source geometry at sampled endpoints is held exact.
pub fn p2_coefficient(emit: ReducedRow, obs: ReducedRow, n: usize) -> Result<f64, RefError> {
    if !(2..=8192).contains(&n) || !n.is_multiple_of(2) {
        return Err(RefError::InvalidInput("even_n_in_2_8192"));
    }
    let h = 2.0 / n as f64;
    let mut s = 0.0;
    for i in 0..=n {
        let mu = -1.0 + i as f64 * h;
        let p2 = 0.5 * (3.0 * mu * mu - 1.0);
        let f = delta_ln_energy(emit, obs, mu)? * p2;
        let w = if i == 0 || i == n {
            1.0
        } else if i % 2 == 0 {
            2.0
        } else {
            4.0
        };
        s += w * f;
    }
    Ok(5.0 * h * s / 6.0)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn close(a: f64, b: f64, tolerance: f64) {
        assert!((a - b).abs() <= tolerance * b.abs().max(1.0), "{a} vs {b}");
    }
    fn rp() -> Vec<ReducedRow> {
        parse_samples(RP01_SAMPLES).unwrap()
    }
    fn fl() -> Vec<ReducedRow> {
        parse_samples(FLRW_SAMPLES).unwrap()
    }

    #[test]
    fn samples_parse_and_reduced_ledger() {
        let _ = rp();
        let _ = fl();
    }
    #[test]
    fn equal_mean_scale_but_different_proper_times() {
        let r = rp();
        let f = fl();
        for i in 0..3 {
            close(r[i].x, f[i].x, 1e-14);
            close(r[i].z, f[i].z, 1e-14);
        }
        assert_ne!(r[2].t_s, f[2].t_s);
    }
    #[test]
    fn stored_optical_depth_is_partial_only() {
        close(rp()[2].tau, 0.037_415_709_019_163_92, 1e-14);
        close(fl()[2].tau, 0.037_441_821_268_862_3, 1e-14);
    }
    #[test]
    fn isotropic_limit() {
        let f = fl();
        for mu in [-1.0, -0.4, 0.0, 0.6, 1.0] {
            close(delta_ln_energy(f[0], f[2], mu).unwrap(), 0.0, 1e-14);
        }
    }
    #[test]
    fn exact_lrs_axes() {
        let r = rp();
        let b = r[2].b - r[0].b;
        close(delta_ln_energy(r[0], r[2], 0.0).unwrap(), -b, 1e-14);
        close(delta_ln_energy(r[0], r[2], 1.0).unwrap(), 2.0 * b, 1e-14);
    }
    #[test]
    fn angular_parity() {
        let r = rp();
        for m in [0.2, 0.7, 0.99] {
            close(
                delta_ln_energy(r[0], r[2], m).unwrap(),
                delta_ln_energy(r[0], r[2], -m).unwrap(),
                1e-14,
            );
        }
    }
    #[test]
    fn zero_interval() {
        let r = rp();
        close(delta_ln_energy(r[1], r[1], 0.4).unwrap(), 0.0, 1e-14);
    }
    #[test]
    fn quadrupole_converges() {
        let r = rp();
        let q512 = p2_coefficient(r[0], r[2], 512).unwrap();
        let q1024 = p2_coefficient(r[0], r[2], 1024).unwrap();
        close(q512, q1024, 2e-10);
    }
    #[test]
    fn linear_b_coefficient() {
        let r = rp();
        let mut o = r[2];
        o.b = 1.0e-7;
        close(p2_coefficient(r[0], o, 64).unwrap(), 2.0e-7, 1e-12);
    }
    #[test]
    fn reject_invalid_mu() {
        let r = rp();
        assert!(energy_ratio(r[0], r[2], 1.01).is_err());
    }
    #[test]
    fn reject_corrupted_saved_row() {
        let mut r = rp();
        r[1].z = 80.0;
        assert!(r[1].validate().is_err());
        r[1] = rp()[1];
        r[1].nemit += 0.01;
        assert!(r[1].validate().is_err());
    }
    #[test]
    fn reject_physical_intensity_claim_without_spectrum() {
        let s = include_str!("../../../docs/SCIENTIFIC_SCOPE.md");
        assert!(s.contains("IONIZING_SPECTRUM_MISSING"));
    }
}
