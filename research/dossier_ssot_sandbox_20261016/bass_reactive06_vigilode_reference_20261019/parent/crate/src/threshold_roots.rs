//! Bianchi-I photo-edge crossing roots within a finite proper-time interval.
//! Exactly preserves the immutable original geometry and photo providers.
//! Splits 13.60, 24.59, 54.42 eV (Verner H/He fitted edges) and the
//! explicit DAtomicProvider binding threshold chi_D, NOT gas binding edges.
//! Supports signed prescribed shear and at most one energy turning point.
use crate::bianchi_i::{ConstantAxisymmetricBackground, GeometryBackground, GeometrySnapshot};
use crate::full_network::NetworkError;
use crate::source_age::Cohort;

pub const VERNER_EDGES_EV: [f64; 3] = [13.60, 24.59, 54.42];

fn energy(co: &Cohort, geom: &ConstantAxisymmetricBackground, t: f64) -> Result<f64, NetworkError> {
    let snap = geom
        .snapshot(t)
        .map_err(|_| NetworkError::InputOutsideDomain)?;
    Ok(co.ray_at(&snap)?.energy_ev)
}

/// Unique stationary point of E^2 for axisymmetric constant directional Hubble.
/// If all weighted directional Hubble parameters share a sign, it is monotone.
/// This is a prescribed metric calculation, NOT an Einstein on-shell proof.
pub fn turning_time(
    co: &Cohort,
    geom: &ConstantAxisymmetricBackground,
) -> Result<Option<f64>, NetworkError> {
    let mu = co.direction_at_birth[2];
    if !mu.is_finite() {
        return Err(NetworkError::InvalidInput);
    }
    let wpar = mu * mu;
    let wperp = co.direction_at_birth[0].powi(2) + co.direction_at_birth[1].powi(2);
    let h = geom.reference_point.mean_hubble_per_s;
    let sh = geom.reference_point.shear_per_s;
    let hp = h - sh;
    let hz = h + 2.0 * sh;
    if !h.is_finite() || !sh.is_finite() || hp * hz >= 0.0 || wperp == 0.0 || wpar == 0.0 {
        return Ok(None);
    }
    let ratio = -wpar * hz / (wperp * hp);
    if !ratio.is_finite() || ratio <= 0.0 || hz == hp {
        return Err(NetworkError::InputOutsideDomain);
    }
    let t = co.birth_time_s + ratio.ln() / (2.0 * (hz - hp));
    if !t.is_finite() {
        return Err(NetworkError::NonFinite);
    }
    Ok(Some(t))
}

/// Return [start, all interior photo-fit/binding opacity edges, end].
/// An optional turning point makes each bracket monotonic, therefore a
/// bisection finds every isolated threshold root, including two crossings
/// of the same edge in contracting/transverse-expanding backgrounds.
pub fn split_by_thresholds(
    geom: &ConstantAxisymmetricBackground,
    co: &Cohort,
    ta: f64,
    tb: f64,
    ga: &GeometrySnapshot,
    gb: &GeometrySnapshot,
    d_threshold_ev: f64,
) -> Result<Vec<f64>, NetworkError> {
    if !ta.is_finite()
        || !tb.is_finite()
        || tb <= ta
        || !d_threshold_ev.is_finite()
        || d_threshold_ev <= 0.0
    {
        return Err(NetworkError::InvalidInput);
    }
    split_by_thresholds_from_energies(
        geom,
        co,
        ta,
        tb,
        co.ray_at(ga)?.energy_ev,
        co.ray_at(gb)?.energy_ev,
        d_threshold_ev,
    )
}

/// Identical root algorithm, accepting ray energies computed by the caller once.
pub fn split_by_thresholds_from_energies(
    geom: &ConstantAxisymmetricBackground,
    co: &Cohort,
    ta: f64,
    tb: f64,
    e0: f64,
    e1: f64,
    d_threshold_ev: f64,
) -> Result<Vec<f64>, NetworkError> {
    if !e0.is_finite() || !e1.is_finite() || e0 <= 0. || e1 <= 0. {
        return Err(NetworkError::InputOutsideDomain);
    }

    let mut monotone = vec![ta];
    if let Some(tturn) = turning_time(co, geom)?
        && tturn > ta
        && tturn < tb
    {
        monotone.push(tturn);
    }
    monotone.push(tb);
    let mut boundaries = vec![ta];
    for window in monotone.windows(2) {
        let a = window[0];
        let b = window[1];
        let ea = if a == ta { e0 } else { energy(co, geom, a)? };
        let eb = if b == tb { e1 } else { energy(co, geom, b)? };
        for edge in [
            VERNER_EDGES_EV[0],
            VERNER_EDGES_EV[1],
            VERNER_EDGES_EV[2],
            d_threshold_ev,
        ] {
            let fa = ea / edge - 1.0;
            let fb = eb / edge - 1.0;
            if (fa < 0.0 && fb > 0.0) || (fa > 0.0 && fb < 0.0) {
                let (mut lo, mut hi, mut flo) = (a, b, fa);
                for _ in 0..100 {
                    let mid = lo + 0.5 * (hi - lo);
                    if mid == lo || mid == hi {
                        break;
                    }
                    let fm = energy(co, geom, mid)? / edge - 1.0;
                    if fm == 0.0 {
                        lo = mid;
                        hi = mid;
                        break;
                    }
                    if (fm < 0.0) == (flo < 0.0) {
                        lo = mid;
                        flo = fm;
                    } else {
                        hi = mid;
                    }
                }
                let root = lo + 0.5 * (hi - lo);
                if root > ta && root < tb {
                    boundaries.push(root);
                }
            }
        }
    }
    boundaries.push(tb);
    boundaries.sort_by(f64::total_cmp);
    // Adjacent roots are distinct physically unless unresolvable in f64 time.
    boundaries
        .dedup_by(|a, b| (*a - *b).abs() <= 32.0 * f64::EPSILON * ta.abs().max(tb.abs()).max(1.0));
    if boundaries.len() < 2 || boundaries[0] != ta || *boundaries.last().unwrap() != tb {
        return Err(NetworkError::NoForwardProgress);
    }
    Ok(boundaries)
}
