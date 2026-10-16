//! Evidence-aware C10 advisory decision for a preexisting Grackle rate table.
//!
//! No production backend is switched by this crate. Measurements are conditional
//! and must be matched on source code, temperature distribution and concurrency.
//! No derivative/Jacobian or EoR trajectory admission is implied by a selection.
#![forbid(unsafe_code)]

/// Frozen table coefficient value tolerance from the upstream source contract.
pub const MAX_SAMPLED_COEFFICIENT_RELATIVE_ERROR: f64 = 1.0e-5;
/// Only a calibrated forecast saving at least 10% can be selected.
pub const MIN_WHOLE_EVALUATOR_SPEEDUP: f64 = 1.10;
/// Guard against overoptimistic amortization of table construction.
pub const MIN_BUILD_COST_MARGIN: f64 = 1.50;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum TemperaturePattern {
    OrderedLogT,
    RandomLogT,
    Unknown,
}

#[derive(Clone, Copy, Debug)]
pub struct Benchmark {
    pub pattern: TemperaturePattern,
    pub worker_count: u8,
    pub measured_queries: u64,
    pub direct_seconds: f64,
    pub table_seconds: f64,
    pub table_build_seconds: f64,
    pub table_resident_bytes: u64,
    /// The same exact frozen chemistry/atomic source is used in both paths.
    pub source_identity_matched: bool,
    /// Empirical pointwise bound, not a certified function-space bound.
    pub max_sampled_coefficient_relative_error: f64,
}

#[derive(Clone, Copy, Debug)]
pub struct Forecast {
    pub pattern: TemperaturePattern,
    pub worker_count: u8,
    pub expected_queries: u64,
    pub available_table_bytes: u64,
    /// A future Newton/implicit caller needs a source-consistent temperature derivative.
    pub requires_derivative_or_jacobian: bool,
}
#[derive(Debug, PartialEq)]
pub enum Decision {
    Direct {
        reason: &'static str,
    },
    Table {
        expected_net_saved_seconds: f64,
        expected_speedup: f64,
    },
}
#[derive(Debug, PartialEq)]
pub enum InvalidCalibration {
    NonFiniteOrNegative,
    MissingSamples,
    InvalidWorkers,
}

pub fn choose(bench: Benchmark, run: Forecast) -> Result<Decision, InvalidCalibration> {
    for x in [
        bench.direct_seconds,
        bench.table_seconds,
        bench.table_build_seconds,
        bench.max_sampled_coefficient_relative_error,
    ] {
        if !x.is_finite() || x < 0.0 {
            return Err(InvalidCalibration::NonFiniteOrNegative);
        }
    }
    if bench.measured_queries == 0 {
        return Err(InvalidCalibration::MissingSamples);
    }
    if bench.worker_count == 0
        || bench.worker_count > 4
        || run.worker_count == 0
        || run.worker_count > 4
    {
        return Err(InvalidCalibration::InvalidWorkers);
    }
    if !bench.source_identity_matched {
        return Ok(Decision::Direct {
            reason: "SOURCE_IDENTITY_UNMATCHED",
        });
    }
    if bench.max_sampled_coefficient_relative_error > MAX_SAMPLED_COEFFICIENT_RELATIVE_ERROR {
        return Ok(Decision::Direct {
            reason: "RATE_ACCURACY_GATE",
        });
    }
    if run.requires_derivative_or_jacobian {
        return Ok(Decision::Direct {
            reason: "DERIVATIVE_UNADMITTED",
        });
    }
    if run.pattern == TemperaturePattern::Unknown
        || run.pattern != bench.pattern
        || run.worker_count != bench.worker_count
    {
        return Ok(Decision::Direct {
            reason: "MISMATCHED_BENCHMARK_CONDITIONS",
        });
    }
    if run.available_table_bytes < bench.table_resident_bytes {
        return Ok(Decision::Direct {
            reason: "INSUFFICIENT_MEMORY_BUDGET",
        });
    }
    if run.expected_queries == 0 || bench.table_seconds >= bench.direct_seconds {
        return Ok(Decision::Direct {
            reason: "NO_PREDICTED_AMORTIZATION",
        });
    }
    let n = run.expected_queries as f64 / bench.measured_queries as f64;
    let direct_cost = n * bench.direct_seconds;
    let table_cost = bench.table_build_seconds + n * bench.table_seconds;
    let gross_savings = n * (bench.direct_seconds - bench.table_seconds);
    if !direct_cost.is_finite() || !table_cost.is_finite() || !gross_savings.is_finite() {
        return Err(InvalidCalibration::NonFiniteOrNegative);
    }
    if table_cost <= 0.0 || gross_savings < MIN_BUILD_COST_MARGIN * bench.table_build_seconds {
        return Ok(Decision::Direct {
            reason: "AMORTIZATION_MARGIN_NOT_MET",
        });
    }
    let speedup = direct_cost / table_cost;
    if speedup < MIN_WHOLE_EVALUATOR_SPEEDUP {
        return Ok(Decision::Direct {
            reason: "SMALL_PREDICTED_NET_GAIN",
        });
    }
    Ok(Decision::Table {
        expected_net_saved_seconds: direct_cost - table_cost,
        expected_speedup: speedup,
    })
}
