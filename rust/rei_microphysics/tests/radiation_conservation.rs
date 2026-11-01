use rei_microphysics::{
    CharacteristicRay, GeometrySnapshot, PhotonGrid, PhotonPacket, RadiationState,
};
fn close(a: f64, b: f64) {
    assert!(a.is_finite() && b.is_finite());
    assert!((a - b).abs() <= 5e-14 * b.abs().max(1e-30), "{a:e}!={b:e}");
}
fn ray(e: f64, d: [f64; 3], n: f64) -> PhotonPacket {
    PhotonPacket::new(CharacteristicRay::new(e, d, 0.7).unwrap(), n).unwrap()
}
#[test]
fn collisionless_number_volume_and_energy_work() {
    let g0 = GeometrySnapshot::new([1.0; 3], [0.0; 3]).unwrap();
    let g1 = GeometrySnapshot::new([2.0, 3.0, 4.0], [0.0; 3]).unwrap();
    let packets = vec![
        ray(40.0, [1.0, 0.0, 0.0], 2.0),
        ray(60.0, [0.0, 1.0, 0.0], 3.0),
        ray(80.0, [0.0, 0.0, 1.0], 4.0),
    ];
    let s = RadiationState::new(g0, packets).unwrap();
    let b = s.transport(g1).unwrap();
    close(s.comoving_photon_count().unwrap(), 9.0);
    close(b.comoving_photon_count().unwrap(), 9.0);
    close(
        b.proper_photon_density_cm3().unwrap() * g1.volume_factor().unwrap(),
        9.0,
    );
    close(b.comoving_energy_ev_cm3().unwrap(), 180.0);
    close(s.comoving_energy_ev_cm3().unwrap(), 580.0);
    for p in &b.packets {
        assert_eq!(p.ray.occupation, 0.7);
        assert!(p.comoving_count_cm3 >= 0.0);
    }
    let f = GeometrySnapshot::new([2.0; 3], [0.0; 3]).unwrap();
    let iso = s.transport(f).unwrap();
    close(iso.proper_photon_density_cm3().unwrap(), 9.0 / 8.0);
    close(iso.comoving_energy_ev_cm3().unwrap(), 290.0);
}
#[test]
fn guard_ownership_and_positive_histogram() {
    let g = GeometrySnapshot::new([1.0; 3], [0.0; 3]).unwrap();
    let state = RadiationState::new(
        g,
        vec![
            ray(5.0, [1.0, 0.0, 0.0], 1.0),
            ray(20.0, [0.0, 1.0, 0.0], 2.0),
            ray(200.0, [0.0, 0.0, 1.0], 3.0),
        ],
    )
    .unwrap();
    let grid = PhotonGrid::new(vec![10.0, 30.0, 100.0], vec![-1.0, 0.0, 1.0], 4).unwrap();
    let b = state.remap(&grid).unwrap();
    close(b.below_count_cm3, 1.0);
    close(b.above_count_cm3, 3.0);
    close(b.below_energy_ev_cm3, 5.0);
    close(b.above_energy_ev_cm3, 600.0);
    close(b.counts_cm3.iter().sum(), 2.0);
    close(b.energy_ev_cm3.iter().sum(), 40.0);
    close(b.total_count().unwrap(), 6.0);
    close(b.total_energy_ev_cm3().unwrap(), 645.0);
    assert!(b
        .counts_cm3
        .iter()
        .chain(&b.energy_ev_cm3)
        .all(|v| v.is_finite() && *v >= 0.0));
}
#[test]
fn declared_midpoint_refinement() {
    let g = GeometrySnapshot::new([1.0; 3], [0.0; 3]).unwrap();
    let direction = [(8.0_f64 / 9.0).sqrt(), 0.0, 1.0 / 3.0];
    let state = RadiationState::new(g, vec![ray(42.0, direction, 1.0)]).unwrap();
    let mut errors = Vec::new();
    for n in [4, 8, 16] {
        let energy = (0..=n).map(|i| 10.0 + 96.0 * i as f64 / n as f64).collect();
        let mu = (0..=n).map(|i| -1.0 + 2.0 * i as f64 / n as f64).collect();
        let grid = PhotonGrid::new(energy, mu, n).unwrap();
        let bins = state.remap(&grid).unwrap();
        let mut energy = 0.0;
        let mut moment = 0.0;
        for k in 0..n {
            for j in 0..n {
                for p in 0..n {
                    let count = bins.counts_cm3[(k * n + j) * n + p];
                    energy += count * (grid.energy_edges_ev[k] + grid.energy_edges_ev[k + 1]) / 2.0;
                    moment += count * (grid.mu_edges[j] + grid.mu_edges[j + 1]) / 2.0;
                }
            }
        }
        let err = (energy - 42.0).abs();
        let angular = (moment - 1.0 / 3.0).abs();
        assert!(err <= 48.0 / n as f64 && angular <= 1.0 / n as f64);
        close(bins.total_energy_ev_cm3().unwrap(), 42.0);
        errors.push((err, angular));
    }
    close(errors[0].0, 4.0);
    close(errors[1].0, 2.0);
    close(errors[2].0, 1.0);
    assert!(
        (errors[0].1 / errors[1].1 - 2.0).abs() < 1e-12
            && (errors[1].1 / errors[2].1 - 2.0).abs() < 1e-12
    );
}
#[test]
fn invalid_grid_and_transaction() {
    assert!(PhotonGrid::new(vec![20.0, 10.0], vec![-1.0, 1.0], 4).is_err());
    assert!(PhotonGrid::new(vec![10.0, 20.0], vec![-0.9, 1.0], 4).is_err());
    assert!(PhotonGrid::new(vec![10.0, 20.0], vec![-1.0, 1.0], 0).is_err());
    assert!(PhotonPacket::new(
        CharacteristicRay::new(20.0, [1.0, 0.0, 0.0], 0.0).unwrap(),
        f64::NAN
    )
    .is_err());
    let g = GeometrySnapshot::new([1.0; 3], [0.0; 3]).unwrap();
    let state = RadiationState::new(g, vec![ray(1e-300, [1.0, 0.0, 0.0], 1.0)]).unwrap();
    let before = state.clone();
    let b = GeometrySnapshot::new([1e100; 3], [0.0; 3]).unwrap();
    assert!(state.transport(b).is_err());
    assert_eq!(state, before);
}
