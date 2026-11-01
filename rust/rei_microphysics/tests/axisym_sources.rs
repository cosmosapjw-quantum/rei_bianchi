use rei_microphysics::{validate_routing, ExcessPartition, PhotonRouting, PrimaryPhotoEvent};
#[test]
fn one_primary_and_closed_excess() {
    let l = PrimaryPhotoEvent {
        rate_m3_s: 2.,
        photon_energy_j: 5.,
        threshold_j: 3.,
        partition: ExcessPartition {
            heat: 0.25,
            secondary_ionization: 0.25,
            excitation: 0.25,
            escape: 0.25,
        },
    }
    .ledger()
    .unwrap();
    assert_eq!(l.photon_loss_m3_s, -2.);
    assert_eq!(l.primary_ionization_m3_s, 2.);
    assert_eq!(l.threshold_power_j_m3_s, 6.);
    assert_eq!(l.excess_power_j_m3_s, 4.);
    assert_eq!(
        l.heat_power_j_m3_s
            + l.secondary_power_j_m3_s
            + l.excitation_power_j_m3_s
            + l.escape_power_j_m3_s,
        4.
    );
}
#[test]
fn rejects_invalid_or_duplicate_ownership() {
    assert!(validate_routing(PhotonRouting::EliminatedByOts, true).is_err());
    assert!(PrimaryPhotoEvent {
        rate_m3_s: 1.,
        photon_energy_j: 1.,
        threshold_j: 2.,
        partition: ExcessPartition {
            heat: 1.,
            secondary_ionization: 0.,
            excitation: 0.,
            escape: 0.
        }
    }
    .ledger()
    .is_err());
}
