use rei_microphysics::axbi_covariant_transport::{CovariantTransport, PhotonState};
use rei_microphysics::axbi_driver::{Driver, DriverConfig, DriverState};
use rei_microphysics::axbi_parallel::OrderedWorkerPool;
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::{ForwardError, GeometrySnapshot};
use std::collections::HashSet;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Barrier};
fn geometry(ratio: f64) -> GeometrySnapshot {
    GeometrySnapshot::new([ratio / 21.0; 3], [0.0; 3]).unwrap()
}
fn transport(threads: usize) -> CovariantTransport {
    let source = AxbiSource::new(1.898198450714027e-7, 0.2, 16, 8).unwrap();
    CovariantTransport::new(&source, geometry(1.0), 128, 13.6, 512.0)
        .unwrap()
        .with_threads(threads)
        .unwrap()
}
fn populated(core: &CovariantTransport) -> PhotonState {
    let mut state = core.empty_state();
    for j in 0..state.number.len() {
        let i = j % core.n_energy();
        let lo = core.edges()[i];
        let hi = core.edges()[i + 1];
        let mean = lo
            + (hi - lo)
                * match i % 4 {
                    0 => 0.3,
                    1 => 0.7,
                    2 => 1e-8,
                    _ => 1.0 - 1e-8,
                };
        state.number[j] = 1e-11 * (1.0 + i as f64 / 100.0);
        state.energy_ref[j] = mean * state.number[j];
        state.support_lo[j] = lo;
        state.support_hi[j] = hi;
    }
    core.validate_state(&state).unwrap();
    state
}
fn assert_state(a: &DriverState, b: &DriverState) {
    // No clocks or counters are excluded here: adaptive_step never measures wall
    // time. Pool metadata lives on Driver, outside the deterministic physics state.
    assert_eq!(format!("{a:?}"), format!("{b:?}"));
}
#[test]
fn persistent_workers_preserve_index_order_and_reuse_fixed_threads() {
    let pool = OrderedWorkerPool::new(4).unwrap();
    assert_eq!(pool.width(), 4);
    let first = {
        let barrier = Arc::new(Barrier::new(4));
        pool.map_ordered(16, move |i| {
            if i < 4 {
                barrier.wait();
            }
            Ok((i, std::thread::current().id()))
        })
        .unwrap()
    };
    let second = {
        let barrier = Arc::new(Barrier::new(4));
        pool.map_ordered(16, move |i| {
            if i < 4 {
                barrier.wait();
            }
            Ok((i, std::thread::current().id()))
        })
        .unwrap()
    };
    assert_eq!(
        first.iter().map(|x| x.0).collect::<Vec<_>>(),
        (0..16).collect::<Vec<_>>()
    );
    assert_eq!(
        first.iter().take(4).map(|x| x.1).collect::<HashSet<_>>(),
        second.iter().take(4).map(|x| x.1).collect::<HashSet<_>>()
    );
    assert_eq!(
        first
            .iter()
            .take(4)
            .map(|x| x.1)
            .collect::<HashSet<_>>()
            .len(),
        4
    );
    // Dropping joins the persistent workers; no detached threads or delayed jobs.
    drop(pool);
}
#[test]
fn lowest_index_error_is_deterministic_and_pool_survives_failure() {
    let pool = OrderedWorkerPool::new(4).unwrap();
    let completed = Arc::new(AtomicUsize::new(0));
    let c = Arc::clone(&completed);
    let error = pool
        .map_ordered(64, move |i| {
            c.fetch_add(1, Ordering::SeqCst);
            match i {
                3 => Err(ForwardError::InvalidInput("lowest_cell")),
                41 => Err(ForwardError::InvalidInput("later_cell")),
                _ => Ok(i),
            }
        })
        .unwrap_err();
    assert!(format!("{error:?}").contains("lowest_cell"));
    assert_eq!(completed.load(Ordering::SeqCst), 64);
    assert_eq!(
        pool.map_ordered(8, Ok::<usize, ForwardError>).unwrap(),
        (0..8).collect::<Vec<_>>()
    );
    assert!(OrderedWorkerPool::new(0).is_err());
    assert!(OrderedWorkerPool::new(65).is_err());
}
#[test]
fn original_scalar_new_serial_and_parallel_prepare_are_bitwise_equal() {
    let serial = transport(1);
    let state = populated(&serial);
    let g = geometry(1.001);
    let reference = serial.prepare_legacy_serial(&state, &g).unwrap();
    let expected = format!("{reference:?}");
    let reference_result = format!(
        "{:?}",
        reference
            .evaluate([0.0017, 0.00014, 1e-8], 0.0017, 1e8)
            .unwrap()
    );
    for width in [1, 8, 32, 64] {
        let core = transport(width);
        let prepared = core.prepare(&state, &g).unwrap();
        assert_eq!(format!("{prepared:?}"), expected, "width{width}");
        assert_eq!(
            format!(
                "{:?}",
                prepared
                    .evaluate([0.0017, 0.00014, 1e-8], 0.0017, 1e8)
                    .unwrap()
            ),
            reference_result,
            "width{width}"
        );
    }
}
#[test]
fn exact_zero_heii_events_and_invalid_input_priority_do_not_depend_on_width() {
    for width in [1, 8, 32, 64] {
        let core = transport(width);
        let mut state = core.empty_state();
        core.add_delta(&mut state, 0, 54.42, 1.0).unwrap();
        let prepared = core.prepare(&state, &geometry(1.001)).unwrap();
        let result = prepared.evaluate([0.0, 0.0, 0.001], 0.0017, 1e10).unwrap();
        assert_eq!(result.absorbed_per_h[2], 0.0);
        assert_eq!(result.photo.gamma_s[2], 0.0);
        assert_eq!(result.heat_ev_per_h, 0.0);
        state.number[1] = 1.0;
        let error = core.prepare(&state, &geometry(1.001)).unwrap_err();
        assert!(format!("{error:?}").contains("AXBI_COVARIANT_SUPPORT_DOMAIN"));
    }
}
#[test]
fn production_driver_serial_threaded_states_ledgers_and_decisions_match() {
    let mut config = DriverConfig::baseline();
    config.end_zbar = 19.8;
    config.background_panels = 64;
    config.transport_cells = 128;
    config.inactive_hi_split = true;
    let (serial, mut one) = Driver::new(config.clone()).unwrap();
    config.transport_threads = 8;
    let (parallel, mut many) = Driver::new(config).unwrap();
    assert_eq!(parallel.transport.transport_threads(), 8);
    for _ in 0..24 {
        let accepted_one = serial.adaptive_step(&mut one).unwrap();
        let accepted_many = parallel.adaptive_step(&mut many).unwrap();
        assert_eq!(accepted_one, accepted_many);
        assert_state(&one, &many);
        if one.accepted >= 3 {
            break;
        }
    }
    assert_eq!(one.accepted, 3);
    serial.validate(&one, 1e-8).unwrap();
    parallel.validate(&many, 1e-8).unwrap();
    assert_eq!(
        serial.photon_pool_inventory(&one).unwrap(),
        parallel.photon_pool_inventory(&many).unwrap()
    );
}
#[test]
fn thread_configuration_is_bounded_explicit_and_defaults_to_one() {
    assert_eq!(DriverConfig::baseline().transport_threads, 1);
    assert_eq!(
        DriverConfig::read("transport_threads=64\n")
            .unwrap()
            .transport_threads,
        64
    );
    for value in ["0", "65", "NaN", "-1"] {
        assert!(DriverConfig::read(&format!("transport_threads={value}\n")).is_err());
    }
}
