use rei_microphysics::igm_background::{FlatFlrwBackground, FlatFlrwConfig};
use rei_microphysics::igm_source::{build_birth_schedule, Birth, ConstantSource};
use rei_microphysics::{verner_cutoff_ev, Absorber, HHeModel};

fn matter_background(lo: f64, hi: f64) -> FlatFlrwBackground {
    FlatFlrwBackground::new(FlatFlrwConfig {
        h0_per_s: 2.2e-18,
        omega_r: 0.0,
        omega_m: 1.0,
        omega_b: 0.048,
        omega_lambda: 0.0,
        helium_mass_fraction: 0.24,
        tcmb0_k: 2.7255,
        ln_a_min: lo,
        ln_a_max: hi,
        parameter_source: "manufactured analytic matter-only fixture".into(),
    })
    .unwrap()
}

fn analytic_time(lo: f64, hi: f64) -> f64 {
    (2.0 / (3.0 * 2.2e-18)) * ((1.5 * hi).exp() - (1.5 * lo).exp())
}
fn analytic_mean_energy(source: ConstantSource) -> f64 {
    (source.energy_max_ev / source.energy_min_ev).ln()
        / (1.0 / source.energy_min_ev - 1.0 / source.energy_max_ev)
}
fn relative_error(got: f64, expected: f64) -> f64 {
    ((got - expected) / expected).abs()
}
fn source_moments(source: ConstantSource, panels: usize) -> (f64, f64) {
    let nodes = source.energy_quadrature(panels).unwrap();
    (
        nodes.iter().map(|node| node.number_weight).sum(),
        nodes
            .iter()
            .map(|node| node.energy_ev * node.number_weight)
            .sum(),
    )
}

#[test]
fn manufactured_source_is_frozen_and_explicitly_overridable() {
    let source = ConstantSource::manufactured_v1();
    assert_eq!(source.photons_per_h_per_s, 1e-15);
    assert_eq!(source.energy_min_ev, 13.7);
    assert_eq!(source.energy_max_ev, 100.0);
    let other = ConstantSource {
        photons_per_h_per_s: 4e-15,
        energy_min_ev: 10.0,
        energy_max_ev: 200.0,
    };
    assert!(other.energy_quadrature(2).is_ok());
}

#[test]
fn positive_gauss_pairs_respect_binding_and_verner_segment_boundaries() {
    let source = ConstantSource {
        energy_min_ev: 10.0,
        ..ConstantSource::manufactured_v1()
    };
    let bindings = HHeModel::controlled_fixture().threshold_ev;
    let cutoffs = [Absorber::HI, Absorber::HeI, Absorber::HeII].map(verner_cutoff_ev);
    let mut boundaries = vec![source.energy_min_ev, source.energy_max_ev];
    boundaries.extend(bindings);
    boundaries.extend(cutoffs);
    boundaries.sort_by(f64::total_cmp);
    let panels = 3;
    let nodes = source.energy_quadrature(panels).unwrap();
    assert_eq!(nodes.len(), 2 * panels * (boundaries.len() - 1));
    let mut cursor = 0;
    for edges in boundaries.windows(2) {
        for panel in 0..panels {
            let left = edges[0] + (edges[1] - edges[0]) * panel as f64 / panels as f64;
            let right = edges[0] + (edges[1] - edges[0]) * (panel + 1) as f64 / panels as f64;
            for node in &nodes[cursor..cursor + 2] {
                assert!(node.energy_ev > left && node.energy_ev < right);
                assert!(node.number_weight.is_normal() && node.number_weight > 0.0);
            }
            assert!(nodes[cursor].energy_ev < nodes[cursor + 1].energy_ev);
            cursor += 2;
        }
    }
}

#[test]
fn analytic_number_and_energy_moments_converge_at_gauss_order() {
    let source = ConstantSource::manufactured_v1();
    let exact_energy = analytic_mean_energy(source);
    let errors: Vec<_> = [4, 8, 16]
        .into_iter()
        .map(|panels| {
            let (number, energy) = source_moments(source, panels);
            ((number - 1.0).abs(), relative_error(energy, exact_energy))
        })
        .collect();
    for pair in errors.windows(2) {
        assert!(pair[0].0 > 8.0 * pair[1].0, "number errors: {errors:?}");
        assert!(pair[0].1 > 8.0 * pair[1].1, "energy errors: {errors:?}");
    }
    let (number, energy) = source_moments(source, 128);
    assert!((number - 1.0).abs() <= 1e-8);
    assert!(relative_error(energy, exact_energy) <= 1e-8);
}

#[test]
fn birth_weights_use_one_inverse_hubble_factor_and_no_density_dilution() {
    let lo = -2.6;
    let hi = -2.4;
    let background = matter_background(lo, hi);
    let source = ConstantSource::manufactured_v1();
    let sed_number = source_moments(source, 4).0;
    let exact_time = analytic_time(lo, hi);
    let errors: Vec<_> = [1, 2, 4]
        .into_iter()
        .map(|panels| {
            let births = build_birth_schedule(&background, &source, lo, hi, panels, 4).unwrap();
            let emitted: f64 = births.iter().map(|birth| birth.per_h).sum();
            relative_error(
                emitted / (source.photons_per_h_per_s * sed_number),
                exact_time,
            )
        })
        .collect();
    assert!(errors[0] > 12.0 * errors[1], "birth errors: {errors:?}");
    assert!(errors[1] > 12.0 * errors[2], "birth errors: {errors:?}");
    let births = build_birth_schedule(&background, &source, lo, hi, 32, 4).unwrap();
    let emitted: f64 = births.iter().map(|birth| birth.per_h).sum();
    assert!(
        relative_error(
            emitted / (source.photons_per_h_per_s * sed_number),
            exact_time
        ) <= 1e-11
    );
    let emitted_comoving = emitted * background.n_h_comoving_cm3();
    assert!(relative_error(emitted_comoving / background.n_h_comoving_cm3(), emitted) <= 1e-15);
}

