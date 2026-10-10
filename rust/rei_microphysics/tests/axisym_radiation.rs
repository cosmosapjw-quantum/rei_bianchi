use rei_microphysics::{
    AxisymPhotonLedgerContract, CharacteristicRay, GeometrySnapshot, PhotonPacket, RadiationState,
};
#[test]
fn collisionless_transport_preserves_packet_number() {
    let a = GeometrySnapshot::new([1.; 3], [0.; 3]).unwrap();
    let b = GeometrySnapshot::new([2., 1., 1.], [0.; 3]).unwrap();
    let r = CharacteristicRay::new(20., [1., 0., 0.], 1.).unwrap();
    let s = RadiationState::new(a, vec![PhotonPacket::new(r, 3.).unwrap()]).unwrap();
    let c = AxisymPhotonLedgerContract::new(vec![1., 11., 30.], vec![-1., 0., 1.]).unwrap();
    let out = c.collisionless_step(&s, b).unwrap();
    assert_eq!(out.number_change_cm3, 0.);
    assert!(out.energy_change_ev_cm3 < 0.);
    assert_eq!(out.number_face_transfer_cm3, vec![0., -3., 0.]);
    assert_eq!(out.energy_face_transfer_ev_cm3, vec![0., -33., 0.]);
}
#[test]
fn highest_edge_uses_inside_tie_convention() {
    let a = GeometrySnapshot::new([1.; 3], [0.; 3]).unwrap();
    let b = GeometrySnapshot::new([0.5, 1., 1.], [0.; 3]).unwrap();
    let ray = CharacteristicRay::new(10., [1., 0., 0.], 1.).unwrap();
    let state = RadiationState::new(a, vec![PhotonPacket::new(ray, 3.).unwrap()]).unwrap();
    let contract = AxisymPhotonLedgerContract::new(vec![1., 11., 20.], vec![-1., 1.]).unwrap();
    let out = contract.collisionless_step(&state, b).unwrap();
    assert_eq!(out.transported.packets[0].ray.energy_ev, 20.);
    assert_eq!(out.number_face_transfer_cm3[2], 0.);
}
#[test]
fn face_ledger_preserves_representable_cancellation_residual() {
    let a = GeometrySnapshot::new([1.; 3], [0.; 3]).unwrap();
    let b = GeometrySnapshot::new([0.5, 0.5, 2.], [0.; 3]).unwrap();
    let packets = vec![
        PhotonPacket::new(
            CharacteristicRay::new(1., [1., 0., 0.], 1.).unwrap(),
            2_f64.powi(53),
        )
        .unwrap(),
        PhotonPacket::new(CharacteristicRay::new(1., [1., 0., 0.], 1.).unwrap(), 1.).unwrap(),
        PhotonPacket::new(
            CharacteristicRay::new(2., [0., 0., 1.], 1.).unwrap(),
            2_f64.powi(53),
        )
        .unwrap(),
    ];
    let state = RadiationState::new(a, packets).unwrap();
    let contract = AxisymPhotonLedgerContract::new(vec![0.25, 1.5, 4.], vec![-1., 0., 1.]).unwrap();
    let out = contract.collisionless_step(&state, b).unwrap();
    assert_eq!(out.number_face_transfer_cm3[1], 1.);
    assert_eq!(out.energy_face_transfer_ev_cm3[1], 1.5);
}
