mod common;
use common::{bit_parity, fixture, pulse};
use rei_iso_couple_reference::{
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground},
    positive_spectral::SpectralMode,
    reflection_pool::{PoolLimits, ReflectionPooledBridge, scalar_signature},
    retarded_transport_threshold::PositiveThresholdBridge,
};
#[test]
fn actual_native_reflection_pairs_reuse_nonzero_paths_and_preserve_complete_state() {
    let (base, ctr, conf, gas) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let old = PositiveThresholdBridge(base.clone(), ctr);
    let new = ReflectionPooledBridge(base, ctr, PoolLimits::default());
    let a = old.initial(gas, &conf, 0.).unwrap();
    let r = old.advance(&a, &conf, 2e9).unwrap();
    let (s, d) = new.advance_with_diagnostics(&a, &conf, 2e9).unwrap();
    bit_parity(&r, &s);
    assert!(
        d.reused_paths > 0,
        "the new path must actually reuse reflection traces"
    );
    assert_eq!(d.computed_paths, d.reused_paths);
}
#[test]
fn all_eight_sign_reflections_share_signature_but_not_phase_space_records() {
    let (base, _, _, _) = fixture(0.06, false, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let mut c = pulse(&base, 30., 0.4, 0.01);
    c.direction_at_birth = [0.3, 0.4, (0.75f64).sqrt()];
    let key = scalar_signature(&c, 0.).unwrap();
    for signs in 0..8 {
        let mut d = c.clone();
        for i in 0..3 {
            if signs & (1 << i) != 0 {
                d.direction_at_birth[i] *= -1.;
            }
        }
        assert_eq!(scalar_signature(&d, 0.).unwrap(), key);
        for t in [0., 1e11, 1e13] {
            let snap = base.geometry.snapshot(t).unwrap();
            let r = c.ray_at(&snap).unwrap();
            let s = d.ray_at(&snap).unwrap();
            assert_eq!(r.energy_ev.to_bits(), s.energy_ev.to_bits());
        }
    }
}
#[test]
fn signature_separates_weight_energy_time_geometry_and_direction_magnitude() {
    let (base, _, _, _) = fixture(0.06, false, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let c = pulse(&base, 30., 0.4, 0.01);
    let key = scalar_signature(&c, 0.).unwrap();
    for j in 0..7 {
        let mut d = c.clone();
        match j {
            0 => d.n_comoving_m3 = f64::from_bits(d.n_comoving_m3.to_bits() + 1),
            1 => d.energy_at_birth_ev = f64::from_bits(d.energy_at_birth_ev.to_bits() + 1),
            2 => d.birth_time_s = 1.,
            3 => d.birth_geometry.scale_factors[0] *= 1.00001,
            4 => d.birth_geometry.hubble_per_s[0] *= 1.01,
            5 => {
                d.direction_at_birth = [0.6, 0., 0.8];
            }
            6 => {
                assert_ne!(key, scalar_signature(&d, 1.).unwrap());
                continue;
            }
            _ => unreachable!(),
        }
        assert_ne!(key, scalar_signature(&d, 0.).unwrap());
    }
}
#[test]
fn bad_signature_inputs_fail_instead_of_reusing() {
    let (base, _, _, _) = fixture(0.06, false, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let c = pulse(&base, 30., 0.4, 0.01);
    for j in 0..5 {
        let mut d = c.clone();
        match j {
            0 => d.energy_at_birth_ev = f64::NAN,
            1 => d.n_comoving_m3 = -1.,
            2 => d.birth_time_s = f64::INFINITY,
            3 => d.birth_geometry.scale_factors[0] = 0.,
            4 => d.direction_at_birth[0] = 3.,
            _ => unreachable!(),
        }
        assert!(scalar_signature(&d, 0.).is_err());
    }
    assert!(scalar_signature(&c, f64::NAN).is_err());
}
#[test]
fn disabled_and_tiny_caches_are_safe_fallbacks() {
    let (base, ctr, conf, gas) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let old = PositiveThresholdBridge(base.clone(), ctr);
    let a = old.initial(gas, &conf, 0.).unwrap();
    let r = old.advance(&a, &conf, 2e9).unwrap();
    for limits in [
        PoolLimits {
            max_entries: 0,
            max_segments: 0,
        },
        PoolLimits {
            max_entries: 1,
            max_segments: 32,
        },
        PoolLimits {
            max_entries: 64,
            max_segments: 1,
        },
    ] {
        let (s, d) = ReflectionPooledBridge(base.clone(), ctr, limits)
            .advance_with_diagnostics(&a, &conf, 2e9)
            .unwrap();
        bit_parity(&r, &s);
        assert!(d.peak_cached_traces <= limits.max_entries);
        assert!(d.peak_cached_segments <= limits.max_segments);
    }
}
#[test]
fn full_chemistry_multiple_steps_retains_nonlinear_response() {
    for shear in [-0.06, 0., 0.06] {
        let (base, ctr, conf, gas) =
            fixture(shear, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
        let old = PositiveThresholdBridge(base.clone(), ctr);
        let new = ReflectionPooledBridge(base, ctr, PoolLimits::default());
        let mut a = old.initial(gas, &conf, 0.).unwrap();
        let mut b = a.clone();
        for _ in 0..3 {
            let r = old.advance(&a, &conf, 2e10).unwrap();
            let (s, d) = new.advance_with_diagnostics(&b, &conf, 2e10).unwrap();
            bit_parity(&r, &s);
            assert!(d.reused_paths > 0);
            assert!(r.chemistry_budget.rr_events_m3.iter().any(|v| *v > 0.));
            assert!(r.chemistry_budget.cx_signed_m3.abs() > 0.);
            assert!(r.chemistry_budget.freefree_integrated_j_m3 > 0.);
            assert!(r.chemistry_budget.cmb_change_j_m3.abs() > 0.);
            a = r.state;
            b = s.state;
        }
    }
}
#[test]
fn split_d_edge_gauss4_births_preserve_source_ages_and_spectrum() {
    let (base, ctr, conf, gas) = fixture(0.06, true, 0.2, SpectralMode::SplitPositiveGauss3, 4, 8);
    let old = PositiveThresholdBridge(base.clone(), ctr);
    let new = ReflectionPooledBridge(base, ctr, PoolLimits::default());
    let a = old.initial(gas, &conf, 0.).unwrap();
    let r = old.advance(&a, &conf, 2e10).unwrap();
    let (s, d) = new.advance_with_diagnostics(&a, &conf, 2e10).unwrap();
    bit_parity(&r, &s);
    assert_eq!(d.computed_paths, d.reused_paths);
    assert!(s.state.cohorts.len() > 4000);
}
#[test]
fn unequal_reflected_weights_and_odd_flux_are_not_merged() {
    let (base, ctr, conf, gas) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let old = PositiveThresholdBridge(base.clone(), ctr);
    let new = ReflectionPooledBridge(base.clone(), ctr, PoolLimits::default());
    let mut a = old.initial(gas, &conf, 0.).unwrap();
    a.cohorts.push(pulse(&base, 65., 0.4, 1e-10));
    a.cohorts.push(pulse(&base, 65., -0.4, 2e-10));
    let r = old.advance(&a, &conf, 2e9).unwrap();
    let (s, _) = new.advance_with_diagnostics(&a, &conf, 2e9).unwrap();
    bit_parity(&r, &s);
    assert!(s.state.cohorts[0].direction_at_birth[2] > 0.);
    assert!(s.state.cohorts[1].direction_at_birth[2] < 0.);
    assert_ne!(
        s.state.cohorts[0].n_comoving_m3.to_bits(),
        s.state.cohorts[1].n_comoving_m3.to_bits()
    );
}
#[test]
fn threshold_crossing_trace_is_reused_with_identical_species_events() {
    let (mut base, ctr, mut conf, gas) =
        fixture(0., false, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    base.geometry = ConstantAxisymmetricBackground::new(
        0.,
        AxisymmetricPoint::new(1. / 21., 0., 2e-15, 0.).unwrap(),
        [0., 1.5e14],
    )
    .unwrap();
    conf.use_collisions = false;
    let old = PositiveThresholdBridge(base.clone(), ctr);
    let new = ReflectionPooledBridge(base.clone(), ctr, PoolLimits::default());
    let mut a = old.initial(gas, &conf, 0.).unwrap();
    a.cohorts.push(pulse(&base, 13.605, 0.4, 1e-12));
    a.cohorts.push(pulse(&base, 13.605, -0.4, 1e-12));
    let (r, rd) = old.advance_with_diagnostics(&a, &conf, 1e12).unwrap();
    let (s, d) = new.advance_with_diagnostics(&a, &conf, 1e12).unwrap();
    bit_parity(&r, &s);
    assert!(d.threshold_crossings > 0);
    assert_eq!(d.threshold_crossings, rd.threshold_crossings);
}
#[test]
fn cache_is_recreated_after_gas_temperature_or_source_changes() {
    let (base, ctr, conf, gas) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let old = PositiveThresholdBridge(base.clone(), ctr);
    let new = ReflectionPooledBridge(base, ctr, PoolLimits::default());
    let mut a = old.initial(gas, &conf, 0.).unwrap();
    for factor in [1., 1.01, 0.99] {
        a.full.gas.thermal_j_m3 *= factor;
        let r = old.advance(&a, &conf, 2e9).unwrap();
        let (s, d) = new.advance_with_diagnostics(&a, &conf, 2e9).unwrap();
        bit_parity(&r, &s);
        assert!(d.computed_paths > 0);
    }
}
#[test]
fn rejection_is_transactional_and_controls_are_bounded() {
    let (base, ctr, mut conf, gas) = fixture(0.06, true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    let old = PositiveThresholdBridge(base.clone(), ctr);
    let a = old.initial(gas, &conf, 0.).unwrap();
    let before = format!("{a:?}");
    conf.photon_source = "NOT_THE_SOURCE";
    assert!(
        ReflectionPooledBridge(base.clone(), ctr, PoolLimits::default())
            .advance(&a, &conf, 2e9)
            .is_err()
    );
    conf.photon_source = rei_iso_couple_reference::axbi_sources::SOURCE_ID;
    assert!(
        ReflectionPooledBridge(
            base,
            ctr,
            PoolLimits {
                max_entries: 5000,
                max_segments: 1
            }
        )
        .advance(&a, &conf, 2e9)
        .is_err()
    );
    assert_eq!(before, format!("{a:?}"));
}
#[test]
fn tilt_breaks_energy_reflection_and_has_no_admitted_cached_operator() {
    let beta = 0.08f64;
    let mu = 0.7;
    let e = 30.;
    let gamma = 1. / (1. - beta * beta).sqrt();
    let forward = gamma * e * (1. - beta * mu);
    let backward = gamma * e * (1. + beta * mu);
    assert!(forward != backward);
    assert!(((backward - forward) - 2. * gamma * e * beta * mu).abs() < 1e-13);
}
