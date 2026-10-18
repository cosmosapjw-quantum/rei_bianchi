use rei_microphysics::{igm_rates::igm_rates, AtomicProvider, RawProcess, RecombinationCase};
#[test]
fn source_low_temperature_branches_are_explicit() {
    let r = igm_rates(1.0).unwrap();
    assert_eq!(r.ci_cm3_s, [1e-20; 3]);
    assert!(r.rr_cm3_s.iter().all(|x| x.is_finite() && *x > 0.0));
    assert_eq!(r.dr_cm3_s, 0.0);
    assert_eq!(r.dr_cooling_erg_cm3_s, 0.0);
    assert!(r.dr_raw_cooling_erg_cm3_s > 0.0);
    assert_eq!(
        r.diagnostics.dr_excluded_erg_cm3_s,
        r.dr_raw_cooling_erg_cm3_s
    );
    assert!(r.diagnostics.ce_cap_erg.iter().all(|x| *x > 0.0));
    assert!(igm_rates(9284.0).unwrap().diagnostics.dr_low_branch);
    assert!(igm_rates(9284.000001).unwrap().dr_cm3_s > 0.0);
}
#[test]
fn temperature_admission_is_separate_and_strict() {
    for t in [0.999999, 1e6 + 1.0, f64::NAN, f64::INFINITY, -1.0] {
        assert!(igm_rates(t).is_err());
    }
    for t in [1.0, 99.0, 100.0, 1e6] {
        assert!(igm_rates(t).is_ok());
    }
    assert!(AtomicProvider::reference()
        .raw_coefficient(RawProcess::K1, 99.0, RecombinationCase::A)
        .is_err());
}
#[test]
fn overlapping_source_values_match_existing_raw_provider() {
    let p = AtomicProvider::reference();
    for t in [100.0, 5500.0, 5500.000001, 9284.0, 9284.000001, 3e4, 1e6] {
        let r = igm_rates(t).unwrap();
        let pairs = [
            (RawProcess::K1, r.ci_cm3_s[0]),
            (RawProcess::K3, r.ci_cm3_s[1]),
            (RawProcess::K5, r.ci_cm3_s[2]),
            (RawProcess::K2, r.rr_cm3_s[0]),
            (RawProcess::K4, r.rr_cm3_s[1] + r.dr_cm3_s),
            (RawProcess::K6, r.rr_cm3_s[2]),
            (RawProcess::CeHeI, r.ce_erg[1]),
            (RawProcess::ReHeII2, r.dr_raw_cooling_erg_cm3_s),
        ];
        for (k, v) in pairs {
            let x = p.raw_coefficient(k, t, RecombinationCase::A).unwrap().value;
            assert!((v - x).abs() <= 2e-13 * x, "{k:?} {t} {v} {x}");
        }
    }
}
#[test]
fn independent_original_c_parity_all_selected_channels() {
    let csv = include_str!("data/igm_grackle/grackle_literal_reference.csv");
    let mut rows = 0;
    for line in csv.lines().skip(1) {
        let a: Vec<f64> = line.split(',').map(|x| x.parse().unwrap()).collect();
        let t = a[0];
        let r = igm_rates(t).unwrap();
        let values = [
            r.ci_cm3_s[0],
            r.ci_cm3_s[1],
            r.ci_cm3_s[2],
            r.rr_cm3_s[0],
            r.rr_cm3_s[1],
            r.rr_cm3_s[2],
            r.dr_cm3_s,
            r.ce_erg[0],
            r.ce_erg[1],
            r.ce_erg[2],
            r.rr_cooling_erg_cm3_s[0],
            r.rr_cooling_erg_cm3_s[1],
            r.rr_cooling_erg_cm3_s[2],
            r.dr_raw_cooling_erg_cm3_s,
            r.freefree_erg_cm3_s,
            r.rr_cm3_s[1] + r.dr_cm3_s,
            r.dr_cooling_erg_cm3_s,
        ];
        for (i, (&v, &expected)) in values.iter().zip(a[1..].iter()).enumerate() {
            if expected == 0.0 {
                assert_eq!(v, 0.0)
            } else {
                assert!(
                    (v - expected).abs() / expected <= 3e-13,
                    "T={t}, col={i}, {v:e} != {expected:e}"
                );
            }
        }
        rows += 1;
    }
    assert_eq!(rows, 96);
}
