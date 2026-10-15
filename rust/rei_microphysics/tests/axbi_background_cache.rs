use rei_microphysics::axbi_background::{
    AxbiBackground, BackgroundFamily, BackgroundPoint, Cosmology,
};
use rei_microphysics::axbi_driver::{Driver, DriverConfig};
fn model(q: f64) -> AxbiBackground {
    AxbiBackground::new(
        Cosmology {
            h0_per_s: 2.2e-18,
            omega_m: 0.3,
            omega_r: 0.00009,
            omega_lambda: 0.69991,
        },
        1.0 / 21.0,
        0.2,
        0.0,
        q,
        BackgroundFamily::PhysicalDensityFixed,
        64,
    )
    .unwrap()
}
fn bits(p: BackgroundPoint) -> [u64; 7] {
    [
        p.a,
        p.b,
        p.time_s,
        p.h_flrw_per_s,
        p.h_per_s,
        p.s_per_s,
        p.sigma,
    ]
    .map(f64::to_bits)
}
#[test]
fn all_fields_endpoints_adjacent_and_original_arithmetic_match() {
    for q in [0.0, -0.01, 0.01] {
        let b = model(q);
        for a in [
            1.0 / 21.0,
            f64::from_bits((1.0f64 / 21.0).to_bits() + 1),
            0.06,
            0.1,
            0.2,
        ] {
            let original = bits(b.point_at_scale_uncached(a).unwrap());
            assert_eq!(original, bits(b.point_at_scale(a).unwrap()));
            assert_eq!(original, bits(b.point_at_scale(a).unwrap()));
        }
    }
    let b = model(0.0);
    let a = 0.1f64;
    b.point_at_scale(a).unwrap();
    b.point_at_scale(f64::from_bits(a.to_bits() + 1)).unwrap();
    let keys = b.point_cache_telemetry().resident_keys;
    assert!(keys.contains(&a.to_bits()));
    assert!(keys.contains(&(a.to_bits() + 1)));
}
#[test]
fn invalid_errors_priority_and_cache_immutability() {
    let b = model(0.0);
    let before = b.point_cache_telemetry().resident_keys;
    for a in [
        f64::NAN,
        f64::INFINITY,
        f64::NEG_INFINITY,
        0.0,
        -0.0,
        -1.0,
        0.01,
        0.3,
    ] {
        assert_eq!(
            format!("{:?}", b.point_at_scale(a).unwrap_err()),
            format!("{:?}", b.point_at_scale_uncached(a).unwrap_err())
        );
    }
    assert_eq!(before, b.point_cache_telemetry().resident_keys);
}
#[test]
fn warming_bypass_clones_independence_and_eviction_are_explicit() {
    let b = model(0.0);
    let warm = b.point_cache_telemetry();
    assert_eq!((warm.calls, warm.misses, warm.actual_uncached), (1, 1, 1));
    assert_eq!(warm.resident_keys.len(), 1);
    let clone = b.clone();
    clone.point_at_scale(0.1).unwrap();
    assert_eq!(clone.point_cache_telemetry(), b.point_cache_telemetry());
    let keys = b.point_cache_telemetry().resident_keys;
    b.set_point_cache_enabled(false);
    let before = b.point_cache_telemetry();
    b.point_at_scale(0.11).unwrap();
    let after = b.point_cache_telemetry();
    assert_eq!(after.resident_keys, keys);
    assert_eq!(after.hits, before.hits);
    assert_eq!(after.misses, before.misses);
    assert_eq!(after.actual_uncached, before.actual_uncached + 1);
    b.set_point_cache_enabled(true);
    for i in 0..80 {
        b.point_at_scale(0.05 + (i as f64) * 0.001).unwrap();
    }
    assert_eq!(b.point_cache_telemetry().resident_keys.len(), 32);
    assert!(b.point_cache_telemetry().evictions > 0);
    let other = model(0.01);
    assert_eq!(other.point_cache_telemetry().resident_keys.len(), 1);
    assert_ne!(
        bits(other.point_at_scale(0.1).unwrap()),
        bits(b.point_at_scale(0.1).unwrap())
    );
}
#[test]
fn concurrent_duplicates_preserve_exact_physics_and_bounded_ring() {
    let b = model(-0.01);
    std::thread::scope(|s| {
        for _ in 0..8 {
            let c = b.clone();
            s.spawn(move || {
                for i in 0..64 {
                    let a = 0.05 + (i % 40) as f64 * 0.001;
                    assert_eq!(
                        bits(c.point_at_scale(a).unwrap()),
                        bits(c.point_at_scale_uncached(a).unwrap())
                    );
                }
            });
        }
    });
    assert!(b.point_cache_telemetry().resident_keys.len() <= 32);
}
#[test]
fn production_startup_and_adaptive_bits_match_bypass_and_config_is_not_model_key() {
    let mut cfg = DriverConfig::baseline();
    cfg.end_zbar = 19.8;
    cfg.background_panels = 64;
    cfg.inactive_hi_split = true;
    cfg.transport_threads = 8;
    let (mut cached, mut a) = Driver::new(cfg.clone()).unwrap();
    let (uncached, mut b) = Driver::new(cfg).unwrap();
    uncached.background.set_point_cache_enabled(false);
    assert_eq!(format!("{a:?}"), format!("{b:?}"));
    let refpoint = bits(cached.background.point_at_scale(a.a).unwrap());
    cached.config.q_ref = 0.01;
    assert_eq!(
        bits(cached.background.point_at_scale(a.a).unwrap()),
        refpoint
    );
    cached.config.q_ref = 0.0;
    for _ in 0..24 {
        assert_eq!(
            cached.adaptive_step(&mut a).unwrap(),
            uncached.adaptive_step(&mut b).unwrap()
        );
        assert_eq!(format!("{a:?}"), format!("{b:?}"));
        assert_eq!(
            bits(cached.background.point_at_scale(a.a).unwrap()),
            bits(uncached.background.point_at_scale_uncached(b.a).unwrap())
        );
        if a.accepted >= 3 {
            break;
        }
    }
    assert_eq!(a.accepted, 3);
    assert_eq!(
        cached.residuals(&a).unwrap(),
        uncached.residuals(&b).unwrap()
    );
    cached.background = model(0.01);
    assert_eq!(
        cached
            .background
            .point_cache_telemetry()
            .resident_keys
            .len(),
        1
    );
    assert_eq!(
        bits(cached.background.point_at_scale(0.1).unwrap()),
        bits(model(0.01).point_at_scale_uncached(0.1).unwrap())
    );
}
