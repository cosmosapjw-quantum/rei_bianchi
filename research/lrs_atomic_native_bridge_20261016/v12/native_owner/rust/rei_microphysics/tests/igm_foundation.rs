use rei_microphysics::coupled_primary::PrimaryPacket;
use rei_microphysics::igm_background::*;
use rei_microphysics::igm_state::*;
use rei_microphysics::{
    CharacteristicRay, HHeModel, PhotonNode, PhotonPacket, RadiationState, MPC_CM,
};

fn config() -> FlatFlrwConfig {
    FlatFlrwConfig {
        h0_per_s: 2e-18,
        omega_r: 0.01,
        omega_m: 0.29,
        omega_b: 0.04,
        omega_lambda: 0.70,
        helium_mass_fraction: 0.24,
        tcmb0_k: 3.0,
        ln_a_min: 0.125_f64.ln(),
        ln_a_max: 0.0,
        parameter_source: "manufactured-test-v1".into(),
    }
}
fn close(a: f64, b: f64) {
    assert!(a.is_finite() && b.is_finite());
    assert!((a - b).abs() <= 1e-12 * b.abs(), "{a:e} != {b:e}");
}

#[test]
fn background_normalization_and_geometry() {
    let result = FlatFlrwBackground::new(config());
    assert!(
        result.is_ok(),
        "valid explicit FLRW configuration must be supported: {result:?}"
    );
    let bg = result.unwrap();
    let p = bg.at_ln_a(0.0).unwrap();
    close(p.hubble_per_s, 2e-18);
    close(p.a, 1.0);
    assert_eq!(p.redshift, 0.0);
    let rho = 3.0 * 4e-36 / (8.0 * std::f64::consts::PI * 6.67430e-8);
    close(p.n_h_cm3, 0.76 * 0.04 * rho / 1.67262192595e-24);
    close(p.n_he_cm3 / p.n_h_cm3, 0.24 / (4.0 * 0.76));
    close(bg.n_h_comoving_cm3(), p.n_h_cm3);
    let q = bg.at_redshift(3.0).unwrap();
    close(q.a, 0.25);
    close(
        q.hubble_per_s,
        2e-18 * (0.01_f64 * 256.0 + 0.29 * 64.0 + 0.70).sqrt(),
    );
    close(q.n_h_cm3 / p.n_h_cm3, 64.0);
    close(q.n_he_cm3 / p.n_he_cm3, 64.0);
    close(q.tcmb_k, 12.0);
    close(q.dt_dln_a_s, 1.0 / q.hubble_per_s);
    close(q.dt_dz_s, -1.0 / (4.0 * q.hubble_per_s));
    assert_eq!(q.geometry.scale_factors, [q.a; 3]);
    assert_eq!(q.geometry.hubble_per_s, [q.hubble_per_s; 3]);
    close(q.geometry.volume_factor().unwrap(), 1.0 / 64.0);
}
#[test]
fn limiting_backgrounds_and_zero_helium() {
    for (r, m, l, ratio) in [
        (0.0, 1.0, 0.0, 8.0),
        (0.75, 0.25, 0.0, (0.75_f64 * 256.0 + 0.25 * 64.0).sqrt()),
    ] {
        let mut c = config();
        c.omega_r = r;
        c.omega_m = m;
        c.omega_lambda = l;
        c.helium_mass_fraction = 0.0;
        let bg = FlatFlrwBackground::new(c).unwrap();
        let p = bg.at_redshift(3.0).unwrap();
        close(p.hubble_per_s / 2e-18, ratio);
        assert_eq!(p.n_he_cm3, 0.0);
    }
}
#[test]
fn rejects_bad_background_parameters_and_coordinates() {
    let mut cases = Vec::new();
    for bad in [f64::NAN, f64::INFINITY, -1.0, 0.0, 1e308, 1e-308] {
        let mut c = config();
        c.h0_per_s = bad;
        cases.push(c);
    }
    for bad in [f64::NAN, f64::INFINITY, -0.1, 1.0, 1.1] {
        let mut c = config();
        c.helium_mass_fraction = bad;
        cases.push(c);
    }
    for bad in [f64::NAN, f64::INFINITY, -0.1] {
        let mut c = config();
        c.omega_r = bad;
        cases.push(c);
    }
    for bad in [f64::NAN, f64::INFINITY, -0.1, 0.5] {
        let mut c = config();
        c.omega_lambda = bad;
        cases.push(c);
    }
    for bad in [f64::NAN, 0.0, -0.1, 0.3] {
        let mut c = config();
        c.omega_b = bad;
        cases.push(c);
    }
    for bad in [f64::NAN, 0.0, -1.0, f64::INFINITY] {
        let mut c = config();
        c.tcmb0_k = bad;
        cases.push(c);
    }
    for bad in [f64::NAN, 1.0, -1000.0] {
        let mut c = config();
        c.ln_a_min = bad;
        cases.push(c);
    }
    let mut c = config();
    c.parameter_source = "  ".into();
    cases.push(c);
    for c in cases {
        assert!(
            FlatFlrwBackground::new(c.clone()).is_err(),
            "accepted {c:?}"
        );
    }
    let bg = FlatFlrwBackground::new(config()).unwrap();
    for x in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY, 0.1, -3.0] {
        assert!(bg.at_ln_a(x).is_err());
    }
    for z in [f64::NAN, f64::INFINITY, -1.0, -2.0, 8.0] {
        assert!(bg.at_redshift(z).is_err());
    }
}
#[test]
fn gas_boundaries_eos_and_adiabatic_law() {
    for f in [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 1.0],
        [0.2, 0.3, 0.7],
    ] {
        for he in [0.0, 0.08] {
            let result = IgmGasState::from_temperature(f, 1e-4, he * 1e-4, 17.0);
            assert!(
                result.is_ok(),
                "valid simplex boundary must be supported: {result:?}"
            );
            let s = result.unwrap();
            let e = s.eos(1e-4, he * 1e-4).unwrap();
            close(e.temperature_k, 17.0);
            close(
                e.electron_density_cm3,
                1e-4 * (f[0] + he * (f[1] + 2.0 * f[2])),
            );
            close(
                e.u_erg_cm3,
                1.5 * HHeModel::controlled_fixture().kb_erg_k
                    * 17.0
                    * (1e-4 + he * 1e-4 + e.electron_density_cm3),
            );
            let next = s.adiabatic_to(0.25, 0.5).unwrap();
            assert_eq!(s.fractions, next.fractions);
            close(
                next.eos(1e-4 / 8.0, he * 1e-4 / 8.0).unwrap().temperature_k,
                17.0 / 4.0,
            );
        }
    }
}
#[test]
fn rejects_bad_gas_and_extreme_arithmetic() {
    for f in [
        [-1e-10, 0.0, 0.0],
        [1.1, 0.0, 0.0],
        [0.0, 0.7, 0.4],
        [0.0, -0.1, 0.0],
        [0.0, 0.0, f64::NAN],
    ] {
        assert!(IgmGasState::new(f, 1e-14).is_err());
    }
    for w in [0.0, -1.0, f64::NAN, f64::INFINITY] {
        assert!(IgmGasState::new([0.0; 3], w).is_err());
    }
    let s = IgmGasState::new([0.0; 3], 1e-14).unwrap();
    for h in [0.0, -1.0, f64::NAN, f64::INFINITY, 1e-310] {
        assert!(s.eos(h, 0.0).is_err());
    }
    for he in [-1.0, f64::NAN, f64::INFINITY] {
        assert!(s.eos(1e-4, he).is_err());
    }
    for t in [0.0, -1.0, f64::NAN, f64::INFINITY, 1e-310] {
        assert!(IgmGasState::from_temperature([0.0; 3], 1e-4, 0.0, t).is_err());
    }
    assert!(IgmGasState::new([0.0; 3], f64::MAX)
        .unwrap()
        .eos(10.0, 0.0)
        .is_err());
    for a in [0.0, -1.0, f64::NAN, f64::INFINITY, 1e-300] {
        assert!(s.adiabatic_to(1.0, a).is_err());
    }
}
#[test]
fn photon_units_and_exact_transport() {
    let bg = FlatFlrwBackground::new(config()).unwrap();
    let n0 = bg.n_h_comoving_cm3();
    for count in [0.0, 0.1, 2.0] {
        let p = PrimaryPacket {
            energy_ev: 70.0,
            per_h: count,
        };
        let packet = primary_to_photon_packet(&p, n0, [0.0, 0.6, 0.8]).unwrap();
        close(packet.comoving_count_cm3, n0 * count);
        close(photon_packet_to_primary(&packet, n0).unwrap().per_h, count);
        let node = primary_to_photon_node(&p, n0).unwrap();
        close(node.n_comoving_per_cmpc3, n0 * count * MPC_CM.powi(3));
        close(photon_node_to_primary(&node, n0).unwrap().per_h, count);
        let g0 = bg.at_redshift(7.0).unwrap();
        let g1 = bg.at_redshift(3.0).unwrap();
        let rad = RadiationState::new(g0.geometry, vec![packet]).unwrap();
        let out = rad.transport(g1.geometry).unwrap();
        close(out.packets[0].ray.energy_ev, 35.0);
        assert_eq!(
            out.comoving_photon_count().unwrap(),
            rad.comoving_photon_count().unwrap()
        );
        close(
            photon_packet_to_primary(&out.packets[0], n0).unwrap().per_h,
            count,
        );
        close(out.proper_photon_density_cm3().unwrap(), count * g1.n_h_cm3);
    }
    close(w_erg_per_h_to_ev(1.602176634e-12).unwrap(), 1.0);
    close(w_ev_per_h_to_erg(1.0).unwrap(), 1.602176634e-12);
    assert_eq!(w_ev_per_h_to_erg(0.0).unwrap(), 0.0);
}
#[test]
fn adapters_reject_invalid_and_unrepresentable_values() {
    let p = PrimaryPacket {
        energy_ev: 1.0,
        per_h: 1.0,
    };
    for n in [0.0, -1.0, f64::NAN, f64::INFINITY] {
        assert!(primary_to_photon_node(&p, n).is_err());
        assert!(primary_to_photon_packet(&p, n, [1.0, 0.0, 0.0]).is_err());
    }
    for x in [-1.0, f64::NAN, f64::INFINITY] {
        assert!(w_ev_per_h_to_erg(x).is_err());
        assert!(w_erg_per_h_to_ev(x).is_err());
    }
    assert!(w_erg_per_h_to_ev(f64::MAX).is_err());
    assert!(w_ev_per_h_to_erg(f64::MIN_POSITIVE).is_err());
    assert!(primary_to_photon_node(&p, f64::MAX).is_err());
    assert!(primary_to_photon_packet(
        &PrimaryPacket {
            energy_ev: 1.0,
            per_h: 1e-200
        },
        1e-200,
        [1.0, 0.0, 0.0]
    )
    .is_err());
    for energy in [0.0, -1.0, f64::NAN, f64::INFINITY] {
        assert!(photon_node_to_primary(
            &PhotonNode {
                energy_ev: energy,
                n_comoving_per_cmpc3: 0.0
            },
            1.0
        )
        .is_err());
    }
    let invalid = PhotonPacket {
        ray: CharacteristicRay {
            energy_ev: 1.0,
            direction: [2.0, 0.0, 0.0],
            occupation: 0.0,
        },
        comoving_count_cm3: 1.0,
    };
    assert!(photon_packet_to_primary(&invalid, 1.0).is_err());
}

#[test]
fn eos_rejects_subnormal_denominator_before_legacy_rounding() {
    let s = IgmGasState::new([0.0; 3], 1e-10).unwrap();
    assert!(
        s.eos(1e-295, 0.0).is_err(),
        "positive subnormal EOS denominator must not silently lose relative precision"
    );
}

#[test]
fn redshift_roundtrips_declared_coordinate_endpoints() {
    for k in 1..1000 {
        let mut c = config();
        c.ln_a_min = -f64::from(k) / 100.0;
        let bg = FlatFlrwBackground::new(c.clone()).unwrap();
        for ln_a in [c.ln_a_min, c.ln_a_max] {
            let p = bg.at_ln_a(ln_a).unwrap();
            let roundtrip = bg.at_redshift(p.redshift);
            assert!(
                roundtrip.is_ok(),
                "declared endpoint {ln_a} rejected at z={}: {roundtrip:?}",
                p.redshift
            );
            close(roundtrip.unwrap().a, p.a);
        }
        assert!(bg
            .at_redshift(bg.at_ln_a(c.ln_a_min).unwrap().redshift + 1e-8)
            .is_err());
    }
}
