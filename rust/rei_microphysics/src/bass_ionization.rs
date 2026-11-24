//! Electron history for the BASS native sky: x_e per H nucleus on the e-fold
//! clock eta = ln[(1 + z_emit)/(1 + z)] (BASS `--ionization` format).
//!
//! The history is assembled from three owners without overlap:
//! 1. an external recombination table (REC/HYREC) for z > z_high,
//! 2. a native REI H/He history on [z_low, z_high] (AX08 mean redshifts 20..4),
//! 3. a donor-matched continuation for 0 <= z < z_low that is continuous with
//!    the REI value at z_low and reaches full ionization 1 + 2 f_He at z = 0:
//!    x_e(z) = x_m + (1 + 2 f_He - x_m) [F(z) - F(z_low)] / [F(0) - F(z_low)],
//!    F(z) = [1 + tanh((y(z_HeII) - y(z)) / dy)]/2, y = (1+z)^{3/2},
//!    dy = 1.5 sqrt(1 + z_HeII) dz_HeII (htt_base R107 `DonorMatchedContinuation`).
//! The z < 4 shape is a conditional placeholder until astrophysical sources,
//! SEDs and absorbers are supplied; the join at z_high is reported, not smoothed.

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Knot {
    pub eta: f64,
    pub xe: f64,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Continuation {
    pub f_he: f64,
    pub z_heii: f64,
    pub dz_heii: f64,
}

impl Continuation {
    fn shape(&self, z: f64) -> f64 {
        let y = |z: f64| (1.0 + z).powf(1.5);
        let dy = 1.5 * (1.0 + self.z_heii).sqrt() * self.dz_heii;
        0.5 * (1.0 + ((y(self.z_heii) - y(z)) / dy).tanh())
    }
    /// Continuation value at 0 <= z <= z_match from the donor value x_match.
    pub fn xe(&self, z: f64, z_match: f64, x_match: f64) -> Result<f64, String> {
        if !(self.f_he > 0.0 && self.f_he < 1.0) || !(self.z_heii > 0.0) || !(self.dz_heii > 0.0)
        {
            return Err("continuation needs 0 < f_He < 1 and positive z_HeII and width".into());
        }
        if !(z_match > 0.0) || !z_match.is_finite() {
            return Err("continuation requires positive finite z_match".into());
        }
        let full = 1.0 + 2.0 * self.f_he;
        if !(1.0..=full).contains(&x_match) {
            return Err(format!(
                "donor x_e {x_match} at z = {z_match} lies outside [1, 1 + 2 f_He]"
            ));
        }
        if !(0.0..=z_match).contains(&z) {
            return Err("continuation is defined on 0 <= z <= z_match".into());
        }
        let (f, f0, fm) = (self.shape(z), self.shape(0.0), self.shape(z_match));
        Ok(x_match + (full - x_match) * (f - fm) / (f0 - fm))
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct MergeReport {
    pub z_high: f64,
    pub z_low: f64,
    /// REC x_e linearly interpolated in eta at z_high minus the first REI value.
    pub jump_at_z_high: f64,
    pub rec_knots: usize,
    pub rei_knots: usize,
    pub continuation_knots: usize,
}

fn eta_of(z: f64, z_emit: f64) -> f64 {
    ((1.0 + z_emit) / (1.0 + z)).ln()
}

/// Merge the three owners. `rec` is in BASS format (first eta = 0, increasing);
/// `rei` holds (z, x_e) pairs in any order on [z_low, z_high].
pub fn merge(
    rec: &[Knot],
    rei: &[(f64, f64)],
    z_emit: f64,
    continuation: Continuation,
    dz: f64,
) -> Result<(Vec<Knot>, MergeReport), String> {
    if !(z_emit > 0.0) || !(dz > 0.0) {
        return Err("z_emit and the continuation step must be positive".into());
    }
    if rec.len() < 2 || rec[0].eta != 0.0 {
        return Err("recombination table must start at eta = 0 with at least two knots".into());
    }
    for w in rec.windows(2) {
        if !(w[1].eta > w[0].eta) {
            return Err("recombination eta must increase strictly".into());
        }
    }
    if rec.iter().any(|k| !k.xe.is_finite() || k.xe < 0.0) {
        return Err("recombination x_e must be finite and nonnegative".into());
    }
    let mut rei: Vec<(f64, f64)> = rei.to_vec();
    if rei.len() < 2
        || rei
            .iter()
            .any(|(z, x)| !(z.is_finite() && *z >= 0.0 && x.is_finite() && *x >= 0.0))
    {
        return Err("REI history needs at least two finite (z >= 0, x_e >= 0) rows".into());
    }
    rei.sort_by(|a, b| b.0.total_cmp(&a.0));
    for w in rei.windows(2) {
        if !(w[1].0 < w[0].0) {
            return Err("REI redshifts must be distinct".into());
        }
    }
    let (z_high, z_low) = (rei[0].0, rei[rei.len() - 1].0);
    if z_high >= z_emit {
        return Err("REI history must start below the emission redshift".into());
    }
    let eta_high = eta_of(z_high, z_emit);
    let end = eta_of(0.0, z_emit);
    if rec[rec.len() - 1].eta < eta_high {
        return Err("recombination table does not reach the REI start".into());
    }
    // Linear-in-eta REC value at z_high.
    let i = rec.partition_point(|k| k.eta <= eta_high).clamp(1, rec.len() - 1);
    let (a, b) = (rec[i - 1], rec[i]);
    let rec_at_high = a.xe + (b.xe - a.xe) * (eta_high - a.eta) / (b.eta - a.eta);
    let mut out: Vec<Knot> = rec.iter().copied().filter(|k| k.eta < eta_high).collect();
    let rec_knots = out.len();
    for (z, x) in &rei {
        out.push(Knot {
            eta: eta_of(*z, z_emit),
            xe: *x,
        });
    }
    let x_match = rei[rei.len() - 1].1;
    let mut continuation_knots = 0;
    if z_low > 0.0 {
        let steps = (z_low / dz).ceil().max(1.0) as usize;
        for k in 1..=steps {
            let z = (z_low * (1.0 - k as f64 / steps as f64)).max(0.0);
            out.push(Knot {
                eta: if k == steps { end } else { eta_of(z, z_emit) },
                xe: continuation.xe(z, z_low, x_match)?,
            });
            continuation_knots += 1;
        }
    }
    for w in out.windows(2) {
        if !(w[1].eta > w[0].eta) {
            return Err("merged eta is not strictly increasing".into());
        }
    }
    Ok((
        out,
        MergeReport {
            z_high,
            z_low,
            jump_at_z_high: rec_at_high - rei[0].1,
            rec_knots,
            rei_knots: rei.len(),
            continuation_knots,
        },
    ))
}

#[cfg(test)]
mod tests {
    use super::*;

    const F_HE: f64 = 0.081_301_351_709_514_98;

    fn cont() -> Continuation {
        Continuation {
            f_he: F_HE,
            z_heii: 3.5,
            dz_heii: 0.5,
        }
    }

    #[test]
    fn continuation_is_continuous_and_reaches_full_ionization() {
        let c = cont();
        let x_m = 1.0 + F_HE;
        assert!((c.xe(4.0, 4.0, x_m).unwrap() - x_m).abs() < 1e-15);
        assert!((c.xe(0.0, 4.0, x_m).unwrap() - (1.0 + 2.0 * F_HE)).abs() < 1e-15);
        let mid = c.xe(3.5, 4.0, x_m).unwrap();
        assert!(mid > x_m && mid < 1.0 + 2.0 * F_HE);
        assert!(c.xe(4.5, 4.0, x_m).is_err());
        assert!(c.xe(1.0, 4.0, 0.5).is_err());
    }

    #[test]
    fn merge_has_single_owners_and_ends_at_z_zero() {
        let z_emit = 1100.0;
        let rec: Vec<Knot> = (0..=110)
            .map(|k| {
                let z = 1100.0 - 10.0 * k as f64;
                Knot {
                    eta: eta_of(z, z_emit),
                    xe: 2e-4 + 1e-6 * z,
                }
            })
            .collect();
        let rei: Vec<(f64, f64)> = (0..=16)
            .map(|k| {
                let z = 20.0 - k as f64;
                (z, if z > 8.0 { 2e-4 } else { 1.0 + F_HE })
            })
            .collect();
        let (out, report) = merge(&rec, &rei, z_emit, cont(), 0.05).unwrap();
        assert_eq!(out[0].eta, 0.0);
        assert!((out.last().unwrap().eta - (1101f64).ln()).abs() < 1e-15);
        assert!((out.last().unwrap().xe - (1.0 + 2.0 * F_HE)).abs() < 1e-15);
        assert_eq!(report.rei_knots, 17);
        assert_eq!(report.continuation_knots, 80);
        assert!((report.jump_at_z_high - 2e-5).abs() < 1e-12, "{}", report.jump_at_z_high);
        assert!(out.windows(2).all(|w| w[1].eta > w[0].eta));
        let bad = vec![Knot { eta: 0.1, xe: 0.1 }, Knot { eta: 0.2, xe: 0.1 }];
        assert!(merge(&bad, &rei, z_emit, cont(), 0.05).is_err());
    }

    #[test]
    fn z_low_zero_skips_continuation_without_nan_or_duplicate_eta() {
        let z_emit = 1100.0;
        let rec: Vec<Knot> = (0..=110)
            .map(|k| Knot {
                eta: eta_of(1100.0 - 10.0 * k as f64, z_emit),
                xe: 2e-4,
            })
            .collect();
        let rei: Vec<(f64, f64)> = (0..=20)
            .map(|k| (20.0 - k as f64, if k == 20 { 1.0 + 2.0 * F_HE } else { 1.0 }))
            .collect();
        let (out, report) = merge(&rec, &rei, z_emit, cont(), 0.05).unwrap();
        assert_eq!(report.continuation_knots, 0);
        assert!((out.last().unwrap().eta - (1101f64).ln()).abs() < 1e-15);
        assert!(out.iter().all(|k| k.xe.is_finite()));
        assert!(out.windows(2).all(|w| w[1].eta > w[0].eta));
        assert!(cont().xe(0.0, 0.0, 1.0 + F_HE).is_err());
    }
}
