use rei_microphysics::extra_ion_rates::*;

fn provider()->CarbonProvider { CarbonProvider::from_primary_rows(CarbonIdentity::ElementalGroundParent).unwrap() }
#[test]
fn elemental_identity_and_source_domains_are_explicit() {
    assert!(matches!(CarbonProvider::from_primary_rows(CarbonIdentity::Isotope {mass_number:12}),Err(CarbonError::MissingIsotopeNative)));
    let p=provider();
    let rr=p.record(CarbonProcess::RadiativeRecombination,1).unwrap();
    assert_eq!(rr.minimum_k,10.0);
    assert!(p.coefficient_cm3_s(CarbonProcess::RadiativeRecombination,1,10.0).unwrap()>0.0);
    assert_eq!(p.rates(10.0),Err(CarbonError::TemperatureDomain));
    assert_eq!(p.coefficient_cm3_s(CarbonProcess::CollisionalIonization,0,1.0),Err(CarbonError::TemperatureDomain));
    assert_eq!(p.coefficient_cm3_s(CarbonProcess::DielectronicRecombination,6,1.0).unwrap(),0.0);
    for t in [f64::NAN,0.0,-1.0,f64::INFINITY] { assert!(p.rates(t).is_err()); }
    for process in [CarbonProcess::CollisionalIonization,CarbonProcess::RadiativeRecombination,CarbonProcess::DielectronicRecombination] {
        for q in 0..7 {
            let record=p.record(process,q).unwrap();
            if record.structural_zero { continue; }
            let lo=record.minimum_k;
            let hi=record.maximum_k;
            assert_eq!(p.coefficient_cm3_s(process,q,f64::from_bits(lo.to_bits()-1)),Err(CarbonError::TemperatureDomain));
            assert!(p.coefficient_cm3_s(process,q,lo).is_ok());
            assert!(p.coefficient_cm3_s(process,q,f64::from_bits(lo.to_bits()+1)).is_ok());
            assert!(p.coefficient_cm3_s(process,q,hi).is_ok());
            assert_eq!(p.coefficient_cm3_s(process,q,f64::from_bits(hi.to_bits()+1)),Err(CarbonError::TemperatureDomain));
        }
    }
    let cold=p.coefficient_cm3_s(CarbonProcess::RadiativeRecombination,1,100.0).unwrap();
    assert!(cold>0.0);
    let hot=p.rates(1e6).unwrap();
    let zero=carbon_number_rhs(&hot,[1.0;7],0.0).unwrap();
    assert_eq!(zero.species_m3_s,[0.0;7]);
    assert_eq!(zero.electron_m3_s,0.0);
    assert_eq!(zero.ionization_events_m3_s,[0.0;7]);
    assert_eq!(zero.recombination_events_m3_s,[0.0;7]);
}
#[test]
fn primary_rows_are_parsed_and_signed_dr_sum_is_retained() {
    let p=provider(); let t:f64=1e6;
    // Independent hand substitution of the C4+ row, including its negative amplitude.
    let expected=(2.646e-3*(-2.804e6/t).exp()+1.762e-2*(-3.485e6/t).exp()-7.843e-4*(-4.324e6/t).exp())/t.powf(1.5);
    let got=p.coefficient_cm3_s(CarbonProcess::DielectronicRecombination,4,t).unwrap();
    assert!((got/expected-1.0).abs()<2e-15);
    let a=5.337e-10; let b=0.7485; let x=(t/95.02).sqrt(); let y=(t/2.517e7).sqrt();
    let expected=a/(x*(1.0+x).powf(1.0-b)*(1.0+y).powf(1.0+b));
    assert!((p.coefficient_cm3_s(CarbonProcess::RadiativeRecombination,6,t).unwrap()/expected-1.0).abs()<2e-15);
    let u=11.3/(VORONOV_KB_EV_K*t);
    let expected=6.85e-8/(0.193+u)*u.powf(0.25)*(-u).exp();
    assert!((p.coefficient_cm3_s(CarbonProcess::CollisionalIonization,0,t).unwrap()/expected-1.0).abs()<2e-15);
}
#[test]
fn shared_temperature_table_and_number_fluxes_preserve_scope() {
    let p=provider(); let table=CarbonRateTable::build(p.clone(),8193).unwrap();
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
        let n=[1.0,3.0,2.0,5.0,7.0,11.0,13.0]; let ne=19.0;
        let rhs=carbon_number_rhs(&tab,n,ne).unwrap();
        let reference=carbon_number_rhs(&direct,n,ne).unwrap();
        let events:f64=rhs.ionization_events_m3_s.iter().chain(&rhs.recombination_events_m3_s).sum();
        let nuclei:f64=rhs.species_m3_s.iter().sum();
        let charge:f64=rhs.species_m3_s.iter().enumerate().map(|(q,x)|q as f64*x).sum();
        assert!(nuclei.abs()<=2e-15*events);
        assert!((charge-rhs.electron_m3_s).abs()<=4e-15*events);
        for (a,b) in rhs.species_m3_s.iter().zip(reference.species_m3_s) { assert!((a-b).abs()<=1e-5*events); }
        assert!((rhs.ionization_events_m3_s[0]-ne*n[0]*tab.ci_cm3_s[0]*1e-6).abs()<=2e-15*events);
    }
    assert!(maximum<=1e-5,"sampled carbon coefficient relative error {maximum:e}");
    println!("carbon nodes=8193 independent_temperatures={} sampled_max_relative_error={maximum:e}",temperatures.len());
    assert!(table.rates(COMMON_MIN_K*0.999).is_err());
    assert!(table.rates(COMMON_MAX_K*1.001).is_err());
}
