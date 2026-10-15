use rei_microphysics::{axbi_sources::AxbiSource, HHeModel, MPC_CM};
fn reference(lo: f64, hi: f64, n: usize, moment: bool) -> f64 {
    let c = HHeModel::controlled_fixture();
    let kt = 50000.0 * c.kb_erg_k / c.ev_erg;
    let dx = (hi - lo) / n as f64;
    (0..=n)
        .map(|i| {
            let e = lo + dx * i as f64;
            let weight = if i == 0 || i == n {
                1.0
            } else if i % 2 == 0 {
                2.0
            } else {
                4.0
            };
            weight * e.powi(2) / (e / kt).exp_m1() * if moment { e } else { 1.0 }
        })
        .sum::<f64>()
        * dx
        / 3.0
}
#[test]
fn photon_weights_energy_moments_and_parity_are_controlled() {
    for nmu in [8, 16, 32] {
        let s = AxbiSource::new(1.9e-7, 0.2, 16, nmu).unwrap();
        assert!(
            (s.spectral_cells
                .iter()
                .map(|c| c.photon_fraction)
                .sum::<f64>()
                - 1.0)
                .abs()
                < 1e-12
        );
        assert!(
            (s.angular_cells
                .iter()
                .map(|c| c.count_fraction)
                .sum::<f64>()
                - 1.0)
                .abs()
                < 1e-12
        );
        assert!(
            s.angular_cells
                .iter()
                .map(|c| c.mu * c.count_fraction)
                .sum::<f64>()
                .abs()
                < 1e-12
        );
        let refn = reference(13.6, 100.0, 8192, false);
        let refu = reference(13.6, 100.0, 8192, true) / refn;
        let u = s
            .spectral_cells
            .iter()
            .map(|c| c.energy_ev * c.photon_fraction)
            .sum::<f64>();
        assert!((u / refu - 1.0).abs() < 1e-7);
        for cell in &s.spectral_cells {
            let nc = reference(cell.lower_ev, cell.upper_ev, 64, false);
            let uc = reference(cell.lower_ev, cell.upper_ev, 64, true);
            assert!(
                (cell.energy_ev / (uc / nc) - 1.0).abs() < 1e-7,
                "Ecell={}..{} relative_mean_error={}",
                cell.lower_ev,
                cell.upper_ev,
                cell.energy_ev / (uc / nc) - 1.0
            );
            assert!(cell.energy_ev > cell.lower_ev && cell.energy_ev < cell.upper_ev);
        }
        assert!(s.normalization_relative_residual <= 1e-7);
        assert!(
            s.omitted_blackbody_tail_photon_fraction > 0.0
                && s.omitted_blackbody_tail_photon_fraction < 1e-6
        );
    }
}
#[test]
fn continuous_source_has_one_angle_owner_and_exact_units() {
    let nh0 = 1.9e-7;
    let s = AxbiSource::new(nh0, 0.2, 16, 8).unwrap();
    for z in [4.0, 12.0, 20.0] {
        let r = s.at_redshift(z).unwrap();
        let nh = nh0 * (1.0 + z).powi(3);
        assert!((r.proper_photons_cm3_s / (r.per_h_s * nh) - 1.0).abs() < 1e-12);
        assert!(
            (r.comoving_photons_per_s_cmpc3
                / (r.proper_photons_cm3_s * MPC_CM.powi(3) / (1.0 + z).powi(3))
                - 1.0)
                .abs()
                < 1e-12
        );
        let sum = (0..s.spectral_cells.len())
            .flat_map(|i| (0..s.angular_cells.len()).map(move |j| (i, j)))
            .map(|(i, j)| s.cell_per_h_s(z, i, j).unwrap())
            .sum::<f64>();
        assert!((sum / r.per_h_s - 1.0).abs() < 1e-12);
    }
    for z in [3.9, 20.1, f64::NAN, f64::INFINITY] {
        assert!(s.at_redshift(z).is_err());
    }
    assert!(AxbiSource::new(nh0, 1.1, 16, 8).is_err());
    assert!(AxbiSource::new(nh0, 0.2, 0, 8).is_err());
    assert!(AxbiSource::new(nh0, 0.2, 16, 7).is_err());
}
