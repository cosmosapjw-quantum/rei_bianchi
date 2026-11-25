use rei_microphysics::{general_ray::canonical_ray, CharacteristicRay, GeometrySnapshot};
#[test]
fn diagonal_and_rotated_coframe() {
    let n = [0.6, 0., 0.8];
    let a = GeometrySnapshot::new([1.; 3], [0.; 3]).unwrap();
    let b = GeometrySnapshot::new([2., 3., 4.], [0.; 3]).unwrap();
    let ray = CharacteristicRay::new(1., n, 0.).unwrap();
    let p = ray.pullback(&a, &b).unwrap();
    let r = canonical_ray(
        [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]],
        [[2., 0., 0.], [0., 3., 0.], [0., 0., 4.]],
        n,
    )
    .unwrap();
    assert!((r.energy_scale - p.energy_ev).abs() < 1e-14);
    assert!((r.jacobian - ray.solid_angle_jacobian(&a, &b).unwrap()).abs() < 1e-14);
    let r = canonical_ray(
        [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]],
        [[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]],
        n,
    )
    .unwrap();
    assert_eq!(r.energy_scale, 1.);
    assert_eq!(r.jacobian, 1.);
    assert_eq!(r.direction, [0., 0.6, 0.8]);
}
