use rei_br06_reference::{
    fixture::NativeFixture,
    reference::{self, BirthMethod, NativePath, PathControls, PathModel, PathSample, RunControls},
};
use rei_brperf01_photon::{
    Error, Mode, Result,
    batch::{ParallelPool, PreparedBatch, evaluate_serial},
    fingerprint::{ledger_bits, path_bits},
    fixture_root,
    kernel::{NativeKernel, PreparedNativePath, PreparedOpacity, Rules, integrate_path_cached},
};

struct Constant {
    rates: [f64; 4],
    expansion: f64,
}
impl PathModel for Constant {
    fn sample(&self, t: f64) -> Result<PathSample> {
        let energy_ev = 100.0 * (-self.expansion * t).exp();
        Ok(PathSample {
            energy_ev,
            direction: [0.8, 0.0, 0.6],
            energy_derivative_ev_s: -self.expansion * energy_ev,
            rates_per_s: self.rates,
        })
    }
}
fn controls(limit: usize) -> RunControls {
    RunControls {
        birth: BirthMethod::Fitted,
        refinement: 1,
        birth_degree: 8,
        path: PathControls {
            slabs: 2,
            opacity_degree: 2,
            event_degree: 4,
            ..PathControls::default()
        },
        split_spectrum: false,
        template_limit: limit,
        source_scale: 1.0,
    }
}

#[test]
fn constant_thin_thick_and_subnormal_all_fields_exact() {
    for tau in [
        0.0,
        f64::from_bits(1),
        1e-320,
        1e-100,
        1e-12,
        1e-8,
        1.00000001e-8,
        1e-5,
        1.0,
        94.0,
        1e4,
        1e12,
    ] {
        for opacity_degree in [1, 4, 16] {
            let control = PathControls {
                slabs: 2,
                opacity_degree,
                event_degree: 8,
                ..PathControls::default()
            };
            let model = Constant {
                rates: [tau, 2.0 * tau, 3.0 * tau, 4.0 * tau],
                expansion: 0.05,
            };
            let expected = reference::integrate_path(
                &model,
                &[0.0, 0.125, 1.0],
                [10.0, 20.0, 30.0, 11.0],
                control,
            )
            .unwrap();
            let rules = Rules::new(control).unwrap();
            let actual = integrate_path_cached(
                &model,
                &[0.0, 0.125, 1.0],
                [10.0, 20.0, 30.0, 11.0],
                control,
                &rules,
            )
            .unwrap();
            assert_eq!(
                path_bits(&actual),
                path_bits(&expected),
                "tau={tau} q={opacity_degree}"
            );
            assert_eq!(rules.work().virtual_samples, actual.samples);
            assert!(rules.work().opacity_integrals > 0);
        }
    }
}

#[test]
fn invalid_path_inputs_and_work_limits_keep_failure_classes() {
    let c = PathControls::default();
    let rules = Rules::new(c).unwrap();
    for rates in [
        [-1.0, 0.0, 0.0, 0.0],
        [f64::NAN, 0.0, 0.0, 0.0],
        [f64::INFINITY, 0.0, 0.0, 0.0],
    ] {
        let model = Constant {
            rates,
            expansion: 0.0,
        };
        let a = reference::integrate_path(&model, &[0.0, 1.0], [0.0; 4], c).unwrap_err();
        let b = integrate_path_cached(&model, &[0.0, 1.0], [0.0; 4], c, &rules).unwrap_err();
        assert_eq!(format!("{a:?}"), format!("{b:?}"));
    }
    let model = Constant {
        rates: [0.0; 4],
        expansion: 0.0,
    };
    for cuts in [vec![], vec![0.0], vec![1.0, 0.0], vec![0.0, f64::NAN]] {
        let a = reference::integrate_path(&model, &cuts, [0.0; 4], c).unwrap_err();
        let b = integrate_path_cached(&model, &cuts, [0.0; 4], c, &rules).unwrap_err();
        assert_eq!(format!("{a:?}"), format!("{b:?}"));
    }
    let c = PathControls {
        max_samples: 1,
        ..c
    };
    let a = reference::integrate_path(&model, &[0.0, 1.0], [0.0; 4], c).unwrap_err();
    let b = integrate_path_cached(&model, &[0.0, 1.0], [0.0; 4], c, &rules).unwrap_err();
    assert_eq!(a.class(), "REFERENCE_WORK_LIMIT");
    assert_eq!(format!("{a:?}"), format!("{b:?}"));
    assert!(
        Rules::new(PathControls {
            opacity_degree: 0,
            ..c
        })
        .is_err()
    );
    assert!(
        Rules::new(PathControls {
            event_degree: 129,
            ..c
        })
        .is_err()
    );
}

