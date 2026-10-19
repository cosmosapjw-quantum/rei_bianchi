use rei_iso_couple_reference::{
    HHeModel,
    bass_geometry::BassPoint,
    deuterium_atomic::DAtomicProvider,
    full_network::NetworkConfig,
    retarded_joint::{RetardedContext, rhs_x},
};
fn conf() -> NetworkConfig {
    let h = HHeModel::controlled_fixture().threshold_ev[0];
    let mut c = NetworkConfig::source_bound(
        DAtomicProvider::new(h, h + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        "MD14_Z002_FESC_BB50K_13P6_100_V1",
    );
    c.use_photo = false;
    c
}
#[test]
fn comoving_adiabatic_work_not_proper_volume_cooling() {
    let c = conf();
    let mut u = [0.; 14];
    u[1] = 100.;
    u[2] = 10.;
    u[13] = 2e-17;
    let ctx = RetardedContext {
        point: BassPoint {
            x: 0.72,
            a: 0.1,
            b: 0.,
            h: 1e-16,
            s: 0.,
            time_s: 1e12,
        },
        a_ref: 0.08,
        cohorts: &[],
        active: 0,
        config: &c,
        gas_mask: 0,
        photo: false,
        expansion: true,
    };
    let q = rhs_x(&u, &[], &ctx).unwrap();
    assert_eq!(q[1], 0.);
    assert_eq!(q[13], -2. * u[13]);
    assert_eq!(q[35], 2. * u[13]);
}
use rei_iso_couple_reference::{
    bianchi_i::GeometrySnapshot,
    full_network::EV_J,
    full_network::FullState,
    isotope_state::IsotopeNumberState,
    joint_slab::{SlabSpectrum, joint_rhs},
    mixture_eos::MixtureState,
    source_age::Cohort,
};
fn gas() -> [f64; 14] {
    let mut u = [0.; 14];
    u[1] = 100.;
    u[2] = 10.;
    u[3] = 0.003;
    u[4] = 0.0003;
    u[10] = 8.;
    u[11] = 1.;
    u[12] = 1.;
    u[13] = 3e-17;
    u
}
fn point() -> BassPoint {
    BassPoint {
        x: 0.,
        a: 0.1,
        b: 0.,
        h: 1e-16,
        s: 1e-18,
        time_s: 1e12,
    }
}
fn ray(mu: f64) -> Cohort {
    Cohort {
        birth_time_s: 0.,
        birth_geometry: GeometrySnapshot::new([0.1; 3], [1e-16; 3]).unwrap(),
        energy_at_birth_ev: 70.,
        direction_at_birth: [(1. - mu * mu).sqrt(), 0., mu],
        n_comoving_m3: 0.001,
        spectral_index: 0,
        angular_index: 0,
    }
}
#[test]
fn all_four_photo_edges_and_total_work_energy_identity() {
    let c = conf();
    let cs = [ray(0.3)];
    let ctx = RetardedContext {
        point: point(),
        a_ref: 0.1,
        cohorts: &cs,
        active: 1,
        config: &c,
        gas_mask: 7,
        photo: true,
        expansion: true,
    };
    let u = gas();
    let d = 0.2;
    let q = rhs_x(&u, &[d], &ctx).unwrap();
    let p = 28;
    let chi = HHeModel::controlled_fixture().threshold_ev;
    for j in 0..4 {
        assert!(q[p + j] > 0.);
    }
    let chemical = EV_J
        * (chi[0] * q[2]
            + c.deuterium.chi_d_ev() * q[4]
            + chi[1] * q[11]
            + (chi[1] + chi[2]) * q[12]);
    let photo_loss = 70. * EV_J * cs[0].n_comoving_m3 / 0.1_f64.powi(3) * (-d).exp() * q[27];
    // Radiation redshift is -W_photon', absorption is -E N tau'.
    let residual = q[13] + q[14] + q[15] + chemical + q[p + 8] - photo_loss;
    let scale = q[13].abs() + chemical.abs() + photo_loss.abs();
    assert!(residual.abs() < 2e-14 * scale);
    assert!(q[p + 9] > 0.);
}
#[test]
fn static_operator_matches_parent_joint_slab() {
    let c = conf();
    let cs = [ray(0.)];
    let u = gas();
    let mut n = [0.; 13];
    n.copy_from_slice(&u[..13]);
    let mut cc = c;
    cc.cmb_temperature_k = 2.7255 / 0.1;
    let full = FullState {
        gas: MixtureState {
            nuclei: IsotopeNumberState::new(n).unwrap(),
            thermal_j_m3: u[13],
        },
        photon_bins: vec![],
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
        elapsed_s: 0.,
    };
    let ctx = RetardedContext {
        point: point(),
        a_ref: 0.1,
        cohorts: &cs,
        active: 1,
        config: &c,
        gas_mask: 7,
        photo: true,
        expansion: false,
    };
    let q = rhs_x(&u, &[0.], &ctx).unwrap();
    let count = cs[0].n_comoving_m3 / 0.1_f64.powi(3);
    let sp = SlabSpectrum::native(vec![70.], vec![0.], &c).unwrap();
    let old = joint_rhs(&full, &cc, &sp, &[count], 7, true).unwrap();
    for i in 0..27 {
        assert!((q[i] * point().h - old[i]).abs() < 1e-13 * (old[i].abs() + 1e-50));
    }
    assert!((-count * q[27] * point().h - old[27]).abs() < 1e-13 * old[27].abs());
}
#[test]
fn inactive_births_have_no_absorption_or_work() {
    let c = conf();
    let cs = [ray(0.)];
    let ctx = RetardedContext {
        point: point(),
        a_ref: 0.1,
        cohorts: &cs,
        active: 0,
        config: &c,
        gas_mask: 0,
        photo: true,
        expansion: true,
    };
    let q = rhs_x(&gas(), &[0.], &ctx).unwrap();
    assert_eq!(q[27], 0.);
    assert_eq!(q[28], 0.);
    assert_eq!(q[37], 0.);
}
#[test]
fn negative_gas_and_duplicate_photo_owner_rejected() {
    let c = conf();
    let mut u = gas();
    u[1] = -1.;
    let ctx = RetardedContext {
        point: point(),
        a_ref: 0.1,
        cohorts: &[],
        active: 0,
        config: &c,
        gas_mask: 0,
        photo: true,
        expansion: true,
    };
    assert!(rhs_x(&u, &[], &ctx).is_err());
    let mut bad = c;
    bad.use_photo = true;
    let ctx = RetardedContext {
        config: &bad,
        ..ctx
    };
    assert!(rhs_x(&gas(), &[], &ctx).is_err());
}
#[test]
fn reflected_rays_share_depth_and_add_scalar_events() {
    let c = conf();
    let cs = [ray(0.6), ray(-0.6)];
    let ctx = RetardedContext {
        point: point(),
        a_ref: 0.1,
        cohorts: &cs,
        active: 2,
        config: &c,
        gas_mask: 0,
        photo: true,
        expansion: false,
    };
    let q = rhs_x(&gas(), &[0.3, 0.3], &ctx).unwrap();
    assert_eq!(q[27], q[28]);
    let mut merged = ray(0.6);
    merged.n_comoving_m3 *= 2.;
    let merged = [merged];
    let ctx2 = RetardedContext {
        cohorts: &merged,
        active: 1,
        ..ctx
    };
    let r = rhs_x(&gas(), &[0.3], &ctx2).unwrap();
    for i in 0..27 {
        assert!((q[i] - r[i]).abs() <= 8. * f64::EPSILON * q[i].abs().max(r[i].abs()));
    }
}
#[test]
fn impossible_birth_clock_and_dimension_are_rejected() {
    let c = conf();
    let mut cs = [ray(0.)];
    cs[0].birth_time_s = 2e12;
    let ctx = RetardedContext {
        point: point(),
        a_ref: 0.1,
        cohorts: &cs,
        active: 1,
        config: &c,
        gas_mask: 0,
        photo: true,
        expansion: true,
    };
    assert!(rhs_x(&gas(), &[0.], &ctx).is_err());
    assert!(rhs_x(&gas(), &[], &ctx).is_err());
}
