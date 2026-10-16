use rei_rate_optin_policy::{
    choose, Benchmark, Decision, Forecast, InvalidCalibration, TemperaturePattern,
};
fn calibration(pattern: TemperaturePattern) -> Benchmark {
    Benchmark {
        pattern,
        worker_count: 4,
        measured_queries: 262144,
        direct_seconds: 0.049915997,
        table_seconds: 0.031050621,
        table_build_seconds: 0.132711501,
        table_resident_bytes: 9_109_624,
        source_identity_matched: true,
        max_sampled_coefficient_relative_error: 3.8172670147488274e-7,
    }
}
fn forecast(pattern: TemperaturePattern, queries: u64) -> Forecast {
    Forecast {
        pattern,
        worker_count: 4,
        expected_queries: queries,
        available_table_bytes: 20_000_000,
        requires_derivative_or_jacobian: false,
    }
}
#[test]
fn optimized_for_large_matched_ordered_workload() {
    let d = choose(
        calibration(TemperaturePattern::OrderedLogT),
        forecast(TemperaturePattern::OrderedLogT, 6_000_000),
    )
    .unwrap();
    assert!(
        matches!(d,Decision::Table{expected_net_saved_seconds:s,expected_speedup:v} if s>0.0&&v>=1.1)
    );
}
#[test]
fn small_workload_is_not_amortized() {
    assert_eq!(
        choose(
            calibration(TemperaturePattern::OrderedLogT),
            forecast(TemperaturePattern::OrderedLogT, 10000)
        )
        .unwrap(),
        Decision::Direct {
            reason: "AMORTIZATION_MARGIN_NOT_MET"
        }
    );
}
#[test]
fn requires_derivative_must_not_choose_table() {
    let mut f = forecast(TemperaturePattern::OrderedLogT, 30_000_000);
    f.requires_derivative_or_jacobian = true;
    assert_eq!(
        choose(calibration(TemperaturePattern::OrderedLogT), f).unwrap(),
        Decision::Direct {
            reason: "DERIVATIVE_UNADMITTED"
        }
    );
}
#[test]
fn source_identity_fails_closed() {
    let mut b = calibration(TemperaturePattern::OrderedLogT);
    b.source_identity_matched = false;
    assert_eq!(
        choose(b, forecast(TemperaturePattern::OrderedLogT, 30_000_000)).unwrap(),
        Decision::Direct {
            reason: "SOURCE_IDENTITY_UNMATCHED"
        }
    );
}
#[test]
fn insufficient_memory_fails_closed() {
    let mut f = forecast(TemperaturePattern::OrderedLogT, 30_000_000);
    f.available_table_bytes = 1_000;
    assert_eq!(
        choose(calibration(TemperaturePattern::OrderedLogT), f).unwrap(),
        Decision::Direct {
            reason: "INSUFFICIENT_MEMORY_BUDGET"
        }
    );
}
#[test]
fn no_unmatched_worker_or_pattern() {
    let b = calibration(TemperaturePattern::OrderedLogT);
    assert_eq!(
        choose(b, forecast(TemperaturePattern::Unknown, 30_000_000)).unwrap(),
        Decision::Direct {
            reason: "MISMATCHED_BENCHMARK_CONDITIONS"
        }
    );
    let mut f = forecast(TemperaturePattern::OrderedLogT, 30_000_000);
    f.worker_count = 2;
    assert_eq!(
        choose(b, f).unwrap(),
        Decision::Direct {
            reason: "MISMATCHED_BENCHMARK_CONDITIONS"
        }
    );
}
#[test]
fn statistical_accuracy_gate_retained() {
    let mut b = calibration(TemperaturePattern::OrderedLogT);
    b.max_sampled_coefficient_relative_error = 2e-5;
    assert_eq!(
        choose(b, forecast(TemperaturePattern::OrderedLogT, 30_000_000)).unwrap(),
        Decision::Direct {
            reason: "RATE_ACCURACY_GATE"
        }
    );
}
#[test]
fn slower_random_reference_cannot_be_admitted() {
    let mut b = calibration(TemperaturePattern::RandomLogT);
    b.table_seconds = 0.06;
    assert_eq!(
        choose(b, forecast(TemperaturePattern::RandomLogT, 30_000_000)).unwrap(),
        Decision::Direct {
            reason: "NO_PREDICTED_AMORTIZATION"
        }
    );
}
#[test]
fn bad_benchmark_rejected() {
    let mut b = calibration(TemperaturePattern::OrderedLogT);
    b.table_seconds = f64::NAN;
    assert_eq!(
        choose(b, forecast(TemperaturePattern::OrderedLogT, 30_000_000)).unwrap_err(),
        InvalidCalibration::NonFiniteOrNegative
    );
}
