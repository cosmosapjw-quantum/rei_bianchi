use rei_microphysics::{
    axbi_rates::{AxbiProvider, AXBI_PROVIDER_ID},
    igm_rates::igm_rates,
    igm_state::IgmGasState,
    igm_thermal::{igm_point_rhs, IgmPhotoInput},
};

#[test]
fn campaign_binding_preserves_cold_and_reheated_point_model() {
    let (nh, nhe) = (1.5e-3, 1.2e-4);
    let photo = IgmPhotoInput {
        gamma_s: [1e-13, 2e-14, 3e-15],
        heat_erg_per_absorber_s: [1e-24, 2e-25, 3e-26],
    };
    for t in [6.137, 20.0, 100.0, 5500.0, 9284.0, 1e4, 1e5] {
        let gas = IgmGasState::from_temperature([2e-4, 1e-5, 1e-8], nh, nhe, t).unwrap();
        let p = AxbiProvider
            .point(&gas, nh, nhe, 1e-16, 57.2355, photo)
            .unwrap();
        let expected = igm_point_rhs(&gas, nh, nhe, 1e-16, 57.2355, photo).unwrap();
        assert_eq!(p.provider_id, AXBI_PROVIDER_ID);
        assert_eq!(p.temperature_k, gas.eos(nh, nhe).unwrap().temperature_k);
        // Every public coefficient, diagnostic and RHS field is preserved.
        assert_eq!(
            format!("{:?}", p.rates),
            format!("{:?}", igm_rates(p.temperature_k).unwrap())
        );
        assert_eq!(format!("{:?}", p.rhs), format!("{expected:?}"));
        let r = p.rhs;
        let residual = r.thermal_micro_erg_cm3_s + r.binding_micro_erg_cm3_s + r.escape_erg_cm3_s
            - r.photo_input_erg_cm3_s
            - r.cmb_to_gas_erg_cm3_s;
        let scale = r.escape_erg_cm3_s + r.photo_input_erg_cm3_s + r.cmb_to_gas_erg_cm3_s.abs();
        assert!(residual.abs() <= 2e-14 * scale);
        assert_eq!(
            r.species_chemical_cm3_s[0] + r.species_chemical_cm3_s[1],
            0.0
        );
    }
}

#[test]
fn campaign_binding_retains_strict_domain_and_endpoint_rules() {
    for t in [1.0, 1e6] {
        assert!(AxbiProvider.rates(t).is_ok());
    }
    for t in [0.999999, 1e6 + 1.0, 0.0, -1.0, f64::NAN, f64::INFINITY] {
        assert!(AxbiProvider.rates(t).is_err());
    }
    for t in [0.9, 1.1e6] {
        let gas = IgmGasState::from_temperature([0.1, 0.1, 0.1], 1e-3, 8e-5, t).unwrap();
        assert!(AxbiProvider
            .point(&gas, 1e-3, 8e-5, 0.0, 57.0, IgmPhotoInput::default())
            .is_err());
    }
}
