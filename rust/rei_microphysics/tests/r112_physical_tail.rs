use rei_microphysics::bass_ionization::{merge_with_physical_tail, Knot};
#[test]
fn tail_has_single_owner_and_no_forced_ionization() {
    let rec = [Knot { eta: 0., xe: 1.1 }, Knot { eta: 5., xe: 0.01 }];
    let rei = [(20., 0.01), (4., 1.02)];
    let tail = [(4., 1.02), (2., 1.08), (0., 1.12)];
    let (rows, report) = merge_with_physical_tail(&rec, &rei, &tail, 1100., 0.08).unwrap();
    assert_eq!(report.z_low, 4.);
    assert_eq!(report.rei_knots, 2);
    assert_eq!(report.continuation_knots, 2);
    assert_eq!(rows.last().unwrap().xe, 1.12);
    assert!(rows.windows(2).all(|w| w[1].eta > w[0].eta));
    assert!(merge_with_physical_tail(&rec, &rei, &[(4., 1.01), (0., 1.12)], 1100., 0.08).is_err());
    assert!(merge_with_physical_tail(&rec, &rei, &[(4., 1.02), (0., 1.3)], 1100., 0.08).is_err());
    assert!(merge_with_physical_tail(&rec, &rei, &[(4., 1.02), (1., 1.1)], 1100., 0.08).is_err());
}
