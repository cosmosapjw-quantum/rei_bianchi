use rei_microphysics::coupled_primary::PrimaryPacket;
use rei_microphysics::rux_adapter::*;

fn input() -> ScenarioInput {
    ScenarioInput {
        clock: ProperClock {
            origin: "manufactured_epoch".into(),
            seconds_since_origin: 2.0,
        },
        hydrogen_density: HydrogenDensity::ProperCm3(1e-4),
        helium_to_hydrogen: 0.083,
        mean_hubble_per_s: 0.0,
        fractions: [0.2, 0.1, 0.01],
        thermal_ev_per_h: 6.0,
        escape_ev_per_h: 0.0,
        packets: vec![PrimaryPacket {
            energy_ev: 35.0,
            per_h: 0.005,
        }],
        source_role: PhotonSourceRole::InitialStock,
        closure: PrimaryClosure::HomogeneousCaseAEscape,
        event_owner: EventOwner::PrimaryStage,
    }
}

#[test]
fn explicit_density_and_clock_seams() {
    let (proper, _) = bind_primary(input()).unwrap();
    let mut changed = input();
    changed.hydrogen_density = HydrogenDensity::ComovingCm3 {
        value: 1.25e-5,
        scale_factor: 0.5,
    };
    let (converted, _) = bind_primary(changed).unwrap();
    assert_eq!(proper.n_h_cm3, converted.n_h_cm3);
    let mut absent = input();
    absent.clock.origin = "".into();
    assert!(bind_primary(absent).is_err());
}

#[test]
fn source_and_event_ownership_require_callbacks() {
    let mut source = input();
    source.source_role = PhotonSourceRole::ExternalEmissivity;
    assert_eq!(
        bind_primary(source).unwrap_err().code(),
        "MISSING_AUTHORITY"
    );
    let mut uvb = input();
    uvb.source_role = PhotonSourceRole::ImposedUvb;
    assert_eq!(bind_primary(uvb).unwrap_err().code(), "MISSING_AUTHORITY");
    let mut owner = input();
    owner.event_owner = EventOwner::External;
    assert_eq!(bind_primary(owner).unwrap_err().code(), "MISSING_AUTHORITY");
}
