//! HE20 native Rust conditional continuum-spectrum cutoff test.
//! Original rei_microphysics at f7830e2; no changes to the receiver.
//! Source-only: no H/He chemistry or full reionization claim.
use rei_microphysics::axbi_driver::{Driver, DriverConfig};
use rei_microphysics::axbi_q_reference::CovariantPhoton;
use rei_microphysics::axbi_sources::SpectralCell;
use rei_microphysics::{CharacteristicRay, HHeModel};
use std::cmp::Ordering;
const CUTS: [f64; 3] = [13.6, 24.59, 54.42];

#[derive(Clone, Copy, Debug)]
struct Child {
    lo: f64,
    hi: f64,
    n: f64,
    u: f64,
}
fn shape(e: f64) -> f64 {
    let m = HHeModel::controlled_fixture();
    let kt = m.kb_erg_k / m.ev_erg * 50000.;
    e * e / (e / kt).exp_m1()
}
fn simpson(lo: f64, hi: f64, power: i32) -> f64 {
    assert!(lo.is_finite() && hi.is_finite() && lo > 0. && hi >= lo);
    if hi == lo {
        return 0.;
    }
    let h = (hi - lo) / 32.;
    let mut sum = 0.;
    for j in 0..=32 {
        let e = lo + (j as f64) * h;
        let w = if j == 0 || j == 32 {
            1.
        } else if j % 2 == 0 {
            2.
        } else {
            4.
        };
        sum += w * shape(e) * e.powi(power);
    }
    sum * h / 3.
}

/// Partition each source cell at the *preimages* of all H/He ionization cuts.
/// Every child has positive N and support-realizable U/N; raw source N/U
/// is preserved, rather than normalized to a newly rounded quadrature.
fn split_source(cell: &SpectralCell, count: f64, cut_birth: &[f64; 3]) -> Vec<Child> {
    assert!(count.is_finite() && count >= 0.);
    if count == 0. {
        return Vec::new();
    }
    let mut edges = vec![cell.lower_ev];
    for &cut in cut_birth {
        if cut.is_finite() && cut > cell.lower_ev && cut < cell.upper_ev {
            edges.push(cut);
        }
    }
    edges.sort_by(|a, b| a.partial_cmp(b).unwrap_or(Ordering::Equal));
    edges.dedup_by(|a, b| (*a - *b).abs() < 1e-13);
    edges.push(cell.upper_ev);
    if edges.len() == 2 {
        return vec![Child {
            lo: cell.lower_ev,
            hi: cell.upper_ev,
            n: count,
            u: count * cell.energy_ev,
        }];
    }
    let mut children: Vec<Child> = edges
        .windows(2)
        .map(|w| {
            let n = simpson(w[0], w[1], 0);
            let u = simpson(w[0], w[1], 1);
            Child {
                lo: w[0],
                hi: w[1],
                n,
                u,
            }
        })
        .collect();
    let norm: f64 = children.iter().map(|c| c.n).sum();
    assert!(norm.is_finite() && norm > 0.);
    let scale = count / norm;
    let mut largest = 0usize;
    for j in 0..children.len() {
        children[j].n *= scale;
        children[j].u *= scale;
        if children[j].n > children[largest].n {
            largest = j;
        }
    }
    let delta_n = count - children.iter().map(|c| c.n).sum::<f64>();
    children[largest].n += delta_n;
    let delta_u = count * cell.energy_ev - children.iter().map(|c| c.u).sum::<f64>();
    children[largest].u += delta_u;
    for c in &children {
        assert!(c.n > 0. && c.u > 0.);
        let e = c.u / c.n;
        assert!(
            e >= c.lo - 2e-11 && e <= c.hi + 2e-11,
            "invalid child spectral support"
        );
    }
    children
}

