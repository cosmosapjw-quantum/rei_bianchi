use crate::{positive, radiation::SPECIES, Fallible};
use rei_microphysics::verner_cutoff_ev;
/// Additive exact-event representation. No epsilon, nextafter or changed support.
pub fn start_energy(eta: f64, a: f64, b: f64) -> Fallible<(f64, bool)> {
    if !(b > a) {
        return Err("invalid anchored segment".into());
    }
    let mut at_start = None;
    let mut at_end = None;
    for atom in SPECIES {
        let c = verner_cutoff_ev(atom);
        let t = eta - c.ln();
        if a == t {
            at_start = Some(c)
        }
        if b == t {
            at_end = Some(c)
        }
    }
    let decay = positive((-(b - a)).exp())?;
    if let Some(c) = at_end {
        let e = positive(c / decay)?;
        if e * decay != c {
            return Err(format!("exact-event division/multiplication incompatibility: cutoff={c:.17e}, computed={:.17e}",e*decay));
        }
        if at_start.is_some_and(|v| v != e) {
            return Err("incompatible exact start/end event anchors".into());
        }
        Ok((e, true))
    } else if let Some(c) = at_start {
        Ok((c, true))
    } else {
        Ok((positive((eta - a).exp())?, false))
    }
}
