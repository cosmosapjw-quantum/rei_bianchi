#[path = "../examples/long_support/mod.rs"]
mod support;
use rei_iso_couple_reference::positive_spectral::SpectralMode;
#[test]
fn spectrum_does_not_choose_birth_nodes() {
    for q in [2, 4] {
        for split in [false, true] {
            let r = support::controls(split, q, 4).unwrap();
            assert_eq!(r.birth_gauss_nodes, q);
            assert_eq!(
                r.spectrum,
                if split {
                    SpectralMode::SplitPositiveGauss3
                } else {
                    SpectralMode::OriginalCellMean
                }
            );
        }
    }
}
#[test]
fn opacity_is_an_independent_axis() {
    for m in [1, 2, 4, 8, 16, 32] {
        assert_eq!(support::controls(false, 4, m).unwrap().opacity_substeps, m);
    }
}
#[test]
fn invalid_birth_rule_is_rejected() {
    assert!(support::controls(false, 3, 4).is_err());
}
#[test]
fn invalid_opacity_partition_is_rejected() {
    assert!(support::controls(true, 4, 3).is_err());
}