#[test]
fn prepared_opacity_edge_values_and_frozen_volume_are_bitwise_exact() {
    let f = NativeFixture::load(&fixture_root(), "SIGNED_MINUS").unwrap();
    let prepared = PreparedOpacity::new(&f).unwrap();
    let mut energies = vec![0.0, 1.0, 100.0, 1e6, f64::NAN, f64::INFINITY];
    for edge in [13.598434599702_f64, 13.60, 13.602134599702, 24.59, 54.42] {
        energies.extend([
            f64::from_bits(edge.to_bits() - 1),
            edge,
            f64::from_bits(edge.to_bits() + 1),
        ]);
    }
    for energy in energies {
        for volume in [
            f.recorded_mid_volume,
            1.0,
            1e-280,
            1e280,
            0.0,
            -1.0,
            f64::NAN,
        ] {
            let a = f.rates(energy, volume);
            let b = prepared.rates(energy, volume);
            match (a, b) {
                (Ok(a), Ok(b)) => assert_eq!(a.map(f64::to_bits), b.map(f64::to_bits)),
                (Err(a), Err(b)) => assert_eq!(format!("{a:?}"), format!("{b:?}")),
                other => panic!("mismatched opacity result {other:?}"),
            }
        }
    }
}

#[test]
fn invalid_frozen_gas_is_rejected_before_reuse() {
    let mut f = NativeFixture::load(&fixture_root(), "SIGNED_MINUS").unwrap();
    f.rate_gas.thermal_j_m3 = -1.0;
    assert!(PreparedOpacity::new(&f).is_err());
}

#[test]
fn prepared_opacity_cannot_be_bound_to_a_different_fixture() {
    let a = NativeFixture::load(&fixture_root(), "SIGNED_MINUS").unwrap();
    let b = NativeFixture::load(&fixture_root(), "SIGNED_PLUS").unwrap();
    let prepared = PreparedOpacity::new(&a).unwrap();
    let co = b.templates(false).unwrap().remove(0);
    assert!(matches!(
        PreparedNativePath::new(&b, &co, &prepared),
        Err(Error::InvalidInput("prepared_fixture_identity"))
    ));
}

#[test]
fn batch_and_worker_frozen_source_identities_are_bound() {
    let a = NativeFixture::load(&fixture_root(), "SIGNED_MINUS").unwrap();
    let b = NativeFixture::load(&fixture_root(), "SIGNED_PLUS").unwrap();
    let c = controls(1);
    let batch = PreparedBatch::build(&a, c).unwrap();
    assert!(matches!(
        evaluate_serial(&b, &batch, c.path, Mode::Cached),
        Err(Error::InvalidInput("batch_fixture_identity"))
    ));
    assert!(matches!(
        batch.reduce(&b, &[]),
        Err(Error::InvalidInput("batch_fixture_identity"))
    ));
    let wrong_pool = ParallelPool::new(&fixture_root(), "SIGNED_PLUS", 1).unwrap();
    assert!(matches!(
        wrong_pool.evaluate(&batch, c.path),
        Err(Error::InvalidInput("parallel_fixture_identity"))
    ));
    // Same geometry alone does not bind frozen gas or final observation time.
    let pool = ParallelPool::new(&fixture_root(), "SIGNED_MINUS", 1).unwrap();
    for change_gas in [false, true] {
        let mut changed = NativeFixture::load(&fixture_root(), "SIGNED_MINUS").unwrap();
        if change_gas {
            changed.rate_gas.thermal_j_m3 *= 1.01;
        } else {
            changed.t1 *= 0.9;
        }
        let changed_batch = PreparedBatch::build(&changed, c).unwrap();
        assert!(matches!(
            pool.evaluate(&changed_batch, c.path),
            Err(Error::InvalidInput("parallel_fixture_identity"))
        ));
    }
}

#[test]
fn original_384_source_rays_both_signed_geometries_bitwise_exact() {
    for case in ["SIGNED_MINUS", "SIGNED_PLUS"] {
        let f = NativeFixture::load(&fixture_root(), case).unwrap();
        let prepared = PreparedOpacity::new(&f).unwrap();
        let templates = f.templates(false).unwrap();
        assert_eq!(templates.len(), 384);
        for co in &templates {
            let a = NativePath {
                fixture: &f,
                cohort: co,
            };
            let b = PreparedNativePath::new(&f, co, &prepared).unwrap();
            for fraction in [0.0, 0.125, 0.5, 0.875, 1.0] {
                let t = f.t0 + (f.t1 - f.t0) * fraction;
                let pa = a.sample(t).unwrap();
                let pb = b.sample(t).unwrap();
                let bits = |p: PathSample| {
                    let mut v = vec![p.energy_ev.to_bits(), p.energy_derivative_ev_s.to_bits()];
                    v.extend(p.direction.map(f64::to_bits));
                    v.extend(p.rates_per_s.map(f64::to_bits));
                    v
                };
                assert_eq!(
                    bits(pa),
                    bits(pb),
                    "{case} spec={} angle={} t={t}",
                    co.spectral_index,
                    co.angular_index
                );
            }
        }
    }
}

