mod bass_common;
#[path = "../study_controls.rs"]
mod study_controls;
use rei_iso_couple_reference::positive_spectral::SpectralMode as S;
use study_controls::AxisControls;
fn controls() -> AxisControls {
    AxisControls {
        birth_gl: 2,
        opacity: 4,
        spectrum: S::OriginalCellMean,
        cx_rtol: 1e-12,
    }
}
#[test]
fn spectral_axis_does_not_change_birth_axis() {
    let (mut b, mut c, _) = bass_common::fixture("SIGNED_MINUS", 121, 0., false, 8192);
    let mut a = controls();
    a.spectrum = S::SplitPositiveGauss3;
    a.apply(&mut b, &mut c).unwrap();
    assert!(matches!(b.1.spectrum, S::SplitPositiveGauss3));
    assert_eq!(b.1.birth_gauss_nodes, 2);
    assert_eq!(b.1.opacity_substeps, 4);
}
#[test]
fn birth_axis_does_not_change_spectral_axis() {
    let (mut b, mut c, _) = bass_common::fixture("SIGNED_MINUS", 121, 0., false, 8192);
    let mut a = controls();
    a.birth_gl = 4;
    a.apply(&mut b, &mut c).unwrap();
    assert_eq!(b.1.birth_gauss_nodes, 4);
    assert!(matches!(b.1.spectrum, S::OriginalCellMean));
}
#[test]
fn opacity_axis_and_cx_tolerance_are_explicit() {
    let (mut b, mut c, _) = bass_common::fixture("SIGNED_MINUS", 121, 0., false, 8192);
    let mut a = controls();
    a.opacity = 8;
    a.cx_rtol = 1e-14;
    a.apply(&mut b, &mut c).unwrap();
    assert_eq!(b.1.opacity_substeps, 8);
    assert_eq!(c.cx_controls.rtol, 1e-14);
    assert_eq!(c.cx_controls.atol_normalized, 1e-16);
    assert_eq!(c.cx_controls.max_attempts, 20000);
    assert_eq!(c.cx_controls.max_rate_calls, 2500000);
}
#[test]
fn invalid_controls_reject_before_mutation() {
    for a in [
        AxisControls {
            birth_gl: 3,
            ..controls()
        },
        AxisControls {
            opacity: 0,
            ..controls()
        },
        AxisControls {
            cx_rtol: f64::NAN,
            ..controls()
        },
        AxisControls {
            cx_rtol: 0.,
            ..controls()
        },
    ] {
        let (mut b, mut c, _) = bass_common::fixture("SIGNED_MINUS", 121, 0., false, 8192);
        let before = format!("{:?} {:?}", b.1, c.cx_controls);
        assert!(a.apply(&mut b, &mut c).is_err());
        assert_eq!(before, format!("{:?} {:?}", b.1, c.cx_controls));
    }
}
#[test]
fn baseline_control_is_exact_native_identity() {
    let (mut b, mut c, g) = bass_common::fixture("SIGNED_MINUS", 121, 0., false, 8192);
    let initial = b.initial(g, &c, 0.).unwrap();
    let refstep = b.advance(&initial, &c, 2e9).unwrap();
    controls().apply(&mut b, &mut c).unwrap();
    let actual = b.advance(&initial, &c, 2e9).unwrap();
    bass_common::common::bit_parity(&refstep, &actual);
}
#[test]
fn source_and_reaction_switches_unchanged() {
    let (mut b, mut c, _) = bass_common::fixture("SIGNED_MINUS", 121, 0., false, 8192);
    let old = format!("{:?}", b.0.source);
    let source = c.photon_source;
    AxisControls {
        birth_gl: 4,
        opacity: 8,
        spectrum: S::SplitPositiveGauss3,
        cx_rtol: 1e-10,
    }
    .apply(&mut b, &mut c)
    .unwrap();
    assert_eq!(format!("{:?}", b.0.source), old);
    assert_eq!(c.photon_source, source);
    assert!(c.use_photo && c.use_cx && c.use_collisions && c.use_cmb);
}
