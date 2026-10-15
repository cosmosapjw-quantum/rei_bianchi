//! C9: source-locked proper-time clock, real q family and MP80 90 exact-f64 inputs.
//! An isolated validation of the new incremental time API, not scientific
//! admission for a resumed historical full AX08 checkpoint.
use rei_microphysics::axbi_background::{AxbiBackground, BackgroundFamily, Cosmology};

const AR: f64 = 1.0 / 21.0;
const AE: f64 = 0.2;
fn cosmo() -> Cosmology {
    Cosmology {
        h0_per_s: 2.1842852410855026e-18,
        omega_m: 0.315,
        omega_r: 9.2e-5,
        omega_lambda: 0.6849080000000001,
    }
}
fn make(q: f64, family: BackgroundFamily) -> AxbiBackground {
    AxbiBackground::new(cosmo(), AR, AE, 0.0, q, family, 64).unwrap()
}
#[test]
fn all_90_original_mp80_float_endpoint_intervals() {
    let raw = include_str!("fixtures/axbi_c9_clock_mp80_90.csv");
    let mut n = 0usize;
    let mut near = 0usize;
    let mut max_clock = 0.0_f64;
    let mut max_b = 0.0_f64;
    let cases = [
        (0.0, BackgroundFamily::PhysicalDensityFixed),
        (0.005, BackgroundFamily::PhysicalDensityFixed),
        (-0.005, BackgroundFamily::PhysicalDensityFixed),
        (0.01, BackgroundFamily::PhysicalDensityFixed),
        (-0.01, BackgroundFamily::PhysicalDensityFixed),
        (0.01, BackgroundFamily::SameHDiagnostic),
    ];
    let backgrounds: Vec<AxbiBackground> = cases.iter().map(|&(q, f)| make(q, f)).collect();
    for line in raw.lines().skip(1) {
        let f: Vec<&str> = line.split(',').collect();
        assert_eq!(f.len(), 6, "fixture schema drift");
        let family = match f[0] {
            "PhysicalDensityFixed" => BackgroundFamily::PhysicalDensityFixed,
            "SameHDiagnostic" => BackgroundFamily::SameHDiagnostic,
            _ => panic!("unknown family"),
        };
        let q: f64 = f[1].parse().unwrap();
        let a0: f64 = f[2].parse().unwrap();
        let a1: f64 = f[3].parse().unwrap();
        let dt80: f64 = f[4].parse().unwrap();
        let db80: f64 = f[5].parse().unwrap();
        let bg = &backgrounds[cases
            .iter()
            .position(|&(x, y)| x == q && y == family)
            .unwrap()];
        let (dt, db) = bg.local_increments(a0, a1).unwrap();
        let t = bg.proper_time_increment(a0, a1).unwrap();
        assert!(dt > 0.0 && dt.is_finite());
        assert_eq!(dt, t);
        let err_t = (dt / dt80 - 1.0).abs();
        let err_b = if db80 == 0.0 {
            assert_eq!(db, 0.0);
            0.0
        } else {
            (db / db80 - 1.0).abs()
        };
        max_clock = max_clock.max(err_t);
        max_b = max_b.max(err_b);
        assert!(err_t < 4e-13, "case {n} q={q} dt drift {err_t:e}");
        assert!(err_b < 4e-13, "case {n} q={q} db drift {err_b:e}");
        if (a1 - a0) / a0 < 1e-14 {
            near += 1;
        }
        n += 1;
    }
    assert_eq!(n, 90);
    assert_eq!(near, 18);
    println!("C9 native GL4 MP80 intervals n={n}, nextfloat={near}, max_dt_rel={max_clock:e}, max_db_rel={max_b:e}");
}
#[test]
fn one_ulp_short_interval_never_subtracts_cumulative_time() {
    let b = make(0.01, BackgroundFamily::PhysicalDensityFixed);
    let a0 = 0.1_f64;
    let a1 = f64::from_bits(a0.to_bits() + 1);
    let dt = b.proper_time_increment(a0, a1).unwrap();
    let naive = b.point_at_scale(a1).unwrap().time_s - b.point_at_scale(a0).unwrap().time_s;
    assert!(dt > 3.5 && dt < 3.6, "physical dt:{dt}");
    assert!(
        naive / dt - 1.0 > 0.10,
        "original must reproduce historic cancellation"
    );
    println!(
        "C9 native nextfloat a=.1 dt={dt}, naive={naive}, ratio={}",
        naive / dt
    );
}
#[test]
fn signed_parity_zero_shear_and_same_h_counterfactual() {
    let pos = make(0.01, BackgroundFamily::PhysicalDensityFixed);
    let neg = make(-0.01, BackgroundFamily::PhysicalDensityFixed);
    let flrw = make(0.0, BackgroundFamily::PhysicalDensityFixed);
    let same = make(0.01, BackgroundFamily::SameHDiagnostic);
    for &(a, b) in &[(0.05, 0.12), (0.1, 0.10000001), (0.1, 0.2)] {
        let (tp, bp) = pos.local_increments(a, b).unwrap();
        let (tm, bm) = neg.local_increments(a, b).unwrap();
        assert_eq!(tp, tm);
        assert_eq!(bp, -bm);
        assert_eq!(flrw.local_increments(a, b).unwrap().1, 0.);
        assert!(same.local_increments(a, b).unwrap().0 > tp);
    }
}
#[test]
fn full_span_agrees_native_original_simpson_and_positive() {
    for &(q, flag) in &[
        (0.0, false),
        (0.005, false),
        (-0.005, false),
        (0.01, false),
        (-0.01, false),
        (0.01, true),
    ] {
        let family = if flag {
            BackgroundFamily::SameHDiagnostic
        } else {
            BackgroundFamily::PhysicalDensityFixed
        };
        let old = AxbiBackground::new(cosmo(), AR, AE, 0.0, q, family, 4096).unwrap();
        let (t, b) = old.local_increments(AR, AE).unwrap();
        let p = old.point_at_scale(AE).unwrap();
        assert!((t / p.time_s - 1.0).abs() < 1e-10);
        if q != 0.0 {
            assert!((b / p.b - 1.0).abs() < 1e-10);
        } else {
            assert_eq!(b, 0.)
        }
    }
}
#[test]
fn illegal_endpoint_and_physical_ranges_fail_closed() {
    let bg = make(0.01, BackgroundFamily::PhysicalDensityFixed);
    for &(a, b) in &[
        (0.1, 0.09),
        (0.02, 0.1),
        (0.1, 0.3),
        (f64::NAN, 0.1),
        (0.1, f64::INFINITY),
        (0.0, 0.1),
    ] {
        assert!(bg.local_increments(a, b).is_err());
    }
    assert_eq!(bg.local_increments(0.1, 0.1).unwrap(), (0.0, 0.0));
}

#[test]
fn actual_run_rejects_prior_clock_source_before_checkpoint_read() {
    use rei_microphysics::axbi_driver::run;
    use std::fs;
    let config = "end_zbar=19.8\nbackground_panels=64\n";
    let dir = std::env::temp_dir().join(format!("axbi_c9_old_source_guard_{}", std::process::id()));
    assert!(
        !dir.exists(),
        "do not trample a prior scientific test directory"
    );
    fs::create_dir(&dir).unwrap();
    fs::write(dir.join("config.cfg"), config).unwrap();
    fs::write(
        dir.join("source_identity.txt"),
        "PREVIOUS_COMPILED_SOURCE_BYTES",
    )
    .unwrap();
    // Deliberately DO NOT make a checkpoint file. A correctly guarded run()
    // must refuse source mismatch *before* attempting any read_checkpoint.
    let failure = run(config, &dir, "ZERO", true).unwrap_err();
    assert!(
        format!("{failure:?}").contains("AXBI_RESUME_IDENTITY"),
        "unexpected checkpoint/source admission error: {failure:?}"
    );
    assert!(!dir.join("checkpoint.txt").exists());
    fs::remove_dir_all(dir).unwrap();
}