#[test]
fn native_path_varied_spectrum_age_and_sign_exact() {
    for case in ["SIGNED_MINUS", "SIGNED_PLUS"] {
        let f = NativeFixture::load(&fixture_root(), case).unwrap();
        let c = controls(0);
        let kernel = NativeKernel::new(&f, c.path).unwrap();
        let templates = f.templates(false).unwrap();
        for index in [0, 31, 64, 127, 128, 191, 255, 256, 319, 383] {
            let births = reference::emit_births(&f, &templates[index], c).unwrap();
            for node in [0, births.len() / 2, births.len() - 1] {
                let co = &births[node].2;
                let a = reference::native_path(&f, co, c.path).unwrap();
                let b = kernel.native_path(co).unwrap();
                assert_eq!(
                    path_bits(&a),
                    path_bits(&b),
                    "{case} template={index} node={node}"
                );
            }
        }
    }
}

#[test]
fn ordered_pool_and_off_dispatch_reproduce_original_run_ledger() {
    let f = NativeFixture::load(&fixture_root(), "SIGNED_MINUS").unwrap();
    let c = controls(8);
    let input = PreparedBatch::build(&f, c).unwrap();
    assert_eq!(Mode::default(), Mode::Baseline);
    let baseline = evaluate_serial(&f, &input, c.path, Mode::default()).unwrap();
    let cached = evaluate_serial(&f, &input, c.path, Mode::Cached).unwrap();
    let pool = ParallelPool::new(&fixture_root(), "SIGNED_MINUS", 2).unwrap();
    let parallel = pool.evaluate(&input, c.path).unwrap();
    for ((a, b), p) in baseline
        .paths
        .iter()
        .zip(&cached.paths)
        .zip(&parallel.paths)
    {
        assert_eq!(path_bits(a), path_bits(b));
        assert_eq!(path_bits(a), path_bits(p));
    }
    let baseline_ledger = input.reduce(&f, &baseline.paths).unwrap();
    assert_eq!(
        ledger_bits(&baseline_ledger),
        ledger_bits(&input.reduce(&f, &parallel.paths).unwrap())
    );
    let directory =
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("evidence/test_original_run");
    let original = reference::run(&f, c, &directory).unwrap();
    assert_eq!(
        format!("{original:?}").replacen("Totals", "Ledger", 1),
        format!("{baseline_ledger:?}")
    );
    let bad = PathControls {
        max_samples: 1,
        ..c.path
    };
    let a = evaluate_serial(&f, &input, bad, Mode::Baseline)
        .err()
        .unwrap();
    let b = pool.evaluate(&input, bad).err().unwrap();
    assert_eq!(a.class(), "REFERENCE_WORK_LIMIT");
    assert_eq!(format!("{a:?}"), format!("{b:?}"));
    // Workers remain usable after a refusal; no pending replies are mistaken
    // for a later batch and the successful ordering remains deterministic.
    let recovered = pool.evaluate(&input, c.path).unwrap();
    assert_eq!(
        path_bits(&recovered.paths[0]),
        path_bits(&baseline.paths[0])
    );
}

#[test]
fn negative_population_and_wrong_birth_geometry_reject() {
    let f = NativeFixture::load(&fixture_root(), "SIGNED_MINUS").unwrap();
    let c = controls(1);
    let kernel = NativeKernel::new(&f, c.path).unwrap();
    let original = reference::emit_births(&f, &f.templates(false).unwrap()[0], c).unwrap()[0]
        .2
        .clone();
    for wrong_geometry in [false, true] {
        let mut co = original.clone();
        if wrong_geometry {
            co.birth_geometry.scale_factors[1] *= 1.01;
        } else {
            co.n_comoving_m3 = -1.0;
        }
        let a = reference::native_path(&f, &co, c.path).unwrap_err();
        let b = kernel.native_path(&co).unwrap_err();
        assert_eq!(format!("{a:?}"), format!("{b:?}"));
    }
}

#[test]
fn source_contract_and_zero_source_metadata_preserved() {
    let mut f = NativeFixture::load(&fixture_root(), "SIGNED_MINUS").unwrap();
    let c = RunControls {
        source_scale: 0.0,
        ..controls(8)
    };
    let input = PreparedBatch::build(&f, c).unwrap();
    assert!(input.births().iter().all(|b| b.cohort.n_comoving_m3 == 0.0));
    let baseline = evaluate_serial(&f, &input, c.path, Mode::Baseline).unwrap();
    let cached = evaluate_serial(&f, &input, c.path, Mode::Cached).unwrap();
    for (a, b) in baseline.paths.iter().zip(&cached.paths) {
        assert_eq!(path_bits(a), path_bits(b));
    }
    let ledger = input.reduce(&f, &cached.paths).unwrap();
    assert_eq!(ledger.born, 0.0);
    assert_eq!(ledger.surviving, 0.0);
    assert_eq!(ledger.zero_born_cohorts, input.births().len());
    assert!(
        PreparedBatch::build(
            &f,
            RunControls {
                source_scale: -1.0,
                ..c
            }
        )
        .is_err()
    );
    f.bridge.0.source.spectral_cells[0].photon_fraction *= 1.01;
    assert!(matches!(
        PreparedBatch::build(&f, c),
        Err(Error::InvalidInput("source_owner_cells"))
    ));
}
