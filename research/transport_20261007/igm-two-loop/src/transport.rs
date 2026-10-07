//! Prescribed transparent FLRW controls with a continuous moving lower face.
//! No gas solver, persistent photon packets, inverse closure, or time integration.
use crate::panel::Panel;
use crate::tail::{self, LogPositive as LP, TailOwners};
pub const EC: f64 = 13.6;
type R<T> = Result<T, String>;

#[derive(Clone, Copy, Debug, Default)]
pub struct LossBudget {
    pub number: f64,
    pub energy: f64,
}
#[derive(Clone, Copy, Debug, Default)]
pub struct Sweep {
    pub owners: TailOwners,
    pub loss: LossBudget,
    pub sites: usize,
    pub max_panel_rule_sites: usize,
    pub anchor_relative: f64,
    pub band_exit_relative: f64,
}

fn upward_add(a: f64, b: f64) -> R<f64> {
    if b == 0.0 {
        return Ok(a);
    }
    let s = a + b;
    if !s.is_finite() || s < 0.0 {
        return Err("loss bound overflow".into());
    }
    Ok(f64::from_bits(s.to_bits() + 1))
}
/// A deliberately loose positive conversion enclosure. Only discarded-addend
/// and final readout losses are covered, not arbitrary log/kernel roundoff.
fn upper(x: LP) -> R<f64> {
    if x.is_empty() {
        return Ok(0.0);
    }
    let (h, l) = x.log_parts();
    if h < -709.0 && l.abs() < h.abs() * 1e-12 {
        return Ok(16.0 * f64::MIN_POSITIVE);
    }
    let v = x.readout()?.value;
    if v == 0.0 || !v.is_finite() || v > f64::MAX / 4.0 {
        return Err("unsupported loss conversion".into());
    }
    Ok(4.0 * v)
}
impl LossBudget {
    fn add(&mut self, o: TailOwners) -> R<()> {
        let a = o.as_array();
        for i in [0, 2, 3, 4, 9, 11] {
            self.number = upward_add(self.number, upper(a[i])?)?;
        }
        for i in [1, 5, 6, 7, 8, 10, 12] {
            self.energy = upward_add(self.energy, upper(a[i])?)?;
        }
        Ok(())
    }
    fn readouts(&mut self, o: TailOwners) -> R<()> {
        for (i, x) in o.as_array().into_iter().enumerate() {
            let r = x.readout()?;
            let amount = upper(r.zero_readout_bound)? + upper(r.subnormal_readout_bound)?;
            if [0, 2, 3, 4, 9, 11].contains(&i) {
                self.number = upward_add(self.number, amount)?;
            } else {
                self.energy = upward_add(self.energy, amount)?;
            }
        }
        Ok(())
    }
}
fn accumulate(total: &mut Sweep, owners: TailOwners, loss: TailOwners, weight: LP) -> R<()> {
    total.loss.add(loss.scale(weight)?)?;
    let (sum, dropped) = total.owners.add(owners.scale(weight)?)?;
    total.loss.add(dropped)?;
    total.owners = sum;
    Ok(())
}

/// Exact supplied f64 boundary is part of the experiment's geometric input.
pub fn sweep_stock(panel: &Panel, s0: f64, s1: f64, parts: usize) -> R<Sweep> {
    if !s0.is_finite() || !s1.is_finite() || s1 < s0 || parts == 0 || parts > 1024 {
        return Err("invalid stock sweep".into());
    }
    panel.validate().map_err(|e| format!("panel: {e:?}"))?;
    if panel.l < s0 + EC.ln() {
        return Err("initial stock below tracking boundary".into());
    }
    let boundary = s1 + EC.ln();
    let mut cuts: Vec<f64> = (0..=parts)
        .map(|i| panel.l + (panel.r - panel.l) * i as f64 / parts as f64)
        .collect();
    cuts[parts] = panel.r;
    if boundary > panel.l && boundary < panel.r {
        cuts.push(boundary);
    }
    cuts.sort_by(f64::total_cmp);
    cuts.dedup();
    let mut total = Sweep::default();
    for pair in cuts.windows(2) {
        let r = panel
            .restrict(pair[0], pair[1])
            .map_err(|e| format!("restriction: {e:?}"))?
            .ok_or("empty integration cell")?;
        let eta = r
            .quadrature_node()
            .map_err(|e| format!("stock node: {e:?}"))?;
        let (hi, lo) = r.log_amplitude_parts();
        let weight = LP::from_log_parts(hi, lo)?;
        let e0 = (eta - s0).exp();
        let mut c = if pair[1] <= boundary {
            let anchored = tail::characteristic_to_cutoff(
                LP::from_linear(1.0)?,
                LP::empty(),
                [0.; 3],
                e0,
                EC,
            )?;
            total.anchor_relative = total
                .anchor_relative
                .max(anchored.energy_anchor_roundtrip_relative.abs());
            anchored.characteristic
        } else {
            tail::characteristic(LP::from_linear(1.0)?, LP::empty(), [0.; 3], s1 - s0, e0)?
        };
        if pair[1] <= boundary {
            let ex = tail::export(c.owners)?;
            total.loss.add(ex.omitted_addend_bounds.scale(weight)?)?;
            c.owners = ex.owners;
        }
        accumulate(&mut total, c.owners, c.omitted_addend_bounds, weight)?;
        total.sites += 1;
        total.max_panel_rule_sites = total.max_panel_rule_sites.max(r.panels * 8);
    }
    total.loss.readouts(total.owners)?;
    Ok(total)
}

