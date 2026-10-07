use rei_microphysics::{igm_config::parse_config, igm_state::IgmGasState};
use short_hhe_control::{
    material::{self, MaterialOwners},
    photo_delta,
    radiation::{self, Grid},
    v2,
};
fn fixture() -> rei_microphysics::igm_config::HistoryConfig {
    parse_config(include_str!(
        "../../../../docs/research_program/igm_next_nodes_20261007/long-flrw/radau-p128-o2/config.cfg"
    ))
    .unwrap()
}
fn close(a: f64, b: f64) {
    assert!(
        (a - b).abs() <= 2e-12 * a.abs().max(b.abs()).max(1e-290),
        "a={a:e} b={b:e}"
    )
}
#[test]
fn owner_identity_mutants() {
    let a = [0.003, 0.002, 0.0005];
    let b = [1e-13, 1.1e-13, 5e-14];
    let f = 0.08;
    let old = [2e-4, 0., 0., 1e-14];
    let d = photo_delta(a, b, f);
    let y = std::array::from_fn(|i| old[i] + d[i]);
    let correct = material::binding(y, f) - material::binding(old, f) + d[3];
    let absorbed = b.iter().sum::<f64>();
    close(correct, absorbed);
    let wrong = photo_delta(a, b, 1.);
    let wrongy = std::array::from_fn(|i| old[i] + wrong[i]);
    assert!(
        (material::binding(wrongy, f) - material::binding(old, f) + wrong[3] - absorbed).abs()
            > 2e-12 * absorbed,
        "wrong fHe escaped"
    );
    let cutoff = [13.6, 24.59, 54.42];
    let cutoff_heat = (0..3)
        .map(|i| b[i] - v2::EPS * cutoff[i] * a[i])
        .sum::<f64>();
    assert!(
        (correct - d[3] + cutoff_heat - absorbed).abs() > 2e-12 * absorbed,
        "CHI/CUTOFF exchange escaped"
    );
    assert!(
        (d[3] - absorbed).abs() > 2e-12 * absorbed,
        "omitted binding escaped"
    );
    let count_mean_heat = a.iter().sum::<f64>() * (40. - 13.6) * v2::EPS;
    assert!(
        (correct - d[3] + count_mean_heat - absorbed).abs() > 2e-12 * absorbed,
        "count-mean heat escaped"
    );
    let q = v2::kernel(0.0, 2.0, [0.2, 0.3, 0.1], 1e-4, 80.).unwrap();
    close(q.n + q.an.iter().sum::<f64>(), q.qn);
    close(q.u + q.be.iter().sum::<f64>() + q.red, q.qe);
    assert!(
        (q.n + q.an.iter().sum::<f64>() - 1.01 * q.qn).abs() > 1e-10 * q.qn,
        "source mismatch escaped"
    );
}
#[test]
fn material_owner_omission_mutants() {
    let cfg = fixture();
    let p = cfg.background.at_ln_a(cfg.start).unwrap();
    let g =
        IgmGasState::from_temperature([0.1, 0.05, 0.01], p.n_h_cm3, p.n_he_cm3, 10000.).unwrap();
    let r = material::rhs(material::values(&g), p).unwrap();
    let m = MaterialOwners::stage(r, p, 2e-4).unwrap();
    let sum = m.nonphoto_thermal + m.nonphoto_binding + m.escape + m.work + m.cmb;
    let scale = m.escape + m.work + m.cmb.abs();
    assert!(sum.abs() < 2e-12 * scale);
    for owner in [m.escape, m.work, m.cmb] {
        assert!((sum - owner).abs() > 2e-12 * scale, "omitted owner escaped")
    }
}
#[test]
fn immutable_rejection_and_tail_admission() {
    let cfg = fixture();
    let p = cfg.background.at_ln_a(cfg.start).unwrap();
    let g = IgmGasState::from_temperature(cfg.fractions, p.n_h_cm3, p.n_he_cm3, cfg.temperature_k)
        .unwrap();
    let y = material::values(&g);
    let grid = Grid::new(&cfg, 128, 2).unwrap();
    let density = vec![0.; grid.nodes.len()];
    let before = density.clone();
    let bad = [-0.1, y[1], y[2], y[3]];
    assert!(
        radiation::transaction(&cfg, &grid, p, bad, cfg.start, cfg.start + 2e-4, &density).is_err()
    );
    assert_eq!(density, before);
    assert_eq!(material::values(&g), y);
    let mut acc = v2::Owners::default();
    let saved = acc;
    let tail = v2::Owners {
        n: 0.,
        u: 0.,
        ln_n: Some(-800.),
        ln_u: Some(-820.),
        ..Default::default()
    };
    assert!(v2::try_add_scaled(&mut acc, tail, 1.).is_err());
    assert_eq!(acc, saved);
    let underflow = v2::Owners {
        n: f64::MIN_POSITIVE,
        u: f64::MIN_POSITIVE,
        ..Default::default()
    };
    assert!(v2::try_add_scaled(&mut acc, underflow, 0.25).is_err());
    assert_eq!(acc, saved);
    assert!(radiation::characteristic(&cfg, p, y, 1.0, cfg.start, cfg.start, 0.).is_err());
}
#[test]
fn exact_upper_front_is_zero_even_zero_absorber() {
    let cfg = fixture();
    let end = cfg.start + 2e-4;
    let p = cfg.background.at_ln_a(end).unwrap();
    let g = IgmGasState::from_temperature([1., 0., 1.], p.n_h_cm3, p.n_he_cm3, 30.).unwrap();
    let y = material::values(&g);
    let front = end + cfg.source.energy_max_ev.ln();
    for eta in [front, front + 0.01] {
        let q = radiation::characteristic(&cfg, p, y, eta, cfg.start, end, 0.).unwrap();
        assert_eq!(q.n, 0.);
        assert_eq!(q.u, 0.);
    }
    let grid = Grid::new(&cfg, 128, 2).unwrap();
    let density = vec![1e-5; grid.nodes.len()];
    let gamma = radiation::gamma(&grid, end, &density, p).unwrap();
    assert!(gamma.into_iter().all(|v| v > 0.));
}
#[test]
fn inherited_cutoff_roundoff_rejects_without_mutation() {
    let cfg = fixture();
    let p = cfg.background.at_ln_a(cfg.start + 2e-4).unwrap();
    let g = IgmGasState::from_temperature(cfg.fractions, p.n_h_cm3, p.n_he_cm3, 30.).unwrap();
    let y = material::values(&g);
    let eta = 6.37405404392686115e-1;
    let b = eta - 24.59f64.ln();
    let result = v2::kernel(0., 1., [0., 1., 0.], b - cfg.start, (eta - cfg.start).exp());
    assert!(
        result
            .as_ref()
            .err()
            .is_some_and(|e| e.contains("unsplit absorption cutoff")),
        "boundary failure changed: {result:?}"
    );
    assert_eq!(material::values(&g), y);
}
#[test]
fn rejected_nonlinear_candidate_preserves_whole_state_and_ledgers() {
    use short_hhe_control::coupled::{advance, evaluate, State};
    let cfg = fixture();
    let grid = Grid::new(&cfg, 128, 2).unwrap();
    let mut old = State::new(&cfg, &grid).unwrap();
    let p = cfg.background.at_ln_a(cfg.start + 2e-4).unwrap();
    let initial = old.y[3] + material::binding(old.y, p.n_he_cm3 / p.n_h_cm3);
    let saved = old.clone();
    let mut bad = old.y;
    bad[3] = -bad[3];
    assert!(evaluate(&cfg, &grid, &old, cfg.start + 2e-4, p, bad).is_err());
    assert_eq!(old, saved);
    // Corrupt only the private negative-control incoming ledger. A converged gas
    // candidate must still reject the independent full original balance gate.
    old.radiation.qn = 0.001;
    old.radiation.qe = 1e-13;
    let before = old.clone();
    let failure = advance(&cfg, &grid, &old, cfg.start + 2e-4, initial).unwrap_err();
    assert!(failure.contains("original budget rejects"), "{failure}");
    assert_eq!(old, before);
}
