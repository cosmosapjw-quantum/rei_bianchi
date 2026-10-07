#[path = "../src/panel.rs"]
mod panel;
use panel::{Family, Panel};
fn p(family: Family) -> Panel {
    Panel {
        l: 0.0,
        r: 1.0,
        beta: 0.0,
        family,
        ln_n: -1000.0,
    }
}
#[test]
fn uniform_half_preserves_moments() {
    let v = p(Family::Ordinary).restrict(0.0, 0.5).unwrap().unwrap();
    assert!((v.ln_fraction + 2.0_f64.ln()).abs() < 1e-13);
    assert!(v.quadrature_node().is_ok());
    assert!((v.mean_exp_eta - 2.0 * (0.5_f64.exp() - 1.0)).abs() < 1e-13);
}
#[test]
fn front_restriction_is_not_retapered() {
    let v = p(Family::RightFront).restrict(0.0, 0.5).unwrap().unwrap();
    assert!((v.ln_fraction - 0.75_f64.ln()).abs() < 1e-13);
    // Integral exp(x)*(1-x) dx = (2-x)exp(x).
    let expected = (1.5 * 0.5_f64.exp() - 2.0) / 0.375;
    assert!((v.mean_exp_eta - expected).abs() < 1e-13);
}
#[test]
fn tail_amplitude_does_not_change_shape() {
    let a = p(Family::RightFront);
    let mut b = a;
    b.ln_n = 500.0;
    let x = a.restrict(0.2, 0.9).unwrap().unwrap();
    let y = b.restrict(0.2, 0.9).unwrap().unwrap();
    assert_eq!(x.normalized_mean.to_bits(), y.normalized_mean.to_bits());
    assert_eq!(x.mean_eta.to_bits(), y.mean_eta.to_bits());
    assert!(x.ln_n < -1000.0 && y.ln_n < 500.0);
}
#[test]
fn empty_intersection_is_exact() {
    assert!(p(Family::RightFront).restrict(1.0, 2.0).unwrap().is_none());
    assert!(p(Family::Ordinary).restrict(0.5, 0.5).unwrap().is_none());
}
#[test]
fn split_moments_without_residual_repair() {
    for family in [Family::Ordinary, Family::RightFront] {
        for beta in [-128.0, -1.0, 0.0, 128.0] {
            let a = Panel {
                beta,
                ln_n: 0.0,
                ..p(family)
            };
            let whole = a.restrict(0.0, 1.0).unwrap().unwrap();
            let mut n = 0.0;
            let mut m = 0.0;
            for i in 0..8 {
                let v = a
                    .restrict(i as f64 / 8.0, (i + 1) as f64 / 8.0)
                    .unwrap()
                    .unwrap();
                n += v.ln_fraction.exp();
                m += v.ln_fraction.exp() * v.mean_exp_eta;
            }
            assert!((n - 1.0).abs() < 3e-13, "{family:?} {beta} {n}");
            assert!(
                (m - whole.mean_exp_eta).abs() < 3e-13,
                "{family:?} {beta} {m}"
            );
        }
    }
}
#[test]
fn narrow_sliver_and_reversed_domain() {
    let a = p(Family::RightFront);
    let lo = f64::from_bits(1.0_f64.to_bits() - 1);
    let v = a.restrict(lo, 1.0).unwrap().unwrap();
    assert!(v.ln_fraction.is_finite());
    assert!((v.normalized_mean - 1.0 / 3.0).abs() < 5e-13);
    assert!(v.quadrature_node().is_err());
    assert!(v.panels <= 128 && v.convergence_error <= 2e-14);
    assert!(a.restrict(1.0, 0.0).is_err());
}
#[test]
fn invalid_parent_is_rejected() {
    for a in [
        Panel {
            ln_n: f64::NEG_INFINITY,
            ..p(Family::Ordinary)
        },
        Panel {
            beta: 129.0,
            ..p(Family::Ordinary)
        },
        Panel {
            r: 1e-8,
            ..p(Family::Ordinary)
        },
        Panel {
            l: -33.0,
            ..p(Family::Ordinary)
        },
    ] {
        assert!(a.restrict(0.0, 1.0).is_err());
    }
}

#[test]
fn huge_log_preserves_restriction_correction() {
    let a = Panel {
        ln_n: -1e12,
        ..p(Family::Ordinary)
    };
    let v = a.restrict(0.0, 0.5).unwrap().unwrap();
    let (hi, lo) = v.log_amplitude_parts();
    // The rounded high component alone loses ~3e-5 in the log correction.
    assert!(((hi - a.ln_n) + 2.0_f64.ln()).abs() > 1e-6);
    assert!(((hi - a.ln_n) + lo + 2.0_f64.ln()).abs() < 1e-15);
}

#[test]
fn subnormal_geometry_rejects_before_quantized_shape() {
    let q = f64::from_bits(1);
    let a = Panel {
        l: -1.0,
        r: 0.0,
        beta: 0.0,
        family: Family::RightFront,
        ln_n: 0.0,
    };
    // A positive physical piece is not empty, but its f64 geometric arithmetic
    // is unsupported: expm1(d*t)/expm1(d) would be a quantized step.
    assert!(a.restrict(-2.0 * q, -q).is_err());
}
