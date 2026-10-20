use rei_run19_metals::beryllium_rr::*;
use rei_run19_metals::lithium_backend::LithiumBackend;
use rei_run19_metals::lithium_rates::{IsotopeRatePolicy, LithiumError, LithiumIsotopeNumberState};

#[test]
fn be_author_rows_charge_direction_and_domain_are_explicit() {
    let p = BeRrProvider::from_primary_rows().unwrap();
    for (i, r) in p.records().iter().enumerate() {
        assert_eq!(r.atomic_number, 4);
        assert_eq!(r.initial_charge, i as u8 + 2);
        assert_eq!(r.final_charge, i as u8 + 1);
        assert_eq!(r.formed_electron_count + r.final_charge, 4);
    }
    let mut max_relative: f64 = 0.0;
    let mut checked = 0;
    for line in include_str!("../provenance/VF1996_BE_DECIMAL_REFERENCE.csv").lines().skip(1) {
        let fields: Vec<_> = line.split(',').collect();
        let charge = fields[1].parse::<u8>().unwrap();
        let t = fields[2].parse::<f64>().unwrap();
        let reference = fields[4].parse::<f64>().unwrap();
        let got = p.coefficient_cm3_s(charge, t).unwrap();
        let relative = (got / reference - 1.0).abs();
        assert!(relative <= 8.0 * f64::EPSILON,
            "formed_charge={charge} T={t:e} direct={got:.17e} Decimal80_rounded={reference:.17e} relative={relative:.17e}");
        max_relative = max_relative.max(relative);
        checked += 1;
    }
    assert_eq!(checked, 18);
    println!("be_rr Decimal80 rounded references={checked} max_relative={max_relative:e}");
    for t in [BE_RR_MIN_K, BE_RR_MAX_K] {
        assert!(p.rates(t).unwrap().alpha_cm3_s().into_iter().all(|v| v > 0.0 && v.is_finite()));
    }
    for t in [f64::NAN, f64::INFINITY, 0.0, -1.0,
        f64::from_bits(BE_RR_MIN_K.to_bits() - 1), f64::from_bits(BE_RR_MAX_K.to_bits() + 1)] {
        assert_eq!(p.rates(t), Err(BeRrError::TemperatureDomain));
    }
    assert_eq!(p.coefficient_cm3_s(0, 1e4), Err(BeRrError::MissingSource));
    assert_eq!(p.coefficient_cm3_s(4, 1e4), Err(BeRrError::InvalidCharge));
}

#[test]
fn be_log_grid_sampled_error_and_batch_order_match_fixed_owner() {
    let p = BeRrProvider::from_primary_rows().unwrap();
    let table = BeRrTable::build(8193).unwrap();
    let mut ts = vec![BE_RR_MIN_K, BE_RR_MAX_K];
    for i in 0..513 {
        let f = (i as f64 + 0.2718281828459045) / 513.0;
        ts.push((BE_RR_MIN_K.ln() + f * (BE_RR_MAX_K / BE_RR_MIN_K).ln()).exp());
    }
    let soa = table.batch_soa(&ts).unwrap();
    let parallel = table.batch_parallel(&ts, 2).unwrap();
    let mut maximum: f64 = 0.0;
    for (i, &t) in ts.iter().enumerate() {
        let direct = p.rates(t).unwrap().alpha_cm3_s();
        let scalar = table.rates(t).unwrap().alpha_cm3_s();
        for j in 0..3 {
            assert_eq!(soa[j][i].to_bits(), scalar[j].to_bits());
            assert_eq!(parallel[j][i].to_bits(), scalar[j].to_bits());
            assert!(scalar[j] > 0.0);
            maximum = maximum.max((scalar[j] / direct[j] - 1.0).abs());
        }
    }
    let h = (BE_RR_MAX_K / BE_RR_MIN_K).ln() / 8192.0;
    // Real-arithmetic |(ln alpha)''|<=1/8 gives expm1(h^2/64).
    // This finite sampled assertion includes roundoff slack, not an interval certificate.
    assert!(maximum < (h * h / 64.0).exp_m1() + 64.0 * f64::EPSILON);
    assert_eq!(table.blocked_cells(), 0);
    assert!(table.batch_parallel(&ts, 0).is_err());
    assert!(table.batch_parallel(&ts, 5).is_err());
    assert!(table.batch_soa(&[1e4, 2.0]).is_err());
    println!("be_rr fixed99 nodes={} storage_bytes={} independent_temperatures={} sampled_max_relative={maximum:e}",
        table.nodes(), table.storage_bytes(), ts.len());
}

