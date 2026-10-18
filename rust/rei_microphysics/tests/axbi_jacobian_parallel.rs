use rei_microphysics::axbi_driver::{jacobian_columns, Driver, DriverConfig};
use rei_microphysics::axbi_parallel::OrderedWorkerPool;
use rei_microphysics::ForwardError;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};

fn polynomial(x: [f64; 4]) -> [f64; 4] {
    [
        x[0] * x[0] + x[1],
        x[1] * 3.0 + x[2],
        x[2] * x[2] - x[3],
        x[3] * 2.0 + x[0],
    ]
}
fn bits(matrix: [[f64; 4]; 4]) -> [[u64; 4]; 4] {
    matrix.map(|row| row.map(f64::to_bits))
}
#[test]
fn flag_is_explicit_opt_in_and_rejects_invalid_values() {
    assert!(!DriverConfig::read("").unwrap().parallel_jacobian_columns);
    assert!(
        !DriverConfig::read("parallel_jacobian_columns=false\n")
            .unwrap()
            .parallel_jacobian_columns
    );
    assert!(
        DriverConfig::read("parallel_jacobian_columns=true\n")
            .unwrap()
            .parallel_jacobian_columns
    );
    for value in ["1", "yes", "TRUE", "NaN", ""] {
        assert!(DriverConfig::read(&format!("parallel_jacobian_columns={value}\n")).is_err());
    }
}
#[test]
fn positive_columns_preserve_residual_and_jacobian_bits() {
    let pool = OrderedWorkerPool::new(8).unwrap();
    let x = [0.2, 0.3, 0.1, 0.7];
    let residual = polynomial(x);
    let mut serial = 3;
    let mut parallel = 3;
    let a = jacobian_columns(&pool, false, x, residual, &mut serial, 100, |v| {
        Ok(polynomial(v))
    })
    .unwrap();
    let b = jacobian_columns(&pool, true, x, residual, &mut parallel, 100, |v| {
        Ok(polynomial(v))
    })
    .unwrap();
    assert_eq!(residual.map(f64::to_bits), polynomial(x).map(f64::to_bits));
    assert_eq!(bits(a), bits(b));
    assert_eq!((serial, parallel), (7, 7));
    assert!((a[0][0] - 0.4).abs() < 1e-6);
    assert!((a[1][1] - 3.0).abs() < 1e-6);
    assert!((a[2][2] - 0.2).abs() < 1e-6);
    assert!((a[3][3] - 2.0).abs() < 1e-6);
}
#[test]
fn negative_fallback_stays_inside_each_column_and_matches_bits() {
    let pool = OrderedWorkerPool::new(8).unwrap();
    let x = [1.0; 4];
    let residual = polynomial(x);
    let mut results = Vec::new();
    for parallel in [false, true] {
        let trace = Arc::new(Mutex::new(Vec::new()));
        let record = Arc::clone(&trace);
        let mut count = 0;
        let jac = jacobian_columns(&pool, parallel, x, residual, &mut count, 8, move |v| {
            let j = (0..4).find(|&j| v[j] != 1.0).unwrap();
            let positive = v[j] > 1.0;
            record.lock().unwrap().push((j, positive));
            if positive {
                Err(ForwardError::InvalidInput("positive_boundary"))
            } else {
                Ok(polynomial(v))
            }
        })
        .unwrap();
        assert_eq!(count, 8);
        let calls = trace.lock().unwrap();
        for j in 0..4 {
            assert_eq!(
                calls
                    .iter()
                    .filter(|&&(k, _)| k == j)
                    .copied()
                    .collect::<Vec<_>>(),
                vec![(j, true), (j, false)]
            );
        }
        results.push(bits(jac));
    }
    assert_eq!(results[0], results[1]);
}
#[test]
fn failures_return_lowest_column_and_charge_discarded_work() {
    let pool = OrderedWorkerPool::new(8).unwrap();
    let kernel = |v: [f64; 4]| {
        let j = (0..4).find(|&j| v[j] != 1.0).unwrap();
        if v[j] > 1.0 {
            return Err(ForwardError::InvalidInput("positive"));
        }
        match j {
            1 => Err(ForwardError::InvalidInput("lowest_j1")),
            3 => Err(ForwardError::InvalidInput("later_j3")),
            _ => Ok(polynomial(v)),
        }
    };
    let mut serial = 0;
    let mut parallel = 0;
    let a = jacobian_columns(
        &pool,
        false,
        [1.0; 4],
        polynomial([1.0; 4]),
        &mut serial,
        100,
        kernel,
    )
    .unwrap_err();
    let b = jacobian_columns(
        &pool,
        true,
        [1.0; 4],
        polynomial([1.0; 4]),
        &mut parallel,
        100,
        kernel,
    )
    .unwrap_err();
    assert!(format!("{a:?}").contains("lowest_j1"));
    assert!(format!("{b:?}").contains("lowest_j1"));
    assert_eq!((serial, parallel), (4, 8));
}
#[test]
fn fewer_than_eight_credits_retain_serial_prefix_exact_boundary_is_bounded() {
    let pool = OrderedWorkerPool::new(8).unwrap();
    let kernel = |v: [f64; 4]| {
        if v.iter().any(|&n| n > 1.0) {
            Err(ForwardError::InvalidInput("positive"))
        } else {
            Ok(polynomial(v))
        }
    };
    for cap in 0..8 {
        let mut serial = 0;
        let mut parallel = 0;
        let a = jacobian_columns(
            &pool,
            false,
            [1.0; 4],
            polynomial([1.0; 4]),
            &mut serial,
            cap,
            kernel,
        )
        .unwrap_err();
        let b = jacobian_columns(
            &pool,
            true,
            [1.0; 4],
            polynomial([1.0; 4]),
            &mut parallel,
            cap,
            kernel,
        )
        .unwrap_err();
        assert_eq!(format!("{a:?}"), format!("{b:?}"));
        assert_eq!((serial, parallel), (cap, cap));
    }
    let mut count = 5;
    jacobian_columns(
        &pool,
        true,
        [1.0; 4],
        polynomial([1.0; 4]),
        &mut count,
        13,
        kernel,
    )
    .unwrap();
    assert_eq!(count, 13);
}
#[test]
fn worker_panic_merges_every_started_debit_and_denial_starts_nothing() {
    let pool = OrderedWorkerPool::new(8).unwrap();
    let started = Arc::new(AtomicUsize::new(0));
    let calls = Arc::clone(&started);
    let mut count = 0;
    let failure = jacobian_columns(
        &pool,
        true,
        [1.0; 4],
        polynomial([1.0; 4]),
        &mut count,
        8,
        move |v| {
            calls.fetch_add(1, Ordering::Relaxed);
            if v[0] != 1.0 {
                panic!("injected worker panic");
            }
            Ok(polynomial(v))
        },
    )
    .unwrap_err();
    assert!(format!("{failure:?}").contains("AXBI_WORKER_TASK_PANIC"));
    assert_eq!(count, 4);
    assert_eq!(started.load(Ordering::Relaxed), count);
    let mut denied = 8;
    let calls = Arc::clone(&started);
    assert!(jacobian_columns(
        &pool,
        true,
        [1.0; 4],
        polynomial([1.0; 4]),
        &mut denied,
        8,
        move |v| {
            calls.fetch_add(1, Ordering::Relaxed);
            Ok(polynomial(v))
        }
    )
    .is_err());
    assert_eq!(denied, 8);
    assert_eq!(started.load(Ordering::Relaxed), 4);
}
#[test]
fn actual_stage_states_ledgers_decisions_match_and_failure_does_not_commit() {
    let mut config = DriverConfig::baseline();
    config.end_zbar = 19.8;
    config.background_panels = 64;
    config.transport_cells = 32;
    config.transport_threads = 8;
    config.inactive_hi_split = true;
    let (serial, mut a) = Driver::new(config).unwrap();
    let mut parallel = serial.clone(); // shares exactly the existing eight workers
    parallel.config.parallel_jacobian_columns = true;
    let mut b = a.clone();
    for _ in 0..4 {
        let accepted_a = serial.adaptive_step(&mut a).unwrap();
        let accepted_b = parallel.adaptive_step(&mut b).unwrap();
        assert_eq!(accepted_a, accepted_b);
        assert_eq!(format!("{a:?}"), format!("{b:?}"));
    }
    assert!(a.rhs_evaluations > 4);
    let before = format!("{b:?}");
    parallel.config.max_rhs = 1;
    let mut counter = 1;
    assert!(parallel.chemical_stage(&mut b, 1e8, &mut counter).is_err());
    assert_eq!(counter, 1);
    assert_eq!(format!("{b:?}"), before);
}