#[derive(Clone, Copy, Default)]
struct Totals {
    born_n: f64,
    born_u: f64,
    expected_n: f64,
    expected_u: f64,
    final_u: f64,
    work: f64,
    below_n: [f64; 3],
    below_u: [f64; 3],
    support_violations: usize,
}
/// Actual native MD14 source rate, LRS Bianchi Killing redshift,
/// source-midpoint angular Jacobian and continuous emitted spectra.
fn run_case(q: f64, m: usize, steps: usize) -> Totals {
    assert!(steps >= 1);
    let mut cfg = DriverConfig::baseline();
    cfg.q_ref = q;
    cfg.energy_subdivisions = m;
    cfg.n_mu = 8;
    cfg.end_zbar = 19.998;
    cfg.background_panels = 4096;
    let (driver, state) = Driver::new(cfg).expect("native Driver/new");
    let a0 = state.a;
    let afinal = 1. / 20.998_f64;
    let total_dloga = (afinal / a0).ln();
    let g0 = driver
        .background
        .point_at_scale(a0)
        .unwrap()
        .geometry()
        .unwrap();
    let gf = driver
        .background
        .point_at_scale(afinal)
        .unwrap()
        .geometry()
        .unwrap();
    let mut out = Totals::default();
    for step in 0..steps {
        let ai = a0 * (total_dloga * (step as f64) / (steps as f64)).exp();
        let aj = a0 * (total_dloga * ((step + 1) as f64) / (steps as f64)).exp();
        let am = (ai * aj).sqrt();
        let dt = driver.background.point_at_scale(aj).unwrap().time_s
            - driver.background.point_at_scale(ai).unwrap().time_s;
        let gm = driver
            .background
            .point_at_scale(am)
            .unwrap()
            .geometry()
            .unwrap();
        let rate = driver.source.at_redshift(1. / am - 1.).unwrap().per_h_s;
        let mut rays: Vec<(f64, f64)> = Vec::new();
        for ang in &driver.source.angular_cells {
            let mu = ang.mu;
            let direction = [(1. - mu * mu).sqrt(), 0., mu];
            let ray = CharacteristicRay::new(1., direction, 0.).unwrap();
            let weight = ang.count_fraction * ray.solid_angle_jacobian(&g0, &gm).unwrap();
            let k = CovariantPhoton::from_local(&gm, 1., direction, 1.).unwrap();
            let g = k.energy_at(&gf).unwrap();
            rays.push((weight, g));
        }
        let weight_sum: f64 = rays.iter().map(|x| x.0).sum();
        assert!(weight_sum > 0.);
        for (weight, g) in rays {
            let cuts_birth = CUTS.map(|cut| cut / g);
            for cell in &driver.source.spectral_cells {
                let count = rate * dt * cell.photon_fraction * weight / weight_sum;
                out.expected_n += count;
                out.expected_u += count * cell.energy_ev;
                for child in split_source(cell, count, &cuts_birth) {
                    out.born_n += child.n;
                    out.born_u += child.u;
                    out.final_u += g * child.u;
                    out.work += (1. - g) * child.u;
                    let emean = g * child.u / child.n;
                    for (j, &cut) in CUTS.iter().enumerate() {
                        let low = g * child.lo;
                        let high = g * child.hi;
                        if low < cut - 3e-11 && high > cut + 3e-11 {
                            out.support_violations += 1;
                        }
                        if emean < cut {
                            out.below_n[j] += child.n;
                            out.below_u[j] += g * child.u;
                        }
                    }
                }
            }
        }
    }
    out
}
fn row(q: f64, m: usize, steps: usize, r: Totals) -> String {
    format!("{q:.17e},{m},{steps},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{}",
        r.born_n,r.born_u,r.final_u,r.work,
        r.below_n[0],r.below_n[1],r.below_n[2],
        r.below_u[0],r.below_u[1],r.below_u[2],
        r.expected_n-r.born_n,
        r.expected_u-r.born_u,
        r.support_violations)
}
fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.len() != 3 {
        eprintln!(
            "usage: native_md14_cut <signed-q> <energy-cells-per-segment> <source-time-steps>"
        );
        std::process::exit(2);
    }
    let q: f64 = args[0].parse().expect("q");
    let m: usize = args[1].parse().expect("energy bins");
    let steps: usize = args[2].parse().expect("steps");
    let r = run_case(q, m, steps);
    println!("{}", row(q, m, steps, r));
}
#[cfg(test)]
mod tests {
    use super::*;
    fn source(m: usize) -> Vec<SpectralCell> {
        let mut cfg = DriverConfig::baseline();
        cfg.end_zbar = 19.998;
        cfg.energy_subdivisions = m;
        cfg.background_panels = 2048;
        Driver::new(cfg).unwrap().0.source.spectral_cells
    }
    #[test]
    fn endpoint_full_child() {
        let c = source(4)[0];
        let a = split_source(&c, 1., &[13.6, 24.59, 54.42]);
        assert_eq!(a.len(), 1);
        assert_eq!(a[0].n, 1.);
        assert_eq!(a[0].u, c.energy_ev);
    }
    #[test]
    fn cut_number_energy_and_support() {
        for m in [4, 8, 16, 64] {
            for c in source(m) {
                let cuts = [(c.lower_ev + c.upper_ev) / 2., 24.59, 54.42];
                let kids = split_source(&c, 1e-6, &cuts);
                let n = kids.iter().map(|x| x.n).sum::<f64>();
                let u = kids.iter().map(|x| x.u).sum::<f64>();
                assert!((n - 1e-6).abs() < 5e-21);
                assert!((u - c.energy_ev * 1e-6).abs() < 5e-19);
                for x in kids {
                    assert!(x.n > 0. && x.u / x.n >= x.lo - 2e-11 && x.u / x.n <= x.hi + 2e-11);
                }
            }
        }
    }
    #[test]
    fn actual_native_source_conservation_and_physical_limit() {
        let r = run_case(0., 16, 8);
        assert!(r.born_n > 0. && r.born_u > 0.);
        assert!(r.below_n[0] >= 0. && r.below_n[0] < 0.001 * r.born_n);
        assert!((r.born_u - r.final_u - r.work).abs() < 1e-10 * r.born_u);
        assert_eq!(r.support_violations, 0);
    }
    #[test]
    fn signed_bianchi_positive_and_zero_support_violations() {
        for q in [-0.005, 0., 0.005] {
            let r = run_case(q, 8, 4);
            assert_eq!(r.support_violations, 0);
            assert!(r.born_u.is_finite() && r.final_u > 0.);
            assert!((r.born_u - r.final_u - r.work).abs() < 1e-10 * r.born_u);
            assert!(r.below_n[0] <= r.below_n[1] && r.below_n[1] <= r.below_n[2]);
        }
    }
}