#[test]
fn be_selected_fluxes_conserve_nuclei_and_consume_one_electron_each() {
    let backend = BeRrBackend::direct().unwrap();
    let state = BerylliumIsotopeNumberState::new([1.0, 2.0, 3.0, 4.0], [5.0, 7.0, 11.0, 13.0]).unwrap();
    let moments = state.moments().unwrap();
    assert_eq!(moments.isotope_nuclei_m3, [10.0, 36.0]);
    assert_eq!(moments.baryon_number_m3, 7.0 * 10.0 + 9.0 * 36.0);
    assert_eq!(moments.nuclear_charge_number_m3, 4.0 * 46.0);
    assert_eq!(moments.ionic_charge_number_m3, 1.0 + 4.0 + 9.0 + 16.0 + 5.0 + 14.0 + 33.0 + 52.0);
    let prepared = backend.prepare(1e4).unwrap();
    let r = backend.number_contribution(1e4, &prepared, &state, 19.0,
        IsotopeRatePolicy::ElementalElectronicEquality).unwrap();
    let event_sum = r.recombination_events_m3_s.iter().flatten().sum::<f64>();
    let charge = r.species_m3_s.iter().map(|row| row.iter().enumerate()
        .map(|(i, v)| (i + 1) as f64 * v).sum::<f64>()).sum::<f64>();
    let mut baryons = 0.0;
    for (a, row) in [7.0, 9.0].into_iter().zip(r.species_m3_s) {
        let nuclei = row.iter().sum::<f64>();
        assert!(nuclei.abs() <= 16.0 * f64::EPSILON * event_sum);
        baryons += a * nuclei;
    }
    assert!(baryons.abs() <= 144.0 * f64::EPSILON * event_sum);
    assert!((charge - r.electron_m3_s).abs() <= 32.0 * f64::EPSILON * event_sum);
    assert!((r.electron_m3_s + event_sum).abs() <= 8.0 * f64::EPSILON * event_sum);
    let expected = 19.0 * 2.0 * prepared.rates().alpha_cm3_s()[0] * 1e-6;
    assert!((r.recombination_events_m3_s[0][0] / expected - 1.0).abs() <= 4.0 * f64::EPSILON);
    assert!(!r.isotope_resolved_coefficients);
    assert_eq!(r.scope, BE_RR_SCOPE);
    assert_eq!(state.density_m3(BerylliumIsotope::Be7, 0), Err(BeRrError::MissingSource));
    assert_eq!(backend.number_contribution(1e4, &prepared, &state, 19.0,
        IsotopeRatePolicy::IsotopeResolved), Err(BeRrError::MissingSource));
    assert_eq!(BerylliumIsotope::Be7.nuclear_evolution_scope(), "NOT_MODELED_BY_ELECTRONIC_PROVIDER");
}

#[test]
fn be_contribution_is_quasipositive_and_handles_zero_reservoirs() {
    let rates = BeRrProvider::from_primary_rows().unwrap().rates(3.0).unwrap();
    let policy = IsotopeRatePolicy::ElementalElectronicEquality;
    for q in 0..4 {
        let mut n = [0.0; 4]; n[q] = 1.0;
        let state = BerylliumIsotopeNumberState::new(n, [0.0; 4]).unwrap();
        let r = be_rr_number_contribution(&rates, &state, 1e6, policy).unwrap();
        for (j, &v) in r.species_m3_s[0].iter().enumerate() {
            if n[j] == 0.0 { assert!(v >= 0.0); }
        }
        assert_eq!(r.species_m3_s[1], [0.0; 4]);
        let zero = be_rr_number_contribution(&rates, &state, 0.0, policy).unwrap();
        assert_eq!(zero.species_m3_s, [[0.0; 4]; 2]);
        assert_eq!(zero.electron_m3_s, 0.0);
        assert!(be_rr_number_contribution(&rates, &state, -1.0, policy).is_err());
    }
    assert!(BerylliumIsotopeNumberState::new([-1.0; 4], [0.0; 4]).is_err());
    assert!(BerylliumIsotopeNumberState::new([f64::NAN; 4], [0.0; 4]).is_err());
    assert!(BerylliumIsotopeNumberState::new([f64::MAX; 4], [0.0; 4]).is_err());
}

#[test]
fn prepared_lithium_rejects_temperature_and_evaluator_substitution() {
    let direct = LithiumBackend::direct().unwrap();
    let table = LithiumBackend::tabulated(1025).unwrap();
    let other = LithiumBackend::tabulated(2049).unwrap();
    let p = table.prepare(1e6).unwrap();
    assert_eq!(table.require_prepared(1e6, &p).unwrap(), table.rates(1e6).unwrap());
    assert_eq!(direct.require_prepared(1e6, &p), Err(LithiumError::InvalidInput));
    assert_eq!(other.require_prepared(1e6, &p), Err(LithiumError::InvalidInput));
    assert_eq!(table.require_prepared(f64::from_bits(1e6f64.to_bits() + 1), &p), Err(LithiumError::InvalidInput));
    assert_eq!(direct.rates(1e4), Err(LithiumError::TemperatureDomain));
    let state = LithiumIsotopeNumberState::new([1.0; 4], [2.0; 4]).unwrap();
    assert!(table.number_contribution(1e6, &p, &state, 19.0,
        IsotopeRatePolicy::ElementalElectronicEquality).is_ok());
}

#[test]
fn prepared_be_rejects_temperature_and_evaluator_substitution() {
    let direct = BeRrBackend::direct().unwrap();
    let table = BeRrBackend::tabulated(1025).unwrap();
    let other = BeRrBackend::tabulated(2049).unwrap();
    let p = table.prepare(1e4).unwrap();
    assert_eq!(table.require_prepared(1e4, &p).unwrap(), table.rates(1e4).unwrap());
    assert_eq!(direct.require_prepared(1e4, &p), Err(BeRrError::BindingMismatch));
    assert_eq!(other.require_prepared(1e4, &p), Err(BeRrError::BindingMismatch));
    assert_eq!(table.require_prepared(f64::from_bits(1e4f64.to_bits() + 1), &p), Err(BeRrError::BindingMismatch));
}
