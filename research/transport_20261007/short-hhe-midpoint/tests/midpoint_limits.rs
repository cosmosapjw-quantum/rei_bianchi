//! Mathematical coefficients are test doubles, using production affine staging,
//! residual assembly, photo conversion, and the same unchanged characteristic kernel.
use short_hhe_control::{coupled, material, radiation, v2};
fn exact(x: f64, f: f64, k: f64, t: f64) -> f64 {
    let u = 1. - x;
    let d = u - f;
    let e = (-k * d * t).exp();
    x + f - d * f * e / (u - f * e)
}
fn trial(x: f64, f: f64, q: f64, k: f64, h: f64, active: f64, z: f64) -> (f64, v2::Owners) {
    let ys = radiation::affine([x, 0., 0., 1.], [z, 0., 0., 1.], active / (2. * h));
    let o = v2::kernel(f, q, [k * (1. - ys[0]), 0., 0.], active, 80.).unwrap();
    let d = material::photo_delta(o.an, o.be, 0.08);
    let r =
        coupled::assemble_residual([x, 0., 0., 1.], [z, 0., 0., 1.], d, [0.; 3], 0., h).unwrap()[0];
    (r, o)
}
fn step(x: f64, f: f64, q: f64, k: f64, h: f64, active: f64) -> Result<(f64, v2::Owners), String> {
    let (mut lo, mut hi) = (x, 1.);
    if trial(x, f, q, k, h, active, hi).0 < 0. {
        return Err("no physical endpoint root".into());
    }
    for _ in 0..55 {
        let m = (lo + hi) * 0.5;
        if trial(x, f, q, k, h, active, m).0 > 0. {
            hi = m
        } else {
            lo = m
        }
    }
    let z = (lo + hi) * 0.5;
    Ok((z, trial(x, f, q, k, h, active, z).1))
}
fn close(a: f64, b: f64) {
    assert!(
        (a - b).abs() < 2e-12 * a.abs().max(b.abs()).max(1e-280),
        "{a:e} {b:e}"
    );
}
#[test]
fn coupled_feedback_quadratic_counts_energy_and_born_photons() {
    let (x, f, q, k) = (0.2, 0.4, 0.1, 3.);
    let v = k * (1. - x) * f;
    let g = q - v;
    let c = -k * v * f + k * (1. - x) * g;
    let mut coeff = vec![];
    for h in [0.02, 0.01, 0.005, 0.0025] {
        let (z, o) = step(x, f, q, k, h, h).unwrap();
        close(z + o.n, x + f + q * h);
        coeff.push((z - x - h * v) / (h * h));
        let eb = o.be[0] / (v2::EPS * 80.);
        let ec = (eb - h * v) / (h * h);
        println!(
            "COUPLED h={h:e} x_quadratic={:.17e} energy_quadratic={ec:.17e}",
            coeff.last().unwrap()
        );
        if h == 0.0025 {
            assert!((coeff.last().unwrap() - c / 2.).abs() < 0.015);
            assert!((ec - (c - v) / 2.).abs() < 0.02);
            let ym = (x + z) / 2.;
            let naive = h * k * (1. - ym) * f;
            assert!((naive - o.an[0]).abs() > 2e-12 * o.an[0]);
            for wrong in [x, z] {
                let mutant = v2::kernel(f, q, [k * (1. - wrong), 0., 0.], h, 80.).unwrap();
                assert!((mutant.an[0] - o.an[0]).abs() > 2e-12 * o.an[0]);
            }
        }
    }
    let h = 0.0001;
    let (_, born) = step(x, 0., q, k, h, h).unwrap();
    assert!((born.an[0] / h.powi(2) - k * (1. - x) * q / 2.).abs() < 1e-4);
    assert!(born.an[0] > 0.);
    let o = v2::kernel(0.4, 0.1, [2.4, 0., 0.], 0.02, 80.).unwrap();
    let mutant = v2::EPS * 80. * (-0.01f64).exp() * o.an[0];
    let scale = o.qe + v2::EPS * 80. * 0.4;
    assert!(
        (o.u + mutant + o.red - scale).abs() > 2e-12 * scale,
        "midpoint-only energy owner escaped"
    );
}
#[test]
fn smooth_qzero_local_order_3() {
    let mut e = vec![];
    for h in [0.02, 0.01, 0.005, 0.0025] {
        let (z, _) = step(0.2, 0.4, 0., 3., h, h).unwrap();
        e.push((z - exact(0.2, 0.4, 3., h)).abs());
        println!("SMOOTH h={h:e} error={:.17e}", e.last().unwrap());
    }
    let p = (e[2] / e[3]).log2();
    assert!(p > 2.8 && p < 3.2, "p={p}");
}
#[test]
fn coupled_cutoff_local2_fixed_phase_global2_limitation() {
    let (x, f, k, a) = (0.2, 0.4, 3., 1. / 3.);
    let coefficient = 0.5 * k * f * (k * (1. - x) * f) * a * a * (1. - a);
    let mut e = vec![];
    for h in [0.02, 0.01, 0.005, 0.0025] {
        let (z, o) = step(x, f, 0., k, h, a * h).unwrap();
        close(z + o.n, x + f);
        let error = z - exact(x, f, k, a * h);
        e.push(error);
        println!(
            "EVENT_LOCAL h={h:e} error={error:.17e} coefficient={:.17e}",
            error / (h * h)
        );
    }
    assert!((e[3] / 0.0025f64.powi(2) / coefficient - 1.).abs() < 0.04);
    let p = (e[2] / e[3]).log2();
    assert!(p > 1.8 && p < 2.2);
    let t = 0.1;
    let event = t / 3.;
    let mut errors = vec![];
    for m in [1, 4, 16, 64] {
        let h = t / m as f64;
        let (mut z, mut stock) = (x, f);
        for i in 0..m {
            let left = i as f64 * h;
            let active = (event - left).max(0.).min(h);
            if active > 0. {
                let (next, o) = step(z, stock, 0., k, h, active).unwrap();
                z = next;
                stock = o.n;
            }
        }
        let er = (z - exact(x, f, k, event)).abs();
        errors.push(er);
        println!("EVENT_GLOBAL m={m} error={er:.17e}");
    }
    let p = (errors[2] / errors[3]).ln() / 4f64.ln();
    assert!(p > 1.8 && p < 2.2, "p={p}");
}
#[test]
fn stiff_photo_no_root_and_midpoint_sink_reject() {
    assert!(step(0.2, 1.6, 0., 3., 1., 1.)
        .unwrap_err()
        .contains("no physical endpoint root"));
    for kh in [0.1, 3., 100.] {
        let endpoint = (1. - kh / 2.) / (1. + kh / 2.);
        let res = coupled::assemble_residual(
            [1., 0., 0., 1.],
            [endpoint, 0., 0., 1.],
            [0.; 4],
            [-(1. + endpoint) * 0.5, 0., 0.],
            0.,
            kh,
        )
        .unwrap();
        assert!(res[0].abs() < 1e-14);
        if kh > 2. {
            assert!(material::gas([endpoint, 0., 0., 1.]).is_err());
        } else {
            assert!((endpoint - (-kh).exp()).abs() < 1e-4);
        }
    }
}
#[test]
fn jump_diagnostic_owner_is_only_first_order() {
    let alpha: f64 = 1. / 3.;
    let mut last = 0.;
    for h in [0.02, 0.01, 0.005, 0.0025] {
        let candidate = if alpha > 0.5 { h } else { 0. };
        let error = (candidate - alpha * h).abs();
        if last > 0. {
            close(last / error, 2.);
        }
        last = error;
        println!("JUMP h={h:e} error={error:e}");
    }
}
#[test]
fn sourced_coupled_local_error_uses_independent_high_order_series() {
    let (x, f, q, k) = (0.2, 0.4, 0.1, 3.);
    let mut a = [0.; 12];
    a[0] = x;
    for n in 0..11 {
        let mut sum = 0.;
        for j in 0..=n {
            let u = if j == 0 { 1. - a[0] } else { -a[j] };
            let l = n - j;
            let photon = if l == 0 {
                x + f - a[0]
            } else if l == 1 {
                q - a[1]
            } else {
                -a[l]
            };
            sum += u * photon;
        }
        a[n + 1] = k * sum / (n + 1) as f64;
    }
    let mut errors = vec![];
    for h in [0.02f64, 0.01, 0.005, 0.0025] {
        let oracle = a.iter().rev().fold(0., |s, c| s * h + c);
        let (z, _) = step(x, f, q, k, h, h).unwrap();
        let e = (z - oracle).abs();
        errors.push(e);
        println!("SOURCED_LOCAL h={h:e} error={e:.17e}");
    }
    let p = (errors[2] / errors[3]).log2();
    assert!(p > 2.8 && p < 3.2, "p={p}");
}