const GX: [f64; 4] = [
    0.1834346424956498,
    0.5255324099163290,
    0.7966664774136267,
    0.9602898564975363,
];
const GW: [f64; 4] = [
    0.3626837833783620,
    0.3137066458778873,
    0.2223810344533745,
    0.1012285362903763,
];
/// Constant source q per dη ds in the fixed physical energy band. The source is
/// split into birth/band-exit/cutoff histories before integrating geometric dη.
pub fn sweep_source(h: f64, q: f64, emin: f64, emax: f64, subdivisions: usize) -> R<Sweep> {
    if ![h, q, emin, emax].iter().all(|x| x.is_finite())
        || h < 0.0
        || q <= 0.0
        || emin <= EC
        || emax <= emin
        || emax > 50000.0
        || subdivisions == 0
        || subdivisions > 64
    {
        return Err("invalid source sweep".into());
    }
    if h == 0.0 {
        return Ok(Sweep::default());
    }
    let lm = emin.ln();
    let lx = emax.ln();
    let lc = EC.ln();
    let boundary = h + lc;
    let mut cuts = vec![lm, lx, h + lm, h + lx, boundary];
    cuts.retain(|x| *x >= lm && *x <= h + lx);
    cuts.sort_by(f64::total_cmp);
    cuts.dedup();
    let mut total = Sweep::default();
    for ab in cuts.windows(2) {
        for j in 0..subdivisions {
            let a = ab[0] + (ab[1] - ab[0]) * j as f64 / subdivisions as f64;
            let b = if j + 1 == subdivisions {
                ab[1]
            } else {
                ab[0] + (ab[1] - ab[0]) * (j + 1) as f64 / subdivisions as f64
            };
            let half = (b - a) * 0.5;
            let center = a + half;
            for k in 0..4 {
                for sign in [-1., 1.] {
                    let eta = center + sign * half * GX[k];
                    if !(eta > a && eta < b) {
                        return Err("unresolved source quadrature node".into());
                    }
                    let enter = 0.0_f64.max(eta - lx);
                    let leave = h.min(eta - lm);
                    if leave <= enter {
                        return Err("unresolved positive source duration".into());
                    }
                    let first = tail::characteristic(
                        LP::empty(),
                        LP::from_linear(q)?,
                        [0.; 3],
                        leave - enter,
                        (eta - enter).exp(),
                    )?;
                    let mut c = first.owners;
                    let mut losses = LossBudget::default();
                    let weight = LP::from_linear(half * GW[k])?;
                    losses.add(first.omitted_addend_bounds.scale(weight)?)?;
                    let exits = ab[1] <= boundary;
                    if exits || leave < h {
                        // Audit the actual carried-U -> explicit source-band endpoint map.
                        // Reject outside the inherited endpoint continuity target, without
                        // changing any owner to repair a conservation residual.
                        let expected = c.n.mul(LP::from_linear(tail::EV_ERG)?)?.scale(emin)?;
                        let (uh, ul) = c.u.log_parts();
                        let (eh, el) = expected.log_parts();
                        let band_error = ((uh - eh) + (ul - el)).exp_m1().abs();
                        if !band_error.is_finite() || band_error > 2e-12 {
                            return Err("band-exit energy continuity".into());
                        }
                        total.band_exit_relative = total.band_exit_relative.max(band_error);
                        let next = if exits {
                            // Actual band-exit energy is an explicit physical event anchor.
                            let z = tail::characteristic_to_cutoff(
                                c.n,
                                LP::empty(),
                                [0.; 3],
                                emin,
                                EC,
                            )?;
                            total.anchor_relative = total
                                .anchor_relative
                                .max(z.energy_anchor_roundtrip_relative.abs());
                            z.characteristic
                        } else {
                            tail::characteristic(c.n, LP::empty(), [0.; 3], h - leave, emin)?
                        };
                        c.n = LP::empty();
                        c.u = LP::empty();
                        let (sum, dropped) = c.add(next.owners)?;
                        c = sum;
                        losses.add(dropped.scale(weight)?)?;
                        losses.add(next.omitted_addend_bounds.scale(weight)?)?;
                    }
                    if exits {
                        let ex = tail::export(c)?;
                        c = ex.owners;
                        losses.add(ex.omitted_addend_bounds.scale(weight)?)?;
                    }
                    total.loss.number = upward_add(total.loss.number, losses.number)?;
                    total.loss.energy = upward_add(total.loss.energy, losses.energy)?;
                    accumulate(&mut total, c, TailOwners::default(), weight)?;
                    total.sites += 1;
                }
            }
        }
    }
    total.loss.readouts(total.owners)?;
    Ok(total)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn source_onset_is_zero_then_quadratic() {
        let d = 13.7_f64.ln() - EC.ln();
        assert!(sweep_source(d, 1e-8, 13.7, 20., 1)
            .unwrap()
            .owners
            .outn
            .is_empty());
        let x = sweep_source(d + 0.001, 1e-8, 13.7, 20., 1).unwrap();
        let y = sweep_source(d + 0.002, 1e-8, 13.7, 20., 1).unwrap();
        let ratio = y.owners.outn.readout().unwrap().value / x.owners.outn.readout().unwrap().value;
        assert!((ratio - 4.0).abs() < 1e-10);
    }
    #[test]
    fn output_schedule_does_not_advance_a_state() {
        let a = sweep_source(0.1, 1e-8, 13.7, 20., 1).unwrap();
        let _ = sweep_source(0.03, 1e-8, 13.7, 20., 1).unwrap();
        assert_eq!(
            a.owners,
            sweep_source(0.1, 1e-8, 13.7, 20., 1).unwrap().owners
        );
    }
}
