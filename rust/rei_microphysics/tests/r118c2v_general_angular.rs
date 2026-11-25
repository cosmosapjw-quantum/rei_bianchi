use rei_microphysics::general_angular::GeneralAngular;
#[test]
fn reference_mapping_and_isotropic_source() {
    let id = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]];
    let c = [[1.3, 0., 0.], [0., 1.3, 0.], [0., 0., 0.45]];
    let a = GeneralAngular::new(id, c, 16, 32).unwrap();
    let s = a.source_at(c).unwrap();
    assert!((s.raw_area - 1.).abs() < 1e-13);
    assert!(s.dipole.iter().all(|x| x.abs() < 1e-13));
    for i in 0..3 {
        for j in 0..3 {
            assert!((s.pressure[i][j] - if i == j { 1. / 3. } else { 0. }).abs() < 1e-13);
        }
    }
    let e = vec![1.; a.len()];
    let p = a.moments_at(c, &e).unwrap();
    assert!((p.energy - p.pressure[0][0] - p.pressure[1][1] - p.pressure[2][2]).abs() < 1e-11);
}
