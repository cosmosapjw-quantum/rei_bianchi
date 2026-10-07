use rei_microphysics::{
    igm_config::{parse_config, HistoryConfig},
    igm_photo::packet_opacity,
    igm_state::IgmGasState,
};
use short_hhe_control::{
    coupled::{self, State},
    event_anchor,
    material::{self, MaterialOwners},
    radiation::{self, Grid},
    v2,
};
fn fixture() -> HistoryConfig {
    parse_config(include_str!(
        "../../../../docs/research_program/igm_next_nodes_20261007/long-flrw/radau-p128-o2/config.cfg"
    ))
    .unwrap()
}
fn close(a: f64, b: f64) {
    assert!(
        (a - b).abs() <= 2e-12 * a.abs().max(b.abs()).max(1e-290),
        "a={a:.17e} b={b:.17e}"
    );
}
fn state(cfg: &HistoryConfig, g: &Grid, t: f64, x: [f64; 3]) -> State {
    let mut s = State::new(cfg, g).unwrap();
    let p = cfg.background.at_ln_a(s.s).unwrap();
    s.y = material::values(&IgmGasState::from_temperature(x, p.n_h_cm3, p.n_he_cm3, t).unwrap());
    s
}
#[test]
fn nonphoto_actual_residual_uses_fraction_w_midpoint_and_shared_rhs() {
    let cfg = fixture();
    let grid = Grid {
        nodes: vec![],
        intervals: 0,
        base: 128,
        order: 2,
    };
    let old = state(&cfg, &grid, 300., [0.1, 0.05, 0.01]);
    let s1 = cfg.start + cfg.max_dln_a;
    let p1 = cfg.background.at_ln_a(s1).unwrap();
    let p = cfg.background.at_ln_a((old.s + s1) * 0.5).unwrap();
    let y = material::values(
        &IgmGasState::from_temperature([0.4, 0.2, 0.1], p1.n_h_cm3, p1.n_he_cm3, 1200.).unwrap(),
    );
    let ym = std::array::from_fn(|i| (old.y[i] + y[i]) * 0.5);
    let ev = coupled::evaluate(&cfg, &grid, &old, s1, p1, y).unwrap();
    let r = material::rhs(ym, p).unwrap();
    let expected = MaterialOwners::stage(r, p, s1 - old.s).unwrap();
    close(ev.material.work, expected.work);
    close(ev.material.cmb, expected.cmb);
    close(ev.material.escape, expected.escape);
    for i in 0..3 {
        close(
            ev.r[i],
            y[i] - old.y[i] - (s1 - old.s) / p.hubble_per_s * r.fraction_dt[i],
        );
    }
    close(
        ev.r[3],
        y[3] - old.y[3] - (s1 - old.s) / p.hubble_per_s * r.w_dt_erg_per_h_s,
    );
    let ts = material::gas(ym)
        .unwrap()
        .eos(p.n_h_cm3, p.n_he_cm3)
        .unwrap()
        .temperature_k;
    assert!((ts - 750.).abs() > 1.);
    assert!(ts > 300. && ts < 1200.);
    let mut pert = y;
    pert[3] *= 1.0001;
    let changed = coupled::evaluate(&cfg, &grid, &old, s1, p1, pert).unwrap();
    assert_ne!(
        changed.material.work, ev.material.work,
        "stale finite-difference stage"
    );
    let endpoint = MaterialOwners::stage(material::rhs(y, p1).unwrap(), p1, s1 - old.s).unwrap();
    assert!(
        (endpoint.work - ev.material.work).abs() > 2e-12 * ev.material.work,
        "endpoint-owned work mutant"
    );
    let defect = ev.r[3] + material::binding(ev.r, p.n_he_cm3 / p.n_h_cm3);
    let full = y[3] - old.y[3] + material::binding(y, p.n_he_cm3 / p.n_h_cm3)
        - material::binding(old.y, p.n_he_cm3 / p.n_h_cm3)
        + ev.material.escape
        + ev.material.work
        + ev.material.cmb;
    close(defect, full);
}
#[test]
fn actual_radiation_residual_uses_segment_affine_gas_and_actual_background() {
    let cfg = fixture();
    let s1 = cfg.start + cfg.max_dln_a;
    let eta = 24.59f64.ln() + cfg.start + cfg.max_dln_a / 3.;
    let grid = Grid {
        nodes: vec![(eta, 1.)],
        intervals: 1,
        base: 128,
        order: 2,
    };
    let mut old = state(&cfg, &grid, 300., [0.1, 0.05, 0.01]);
    old.density[0] = 0.0001;
    let p1 = cfg.background.at_ln_a(s1).unwrap();
    let y = material::values(
        &IgmGasState::from_temperature([0.4, 0.2, 0.1], p1.n_h_cm3, p1.n_he_cm3, 1200.).unwrap(),
    );
    let ev = coupled::evaluate(&cfg, &grid, &old, s1, p1, y).unwrap();
    let event = eta - 24.59f64.ln();
    let mut stock = old.density[0];
    let mut an = [0.; 3];
    let mut be = [0.; 3];
    let mut qn = 0.;
    for ab in [old.s, event, s1].windows(2) {
        let (a, b) = (ab[0], ab[1]);
        let mid = (a + b) * 0.5;
        let theta = (mid - old.s) / (s1 - old.s);
        let ys = std::array::from_fn(|i| old.y[i] + theta * (y[i] - old.y[i]));
        let p = cfg.background.at_ln_a(mid).unwrap();
        let e = (eta - mid).exp();
        let rates = packet_opacity(&material::gas(ys).unwrap(), e, p.n_h_cm3, p.n_he_cm3)
            .unwrap()
            .map(|v| v / p.hubble_per_s);
        let q = cfg.source.photons_per_h_per_s
            / ((1. / cfg.source.energy_min_ev - 1. / cfg.source.energy_max_ev)
                * e
                * p.hubble_per_s);
        let es = event_anchor::start_energy(eta, a, b).unwrap().0;
        let o = v2::kernel(stock, q, rates, b - a, es).unwrap();
        stock = o.n;
        qn += o.qn;
        for i in 0..3 {
            an[i] += o.an[i];
            be[i] += o.be[i];
        }
    }
    close(ev.radiation.owners.n, stock);
    close(ev.radiation.owners.qn, qn);
    for i in 0..3 {
        close(ev.radiation.owners.an[i], an[i]);
        close(ev.radiation.owners.be[i], be[i]);
    }
    let mut pert = y;
    pert[0] += 1e-5;
    let changed = coupled::evaluate(&cfg, &grid, &old, s1, p1, pert).unwrap();
    assert_ne!(
        changed.radiation.owners.an[0], ev.radiation.owners.an[0],
        "stale radiation stage"
    );
}
#[test]
fn actual_midpoint_neutral_adiabatic_law_and_order() {
    let mut cfg = fixture();
    cfg.fractions = [0.; 3];
    cfg.max_dln_a = 0.1;
    let grid = Grid {
        nodes: vec![],
        intervals: 0,
        base: 128,
        order: 2,
    };
    let old = State::new(&cfg, &grid).unwrap();
    let mut errs = vec![];
    for h in [0.04, 0.02, 0.01, 0.005] {
        let s1 = old.s + h;
        let dt = s1 - old.s;
        let got = coupled::advance(&cfg, &grid, &old, s1, old.y[3]).unwrap();
        let expected = old.y[3] * (1. - dt) / (1. + dt);
        close(got.y[3], expected);
        close(got.material.work, old.y[3] - got.y[3]);
        assert_eq!(got.y[..3], [0.; 3]);
        let error = (got.y[3] / old.y[3] - (-2. * dt).exp()).abs();
        errs.push(error);
        println!("ADIABATIC h={dt:.17e} error={error:.17e}");
    }
    let p = (errs[2] / errs[3]).log2();
    assert!(p > 2.8 && p < 3.2, "local order={p}");
}
#[test]
fn endpoint_admission_not_hidden_by_admissible_midpoint() {
    let cfg = fixture();
    let grid = Grid {
        nodes: vec![],
        intervals: 0,
        base: 128,
        order: 2,
    };
    let old = state(&cfg, &grid, 300., [0.4, 0.1, 0.1]);
    let saved = old.clone();
    let end = old.s + cfg.max_dln_a;
    let p = cfg.background.at_ln_a(end).unwrap();
    let mut bad = old.y;
    bad[0] = 1.1;
    let mid = std::array::from_fn(|i| (old.y[i] + bad[i]) * 0.5);
    assert!(material::rhs(mid, p).is_ok());
    assert!(coupled::evaluate(&cfg, &grid, &old, end, p, bad).is_err());
    assert_eq!(old, saved);
}
#[test]
fn refined_lattice_preserves_old_phases_without_regridding() {
    let cfg = fixture();
    let original = Grid::new(&cfg, 512, 4).unwrap();
    for m in [16, 32, 64] {
        for phase in 0..=3 {
            assert_eq!(
                radiation::time_at(&cfg, phase * m, 3 * m).to_bits(),
                radiation::time_at(&cfg, phase, 3).to_bits()
            );
        }
        let again = Grid::new(&cfg, 512, 4).unwrap();
        assert_eq!(original.nodes, again.nodes);
    }
}
#[test]
fn actual_adiabatic_fixed_endpoint_global_order2() {
    let mut cfg = fixture();
    cfg.fractions = [0.; 3];
    cfg.max_dln_a = 0.1;
    let grid = Grid {
        nodes: vec![],
        intervals: 0,
        base: 128,
        order: 2,
    };
    let initial = State::new(&cfg, &grid).unwrap();
    let mut errors = vec![];
    let endpoint = cfg.start + 0.1;
    for m in [1, 2, 4, 8] {
        let mut s = initial.clone();
        for i in 1..=m {
            let end = cfg.start + (endpoint - cfg.start) * i as f64 / m as f64;
            s = coupled::advance(&cfg, &grid, &s, end, initial.y[3]).unwrap();
        }
        let e = (s.y[3] / initial.y[3] - (-2. * (endpoint - cfg.start)).exp()).abs();
        errors.push(e);
        println!("ADIABATIC_GLOBAL m={m} error={e:.17e}");
    }
    let p = (errors[2] / errors[3]).log2();
    assert!(p > 1.8 && p < 2.2, "p={p}");
}
#[test]
fn spectral_grid_reports_used_entries_and_allocated_capacity_separately() {
    let cfg = fixture();
    for order in [2, 4] {
        let grid = Grid::new(&cfg, 512, order).unwrap();
        println!("GRID_ALLOCATION order={order} distinct_nodes={} used_coordinate_slots={} allocated_coordinate_slots={} allocated_coordinate_bytes={}",grid.nodes.len(),2*grid.nodes.len(),2*grid.nodes.capacity(),std::mem::size_of::<(f64,f64)>()*grid.nodes.capacity());
        assert!(grid.nodes.len() <= 4096);
        assert!(grid.nodes.capacity() >= grid.nodes.len());
    }
}
