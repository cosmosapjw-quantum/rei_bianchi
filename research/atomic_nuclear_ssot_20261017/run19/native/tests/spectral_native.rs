#[path = "../examples/common/mod.rs"]
mod common;
use rei_iso_couple_reference::{
    bass_source_bridge::BassSourceBridge, spectral_native::refine_first_cell,
};
#[test]
fn actual_bass_first_cell_contains_crossing_photons() {
    let g = common::load("SIGNED_MINUS", 121);
    let (_, cfg, s) = common::fixture(&g, 0.7);
    let cell = s.spectral_cells[0];
    let b = BassSourceBridge::new(s, g.clone(), 2.7255).unwrap();
    let tb = g.point_at_x(0.70002).unwrap().time_s;
    let end = g.point_at_x(0.7004).unwrap();
    let old = b.source_births(tb, 1e8).unwrap();
    let new = refine_first_cell(&old, cell, &g, end.time_s, cfg.deuterium.chi_d_ev(), 1).unwrap();
    assert!(
        new.len() > old.len(),
        "cell0 must be replaced, not passed through"
    );
    assert!(
        new.iter()
            .any(|q| q.energy_at_birth_ev > cfg.deuterium.chi_d_ev()
                && q.ray_at(&end.snapshot().unwrap()).unwrap().energy_ev
                    < cfg.deuterium.chi_d_ev())
    );
}
#[test]
fn other_47_cells_and_raywise_counts_unchanged() {
    let g = common::load("SIGNED_MINUS", 121);
    let (_, cfg, s) = common::fixture(&g, 0.7);
    let cell = s.spectral_cells[0];
    let b = BassSourceBridge::new(s, g.clone(), 2.7255).unwrap();
    let tb = g.point_at_x(0.70002).unwrap().time_s;
    let end = g.point_at_x(0.7004).unwrap();
    let old = b.source_births(tb, 1e8).unwrap();
    for m in [1, 2] {
        let new =
            refine_first_cell(&old, cell, &g, end.time_s, cfg.deuterium.chi_d_ev(), m).unwrap();
        let retained: Vec<_> = new.iter().filter(|x| x.spectral_index != 0).collect();
        let orig: Vec<_> = old.iter().filter(|x| x.spectral_index != 0).collect();
        assert_eq!(retained.len(), orig.len());
        for (x, y) in retained.into_iter().zip(orig) {
            assert_eq!(format!("{x:?}"), format!("{y:?}"));
        }
        for p in old.iter().filter(|x| x.spectral_index == 0) {
            let kids: Vec<_> = new
                .iter()
                .filter(|x| x.spectral_index == 0 && x.angular_index == p.angular_index)
                .collect();
            let count: f64 = kids.iter().map(|x| x.n_comoving_m3).sum();
            let energy: f64 = kids
                .iter()
                .map(|x| x.n_comoving_m3 * x.energy_at_birth_ev)
                .sum();
            assert!((count / p.n_comoving_m3 - 1.).abs() < 3e-12);
            assert!((energy / count - cell.energy_ev).abs() < 1e-10);
            assert!(
                kids.iter()
                    .all(|x| x.birth_time_s.to_bits() == p.birth_time_s.to_bits()
                        && x.direction_at_birth == p.direction_at_birth)
            );
        }
    }
}
#[test]
fn invalid_subdivision_rejected() {
    let g = common::load("SIGNED_MINUS", 121);
    let (_, cfg, s) = common::fixture(&g, 0.7);
    for m in [0, 65] {
        assert!(
            refine_first_cell(
                &[],
                s.spectral_cells[0],
                &g,
                g.point_at_x(0.7004).unwrap().time_s,
                cfg.deuterium.chi_d_ev(),
                m
            )
            .is_err()
        );
    }
}
