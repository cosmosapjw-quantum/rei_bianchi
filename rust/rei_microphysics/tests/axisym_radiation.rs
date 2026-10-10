use rei_microphysics::{
    AxisymPhotonLedgerContract, CharacteristicRay, GeometrySnapshot, PhotonPacket, RadiationState,
};
#[test]
fn collisionless_transport_preserves_packet_number() {
    let a = GeometrySnapshot::new([1.; 3], [0.; 3]).unwrap();
    let b = GeometrySnapshot::new([2., 1., 1.], [0.; 3]).unwrap();
    let r = CharacteristicRay::new(20., [1., 0., 0.], 1.).unwrap();
    let s = RadiationState::new(a, vec![PhotonPacket::new(r, 3.).unwrap()]).unwrap();
    let c = AxisymPhotonLedgerContract::new(vec![1., 10., 30.], vec![-1., 0., 1.]).unwrap();
    let out = c.collisionless_step(&s, b).unwrap();
    assert_eq!(out.number_change_cm3, 0.);
    assert!(out.energy_change_ev_cm3 < 0.);
}
