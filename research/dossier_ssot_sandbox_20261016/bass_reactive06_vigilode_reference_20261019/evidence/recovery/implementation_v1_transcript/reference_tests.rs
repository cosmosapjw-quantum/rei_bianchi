use rei_br06_reference::{
    Error, Result,
    fixture::NativeFixture,
    quadrature::{PositiveGauss, gauss_age_nodes},
    reference::{
        BirthMethod, PathControls, PathModel, PathSample, RunControls, emit_births, integrate_path,
        native_path,
    },
};
use rei_iso_couple_reference::source_age::Cohort;
use std::path::Path;

struct Constant {
    rates: [f64; 4],
    energy: f64,
    expansion: f64,
}
impl PathModel for Constant {
    fn sample(&self, t: f64) -> Result<PathSample> {
        let energy_ev = self.energy * (-self.expansion * t).exp();
        Ok(PathSample {
            energy_ev,
            direction: [0.8, 0.0, 0.6],
            energy_derivative_ev_s: -self.expansion * energy_ev,
            rates_per_s: self.rates,
        })
    }
}

fn fixture(case: &str) -> NativeFixture {
    NativeFixture::load(&Path::new(env!("CARGO_MANIFEST_DIR")).join(".."), case).unwrap()
}
fn controls() -> RunControls {
    RunControls {
        birth: BirthMethod::Fitted,
        refinement: 4,
        birth_degree: 8,
        path: PathControls::default(),
        split_spectrum: false,
        template_limit: 0,
        source_scale: 1.0,
    }
}

#[test]
fn gauss_package_positive_monomials_and_rejection() {
    let rule = PositiveGauss::new(4).unwrap();
    for power in 0..=7 {
        let actual: f64 = rule.nodes.iter().map(|(x, w)| w * x.powi(power)).sum();
        assert!((actual - 1.0 / (power + 1) as f64).abs() < 2e-15);
    }
    assert!(PositiveGauss::new(0).is_err());
    assert!(PositiveGauss::new(129).is_err());
}

#[test]
fn exact_constant_opacity_birth_phi_and_competing_species_thick() {
    for tau in [0.0, 1e-12, 1e-5, 1.0, 94.0, 1e4, 1e12] {
        let source = 3.0;
        let model = Constant {
            rates: [0.1 * tau, 0.2 * tau, 0.3 * tau, 0.4 * tau],
            energy: 100.0,
            expansion: 0.0,
        };
        let mut survivor = 0.0;
        let mut events = [0.0; 4];
        for (age, weight) in rei_iso_couple_reference::fitted_birth::rule(tau, 2).unwrap() {
            let path = integrate_path(
                &model,
                &[0.0, age],
                [10.0, 20.0, 30.0, 11.0],
                PathControls {
                    slabs: 1,
                    opacity_degree: 2,
                    event_degree: 4,
                    ..PathControls::default()
                },
            )
            .unwrap();
            survivor += source * weight * path.survival;
            for (event, path_event) in events.iter_mut().zip(path.events) {
                *event += source * weight * path_event;
            }
            assert!(path.survival >= 0.0 && path.survival <= 1.0);
            assert!(path.number_residual.abs() < 3e-15);
            assert!(path.photo_split_residual_ev.abs() < 5e-14);
        }
        let exact = source * rei_iso_couple_reference::fitted_birth::phi(tau).unwrap();
        assert!(
            (survivor - exact).abs() < 2e-13 * exact,
            "tau={tau} survivor={survivor} exact={exact}"
        );
        for (i, event) in events.iter().enumerate() {
            let expected = (source - exact) * (i + 1) as f64 / 10.0;
            assert!(*event >= 0.0);
            assert!((event - expected).abs() < 3e-13 * source);
        }
        assert!((survivor + events.iter().sum::<f64>() - source).abs() < 3e-13 * source);
    }
}

#[test]
fn zero_opacity_redshift_work_and_energy_owner() {
    let model = Constant {
        rates: [0.0; 4],
        energy: 100.0,
        expansion: 0.05,
    };
    let r = integrate_path(&model, &[0.0, 2.0], [0.0; 4], PathControls::default()).unwrap();
    assert_eq!(r.survival, 1.0);
    assert_eq!(r.events, [0.0; 4]);
    let expected = 100.0 * ((-0.1_f64).exp() - 1.0);
    assert!((r.geometry_work_independent_ev - expected).abs() < 1e-13);
    assert!(r.energy_residual_ev.abs() < 1e-13);
}

