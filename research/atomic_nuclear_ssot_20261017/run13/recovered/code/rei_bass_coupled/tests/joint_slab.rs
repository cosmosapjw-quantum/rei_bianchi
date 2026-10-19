use rei_iso_couple_reference::{
    HHeModel,
    deuterium_atomic::DAtomicProvider,
    full_network::{EV_J, FullState, NetworkConfig, SPEED_OF_LIGHT_M_S},
    isotope_state::IsotopeNumberState,
    joint_slab::{SlabSpectrum, joint_rhs},
    mixture_eos::{KB_J_K, MixtureState},
};
fn fixture() -> (FullState, NetworkConfig) {
    let mut n = [0.; 13];
    n[1] = 90.;
    n[2] = 10.;
    n[3] = 0.00225;
    n[4] = 0.00025;
    n[10] = 6.;
    n[11] = 1.5;
    n[12] = 0.5;
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let thermal = 1.5 * KB_J_K * nuclei.thermal_particle_density_all_thermal_m3().unwrap() * 1e4;
    let s = FullState {
        gas: MixtureState {
            nuclei,
            thermal_j_m3: thermal,
        },
        photon_bins: vec![],
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
        elapsed_s: 0.,
    };
    let h = HHeModel::controlled_fixture().threshold_ev[0];
    let mut c = NetworkConfig::source_bound(
        DAtomicProvider::new(h, h + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        "MD14_Z002_FESC_BB50K_13P6_100_V1",
    );
    c.use_photo = false;
    c.cmb_temperature_k = 30.;
    (s, c)
}
#[test]
fn real_native_photon_loss_is_one_species_event_and_one_energy_transfer() {
    let (s, c) = fixture();
    let sp = SlabSpectrum::native(vec![20., 60.], vec![0., 0.], &c).unwrap();
    let r = joint_rhs(&s, &c, &sp, &[3., 2.], 0, true).unwrap();
    let expected = 3. * 90. * sp.cross_sections()[0][0] * SPEED_OF_LIGHT_M_S;
    assert!(
        r[sp.photo_index()] > expected,
        "missing physical photo event: {} <= {}",
        r[sp.photo_index()],
        expected
    );
    assert!(r[27] < 0.);
    assert!(r[13] > 0.);
    let binding = r[2] * sp.thresholds()[0]
        + r[4] * sp.thresholds()[3]
        + r[11] * sp.thresholds()[1]
        + r[12] * (sp.thresholds()[1] + sp.thresholds()[2]);
    let radiation = (20. * r[27] + 60. * r[28]) * EV_J;
    let residual = radiation + binding * EV_J + r[13];
    assert!(residual.abs() < 1e-13 * radiation.abs());
}
#[test]
fn empty_photon_reservoir_has_positive_source_and_no_instant_photo_events() {
    let (s, c) = fixture();
    let sp = SlabSpectrum::native(vec![20., 60.], vec![2e-14, 3e-14], &c).unwrap();
    let r = joint_rhs(&s, &c, &sp, &[0., 0.], 0, true).unwrap();
    assert_eq!(&r[27..29], sp.sources());
    assert_eq!(&r[29..37], &[0.; 8]);
    assert_eq!(r[37], 5e-14);
    assert!((r[38] - (20. * 2e-14 + 60. * 3e-14) * EV_J).abs() < 1e-45);
}
#[test]
fn photo_off_is_exact_original_continuous_gas_rhs() {
    let (s, c) = fixture();
    let sp = SlabSpectrum::native(vec![20.], vec![2e-14], &c).unwrap();
    let r = joint_rhs(&s, &c, &sp, &[3.], 7, false).unwrap();
    let g = rei_iso_couple_reference::gas_reference_rhs::gas_rates(&s, &c, 7).unwrap();
    assert_eq!(&r[..27], &g.vector());
    assert!(r[27..].iter().all(|x| *x == 0.));
}
#[test]
fn same_energy_cohorts_can_be_aggregated_exactly_in_this_local_model() {
    let (s, c) = fixture();
    let a = SlabSpectrum::native(vec![20.], vec![5e-14], &c).unwrap();
    let b = SlabSpectrum::native(vec![20., 20.], vec![2e-14, 3e-14], &c).unwrap();
    let ra = joint_rhs(&s, &c, &a, &[7.], 7, true).unwrap();
    let rb = joint_rhs(&s, &c, &b, &[3., 4.], 7, true).unwrap();
    for j in 0..27 {
        assert!((ra[j] - rb[j]).abs() <= 2e-14 * ra[j].abs().max(1e-99));
    }
    assert!((ra[27] - rb[27] - rb[28]).abs() < 2e-14 * ra[27].abs());
    for j in 0..10 {
        assert!((ra[28 + j] - rb[29 + j]).abs() <= 2e-14 * ra[28 + j].abs().max(1e-99));
    }
}
#[test]
fn depleted_neutral_has_zero_photo_destruction_not_clipped_loss() {
    let (mut s, c) = fixture();
    let mut n = [0.; 13];
    for sp in rei_iso_couple_reference::isotope_state::IsotopeSpecies::ALL {
        n[sp as usize] = s.gas.nuclei.density_m3(sp);
    }
    n[2] += n[1];
    n[1] = 0.;
    s.gas.nuclei = IsotopeNumberState::new(n).unwrap();
    let sp = SlabSpectrum::native(vec![20.], vec![0.], &c).unwrap();
    let r = joint_rhs(&s, &c, &sp, &[1000.], 0, true).unwrap();
    assert_eq!(r[1], 0.);
    assert_eq!(r[28], 0.);
    assert!(r[3] < 0.);
}
#[test]
fn invalid_photon_or_duplicate_owner_rejected() {
    let (s, mut c) = fixture();
    let sp = SlabSpectrum::native(vec![20.], vec![0.], &c).unwrap();
    assert!(joint_rhs(&s, &c, &sp, &[-1.], 7, true).is_err());
    assert!(joint_rhs(&s, &c, &sp, &[], 7, true).is_err());
    assert!(SlabSpectrum::native(vec![20.], vec![-1.], &c).is_err());
    assert!(SlabSpectrum::native(vec![f64::NAN], vec![0.], &c).is_err());
    c.use_photo = true;
    assert!(joint_rhs(&s, &c, &sp, &[0.], 7, true).is_err());
}
#[test]
fn binding_and_fit_threshold_are_distinct_no_energy_below_threshold() {
    let (s, c) = fixture();
    let sp = SlabSpectrum::native(vec![13.599, 13.601, 13.603, 54.42], vec![0.; 4], &c).unwrap();
    assert_eq!(sp.cross_sections()[0], [0.; 4]);
    assert!(sp.cross_sections()[1][0] > 0.);
    assert_eq!(sp.cross_sections()[1][3], 0.);
    assert!(sp.cross_sections()[2][3] > 0.);
    let r = joint_rhs(&s, &c, &sp, &[1.; 4], 0, true).unwrap();
    assert!(r[13] >= 0.);
    assert!(
        r[sp.photo_index() + 4..sp.photo_index() + 8]
            .iter()
            .all(|x| *x >= 0.)
    );
}
#[test]
fn all_process_energy_balance_and_each_nuclear_census_close() {
    let (s, c) = fixture();
    let sp = SlabSpectrum::native(vec![20., 40., 60.], vec![1e-13; 3], &c).unwrap();
    let r = joint_rhs(&s, &c, &sp, &[3., 2., 1.], 7, true).unwrap();
    for ii in [&[1, 2][..], &[3, 4][..], &[10, 11, 12][..]] {
        let scale = ii.iter().map(|&j| r[j].abs()).sum::<f64>();
        assert!(ii.iter().map(|&j| r[j]).sum::<f64>().abs() < 1e-13 * scale.max(1e-99));
    }
    let ch = sp.thresholds();
    let chemical = (r[2] * ch[0] + r[4] * ch[3] + r[11] * ch[1] + r[12] * (ch[1] + ch[2])) * EV_J;
    let radiation = sp
        .energies()
        .iter()
        .zip(&r[27..30])
        .map(|(e, n)| e * n * EV_J)
        .sum::<f64>();
    let sum = r[13] + r[14] + r[15] + chemical + radiation - r[sp.dimension() - 1];
    let scale = r[13].abs() + r[14].abs() + r[15].abs() + chemical.abs() + radiation.abs();
    assert!(sum.abs() < 2e-13 * scale);
}
