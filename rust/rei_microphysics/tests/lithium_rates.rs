use rei_microphysics::lithium_rates::*;

fn provider()->LithiumProvider { LithiumProvider::from_primary_rows().unwrap() }
#[test]
fn elemental_identity_and_source_domains_are_explicit() {
    let p=provider();
    let rr=p.record(LithiumProcess::RadiativeRecombination,1).unwrap();
    assert_eq!(rr.minimum_k,10.0);
    assert!(p.coefficient_cm3_s(LithiumProcess::RadiativeRecombination,1,10.0).unwrap()>0.0);
    assert_eq!(p.rates(10.0),Err(LithiumError::TemperatureDomain));
    assert_eq!(p.coefficient_cm3_s(LithiumProcess::CollisionalIonization,0,1.0),Err(LithiumError::TemperatureDomain));
    assert_eq!(p.coefficient_cm3_s(LithiumProcess::DielectronicRecombination,3,1.0).unwrap(),0.0);
    for t in [f64::NAN,0.0,-1.0,f64::INFINITY] { assert!(p.rates(t).is_err()); }
    for process in [LithiumProcess::CollisionalIonization,LithiumProcess::RadiativeRecombination,LithiumProcess::DielectronicRecombination] {
        for q in 0..4 {
            let record=p.record(process,q).unwrap();
            if record.structural_zero { continue; }
            let lo=record.minimum_k;
            let hi=record.maximum_k;
            assert_eq!(p.coefficient_cm3_s(process,q,f64::from_bits(lo.to_bits()-1)),Err(LithiumError::TemperatureDomain));
            assert!(p.coefficient_cm3_s(process,q,lo).is_ok());
            assert!(p.coefficient_cm3_s(process,q,f64::from_bits(lo.to_bits()+1)).is_ok());
            assert!(p.coefficient_cm3_s(process,q,hi).is_ok());
            assert_eq!(p.coefficient_cm3_s(process,q,f64::from_bits(hi.to_bits()+1)),Err(LithiumError::TemperatureDomain));
        }
    }
    let cold=p.coefficient_cm3_s(LithiumProcess::RadiativeRecombination,1,100.0).unwrap();
    assert!(cold>0.0);
    let hot=p.rates(1e6).unwrap();
    let zero=lithium_number_rhs(&hot,[1.0;4],0.0).unwrap();
    assert_eq!(zero.species_m3_s,[0.0;4]);
    assert_eq!(zero.electron_m3_s,0.0);
    assert_eq!(zero.ionization_events_m3_s,[0.0;4]);
    assert_eq!(zero.recombination_events_m3_s,[0.0;4]);
}
#[test]
fn primary_rows_are_parsed_and_signed_dr_sum_is_retained() {
    let p=provider(); let t:f64=1e6;
    // Independent substitutions of preserved official raw rows, not provider calls.
    let expected=(2.941e-5*(-6.345e5/t).exp()+6.068e-5*(-7.024e5/t).exp()-7.753e-7*(-8.271e5/t).exp())/t.powf(1.5);
    let got=p.coefficient_cm3_s(LithiumProcess::DielectronicRecombination,1,t).unwrap();
    assert!((got/expected-1.0).abs()<2e-15);
    let a=8.7e-12; let b=0.364+0.1508*(-715400.0/t).exp(); let x=(t/147.0).sqrt(); let y=(t/7153000.0).sqrt();
    let expected=a/(x*(1.0+x).powf(1.0-b)*(1.0+y).powf(1.0+b));
    assert!((p.coefficient_cm3_s(LithiumProcess::RadiativeRecombination,1,t).unwrap()/expected-1.0).abs()<2e-15);
    let u=5.4/(VORONOV_KB_EV_K*t);
    let expected=1.39e-7/(0.438+u)*u.powf(0.41)*(-u).exp();
    assert!((p.coefficient_cm3_s(LithiumProcess::CollisionalIonization,0,t).unwrap()/expected-1.0).abs()<2e-15);
}
#[test]
fn shared_temperature_table_and_number_fluxes_preserve_scope() {
    let p=provider(); let table=LithiumRateTable::build(p.clone(),8193).unwrap();
    let mut maximum:f64=0.0;
    let mut temperatures=vec![COMMON_MIN_K,COMMON_MAX_K];
    for i in 0..1013 {
        let f=(i as f64+0.3819660112501051)/1013.0;
        temperatures.push((COMMON_MIN_K.ln()+f*(COMMON_MAX_K/COMMON_MIN_K).ln()).exp());
    }
    let batch=table.batch(&temperatures).unwrap();
    for (&t,tab) in temperatures.iter().zip(batch) {
        assert_eq!(tab,table.rates(t).unwrap());
        let direct=p.rates(t).unwrap();
        for (aa,bb) in [(tab.ci_cm3_s,direct.ci_cm3_s),(tab.rr_cm3_s,direct.rr_cm3_s),(tab.dr_cm3_s,direct.dr_cm3_s)] {
            for (a,b) in aa.into_iter().zip(bb) {
                if b==0.0 { assert_eq!(a,0.0); } else { maximum=maximum.max((a/b-1.0).abs()); }
            }
        }
        let n=[1.0,3.0,2.0,5.0]; let ne=19.0;
        let rhs=lithium_number_rhs(&tab,n,ne).unwrap();
        let reference=lithium_number_rhs(&direct,n,ne).unwrap();
        let events:f64=rhs.ionization_events_m3_s.iter().chain(&rhs.recombination_events_m3_s).sum();
        let nuclei:f64=rhs.species_m3_s.iter().sum();
        let charge:f64=rhs.species_m3_s.iter().enumerate().map(|(q,x)|q as f64*x).sum();
        assert!(nuclei.abs()<=2e-15*events);
        assert!((charge-rhs.electron_m3_s).abs()<=4e-15*events);
        for (a,b) in rhs.species_m3_s.iter().zip(reference.species_m3_s) { assert!((a-b).abs()<=1e-5*events); }
        assert!((rhs.ionization_events_m3_s[0]-ne*n[0]*tab.ci_cm3_s[0]*1e-6).abs()<=2e-15*events);
    }
    assert!(maximum<=1e-5,"sampled lithium coefficient relative error {maximum:e}");
    println!("lithium nodes=8193 independent_temperatures={} sampled_max_relative_error={maximum:e}",temperatures.len());
    assert!(table.rates(COMMON_MIN_K*0.999).is_err());
    assert!(table.rates(COMMON_MAX_K*1.001).is_err());
}