#[test]
fn opacity_path_and_event_controls_refine_energy() {
    let model = Constant {
        rates: [1.0, 2.0, 3.0, 4.0],
        energy: 100.0,
        expansion: 0.05,
    };
    let exact_absorbed = 100.0 * 10.0 / 10.05 * (-(-10.05_f64).exp_m1());
    let coarse = integrate_path(
        &model,
        &[0.0, 1.0],
        [0.0; 4],
        PathControls {
            slabs: 1,
            event_degree: 4,
            ..PathControls::default()
        },
    )
    .unwrap();
    let fine = integrate_path(
        &model,
        &[0.0, 1.0],
        [0.0; 4],
        PathControls {
            slabs: 16,
            event_degree: 16,
            ..PathControls::default()
        },
    )
    .unwrap();
    assert!(
        (fine.absorbed_energy_ev - exact_absorbed).abs()
            < (coarse.absorbed_energy_ev - exact_absorbed).abs()
    );
    assert!(
        (fine.absorbed_energy_ev - exact_absorbed).abs() < 3e-11,
        "fine={:.17e} exact={exact_absorbed:.17e} error={:.17e}",
        fine.absorbed_energy_ev,
        fine.absorbed_energy_ev - exact_absorbed
    );
    assert!(
        fine.energy_residual_ev.abs() < 3e-11,
        "energy residual={:.17e}",
        fine.energy_residual_ev
    );
}

#[test]
fn invalid_population_source_and_work_limit_have_distinct_errors() {
    let prior = Error::from(rei_iso_couple_reference::full_network::NetworkError::Cx(
        rei_iso_couple_reference::mixture_coupling::CoupleError::WorkLimit,
    ));
    assert_eq!(prior.class(), "CX_WORK_LIMIT");
    assert_ne!(prior.class(), Error::WorkLimit("path_samples").class());
    let model = Constant {
        rates: [-1.0, 0.0, 0.0, 0.0],
        energy: 100.0,
        expansion: 0.0,
    };
    assert!(matches!(
        integrate_path(&model, &[0.0, 1.0], [0.0; 4], PathControls::default()),
        Err(Error::InvalidInput("path_sample"))
    ));
    let model = Constant {
        rates: [1.0, 0.0, 0.0, 0.0],
        energy: 100.0,
        expansion: 0.0,
    };
    assert!(matches!(
        integrate_path(
            &model,
            &[0.0, 1.0],
            [0.0; 4],
            PathControls {
                max_samples: 1,
                ..PathControls::default()
            }
        ),
        Err(Error::WorkLimit("path_samples"))
    ));
    assert!(matches!(
        integrate_path(&model, &[1.0, 1.0], [0.0; 4], PathControls::default()),
        Err(Error::InvalidInput("path_controls_or_cuts"))
    ));
}

#[test]
fn invalid_direction_and_accumulator_overflow_are_rejected() {
    struct Bad {
        direction: [f64; 3],
        derivative: f64,
    }
    impl PathModel for Bad {
        fn sample(&self, _: f64) -> Result<PathSample> {
            Ok(PathSample {
                energy_ev: 1.0,
                direction: self.direction,
                energy_derivative_ev_s: self.derivative,
                rates_per_s: [0.0; 4],
            })
        }
    }
    assert!(matches!(
        integrate_path(
            &Bad {
                direction: [2.0, 0.0, 0.0],
                derivative: 0.0
            },
            &[0.0, 2.0],
            [0.0; 4],
            PathControls::default()
        ),
        Err(Error::InvalidInput("path_sample"))
    ));
    assert!(matches!(
        integrate_path(
            &Bad {
                direction: [1.0, 0.0, 0.0],
                derivative: 1e308
            },
            &[0.0, 2.0],
            [0.0; 4],
            PathControls::default()
        ),
        Err(Error::InvalidInput("path_accumulator_finite_positive"))
    ));
    let m = Constant {
        rates: [1e4, 0.0, 0.0, 0.0],
        energy: 100.0,
        expansion: 0.0,
    };
    let out = integrate_path(
        &m,
        &[0.0, 1.0],
        [0.0; 4],
        PathControls {
            slabs: 1,
            ..PathControls::default()
        },
    )
    .unwrap();
    assert_eq!(out.survival, 0.0);
    assert!(out.represented_survival_underflow);
}

