use rei_microphysics::{
    axbi_driver::{packet_chemistry_stage, Driver, DriverConfig, PacketStageInput},
    coupled_primary::PrimaryPacket,
    igm_state::{w_erg_per_h_to_ev, IgmGasState},
};
#[test]
fn external_packet_stage_matches_original_driver_at_identical_point() {
    let mut c = DriverConfig::baseline();
    c.end_zbar = 19.999;
    c.energy_subdivisions = 4;
    c.n_mu = 8;
    c.background_panels = 64;
    let (d, mut s) = Driver::new(c).unwrap();
    let nh = d.n_h0_cm3 / s.a.powi(3);
    let nhe = d.n_he0_cm3 / s.a.powi(3);
    for (i, v) in s.photons.iter_mut().enumerate() {
        *v = 1e-8 * (1 + (i % 7)) as f64;
    }
    let packets: Vec<_> = s
        .photons
        .iter()
        .enumerate()
        .map(|(i, &n)| PrimaryPacket {
            energy_ev: d.energies[i % d.energies.len()],
            per_h: n,
        })
        .collect();
    let mut counter = 0;
    let p = packet_chemistry_stage(
        PacketStageInput {
            n_h_cm3: nh,
            n_he_cm3: nhe,
            tcmb_k: 2.7255 / s.a,
        },
        s.gas,
        &packets,
        1e7,
        &mut counter,
        10000,
    )
    .unwrap();
    let mut k = 0;
    d.chemical_stage(&mut s, 1e7, &mut k).unwrap();
    assert_eq!(p.gas.fractions, s.gas.fractions);
    assert_eq!(p.gas.w_erg_per_h, s.gas.w_erg_per_h);
    assert_eq!(p.stocks, s.photons);
    assert_eq!(p.ledgers.photo_events, s.ledgers.photo_events);
    assert_eq!(p.ledgers.escaped_u, s.ledgers.escaped_u);
    assert_eq!(k, counter);
}
#[test]
fn external_packet_support_and_vacuum_are_physical() {
    let nh = 0.001;
    let he = 0.08 * nh;
    let gas = IgmGasState::from_temperature([2e-4, 0., 0.], nh, he, 10.).unwrap();
    let p = PacketStageInput {
        n_h_cm3: nh,
        n_he_cm3: he,
        tcmb_k: 57.,
    };
    let mut n = 0;
    let v = packet_chemistry_stage(
        p,
        gas,
        &[
            PrimaryPacket {
                energy_ev: 13.599,
                per_h: 0.001,
            },
            PrimaryPacket {
                energy_ev: 13.7,
                per_h: 0.001,
            },
        ],
        1e7,
        &mut n,
        10000,
    )
    .unwrap();
    assert_eq!(v.stocks[0], 0.001);
    assert!(v.stocks[1] < 0.001 && v.stocks[1] > 0.);
    assert!(v.gas.fractions[0] > gas.fractions[0]);
    assert!(w_erg_per_h_to_ev(v.gas.w_erg_per_h).unwrap() > 0.);
    assert!(packet_chemistry_stage(
        p,
        gas,
        &[PrimaryPacket {
            energy_ev: 13.7,
            per_h: -1.
        }],
        1.,
        &mut n,
        10000
    )
    .is_err());
}