#[test]
fn isotope_identity_policy_and_number_invariants_are_explicit() {
    let p=provider();
    let table=LithiumRateTable::build(p.clone(),8193).unwrap();
    let approx=IsotopeRatePolicy::ElementalElectronicEquality;
    let native=IsotopeRatePolicy::IsotopeResolved;
    let state=LithiumIsotopeNumberState::new([1.0,2.0,3.0,4.0],[5.0,7.0,11.0,13.0]).unwrap();
    assert_eq!(LithiumIsotopeNumberState::new([-1.0,0.0,0.0,0.0],[0.0;4]),Err(LithiumError::InvalidInput));
    assert_eq!(LithiumIsotopeNumberState::new([f64::NAN,0.0,0.0,0.0],[0.0;4]),Err(LithiumError::InvalidInput));
    assert_eq!(LithiumIonIdentity::new(LithiumIsotope::Li6,4),Err(LithiumError::InvalidCharge));
    let moments=state.moments().unwrap();
    assert_eq!(moments.isotope_nuclei_m3,[10.0,36.0]);
    assert_eq!(moments.baryon_number_m3,6.0*10.0+7.0*36.0);
    assert_eq!(moments.nuclear_charge_number_m3,3.0*46.0);
    assert_eq!(moments.ionic_charge_number_m3,2.0+6.0+12.0+7.0+22.0+39.0);
    for isotope in [LithiumIsotope::Li6,LithiumIsotope::Li7] {
        for q in 0..4 {
            let ion=LithiumIonIdentity::new(isotope,q).unwrap();
            assert_eq!(ion.nuclear_charge(),3);
            assert_eq!(ion.mass_number(),isotope.mass_number());
            assert!(state.density_m3(ion).unwrap()>0.0);
        }
        assert_eq!(p.isotope_rates(isotope,native,1e6),Err(LithiumError::MissingSource));
        assert_eq!(table.isotope_rates(isotope,native,1e6),Err(LithiumError::MissingSource));
        assert!(!p.isotope_rates(isotope,approx,1e6).unwrap().isotope_resolved);
        assert!(p.isotope_coefficient_cm3_s(isotope,approx,LithiumProcess::RadiativeRecombination,1,10.0).unwrap()>0.0);
    }
    for isotope in [LithiumIsotope::Li8,LithiumIsotope::Li9] {
        assert_eq!(isotope.scope(),LithiumIsotopeScope::PendingNuclearDecayDaughterClosure);
        assert_eq!(p.isotope_rates(isotope,approx,1e6),Err(LithiumError::PendingNuclearDecayDaughterClosure));
    }
    let a=table.isotope_rates(LithiumIsotope::Li6,approx,1e6).unwrap();
    let b=table.isotope_rates(LithiumIsotope::Li7,approx,1e6).unwrap();
    assert_ne!(a.isotope,b.isotope);
    assert_eq!(a.electronic,b.electronic); // equality follows only from the named approximation
    let proportional=LithiumIsotopeNumberState::new([1.0,2.0,3.0,4.0],[3.0,6.0,9.0,12.0]).unwrap();
    let proportional_rhs=lithium_isotope_number_rhs(&a.electronic,&proportional,19.0,approx).unwrap();
    let proportional_scale:f64=proportional_rhs.isotope_channels.iter().flat_map(|r|r.ionization_events_m3_s.iter().chain(&r.recombination_events_m3_s)).sum();
    for (li6,li7) in proportional_rhs.species_m3_s[0].iter().zip(proportional_rhs.species_m3_s[1]) {
        assert!((li7-3.0*li6).abs()<=64.0*f64::EPSILON*proportional_scale);
    }
    assert_eq!(lithium_isotope_number_rhs(&a.electronic,&state,19.0,native),Err(LithiumError::MissingSource));
    for t in [COMMON_MIN_K,1e5,1e6,COMMON_MAX_K] {
        let rates=table.rates(t).unwrap();
        let rhs=lithium_isotope_number_rhs(&rates,&state,19.0,approx).unwrap();
        let events:f64=rhs.isotope_channels.iter().flat_map(|r|r.ionization_events_m3_s.iter().chain(&r.recombination_events_m3_s)).sum();
        let mut baryons=0.0; let mut charge=0.0;
        for (a,row) in [6.0,7.0].iter().zip(rhs.species_m3_s) {
            let nuclei:f64=row.iter().sum();
            assert!(nuclei.abs()<=64.0*f64::EPSILON*events);
            baryons+=a*nuclei;
            charge+=row.iter().enumerate().map(|(q,n)|q as f64*n).sum::<f64>();
        }
        assert!(baryons.abs()<=7.0*64.0*f64::EPSILON*events);
        assert!((charge-rhs.electron_m3_s).abs()<=64.0*f64::EPSILON*events);
        let zero=lithium_isotope_number_rhs(&rates,&state,0.0,approx).unwrap();
        assert_eq!(zero.species_m3_s,[[0.0;4];2]);
        assert_eq!(zero.electron_m3_s,0.0);
    }
}