#[test]
fn actual_native_gas_source_zero_and_negative_rejection() {
    let fixture = fixture("SIGNED_MINUS");
    let mut template = fixture.templates(false).unwrap()[0].clone();
    let mut c = controls();
    c.source_scale = 0.0;
    let births = emit_births(&fixture, &template, c).unwrap();
    assert!(!births.is_empty());
    assert!(births.iter().all(|(_, _, co)| co.n_comoving_m3 == 0.0));
    c.source_scale = -1.0;
    assert!(matches!(
        emit_births(&fixture, &template, c),
        Err(Error::InvalidInput("source_weight"))
    ));
    template.n_comoving_m3 = -1.0;
    assert!(matches!(
        emit_births(&fixture, &template, controls()),
        Err(Error::InvalidInput("source_weight"))
    ));
    let mut fixture = fixture;
    fixture.bridge.0.source.spectral_cells[0].photon_fraction *= 2.0;
    assert!(matches!(
        fixture.templates(false),
        Err(Error::InvalidInput("source_owner_cells"))
    ));
}

#[test]
fn fitted_birth_source_labels_and_geometry_match_actual_first_template() {
    let f = fixture("SIGNED_MINUS");
    let templates = f.templates(false).unwrap();
    assert_eq!(templates.len(), 384);
    let mut controls = controls();
    controls.refinement = 8;
    let births = emit_births(&f, &templates[0], controls).unwrap();
    let text = std::fs::read_to_string(
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../inputs/STEP1_BIRTHS.csv"),
    )
    .unwrap();
    let mut rows = text.lines();
    let header: Vec<_> = rows.next().unwrap().split(',').collect();
    let column = |name: &str| header.iter().position(|&x| x == name).unwrap();
    for ((_, _, co), line) in births.iter().zip(rows) {
        let values: Vec<_> = line.split(',').collect();
        let value = |name: &str| values[column(name)].parse::<f64>().unwrap();
        assert_eq!(
            co.birth_time_s.to_bits(),
            value("actual_birth_time_s").to_bits()
        );
        assert_eq!(
            co.n_comoving_m3.to_bits(),
            value("born_count_com3").to_bits()
        );
    }
}

#[test]
fn actual_bass_signed_shear_and_all_fit_threshold_exits() {
    for case in ["SIGNED_MINUS", "SIGNED_PLUS"] {
        let f = fixture(case);
        let geometry = f.bridge.0.geometry.snapshot(f.t0).unwrap();
        let mut co = Cohort {
            birth_time_s: f.t0,
            birth_geometry: geometry,
            energy_at_birth_ev: 1.0,
            direction_at_birth: [(1.0 - 0.37_f64.powi(2)).sqrt(), 0.0, 0.37],
            n_comoving_m3: 1.0,
            spectral_index: 0,
            angular_index: 0,
        };
        let factor = co
            .ray_at(&f.bridge.0.geometry.snapshot(f.tm).unwrap())
            .unwrap()
            .energy_ev;
        for edge in [13.60, 24.59, 54.42, f.thresholds_ev[3]] {
            co.energy_at_birth_ev = edge / factor;
            let result = native_path(
                &f,
                &co,
                PathControls {
                    slabs: 4,
                    opacity_degree: 4,
                    event_degree: 8,
                    ..PathControls::default()
                },
            )
            .unwrap();
            assert!(result.threshold_crossings >= 1);
            assert!(result.events.iter().all(|n| n.is_finite() && *n >= 0.0));
            assert!(result.number_residual.abs() < 2e-14);
            assert!(result.geometry_work_independent_ev < 0.0);
        }
    }
}

#[test]
fn positive_high_order_birth_reference_resolves_frozen_layer() {
    for tau in [0.0, 1e-8, 1.0, 94.0, 1e4, 1e12] {
        let nodes = gauss_age_nodes(tau, 4, 8).unwrap();
        let sum: f64 = nodes.iter().map(|(x, w)| w * (-tau * x).exp()).sum();
        let expected = rei_iso_couple_reference::fitted_birth::phi(tau).unwrap();
        assert!((sum - expected).abs() < 3e-13 * expected, "tau={tau}");
        let born: f64 = nodes.iter().map(|(_, w)| w).sum();
        assert!((born - 1.0).abs() < 1e-13);
    }
}