#[test]
fn integrated_source_matches_separate_analytic_number_and_energy_moments() {
    let lo = -2.6;
    let hi = -2.4;
    let background = matter_background(lo, hi);
    let source = ConstantSource::manufactured_v1();
    let births = build_birth_schedule(&background, &source, lo, hi, 16, 128).unwrap();
    let emitted: f64 = births.iter().map(|birth| birth.per_h).sum();
    let energy: f64 = births
        .iter()
        .map(|birth| birth.energy_ev * birth.per_h)
        .sum();
    let exact_number = source.photons_per_h_per_s * analytic_time(lo, hi);
    assert!(relative_error(emitted, exact_number) <= 1e-8);
    assert!(relative_error(energy, exact_number * analytic_mean_energy(source)) <= 1e-8);
}

fn consume_at_gas_endpoints(births: &[Birth], endpoints: &[f64]) -> Vec<[u64; 3]> {
    let mut cursor = 0;
    let mut consumed = Vec::new();
    for endpoint in endpoints {
        while cursor < births.len() && births[cursor].ln_a <= *endpoint {
            let birth = births[cursor];
            consumed.push([
                birth.ln_a.to_bits(),
                birth.energy_ev.to_bits(),
                birth.per_h.to_bits(),
            ]);
            cursor += 1;
        }
    }
    assert_eq!(cursor, births.len());
    consumed
}

#[test]
fn fixed_birth_schedule_is_identical_under_unrelated_gas_step_subdivisions() {
    let lo = -2.6;
    let hi = -2.4;
    let background = matter_background(lo, hi);
    let source = ConstantSource::manufactured_v1();
    let births = build_birth_schedule(&background, &source, lo, hi, 5, 3).unwrap();
    assert!(!births.is_empty());
    assert!(births
        .iter()
        .all(|b| b.ln_a > lo && b.ln_a < hi && b.per_h > 0.0));
    for pair in births.windows(2) {
        assert!(pair[0].ln_a <= pair[1].ln_a);
        if pair[0].ln_a == pair[1].ln_a {
            assert!(pair[0].energy_ev < pair[1].energy_ev);
        }
    }
    let coarse = consume_at_gas_endpoints(&births, &[lo + 0.07, hi]);
    let fine =
        consume_at_gas_endpoints(&births, &[lo + 0.001, lo + 0.021, lo + 0.08, lo + 0.17, hi]);
    assert_eq!(coarse, fine);
    assert_eq!(
        births,
        build_birth_schedule(&background, &source, lo, hi, 5, 3).unwrap()
    );
}

#[test]
fn zero_source_has_exactly_no_births() {
    let lo = -2.6;
    let hi = -2.4;
    let background = matter_background(lo, hi);
    let source = ConstantSource {
        photons_per_h_per_s: 0.0,
        ..ConstantSource::manufactured_v1()
    };
    assert!(build_birth_schedule(&background, &source, lo, hi, 3, 2)
        .unwrap()
        .is_empty());
    assert!(!source.energy_quadrature(2).unwrap().is_empty());
}

#[test]
fn malformed_source_or_quadrature_inputs_are_rejected() {
    let lo = -2.6;
    let hi = -2.4;
    let background = matter_background(lo, hi);
    let source = ConstantSource::manufactured_v1();
    for value in [-1.0, f64::NAN, f64::INFINITY, f64::from_bits(1)] {
        assert!(ConstantSource {
            photons_per_h_per_s: value,
            ..source
        }
        .energy_quadrature(2)
        .is_err());
    }
    for (lower, upper) in [
        (0.0, 100.0),
        (-1.0, 100.0),
        (100.0, 100.0),
        (100.0, 10.0),
        (10.0, 50001.0),
        (f64::NAN, 100.0),
    ] {
        assert!(ConstantSource {
            energy_min_ev: lower,
            energy_max_ev: upper,
            ..source
        }
        .energy_quadrature(2)
        .is_err());
    }
    assert!(source.energy_quadrature(0).is_err());
    assert!(source.energy_quadrature(usize::MAX).is_err());
    for (start, end, panels) in [
        (hi, lo, 1),
        (lo, lo, 1),
        (lo - 0.01, hi, 1),
        (lo, hi + 0.01, 1),
        (lo, hi, 0),
        (lo, hi, usize::MAX),
    ] {
        assert!(build_birth_schedule(&background, &source, start, end, panels, 1).is_err());
    }
}

#[test]
fn unrepresentable_gauss_interiors_and_weight_arithmetic_are_rejected() {
    let source = ConstantSource::manufactured_v1();
    let narrow = ConstantSource {
        energy_min_ev: 100.0,
        energy_max_ev: f64::from_bits(100.0f64.to_bits() + 1),
        ..source
    };
    assert!(narrow.energy_quadrature(1).is_err());
    let lo = -2.6;
    let hi = -2.4;
    let background = matter_background(lo, hi);
    let over = ConstantSource {
        photons_per_h_per_s: f64::MAX,
        ..source
    };
    assert!(build_birth_schedule(&background, &over, lo, hi, 1, 1).is_err());
    let tiny = ConstantSource {
        photons_per_h_per_s: f64::MIN_POSITIVE,
        ..source
    };
    assert!(build_birth_schedule(&background, &tiny, lo, hi, 1, 128).is_ok());
    let narrow_hi = f64::from_bits(lo.to_bits() - 1);
    assert!(build_birth_schedule(&background, &source, lo, narrow_hi, 1, 1).is_err());
}
